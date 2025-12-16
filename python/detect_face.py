import cv2
import mediapipe as mp
import json
import sys
from collections import deque

mp_tasks = mp.tasks
mp_vision = mp_tasks.vision
mp_image = mp.Image

BaseOptions = mp_tasks.BaseOptions
FaceLandmarker = mp_vision.FaceLandmarker
FaceLandmarkerOptions = mp_vision.FaceLandmarkerOptions
VisionRunningMode = mp_vision.RunningMode


# ============================
#   BLENDSHAPE → EKSPRESI
# ============================
def blendshapes_to_expression(blendshapes):
    if not blendshapes:
        return "no face", 0.0

    b = {bs.category_name: bs.score for bs in blendshapes}

    # ===== fitur dasar =====
    smile = (b.get("mouthSmileLeft", 0) + b.get("mouthSmileRight", 0)) / 2
    frown = (b.get("mouthFrownLeft", 0) + b.get("mouthFrownRight", 0)) / 2
    jaw_open = b.get("jawOpen", 0)
    eye_wide = (b.get("eyeWideLeft", 0) + b.get("eyeWideRight", 0)) / 2
    eye_blink = (b.get("eyeBlinkLeft", 0) + b.get("eyeBlinkRight", 0)) / 2
    cheek_puff = b.get("cheekPuff", 0)

    # ===== marah =====
    brow_lowerer = (b.get("browLowererLeft", 0) + b.get("browLowererRight", 0)) / 2
    eye_squint = (b.get("eyeSquintLeft", 0) + b.get("eyeSquintRight", 0)) / 2
    mouth_press = b.get("mouthPressLeft", 0) + b.get("mouthPressRight", 0)
    nose_sneer = (b.get("noseSneerLeft", 0) + b.get("noseSneerRight", 0)) / 2

    # ===== mencurigakan =====
    brow_inner_up_l = b.get("browInnerUpLeft", b.get("browInnerUp", 0))
    brow_inner_up_r = b.get("browInnerUpRight", b.get("browInnerUp", 0))
    brow_asym = abs(brow_inner_up_l - brow_inner_up_r)

    scores = {}

    # 😊 bahagia
    scores["bahagia"] = (
        smile * 0.65 +
        cheek_puff * 0.25 -
        frown * 0.3
    )

    # 😲 terkejut
    scores["terkejut"] = (
        jaw_open * 0.55 +
        eye_wide * 0.45 +
        b.get("browInnerUp", 0) * 0.35
    )

    # 😡 marah (sensitif tapi realistis)
    scores["marah"] = (
        brow_lowerer * 0.6 +
        nose_sneer * 0.6 +
        mouth_press * 0.45 +
        eye_squint * 0.4 -
        smile * 0.5
    )

    # 😢 sedih
    scores["sedih"] = (
        frown * 0.67 +
        b.get("browInnerUp", 0) * 0.4 -
        smile * 0.3
    )

    # 😴 ngantuk
    scores["ngantuk"] = (
        eye_blink * 0.7 -
        eye_wide * 0.35
    )

    # 🧐 mencurigakan (DIKETATKAN, TAPI TIDAK DIMATIKAN)
    scores["mencurigakan"] = (
        brow_asym * 0.35 +
        (1 - eye_wide) * 0.3 -
        mouth_press * 0.45 -
        brow_lowerer * 0.4
    )

    # ===== threshold realistis =====
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

    # 😐 NETRAL SEBAGAI FALLBACK
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
#   MAIN
# ============================
def main():
    camera_index = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 0
    print(f"[INFO] Kamera index: {camera_index}")

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(
            model_asset_path="D:/Kuliah/RPLO/E-learning_App/python/face_landmarker.task"
        ),
        running_mode=VisionRunningMode.IMAGE,
        output_face_blendshapes=True,
        num_faces=1,
    )

    cap = cv2.VideoCapture(camera_index)

    # gunakan resolusi tertinggi kamera
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    with FaceLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                print(json.dumps({"error": "Camera not accessible"}))
                break

            frame = crop_to_16_9(frame)

            h, w, _ = frame.shape
            expression, confidence, box = process_frame(landmarker, frame)

            if box:
                x1 = int(box[0] * w)
                y1 = int(box[1] * h)
                x2 = int(box[2] * w)
                y2 = int(box[3] * h)

                color_map = {
                    "bahagia": (0, 255, 0),
                    "terkejut": (255, 255, 0),
                    "marah": (0, 0, 255),
                    "sedih": (255, 0, 0),
                    "ngantuk": (255, 0, 255),
                    "mencurigakan": (0, 255, 255),
                    "netral": (200, 200, 200),
                    "no face": (100, 100, 100),
                }

                color = color_map.get(expression, (255, 255, 255))
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                cv2.putText(
                    frame,
                    f"{expression} ({confidence:.2f})",
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2
                )

            cv2.imshow("E-Learning Emotion Detection", frame)

            print(json.dumps({
                "expression": expression,
                "confidence": confidence
            }), flush=True)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
