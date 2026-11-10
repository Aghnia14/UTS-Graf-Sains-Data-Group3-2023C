# Pembahasan Graph dan Evaluasi Sistem Rekomendasi Film

## 1. Hasil Visualisasi Graph Neo4j

Berdasarkan hasil query dan visualisasi Neo4j, sistem **user-based collaborative filtering berhasil membentuk hubungan kemiripan antar pengguna dan menghasilkan rekomendasi film untuk user 1**. Database menyimpan **12.200 relasi `SIMILARITY`** dengan metode `cosine_binary_interactions`. Metode ini mengukur kemiripan berdasarkan kesamaan film yang pernah diberi rating, tanpa mempertimbangkan besar rating dalam perhitungan similarity. Oleh karena itu, kemiripan yang diperoleh menunjukkan kesamaan riwayat interaksi, bukan secara langsung kesamaan penilaian terhadap film.

### 1.1. Hasil Pencarian Tetangga Terdekat

Lima tetangga terdekat user 1 adalah sebagai berikut.

| ID tetangga | Cosine similarity | Jumlah film bersama |
|---|---:|---:|
| 313 | 0,3810 | 107 |
| 330 | 0,3384 | 81 |
| 57 | 0,3370 | 112 |
| 469 | 0,3349 | 110 |
| 39 | 0,3348 | 51 |

**User 313 merupakan tetangga terdekat**, meskipun jumlah film bersamanya lebih sedikit daripada user 57. Hal ini menunjukkan bahwa cosine similarity tidak hanya memperhitungkan jumlah film bersama, tetapi juga menyesuaikannya dengan jumlah keseluruhan film yang diberi rating oleh masing-masing pengguna.

Tabel dan graph riwayat film user 1 memperlihatkan film-film yang memperoleh penilaian tinggi, seperti *Seven*, *The Usual Suspects*, dan *Star Wars: Episode IV – A New Hope*. Sementara itu, visualisasi film bersama memperlihatkan hubungan antara user 1, tetangganya, dan film yang sama-sama mereka beri rating. Hubungan tersebut membantu menjelaskan dasar kemiripan antar pengguna.

### 1.2. Hasil Rekomendasi Film pada Graph

Berdasarkan lima tetangga terdekat, sistem menghasilkan **10 rekomendasi film yang belum diberi rating oleh user 1**. Beberapa di antaranya adalah *The Postman*, *Taxi Driver*, *Blade Runner*, dan *True Romance*. Film yang belum diberi rating tidak selalu berarti belum pernah ditonton oleh pengguna.

Skor rekomendasi dihitung menggunakan rata-rata rating berbobot similarity, dengan hanya memasukkan rating tetangga minimal 4. Pada bagian tabel yang terlihat, film-film memperoleh skor **5,0**, tetapi jumlah pendukungnya berbeda. Sebagai contoh, *Blade Runner* didukung oleh tiga tetangga, yaitu user 313, 57, dan 469, sedangkan *True Romance* didukung oleh dua tetangga, yaitu user 330 dan 469. Dengan demikian, skor yang sama belum tentu memiliki jumlah dukungan yang sama.

### 1.3. Interpretasi Visualisasi Graph

Visualisasi graph memperjelas asal rekomendasi melalui jalur **user 1 → tetangga → film**. Graph akhir menampilkan **15 node**, yang terdiri atas 10 node film dan 5 node pengguna, yaitu user 1 beserta empat tetangga yang berkontribusi. Hubungan yang ditampilkan terdiri atas **4 relasi `SIMILARITY` dan 13 relasi `RATED`**.

User 39 termasuk dalam lima tetangga terdekat, tetapi tidak muncul pada graph rekomendasi akhir. Berdasarkan aturan query, hal ini menunjukkan bahwa user 39 tidak memiliki rating yang memenuhi syarat kontribusi untuk sepuluh film yang terpilih. Jadi, tidak semua tetangga terdekat harus berkontribusi terhadap hasil rekomendasi akhir.


## 2. Evaluasi Sistem Rekomendasi

Setelah hubungan pengguna dan asal rekomendasi ditinjau melalui graph, evaluasi dilakukan menggunakan pemisahan data training dan testing. Kedua tahap menggunakan cosine biner, tetapi pengaturan rekomendasinya berbeda sehingga daftar filmnya tidak harus sama.

| Aspek | Visualisasi graph sebelumnya | Evaluasi terakhir |
|---|---|---|
| Data pembentuk similarity | Seluruh data tersimpan | Data training saja |
| Tetangga untuk rekomendasi | 5 tetangga | Maksimal 20 tetangga |
| Rating yang menyumbang skor | Rating minimal 4 | Semua rating tetangga yang tersedia |
| Minimal pendukung kandidat | 1 | 3 |
| Film yang dikecualikan | Sudah diberi rating pada seluruh data user 1 | Sudah diberi rating pada training user |
| Tujuan | Menjelaskan hubungan dan asal rekomendasi | Mengukur prediksi dan kecocokan dengan testing |

Evaluasi ini menggunakan cosine similarity biner untuk memilih maksimal 20 tetangga berdasarkan data training, dengan minimal 5 film bersama. Prediksi rating dihitung dari rata-rata rating tetangga berbobot similarity. Pada pemilihan rekomendasi akhir, kandidat harus memiliki minimal tiga tetangga pendukung. Skor yang praktis sama diurutkan berdasarkan jumlah pendukung, kemudian ID film.

### 2.1. Pemeriksaan dan Pembagian Data

| Komponen | Jumlah |
|---|---:|
| Baris awal | 100.836 |
| Baris tidak valid | 0 |
| Duplikat identik yang dihapus | 0 |
| Pengguna | 610 |
| Rating bersih | 100.836 |
| Rating training | 80.672 |
| Rating testing | 20.164 |

Tidak ditemukan baris tidak valid atau duplikat identik berdasarkan pemeriksaan pada script. Data dibagi per pengguna menjadi sekitar 80% training dan 20% testing. Perhitungan cosine similarity dan pemilihan tetangga hanya menggunakan data training agar rating testing tidak ikut membentuk model.

### 2.2. Hasil Evaluasi Prediksi Rating

| Metrik | Hasil |
|---|---:|
| Rating testing | 20.164 |
| Rating berhasil diprediksi oleh CF | 17.524 |
| Rating tidak berhasil diprediksi | 2.640 |
| Cakupan prediksi | 86,91% |
| MAE | 0,7690 |
| RMSE | 0,9991 |

Sistem berhasil memprediksi 86,91% pasangan pengguna–film pada data testing. Nilai MAE sebesar 0,7690 menunjukkan rata-rata selisih absolut prediksi dengan rating aktual sekitar 0,77 poin. RMSE sebesar 0,9991 memberikan penalti lebih besar pada kesalahan prediksi yang besar.

MAE dan RMSE tersebut hanya dihitung dari 17.524 pasangan yang dapat diprediksi, bukan seluruh rating testing. Sebanyak 2.640 pasangan tidak dapat diprediksi karena tidak memiliki kontribusi rating dari tetangga terpilih pada data training. Baik atau buruknya nilai error perlu dinilai dengan pembanding pada pembagian data yang sama.

### 2.3. Hasil Evaluasi Rekomendasi Top-10

| Komponen atau metrik | Hasil |
|---|---:|
| Pengguna yang dievaluasi | 604 |
| Pengguna dengan minimal satu rekomendasi | 604 |
| Rata-rata jumlah rekomendasi | 10,00 |
| Precision@10 | 0,0535 atau 5,35% |
| Recall@10 | 0,0716 atau 7,16% |

Evaluasi top-10 dilakukan pada 604 pengguna yang memiliki setidaknya satu film relevan di data testing. Film relevan didefinisikan sebagai film dengan rating aktual minimal 4. Precision dan recall dirata-ratakan antar pengguna (macro-average).

Precision@10 sebesar 5,35% berarti rata-rata sekitar 0,535 dari sepuluh rekomendasi per pengguna cocok dengan film relevan pada data testing. Recall@10 sebesar 7,16% berarti sistem menemukan rata-rata 7,16% dari film relevan milik masing-masing pengguna pada data testing. Semua pengguna yang dievaluasi tetap mendapatkan sepuluh rekomendasi meskipun diterapkan syarat minimal tiga pendukung.

Film rekomendasi yang tidak terdapat dalam kumpulan film relevan testing tidak dihitung sebagai kecocokan. Hal tersebut tidak otomatis membuktikan bahwa pengguna tidak menyukai film itu. Karena itu, metrik ini tidak sama dengan persentase kepuasan pengguna maupun akurasi klasifikasi.

### 2.4. Perbandingan Sebelum dan Sesudah Perubahan Pemilihan Rekomendasi

Perbandingan berikut menggunakan hasil dua percobaan cosine biner dengan pembagian data yang sama. Perubahan mencakup syarat minimal tiga tetangga pendukung dan pembulatan skor hingga sepuluh angka desimal untuk pengurutan, sehingga perbedaan numerik yang sangat kecil tidak mengalahkan pemecah seri jumlah pendukung.

| Metrik | Sebelum perubahan | Sesudah perubahan |
|---|---:|---:|
| Cakupan prediksi | 86,91% | 86,91% |
| MAE | 0,7690 | 0,7690 |
| RMSE | 0,9991 | 0,9991 |
| Pengguna yang dievaluasi pada top-10 | 604 | 604 |
| Rata-rata jumlah rekomendasi | 10,00 | 10,00 |
| Precision@10 | 0,0098 | 0,0535 |
| Recall@10 | 0,0149 | 0,0716 |

Precision@10 meningkat sekitar 5,46 kali, sedangkan Recall@10 meningkat sekitar 4,81 kali berdasarkan nilai yang ditampilkan. Peningkatan tersebut menunjukkan bahwa perubahan pemilihan kandidat dan pengurutan membantu rekomendasi pada pembagian data ini. Pengaruh masing-masing perubahan belum dipisahkan melalui percobaan tersendiri.

MAE, RMSE, dan cakupan prediksi tetap sama karena perubahan hanya diterapkan pada pemilihan rekomendasi, bukan pada perhitungan prediksi rating. Hasil evaluasi lama yang memakai cosine nilai rating tidak dimasukkan ke tabel ini karena metode dan pembagian datanya berbeda.

### 2.5. Sepuluh Rekomendasi User 1 dari Data Training

| Peringkat | ID film | Skor rekomendasi | Jumlah tetangga pendukung |
|---|---:|---:|---:|
| 1 | 3060 | 5,0000 | 3 |
| 2 | 1204 | 4,8825 | 4 |
| 3 | 750 | 4,8568 | 7 |
| 4 | 1272 | 4,8361 | 3 |
| 5 | 58559 | 4,8353 | 3 |
| 6 | 1248 | 4,7710 | 4 |
| 7 | 1199 | 4,7520 | 6 |
| 8 | 527 | 4,7441 | 12 |
| 9 | 4993 | 4,7255 | 7 |
| 10 | 1921 | 4,7074 | 7 |

Film ID 3060 berada pada urutan pertama dengan skor 5,0000 dari tiga tetangga pendukung. Film ID 527 memiliki jumlah pendukung terbanyak pada daftar ini, yaitu 12 tetangga, dengan skor 4,7441. Jumlah pendukung menunjukkan banyaknya tetangga yang menyediakan rating untuk perhitungan skor, bukan jumlah pengguna yang pasti menyukai film tersebut. Seluruh rating yang tersedia, termasuk rating rendah, ikut berkontribusi.

Skor rekomendasi bukan probabilitas bahwa pengguna akan menyukai film. Film dalam daftar ini belum diberi rating oleh user 1 pada data training; sebagian dapat berada di data testing. Daftar tersebut dapat berbeda dari visualisasi Neo4j sebelumnya yang menggunakan relasi similarity dari seluruh data dan pengaturan rekomendasi berbeda. Judul film tidak dicantumkan karena output evaluasi yang diberikan hanya memuat ID film.

## 3. Kesimpulan Akhir

Visualisasi Neo4j memperlihatkan hubungan antara pengguna, tetangga terdekat, dan film yang direkomendasikan sehingga asal rekomendasi dapat ditelusuri. Pada tahap evaluasi, sistem user-based collaborative filtering dengan cosine biner dapat memprediksi sebagian besar rating testing dan menghasilkan sepuluh rekomendasi bagi seluruh pengguna yang memenuhi syarat evaluasi top-10. Penerapan minimal tiga tetangga pendukung disertai penyesuaian pengurutan skor meningkatkan Precision@10 menjadi 0,0535 dan Recall@10 menjadi 0,0716, tanpa mengurangi jumlah rekomendasi yang tersedia pada percobaan ini.

Meskipun meningkat dibandingkan konfigurasi sebelumnya, kecocokan rekomendasi terhadap film relevan testing masih terbatas. Hasil ini belum cukup untuk menyatakan sistem memiliki kualitas rekomendasi yang tinggi. Perbandingan dengan baseline, seperti rekomendasi film terpopuler dari data training, diperlukan untuk menilai manfaat metode secara lebih jelas.

Karena perubahan pengaturan dilakukan setelah melihat hasil testing, hasil ini merupakan eksperimen eksploratif. Untuk evaluasi akhir yang lebih kuat, pemilihan pengaturan dilakukan pada data validasi, kemudian konfigurasi terpilih diuji pada data testing yang tidak digunakan untuk memilih pengaturan.
