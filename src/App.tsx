import React, { useState } from 'react';

const App = () => {
  const [expression, setExpression] = useState<string | null>(null);

  const handleDetectFace = async () => {
    try {
      const result = await window.api.detectFace();
      const data = JSON.parse(result);
      setExpression(data.expression); // simpan ke state
    } catch (err) {
      console.error("Error:", err);
      setExpression("Error saat deteksi wajah");
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'sans-serif' }}>
      <h1>Hello from React + Vite + Electron!</h1>
      <p>This is your starting point for the e-learning app.</p>

      <button onClick={handleDetectFace}>Deteksi Wajah</button>

      {/* tampilkan hasil di layar */}
      {expression && <p>Ekspresi terdeteksi: {expression}</p>}
    </div>
  );
};

export default App;