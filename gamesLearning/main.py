import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import numpy as np
from database import get_lesson, get_all_lessons, get_lesson_list, get_topics, get_lessons_for_topic
import random

# --- KONFIGURASI ---
CAP_WIDTH = 1280
CAP_HEIGHT = 720
BLOCK_SIZE = [180, 80] 
SNAP_THRESHOLD = 120 
SHAKA_HOLD_FRAMES = 6  # require shaka held for this many frames before undo

# Inisialisasi Kamera
cap = cv2.VideoCapture(0)
cap.set(3, CAP_WIDTH)
cap.set(4, CAP_HEIGHT)

# Inisialisasi Detektor Tangan
detector = HandDetector(detectionCon=0.8)

# --- CLASS UNTUK KOTAK KATA ---
class DragBlock:
    def __init__(self, text, pos, target_idx):
        self.text = text
        self.pos = pos              
        self.origin_pos = list(pos) 
        self.size = BLOCK_SIZE       
        self.target_idx = target_idx 
        self.color = (255, 0, 255) # Ungu Default
        self.is_correct = False     

    def update(self, cursor, is_grabbing):
        cx, cy = self.pos
        w, h = self.size
        self.color = (255, 0, 255) 

        # Cek hover
        if cx - w // 2 < cursor[0] < cx + w // 2 and \
           cy - h // 2 < cursor[1] < cy + h // 2:
            
            if is_grabbing:
                self.pos = cursor
                self.color = (0, 255, 0) # Hijau saat dipegang
            else:
                self.color = (200, 50, 200) # Hover
        
        return self.pos

# --- HELPER DRAW FUNCTIONS (Styling untuk anak-anak) ---
def rounded_rect(img, top_left, bottom_right, color, radius=20, thickness=-1):
    # Draw filled rounded rectangle by drawing rectangles + circles
    x1, y1 = top_left
    x2, y2 = bottom_right
    if thickness < 0:
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
        cv2.circle(img, (x1 + radius, y1 + radius), radius, color, thickness)
        cv2.circle(img, (x2 - radius, y1 + radius), radius, color, thickness)
        cv2.circle(img, (x1 + radius, y2 - radius), radius, color, thickness)
        cv2.circle(img, (x2 - radius, y2 - radius), radius, color, thickness)
    else:
        # Outline
        cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, thickness)
        cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, thickness)
        cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, thickness)
        cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, thickness)
        cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, thickness)

def draw_shadowed_block(img, cx, cy, w, h, base_color, text, text_color=(255,255,255)):
    # Soft shadow
    shadow_color = (30, 30, 30)
    shadow_offset = 8
    x1, y1 = int(cx - w // 2), int(cy - h // 2)
    x2, y2 = int(cx + w // 2), int(cy + h // 2)
    rounded_rect(img, (x1 + shadow_offset, y1 + shadow_offset), (x2 + shadow_offset, y2 + shadow_offset), shadow_color, radius=20)
    rounded_rect(img, (x1, y1), (x2, y2), base_color, radius=20)
    # Text centered
    font = cv2.FONT_HERSHEY_SIMPLEX
    text_size = cv2.getTextSize(text, font, 1.0, 3)[0]
    tx = cx - text_size[0] // 2
    ty = cy + text_size[1] // 2
    cv2.putText(img, text, (tx, ty), font, 1.0, text_color, 3, cv2.LINE_AA)

def draw_banner(img, title, subtitle=None):
    # Top banner with soft gradient and rounded corners
    h, w = img.shape[:2]
    banner_h = 90
    # Gradient background
    for i in range(banner_h):
        alpha = i / banner_h
        color = (
            int(120 + (255-120)*alpha),
            int(180 + (220-180)*alpha),
            int(240 - (240-200)*alpha)
        )
        cv2.line(img, (0, i), (w, i), color, 1)
    # Rounded area overlay for banner
    rounded_rect(img, (20, 10), (w-20, 10+banner_h-10), (255,255,255), radius=30)
    # Title text
    cv2.putText(img, title, (60, 60), cv2.FONT_HERSHEY_DUPLEX, 1.6, (40,40,120), 3, cv2.LINE_AA)
    if subtitle:
        cv2.putText(img, subtitle, (60, 60+36), cv2.FONT_HERSHEY_COMPLEX, 0.7, (80,80,140), 2, cv2.LINE_AA)


# --- FUNGSI UNTUK SETUP LESSON ---
def setup_lesson(lesson_key):
    """
    Setup game dengan lesson dari database
    
    Args:
        lesson_key: key lesson dari database
    
    Returns:
        tuple: (blocks, target_positions, lesson_data)
    """
    lesson = get_lesson(lesson_key)
    if not lesson:
        print(f"Lesson '{lesson_key}' tidak ditemukan!")
        return None, None, None
    
    # Acak urutan block untuk ditampilkan di bawah
    block_list = lesson['blocks'].copy()
    original_indices = list(range(len(block_list)))
    
    # Shuffle blocks dengan indeksnya
    combined = list(zip(block_list, original_indices))
    random.shuffle(combined)
    block_list, shuffled_indices = zip(*combined)
    
    # Buat mapping dari shuffled index ke original index
    # Untuk mengetahui target_idx yang benar
    target_order = lesson['correct_order'].copy()
    
    # Buat blocks - tempatkan di tengah layar
    blocks = []
    block_height = CAP_HEIGHT // 2 + 80  # Posisi awal blocks
    block_width = 100
    start_x = 150
    spacing = 200
    
    for i, text in enumerate(block_list):
        # Cari original index dari block ini
        original_idx = shuffled_indices[i]
        # Cari target_idx berdasarkan original_idx dalam correct_order
        target_idx = target_order.index(original_idx)
        
        pos = [start_x + i * spacing, block_height]
        blocks.append(DragBlock(text, pos, target_idx))
    
    # Setup target positions untuk slot - lebih banyak spacing horizontal
    num_slots = len(lesson['blocks'])
    target_positions = []
    # Hitung spacing agar slot tidak terlalu rapat
    if num_slots <= 4:
        slot_spacing = 250  # Spacing lebih besar untuk 4 slot atau kurang
    else:
        slot_spacing = 200
    
    slot_start_x = (CAP_WIDTH - (num_slots - 1) * slot_spacing) // 2
    
    for i in range(num_slots):
        target_positions.append([slot_start_x + i * slot_spacing, 200])
    
    return blocks, target_positions, lesson

# --- SETUP AWAL ---
# Pilih materi (topic) dulu: simple past, past continuous, past perfect, past perfect continuous
topics = get_topics()

def topic_selection_screen(cap, topics):
    sel = None
    last_index_up = False
    # Precompute button layout so coordinates are stable
    btn_w = 300
    btn_h = 80
    gap = 30
    start_x = 30
    y = 120
    keys = list(topics.keys())
    buttons = []
    for i, key in enumerate(keys):
        x = start_x + i * (btn_w + gap)
        buttons.append((key, topics[key], (x, y, x + btn_w, y + btn_h)))

    while True:
        success, frame = cap.read()
        if not success:
            continue
        h, w = frame.shape[:2]
        overlay = frame.copy()
        # header
        cv2.rectangle(overlay, (0, 0), (w, 80), (255, 240, 230), -1)
        cv2.putText(overlay, 'Pilih Materi (Tekan 1-4 atau tunjuk dengan telunjuk):', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (30, 30, 30), 2)

        # Draw buttons and track hover
        hover_key = None
        for idx, (key, title, (x1, y1, x2, y2)) in enumerate(buttons):
            rounded_rect(overlay, (x1, y1), (x2, y2), (200, 230, 255), radius=16)
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (120, 160, 200), 3)
            cv2.putText(overlay, f"{idx+1}. {title}", (x1 + 18, y1 + btn_h // 2 + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (20, 20, 40), 2)

        # Hand detection for pointing selection
        try:
            hands, _imgout = detector.findHands(frame, flipType=False)
        except Exception:
            hands = None

        cursor = None
        index_up = False
        if hands:
            hand = hands[0]
            lmList = hand.get('lmList', [])
            if lmList:
                cursor = lmList[8][:2]
            fingers = detector.fingersUp(hand)
            # index up, middle & ring down considered pointing; ignore shaka
            if fingers and len(fingers) >= 5:
                index_up = (fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0)

        # If we have cursor, check hover
        if cursor is not None:
            cx, cy = int(cursor[0]), int(cursor[1])
            cv2.circle(overlay, (cx, cy), 8, (50, 200, 50), cv2.FILLED)
            for (key, title, (x1, y1, x2, y2)) in buttons:
                if x1 < cx < x2 and y1 < cy < y2:
                    # highlight hovered button
                    rounded_rect(overlay, (x1, y1), (x2, y2), (180, 250, 200), radius=16)
                    cv2.rectangle(overlay, (x1, y1), (x2, y2), (80, 140, 90), 4)
                    hover_key = key
                    break

        cv2.imshow("Magic Hands RPLO", overlay)

        # Keyboard fallback
        k = cv2.waitKey(30) & 0xFF
        if k in (ord('1'), ord('2'), ord('3'), ord('4')):
            sel_idx = (k - ord('1'))
            if 0 <= sel_idx < len(keys):
                sel = keys[sel_idx]
                break
        if k == 27 or k == ord('q') or k == ord('Q'):
            sel = None
            break

        # Hand-based selection: detect rising edge of index-up while hovering a button
        if index_up and hover_key and not last_index_up:
            sel = hover_key
            break
        last_index_up = index_up

    return sel

# Run topic selection
selected_topic = topic_selection_screen(cap, topics)
if selected_topic is None:
    print('No topic selected, exiting')
    cap.release()
    cv2.destroyAllWindows()
    exit()

# load lessons for the chosen topic
lessons = get_lessons_for_topic(selected_topic)
current_idx = 0
current_lesson_key = lessons[current_idx]
blocks, target_positions, current_lesson = setup_lesson(current_lesson_key)

if blocks is None:
    print("Error: Tidak bisa load lesson!")
    cap.release()
    cv2.destroyAllWindows()
    exit()

MESSAGE = current_lesson.get('description', '')
grabbed_block = None

# --- SEQUENTIAL PLACEMENT STATE ---
placed_blocks = []  # List of (block, slot_idx) yang sudah ditempatkan
last_index_finger_up = False  # Frame-by-frame tracking untuk deteksi rising edge
# Shaka debounce state
shaka_frames = 0
shaka_triggered = False

# --- GAME LOOP ---
while True:
    success, img = cap.read()
    if not success:
        break
        
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    cursor = [0, 0]
    index_finger_up = False
    shaka = False
    hovered_block = None

    # --- LOGIKA HAND TRACKING (ANTI CRASH) ---
    try:
        if hands: 
            hand1 = hands[0]
            lmList = hand1["lmList"] 
            cursor = lmList[8][:2]
            fingers = detector.fingersUp(hand1) 
            # fingers format: [thumb, index, middle, ring, pinky]
            # Detect shaka: thumb + pinky extended, others closed
            shaka = (fingers[0] == 1 and fingers[4] == 1 and
                     fingers[1] == 0 and fingers[2] == 0 and fingers[3] == 0)
            index_finger_up = fingers[1] == 1
            middle_down = fingers[2] == 0
            ring_down = fingers[3] == 0

            # Index pointing: index up, middle/ring down, and not shaka
            if index_finger_up and middle_down and ring_down and not shaka:
                # Cari block yang di-hover
                for block in blocks:
                    if not any(b[0] == block for b in placed_blocks):
                        cx, cy = block.pos
                        w, h = block.size
                        if cx - w // 2 < cursor[0] < cx + w // 2 and \
                           cy - h // 2 < cursor[1] < cy + h // 2:
                            hovered_block = block
                            break
            
    except Exception as e:
        pass 

    # 1. Gambar banner judul dan deskripsi (mirip screenshot pengguna)
    draw_banner(img, current_lesson['title'])
    # Description magenta pill inside banner
    desc_text = current_lesson.get('description', '')
    if desc_text:
        magenta = (200, 0, 200)
        desc_x1, desc_y1 = 40, 22
        desc_x2, desc_y2 = CAP_WIDTH - 420, 78
        rounded_rect(img, (desc_x1, desc_y1), (desc_x2, desc_y2), magenta, radius=18)
        # Put description text (left aligned with some padding)
        font = cv2.FONT_HERSHEY_SIMPLEX
        desc_scale = 0.9
        desc_thickness = 2
        # shorten if too long for space (basic trim)
        max_width = desc_x2 - desc_x1 - 24
        display_text = desc_text
        while cv2.getTextSize(display_text, font, desc_scale, desc_thickness)[0][0] > max_width and len(display_text) > 4:
            display_text = display_text[:-4] + '...'
        tx = desc_x1 + 16
        ty = desc_y1 + (desc_y2 - desc_y1)//2 + 8
        cv2.putText(img, display_text, (tx, ty), font, desc_scale, (255,255,255), desc_thickness, cv2.LINE_AA)

    # Instruction pill (right side, smaller)
    instr_color = (170, 220, 255)  # light blue
    rounded_rect(img, (CAP_WIDTH - 420, 20), (CAP_WIDTH - 20, 80), instr_color, radius=20)
    instr_text = "Tunjuk kata, keluarkan jari untuk masuk slot berikutnya"
    it_font = cv2.FONT_HERSHEY_SIMPLEX
    it_scale = 0.50
    it_thickness = 2
    text_size = cv2.getTextSize(instr_text, it_font, it_scale, it_thickness)[0]
    it_x = CAP_WIDTH - 420 + 18
    it_y = 20 + (80 - 20)//2 + text_size[1]//2
    cv2.putText(img, instr_text, (it_x, it_y), it_font, it_scale, (40,40,80), it_thickness, cv2.LINE_AA)

    # Gambar Target Area (rounded pastel slots)
    slot_colors = [(255,180,200),(180,220,255),(200,255,200),(255,230,180),(220,200,255)]
    for i, target in enumerate(target_positions):
        tx, ty = target
        color = slot_colors[i % len(slot_colors)]
        rounded_rect(img, (tx - 120, ty - 50), (tx + 120, ty + 50), color, radius=30)

    
    # 2. LOGIKA SEQUENTIAL PLACEMENT - tunjuk kata, keluarkan jari untuk menempatkan
    
    # Deteksi rising edge: index finger tarik
    if index_finger_up and not last_index_finger_up:
        # Index baru keluar (lepas dari kepalan) - PLACEMENT trigger
        if hovered_block is not None:
            # Hanya bisa menempatkan jika belum ada 
            if not any(b[0] == hovered_block for b in placed_blocks):
                # Tempatkan ke slot berikutnya
                next_slot_idx = len(placed_blocks)
                if next_slot_idx < len(target_positions):
                    hovered_block.pos = list(target_positions[next_slot_idx])
                    hovered_block.is_correct = (hovered_block.target_idx == next_slot_idx)
                    placed_blocks.append((hovered_block, next_slot_idx))

    last_index_finger_up = index_finger_up

    # Deteksi undo: shaka gesture (thumb + pinky) with hold debounce
    if shaka:
        shaka_frames += 1
    else:
        shaka_frames = 0
        shaka_triggered = False

    if shaka_frames >= SHAKA_HOLD_FRAMES and not shaka_triggered:
        if placed_blocks:
            block, slot_idx = placed_blocks.pop()
            block.pos = list(block.origin_pos)
            block.is_correct = False
        shaka_triggered = True

    # 3. Gambar Semua Block dan Cek Pemenang
    correct_count = 0
    for block in blocks:
        is_placed = any(b[0] == block for b in placed_blocks)
        
        # Tentukan warna
        if block.is_correct:
            draw_color = (0, 200, 0)  # Hijau (Benar)
        elif is_placed:
            draw_color = (0, 165, 255)  # Oranye (Ditempatkan salah)
        elif hovered_block == block:
            draw_color = (200, 50, 200)  # Magenta hover
        else:
            draw_color = (255, 0, 255)  # Ungu default

        # Gambar Kotak
        w, h = block.size
        cx, cy = block.pos
        base_color = (int(draw_color[0]*0.9 + 20), int(draw_color[1]*0.9 + 20), int(draw_color[2]*0.9 + 20))
        draw_shadowed_block(img, cx, cy, w, h, base_color, block.text)
        
        # Badge jika benar
        if block.is_correct:
            bx = int(cx + w//2 - 24)
            by = int(cy - h//2 + 24)
            # use green badge and ASCII 'V' to avoid unsupported glyphs
            cv2.circle(img, (bx, by), 20, (0, 200, 0), cv2.FILLED)
            cv2.putText(img, 'V', (bx-10, by+8), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255,255,255), 3, cv2.LINE_AA)

        if block.is_correct:
            correct_count += 1

    # 4. Cek Pemenang
    if correct_count == len(blocks):
        cvzone.putTextRect(img, "BENAR! GOOD JOB!", (300, 360), scale=4, thickness=3, colorR=(0, 255, 0))

    # Tampilkan Layar
    cv2.imshow("Magic Hands RPLO", img)
    
    # Keluar atau Reset
    key = cv2.waitKey(1)
    if key == ord('q') or key == 27:  # Q or ESC
        break
    elif key == ord('r'):
        placed_blocks = []
        for block in blocks:
            block.pos = list(block.origin_pos)
            block.is_correct = False
            block.color = (255, 0, 255)
        shaka_frames = 0
        shaka_triggered = False
    elif key == ord('n'):
        # Ganti ke lesson berikutnya dalam topik yang dipilih
        current_idx = lessons.index(current_lesson_key)
        next_idx = (current_idx + 1) % len(lessons)
        current_lesson_key = lessons[next_idx]
        blocks, target_positions, current_lesson = setup_lesson(current_lesson_key)
        MESSAGE = current_lesson.get('description', '')
        placed_blocks = []
        last_index_finger_up = False
        shaka_frames = 0
        shaka_triggered = False
    elif key == ord('p'):
        # Kembali ke lesson sebelumnya dalam topik yang dipilih
        current_idx = lessons.index(current_lesson_key)
        prev_idx = (current_idx - 1) % len(lessons)
        current_lesson_key = lessons[prev_idx]
        blocks, target_positions, current_lesson = setup_lesson(current_lesson_key)
        MESSAGE = current_lesson.get('description', '')
        placed_blocks = []
        last_index_finger_up = False
        shaka_frames = 0
        shaka_triggered = False

cap.release()
cv2.destroyAllWindows()