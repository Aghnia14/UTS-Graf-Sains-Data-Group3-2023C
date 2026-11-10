
// ======================================================
// VISUALISASI REKOMENDASI FILM — NEO4J
// User-Based Weighted Collaborative Filtering
// Method: Cosine Similarity on Weighted Ratings
// ======================================================


// 1. Lima user yang paling mirip dengan User 1 | GRAPH

MATCH (target:User)
WHERE toString(target.userId) = '1'

MATCH (target)-[s:SIMILARITY]->(neighbor:User)
WHERE s.method = 'cosine_weighted_ratings'

WITH target, neighbor, s
ORDER BY s.value DESC
LIMIT 5

RETURN target, s, neighbor;


// 2. Kandidat film dari lima neighbor terdekat | GRAPH

MATCH (target:User)
WHERE toString(target.userId) = '1'

MATCH (target)-[s:SIMILARITY]->(neighbor:User)
WHERE s.method = 'cosine_weighted_ratings'
  AND s.value > 0

WITH target, neighbor, s
ORDER BY s.value DESC
LIMIT 5

MATCH (neighbor)-[r:RATED]->(m:Movie)
WHERE toFloat(r.rating) >= 4.0
  AND NOT EXISTS {
      MATCH (target)-[:RATED]->(m)
  }

RETURN target, s, neighbor, r, m
LIMIT 50;


// 3. Sepuluh rekomendasi film untuk User 1 | TABEL

MATCH (target:User)
WHERE toString(target.userId) = '1'

MATCH (target)-[s:SIMILARITY]->(neighbor:User)
WHERE s.method = 'cosine_weighted_ratings'
  AND s.value > 0

WITH target, neighbor, s
ORDER BY s.value DESC

WITH target, collect({
    neighborId: neighbor.userId,
    similarity: s.value
}) AS neighbors,
count(neighbor) AS jumlahTetangga

UNWIND neighbors AS n

MATCH (neighbor:User)
WHERE toString(neighbor.userId) = toString(n.neighborId)

MATCH (neighbor)-[r:RATED]->(m:Movie)
WHERE toFloat(r.rating) >= 4.0
  AND NOT EXISTS {
      MATCH (target)-[:RATED]->(m)
  }

WITH
    m,
    jumlahTetangga,
    sum(n.similarity * toFloat(r.rating)) AS totalBerbobot,
    sum(n.similarity) AS totalBobot,
    count(DISTINCT neighbor) AS userPendukung

RETURN
    m.movieId AS movieId,
    m.title AS judul,
    userPendukung,
    jumlahTetangga,
    round((totalBerbobot / totalBobot) * 100) / 100.0
        AS skorRekomendasi

ORDER BY skorRekomendasi DESC, userPendukung DESC
LIMIT 10;
