# API Keys 配置指南

本文档说明如何配置 GraphRAG 项目中使用的各种 API Keys。

---

## 📋 需要的 API Keys

### 1. **LLM API Key**（必需）
用于文本生成、实体提取、关系提取等核心功能。

**提供商**: DeepSeek  
**用途**: 
- 图谱提取
- 实体描述摘要
- 社区报告生成
- 查询响应生成

**配置位置**: `data/.env`
```env
GRAPHRAG_API_BASE=https://api.deepseek.com
GRAPHRAG_API_KEY=sk-你的DeepSeek密钥
GRAPHRAG_MODEL_NAME=deepseek-chat
```

**获取方式**: https://platform.deepseek.com/

---

### 2. **Embedding API Key**（必需）
用于文本向量化、语义检索。

**提供商**: OpenAI  
**用途**:
- 文本向量化
- 实体向量化
- 语义相似度计算

**配置位置**: `data/.env`
```env
Embedding_API_BASE=https://ai.devtool.tech/proxy/v1
Embedding_API_KEY=sk-proj-你的OpenAI密钥
Embedding_MODEL_NAME=text-embedding-3-small
```

**支持的模型**:
- `text-embedding-3-small` - 性价比高（推荐）
- `text-embedding-3-large` - 更高精度
- `text-embedding-ada-002` - 旧版模型

**获取方式**: https://platform.openai.com/api-keys

---

### 3. **视觉模型 API Key**（PDF 处理时需要）
用于为 PDF 中提取的图片生成描述。

**提供商**: OpenAI  
**用途**:
- 图片内容识别
- 图片描述生成
- 图表理解

**配置位置**: `data/.env`
```env
IMAGE_DESCRIPTION_API_KEY=sk-proj-你的OpenAI密钥
IMAGE_DESCRIPTION_MODEL=gpt-4o
IMAGE_DESCRIPTION_BASE_URL=https://ai.devtool.tech/proxy/v1
```

**支持的模型**:
- `gpt-4o` - 最新多模态模型（推荐）
- `gpt-4-vision-preview` - GPT-4 视觉版
- `gpt-4-turbo` - GPT-4 Turbo（支持视觉）

**获取方式**: https://platform.openai.com/api-keys

---

### 4. **表格描述 API Key**（PDF 处理时需要）
用于为 PDF 中提取的表格生成描述。

**提供商**: DeepSeek  
**用途**:
- 表格内容摘要
- 表格数据理解

**配置位置**: `data/.env`
```env
TABLE_DESCRIPTION_API_KEY=sk-你的DeepSeek密钥
TABLE_DESCRIPTION_MODEL=deepseek-chat
TABLE_DESCRIPTION_BASE_URL=https://api.deepseek.com
```

**获取方式**: https://platform.deepseek.com/

---

## 🔧 配置方法

### 方法 1: 使用环境变量（推荐）

1. **编辑 `data/.env` 文件**:
```env
# LLM API
GRAPHRAG_API_KEY=sk-你的密钥

# Embedding API
Embedding_API_KEY=sk-proj-你的密钥

# 视觉模型 API
IMAGE_DESCRIPTION_API_KEY=sk-proj-你的密钥

# 表格描述 API
TABLE_DESCRIPTION_API_KEY=sk-你的密钥
```

2. **在配置文件中引用**（`data/settings.yaml` 或 `data/settings_pdf.yaml`）:
```yaml
models:
  default_chat_model:
    api_key: ${GRAPHRAG_API_KEY}
  
  default_embedding_model:
    api_key: ${Embedding_API_KEY}

input:
  image_description_api_key: ${IMAGE_DESCRIPTION_API_KEY}
  table_description_api_key: ${TABLE_DESCRIPTION_API_KEY}
```

### 方法 2: 直接在配置文件中设置

**不推荐**：API Key 会暴露在配置文件中

编辑 `data/settings_pdf.yaml`:
```yaml
input:
  image_description_api_key: "sk-proj-你的密钥"
  table_description_api_key: "sk-你的密钥"
```

---

## 📁 配置文件说明

### `data/.env`
存储敏感信息（API Keys），不应提交到 Git。

**示例**:
```env
GRAPHRAG_API_KEY=sk-xxx
Embedding_API_KEY=sk-proj-xxx
IMAGE_DESCRIPTION_API_KEY=sk-proj-xxx
TABLE_DESCRIPTION_API_KEY=sk-xxx
```

### `data/settings.yaml`
主配置文件，用于文本数据处理。

**关键配置**:
```yaml
models:
  default_chat_model:
    api_key: ${GRAPHRAG_API_KEY}
    model: ${GRAPHRAG_MODEL_NAME}
  
  default_embedding_model:
    api_key: ${Embedding_API_KEY}
    model: ${Embedding_MODEL_NAME}
```

### `data/settings_pdf.yaml`
PDF 处理专用配置。

**关键配置**:
```yaml
input:
  file_type: pdf
  
  # 视觉模型配置
  image_description_api_key: ${IMAGE_DESCRIPTION_API_KEY}
  image_description_model: ${IMAGE_DESCRIPTION_MODEL}
  image_description_base_url: ${IMAGE_DESCRIPTION_BASE_URL}
  
  # 表格描述配置
  table_description_api_key: ${TABLE_DESCRIPTION_API_KEY}
  table_description_model: ${TABLE_DESCRIPTION_MODEL}
  base_url: ${TABLE_DESCRIPTION_BASE_URL}
```

---

## 🔐 安全建议

### 1. **不要提交 API Keys 到 Git**

确保 `.env` 文件在 `.gitignore` 中：
```bash
echo "data/.env" >> .gitignore
```

### 2. **使用环境变量**

生产环境中使用系统环境变量：
```bash
export GRAPHRAG_API_KEY="sk-xxx"
export IMAGE_DESCRIPTION_API_KEY="sk-proj-xxx"
```

### 3. **定期轮换密钥**

定期更新 API Keys，特别是在：
- 密钥可能泄露时
- 团队成员变动时
- 定期安全审计时

### 4. **限制 API Key 权限**

在 API 提供商的控制台中：
- 设置使用限额
- 限制 IP 地址
- 启用使用监控

---

## 💰 成本估算

### 文本处理（必需）

**LLM API (DeepSeek)**:
- 价格: ~¥0.001/1K tokens
- 用途: 实体提取、关系提取、摘要生成
- 估算: 1000 个文档约 ¥10-50

**Embedding API (OpenAI)**:
- 价格: $0.00002/1K tokens (text-embedding-3-small)
- 用途: 文本向量化
- 估算: 1000 个文档约 $0.5-2

### PDF 处理（可选）

**视觉模型 (GPT-4o)**:
- 价格: $0.005/image
- 用途: 图片描述生成
- 估算: 100 张图片约 $0.5

**表格描述 (DeepSeek)**:
- 价格: ~¥0.001/1K tokens
- 用途: 表格摘要
- 估算: 100 个表格约 ¥1-5

---

## 🧪 测试配置

### 测试 API Key 是否有效

```bash
# 测试 LLM API
curl https://api.deepseek.com/v1/chat/completions \
  -H "Authorization: Bearer $GRAPHRAG_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'

# 测试 Embedding API
curl https://api.openai.com/v1/embeddings \
  -H "Authorization: Bearer $Embedding_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"text-embedding-3-small","input":"Hello"}'

# 测试视觉模型 API
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $IMAGE_DESCRIPTION_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4o","messages":[{"role":"user","content":"Hello"}]}'
```

---

## 🆘 常见问题

### Q1: API Key 无效

**错误**: `Authentication failed` 或 `Invalid API key`

**解决**:
1. 检查 API Key 是否正确复制
2. 确认 API Key 没有过期
3. 检查 API 提供商账户余额
4. 确认 API Key 有相应权限

### Q2: 配置未生效

**错误**: 仍然使用旧的 API Key

**解决**:
1. 重启服务
2. 检查环境变量是否正确设置
3. 确认配置文件语法正确
4. 检查是否使用了正确的配置文件

### Q3: 成本过高

**解决**:
1. 使用更便宜的模型（如 DeepSeek）
2. 减少 `max_gleanings` 参数
3. 增大文本分块大小
4. 禁用可选功能（如图片描述）

### Q4: 速率限制

**错误**: `Rate limit exceeded`

**解决**:
1. 降低 `concurrent_requests` 参数
2. 增加 `retry_delay`
3. 升级 API 套餐
4. 使用多个 API Key 轮换

---

## 📞 获取帮助

- **DeepSeek 文档**: https://platform.deepseek.com/docs
- **OpenAI 文档**: https://platform.openai.com/docs
- **GraphRAG 文档**: https://microsoft.github.io/graphrag

---

**最后更新**: 2025-01-04
