// VISUALISASI REKOMENDASI FILM — NEO4J
// Item-Based Weighted Collaborative Filtering

// 1. rekomendasi top 10 untuk userid 1
MATCH (u:User {userId: '1'})-[r:RATED]->(watched:Movie)
WHERE toFloat(r.rating) >= 4.0

MATCH (watched)-[s:SIMILARITY]->(candidate:Movie)
WHERE s.method = 'cosine_rating'
    AND NOT EXISTS {
        MATCH (u)-[:RATED]->(candidate)
    }

WITH candidate,
     sum(toFloat(r.rating) * s.value) AS weighted_sum,
     sum(s.value) AS similarity_sum,
     count(DISTINCT watched) AS supporting_movies

WHERE similarity_sum > 0

RETURN
    candidate.title AS recommendation,
    round((weighted_sum / similarity_sum) * 1000) / 1000 AS predicted_score,
    supporting_movies AS film_pendukung

ORDER BY predicted_score DESC, supporting_movies DESC
LIMIT 10;

// 2. riwayat film userid 1
MATCH (u:User {userId: '1'})-[r:RATED]->(m:Movie)
RETURN
    u.userId AS user_id,
    m.title AS film_yang_ditonton,
    toFloat(r.rating) AS rating
ORDER BY rating DESC, film_yang_ditonton;

// 3. film yang disukai userid 1 (rating >= 4)
MATCH (u:User {userId: '1'})-[r:RATED]->(m:Movie)
WHERE toFloat(r.rating) >= 4.0
RETURN
    m.title AS film_yang_disukai,
    toFloat(r.rating) AS rating
ORDER BY rating DESC, film_yang_disukai;

