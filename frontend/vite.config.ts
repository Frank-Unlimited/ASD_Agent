import path from 'path';
import https from 'https';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    // 从当前目录（frontend/）加载 .env 文件
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
        proxy: {
          '/dashscope-api': {
            target: 'https://dashscope.aliyuncs.com',
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/dashscope-api/, ''),
          },
        },
      },
      plugins: [
        react(),
        // 图片下载代理中间件：/image-proxy/<encoded-url> → 转发到目标 URL
        {
          name: 'image-proxy',
          configureServer(server) {
            server.middlewares.use((req, res, next) => {
              if (!req.url?.startsWith('/image-proxy/')) return next();
              const encodedUrl = req.url.slice('/image-proxy/'.length);
              const targetUrl = decodeURIComponent(encodedUrl);
              https.get(targetUrl, (imgRes) => {
                // 只保留安全的响应头
                const headers: Record<string, string> = {};
                if (imgRes.headers['content-type']) headers['content-type'] = imgRes.headers['content-type'];
                if (imgRes.headers['content-length']) headers['content-length'] = imgRes.headers['content-length'];
                res.writeHead(imgRes.statusCode || 200, headers);
                imgRes.pipe(res);
              }).on('error', (err) => {
                res.writeHead(502, { 'content-type': 'text/plain' });
                res.end(`Proxy error: ${err.message}`);
              });
            });
          },
        },
      ],
      define: {
        // Qwen service uses import.meta.env, no need to define process.env
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
