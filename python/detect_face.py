import cv2
import mediapipe as mp
import json
import sys
import os
from collections import deque
import numpy as np

mp_tasks = mp.tasks
mp_vision = mp_tasks.vision
mp_image = mp.Image

BaseOptions = mp_tasks.BaseOptions
FaceLandmarker = mp_vision.FaceLandmarker
FaceLandmarkerOptions = mp_vision.FaceLandmarkerOptions
VisionRunningMode = mp_vision.RunningMode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "face_landmarker.task")


# ============================
#   EMOJI CONFIGURATION
# ============================
EMOJI_CONFIG = {
    "bahagia": {
        "emoji": "smile.png",
        "text": "Happy",
        "description": "You're smiling!",
        "color": (0, 255, 0)
    },
    "terkejut": {
        "emoji": "surprised.png",
        "text": "Surprised",
        "description": "Wow! Shocked!",
        "color": (255, 255, 0)
    },
    "marah": {
        "emoji": "angry.png",
        "text": "Angry",
        "description": "Feeling angry",
        "color": (0, 0, 255)
    },
    "sedih": {
        "emoji": "sad.png",
        "text": "Sad",
        "description": "Feeling down",
        "color": (255, 0, 0)
    },
    "ngantuk": {
        "emoji": "sleepy.png",
        "text": "Sleepy",
        "description": "Feeling drowsy",
        "color": (255, 0, 255)
    },
    "mencurigakan": {
        "emoji": "suspicious.png",
        "text": "Suspicious",
        "description": "Looks curious",
        "color": (0, 255, 255)
    },
    "netral": {
        "emoji": "neutral.png",
        "text": "Neutral",
        "description": "Calm & focused",
        "color": (200, 200, 200)
    },
    "no face": {
        "emoji": "question.png",
        "text": "No Face",
        "description": "No face detected",
        "color": (100, 100, 100)
    }
}

# Load emoji images
emoji_images = {}
EMOJI_PATH = "assets/emojis/"


def load_emojis():
    """Load all emoji images from the assets folder"""
    print(f"[INFO] Loading emojis from: {os.path.abspath(EMOJI_PATH)}")
    
    if not os.path.exists(EMOJI_PATH):
        print(f"[ERROR] Emoji folder not found: {EMOJI_PATH}")
        print(f"[INFO] Please create the folder and add emoji images")
        return
    
    for key, config in EMOJI_CONFIG.items():
        emoji_file = os.path.join(EMOJI_PATH, config["emoji"])
        
        if os.path.exists(emoji_file):
            img = cv2.imread(emoji_file, cv2.IMREAD_UNCHANGED)
            if img is not None:
                emoji_images[key] = img
                print(f"[SUCCESS] Loaded emoji: {config['emoji']} ({img.shape})")
            else:
                print(f"[ERROR] Failed to read: {emoji_file}")
                emoji_images[key] = None
        else:
            print(f"[WARNING] Emoji not found: {emoji_file}")
            emoji_images[key] = None
    
    loaded_count = sum(1 for v in emoji_images.values() if v is not None)
    print(f"[INFO] Successfully loaded {loaded_count}/{len(EMOJI_CONFIG)} emojis")


def overlay_transparent(background, overlay, x, y, size=None):
    """Overlay transparent PNG emoji on video frame"""
    if overlay is None:
        return background
    
    # Resize emoji if size is specified
    if size:
        overlay = cv2.resize(overlay, (size, size))
    
    h, w = overlay.shape[:2]
    
    # Ensure overlay fits within background
    if x + w > background.shape[1]:
        w = background.shape[1] - x
        overlay = overlay[:, :w]
    if y + h > background.shape[0]:
        h = background.shape[0] - y
        overlay = overlay[:h, :]
    if x < 0 or y < 0:
        return background
    
    # Handle alpha channel
    if overlay.shape[2] == 4:
        alpha = overlay[:, :, 3] / 255.0
        
        for c in range(3):
            background[y:y+h, x:x+w, c] = (
                alpha * overlay[:, :, c] +
                (1 - alpha) * background[y:y+h, x:x+w, c]
            )
    else:
        background[y:y+h, x:x+w] = overlay
    
    return background


# ============================
#   BLENDSHAPE → EXPRESSION
# ============================
def blendshapes_to_expression(blendshapes):
    if not blendshapes:
        return "no face", 0.0

    b = {bs.category_name: bs.score for bs in blendshapes}

    # ===== basic features =====
    smile = (b.get("mouthSmileLeft", 0) + b.get("mouthSmileRight", 0)) / 2
    frown = (b.get("mouthFrownLeft", 0) + b.get("mouthFrownRight", 0)) / 2
    jaw_open = b.get("jawOpen", 0)
    eye_wide = (b.get("eyeWideLeft", 0) + b.get("eyeWideRight", 0)) / 2
    eye_blink = (b.get("eyeBlinkLeft", 0) + b.get("eyeBlinkRight", 0)) / 2
    cheek_puff = b.get("cheekPuff", 0)

    # ===== angry =====
    brow_lowerer = (b.get("browLowererLeft", 0) + b.get("browLowererRight", 0)) / 2
    eye_squint = (b.get("eyeSquintLeft", 0) + b.get("eyeSquintRight", 0)) / 2
    mouth_press = b.get("mouthPressLeft", 0) + b.get("mouthPressRight", 0)
    nose_sneer = (b.get("noseSneerLeft", 0) + b.get("noseSneerRight", 0)) / 2

    # ===== suspicious =====
    brow_inner_up_l = b.get("browInnerUpLeft", b.get("browInnerUp", 0))
    brow_inner_up_r = b.get("browInnerUpRight", b.get("browInnerUp", 0))
    brow_asym = abs(brow_inner_up_l - brow_inner_up_r)

    scores = {}

    # 😊 happy
    scores["bahagia"] = (
        smile * 0.65 +
        cheek_puff * 0.25 -
        frown * 0.3
    )

    # 😲 surprised
    scores["terkejut"] = (
        jaw_open * 0.55 +
        eye_wide * 0.45 +
        b.get("browInnerUp", 0) * 0.35
    )

    # 😡 angry
    scores["marah"] = (
        brow_lowerer * 0.6 +
        nose_sneer * 0.6 +
        mouth_press * 0.45 +
        eye_squint * 0.4 -
        smile * 0.5
    )

    # 😢 sad
    scores["sedih"] = (
        frown * 0.67 +
        b.get("browInnerUp", 0) * 0.4 -
        smile * 0.3
    )

    # 😴 sleepy
    scores["ngantuk"] = (
        eye_blink * 0.7 -
        eye_wide * 0.35
    )

    # 🧐 suspicious
    scores["mencurigakan"] = (
        brow_asym * 0.35 +
        (1 - eye_wide) * 0.3 -
        mouth_press * 0.45 -
        brow_lowerer * 0.4
    )

    # ===== realistic thresholds =====
    thresholds = {
        "bahagia": 0.25,
        "terkejut": 0.25,
        "marah": 0.2,
        "sedih": 0.25,
        "ngantuk": 0.25,
        "mencurigakan": 0.32
    }

    filtered = {
        k: max(0, v)
        for k, v in scores.items()
        if v > thresholds[k]
    }

    # 😐 NEUTRAL AS FALLBACK
    if not filtered:
        return "netral", 0.33

    expression = max(filtered, key=filtered.get)
    confidence = round(float(filtered[expression]), 3)

    return expression, confidence


# ============================
#   SMOOTHING
# ============================
smooth_window = deque(maxlen=5)
dominant_window = deque(maxlen=15)


# ============================
#   PROCESS FRAME
# ============================
def process_frame(landmarker, frame_bgr):
    frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    mp_img = mp_image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

    result = landmarker.detect(mp_img)

    if not result.face_landmarks or not result.face_blendshapes:
        return "no face", 0.0, None

    blendshapes = result.face_blendshapes[0]
    expression, confidence = blendshapes_to_expression(blendshapes)

    # smoothing
    smooth_window.append((expression, confidence))
    avg_conf = sum(c for _, c in smooth_window) / len(smooth_window)

    smoothed_expression = max(
        set(e for e, _ in smooth_window),
        key=lambda x: sum(1 for e, _ in smooth_window if e == x)
    )

    dominant_window.append(smoothed_expression)

    final_expression = max(
        set(dominant_window),
        key=lambda x: sum(1 for d in dominant_window if d == x)
    )

    final_confidence = round(avg_conf, 3)

    # bounding box
    face_landmarks = result.face_landmarks[0]
    xs = [lm.x for lm in face_landmarks]
    ys = [lm.y for lm in face_landmarks]

    return final_expression, final_confidence, (min(xs), min(ys), max(xs), max(ys))


# ============================
#   CROP 16:9 (NO STRETCH)
# ============================
def crop_to_16_9(frame):
    h, w, _ = frame.shape
    target_ratio = 16 / 9
    current_ratio = w / h

    if current_ratio > target_ratio:
        new_w = int(h * target_ratio)
        x1 = (w - new_w) // 2
        return frame[:, x1:x1 + new_w]
    else:
        new_h = int(w / target_ratio)
        y1 = (h - new_h) // 2
        return frame[y1:y1 + new_h, :]


# ============================
#   DRAW EMOTION UI
# ============================
def draw_emotion_ui(frame, expression, confidence, box):
    """Draw beautiful emotion UI with emoji and text"""
    h, w, _ = frame.shape
    config = EMOJI_CONFIG.get(expression, EMOJI_CONFIG["netral"])
    color = config["color"]
    
    if box:
        x1 = int(box[0] * w)
        y1 = int(box[1] * h)
        x2 = int(box[2] * w)
        y2 = int(box[3] * h)
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        
        # Calculate emoji position (top-left of bounding box)
        emoji_size = 80
        emoji_x = max(10, x1 - emoji_size - 10)
        emoji_y = max(10, y1)
        
        # Overlay emoji
        if expression in emoji_images:
            frame = overlay_transparent(frame, emoji_images[expression], emoji_x, emoji_y, emoji_size)
        
        # Draw semi-transparent background for text
        text_bg_height = 70
        text_bg_y = max(10, y1 - text_bg_height)
        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, text_bg_y), (x2, y1), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw emotion text (English)
        emotion_text = config["text"].upper()
        cv2.putText(
            frame,
            emotion_text,
            (x1 + 10, text_bg_y + 30),
            cv2.FONT_HERSHEY_COMPLEX,
            0.9,
            color,
            2
        )
        
        # Draw description
        cv2.putText(
            frame,
            config["description"],
            (x1 + 10, text_bg_y + 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 255),
            1
        )
        
        # Draw confidence bar
        bar_width = x2 - x1
        bar_height = 8
        bar_y = y2 + 10
        
        # Background bar
        cv2.rectangle(frame, (x1, bar_y), (x2, bar_y + bar_height), (50, 50, 50), -1)
        # Confidence bar
        conf_width = int(bar_width * confidence)
        cv2.rectangle(frame, (x1, bar_y), (x1 + conf_width, bar_y + bar_height), color, -1)
        
        # Confidence percentage
        cv2.putText(
            frame,
            f"{int(confidence * 100)}%",
            (x1, bar_y + bar_height + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1
        )
    
    # Draw title at top
    title = "E-Learning Emotion Detection"
    title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_COMPLEX, 1.2, 2)[0]
    title_x = (w - title_size[0]) // 2
    
    # Title background
    cv2.rectangle(frame, (title_x - 20, 10), (title_x + title_size[0] + 20, 60), (0, 0, 0), -1)
    cv2.rectangle(frame, (title_x - 20, 10), (title_x + title_size[0] + 20, 60), color, 2)
    
    cv2.putText(
        frame,
        title,
        (title_x, 45),
        cv2.FONT_HERSHEY_COMPLEX,
        1.2,
        color,
        2
    )
    
    return frame


# ============================
#   MAIN
# ============================
def main():
    # Load emoji images first
    load_emojis()
    
    camera_index = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
    print(f"[INFO] Camera index: {camera_index}")

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path=MODEL_PATH
        ),
        running_mode=VisionRunningMode.IMAGE,
        output_face_blendshapes=True,
        num_faces=1,
    )

    cap = cv2.VideoCapture(camera_index)

    # Use highest camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    with FaceLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print(json.dumps({"error": "Camera not accessible"}))
                break

            frame = crop_to_16_9(frame)
            expression, confidence, box = process_frame(landmarker, frame)

            # Draw beautiful UI
            frame = draw_emotion_ui(frame, expression, confidence, box)

            cv2.imshow("E-Learning Emotion Detection", frame)

            # Output JSON for the React app
            config = EMOJI_CONFIG.get(expression, EMOJI_CONFIG["netral"])
            print(json.dumps({
                "expression": expression,
                "expressionEnglish": config["text"],
                "description": config["description"],
                "confidence": confidence
            }), flush=True)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()