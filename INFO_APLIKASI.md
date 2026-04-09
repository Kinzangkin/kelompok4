# Dokumentasi Lengkap Aplikasi Pengolahan Citra Digital

## 1. Deskripsi Umum
Aplikasi ini adalah perangkat lunak desktop berbasis Python yang dirancang untuk melakukan berbagai teknik pengolahan citra digital secara real-time maupun menggunakan file gambar. Aplikasi menggunakan library **Tkinter** untuk antarmuka pengguna (GUI), **OpenCV** untuk pemrosesan gambar dan akuisisi kamera, serta **PIL (Pillow)** untuk manipulasi tampilan gambar di GUI.

## 2. Struktur Proyek
Aplikasi ini memiliki struktur modular yang terbagi ke dalam beberapa komponen utama:
- `main.py`: Titik masuk utama aplikasi yang mengatur navigasi antar menu.
- `launcher.py`: Script untuk menjalankan aplikasi dengan pengecekan dependensi.
- `components/`: Folder yang berisi modul-modul fungsional spesifik:
  - `camera_panel.py`: Panel untuk akuisisi citra langsung dari kamera.
  - `gallery_page.py`: Menampilkan daftar gambar yang telah disimpan/capture.
  - `image_detail.py`: Menampilkan detail gambar yang dipilih dari galeri.
  - `rgb_to_gray.py`: Panel untuk konversi warna RGB ke Skala Abu-abu (Grayscale).
  - `gray_to_biner.py`: Panel untuk konversi gambar abu-abu ke Biner (Black & White).
  - `histogram_panel.py`: Analisis statistik RGB dan perhitungan Skewness, Average, STD, dan Kurtosis.
  - `edge_detection_panel.py`: Implementasi berbagai filter deteksi tepi (Sobel, Canny, Prewitt, dll).
  - `selectors.py`: Dialog untuk pemilihan sumber kamera.
  - `utils.py`: Fungsi pembantu untuk manipulasi file dan warna.

## 3. Fitur Utama
1. **Akuisisi Citra**: Mengambil foto secara langsung dari kamera (internal/webcam).
2. **Konversi Citra**: 
   - Konversi RGB ke Grayscale.
   - Konversi Grayscale ke Biner dengan thresholding.
3. **Analisis Citra**:
   - **Histogram**: Menampilkan grafik distribusi intensitas warna R, G, dan B. Menghitung statistik citra (Mean, Std Dev, Skewness, Kurtosis).
   - **Deteksi Tepi**: Mendukung berbagai algoritma (Robert, Prewitt, Sobel, Canny, dll).
   - **Analisis Bentuk**: Menghitung parameter objek (Luas, Lebar, Panjang, Perimeter, Dispersi, Kebulatan, Kerampingan) dengan fitur Export Excel.
5. **Manajemen Galeri**: Menyimpan hasil olah citra secara otomatis ke folder `gallery/` dan menampilkannya di dalam aplikasi.

## 4. Teknologi & Library yang Digunakan
- **Bahasa Pemrograman**: Python 3.x
- **GUI Framework**: Tkinter
- **Image Processing**: OpenCV (`cv2`), Pillow (`PIL`)
- **Data Analysis**: NumPy, SciPy (untuk statistik)
- **Visualization**: Matplotlib
- **Database**: SQLite3
- **File Export**: openpyxl (Excel)

## 5. Cara Penggunaan
1. Jalankan `launcher.py` atau `main.py`.
2. Gunakan menu bar di bagian atas untuk navigasi:
   - **File**: Kembali ke galeri atau keluar.
   - **Akuisisi Citra**: Untuk mengambil gambar baru.
   - **Konversi Citra**: Untuk mengubah format warna gambar.
   - **Analisis Citra**: Untuk melihat histogram atau melakukan deteksi tepi.
3. Gambar yang di-capture akan otomatis tersimpan di folder `gallery/`.

## 6. Lokasi Penyimpanan Data
- **Gambar**: Disimpan di folder `gallery/` dalam format `.png`.
- **Statistik Histogram**: Disimpan di file `histogram_data.db` (SQLite).
- **Export Excel**: Lokasi penyimpanan ditentukan oleh pengguna saat klik tombol "Export".
