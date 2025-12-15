"""
Database materi untuk English Learning Game
Menyimpan berbagai lesson dengan format soal drag-and-drop
"""

# Format: Lesson = {
#     'id': lesson id
#     'title': judul lesson
#     'blocks': [text yang bisa di-drag]
#     'target_positions': [posisi target untuk menyusun kalimat]
#     'correct_order': [indeks block yang benar untuk setiap slot]
#     'description': penjelasan lesson
# }

LESSONS = {
    'present_simple': {
        'id': 1,
        'title': 'Present Simple',
        'description': 'Menyusun kalimat Present Simple',
        'blocks': ['EAT', 'APPLE', 'I'],
        'correct_order': [2, 0, 1],  # I, EAT, APPLE (correct: I eat apple)
    },
    'past_simple_1': {
        'id': 2,
        'title': 'Past Tense - Went',
        'description': 'Menyusun kalimat Past Tense dengan kata kerja "went"',
        'blocks': ['YESTERDAY', 'PARK', 'TO', 'THE', 'WENT', 'I'],
        'correct_order': [5, 4, 2, 3, 1, 0],  # I went to the park yesterday
    },
    'past_simple_2': {
        'id': 3,
        'title': 'Past Tense - Ate',
        'description': 'Menyusun kalimat Past Tense dengan kata kerja "ate"',
        'blocks': ['ATE', 'I', 'RICE', 'YESTERDAY'],
        'correct_order': [1, 0, 2, 3],  # I ate rice yesterday
    },
    'past_simple_3': {
        'id': 4,
        'title': 'Past Tense - Played',
        'description': 'Menyusun kalimat Past Tense dengan aktivitas',
            'blocks': ['FOOTBALL', 'PLAYED', 'WITH', 'FRIENDS', 'THEY'],
            'correct_order': [4, 1, 3, 2, 0],  # They played with friends football
    },
    'past_simple_4': {
        'id': 5,
        'title': 'Past Tense - Watched',
        'description': 'Menyusun kalimat Past Tense dengan "watched"',
            'blocks': ['MOVIE', 'WATCHED', 'SHE', 'LAST', 'NIGHT'],
            'correct_order': [2, 1, 0, 3, 4],  # She watched movie last night
    },
    'past_simple_5': {
        'id': 6,
        'title': 'Past Tense - Studied',
        'description': 'Menyusun kalimat Past Tense dengan "studied"',
            'blocks': ['FOR', 'TEST', 'STUDIED', 'WE'],
            'correct_order': [3, 2, 0, 1],  # We studied for test
    },
    'past_continuous_1': {
        'id': 7,
        'title': 'Past Continuous - Was Reading',
        'description': 'Menyusun kalimat Past Continuous',
        'blocks': ['READING', 'WAS', 'BOOK', 'A', 'I'],
        'correct_order': [4, 1, 0, 3, 2],  # I was reading a book
    },
    'past_continuous_2': {
        'id': 8,
        'title': 'Past Continuous - Were Playing',
        'description': 'Menyusun kalimat Past Continuous dengan "were"',
        'blocks': ['WERE', 'PLAYING', 'GAME', 'A', 'THEY'],
        'correct_order': [4, 0, 1, 3, 2],  # They were playing a game
    },
    'past_simple_6': {
        'id': 9,
        'title': 'Past Tense - Bought',
        'description': 'Menyusun kalimat Past Tense dengan "bought"',
        'blocks': ['BOUGHT', 'SOMETHING', 'HE', 'NEW'],
        'correct_order': [2, 0, 1, 3],  # He bought something new
    },
    'past_simple_7': {
        'id': 10,
        'title': 'Past Tense - Called',
        'description': 'Menyusun kalimat Past Tense dengan "called"',
        'blocks': ['CALLED', 'MY', 'FRIEND', 'I', 'YESTERDAY'],
        'correct_order': [3, 0, 1, 2, 4],  # I called my friend yesterday
    },
    'past_continuous_3': {
        'id': 11,
        'title': 'Past Continuous - Was Singing',
        'description': 'Menyusun kalimat Past Continuous dengan "was singing"',
        'blocks': ['WAS', 'SINGING', 'SHE', 'A', 'SONG'],
        'correct_order': [2, 0, 1, 3, 4],  # She was singing a song
    },
    'past_continuous_4': {
        'id': 12,
        'title': 'Past Continuous - Was Cooking',
        'description': 'Menyusun kalimat Past Continuous dengan "was cooking"',
        'blocks': ['I', 'WAS', 'COOKING', 'DINNER', 'LAST', 'NIGHT'],
        'correct_order': [0, 1, 2, 3, 4, 5],  # I was cooking dinner last night
    },
    'past_continuous_5': {
        'id': 13,
        'title': 'Past Continuous - Were Watching',
        'description': 'Menyusun kalimat Past Continuous dengan "were watching"',
        'blocks': ['THEY', 'WERE', 'WATCHING', 'TV'],
        'correct_order': [0, 1, 2, 3],  # They were watching TV
    },
    'past_continuous_6': {
        'id': 14,
        'title': 'Past Continuous - Was Sleeping',
        'description': 'Menyusun kalimat Past Continuous dengan "was sleeping"',
        'blocks': ['HE', 'WAS', 'SLEEPING', 'AT', '10'],
        'correct_order': [0, 1, 2, 3, 4],  # He was sleeping at 10
    },
    'past_continuous_7': {
        'id': 15,
        'title': 'Past Continuous - Was Playing',
        'description': 'Menyusun kalimat Past Continuous lainnya',
        'blocks': ['SHE', 'WAS', 'PLAYING', 'PIANO'],
        'correct_order': [0, 1, 2, 3],  # She was playing piano
    },
    'past_perfect_1': {
        'id': 16,
        'title': 'Past Perfect - Had Finished',
        'description': 'Menyusun kalimat Past Perfect',
        'blocks': ['I', 'HAD', 'FINISHED', 'MY', 'HOMEWORK', 'BEFORE', 'DINNER'],
        'correct_order': [0, 1, 2, 3, 4, 5, 6],  # I had finished my homework before dinner
    },
    'past_perfect_2': {
        'id': 17,
        'title': 'Past Perfect - Had Left',
        'description': 'Menyusun kalimat Past Perfect lainnya',
        'blocks': ['SHE', 'HAD', 'LEFT', 'EARLY'],
        'correct_order': [0, 1, 2, 3],  # She had left early
    },
    'past_perfect_3': {
        'id': 18,
        'title': 'Past Perfect - Had Seen',
        'description': 'Menyusun kalimat Past Perfect dengan "had seen"',
        'blocks': ['WE', 'HAD', 'SEEN', 'THAT', 'MOVIE', 'BEFORE'],
        'correct_order': [0, 1, 2, 3, 4, 5],  # We had seen that movie before
    },
    'past_perfect_4': {
        'id': 19,
        'title': 'Past Perfect - Had Built',
        'description': 'Menyusun kalimat Past Perfect dengan "had built"',
        'blocks': ['THEY', 'HAD', 'BUILT', 'A', 'HOUSE'],
        'correct_order': [0, 1, 2, 3, 4],  # They had built a house
    },
    'past_perfect_5': {
        'id': 20,
        'title': 'Past Perfect - Had Cooked',
        'description': 'Menyusun kalimat Past Perfect',
        'blocks': ['HE', 'HAD', 'COOKED', 'DINNER', 'ALREADY'],
        'correct_order': [0, 1, 2, 3, 4],  # He had cooked dinner already
    },
    'past_perfect_6': {
        'id': 21,
        'title': 'Past Perfect - Had Arrived',
        'description': 'Menyusun kalimat Past Perfect',
        'blocks': ['I', 'HAD', 'ARRIVED', 'AT', 'THE', 'STATION'],
        'correct_order': [0, 1, 2, 3, 4, 5],  # I had arrived at the station
    },
    'past_perfect_7': {
        'id': 22,
        'title': 'Past Perfect - Had Forgotten',
        'description': 'Menyusun kalimat Past Perfect',
        'blocks': ['SHE', 'HAD', 'FORGOTTEN', 'HER', 'KEY'],
        'correct_order': [0, 1, 2, 3, 4],  # She had forgotten her key
    },
    'past_perfect_continuous_1': {
        'id': 23,
        'title': 'Past Perfect Continuous - Had Been Studying',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['SHE', 'HAD', 'BEEN', 'STUDYING', 'FOR', 'HOURS'],
        'correct_order': [0, 1, 2, 3, 4, 5],  # She had been studying for hours
    },
    'past_perfect_continuous_2': {
        'id': 24,
        'title': 'Past Perfect Continuous - Had Been Working',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['HE', 'HAD', 'BEEN', 'WORKING', 'ALL', 'DAY'],
        'correct_order': [0, 1, 2, 3, 4, 5],  # He had been working all day
    },
    'past_perfect_continuous_3': {
        'id': 25,
        'title': 'Past Perfect Continuous - Had Been Waiting',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['WE', 'HAD', 'BEEN', 'WAITING', 'SINCE', 'MORNING'],
        'correct_order': [0, 1, 2, 3, 4, 5],
    },
    'past_perfect_continuous_4': {
        'id': 26,
        'title': 'Past Perfect Continuous - Had Been Traveling',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['THEY', 'HAD', 'BEEN', 'TRAVELING', 'FOR', 'MONTHS'],
        'correct_order': [0, 1, 2, 3, 4, 5],
    },
    'past_perfect_continuous_5': {
        'id': 27,
        'title': 'Past Perfect Continuous - Had Been Crying',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['SHE', 'HAD', 'BEEN', 'CRYING', 'FOR', 'A', 'LONG', 'TIME'],
        'correct_order': [0, 1, 2, 3, 4, 5, 6, 7],
    },
    'past_perfect_continuous_6': {
        'id': 28,
        'title': 'Past Perfect Continuous - Had Been Practicing',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['HE', 'HAD', 'BEEN', 'PRACTICING', 'THE', 'PIANO'],
        'correct_order': [0, 1, 2, 3, 4, 5],
    },
    'past_perfect_continuous_7': {
        'id': 29,
        'title': 'Past Perfect Continuous - Had Been Living',
        'description': 'Menyusun kalimat Past Perfect Continuous',
        'blocks': ['I', 'HAD', 'BEEN', 'LIVING', 'IN', 'THE', 'CITY'],
        'correct_order': [0, 1, 2, 3, 4, 5, 6],
    },
}

TOPICS = {
    'simple_past': 'Simple Past',
    'past_continuous': 'Past Continuous',
    'past_perfect': 'Past Perfect',
    'past_perfect_continuous': 'Past Perfect Continuous'
}

def get_topics():
    """Return mapping of topic keys to display titles (ordered)."""
    return TOPICS

def get_lessons_for_topic(topic_key):
    """Return list of lesson keys for the given topic (7 lessons each).

    Topic mapping uses naming conventions in LESSONS keys.
    """
    if topic_key == 'simple_past':
        return [f'past_simple_{i}' for i in range(1, 8)]
    if topic_key == 'past_continuous':
        return [f'past_continuous_{i}' for i in range(1, 8)]
    if topic_key == 'past_perfect':
        return [f'past_perfect_{i}' for i in range(1, 8)]
    if topic_key == 'past_perfect_continuous':
        return [f'past_perfect_continuous_{i}' for i in range(1, 8)]
    return []

def get_lesson(lesson_key):
    """
    Mengambil lesson dari database
    
    Args:
        lesson_key: key dari LESSONS dictionary
    
    Returns:
        dict: lesson data atau None jika tidak ditemukan
    """
    return LESSONS.get(lesson_key)

def get_all_lessons():
    """
    Mengambil semua lesson yang tersedia
    
    Returns:
        dict: semua lesson dalam LESSONS
    """
    return LESSONS

def get_lesson_list():
    """
    Mengambil list judul dan key lesson
    
    Returns:
        list: list tuple (key, title)
    """
    return [(key, lesson['title']) for key, lesson in LESSONS.items()]

def get_lesson_by_id(lesson_id):
    """
    Mengambil lesson berdasarkan ID
    
    Args:
        lesson_id: ID lesson
    
    Returns:
        tuple: (key, lesson_data) atau (None, None) jika tidak ditemukan
    """
    for key, lesson in LESSONS.items():
        if lesson['id'] == lesson_id:
            return key, lesson
    return None, None
