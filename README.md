# RPLO_Kelompok3
# Facial Expression Recognition + FaceMesh Project

Proyek ini menggabungkan **Facial Expression Recognition (FER)** dengan **MediaPipe FaceMesh** untuk:
- Mendeteksi ekspresi wajah (happy, sad, angry, surprise, neutral, disgust, fear).
- Menampilkan visualisasi titik-titik wajah (468 landmark).
- Mengirim hasil ekspresi ke aplikasi Electron/React untuk integrasi UI.

---

## 🚀 Cara Menjalankan

### 1. Clone Repository
```bash
git clone <repo-url>
cd <repo-folder>
```

### 2. Setup Python Environment
Karena `mediapipe` dan `fer` punya dependensi berbeda, gunakan **virtual environment**:

#### a. Buat environment untuk FER
```bash
python -m venv fer-env
fer-env\Scripts\activate   # Windows
# atau source fer-env/bin/activate (Linux/macOS)

pip install fer==22.4.0 opencv-python
```

#### b. Buat environment untuk MediaPipe
```bash
python -m venv mediapipe-env
mediapipe-env\Scripts\activate

pip install mediapipe==0.10.21 protobuf==4.25.3 opencv-python
```

> ⚠️ Catatan: `mediapipe` tidak kompatibel dengan protobuf versi 6+, jadi pastikan pakai `protobuf==4.25.3`.

---

### 3. Jalankan Script Python
Gunakan environment yang sesuai, lalu jalankan:

```bash
python fer_detect.py
```

- Tekan `q` untuk keluar.
- Output ekspresi akan muncul di terminal dan ditampilkan di layar dengan mesh wajah.

---

### 4. Setup Node.js (Electron/React)
```bash
npm install
npm start
```

Pastikan `node_modules/` sudah di-ignore di `.gitignore`.

---

## 📂 Struktur Proyek

```
project/
│
├── python/
│   ├── fer_detect.py        # Script utama FER + FaceMesh
│   ├── requirements.txt     # Dependensi Python
│
├── electron-app/            # Folder untuk React/Electron
│   ├── package.json
│   └── src/
│
└── README.md
```

---

## 🛠️ Troubleshooting

- **Kamera tidak terbaca di Windows** → gunakan `cv2.VideoCapture(0, cv2.CAP_DSHOW)`.
- **Error protobuf** → downgrade ke `protobuf==4.25.3`.
- **FER ImportError** → gunakan `fer==22.4.0` agar class `FER` tersedia.

---

## 📌 Catatan Gitignore

File `.gitignore` sudah diatur agar environment lokal dan dependensi tidak ikut ter-push:

```
# Python
venv/
env/
fer-env/
mediapipe-env/
__pycache__/
*.pyc
*.pyo
*.pyd

# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
```
---

## 📂 Folder yang Tidak Terupload ke GitHub

Beberapa folder dan file **tidak ikut ter‑push ke GitHub** karena hanya digunakan secara lokal oleh masing‑masing developer:

- **`fer-env/`** → virtual environment khusus untuk library FER.  
- **`mediapipe-env/`** → virtual environment khusus untuk MediaPipe.  
- **`venv/` / `env/`** → environment Python umum.  
- **`__pycache__/`** → cache Python otomatis.  
- **`node_modules/`** → dependency Node.js/Electron.  
- File sementara seperti `*.pyc`, `*.pyo`, `*.pyd`, dan log (`*.log`).  

👉 Semua dependency bisa di‑install ulang menggunakan:
- `requirements.txt` untuk Python.  
- `package.json` untuk Node.js/Electron.  

Dengan begitu, repo tetap ringan dan tidak berisi file besar (DLL, `.pyd`, `.exe`) yang tidak diperlukan di GitHub.

---

---

## 👥 Kontribusi

1. Pastikan environment sesuai sebelum menjalankan script.
2. Tambahkan fitur baru di folder masing-masing (Python atau Electron).
3. Gunakan branch terpisah untuk pengembangan.
4. Buat pull request untuk review.

---

## 📊 Next Steps

- Logging ekspresi ke file CSV untuk analisis.
- Integrasi penuh dengan React UI.
- Tambah model CNN (DeepFace/FER2013) untuk akurasi lebih tinggi.
```

---