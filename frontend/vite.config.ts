import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '..', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        'process.env.API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.GEMINI_API_KEY),
        'process.env.DASHSCOPE_API_KEY': JSON.stringify(env.VITE_DASHSCOPE_API_KEY),
        'process.env.DASHSCOPE_BASE_URL': JSON.stringify(env.VITE_DASHSCOPE_BASE_URL),
        'process.env.DASHSCOPE_MODEL': JSON.stringify(env.VITE_DASHSCOPE_MODEL),
        'process.env.MAX_IMAGE_SIZE': JSON.stringify(env.VITE_MAX_IMAGE_SIZE),
        'process.env.MAX_VIDEO_SIZE': JSON.stringify(env.VITE_MAX_VIDEO_SIZE)
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
