# QUICKSTART

1. Install dependencies (PowerShell):

```powershell
python -m pip install opencv-python cvzone numpy
```

2. Jalankan aplikasi (PowerShell):

```powershell
python main.py
```

atau menggunakan wrapper:

```powershell
python scripts\run.py
```

3. Kontrol saat bermain:
- Tekan `N` untuk lesson berikutnya
- Tekan `P` untuk lesson sebelumnya
- Tekan `R` untuk reset lesson
- Tekan `Q` untuk keluar

4. Tips penggunaan:
- Pastikan kamera terpasang dan pencahayaan memadai
- Gunakan latar polos agar hand tracking lebih stabil
- Gunakan telunjuk (index) untuk menunjuk dan gunakan kepalan untuk mengambil

5. Menambah atau mengedit lesson:
- Edit `database.py` sesuai format di `docs/LESSON_TEMPLATE.py`

6. Jika ada error import setelah reorganisasi, jalankan `python scripts\run.py` agar path ditetapkan.
