# User-Based Weighted Collaborative Filtering — MovieLens

## Hasil Perhitungan Similarity

Perhitungan pada seluruh dataset menghasilkan:
- Jumlah pengguna: **610**
- Total pasangan pengguna yang mungkin dibandingkan: **185.745**
- Pasangan yang memenuhi minimum 5 film bersama: **108.202**
- Jumlah relasi Top-K yang disimpan ke Neo4j: **12.183**
- Jumlah neighbor maksimum per pengguna: **20**

### Contoh Top-20 Neighbor untuk User 1

Berikut 20 pengguna dengan similarity tertinggi terhadap User 1 berdasarkan perhitungan pada seluruh dataset.

| Peringkat | User tetangga | Similarity | Film bersama |
|---:|---:|---:|---:|
| 1 | 77 | 1.000000 | 6 |
| 2 | 511 | 0.999193 | 6 |
| 3 | 366 | 0.998633 | 5 |
| 4 | 114 | 0.998060 | 6 |
| 5 | 65 | 0.997825 | 5 |
| 6 | 49 | 0.996963 | 7 |
| 7 | 258 | 0.996546 | 5 |
| 8 | 180 | 0.996287 | 10 |
| 9 | 523 | 0.996205 | 6 |
| 10 | 9 | 0.995739 | 5 |
| 11 | 300 | 0.995508 | 8 |
| 12 | 398 | 0.995100 | 6 |
| 13 | 401 | 0.994953 | 5 |
| 14 | 189 | 0.994909 | 7 |
| 15 | 530 | 0.994893 | 8 |
| 16 | 319 | 0.994282 | 5 |
| 17 | 13 | 0.994282 | 6 |
| 18 | 582 | 0.994025 | 5 |
| 19 | 25 | 0.993976 | 7 |
| 20 | 515 | 0.993940 | 7 |

Pada hasil tersebut, User 77 memiliki similarity tertinggi terhadap User 1, yaitu **1,000000**, berdasarkan 6 film yang sama-sama dinilai. Nilai ini menunjukkan bahwa vektor rating kedua pengguna pada film-film yang sama tersebut memiliki arah yang identik; bukan berarti seluruh preferensi film kedua pengguna pasti sama.

## Visualisasi Neo4j

Hasil similarity disimpan dalam relasi `SIMILARITY` dengan properti:
- `value`: nilai Weighted Cosine Similarity.
- `commonMovies`: jumlah film yang sama-sama dinilai.
- `method`: `cosine_weighted_ratings`.

Visualisasi di Neo4j digunakan untuk memperlihatkan:
1. Hubungan User 1 dengan lima neighbor terdekat.
2. Kandidat film yang memperoleh rating minimal 4,0 dari neighbor dan belum pernah dinilai oleh User 1.
3. Hasil rekomendasi Top-10 untuk User 1 dalam bentuk tabel.

Simpan screenshot hasil Neo4j pada folder `screenshots/` dengan nama berikut agar dapat ditampilkan di GitHub:

## Evaluasi Model

Evaluasi dilakukan dengan membagi rating per pengguna menjadi **80% training** dan **20% testing**. Similarity dihitung ulang hanya menggunakan data training agar data testing tidak digunakan dalam pembentukan model.

### Hasil Evaluasi Prediksi Rating

Jumlah rating testing: 20.164 
Rating berhasil diprediksi: 7.387
Cakupan prediksi: 36,63% 
MAE: 0,8219 
RMSE: 1,0929 

- **MAE 0,8219** menunjukkan rata-rata selisih absolut antara rating prediksi dan rating aktual sekitar 0,82 poin.
- **RMSE 1,0929** mengukur kesalahan prediksi dengan penalti lebih besar terhadap kesalahan yang tinggi.
- Model berhasil memprediksi 7.387 dari 20.164 rating testing, dengan cakupan **36,63%**.

MAE dan RMSE dihitung hanya pada pasangan user-film yang dapat diprediksi, bukan pada seluruh rating testing.

### Hasil Evaluasi Rekomendasi Top-10

User yang dievaluasi: 603 
User dengan minimal satu rekomendasi: 602 
Rata-rata jumlah rekomendasi: 9,97 
Precision@10: 0,0633 
Recall@10: 0,0354 

- **Precision@10 sebesar 0,0633** menunjukkan rata-rata proporsi film relevan dalam daftar 10 rekomendasi sekitar 6,33%.
- **Recall@10 sebesar 0,0354** menunjukkan rata-rata proporsi film relevan pada data testing yang berhasil ditemukan dalam daftar rekomendasi sekitar 3,54%.
- Hampir seluruh pengguna yang dievaluasi memperoleh setidaknya satu rekomendasi, dengan rata-rata 9,97 film per pengguna.

Precision@10 dan Recall@10 menggunakan macro-average pada pengguna yang memiliki setidaknya satu film relevan di data testing. Slot rekomendasi yang tidak terisi tetap dihitung sebagai tidak relevan dalam Precision@10.

## Kesimpulan

Berdasarkan implementasi, pendekatan User-Based Weighted Collaborative Filtering berhasil membangun hubungan kemiripan antar pengguna berdasarkan nilai rating film yang sama-sama dinilai. Pada contoh User 1, User 77 menjadi neighbor terdekat dengan similarity **1,000000** dan 6 film bersama. Sistem juga berhasil menyimpan **12.183 relasi Weighted Similarity** ke Neo4j dan menampilkan hubungan antar pengguna serta kandidat film melalui visualisasi graph.

Pada evaluasi prediksi rating, model memperoleh MAE sebesar **0,8219** dan RMSE sebesar **1,0929**, dengan cakupan prediksi **36,63%** dari keseluruhan rating testing. Pada evaluasi rekomendasi Top-10, model memperoleh Precision@10 sebesar **0,0633** dan Recall@10 sebesar **0,0354**. Sebanyak 602 dari 603 pengguna yang dievaluasi memperoleh setidaknya satu rekomendasi.

Hasil tersebut menunjukkan bahwa model dapat menghasilkan rekomendasi bagi hampir seluruh pengguna yang memenuhi kriteria evaluasi. Namun, cakupan prediksi dan nilai metrik ranking menunjukkan masih terdapat ruang untuk meningkatkan kemampuan model dalam memprediksi rating dan menemukan lebih banyak film relevan.

## Keterbatasan

- Prediksi rating hanya dapat dilakukan apabila neighbor memiliki rating pada film yang dievaluasi.
- Pengguna dengan sedikit film bersama dapat memiliki jumlah neighbor terbatas karena syarat minimal 5 film bersama.
- Rekomendasi evaluasi menggunakan batas minimal 3 neighbor pendukung.
- Hasil evaluasi bergantung pada pembagian training-testing dan parameter yang digunakan.
- Top-20 neighbor yang ditampilkan pada bagian hasil similarity berasal dari perhitungan seluruh dataset, sedangkan evaluasi menghitung ulang similarity hanya dari data training. Keduanya memiliki tujuan yang berbeda.
- Hasil ini belum membuktikan bahwa model lebih baik daripada pendekatan lain tanpa evaluasi pembanding dengan protokol yang sama.

## ile Proyek

| `user-based-weighted-cf.ipynb`: eksplorasi data, preprocessing, perhitungan similarity, rekomendasi, dan evaluasi
| `user-based-weighted_visualization.cypher`: Query Cypher untuk visualisasi dan rekomendasi di Neo4j
| `user-based-weighted-conclusion.md`: kesimpulan hasil
