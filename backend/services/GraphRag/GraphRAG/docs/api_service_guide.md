# GraphRAG API 服务使用指南

## 📋 项目路径配置

所有路径已更新为 Mac 系统路径：`/Users/fengguihuan/Desktop/HHC/graphrag`

已修改的文件：
- ✅ `dev/graphrag_api.py` - API 服务主文件
- ✅ `dev/graphrag_indexing.py` - 索引构建脚本
- ✅ `dev/graphrag_query.py` - 查询脚本
- ✅ `dev/graphrag_prompt_tune.py` - Prompt 调优脚本
- ✅ `data/settings.yaml` - 配置文件（路径分隔符从 `\` 改为 `/`）

---

## 🚀 快速开始

### 1. 安装依赖

由于没有安装 Poetry，使用 pip 安装：

```bash
# 激活 conda 环境
conda activate hhc_base

# 安装 GraphRAG
pip install -e .

# 或者安装特定依赖
pip install fastapi uvicorn aiofiles pydantic python-dotenv pyyaml
```

### 2. 配置环境变量

编辑 `data/.env` 文件，确保 API 密钥正确：

```env
GRAPHRAG_API_BASE=https://api.deepseek.com
GRAPHRAG_API_KEY=你的DeepSeek密钥
GRAPHRAG_MODEL_NAME=deepseek-chat

Embedding_API_BASE=https://ai.devtool.tech/proxy/v1
Embedding_API_KEY=你的Embedding密钥
Embedding_MODEL_NAME=text-embedding-3-small
```

### 3. 构建索引（如果还没有）

```bash
cd data
python -m graphrag index --root .
```

或使用开发脚本：
```bash
cd dev
python graphrag_indexing.py
```

### 4. 启动 API 服务

```bash
cd dev
python graphrag_api.py
```

服务将在 `http://localhost:8000` 启动。

---

## 📡 API 接口说明

### 健康检查
```bash
GET http://localhost:8000/api/health
```

响应：
```json
{
  "status": "ok",
  "version": "1.0.0"
}
```

### 查询接口（POST）
```bash
POST http://localhost:8000/api/query
Content-Type: application/json

{
  "query": "什么是人工智能？",
  "query_type": "local",
  "response_type": "text",
  "community_level": 1,
  "dynamic_community_selection": false
}
```

**参数说明：**
- `query`: 查询文本（必填）
- `query_type`: 查询类型，可选 `local`、`global`、`drift`、`basic`（默认 `local`）
- `response_type`: 响应类型，可选 `text`、`json`（默认 `text`）
- `community_level`: 社区级别，整数（默认 1）
- `dynamic_community_selection`: 是否使用动态社区选择（默认 false）

### 查询接口（GET）
```bash
GET http://localhost:8000/api/query?query=什么是人工智能&query_type=local
```

### 流式查询接口
```bash
POST http://localhost:8000/api/query_stream
Content-Type: application/json

{
  "query": "介绍一下量子计算",
  "query_type": "global"
}
```

---

## 🌐 Web 界面

服务提供了 3 个 Web 测试界面：

1. **主界面**: `http://localhost:8000/` → 重定向到 `/static/index.html`
2. **简单界面**: `http://localhost:8000/simple` → 重定向到 `/static/simple.html`
3. **流式界面**: `http://localhost:8000/stream` → 重定向到 `/static/stream.html`
4. **API 文档**: `http://localhost:8000/docs` - Swagger UI 交互式文档
5. **ReDoc**: `http://localhost:8000/redoc` - ReDoc 风格文档

---

## 🔧 使用示例

### 使用 curl 测试

```bash
# 本地搜索
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是GraphRAG？",
    "query_type": "local"
  }'

# 全局搜索
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "总结一下主要的技术趋势",
    "query_type": "global",
    "community_level": 2
  }'

# 流式查询
curl -X POST http://localhost:8000/api/query_stream \
  -H "Content-Type: application/json" \
  -d '{
    "query": "介绍量子计算",
    "query_type": "local"
  }'
```

### 使用 Python 调用

```python
import requests

# 查询
response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "query": "人工智能的应用领域有哪些？",
        "query_type": "local",
        "response_type": "text"
    }
)

result = response.json()
print(result["response"])
```

### 使用 JavaScript 调用

```javascript
fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: '什么是知识图谱？',
    query_type: 'local'
  })
})
.then(response => response.json())
.then(data => console.log(data.response));
```

---

## 🔍 查询类型说明

### 1. Local Search（本地搜索）
- **适用场景**: 需要精确查找特定实体和关系的问题
- **特点**: 基于实体、关系和文本单元的精确检索
- **示例**: "某公司的CEO是谁？"、"A和B之间有什么关系？"

### 2. Global Search（全局搜索）
- **适用场景**: 需要宏观理解和总结的问题
- **特点**: 基于社区报告的高层次摘要
- **示例**: "总结主要的技术趋势"、"整体市场格局如何？"

### 3. Drift Search（漂移搜索）
- **适用场景**: 需要结合精确和宏观信息的复杂问题
- **特点**: 混合本地和全局搜索的优势
- **示例**: "某技术的发展历程和未来趋势"

### 4. Basic Search（基础搜索）
- **适用场景**: 简单的文本检索
- **特点**: 基于文本单元的基础检索
- **示例**: "文档中提到了哪些技术？"

---

## 🐛 常见问题

### 1. 找不到索引数据
**错误**: `FileNotFoundError: entities.parquet not found`

**解决**: 先运行索引构建
```bash
cd data
python -m graphrag index --root .
```

### 2. API 密钥错误
**错误**: `Authentication failed`

**解决**: 检查 `data/.env` 文件中的 API 密钥是否正确

### 3. 端口被占用
**错误**: `Address already in use`

**解决**: 修改 `dev/graphrag_api.py` 中的端口号
```python
port = 8001  # 改为其他端口
```

### 4. 导入错误
**错误**: `ModuleNotFoundError: No module named 'utils'`

**解决**: 确保在 `dev` 目录下运行脚本
```bash
cd dev
python graphrag_api.py
```

### 5. 内存不足
**错误**: `MemoryError` 或服务崩溃

**解决**: 
- 减少 `concurrent_requests` 配置
- 使用更小的 `community_level`
- 考虑增加系统内存

---

## 📊 数据流程图

```
输入数据 (input/)
    ↓
索引构建 (graphrag index)
    ↓
结构化数据 (output/)
    ├── entities.parquet
    ├── relationships.parquet
    ├── communities.parquet
    └── community_reports.parquet
    ↓
API 服务加载数据
    ↓
用户查询 → 查询引擎 → 返回结果
```

---

## 🎯 生产部署建议

### 1. 使用 Gunicorn + Uvicorn

```bash
# 安装 gunicorn
pip install gunicorn

# 启动服务（4个工作进程）
cd dev
gunicorn graphrag_api:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

### 2. 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;
    }
}
```

### 3. 使用 Docker 部署

创建 `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

COPY . .

EXPOSE 8000

CMD ["python", "dev/graphrag_api.py"]
```

### 4. 添加 API 认证

在 `dev/graphrag_api.py` 中添加：
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

API_KEY = "your-secret-api-key"
api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# 在路由中使用
@app.post("/api/query", dependencies=[Depends(verify_api_key)])
async def query(request: QueryRequest):
    ...
```

### 5. 添加限流

```bash
pip install slowapi
```

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/query")
@limiter.limit("10/minute")
async def query(request: Request, query_request: QueryRequest):
    ...
```

---

## 🔐 安全建议

1. **不要提交 .env 文件到 Git**
   ```bash
   echo "data/.env" >> .gitignore
   ```

2. **使用环境变量管理敏感信息**
3. **为生产环境添加 API 认证**
4. **限制 API 请求频率**
5. **定期更新依赖包**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

6. **启用 HTTPS**
7. **配置防火墙规则**
8. **定期备份数据**

---

## 📈 性能优化

### 1. 数据预加载
API 服务启动时会自动预加载所有索引数据到内存，避免每次查询都读取文件。

### 2. 缓存策略
- LLM 调用结果会缓存在 `data/cache/` 目录
- 向量检索结果可以考虑使用 Redis 缓存

### 3. 并发控制
在 `data/settings.yaml` 中调整：
```yaml
models:
  default_chat_model:
    concurrent_requests: 25  # 根据 API 限制调整
```

### 4. 社区级别选择
- `community_level: 0` - 最详细，查询慢
- `community_level: 1` - 平衡（推荐）
- `community_level: 2+` - 更宏观，查询快

---

## 📞 获取帮助

- **官方文档**: https://microsoft.github.io/graphrag
- **GitHub Issues**: https://github.com/microsoft/graphrag/issues
- **API 文档**: http://localhost:8000/docs（启动服务后访问）
- **本地文档**: 查看 `docs/` 目录下的其他文档

---

## 📝 相关文档

- [Data 目录结构说明](./data_structure_guide.md)
- [配置文件详解](./config/yaml.md)
- [查询方法指南](./query/overview.md)
- [开发指南](./developing.md)

---

**最后更新**: 2025-01-04  
**项目路径**: `/Users/fengguihuan/Desktop/HHC/graphrag`  
**Python 环境**: `conda hhc_base`
