# 10 film paling mirip avengers: infinity war
MATCH (m:Movie {movieId: '122912'})-[s:SIMILARITY]->(similar:Movie)
WHERE s.method = 'cosine_rating'
RETURN
    m.title AS film,
    similar.title AS film_mirip,
    round(s.value * 1000) / 1000 AS similarity,
    s.commonUsers AS common_users
ORDER BY s.value DESC
LIMIT 10;

# graf hubungan film
MATCH (m:Movie {movieId: '122912'})-[s:SIMILARITY]->(similar:Movie)
WHERE s.method = 'cosine_rating'
RETURN m, s, similar
ORDER BY s.value DESC
LIMIT 10;