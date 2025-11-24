import { contextBridge, ipcRenderer } from 'electron';

contextBridge.exposeInMainWorld('api', {
  detectFace: () => ipcRenderer.invoke('detect-face'),
});