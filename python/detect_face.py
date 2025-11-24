import cv2
import mediapipe as mp
import json
import os

# Setup MediaPipe Face Landmarker
BaseOptions = mp.tasks.BaseOptions
VisionRunningMode = mp.tasks.vision.RunningMode
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions

# Pastikan file model ada di folder yang sama dengan script
model_path = os.path.join(os.path.dirname(__file__), "face_landmarker.task")

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    output_face_blendshapes=True
)

# Ekspresi target dan mapping
target_expressions = {
    "smile": "bahagia",
    "frown": "marah",
    "mouthOpen": "terkejut",
    "eyeSquintLeft": "sedih",
    "eyeSquintRight": "sedih"
}

# Fungsi klasifikasi ekspresi dari blendshape
def classify_expression(blendshapes):
    # blendshapes sudah berupa list of Category
    scores = {b.category_name: b.score for b in blendshapes}
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    for name, score in sorted_scores:
        if name in target_expressions and score > 0.5:
            return target_expressions[name], scores
    return "neutral", scores

# Kamera
cap = cv2.VideoCapture(0)

with FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print(json.dumps({"error": "Camera not accessible"}))
            break

        # Convert frame ke format MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        timestamp = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        # Deteksi wajah (pakai detect_for_video)
        result = landmarker.detect_for_video(mp_image, timestamp)

        expression = "no face"
        scores = {}

        if result.face_blendshapes:
            # Ambil list blendshapes dari wajah pertama
            expression, scores = classify_expression(result.face_blendshapes[0])

        # Tampilkan ekspresi
        cv2.putText(frame, f"Expression: {expression}", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Tampilkan nilai blendshape utama
        y_offset = 60
        for name in ["smile", "frown", "mouthOpen", "eyeSquintLeft", "eyeSquintRight"]:
            if name in scores:
                cv2.putText(frame, f"{name}: {scores[name]:.2f}", (30, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                y_offset += 30

        cv2.imshow("Camera Feed", frame)

        # Kirim ekspresi ke Electron
        print(json.dumps({"expression": expression}), flush=True)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()