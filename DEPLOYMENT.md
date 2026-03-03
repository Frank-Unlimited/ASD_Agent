# 内网穿透部署指南

## 概述

本项目包含前端（端口 3000）和两个后端服务（端口 8000、8001）。通过 Vite 代理功能，只需暴露前端端口 3000，即可同时访问前后端服务。

## 架构说明

```
外部设备（手机/其他电脑）
    ↓ HTTPS
内网穿透（cpolar）→ 端口 3000（前端 Vite 服务器）
                        ↓
                    Vite 代理（自动处理 HTTP/WS → HTTPS/WSS）
                    ↙        ↓        ↘
        端口 8000      端口 8766      端口 8001
      （记忆服务）  （Qwen WebSocket） （RAG 知识库）
```

## 重要说明：HTTPS 混合内容问题

当通过 HTTPS 内网穿透（如 cpolar）访问前端时，浏览器会阻止前端直接访问 HTTP/WS 后端服务（混合内容安全策略）。

**解决方案**：使用 Vite 代理转发所有请求
- 前端使用相对路径（`/api/memory`、`/api/rag`、`/ws/qwen`）
- Vite 代理自动转发到本地 HTTP/WS 服务
- 外部设备只看到 HTTPS/WSS 连接，符合浏览器安全要求

## 配置步骤

### 1. Vite 代理配置（已完成）

`vite.config.ts` 已配置代理规则：
- `/api/memory/*` → `http://localhost:8000/*`（记忆服务）
- `/api/rag/*` → `http://localhost:8001/*`（RAG 知识库，路径重写）
- `/ws/qwen` → `ws://localhost:8766`（Qwen 实时通话 WebSocket）

### 2. 前端环境变量（已完成）

`frontend/.env` 已配置相对路径：
```env
VITE_MEMORY_SERVICE_URL=/api/memory
VITE_RAG_SERVICE_URL=/api/rag
# Qwen WebSocket 自动根据当前协议选择 ws:// 或 wss://
```

### 3. 启动服务

#### 启动后端服务

```bash
cd ASD_Agent/backend
start_services.bat
```

这会启动：
- 记忆服务（端口 8000）
- RAG 知识库服务（端口 8001）
- Qwen Realtime WebSocket 服务（端口 8766）
- Neo4j 数据库（端口 7474, 7687）

#### 启动前端服务

```bash
cd ASD_Agent/frontend
npm run dev
```

前端服务运行在端口 3000。

### 4. 配置内网穿透（只需一个隧道）

```bash
cpolar http 3000
```

假设获得域名：`https://7869c576.r33.cpolar.top`

### 5. 更新 Vite 配置中的域名

修改 `vite.config.ts` 中的 `allowedHosts` 和 `hmr.host`：

```typescript
allowedHosts: [
  '7869c576.r33.cpolar.top',  // 你的实际域名
  '.cpolar.top',
],
hmr: {
  protocol: 'wss',
  host: '7869c576.r33.cpolar.top',  // 你的实际域名
  clientPort: 443,
},
```

### 6. 重启前端服务

修改配置后需要重启 Vite 服务器。

## 验证部署

1. 访问前端：`https://7869c576.r33.cpolar.top`
2. 测试记忆搜索功能（会通过 `/api/memory` 代理到后端）
3. 测试 RAG 搜索功能（会通过 `/api/rag` 代理到后端）
4. 检查浏览器控制台是否有错误

## 请求路径示例

外部设备访问时的请求流程：

```
前端页面：https://7869c576.r33.cpolar.top
    ↓
记忆搜索：https://7869c576.r33.cpolar.top/api/memory/search
    ↓ (Vite 代理)
实际请求：http://localhost:8000/search
    ↓
记忆服务响应

RAG 搜索：https://7869c576.r33.cpolar.top/api/rag/healthcheck
    ↓ (Vite 代理 + 路径重写)
实际请求：http://localhost:8001/healthcheck
    ↓
RAG 服务响应

WebSocket：wss://7869c576.r33.cpolar.top/ws/qwen
    ↓ (Vite WebSocket 代理)
实际连接：ws://localhost:8766
    ↓
Qwen 实时通话服务
```

## 优势

1. **只需一个内网穿透隧道**：节省资源，配置简单
2. **无需 CORS 配置**：前后端同源，避免跨域问题
3. **统一入口**：所有请求通过同一个域名
4. **开发生产一致**：本地开发和远程访问使用相同配置
5. **自动协议适配**：HTTP/WS 自动转换为 HTTPS/WSS，符合浏览器安全要求
6. **支持手机访问**：解决 HTTPS 混合内容问题，手机浏览器可正常使用所有功能

## 注意事项

1. **域名变化**：cpolar 免费版域名会定期变化，需要更新 `vite.config.ts` 中的域名配置
2. **后端必须运行**：确保所有后端服务（8000、8001、8766）在本地正常运行
3. **代理路径**：前端代码中使用相对路径（`/api/memory`、`/api/rag`、`/ws/qwen`）
4. **WebSocket**：HMR 和 Qwen 实时通话都使用 WSS 协议，确保配置正确
5. **手机权限**：手机访问摄像头/麦克风需要 HTTPS，cpolar 提供的域名已支持

## 故障排查

### 问题：无法访问后端服务

检查：
1. 后端服务是否正常运行（`http://localhost:8000/health`）
2. Vite 代理配置是否正确
3. 浏览器控制台是否有 404 或 502 错误

### 问题：WebSocket 连接失败

检查：
1. `vite.config.ts` 中 `hmr.protocol` 是否为 `wss`
2. `hmr.host` 是否为正确的内网穿透域名
3. cpolar 是否支持 WebSocket（默认支持）
4. Qwen WebSocket 服务（端口 8766）是否正常运行

### 问题：手机无法访问摄像头/麦克风

错误：`NotAllowedError: Permission denied`

原因：
- 手机浏览器要求 HTTPS 才能访问摄像头/麦克风
- 前端尝试连接 HTTP/WS 后端被浏览器阻止（混合内容）

解决：
1. 确保通过 HTTPS 内网穿透域名访问（如 `https://xxx.cpolar.top`）
2. 确保前端使用相对路径，通过 Vite 代理访问后端
3. 检查浏览器控制台是否有 "Mixed Content" 错误

### 问题：CORS 错误

如果使用代理仍有 CORS 错误，检查：
1. 请求路径是否以 `/api/memory`、`/api/rag` 或 `/ws/qwen` 开头
2. 是否直接使用了 `localhost:8000` 而不是代理路径
3. 环境变量中是否配置了绝对 URL（应该使用相对路径）

## 生产环境建议

对于生产环境，建议：

1. 使用云服务器部署（阿里云、腾讯云等）
2. 配置 Nginx 反向代理替代 Vite 代理
3. 使用固定域名和 SSL 证书
4. 配置防火墙和安全组规则
5. 使用 PM2 或 systemd 管理服务进程
