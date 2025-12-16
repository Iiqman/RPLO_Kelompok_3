import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'node:path';
import fs from 'fs';
import started from 'electron-squirrel-startup';
import { spawn } from 'child_process';

// Quit if launched by electron-squirrel-startup
if (started) {
  app.quit();
}

// Determine if we're in development mode
const isDev = !app.isPackaged;
const devURL = process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173';
const prodPath = path.join(__dirname, '../dist/index.html');

// Create window
const createWindow = () => {
  const mainWindow = new BrowserWindow({
    width: 1024,
    height: 768,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  if (isDev) {
    mainWindow.loadURL(devURL);
  } else {
    mainWindow.loadFile(prodPath);
  }
};

// App lifecycle
app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// ✅ Python runner using venv
function runPython(script: string, args: string[] = []) {
  return new Promise<string>((resolve, reject) => {
    const pythonPath = "D:\\Kuliah\\RPLO\\E-learning_App\\.venv\\Scripts\\pythonw.exe";
    const scriptPath = "D:\\Kuliah\\RPLO\\E-learning_App\\" + script.replace(/\//g, "\\");

    const py = spawn("cmd.exe", ["/c", pythonPath, scriptPath, ...args]);

    let data = "";

    py.stdout?.on("data", (chunk) => {
      data += chunk.toString();
    });

    py.stderr?.on("data", (err) => {
      console.error("🐍 Python error:", err.toString());
    });

    py.on("close", () => {
      resolve(data.trim());
    });
  });
}

// ✅ IPC handler — menerima cameraIndex dari React
ipcMain.handle("detect-face", async (_, cameraIndex) => {
  console.log("🎥 Kamera dipilih index:", cameraIndex);

  if (cameraIndex === undefined || cameraIndex === null || isNaN(cameraIndex)) {
    console.log("❌ Kamera index invalid, fallback ke 0");
    cameraIndex = 0;
  }

  const result = await runPython("python/detect_face.py", [String(cameraIndex)]);
  return result;
});

ipcMain.handle("draw-emoji", async () => {
  const result = await runPython("python/finger_draw_emoji.py");
  return result;
});

ipcMain.handle("run-quiz", async () => {
  const result = await runPython("python/quiz_game.py");
  return result;
});

ipcMain.handle("run-guess-game", async () => {
  const result = await runPython("python/guess_game.py");
  return result;
});

ipcMain.handle("run-quiz-editor", async () => {
  const result = await runPython("python/quiz_editor.py");
  return result;
});