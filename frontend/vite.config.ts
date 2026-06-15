import path from 'path';
import https from 'https';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    // 从当前目录（frontend/）加载 .env 文件
    const env = loadEnv(mode, '.', '');
    
    // 从环境变量读取内网穿透地址，如果没有则使用默认值
    const tunnelHost = env.VITE_TUNNEL_HOST || '';
    
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
        strictPort: false, // 如果端口被占用，自动尝试下一个端口
        allowedHosts: [
          '.cpolar.top', // 允许所有 cpolar.top 子域名
          '.ngrok.io',   // 支持 ngrok
          '.localtunnel.me', // 支持 localtunnel
          'localhost',
        ],
        hmr: tunnelHost ? {
          // 如果配置了内网穿透地址，使用 WSS 协议
          protocol: 'wss',
          host: tunnelHost,
          clientPort: 443,
          timeout: 120000, // 增加到 120 秒
          overlay: false, // 禁用错误覆盖层
        } : {
          // 本地开发使用默认配置
          timeout: 120000, // 增加到 120 秒
          overlay: false,
        },
        // 增加请求超时时间
        headers: {
          'Keep-Alive': 'timeout=120',
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
            rewrite: (path) => path.replace(/^\/api\/rag/, ''),
          },
          // 代理 Qwen Realtime WebSocket 服务（端口 8766）
          '/ws/qwen': {
            target: 'ws://localhost:8766',
            ws: true,
            changeOrigin: true,
          },
        },
      },
      plugins: [
        react(),
        // 图片下载代理中间件：/image-proxy/<encoded-url> → 转发到目标 URL
        {
          name: 'image-proxy',
          configureServer(server) {
            server.middlewares.use((_req, res, next) => {
              if (!_req.url?.startsWith('/image-proxy/')) return next();
              const encodedUrl = _req.url.slice('/image-proxy/'.length);
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
                // 忽略常见的 WebSocket 错误
                const ignoredErrors = [
                  'WS_ERR_INVALID_CLOSE_CODE',
                  'invalid status code 1006',
                  'ECONNRESET',
                  'EPIPE',
                  'ETIMEDOUT',
                ];
                
                const shouldIgnore = ignoredErrors.some(errType => 
                  err.code === errType || (err.message && err.message.includes(errType))
                );
                
                if (shouldIgnore) {
                  console.warn('[vite] WebSocket error (ignored):', err.code || err.message);
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
                      const ignoredErrors = [
                        'WS_ERR_INVALID_CLOSE_CODE',
                        'invalid status code 1006',
                        'ECONNRESET',
                        'EPIPE',
                        'ETIMEDOUT',
                      ];
                      
                      const shouldIgnore = ignoredErrors.some(errType => 
                        err.code === errType || (err.message && err.message.includes(errType))
                      );
                      
                      if (shouldIgnore) {
                        console.warn('[vite] HMR WebSocket error (ignored):', err.code || err.message);
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
  const ignoredErrors = [
    'WS_ERR_INVALID_CLOSE_CODE',
    'invalid status code 1006',
    'ECONNRESET',
    'EPIPE',
    'ETIMEDOUT',
  ];
  
  const shouldIgnore = ignoredErrors.some(errType => 
    err.code === errType || (err.message && err.message.includes(errType))
  );
  
  if (shouldIgnore) {
    console.warn('[vite] Uncaught error (ignored):', err.code || err.message);
    return;
  }
  
  // 其他未捕获的错误正常处理
  console.error('[vite] Uncaught exception:', err);
  process.exit(1);
});

process.on('unhandledRejection', (reason: any) => {
  const ignoredErrors = [
    'WS_ERR_INVALID_CLOSE_CODE',
    'invalid status code 1006',
    'ECONNRESET',
    'EPIPE',
    'ETIMEDOUT',
  ];
  
  const shouldIgnore = ignoredErrors.some(errType => 
    reason?.code === errType || (reason?.message && reason.message.includes(errType))
  );
  
  if (shouldIgnore) {
    console.warn('[vite] Unhandled rejection (ignored):', reason?.code || reason?.message);
    return;
  }
  
  // 其他未处理的 Promise 拒绝正常处理
  console.error('[vite] Unhandled rejection:', reason);
});
