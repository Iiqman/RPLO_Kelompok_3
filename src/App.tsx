import React, { useEffect, useState } from 'react';

const App = () => {
  const [expression, setExpression] = useState<string | null>(null);
  const [emoji, setEmoji] = useState<string | null>(null);
  const [quizResult, setQuizResult] = useState<string | null>(null);
  const [guessResult, setGuessResult] = useState<string | null>(null);
  const [editorStatus, setEditorStatus] = useState<string | null>(null);

  const [error, setError] = useState<string | null>(null);
  const [loadingFace, setLoadingFace] = useState<boolean>(false);
  const [loadingEmoji, setLoadingEmoji] = useState<boolean>(false);
  const [loadingQuiz, setLoadingQuiz] = useState<boolean>(false);
  const [loadingGuess, setLoadingGuess] = useState<boolean>(false);
  const [loadingEditor, setLoadingEditor] = useState<boolean>(false);

  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);
  const [selectedCameraIndex, setSelectedCameraIndex] = useState<number>(0);

  // Ambil daftar kamera
  useEffect(() => {
    navigator.mediaDevices.enumerateDevices().then(devices => {
      const videoInputs = devices.filter(d => d.kind === 'videoinput');
      setCameras(videoInputs);

      if (videoInputs.length === 0) {
        setError("Tidak ada kamera yang terdeteksi");
      }
    });
  }, []);

  // Pastikan index kamera valid
  useEffect(() => {
    if (cameras.length > 0 && selectedCameraIndex >= cameras.length) {
      setSelectedCameraIndex(0);
    }
  }, [cameras]);

  // ✅ DETEKSI WAJAH
  const handleDetectFace = async () => {
    setLoadingFace(true);
    setError(null);
    setExpression(null);

    try {
      const result = await window.api.detectFace(selectedCameraIndex);
      const data = JSON.parse(result);

      if (data.error) setError(data.error);
      else setExpression(data.expression);
    } catch {
      setError("Error saat menjalankan deteksi wajah");
    }

    setLoadingFace(false);
  };

  // ✅ MODE MENGGAMBAR (EMOJI)
  const handleDrawEmoji = async () => {
    setLoadingEmoji(true);
    setEmoji(null);
    setError(null);

    try {
      const result = await window.api.drawEmoji();
      const data = JSON.parse(result);

      if (data.error) setError(data.error);
      else setEmoji(data.emoji);
    } catch {
      setError("Error saat menjalankan mode menggambar");
    }

    setLoadingEmoji(false);
  };

  // ✅ KUIS BAHASA INGGRIS
  const handleRunQuiz = async () => {
    setLoadingQuiz(true);
    setQuizResult(null);
    setError(null);

    try {
      const result = await window.api.runQuiz();
      const data = JSON.parse(result);

      if (data.error) setError(data.error);
      else setQuizResult(data.question || "Kuis selesai");
    } catch {
      setError("Error saat menjalankan kuis");
    }

    setLoadingQuiz(false);
  };

  // ✅ GUESS GAME
  const handleRunGuessGame = async () => {
    setLoadingGuess(true);
    setGuessResult(null);
    setError(null);

    try {
      const result = await window.api.runGuessGame();
      const data = JSON.parse(result);

      if (data.error) setError(data.error);
      else setGuessResult(data.message || "Game selesai");
    } catch {
      setError("Error saat menjalankan guess game");
    }

    setLoadingGuess(false);
  };

  // ✅ QUIZ EDITOR
  const handleRunQuizEditor = async () => {
    setLoadingEditor(true);
    setEditorStatus(null);
    setError(null);

    try {
      const result = await window.api.runQuizEditor();
      const data = JSON.parse(result);

      if (data.error) setError(data.error);
      else setEditorStatus(data.status || "Editor selesai");
    } catch {
      setError("Error saat membuka quiz editor");
    }

    setLoadingEditor(false);
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif', maxWidth: 500 }}>
      <h1>E-Learning App</h1>
      <p>Face Tracking + Gesture Drawing + Emoji Recognition + Quiz + Games</p>

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
        disabled={loadingFace || loadingEmoji || loadingQuiz}
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
        disabled={loadingFace}
        style={{ padding: '0.6rem 1rem', marginRight: '1rem' }}
      >
        {loadingFace ? "Mendeteksi..." : "Deteksi Wajah"}
      </button>

      {/* ✅ Tombol mode menggambar */}
      <button
        onClick={handleDrawEmoji}
        disabled={loadingEmoji}
        style={{ padding: '0.6rem 1rem', marginRight: '1rem' }}
      >
        {loadingEmoji ? "Menunggu Gambar..." : "Mode Menggambar (Emoji)"}
      </button>

      {/* ✅ Tombol kuis */}
      <button
        onClick={handleRunQuiz}
        disabled={loadingQuiz}
        style={{ padding: '0.6rem 1rem', marginRight: '1rem' }}
      >
        {loadingQuiz ? "Menjalankan Kuis..." : "Mulai Kuis Bahasa Inggris"}
      </button>

      {/* ✅ Tombol Guess Game */}
      <button
        onClick={handleRunGuessGame}
        disabled={loadingGuess}
        style={{ padding: '0.6rem 1rem', marginTop: '1rem' }}
      >
        {loadingGuess ? "Menjalankan Game..." : "Guess Game"}
      </button>

      {/* ✅ Tombol Quiz Editor */}
      <button
        onClick={handleRunQuizEditor}
        disabled={loadingEditor}
        style={{ padding: '0.6rem 1rem', marginTop: '1rem' }}
      >
        {loadingEditor ? "Membuka Editor..." : "Quiz Editor"}
      </button>

      {/* ✅ Error */}
      {error && <p style={{ color: 'red', marginTop: '1rem' }}>{error}</p>}

      {/* ✅ Output */}
      {expression && !error && (
        <p style={{ marginTop: '1rem' }}>
          Ekspresi terdeteksi: <strong>{expression}</strong>
        </p>
      )}

      {emoji && !error && (
        <p style={{ marginTop: '1rem' }}>
          Emoji terdeteksi: <strong>{emoji}</strong>
        </p>
      )}

      {quizResult && !error && (
        <p style={{ marginTop: '1rem' }}>
          Soal kuis: <strong>{quizResult}</strong>
        </p>
      )}

      {guessResult && !error && (
        <p style={{ marginTop: '1rem' }}>
          Hasil Guess Game: <strong>{guessResult}</strong>
        </p>
      )}

      {editorStatus && !error && (
        <p style={{ marginTop: '1rem' }}>
          Status Editor: <strong>{editorStatus}</strong>
        </p>
      )}
    </div>
  );
};

export default App;