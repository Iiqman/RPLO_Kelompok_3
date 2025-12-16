"""
Script untuk menjalankan main.py dengan error handling
Gunakan ini jika ada masalah dengan library yang belum terinstall
"""

import sys
import subprocess

# List library yang dibutuhkan
REQUIRED_LIBRARIES = [
    'opencv-python',
    'cvzone',
    'numpy'
]

def check_and_install_libraries():
    """Cek dan install library yang diperlukan"""
    print("Checking required libraries...")
    
    for lib in REQUIRED_LIBRARIES:
        try:
            __import__(lib.replace('-', '_'))
            print(f"✓ {lib} sudah terinstall")
        except ImportError:
            print(f"✗ {lib} belum terinstall, menginstall...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])
            print(f"✓ {lib} berhasil diinstall")

def run_application():
    """Jalankan aplikasi"""
    print("\n" + "=" * 70)
    print("MEMULAI MAGIC HANDS ENGLISH LEARNING")
    print("=" * 70)
    print("\nGame dimulai... Instruksi ada di layar game.")
    print("\n" + "=" * 70 + "\n")
    
    try:
        subprocess.run([sys.executable, 'main.py'])
    except Exception as e:
        print(f"Error menjalankan aplikasi: {e}")
        print("\nPastikan kamera tersambung dan library terinstall dengan benar!")

if __name__ == "__main__":
    check_and_install_libraries()
    print("\nSemua library siap!")
    input("\nTekan Enter untuk memulai aplikasi...")
    run_application()
