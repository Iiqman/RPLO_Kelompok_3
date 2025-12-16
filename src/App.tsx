import React, { useEffect, useState } from 'react';

const App = () => {
  const [expression, setExpression] = useState<string | null>(null);
  const [emoji, setEmoji] = useState<string | null>(null);
  const [quizResult, setQuizResult] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [loadingFace, setLoadingFace] = useState<boolean>(false);
  const [loadingEmoji, setLoadingEmoji] = useState<boolean>(false);
  const [loadingQuiz, setLoadingQuiz] = useState<boolean>(false);

  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [selectedCameraIndex, setSelectedCameraIndex] = useState<number>(0);

  // Ambil daftar kamera saat komponen dimount
  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then(devices => {
      const videoInputs = devices.filter(d => d.kind === 'videoinput');
      setCameras(videoInputs);

      if (videoInputs.length === 0) {
        setError("Tidak ada kamera yang terdeteksi");
      }
    });
  }, []);

  // Jika daftar kamera berubah, pastikan index valid
  useEffect(() => {
    if (cameras.length > 0 && selectedCameraIndex >= cameras.length) {
      setSelectedCameraIndex(0);
    }
  }, [cameras]);

  // ============================
  // ✅ HANDLE DETEKSI WAJAH
  // ============================
  const handleDetectFace = async () => {
    setLoadingFace(true);
    setError(null);
    setExpression(null);

    if (
      selectedCameraIndex === undefined ||
      selectedCameraIndex === null ||
      isNaN(selectedCameraIndex)
    ) {
      setError("Kamera belum dipilih");
      setLoadingFace(false);
      return;
    }

    try {
      const result = await window.api.detectFace(selectedCameraIndex);
      const data = JSON.parse(result);

      if (data.error) {
        setError(data.error);
      } else {
        setExpression(data.expression);
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Error saat menjalankan deteksi wajah");
    }

    setLoadingFace(false);
  };

  // ============================
  // ✅ HANDLE MODE MENGGAMBAR (EMOJI)
  // ============================
  const handleDrawEmoji = async () => {
    setLoadingEmoji(true);
    setEmoji(null);
    setError(null);

    try {
      const result = await window.api.drawEmoji();
      const data = JSON.parse(result);

      if (data.error) {
        setError(data.error);
      } else {
        setEmoji(data.emoji);
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Error saat menjalankan mode menggambar");
    }

    setLoadingEmoji(false);
  };

  // ============================
  // ✅ HANDLE KUIS BAHASA INGGRIS
  // ============================
  const handleRunQuiz = async () => {
    setLoadingQuiz(true);
    setQuizResult(null);
    setError(null);

    try {
      const result = await window.api.runQuiz();
      const data = JSON.parse(result);

      if (data.error) {
        setError(data.error);
      } else {
        setQuizResult(data.question || "Kuis selesai");
      }
    } catch (err) {
      console.error("Error:", err);
      setError("Error saat menjalankan kuis");
    }

    setLoadingQuiz(false);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: 500 }}>
      <h1>E-Learning App</h1>
      <p>Face Tracking + Gesture Drawing + Emoji Recognition + Quiz</p>

      {/* ✅ Dropdown kamera */}
      <label htmlFor="camera-select" style={{ fontWeight: 'bold' }}>
        Pilih Kamera:
      </label>

      <select
        id="camera-select"
        value={selectedCameraIndex}
        onChange={(e) => setSelectedCameraIndex(Number(e.target.value))}
        style={{
          marginBottom: '1rem',
          display: 'block',
          padding: '0.4rem',
          width: '100%',
        }}
        disabled={loadingFace || loadingEmoji || loadingQuiz || cameras.length === 0}
      >
        {cameras.length > 0 ? (
          cameras.map((cam, index) => (
            <option key={index} value={index}>
              {cam.label || `Kamera ${index}`}
            </option>
          ))
        ) : (
          <option>Tidak ada kamera</option>
        )}
      </select>

      {/* ✅ Tombol deteksi wajah */}
      <button
        onClick={handleDetectFace}
        disabled={loadingFace || loadingEmoji || loadingQuiz || cameras.length === 0}
        style={{
          padding: '0.6rem 1rem',
          cursor: loadingFace ? 'not-allowed' : 'pointer',
          opacity: loadingFace ? 0.6 : 1,
          marginRight: '1rem'
        }}
      >
        {loadingFace ? "Mendeteksi..." : "Deteksi Wajah"}
      </button>

      {/* ✅ Tombol mode menggambar */}
      <button
        onClick={handleDrawEmoji}
        disabled={loadingFace || loadingEmoji || loadingQuiz}
        style={{
          padding: '0.6rem 1rem',
          cursor: loadingEmoji ? 'not-allowed' : 'pointer',
          opacity: loadingEmoji ? 0.6 : 1,
          marginRight: '1rem'
        }}
      >
        {loadingEmoji ? "Menunggu Gambar..." : "Mode Menggambar (Emoji)"}
      </button>

      {/* ✅ Tombol kuis */}
      <button
        onClick={handleRunQuiz}
        disabled={loadingFace || loadingEmoji || loadingQuiz}
        style={{
          padding: '0.6rem 1rem',
          cursor: loadingQuiz ? 'not-allowed' : 'pointer',
          opacity: loadingQuiz ? 0.6 : 1,
        }}
      >
        {loadingQuiz ? "Menjalankan Kuis..." : "Mulai Kuis Bahasa Inggris"}
      </button>

      {/* ✅ Error message */}
      {error && (
        <p style={{ color: 'red', marginTop: '1rem' }}>
          {error}
        </p>
      )}

      {/* ✅ Hasil ekspresi wajah */}
      {expression && !error && (
        <p style={{ marginTop: '1rem', fontSize: '1.1rem' }}>
          Ekspresi terdeteksi: <strong>{expression}</strong>
        </p>
      )}

      {/* ✅ Hasil emoji */}
      {emoji && !error && (
        <p style={{ marginTop: '1rem', fontSize: '1.3rem' }}>
          Emoji terdeteksi: <strong>{emoji}</strong>
        </p>
      )}

      {/* ✅ Hasil kuis */}
      {quizResult && !error && (
        <p style={{ marginTop: '1rem', fontSize: '1.1rem' }}>
          Soal kuis: <strong>{quizResult}</strong>
        </p>
      )}
    </div>
  );
};

export default App;