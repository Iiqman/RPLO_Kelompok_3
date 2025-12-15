"""
Script untuk menampilkan semua lesson yang tersedia di database
dan cara menggunakannya
"""

from database import get_lesson, get_lesson_list, get_all_lessons, get_lesson_by_id

def display_all_lessons():
    """Menampilkan semua lesson yang tersedia"""
    print("=" * 70)
    print("DAFTAR SEMUA LESSON ENGLISH LEARNING GAME")
    print("=" * 70)
    
    lessons = get_all_lessons()
    
    for idx, (key, lesson) in enumerate(lessons.items(), 1):
        print(f"\n{idx}. {lesson['title']}")
        print(f"   Key: {key}")
        print(f"   ID: {lesson['id']}")
        print(f"   Deskripsi: {lesson['description']}")
        print(f"   Kata-kata: {', '.join(lesson['blocks'])}")
        print(f"   Urutan Benar: {lesson['correct_order']}")

def display_lesson_simple():
    """Menampilkan lesson dalam format yang lebih simple"""
    print("\n" + "=" * 70)
    print("DAFTAR LESSON (Format Singkat)")
    print("=" * 70)
    
    lesson_list = get_lesson_list()
    for idx, (key, title) in enumerate(lesson_list, 1):
        print(f"{idx}. [{key}] {title}")

def get_specific_lesson(lesson_key):
    """Menampilkan detail lesson tertentu"""
    lesson = get_lesson(lesson_key)
    
    if lesson:
        print(f"\n{'=' * 70}")
        print(f"DETAIL LESSON: {lesson['title']}")
        print(f"{'=' * 70}")
        print(f"Key: {lesson_key}")
        print(f"ID: {lesson['id']}")
        print(f"Deskripsi: {lesson['description']}")
        print(f"\nKata-kata yang harus disusun:")
        for i, word in enumerate(lesson['blocks']):
            print(f"  {i}: {word}")
        print(f"\nUrutan yang BENAR: {' -> '.join([lesson['blocks'][i] for i in lesson['correct_order']])}")
    else:
        print(f"Lesson dengan key '{lesson_key}' tidak ditemukan!")

if __name__ == "__main__":
    # Tampilkan semua lesson
    display_all_lessons()
    
    # Tampilkan format singkat
    display_lesson_simple()
    
    # Tampilkan contoh lesson spesifik
    print("\n" + "=" * 70)
    print("CONTOH: Menampilkan detail lesson 'past_simple_2'")
    print("=" * 70)
    get_specific_lesson('past_simple_2')
    
    # Contoh mengambil lesson berdasarkan ID
    print("\n" + "=" * 70)
    print("CONTOH: Mencari lesson dengan ID 4")
    print("=" * 70)
    key, lesson = get_lesson_by_id(4)
    if lesson:
        print(f"Ditemukan: {lesson['title']} (Key: {key})")
