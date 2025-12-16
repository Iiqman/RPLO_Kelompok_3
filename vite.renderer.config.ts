import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  root: path.join(__dirname, 'src'),
  base: './',
  plugins: [react()],
  build: {
    outDir: path.join(__dirname, 'dist', 'renderer'),
    emptyOutDir: true,
    rollupOptions: {
      input: path.join(__dirname, 'src', 'main.tsx'),
    },
  },
});