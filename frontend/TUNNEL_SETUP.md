# 内网穿透配置指南

## 概述

本项目支持通过内网穿透（如 cpolar、ngrok）将本地开发服务器暴露到公网，方便在移动设备或远程环境中测试。

## 配置步骤

### 1. 启动内网穿透服务

#### 使用 cpolar

```bash
# 启动 cpolar 隧道（映射到本地 3000 端口）
cpolar http 3000
```

cpolar 会生成一个临时域名，例如：
```
https://52095bd8.r33.cpolar.top
```

#### 使用 ngrok

```bash
# 启动 ngrok 隧道
ngrok http 3000
```

ngrok 会生成一个临时域名，例如：
```
https://abc123.ngrok.io
```

### 2. 配置环境变量

编辑 `frontend/.env` 文件，设置 `VITE_TUNNEL_HOST` 为你的内网穿透域名（不包含协议和端口）：

```env
# cpolar 示例
VITE_TUNNEL_HOST=52095bd8.r33.cpolar.top

# ngrok 示例
VITE_TUNNEL_HOST=abc123.ngrok.io
```

### 3. 重启开发服务器

```bash
cd frontend
npm run dev
```

### 4. 访问应用

使用内网穿透提供的 HTTPS 地址访问应用：
```
https://52095bd8.r33.cpolar.top
```

## 工作原理

配置 `VITE_TUNNEL_HOST` 后，Vite 会自动：

1. 允许来自该域名的请求（`allowedHosts`）
2. 配置 HMR（热模块替换）使用 WSS 协议
3. 设置正确的 WebSocket 端口（443）

## 本地开发

如果不需要内网穿透，保持 `VITE_TUNNEL_HOST` 为空即可：

```env
VITE_TUNNEL_HOST=
```

这样 Vite 会使用默认的本地开发配置。

## 常见问题

### Q: 切换内网穿透地址后需要做什么？

A: 只需要：
1. 更新 `.env` 文件中的 `VITE_TUNNEL_HOST`
2. 重启开发服务器

不需要修改任何代码！

### Q: 图片无法显示怎么办？

A: 确保：
1. 使用的是 HTTPS 协议访问（内网穿透通常提供 HTTPS）
2. 浏览器控制台没有安全策略错误
3. 图片已正确转换为 base64 格式

可以使用 `test-image-display.html` 测试页面进行调试：
```
https://your-tunnel-host/test-image-display.html
```

### Q: WebSocket 连接失败怎么办？

A: 检查：
1. `VITE_TUNNEL_HOST` 是否正确配置
2. 内网穿透服务是否正常运行
3. 浏览器控制台是否有 WebSocket 错误

### Q: 支持哪些内网穿透服务？

A: 理论上支持所有提供 HTTPS 的内网穿透服务，包括：
- cpolar
- ngrok
- localtunnel
- frp
- 其他类似服务

## 安全提示

⚠️ 内网穿透会将你的本地服务暴露到公网，请注意：

1. 不要在生产环境使用内网穿透
2. 不要在 `.env` 文件中提交敏感信息到 Git
3. 使用完毕后及时关闭内网穿透服务
4. 定期更换 API 密钥

## 技术细节

### Vite 配置

```typescript
// vite.config.ts
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, '.', '');
  const tunnelHost = env.VITE_TUNNEL_HOST || '';
  
  return {
    server: {
      allowedHosts: [
        '.cpolar.top',
        '.ngrok.io',
        '.localtunnel.me',
        'localhost',
      ],
      hmr: tunnelHost ? {
        protocol: 'wss',
        host: tunnelHost,
        clientPort: 443,
      } : {
        // 本地开发默认配置
      },
    },
  };
});
```

### 图片处理

为了确保图片在内网穿透环境下正常显示，我们使用 base64 编码：

```typescript
// 将图片转换为 base64
const metadata = await fileUploadService.processFile(file);
const mimeType = file.type || 'image/jpeg';
const imageBase64 = `data:${mimeType};base64,${metadata.base64}`;

// 保存到消息
const userMsg: ChatMessage = {
  imageUrl: imageBase64,
  // ...
};
```

这样图片数据直接嵌入在 HTML 中，不依赖外部 URL，在任何环境下都能正常显示。
