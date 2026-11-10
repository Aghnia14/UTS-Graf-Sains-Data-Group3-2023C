
from neo4j import GraphDatabase
from getpass import getpass

import numpy as np
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors


# ==========================================
# 1. KONFIGURASI NEO4J
# ==========================================

URI = "bolt://127.0.0.1:7687"
USERNAME = "neo4j"
DATABASE = "neo4j"


# ==========================================
# 2. PARAMETER ITEM-BASED CF
# ==========================================

K = 20
MIN_COMMON_USERS = 5
METHOD = "cosine_rating"
BATCH_SIZE = 1000


# ==========================================
# 3. MENGAMBIL DATA RATING DARI NEO4J
# ==========================================

LOAD_RATINGS_QUERY = """
MATCH (u:User)-[r:RATED]->(m:Movie)
RETURN
    u.userId AS userId,
    m.movieId AS movieId,
    toFloat(r.rating) AS rating
"""


def load_ratings(tx):
    result = tx.run(LOAD_RATINGS_QUERY)

    return [
        {
            "userId": str(record["userId"]),
            "movieId": str(record["movieId"]),
            "rating": float(record["rating"]),
        }
        for record in result
        if record["rating"] is not None
    ]


# ==========================================
# 4. MEMBENTUK MATRIKS RATING
# ==========================================

def build_rating_matrix(rating_rows):
    """
    Baris   = film
    Kolom   = user
    Nilai   = rating asli
    """

    movie_ids = sorted({
        row["movieId"] for row in rating_rows
    })

    user_ids = sorted({
        row["userId"] for row in rating_rows
    })

    movie_index = {
        movie_id: index
        for index, movie_id in enumerate(movie_ids)
    }

    user_index = {
        user_id: index
        for index, user_id in enumerate(user_ids)
    }

    rows = []
    cols = []
    values = []

    for record in rating_rows:
        rows.append(movie_index[record["movieId"]])
        cols.append(user_index[record["userId"]])
        values.append(record["rating"])

    rating_matrix = csr_matrix(
        (values, (rows, cols)),
        shape=(len(movie_ids), len(user_ids)),
        dtype=np.float32
    )

    return rating_matrix, movie_ids, user_ids


# ==========================================
# 5. MENGHITUNG JUMLAH USER BERSAMA
# ==========================================

def build_interaction_matrix(rating_matrix):
    """
    Mengubah rating menjadi indikator interaksi:
    1 = user memberi rating pada film
    0 = user tidak memberi rating pada film

    Matriks ini HANYA untuk menghitung commonUsers.
    Similarity tetap dihitung menggunakan rating asli.
    """

    interaction_matrix = rating_matrix.copy()
    interaction_matrix.data = np.ones_like(
        interaction_matrix.data,
        dtype=np.int8
    )

    return interaction_matrix


# ==========================================
# 6. MENGHITUNG ITEM-BASED COSINE SIMILARITY
# ==========================================

def calculate_item_similarity(rating_matrix):
    """
    Menghitung cosine similarity antarfilm
    menggunakan rating asli, kemudian memilih
    maksimal K tetangga untuk setiap film.
    """

    n_movies = rating_matrix.shape[0]

    if n_movies < 2:
        return []

    interaction_matrix = build_interaction_matrix(
        rating_matrix
    )

    # Jumlah user yang memberi rating pada setiap film.
    movie_rating_counts = np.asarray(
        interaction_matrix.sum(axis=1)
    ).ravel()

    # Film yang memiliki kurang dari MIN_COMMON_USERS
    # rating tidak mungkin memenuhi syarat pasangan.
    eligible_indices = np.flatnonzero(
        movie_rating_counts >= MIN_COMMON_USERS
    )

    if len(eligible_indices) < 2:
        return []

    eligible_matrix = rating_matrix[eligible_indices]

    n_neighbors = min(K + 1, len(eligible_indices))

    knn = NearestNeighbors(
        n_neighbors=n_neighbors,
        metric="cosine",
        algorithm="brute",
        n_jobs=-1
    )

    knn.fit(eligible_matrix)

    distances, indices = knn.kneighbors(eligible_matrix)

    similarities = []

    for local_idx in range(len(eligible_indices)):
        movie_idx = int(eligible_indices[local_idx])

        for distance, neighbor_local_idx in zip(
            distances[local_idx],
            indices[local_idx]
        ):
            neighbor_idx = int(
                eligible_indices[neighbor_local_idx]
            )

            # Abaikan film yang sama.
            if movie_idx == neighbor_idx:
                continue

            similarity = 1.0 - float(distance)

            # Batasi nilai similarity akibat presisi numerik.
            similarity = max(0.0, min(1.0, similarity))

            if similarity <= 0:
                continue

            # Hitung user yang memberi rating pada KEDUA film.
            common_users = int(
                interaction_matrix[movie_idx]
                .multiply(interaction_matrix[neighbor_idx])
                .sum()
            )

            if common_users < MIN_COMMON_USERS:
                continue

            similarities.append({
                "movie_index": movie_idx,
                "neighbor_index": neighbor_idx,
                "similarity": similarity,
                "commonUsers": common_users
            })

    return similarities


# ==========================================
# 7. MENYIMPAN SIMILARITY KE NEO4J
# ==========================================

CLEAR_OWN_KNN_QUERY = """
MATCH (a:Movie)-[s:SIMILARITY]->(b:Movie)
WHERE s.method = $method
DELETE s
"""

STORE_SIMILARITY_QUERY = """
UNWIND $batch AS item

MATCH (a:Movie {movieId: item.movieId})
MATCH (b:Movie {movieId: item.neighborId})

MERGE (a)-[s:SIMILARITY {method: $method}]->(b)

SET s.value = item.similarity,
    s.commonUsers = item.commonUsers

RETURN count(s) AS saved
"""


def clear_old_item_similarity(tx):
    tx.run(
        CLEAR_OWN_KNN_QUERY,
        method=METHOD
    ).consume()


def store_similarity_batch(tx, batch):
    result = tx.run(
        STORE_SIMILARITY_QUERY,
        batch=batch,
        method=METHOD
    )

    return result.single()["saved"]


# ==========================================
# 8. FUNGSI UTAMA
# ==========================================

def main():
    password = getpass("Password Neo4j: ")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, password)
    )

    try:
        driver.verify_connectivity()
        print("Koneksi Neo4j berhasil.")

        with driver.session(database=DATABASE) as session:
            print("Mengambil data rating dari Neo4j...")

            rating_rows = session.execute_read(load_ratings)

            if not rating_rows:
                print("Tidak ada data rating yang ditemukan.")
                return

            print(f"Total data rating: {len(rating_rows):,}")

            rating_matrix, movie_ids, user_ids = (
                build_rating_matrix(rating_rows)
            )

            print(f"Total film dengan rating: {len(movie_ids):,}")
            print(f"Total user dengan rating: {len(user_ids):,}")

            print("Menghitung Item-Based Cosine Similarity...")

            similarities = calculate_item_similarity(
                rating_matrix
            )

            print(
                f"Total pasangan similarity yang memenuhi syarat: "
                f"{len(similarities):,}"
            )

            if not similarities:
                print(
                    "Tidak ada pasangan similarity yang memenuhi syarat. "
                    "Database tidak diubah."
                )
                return

            # Hapus hanya relasi Movie-Movie yang dibuat
            # dengan metode cosine_rating.
            print("Membersihkan hasil Item-Based CF sebelumnya...")

            session.execute_write(
                clear_old_item_similarity
            )

            total_saved = 0

            print("Menyimpan similarity ke Neo4j...")

            for start in range(
                0, len(similarities), BATCH_SIZE
            ):
                batch_results = similarities[
                    start:start + BATCH_SIZE
                ]

                batch = [
                    {
                        "movieId": movie_ids[item["movie_index"]],
                        "neighborId": movie_ids[item["neighbor_index"]],
                        "similarity": item["similarity"],
                        "commonUsers": item["commonUsers"]
                    }
                    for item in batch_results
                ]

                saved = session.execute_write(
                    store_similarity_batch,
                    batch
                )

                total_saved += saved

                print(
                    f"Tersimpan: {total_saved:,} / "
                    f"{len(similarities):,}"
                )

            print("\nProses Item-Based CF selesai.")
            print(
                f"Total relasi similarity tersimpan: "
                f"{total_saved:,}"
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()
