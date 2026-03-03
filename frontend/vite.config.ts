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
        allowedHosts: [
          '7869c576.r33.cpolar.top',
          '.cpolar.top', // 允许所有 cpolar.top 子域名
        ],
        hmr: {
          protocol: 'wss', // 使用安全的 WebSocket 协议（HTTPS 页面必须用 wss）
          host: '7869c576.r33.cpolar.top',
          clientPort: 443, // cpolar 使用 HTTPS，所以 WebSocket 也走 443 端口
        },
        proxy: {
          '/dashscope-api': {
            target: 'https://dashscope.aliyuncs.com',
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/dashscope-api/, ''),
          },
          // 代理记忆服务（端口 8000）
          '/api/memory': {
            target: 'http://localhost:8000',
            changeOrigin: true,
            // 不重写路径，保持 /api/memory 前缀
          },
          // 代理 RAG 知识库服务（端口 8001）
          '/api/rag': {
            target: 'http://localhost:8001',
            changeOrigin: true,
            // 不重写路径，保持 /api/rag 前缀
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
        // WebSocket 错误处理插件：防止 HMR WebSocket 错误导致进程崩溃
        {
          name: 'websocket-error-handler',
          configureServer(server) {
            // 在服务器启动后添加 WebSocket 错误处理
            server.httpServer?.on('upgrade', (req, socket) => {
              // 捕获 socket 错误，防止进程崩溃
              socket.on('error', (err: any) => {
                // 忽略 WebSocket 状态码 1006 错误（cpolar 代理导致的已知问题）
                if (err.code === 'WS_ERR_INVALID_CLOSE_CODE' || 
                    (err.message && err.message.includes('invalid status code 1006'))) {
                  console.warn('[vite] WebSocket error (ignored):', err.message);
                  return;
                }
                // 其他错误正常记录
                console.error('[vite] WebSocket error:', err);
              });
            });

            // 捕获 WebSocket 服务器的错误
            if (server.ws) {
              const originalOn = server.ws.on?.bind(server.ws);
              if (originalOn) {
                server.ws.on = function(event: string, handler: any) {
                  if (event === 'error') {
                    // 包装错误处理器
                    const wrappedHandler = (err: any) => {
                      if (err.code === 'WS_ERR_INVALID_CLOSE_CODE' || 
                          (err.message && err.message.includes('invalid status code 1006'))) {
                        console.warn('[vite] HMR WebSocket error (ignored):', err.message);
                        return;
                      }
                      handler(err);
                    };
                    return originalOn(event, wrappedHandler);
                  }
                  return originalOn(event, handler);
                };
              }
            }
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

// 全局捕获未处理的错误，防止进程崩溃
process.on('uncaughtException', (err: any) => {
  if (err.code === 'WS_ERR_INVALID_CLOSE_CODE' || 
      (err.message && err.message.includes('invalid status code 1006'))) {
    console.warn('[vite] Uncaught WebSocket error (ignored):', err.message);
    return;
  }
  // 其他未捕获的错误正常处理
  console.error('[vite] Uncaught exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason: any) => {
  if (reason?.code === 'WS_ERR_INVALID_CLOSE_CODE' || 
      (reason?.message && reason.message.includes('invalid status code 1006'))) {
    console.warn('[vite] Unhandled WebSocket rejection (ignored):', reason.message);
    return;
  }
  // 其他未处理的 Promise 拒绝正常处理
  console.error('[vite] Unhandled rejection:', reason);
});
