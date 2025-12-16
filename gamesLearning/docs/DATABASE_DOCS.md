
# Database Format & API

File: `database.py`

Struktur data utama adalah dictionary `LESSONS` yang berisi beberapa lesson. Contoh entry:

```python
'past_simple_1': {
	'id': 1,
	'title': 'Past Simple - Went',
	'description': 'Menyusun kalimat dengan "went"',
	'blocks': ['I', 'went', 'to', 'the', 'park'],
	'correct_order': [0, 1, 2, 3, 4]
}
```

Helper functions tersedia untuk mengakses database:

- `get_lesson(key)` → mengembalikan objek lesson berdasarkan `key`
- `get_all_lessons()` → list semua lesson
- `get_lesson_list()` → list tuple `(key, title)` untuk menu
- `get_lesson_by_id(id)` → cari lesson berdasarkan id

Menambah lesson baru hanya perlu menambahkan entry baru ke `LESSONS`.
