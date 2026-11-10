# Item-Based Collaborative Filtering — MovieLens

## 1. Hasil Perhitungan Similarity

Perhitungan kemiripan antarfilm dilakukan menggunakan metode **Cosine Similarity** berdasarkan pola rating pengguna. Setiap film direpresentasikan sebagai vektor rating pengguna, kemudian dibandingkan dengan film lainnya.

Konfigurasi yang digunakan:
- Metode similarity: **Cosine Similarity pada rating asli** (`cosine_rating`).
- Jumlah neighbor maksimum: **20 (K=20)**.
- Minimum pengguna yang sama: **5 (MIN_COMMON_USERS=5)**.
- Jumlah rating pada dataset: **100.836**.
- Jumlah pengguna: **610**.
- Jumlah film pada graph: **9.742**.

Pada implementasi ini, sistem mengambil hingga 20 neighbor terdekat terlebih dahulu, kemudian menyaring pasangan yang memiliki kurang dari 5 pengguna bersama. Hasil similarity disimpan di Neo4j sebagai relasi `SIMILARITY` dengan properti:
- `value`: nilai cosine similarity antarfilm.
- `commonUsers`: jumlah pengguna yang memberikan rating pada kedua film.
- `method`: metode perhitungan, yaitu `cosine_rating`.

Berdasarkan hasil penyimpanan yang tercatat, terdapat **40.664 relasi similarity berarah** pada graph Neo4j.

## 2. Contoh Hasil Kemiripan Film

Sebagai contoh penelusuran, film *Avengers: Infinity War* digunakan sebagai film acuan. Query Neo4j mengambil film-film yang memiliki relasi `SIMILARITY` dengan film tersebut, kemudian mengurutkannya berdasarkan nilai similarity tertinggi.

Hasil query menampilkan:
- Judul film acuan.
- Judul film yang memiliki kemiripan.
- Nilai cosine similarity.
- Jumlah pengguna yang sama-sama memberikan rating.

Nilai similarity yang lebih tinggi menunjukkan pola rating yang lebih searah pada pengguna yang sama-sama menilai kedua film. Sementara itu, `commonUsers` menunjukkan jumlah pengguna yang menjadi dasar perbandingan. Nilai similarity tidak secara langsung menyatakan bahwa kedua film memiliki genre atau cerita yang sama.

*Catatan: tabel peringkat dan nilai similarity untuk Avengers: Infinity War dapat ditambahkan dari hasil aktual query Neo4j.*

## 3. Visualisasi Graph Neo4j

Hasil perhitungan similarity disimpan dalam Neo4j sehingga hubungan antarfilm dapat ditampilkan dalam bentuk graph. Setiap node `Movie` merepresentasikan sebuah film, sedangkan relasi `SIMILARITY` menghubungkan film dengan film lain yang memiliki kemiripan.

Visualisasi dapat digunakan untuk memperlihatkan:
1. Film acuan, yaitu *Avengers: Infinity War*.
2. Film-film yang memiliki hubungan similarity dengan film acuan.
3. Nilai similarity dan jumlah pengguna bersama pada setiap relasi.

Untuk dokumentasi repository, screenshot hasil Neo4j dapat disimpan pada folder `screenshots/`, misalnya:
- `similarity_result.png`: hasil similarity dalam bentuk tabel.
- `neo4j_similarity_graph.png`: visualisasi hubungan kemiripan antarfilm.

## 4. Proses Rekomendasi Film

Sistem rekomendasi menggunakan pendekatan **Item-Based Collaborative Filtering dengan Weighted Rating Prediction**. Setelah relasi kemiripan antarfilm tersedia, sistem dapat menghasilkan rekomendasi berdasarkan film-film yang sebelumnya disukai pengguna.

Pada contoh rekomendasi untuk User 1, tahapan yang dilakukan adalah:

1. Mengambil film yang telah diberi rating minimal **4,0** oleh User 1.
2. Mencari film kandidat yang memiliki relasi similarity dengan film-film tersebut.
3. Menghapus kandidat yang sudah pernah diberi rating oleh User 1.
4. Menghitung prediksi rating menggunakan nilai rating pengguna dan similarity antarfilm.
5. Mengurutkan kandidat berdasarkan prediksi rating, kemudian jumlah film pendukung.
6. Menampilkan maksimal 10 film sebagai rekomendasi Top-10.

Prediksi rating dihitung menggunakan rata-rata berbobot:

\[
\hat{r}_{u,i} =
\frac{\sum_{j \in N(i;u)} r_{u,j} \times s_{i,j}}
{\sum_{j \in N(i;u)} s_{i,j}}
\]

Keterangan:
- \(\hat{r}_{u,i}\): prediksi rating pengguna \(u\) terhadap film \(i\).
- \(r_{u,j}\): rating pengguna \(u\) terhadap film yang telah dinilai, yaitu film \(j\).
- \(s_{i,j}\): nilai similarity antara film kandidat \(i\) dan film yang telah dinilai \(j\).
- \(N(i;u)\): film-film yang telah dinilai pengguna dan memiliki hubungan similarity dengan film kandidat.

Dengan demikian, film yang memiliki kemiripan tinggi dengan film yang disukai pengguna dapat memperoleh prediksi rating yang lebih tinggi. Jumlah film pendukung menunjukkan banyaknya film yang berkontribusi pada perhitungan prediksi, bukan jumlah pengguna yang menyukai kandidat tersebut.

## 5. Evaluasi Model

Evaluasi Item-Based Collaborative Filtering yang tercatat sebelumnya menggunakan pembagian data rating secara acak dengan proporsi **80% training** dan **20% testing**, serta `random_state=42`. Similarity dihitung menggunakan data training, kemudian prediksi dievaluasi pada pasangan user-film dalam data testing yang berhasil diprediksi.

### 5.1. Hasil Evaluasi Prediksi Rating

| Komponen | Hasil |
|---|---:|
| Total rating | 100.836 |
| Data training | 80.668 |
| Data testing | 20.168 |
| Rating berhasil diprediksi | 14.301 |
| Rating tidak berhasil diprediksi | 5.867 |
| Cakupan prediksi | 70,91% |
| MAE | 0,6619 |
| RMSE | 0,8955 |

- **MAE sebesar 0,6619** menunjukkan rata-rata selisih absolut antara rating prediksi dan rating aktual sekitar 0,66 poin.
- **RMSE sebesar 0,8955** mengukur kesalahan prediksi dengan memberikan penalti lebih besar terhadap kesalahan yang tinggi.
- **Cakupan prediksi sebesar 70,91%** menunjukkan bahwa model berhasil menghasilkan prediksi untuk 14.301 dari 20.168 rating testing.

MAE dan RMSE dihitung hanya pada pasangan user-film yang berhasil diprediksi. Karena itu, metrik error tersebut tidak mewakili seluruh rating pada data testing.

### 5.2. Perbandingan dengan Baseline

| Metrik | Item-Based CF | Baseline |
|---|---:|---:|
| MAE | 0,6619 | 0,7201 |
| RMSE | 0,8955 | 0,9291 |

Pada evaluasi yang tercatat, Item-Based Collaborative Filtering menghasilkan MAE dan RMSE yang lebih rendah dibandingkan baseline pada pasangan data testing yang sama-sama berhasil diprediksi. Hasil ini menunjukkan bahwa prediksi berbasis similarity memberikan perbaikan terhadap baseline pada cakupan pasangan tersebut.

*Catatan: angka evaluasi di atas berasal dari eksperimen pembagian data global 80:20. Jika menggunakan script evaluasi terbaru dengan pembagian per pengguna dan metrik ranking, hasilnya perlu diperbarui berdasarkan output aktual script tersebut.*

### 5.3. Evaluasi Rekomendasi Top-10

Metrik evaluasi ranking seperti **Precision@10, Recall@10, dan NDCG@10** dapat digunakan untuk menilai relevansi daftar rekomendasi terhadap film yang terdapat pada data testing. Nilai metrik tersebut belum dicantumkan di dokumen ini karena hasil aktual dari script evaluasi terbaru belum tersedia.

## 6. Kesimpulan

Implementasi Item-Based Collaborative Filtering berhasil membangun hubungan kemiripan antarfilm menggunakan Cosine Similarity berdasarkan pola rating pengguna. Dengan konfigurasi K=20 dan minimum 5 pengguna bersama, sistem menyimpan 40.664 relasi similarity berarah ke Neo4j. Relasi tersebut dapat digunakan untuk menelusuri film-film yang memiliki pola rating serupa.

Pada proses rekomendasi, sistem menggabungkan informasi rating film yang telah disukai pengguna dengan nilai similarity untuk menghitung prediksi rating menggunakan Weighted Rating Prediction. Kandidat yang sudah pernah dinilai pengguna dikecualikan, kemudian film diurutkan untuk menghasilkan rekomendasi Top-10.

Pada eksperimen evaluasi yang tercatat, model memperoleh MAE sebesar **0,6619**, RMSE sebesar **0,8955**, dan cakupan prediksi sebesar **70,91%**. Nilai MAE dan RMSE lebih rendah dibandingkan baseline yang digunakan pada eksperimen tersebut. Hasil ini menunjukkan bahwa pendekatan similarity antarfilm dapat membantu memperkirakan rating pengguna terhadap film yang belum dinilai.

Secara keseluruhan, sistem telah mengimplementasikan proses Item-Based Collaborative Filtering mulai dari perhitungan similarity, penyimpanan hubungan antarfilm di Neo4j, hingga pembentukan rekomendasi berbasis weighted prediction. Evaluasi lebih lanjut dengan protokol pembagian data yang sama dan metrik ranking diperlukan untuk menilai kualitas rekomendasi secara lebih menyeluruh serta membandingkannya secara adil dengan pendekatan User-Based Collaborative Filtering.

## 7. Keterbatasan

- Film yang memiliki kurang dari 5 pengguna bersama tidak memenuhi syarat untuk disimpan sebagai relasi similarity.
- Sistem mengambil hingga 20 neighbor terdekat terlebih dahulu, kemudian menerapkan filter minimum common users. Karena itu, jumlah neighbor yang tersimpan dapat kurang dari 20.
- Prediksi rating hanya dapat dilakukan jika terdapat film yang telah dinilai pengguna dan memiliki relasi similarity dengan film kandidat.
- Cakupan prediksi pada eksperimen yang tercatat adalah 70,91%; sebagian pasangan user-film pada data testing tidak memperoleh prediksi.
- Nilai MAE dan RMSE hanya dihitung pada pasangan yang berhasil diprediksi.
- Hasil evaluasi global 80:20 tidak boleh langsung dibandingkan dengan hasil User-Based CF yang menggunakan pembagian data per pengguna. Protokol pembagian data dan pengaturan evaluasi perlu disamakan terlebih dahulu.

## 8. File Proyek

| File | Keterangan |
|---|---|
| `item_based_cf.py` | Script perhitungan cosine similarity antarfilm dan penyimpanan relasi ke Neo4j. |
| `evaluasi_item_based.py` | Script evaluasi model Item-Based Collaborative Filtering. |
| `similarity_queries.cypher` | Query Cypher untuk melihat hasil similarity dan visualisasi hubungan antarfilm. |
| `recommendation_queries.cypher` | Query Cypher untuk menampilkan riwayat rating dan rekomendasi film pengguna. |
| `CONCLUSION.md` | Dokumentasi hasil, evaluasi, dan kesimpulan Item-Based Collaborative Filtering. |
