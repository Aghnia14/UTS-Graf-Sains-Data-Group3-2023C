# USER BASED - BINARY APPROACH
# Elizabeth Hanov - 23031554055

import getpass
from collections import defaultdict

import numpy as np
import pandas as pd
from neo4j import GraphDatabase


# 1. KONFIGURASI

URI = "bolt://127.0.0.1:7687"
DATABASE = "neo4j"

K = 20
MIN_COMMON = 5
TOP_N = 10
TEST_RATIO = 0.20
RELEVANT_RATING = 4.0
SEED = 42


# 2. AMBIL DATA

def load_data():
    query = """
    MATCH (u:User)-[r:RATED]->(m:Movie)
    RETURN
        toString(u.userId) AS userId,
        toString(m.movieId) AS movieId,
        r.rating AS rating
    """

    password = getpass.getpass("Password Neo4j: ")

    with GraphDatabase.driver(
        URI, auth=("neo4j", password)
    ) as driver:
        driver.verify_connectivity()

        with driver.session(database=DATABASE) as session:
            rows = [record.data() for record in session.run(query)]

    return pd.DataFrame(
        rows, columns=["userId", "movieId", "rating"]
    )


# 3. PEMERIKSAAN DAN PEMBERSIHAN

def preprocess(df):
    df = df.copy()
    print("Jumlah baris awal:", len(df))

    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    for column in ["userId", "movieId"]:
        df[column] = df[column].astype("string").str.strip()
        df[column] = df[column].replace("", pd.NA)

    valid = (
        df["userId"].notna()
        & df["movieId"].notna()
        & df["rating"].between(0.5, 5.0)
    )

    print("Baris tidak valid:", int((~valid).sum()))
    df = df.loc[valid].copy()

    before = len(df)
    df = df.drop_duplicates(["userId", "movieId", "rating"])
    print("Duplikat identik dihapus:", before - len(df))

    conflicts = df.duplicated(
        ["userId", "movieId"], keep=False
    )

    if conflicts.any():
        examples = df.loc[conflicts].head(10)
        raise ValueError(
            "Ada pasangan user-film dengan rating berbeda.\n"
            "Periksa impor data atau gunakan rating terbaru "
            "berdasarkan timestamp sebelum evaluasi.\n"
            f"{examples.to_string(index=False)}"
        )

    df = df.sort_values(
        ["userId", "movieId"]
    ).reset_index(drop=True)

    if df.empty:
        raise ValueError("Tidak ada rating valid.")

    print("Jumlah user:", df["userId"].nunique())
    print("Jumlah rating bersih:", len(df))
    return df


# 4. TRAIN-TEST SPLIT PER USER

def split_data(df):
    rng = np.random.default_rng(SEED)
    train = defaultdict(dict)
    test = defaultdict(dict)

    for user, group in df.groupby("userId", sort=True):
        items = list(
            group[["movieId", "rating"]].itertuples(
                index=False, name=None
            )
        )
        rng.shuffle(items)

        if len(items) < 2:
            train[user] = dict(items)
            continue

        n_test = max(1, round(len(items) * TEST_RATIO))
        n_test = min(n_test, len(items) - 1)

        test[user] = dict(items[:n_test])
        train[user] = dict(items[n_test:])

    print("Rating training:", sum(map(len, train.values())))
    print("Rating testing :", sum(map(len, test.values())))

    return train, test


# 5. COSINE BINER DAN TOP-K DARI TRAINING SAJA

def calculate_neighbors(train):
    users = sorted(train, key=int)
    interactions = {
        user: set(train[user]) for user in users
    }
    neighbors = {user: [] for user in users}

    for i, user_a in enumerate(users):
        movies_a = interactions[user_a]

        for user_b in users[i + 1:]:
            movies_b = interactions[user_b]
            common = len(movies_a & movies_b)

            if common < MIN_COMMON:
                continue

            similarity = common / np.sqrt(
                len(movies_a) * len(movies_b)
            )

            neighbors[user_a].append(
                (user_b, similarity, common)
            )
            neighbors[user_b].append(
                (user_a, similarity, common)
            )

    for user in users:
        neighbors[user] = sorted(
            neighbors[user],
            key=lambda x: (-x[1], -x[2], int(x[0]))
        )[:K]

    return neighbors


# 6. SKOR FILM DARI SEMUA RATING TETANGGA

def score_movies(user, train, neighbors):
    numerator = defaultdict(float)
    denominator = defaultdict(float)
    support = defaultdict(int)

    seen = train[user]

    for neighbor, similarity, _ in neighbors[user]:
        for movie, rating in train[neighbor].items():
            if movie in seen:
                continue

            numerator[movie] += similarity * rating
            denominator[movie] += similarity
            support[movie] += 1

    scores = {
        movie: numerator[movie] / denominator[movie]
        for movie in numerator
        if denominator[movie] > 0
    }

    return scores, support


# 7. EVALUASI

def evaluate(train, test, neighbors):
    errors = []
    precision_values = []
    recall_values = []

    total_test = sum(map(len, test.values()))
    eligible_users = 0
    users_with_recommendations = 0
    recommendation_lengths = []
    user1_recommendations = []

    for user in sorted(train, key=int):
        scores, support = score_movies(
            user, train, neighbors
        )

        # MAE/RMSE: hanya pasangan yang dapat diprediksi.
        for movie, actual in test.get(user, {}).items():
            if movie in scores:
                errors.append(scores[movie] - actual)

        eligible_movies = [
            movie
            for movie in scores
            if support[movie] >= 3
        ]

        # Urutkan berdasarkan skor, jumlah pendukung, lalu movieId.
        ranked = sorted(
            eligible_movies,
            key=lambda movie: (
                -round(scores[movie], 10),
                -support[movie],
                int(movie)
            )
        )[:TOP_N]

        if user == "1":
            user1_recommendations = [
                (movie, scores[movie], support[movie])
                for movie in ranked
            ]

        relevant = {
            movie
            for movie, rating in test.get(user, {}).items()
            if rating >= RELEVANT_RATING
        }

        if not relevant:
            continue

        eligible_users += 1
        users_with_recommendations += bool(ranked)
        recommendation_lengths.append(len(ranked))

        hits = len(set(ranked) & relevant)

        precision_values.append(hits / TOP_N)
        recall_values.append(hits / len(relevant))

    print("\n=== EVALUASI RATING ===")
    print("Jumlah rating testing:", total_test)
    print("Rating berhasil diprediksi:", len(errors))

    coverage = len(errors) / total_test if total_test else 0
    print(f"Cakupan prediksi: {coverage:.2%}")

    if errors:
        errors = np.asarray(errors)
        print(f"MAE  : {np.mean(np.abs(errors)):.4f}")
        print(f"RMSE : {np.sqrt(np.mean(errors ** 2)):.4f}")
    else:
        print("MAE/RMSE tidak tersedia: tidak ada prediksi.")

    print(f"\n=== EVALUASI TOP-{TOP_N} ===")
    print("User yang dievaluasi:", eligible_users)
    print(
        "User dengan minimal satu rekomendasi:",
        users_with_recommendations
    )

    if eligible_users:
        print(
            "Rata-rata jumlah rekomendasi:",
            f"{np.mean(recommendation_lengths):.2f}"
        )
        print(
            f"Precision@{TOP_N}: "
            f"{np.mean(precision_values):.4f}"
        )
        print(
            f"Recall@{TOP_N}   : "
            f"{np.mean(recall_values):.4f}"
        )
    else:
        print("Tidak ada user dengan film relevan di testing.")

    print("\n=== REKOMENDASI USER 1 DARI TRAINING ===")
    for rank, (movie, score, count) in enumerate(
        user1_recommendations, start=1
    ):
        print(
            f"{rank:2}. movieId={movie:>6} | "
            f"skor={score:.4f} | pendukung={count}"
        )


# 8. RUN

def main():
    df = preprocess(load_data())
    train, test = split_data(df)

    neighbors = calculate_neighbors(train)
    print("Perhitungan cosine biner selesai.")

    evaluate(train, test, neighbors)


if __name__ == "__main__":
    main()
