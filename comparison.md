# Perbandingan Tiga Metode Collaborative Filtering

## 1. Tujuan

Laporan ini membandingkan hasil **Top-10 rekomendasi** dari tiga metode berdasarkan hasil query Neo4j dan file hasil Item-Based yang diberikan:

1. **User-Based Binary**
2. **User-Based Weighted**
3. **Item-Based Weighted**

Analisis dibatasi pada tiga daftar Top-10 tersebut. Angka evaluasi seperti MAE, RMSE, Precision@10, Recall@10, atau NDCG tidak dihitung ulang dalam laporan ini karena file yang diberikan hanya berisi hasil rekomendasi, skor, dan informasi pendukung.

## 2. Hasil Rekomendasi

### 2.1 User-Based Binary

|   Rank |   Movie ID | Rekomendasi                                            |   Predicted Score |   Nilai Pendukung |
|-------:|-----------:|:-------------------------------------------------------|------------------:|------------------:|
|      1 |         58 | Postman, The (Postino, Il) (1994)                      |                 5 |                 1 |
|      2 |        111 | Taxi Driver (1976)                                     |                 5 |                 1 |
|      3 |        288 | Natural Born Killers (1994)                            |                 5 |                 1 |
|      4 |        471 | Hudsucker Proxy, The (1994)                            |                 5 |                 1 |
|      5 |        529 | Searching for Bobby Fischer (1993)                     |                 5 |                 1 |
|      6 |        541 | Blade Runner (1982)                                    |                 5 |                 3 |
|      7 |        555 | True Romance (1993)                                    |                 5 |                 2 |
|      8 |        595 | Beauty and the Beast (1991)                            |                 5 |                 1 |
|      9 |        720 | Wallace & Gromit: The Best of Aardman Animation (1996) |                 5 |                 1 |
|     10 |        880 | Island of Dr. Moreau, The (1996)                       |                 5 |                 1 |

### 2.2 User-Based Weighted

|   Rank |   Movie ID | Rekomendasi                                                    |   Predicted Score |   Nilai Pendukung |
|-------:|-----------:|:---------------------------------------------------------------|------------------:|------------------:|
|      1 |        364 | Lion King, The (1994)                                          |                 5 |                 2 |
|      2 |       5618 | Spirited Away (Sen to Chihiro no kamikakushi) (2001)           |                 5 |                 2 |
|      3 |        293 | L on: The Professional (a.k.a. The Professional) (L on) (1994) |                 5 |                 2 |
|      4 |       7147 | Big Fish (2003)                                                |                 5 |                 2 |
|      5 |      48394 | Pan's Labyrinth (Laberinto del fauno, El) (2006)               |                 5 |                 2 |
|      6 |       3996 | Crouching Tiger, Hidden Dragon (Wo hu cang long) (2000)        |                 5 |                 2 |
|      7 |       4995 | Beautiful Mind, A (2001)                                       |                 5 |                 2 |
|      8 |     122904 | Deadpool (2016)                                                |                 5 |                 2 |
|      9 |       5989 | Catch Me If You Can (2002)                                     |                 5 |                 2 |
|     10 |       5971 | My Neighbor Totoro (Tonari no Totoro) (1988)                   |                 5 |                 2 |

### 2.3 Item-Based Weighted

|   Rank |   Movie ID | Rekomendasi                                               |   Predicted Score |   Nilai Pendukung |
|-------:|-----------:|:----------------------------------------------------------|------------------:|------------------:|
|      1 |       4226 | Memento (2000)                                            |                 5 |                 9 |
|      2 |        778 | Trainspotting (1996)                                      |                 5 |                 9 |
|      3 |       6874 | Kill Bill: Vol. 1 (2003)                                  |                 5 |                 7 |
|      4 |       4993 | Lord of the Rings: The Fellowship of the Ring, The (2001) |                 5 |                 6 |
|      5 |        616 | Aristocats, The (1970)                                    |                 5 |                 5 |
|      6 |       1221 | Godfather: Part II, The (1974)                            |                 5 |                 5 |
|      7 |       2085 | 101 Dalmatians (One Hundred and One Dalmatians) (1961)    |                 5 |                 5 |
|      8 |       1682 | Truman Show, The (1998)                                   |                 5 |                 5 |
|      9 |       7153 | Lord of the Rings: The Return of the King, The (2003)     |                 5 |                 5 |
|     10 |       2791 | Airplane! (1980)                                          |                 5 |                 4 |

## 3. Perbandingan Skor Prediksi

Ketiga metode menghasilkan predicted score sebesar **5,0 untuk seluruh film dalam daftar Top-10**. Dengan demikian, skor prediksi tidak membedakan urutan film pada hasil yang diberikan; urutan mengikuti urutan hasil query masing-masing metode.

## 4. Perbandingan Nilai Pendukung

![Jumlah pendukung per metode](support_top10_3_metode.png)

Kolom pendukung pada sumber tidak memiliki definisi yang seragam:
- User-Based Binary: `jumlahPendukung` (serta `idPendukung` pada file sumber).
- User-Based Weighted: `userPendukung`.
- Item-Based Weighted: `film_pendukung`.

Karena unit/arti pendukungnya berbeda, grafik ditampilkan dalam panel terpisah dan angka tidak boleh dibandingkan langsung antar-metode.

## 5. Irisan Rekomendasi Antar-Metode

![Venn Top-10 tiga metode](venn_top10_3_metode.png)

Pencocokan judul dilakukan melalui `movieId` pada dataset MovieLens (`movies.csv`), sehingga film yang sama dapat dikenali meskipun format judul pada CSV berbeda.

| Perbandingan | Jumlah film yang sama |
|---|---:|
| User-Based Binary ∩ User-Based Weighted | 0 |
| User-Based Binary ∩ Item-Based Weighted | 0 |
| User-Based Weighted ∩ Item-Based Weighted | 0 |
| Irisan ketiga metode | 0 |

### Film yang sama: Binary dan Weighted\n\n- Tidak ada film yang sama.\n\n### Film yang sama: Binary dan Item-Based\n\n- Tidak ada film yang sama.\n\n### Film yang sama: Weighted dan Item-Based\n\n- Tidak ada film yang sama.\n\n### Film yang sama: Ketiga metode\n\n- Tidak ada film yang sama.\n\n## 6. Pembahasan

- Ketiga metode memberikan daftar rekomendasi yang berbeda. Irisan Top-10 dapat dilihat pada Venn Diagram dan tabel jumlah irisan.
- Semua film memperoleh predicted score 5,0, sehingga skor tidak memberikan variasi dalam daftar yang tersedia.
- User-Based Binary menggunakan informasi interaksi biner dalam pembentukan similarity, sedangkan User-Based Weighted menggunakan rating asli.
- Item-Based Weighted membentuk rekomendasi berdasarkan kemiripan antarfilm.
- Nilai pendukung harus ditafsirkan sesuai nama kolom dan metode asalnya. Khususnya, `film_pendukung` pada Item-Based tidak otomatis setara dengan jumlah user pendukung pada metode User-Based.

## 7. Kesimpulan

Berdasarkan daftar Top-10 yang tersedia, ketiga metode menghasilkan rekomendasi yang cenderung berbeda. Semua rekomendasi memiliki predicted score 5,0. Oleh karena itu, perbedaan utama yang dapat diamati dari data ini adalah judul film yang direkomendasikan, tingkat irisan antar-metode, dan nilai pendukung sesuai definisi masing-masing query.

Untuk menyimpulkan metode mana yang memiliki kualitas rekomendasi terbaik, diperlukan metrik evaluasi pada data testing yang sama. Daftar Top-10 saja belum cukup untuk menentukan metode terbaik.

## 8. File Pendukung

- `visualisasi_3_metode.py` — kode untuk membuat grafik.
- `user_based_binary_top10.csv`
- `user_based_weighted_top10.csv`
- `item_based_weighted_top10.csv`
- `venn_top10_3_metode.png`
- `support_top10_3_metode.png`

---
*Sumber: dua file hasil query Neo4j untuk User-Based Binary dan User-Based Weighted, file Top-10 Item-Based, serta `movies.csv` untuk pencocokan Movie ID.*
