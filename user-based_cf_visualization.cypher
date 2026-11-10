// VISUALISASI REKOMENDASI FILM — NEO4J
// User - Based Binary Collaborative Filtering
//Elizabeth Hanov - 23031554055

// 0. Periksa data | TABEL
MATCH (:User)-[s:SIMILARITY]->(:User)
RETURN s.method AS metode, count(s) AS jumlahRelasi
ORDER BY jumlahRelasi DESC;

// 1. Gambaran KNN: lima user, masing-masing tiga tetangga | GRAPH
MATCH (u:User)
WHERE toInteger(u.userId) IN [1, 2, 3, 4, 5]
MATCH (u)-[s:SIMILARITY]->(n:User)
WHERE s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, n, s
ORDER BY toInteger(u.userId), s.value DESC,
         s.commonMovies DESC, toInteger(n.userId)
WITH u, collect({neighbor: n, similarity: s})[0..3] AS terdekat
UNWIND terdekat AS item
RETURN u, item.similarity AS similarity, item.neighbor AS tetangga;

// 2. Riwayat user 1: 20 film dengan rating tertinggi | TABEL
MATCH (u:User)-[r:RATED]->(m:Movie)
WHERE toString(u.userId) = '1' AND toFloat(r.rating) IS NOT NULL
WITH u, r, m
ORDER BY toFloat(r.rating) DESC, toInteger(m.movieId)
LIMIT 20
RETURN m.movieId AS movieId, m.title AS judul,
       toFloat(r.rating) AS ratingUser1
ORDER BY ratingUser1 DESC, toInteger(movieId);

// 2. Riwayat user 1: 20 film dengan rating tertinggi | GRAPH
MATCH (u:User)-[r:RATED]->(m:Movie)
WHERE toString(u.userId) = '1' AND toFloat(r.rating) IS NOT NULL
WITH u, r, m
ORDER BY toFloat(r.rating) DESC, toInteger(m.movieId)
LIMIT 20
RETURN u, r, m;

// 3. Satu tetangga paling dekat dengan user 1 | GRAPH
MATCH (u:User)-[s:SIMILARITY]->(n:User)
WHERE toString(u.userId) = '1'
  AND s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, s, n
ORDER BY s.value DESC, s.commonMovies DESC, toInteger(n.userId)
LIMIT 1
RETURN u, s, n;

// 4. Daftar lima tetangga paling mirip dengan user 1 | TABEL
MATCH (u:User)-[s:SIMILARITY]->(n:User)
WHERE toString(u.userId) = '1'
  AND s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, s, n
ORDER BY s.value DESC, s.commonMovies DESC, toInteger(n.userId)
LIMIT 5
RETURN n.userId AS userTetangga,
       s.value AS cosineSimilarity,
       s.commonMovies AS jumlahFilmBersama
ORDER BY cosineSimilarity DESC, jumlahFilmBersama DESC,
         toInteger(userTetangga);

// 4. Daftar lima tetangga paling mirip dengan user 1 | GRAPH
MATCH (u:User)-[s:SIMILARITY]->(n:User)
WHERE toString(u.userId) = '1'
  AND s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, s, n
ORDER BY s.value DESC, s.commonMovies DESC, toInteger(n.userId)
LIMIT 5
RETURN u, s, n;

// 5. Mengapa mereka mirip? Tampilkan film bersama | GRAPH
MATCH (u:User)-[s:SIMILARITY]->(n:User)
WHERE toString(u.userId) = '1'
  AND s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, s, n
ORDER BY s.value DESC, s.commonMovies DESC, toInteger(n.userId)
LIMIT 5
MATCH (u)-[ru:RATED]->(m:Movie)<-[rn:RATED]-(n)
WITH u, s, n, m, ru, rn
ORDER BY toInteger(n.userId), toFloat(ru.rating) DESC,
         toFloat(rn.rating) DESC, toInteger(m.movieId)
WITH u, s, n, collect({movie: m, ratingUser: ru, ratingNeighbor: rn})[0..2] AS contoh
UNWIND contoh AS item
RETURN u, s, n, item.movie AS filmBersama,
       item.ratingUser AS ratingUser1,
       item.ratingNeighbor AS ratingTetangga;

// 6. Sepuluh rekomendasi film untuk user 1 | TABEL
MATCH (u:User)-[s:SIMILARITY]->(n:User)
WHERE toString(u.userId) = '1'
  AND s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, s, n
ORDER BY s.value DESC, s.commonMovies DESC, toInteger(n.userId)
LIMIT 5
MATCH p = (u)-[s]->(n)-[r:RATED]->(m:Movie)
WHERE toFloat(r.rating) >= 4.0
  AND NOT (u)-[:RATED]->(m)
WITH u, m,
     sum(s.value * toFloat(r.rating)) AS totalBerbobot,
     sum(s.value) AS totalBobot,
     count(DISTINCT n) AS jumlahPendukung,
     collect(DISTINCT n.userId) AS idPendukung,
     collect(p) AS jalurPendukung
WHERE totalBobot > 0
WITH u, m, totalBerbobot / totalBobot AS skor,
     jumlahPendukung, idPendukung, jalurPendukung
ORDER BY skor DESC, toInteger(m.movieId)
LIMIT 10
RETURN m.movieId AS movieId, m.title AS judul,
       skor AS skorRekomendasi,
       jumlahPendukung, idPendukung
ORDER BY skorRekomendasi DESC, toInteger(movieId);

// 7. Graph rekomendasi beserta asal rekomendasinya | GRAPH
MATCH (u:User)-[s:SIMILARITY]->(n:User)
WHERE toString(u.userId) = '1'
  AND s.method = 'cosine_binary_interactions'
  AND s.value > 0 AND u <> n
WITH u, s, n
ORDER BY s.value DESC, s.commonMovies DESC, toInteger(n.userId)
LIMIT 5
MATCH p = (u)-[s]->(n)-[r:RATED]->(m:Movie)
WHERE toFloat(r.rating) >= 4.0
  AND NOT (u)-[:RATED]->(m)
WITH u, m,
     sum(s.value * toFloat(r.rating)) AS totalBerbobot,
     sum(s.value) AS totalBobot,
     count(DISTINCT n) AS jumlahPendukung,
     collect(DISTINCT n.userId) AS idPendukung,
     collect(p) AS jalurPendukung
WHERE totalBobot > 0
WITH u, m, totalBerbobot / totalBobot AS skor,
     jumlahPendukung, idPendukung, jalurPendukung
ORDER BY skor DESC, toInteger(m.movieId)
LIMIT 10
UNWIND jalurPendukung AS jalur
RETURN jalur, m.title AS judul, skor AS skorRekomendasi
ORDER BY skorRekomendasi DESC, judul;
