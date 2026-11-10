# Perbandingan Tiga Metode Collaborative Filtering

## 1. Tujuan

Laporan ini membandingkan hasil rekomendasi **Top-10** dari tiga metode Collaborative Filtering, yaitu:

1. **User-Based Binary**
2. **User-Based Weighted**
3. **Item-Based Weighted**

Perbandingan dilakukan berdasarkan daftar film yang direkomendasikan, skor prediksi, dan nilai pendukung yang dihasilkan oleh masing-masing metode.

## 2. Hasil Rekomendasi

### 2.1 User-Based Binary

| Peringkat | Movie ID | Judul Film | Skor Prediksi | Jumlah Pendukung |
|---:|---:|---|---:|---:|
| 1 | 58 | Postman, The (Postino, Il) (1994) | 5,0 | 1 |
| 2 | 111 | Taxi Driver (1976) | 5,0 | 1 |
| 3 | 288 | Natural Born Killers (1994) | 5,0 | 1 |
| 4 | 471 | Hudsucker Proxy, The (1994) | 5,0 | 1 |
| 5 | 529 | Searching for Bobby Fischer (1993) | 5,0 | 1 |
| 6 | 541 | Blade Runner (1982) | 5,0 | 3 |
| 7 | 555 | True Romance (1993) | 5,0 | 2 |
| 8 | 595 | Beauty and the Beast (1991) | 5,0 | 1 |
| 9 | 720 | Wallace & Gromit: The Best of Aardman Animation (1996) | 5,0 | 1 |
| 10 | 880 | Island of Dr. Moreau, The (1996) | 5,0 | 1 |

### 2.2 User-Based Weighted

| Peringkat | Movie ID | Judul Film | Skor Prediksi | User Pendukung |
|---:|---:|---|---:|---:|
| 1 | 364 | The Lion King (1994) | 5,0 | 2 |
| 2 | 5618 | Spirited Away (2001) | 5,0 | 2 |
| 3 | 293 | Léon: The Professional (1994) | 5,0 | 2 |
| 4 | 7147 | Big Fish (2003) | 5,0 | 2 |
| 5 | 48394 | Pan's Labyrinth (2006) | 5,0 | 2 |
| 6 | 3996 | Crouching Tiger, Hidden Dragon (2000) | 5,0 | 2 |
| 7 | 4995 | A Beautiful Mind (2001) | 5,0 | 2 |
| 8 | 122904 | Deadpool (2016) | 5,0 | 2 |
| 9 | 5989 | Catch Me If You Can (2002) | 5,0 | 2 |
| 10 | 5971 | My Neighbor Totoro (1988) | 5,0 | 2 |

### 2.3 Item-Based Weighted

| Peringkat | Movie ID | Judul Film | Skor Prediksi | Film Pendukung |
|---:|---:|---|---:|---:|
| 1 | 4226 | Memento (2000) | 5,0 | 9 |
| 2 | 778 | Trainspotting (1996) | 5,0 | 9 |
| 3 | 6874 | Kill Bill: Vol. 1 (2003) | 5,0 | 7 |
| 4 | 4993 | The Lord of the Rings: The Fellowship of the Ring (2001) | 5,0 | 6 |
| 5 | 616 | The Aristocats (1970) | 5,0 | 5 |
| 6 | 1221 | The Godfather: Part II (1974) | 5,0 | 5 |
| 7 | 2085 | One Hundred and One Dalmatians (1961) | 5,0 | 5 |
| 8 | 1682 | The Truman Show (1998) | 5,0 | 5 |
| 9 | 7153 | The Lord of the Rings: The Return of the King (2003) | 5,0 | 5 |
| 10 | 2791 | Airplane! (1980) | 5,0 | 4 |

## 3. Perbandingan Skor Prediksi

Ketiga metode menghasilkan skor prediksi sebesar **5,0 untuk seluruh film** dalam daftar Top-10. Artinya, skor prediksi yang dihasilkan tidak menunjukkan perbedaan antarfilm pada daftar yang dianalisis. Oleh karena itu, urutan rekomendasi mengikuti urutan hasil yang diberikan oleh masing-masing metode.

## 4. Perbandingan Nilai Pendukung

Nilai pendukung pada masing-masing metode adalah sebagai berikut.

| Metode | Nilai pendukung pada urutan Top-10 |
|---|---|
| User-Based Binary | 1, 1, 1, 1, 1, 3, 2, 1, 1, 1 |
| User-Based Weighted | 2, 2, 2, 2, 2, 2, 2, 2, 2, 2 |
| Item-Based Weighted | 9, 9, 7, 6, 5, 5, 5, 5, 5, 4 |

Perlu diperhatikan bahwa istilah nilai pendukung pada ketiga metode berasal dari kolom yang berbeda, yaitu:

- **User-Based Binary:** `jumlahPendukung`.
- **User-Based Weighted:** `userPendukung`.
- **Item-Based Weighted:** `film_pendukung`.

Karena definisi dan unit nilai pendukung tersebut tidak sepenuhnya sama, angkanya tidak dapat dibandingkan secara langsung antar-metode. Nilai tersebut lebih tepat digunakan untuk membaca hasil di dalam masing-masing metode.

## 5. Perbandingan Kesamaan Rekomendasi

Perbandingan dilakukan dengan mencocokkan identitas film berdasarkan Movie ID. Hasilnya menunjukkan bahwa tidak terdapat film yang sama di antara daftar Top-10 ketiga metode.

| Perbandingan | Jumlah Film yang Sama |
|---|---:|
| User-Based Binary dan User-Based Weighted | 0 |
| User-Based Binary dan Item-Based Weighted | 0 |
| User-Based Weighted dan Item-Based Weighted | 0 |
| Kesamaan pada ketiga metode | 0 |

Hasil tersebut menunjukkan bahwa setiap metode menghasilkan sepuluh rekomendasi yang berbeda pada daftar yang dianalisis.

## 6. Pembahasan

Berdasarkan hasil rekomendasi, terdapat beberapa hal yang dapat dibahas:

1. **Perbedaan daftar rekomendasi.** Ketiga metode menghasilkan daftar Top-10 yang berbeda dan tidak memiliki film yang sama. Hal ini menunjukkan bahwa pendekatan User-Based dan Item-Based menghasilkan pilihan rekomendasi yang berbeda pada data yang dianalisis.
2. **Skor prediksi seragam.** Seluruh film pada ketiga daftar memiliki skor prediksi 5,0. Dengan demikian, skor prediksi belum dapat digunakan untuk membedakan kualitas relatif setiap film dalam daftar tersebut.
3. **Perbedaan pendekatan.** User-Based Binary menggunakan representasi interaksi biner dalam perhitungan kemiripan pengguna, sedangkan User-Based Weighted mempertimbangkan bobot rating. Sementara itu, Item-Based Weighted menggunakan kemiripan antarfilm sebagai dasar pembentukan rekomendasi.
4. **Interpretasi nilai pendukung.** Nilai pendukung perlu dibaca berdasarkan definisi kolom pada masing-masing metode. Khususnya, `film_pendukung` pada Item-Based Weighted tidak dapat langsung dianggap setara dengan jumlah pengguna pendukung pada metode User-Based.

## 7. Kesimpulan

Berdasarkan hasil Top-10, User-Based Binary, User-Based Weighted, dan Item-Based Weighted menghasilkan daftar rekomendasi yang berbeda. Tidak ditemukan film yang sama pada perbandingan pasangan metode maupun pada ketiga daftar sekaligus. Seluruh film yang direkomendasikan juga memiliki skor prediksi 5,0.

Dengan hasil tersebut, belum dapat ditentukan metode yang memiliki kualitas rekomendasi paling baik hanya berdasarkan daftar Top-10. Penentuan metode terbaik memerlukan evaluasi lebih lanjut menggunakan data pengujian yang sama dan metrik evaluasi rekomendasi, seperti Precision@K, Recall@K, NDCG, MAE, atau RMSE sesuai tujuan evaluasi.
