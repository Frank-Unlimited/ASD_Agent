# Google Custom Search API 配置指南

## 为什么需要配置？

系统默认使用 LLM 的 `enable_search` 功能进行联网搜索，但配置 Google Custom Search API 可以获得更准确的搜索结果。

## 配置步骤

### 1. 创建 Google Cloud 项目

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建新项目或选择现有项目

### 2. 启用 Custom Search API

1. 访问 [Custom Search API 页面](https://console.developers.google.com/apis/api/customsearch.googleapis.com/overview)
2. 点击"启用"按钮
3. 等待几分钟让 API 生效

### 3. 创建 API Key

1. 访问 [API 凭据页面](https://console.cloud.google.com/apis/credentials)
2. 点击"创建凭据" → "API 密钥"
3. 复制生成的 API Key
4. （可选）限制 API Key 只能访问 Custom Search API

### 4. 创建 Programmable Search Engine

1. 访问 [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. 点击"添加"创建新的搜索引擎
3. 配置搜索范围：
   - 搜索整个网络：选择"搜索整个网络"
   - 或指定特定网站（如自闭症相关网站）
4. 创建后，在"概览"页面找到"搜索引擎 ID"（cx 参数）

### 5. 配置环境变量

在 `ASD_Agent/frontend/.env` 文件中添加：

```env
# Google Custom Search API 配置
VITE_GOOGLE_SEARCH_API_KEY=你的API密钥
VITE_GOOGLE_SEARCH_ENGINE_ID=你的搜索引擎ID
```

### 6. 重启开发服务器

```bash
npm run dev
```

## 免费额度

- 每天 100 次免费查询
- 超出后需要付费（$5/1000次查询）

## 降级方案

如果不配置 Google Search API，系统会自动使用 LLM 的 `enable_search` 功能作为降级方案，功能仍然可用。

## 验证配置

配置完成后，在控制台查看日志：
- ✅ 成功：`✅ Google Search 返回 X 个结果`
- ❌ 失败：`⚠️ Google Search 未配置或无结果，尝试使用 LLM 联网搜索`

## 常见问题

### Q: 403 Forbidden 错误
A: 需要在 Google Cloud Console 中启用 Custom Search API

### Q: 401 Unauthorized 错误
A: API Key 无效或未正确配置

### Q: 每天只有 100 次查询够用吗？
A: 对于个人使用和开发测试完全够用。如果需要更多，可以考虑付费方案。

### Q: 可以不配置吗？
A: 可以，系统会自动使用 LLM 的联网搜索功能作为降级方案。
