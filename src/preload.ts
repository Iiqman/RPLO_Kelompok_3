import { contextBridge, ipcRenderer } from "electron";

contextBridge.exposeInMainWorld("api", {
  detectFace: (cameraIndex: number) => ipcRenderer.invoke("detect-face", cameraIndex),
  runGuessGame: (cameraIndex: number) => ipcRenderer.invoke("run-guess-game", cameraIndex),
  drawEmoji: () => ipcRenderer.invoke("draw-emoji"),
  runQuiz: () => ipcRenderer.invoke("run-quiz"),
  runQuizEditor: () => ipcRenderer.invoke("run-quiz-editor"),
  runGuessEditor: () => ipcRenderer.invoke("run-guess-editor"),
});
