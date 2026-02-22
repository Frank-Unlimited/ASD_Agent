# ASD 地板时光干预辅助系统

基于 LangGraph 的多 Agent 协同干预系统，使用 Graphiti 记忆网络实现时序知识图谱。

## 目录

- [系统架构](#系统架构)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [部署指南](#部署指南)
- [开发指南](#开发指南)
- [测试](#测试)

---

## 系统架构

### 技术栈

- **后端框架**: FastAPI + LangGraph
- **记忆网络**: Graphiti (时序知识图谱)
- **图数据库**: Neo4j
- **LLM**: Qwen (通义千问) / DeepSeek / OpenAI
- **数据库**: SQLite
- **前端**: HTML + JavaScript

### 核心模块

```
services/
├── Graphiti/          # Graphiti 记忆网络服务
├── SQLite/            # SQLite 数据管理
├── mock/              # Mock 服务（开发测试）
└── real/              # 真实服务实现

src/
├── langgraph/         # LangGraph 工作流
├── api/               # FastAPI 路由
├── interfaces/        # 服务接口定义
└── models/            # 数据模型
```

---

## 快速开始

### 前置要求

- Python 3.11+
- Docker (用于 Neo4j)
- Conda (推荐)

### 1. 克隆项目

```bash
git clone https://github.com/Frank-Unlimited/ASD_Agent.git
cd ASD_Agent
```

### 2. 创建 Conda 环境

```bash
conda create -n asd_agent python=3.11
conda activate asd_agent
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制 `.env.example` 到 `.env` 并配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件：

```bash
# AI 服务配置
AI_PROVIDER=qwen
QWEN_API_KEY=your_qwen_api_key_here

# Neo4j 配置（Graphiti 使用）
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 服务开关
USE_REAL_GRAPHITI=true
```

### 5. 启动 Neo4j (Graphiti 依赖)

```bash
# 使用 Docker 启动 Neo4j
docker run -d \
  --name neo4j-graphiti \
  -p 7688:7687 \
  -p 7475:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

等待 Neo4j 启动（约 30 秒），然后初始化索引：

```bash
python scripts/init_graphiti_neo4j.py
```

### 6. 启动后端

```bash
# 方式 1: 直接运行（推荐）
python src/main.py

# 方式 2: 使用模块方式
python -m src.main
```

后端将在 `http://localhost:7860` 启动。

**注意**: 如果看到 "LLM 服务注册失败" 的警告，这是正常的。只要看到 `Uvicorn running on http://0.0.0.0:7860` 就说明启动成功。

### 7. 验证部署

访问以下端点：

- **健康检查**: http://localhost:7860/
- **API 文档**: http://localhost:7860/docs
- **测试工作流**: POST http://localhost:7860/test/workflow

---

## 环境配置

### 必需配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `AI_PROVIDER` | LLM 提供商 | `qwen` / `deepseek` / `openai` |
| `QWEN_API_KEY` | 通义千问 API Key | `sk-xxx` |
| `NEO4J_URI` | Neo4j 连接地址 | `bolt://localhost:7688` |
| `NEO4J_USER` | Neo4j 用户名 | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j 密码 | `password` |

### 可选配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `USE_REAL_GRAPHITI` | 启用真实 Graphiti 服务 | `false` |
| `USE_REAL_SQLITE` | 启用真实 SQLite 服务 | `false` |
| `PORT` | 后端端口 | `7860` |

### LLM 提供商配置

#### Qwen (通义千问) - 推荐

```bash
AI_PROVIDER=qwen
QWEN_API_KEY=sk-xxx
QWEN_MODEL=qwen-plus
QWEN_BASE_URL=https://dashscope.aliyuncs.com
```

**优势**: 
- ✅ 支持 `json_schema` 结构化输出
- ✅ 与 Graphiti 完全兼容
- ✅ 性价比高

#### DeepSeek

```bash
AI_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxx
DEEPSEEK_MODEL=deepseek-chat
```

**注意**: ⚠️ DeepSeek 不支持 `json_schema`，无法与 Graphiti 配合使用

#### OpenAI

```bash
AI_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

---

## 部署指南

### Graphiti 记忆网络部署

Graphiti 是本系统的核心组件，用于构建时序知识图谱。

#### 1. 启动 Neo4j

**使用 Docker (推荐)**:

```bash
# 启动 Neo4j 容器
docker run -d \
  --name neo4j-graphiti \
  -p 7688:7687 \
  -p 7475:7474 \
  -e NEO4J_AUTH=neo4j/password \
  -v neo4j_data:/data \
  neo4j:latest

# 查看日志
docker logs -f neo4j-graphiti

# 等待启动完成（看到 "Started" 消息）
```

**使用本地安装**:

```bash
# 下载 Neo4j Community Edition
# https://neo4j.com/download/

# 启动 Neo4j
neo4j start

# 修改端口（如果需要）
# 编辑 neo4j.conf:
# server.bolt.listen_address=:7688
```

#### 2. 验证 Neo4j 连接

```bash
# 使用 cypher-shell 测试
docker exec -it neo4j-graphiti cypher-shell -u neo4j -p password

# 或访问 Web 界面
# http://localhost:7475
```

#### 3. 初始化 Graphiti 索引

```bash
# 运行初始化脚本
python scripts/init_graphiti_neo4j.py
```

**预期输出**:

```
[Graphiti Init] 连接到 Neo4j: bolt://localhost:7688
[Graphiti Init] 开始创建索引和约束...
✓ 索引和约束创建完成
[Graphiti Init] 初始化完成！
```

#### 4. 测试 Graphiti 服务

```bash
# 运行示例
python examples/test_graphiti_usage.py
```

**预期输出**:

```
✓ 成功保存 3 条记忆
✓ 找到 6 条最近记忆
✓ 上下文构建完成
```

### 常见问题

#### Neo4j 连接失败

```bash
# 检查 Neo4j 是否运行
docker ps | grep neo4j

# 检查端口是否正确
netstat -an | grep 7688

# 查看 Neo4j 日志
docker logs neo4j-graphiti
```

#### Graphiti 初始化失败

```bash
# 确保 Neo4j 已完全启动（等待 30 秒）
sleep 30

# 重新运行初始化
python scripts/init_graphiti_neo4j.py
```

#### LLM API 调用失败

```bash
# 检查 API Key 是否配置
cat .env | grep API_KEY

# 测试 LLM 服务
python tests/test_llm_service.py
```

---

## 开发指南

### 项目结构

```
ASD_Agent/
├── services/              # 服务层
│   ├── Graphiti/         # Graphiti 记忆网络
│   │   ├── service.py    # 核心服务
│   │   ├── adapters.py   # 接口适配器
│   │   └── api_interface.py  # API 函数
│   ├── SQLite/           # SQLite 数据管理
│   ├── mock/             # Mock 服务
│   └── real/             # 真实服务
├── src/
│   ├── langgraph/        # LangGraph 工作流
│   ├── api/              # FastAPI 路由
│   ├── interfaces/       # 服务接口
│   ├── models/           # 数据模型
│   └── main.py           # 应用入口
├── tests/                # 测试文件
├── scripts/              # 工具脚本
└── examples/             # 示例代码
```

### 使用 Graphiti 服务

#### 方式 1: 通过容器（推荐）

```python
from src.container import container, init_services

# 初始化服务
init_services()

# 获取 Graphiti 服务
graphiti = container.get('graphiti')

# 保存记忆
await graphiti.save_memories(child_id="child-001", memories=[
    {
        "timestamp": "2026-01-27T10:00:00",
        "type": "observation",
        "content": "孩子主动与妈妈进行眼神接触",
        "metadata": {"dimension": "eye_contact"}
    }
])

# 构建上下文
context = await graphiti.build_context(child_id="child-001")
```

#### 方式 2: 直接使用

```python
from services.Memory import get_memory_service

memory = await get_memory_service()
await memory.record_behavior(child_id, raw_input, input_type)
```

### 添加新服务

1. 在 `src/interfaces/` 定义接口
2. 在 `services/mock/` 创建 Mock 实现
3. 在 `services/real/` 创建真实实现
4. 在 `src/container.py` 注册服务

---

## 测试

### 运行所有测试

```bash
pytest tests/ -v
```

### 测试 Graphiti 服务

```bash
# 单元测试
pytest tests/test_graphiti_service.py -v

# 集成测试
pytest tests/test_integration_workflow.py -v

# 示例测试
python examples/test_graphiti_usage.py
```

### 测试 LLM 服务

```bash
pytest tests/test_llm_service.py -v
```

### 测试工作流

```bash
# 通过 API 测试
curl -X POST http://localhost:7860/test/workflow
```

---

## 生产部署

### 使用 Docker Compose

```yaml
version: '3.8'

services:
  neo4j:
    image: neo4j:latest
    ports:
      - "7688:7687"
      - "7475:7474"
    environment:
      - NEO4J_AUTH=neo4j/password
    volumes:
      - neo4j_data:/data

  backend:
    build: .
    ports:
      - "7860:7860"
    environment:
      - AI_PROVIDER=qwen
      - QWEN_API_KEY=${QWEN_API_KEY}
      - NEO4J_URI=bolt://neo4j:7687
      - USE_REAL_GRAPHITI=true
    depends_on:
      - neo4j

volumes:
  neo4j_data:
```

启动：

```bash
docker-compose up -d
```

---

## 许可证

MIT License

---

## 联系方式

- GitHub: https://github.com/Frank-Unlimited/ASD_Agent
- Issues: https://github.com/Frank-Unlimited/ASD_Agent/issues
