# Magic Hands English Learning - Panduan Penggunaan

## Gambaran Umum
Aplikasi pembelajaran bahasa Inggris interaktif berbasis computer vision yang menggunakan hand tracking untuk menyusun kalimat dalam berbagai tenses.

## Database Lesson
Database berisi 8 lesson yang mencakup berbagai tense:

### Lesson Tersedia:
1. **Present Simple** - Menyusun kalimat Present Simple
2. **Past Tense - Went** - Menyusun kalimat dengan "went"
3. **Past Tense - Ate** - Menyusun kalimat dengan "ate"
4. **Past Tense - Played** - Menyusun kalimat dengan aktivitas
5. **Past Tense - Watched** - Menyusun kalimat dengan "watched"
6. **Past Tense - Studied** - Menyusun kalimat dengan "studied"
7. **Past Continuous - Was Reading** - Menyusun kalimat Past Continuous
8. **Past Continuous - Were Playing** - Menyusun kalimat dengan "were"

## Cara Bermain

### Kontrol Keyboard:
- **Q** - Keluar dari aplikasi
- **R** - Reset/Ulangi lesson saat ini
- **N** - Lanjut ke lesson berikutnya
- **P** - Kembali ke lesson sebelumnya

### Cara Menggunakan Hand Tracking:
1. Genggam/tutup jari tangan (buat kepalan) untuk mengambil kata
2. Buka tangan untuk melepas kata di slot yang dituju
3. Tempatkan kata di slot yang benar (highlight hijau = benar)

### Warna Kotak:
- **Ungu** - Kata di posisi awal atau sedang di-hover
- **Hijau terang** - Kata sedang dipegang
- **Hijau** - Kata ditempatkan dengan benar
- **Oranye** - Kata ditempatkan di slot yang salah

## Struktur Database

Database tersimpan dalam file `database.py` dengan struktur:
```python
{
    'id': nomor lesson,
    'title': judul lesson,
    'description': deskripsi,
    'blocks': [list kata yang bisa di-drag],
    'correct_order': [urutan index yang benar]
}
```

## Cara Menambah Lesson Baru

Edit file `database.py` dan tambahkan entry baru ke dictionary `LESSONS`:

```python
'lesson_key_anda': {
    'id': 9,
    'title': 'Judul Lesson',
    'description': 'Penjelasan lesson',
    'blocks': ['KATA1', 'KATA2', 'KATA3'],
    'correct_order': [2, 0, 1],  # Indeks urutan yang benar
}
```

## Kebutuhan Library
- opencv-python
- cvzone
- numpy

## Setup Awal Lesson
Default lesson saat startup: `past_simple_2` (Past Tense - Went)

Untuk mengubah lesson default, edit baris di `main.py`:
```python
current_lesson_key = 'lesson_key_anda'
```

## Troubleshooting
- Jika hand tidak terdeteksi, pastikan pencahayaan cukup
- Jika block tidak bisa diambil, pastikan untuk membuat kepalan tangan penuh
- Untuk reset, tekan tombol 'R' untuk kembali ke posisi awal
