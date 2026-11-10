import getpass
import math
import random
from collections import defaultdict

import numpy as np
from neo4j import GraphDatabase
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

URI = "bolt://127.0.0.1:7687"
DATABASE = "neo4j"
K = 20
MIN_COMMON = 5
TEST_RATIO = 0.20
TOP_N = 10
RELEVANT_RATING = 4.0
RANDOM_SEED = 42

LOAD_RATINGS = """
MATCH (u:User)-[r:RATED]->(m:Movie)
RETURN toString(u.userId) AS userId,
       toString(m.movieId) AS movieId,
       toFloat(r.rating) AS rating
"""


def main():
    password = getpass.getpass("Password Neo4j: ")
    with GraphDatabase.driver(URI, auth=("neo4j", password)) as driver:
        driver.verify_connectivity()
        with driver.session(database=DATABASE) as session:
            records = list(session.run(LOAD_RATINGS))

    # Sort for repeatable split if database contents are unchanged.
    records.sort(key=lambda x: (int(x["userId"]), int(x["movieId"])))
    all_ratings = defaultdict(dict)
    for row in records:
        all_ratings[row["userId"]][row["movieId"]] = float(row["rating"])

    print("Jumlah user:", len(all_ratings))
    print("Jumlah rating:", sum(len(v) for v in all_ratings.values()))

    # Per-user train-test split, following the structure of the User-Based script.
    rng = random.Random(RANDOM_SEED)
    train, test = defaultdict(dict), defaultdict(dict)
    for user in sorted(all_ratings, key=int):
        items = sorted(all_ratings[user].items(), key=lambda x: int(x[0]))
        rng.shuffle(items)
        if len(items) < 2:
            train[user] = dict(items)
            continue
        n_test = max(1, round(len(items) * TEST_RATIO))
        n_test = min(n_test, len(items) - 1)
        test[user] = dict(items[:n_test])
        train[user] = dict(items[n_test:])

    n_train = sum(len(v) for v in train.values())
    n_test = sum(len(v) for v in test.values())
    print("Rating training:", n_train)
    print("Rating testing:", n_test)

    # Movie-user matrix from training ratings only.
    users = sorted(train.keys(), key=int)
    movies = sorted({m for ratings in train.values() for m in ratings}, key=int)
    user_idx = {u: i for i, u in enumerate(users)}
    movie_idx = {m: i for i, m in enumerate(movies)}
    rows, cols, vals = [], [], []
    movie_user_sets = {m: set() for m in movies}
    for user, ratings in train.items():
        for movie, rating in ratings.items():
            rows.append(movie_idx[movie])
            cols.append(user_idx[user])
            vals.append(rating)
            movie_user_sets[movie].add(user)

    matrix = csr_matrix(
        (vals, (rows, cols)), shape=(len(movies), len(users)), dtype=np.float32
    )
    if len(movies) < 2:
        raise RuntimeError("Jumlah film training tidak cukup untuk menghitung similarity.")

    print("Menghitung item-item cosine similarity dari training...")
    nn = NearestNeighbors(
        metric="cosine", algorithm="brute",
        n_neighbors=min(K + 1, len(movies)), n_jobs=-1
    )
    nn.fit(matrix)
    distances, indices = nn.kneighbors(matrix)

    # Preserve original Item-Based selection rule: select top K first,
    # then filter pairs with fewer than MIN_COMMON common raters.
    neighbors = defaultdict(list)
    for i, movie in enumerate(movies):
        top = []
        for distance, j in zip(distances[i], indices[i]):
            other = movies[int(j)]
            if other == movie:
                continue
            sim = max(0.0, min(1.0, 1.0 - float(distance)))
            if sim <= 0:
                continue
            common = len(movie_user_sets[movie] & movie_user_sets[other])
            top.append((other, sim, common))
        top = top[:K]
        neighbors[movie] = [
            (other, sim, common) for other, sim, common in top
            if common >= MIN_COMMON
        ]
    print("Perhitungan similarity selesai.")

    # Predict a user's rating for a target movie using similar movies they rated.
    def predict_rating(user, target_movie):
        numerator = denominator = 0.0
        for source_movie, rating in train[user].items():
            for candidate, sim, _ in neighbors[source_movie]:
                if candidate == target_movie:
                    numerator += sim * rating
                    denominator += sim
        return numerator / denominator if denominator > 0 else None

    # MAE/RMSE on test ratings that can be predicted.
    abs_errors, sq_errors = [], []
    for user, test_ratings in test.items():
        for movie, actual in test_ratings.items():
            predicted = predict_rating(user, movie)
            if predicted is not None:
                error = predicted - actual
                abs_errors.append(abs(error))
                sq_errors.append(error ** 2)

    print("\n=== EVALUASI RATING ===")
    print("Jumlah rating testing:", n_test)
    print("Jumlah rating berhasil diprediksi:", len(abs_errors))
    if abs_errors:
        print(f"MAE  : {sum(abs_errors) / len(abs_errors):.4f}")
        print(f"RMSE : {math.sqrt(sum(sq_errors) / len(sq_errors)):.4f}")
    else:
        print("MAE/RMSE tidak dapat dihitung: tidak ada prediksi.")

    # Top-N metrics: relevant test movies are those rated >= 4.
    precision_vals, recall_vals, ndcg_vals = [], [], []
    total_hits = total_relevant = 0
    evaluated_users = 0

    for user in users:
        if not test[user]:
            continue
        seen = set(train[user])
        candidates = set()

        # Candidate movies are neighbors of movies this user rated >= 4.
        for source, user_rating in train[user].items():
            if user_rating < RELEVANT_RATING:
                continue
            for candidate, sim, _ in neighbors[source]:
                if sim > 0 and candidate not in seen:
                    candidates.add(candidate)

        scored = []
        for movie in candidates:
            numerator = denominator = 0.0
            support = set()
            for source, user_rating in train[user].items():
                if user_rating < RELEVANT_RATING:
                    continue
                for candidate, sim, _ in neighbors[source]:
                    if candidate == movie and sim > 0:
                        numerator += sim * user_rating
                        denominator += sim
                        support.add(source)
            if denominator > 0:
                scored.append((movie, numerator / denominator, len(support)))

        scored.sort(key=lambda x: (-x[1], -x[2], int(x[0])))
        recommended = [m for m, _, _ in scored[:TOP_N]]
        relevant = {
            m for m, rating in test[user].items()
            if rating >= RELEVANT_RATING
        }
        if not relevant:
            continue

        hits = len(set(recommended) & relevant)
        precision_vals.append(hits / TOP_N)
        recall_vals.append(hits / len(relevant))
        total_hits += hits
        total_relevant += len(relevant)
        evaluated_users += 1

        dcg = sum(
            1.0 / math.log2(rank + 1)
            for rank, movie in enumerate(recommended, start=1)
            if movie in relevant
        )
        ideal_hits = min(len(relevant), TOP_N)
        idcg = sum(1.0 / math.log2(rank + 1) for rank in range(1, ideal_hits + 1))
        ndcg_vals.append(dcg / idcg if idcg else 0.0)

    print("\n=== EVALUASI TOP-10 ===")
    print("Jumlah user yang dievaluasi:", evaluated_users)
    if precision_vals:
        print(f"Precision@10 (Macro): {np.mean(precision_vals):.4f}")
        print(f"Recall@10    (Macro): {np.mean(recall_vals):.4f}")
        print(f"Recall@10    (Micro): {total_hits / total_relevant:.4f}" if total_relevant else "Recall@10 (Micro): N/A")
        print(f"NDCG@10      (Macro): {np.mean(ndcg_vals):.4f}")
        print("Total hit relevan:", total_hits)
        print("Total film relevan di testing:", total_relevant)
    else:
        print("Precision@10/Recall@10/NDCG@10 tidak dapat dihitung.")

    print("\nCatatan:")
    print("- Rating >= 4.0 dianggap relevan.")
    print("- Similarity dihitung dari data training saja.")
    print("- NDCG menggunakan binary relevance.")
    print("- Script hanya membaca Neo4j dan tidak mengubah graph.")


if __name__ == "__main__":
    main()
