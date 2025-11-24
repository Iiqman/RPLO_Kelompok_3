import cv2
import json
from fer import FER
import mediapipe as mp

# Inisialisasi FER
detector = FER(mtcnn=True)

# Inisialisasi MediaPipe FaceMesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # gunakan CAP_DSHOW agar kamera lebih stabil di Windows

while True:
    ret, frame = cap.read()
    if not ret:
        print(json.dumps({"error": "Camera not accessible"}))
        break

    # ====== Deteksi Ekspresi dengan FER ======
    result = detector.detect_emotions(frame)
    expression = "no face"
    scores = {}

    if result:
        top_result = result[0]["emotions"]
        expression = max(top_result, key=top_result.get)
        scores = top_result

    # Tampilkan ekspresi di layar
    cv2.putText(frame, f"Expression: {expression}", (30, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Tampilkan skor confidence tiap ekspresi
    y_offset = 60
    for name, score in scores.items():
        cv2.putText(frame, f"{name}: {score:.2f}", (30, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        y_offset += 30

    # ====== Landmark Wajah dengan MediaPipe ======
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        for landmarks in results.multi_face_landmarks:
            for lm in landmarks.landmark:
                x = int(lm.x * frame.shape[1])
                y = int(lm.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (0, 255, 255), -1)

    # ====== Tampilkan Hasil ======
    cv2.imshow("FER + FaceMesh", frame)

    # Kirim ekspresi ke Electron (opsional)
    print(json.dumps({"expression": expression}), flush=True)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()