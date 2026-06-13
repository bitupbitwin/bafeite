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
  // npm run preview 预览生产构建时也代理 /api 到后端
  preview: {
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
