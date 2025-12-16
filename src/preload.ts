import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  detectFace: (cameraIndex: number) => ipcRenderer.invoke('detect-face', cameraIndex),
  drawEmoji: () => ipcRenderer.invoke("draw-emoji"),
  runQuiz: () => ipcRenderer.invoke("run-quiz"),
});

  