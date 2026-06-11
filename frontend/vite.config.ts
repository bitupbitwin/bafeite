import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// 开发时将 /api 请求代理到本地 FastAPI 后端
export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
