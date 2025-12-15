# 🎯 QUICK START GUIDE

## Instalasi Cepat (First Time)

```bash
# 1. Pastikan di folder project
cd c:\Kuliah\Kodingan\gamesLearning

# 2. Install dependencies (jika belum ada)
pip install opencv-python cvzone numpy

# 3. Run game
python main.py
```

---

## 🎮 Main Controls

| Tombol | Fungsi |
|--------|--------|
| **Q** | Quit/Keluar aplikasi |
| **R** | Reset/Ulangi lesson sekarang |
| **N** | Next - Lesson berikutnya |
| **P** | Previous - Lesson sebelumnya |

---

## 📚 Lesson yang Tersedia

1. **Present Simple** - Dasar kalimat sederhana
2. **Past Tense - Went** - "I went to the park"
3. **Past Tense - Ate** - "I ate rice yesterday"
4. **Past Tense - Played** - "They played with friends"
5. **Past Tense - Watched** - "She watched a movie"
6. **Past Tense - Studied** - "We studied for the test"
7. **Past Continuous - Was Reading** - "I was reading a book"
8. **Past Continuous - Were Playing** - "They were playing a game"

---

## ❓ FAQ

**Q: Bagaimana cara ganti lesson default saat startup?**  
A: Edit `main.py` baris ke-89:
```python
current_lesson_key = 'past_simple_1'  # Ganti dengan lesson yang diinginkan
```

**Q: Bagaimana cara menambah lesson baru?**  
A: 
1. Buka `database.py`
2. Tambah entry baru ke dictionary `LESSONS`
3. Ikuti format yang ada
4. Lihat `LESSON_TEMPLATE.py` untuk contoh

**Q: Hand tidak terdeteksi?**  
A: 
- Pastikan pencahayaan cukup
- Buat kepalan tangan untuk grab
- Buka tangan penuh untuk drop

---

## 🔧 Troubleshooting

**Error: ModuleNotFoundError: No module named 'cvzone'**
```bash
pip install cvzone
```

**Error: ModuleNotFoundError: No module named 'cv2'**
```bash
pip install opencv-python
```

**Kamera tidak terdeteksi**
- Pastikan kamera terhubung
- Test dengan aplikasi camera bawaan Windows dulu

**Block tidak snap ke slot**
- Pastikan threshold SNAP_THRESHOLD cukup (default: 120)
- Edit di `main.py` jika perlu

---

## 📖 Dokumentasi Lengkap

- `README.md` - Panduan lengkap
- `CHANGELOG.md` - Riwayat perubahan
- `LESSON_TEMPLATE.py` - Template membuat lesson baru
- `view_lessons.py` - Lihat semua lesson di database

---

## 🚀 Cara Menjalankan

### Option 1: Direct (Jika semua library sudah ada)
```bash
python main.py
```

### Option 2: Auto-Install (Recommended jika baru pertama kali)
```bash
python run.py
```

### Option 3: Lihat Database Terlebih Dahulu
```bash
python view_lessons.py
```

---

## 💡 Tips

- Tekan **N/P** untuk ganti lesson tanpa restart aplikasi
- Tekan **R** untuk reset tanpa ganti lesson
- Kata di-shuffle setiap kali load lesson
- Block otomatis "snap" ke slot terdekat jika dalam jarak threshold

---

Selamat bermain! 🎉
