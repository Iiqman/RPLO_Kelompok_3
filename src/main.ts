import { app, BrowserWindow, ipcMain } from 'electron';
import path from 'node:path';
import started from 'electron-squirrel-startup';
import { spawn } from 'child_process';

// Quit if launched by electron-squirrel-startup (Windows installer shortcut handling)
if (started) {
  app.quit();
}

// Determine if we're in development mode
const isDev = !app.isPackaged;
const devURL = process.env.VITE_DEV_SERVER_URL || 'http://localhost:5173';
const prodPath = path.join(__dirname, '../dist/index.html');


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

// Python runner
function runPython(script: string, args: string[] = []) {
  return new Promise<string>((resolve, reject) => {
    const py = spawn('python', [script, ...args]);

    let data = '';
    py.stdout.on('data', (chunk) => {
      data += chunk.toString();
    });

    py.stderr.on('data', (err) => {
      console.error('Python error:', err.toString());
    });

    py.on('close', () => {
      resolve(data.trim());
    });
  });
}

// IPC handler
ipcMain.handle('detect-face', async () => {
  const result = await runPython('python/detect_face.py');
  return result;
});