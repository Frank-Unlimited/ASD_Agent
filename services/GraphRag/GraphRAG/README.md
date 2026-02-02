# GraphRAG - 知识图谱增强检索系统

[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://github.com/Frank-Unlimited/GraphRAG)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

基于 Microsoft GraphRAG 的知识图谱增强检索系统，支持文本、PDF、CSV 等多种数据源，提供强大的知识图谱构建和智能检索能力。

## ✨ 主要特性

- 🚀 **多数据源支持**：支持文本、PDF、CSV 等多种格式
- 🧠 **智能知识图谱**：自动构建实体关系图谱
- 🔍 **多种检索模式**：本地搜索、全局搜索、漂移搜索
- 🐳 **Docker 部署**：开箱即用的容器化部署
- 🌐 **RESTful API**：完整的 API 接口
- 📊 **可视化支持**：集成 Neo4j 图数据库可视化

## 📋 目录

- [快速开始](#快速开始)
- [部署方式](#部署方式)
  - [方式一：Docker 镜像部署（推荐）](#方式一docker-镜像部署推荐)
  - [方式二：Docker Compose 部署](#方式二docker-compose-部署)
  - [方式三：本地开发部署](#方式三本地开发部署)
- [配置说明](#配置说明)
- [使用指南](#使用指南)
- [API 文档](#api-文档)
- [二次开发](#二次开发)
- [常见问题](#常见问题)

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- API 密钥：
  - GraphRAG LLM API Key（豆包/OpenAI）
  - Embedding API Key

### 5 分钟快速部署

```bash
# 1. 克隆项目
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥

# 3. 准备 data 目录（见下方说明）

# 4. 拉取并运行
docker pull ghcr.io/frank-unlimited/graphrag:main
docker-compose up -d

# 5. 访问服务
open http://localhost:8080
```

## 📦 部署方式

### 方式一：Docker 镜像部署（推荐）

适合生产环境和快速部署。

#### 从 GitHub Container Registry 拉取

```bash
# 1. 拉取最新镜像
docker pull ghcr.io/frank-unlimited/graphrag:main

# 2. 配置环境变量
cp .env.example .env
vim .env  # 填入必需的 API 密钥

# 3. 创建向量数据库目录（首次运行）
mkdir -p data/output/lancedb

# 4. 运行容器
docker run -d \
  --name graphrag-service \
  -p 8080:80 \
  -v $(pwd)/data/output:/app/data/output \
  --env-file .env \
  ghcr.io/frank-unlimited/graphrag:main

# 5. 查看日志
docker logs -f graphrag-service
```

#### 从阿里云镜像仓库拉取（国内推荐）

```bash
# 1. 登录阿里云
docker login --username=nick1329599640 \
  crpi-925djdtsud86yqkr.cn-hangzhou.personal.cr.aliyuncs.com

# 2. 拉取镜像
docker pull crpi-925djdtsud86yqkr.cn-hangzhou.personal.cr.aliyuncs.com/hhc510105200301150090/graphrag_for_tutorial:v1.0.0

# 3. 创建向量数据库目录
mkdir -p data/output/lancedb

# 4. 运行
docker run -d \
  --name graphrag-service \
  -p 8080:80 \
  -v $(pwd)/data/output:/app/data/output \
  --env-file .env \
  crpi-925djdtsud86yqkr.cn-hangzhou.personal.cr.aliyuncs.com/hhc510105200301150090/graphrag_for_tutorial:v1.0.0
```

### 方式二：Docker Compose 部署

适合需要自定义配置的场景。

```bash
# 1. 克隆项目
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 配置环境变量
cp .env.example .env
vim .env

# 3. 创建向量数据库目录（首次运行）
mkdir -p data/output/lancedb

# 4. 启动服务
docker-compose up -d

# 5. 查看状态
docker-compose ps
docker-compose logs -f
```

### 方式三：本地开发部署

适合开发和调试。

```bash
# 1. 克隆项目
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 安装依赖（需要 Python 3.11+）
pip install poetry
poetry install

# 3. 配置环境变量
cp .env.example data/.env
vim data/.env

# 4. 启动服务
python -m uvicorn server.graphrag_service:app --host 0.0.0.0 --port 8080
```

## ⚙️ 配置说明

### 环境变量配置

编辑 `.env` 文件，配置以下必需项：

```bash
# ========================================
# 必需配置
# ========================================

# GraphRAG 核心 LLM 配置
GRAPHRAG_API_BASE=https://ark.cn-beijing.volces.com/api/v3
GRAPHRAG_API_KEY=your-doubao-api-key-here
GRAPHRAG_MODEL_NAME=doubao-1-5-lite-32k-250115

# Embedding 模型配置
Embedding_API_BASE=https://api.openai-proxy.org/v1
Embedding_API_KEY=your-embedding-api-key-here
Embedding_MODEL_NAME=text-embedding-3-small

# ========================================
# 可选配置
# ========================================

# PDF 处理 - 图片描述（默认使用 GRAPHRAG_API_KEY）
IMAGE_DESCRIPTION_API_KEY=your-api-key-here
IMAGE_DESCRIPTION_MODEL=doubao-1-5-vision-pro-32k-250115

# PDF 处理 - 表格描述（默认使用 GRAPHRAG_API_KEY）
TABLE_DESCRIPTION_API_KEY=your-api-key-here
TABLE_DESCRIPTION_MODEL=doubao-1-5-lite-32k-250115

# MinerU PDF 解析服务（可选）
MINERU_API_URL=http://host.docker.internal:6688/

# 访问控制密钥（可选）
QUERY_ACCESS_KEY=hanhaochen
UPDATE_ACCESS_KEY=duping
```

### 数据目录准备

项目的配置文件、prompt 模板等已包含在代码仓库中，但**向量数据库文件因体积过大未上传到 GitHub**。

#### 为什么需要挂载向量数据库目录？

GraphRAG 使用 LanceDB 作为向量数据库，存储文档的向量嵌入和索引数据。这些文件通常很大（几百 MB 到几 GB），无法上传到 GitHub。因此：

- ✅ **配置文件**（settings.yaml、prompts 等）已在仓库中
- ❌ **向量数据库**（data/output/lancedb/）需要你自己生成或从其他地方获取
- 🔄 **首次运行**时，系统会自动创建空的向量数据库目录

#### 目录结构说明

```
项目根目录/
├── data/                         # 已在仓库中
│   ├── .env                      # ✅ 环境变量模板（需配置）
│   ├── settings.yaml             # ✅ GraphRAG 配置
│   ├── settings_pdf.yaml         # ✅ PDF 处理配置
│   ├── settings_csv.yaml         # ✅ CSV 处理配置
│   ├── prompts/                  # ✅ Prompt 模板目录
│   ├── prompt_turn_output/       # ✅ Prompt 调优输出
│   └── output/                   # ⚠️ 需要挂载（向量数据库）
│       ├── *.parquet             # ✅ 实体、关系等数据文件（已在仓库）
│       └── lancedb/              # ❌ 向量数据库（未在仓库，需挂载）
└── output/                       # 项目根目录的 output（仅配置文件）
    └── config.yaml
```

#### 准备方式

**方式 1：首次使用（推荐）**

如果你是第一次使用，系统会自动创建向量数据库：

```bash
# 1. 克隆项目
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 创建向量数据库目录
mkdir -p data/output/lancedb

# 3. 配置环境变量
cp .env.example .env
vim .env  # 填入你的 API 密钥

# 4. 启动服务（会自动初始化向量数据库）
docker-compose up -d
```

**方式 2：使用现有的向量数据库**

如果你有现有的向量数据库（从其他环境迁移）：

```bash
# 1. 克隆项目
git clone https://github.com/Frank-Unlimited/GraphRAG.git
cd GraphRAG

# 2. 复制现有的向量数据库
cp -r /path/to/existing/data/output/lancedb ./data/output/

# 3. 配置并启动
cp .env.example .env
vim .env
docker-compose up -d
```

**方式 3：从备份恢复**

```bash
# 如果你有向量数据库的备份
tar -xzf lancedb-backup.tar.gz -C ./data/output/
```

### Docker 命令参数说明

```bash
docker run -d \
  --name graphrag-service \      # 容器名称
  -p 8080:80 \                   # 端口映射：宿主机8080 → 容器80
  -v $(pwd)/data/output:/app/data/output \  # 挂载向量数据库目录（必需）
  --env-file .env \              # 环境变量文件
  ghcr.io/frank-unlimited/graphrag:main  # 镜像地址
```

**参数详解：**
- `-d`：后台运行
- `--name`：指定容器名称，方便管理
- `-p 8080:80`：将容器的 80 端口映射到宿主机 8080 端口
- `-v $(pwd)/data/output:/app/data/output`：**挂载向量数据库目录**
  - 向量数据库文件体积大（几百 MB 到几 GB）
  - GitHub 无法存储这些大文件
  - 必须挂载到宿主机以实现数据持久化
- `--env-file .env`：从文件加载环境变量

**为什么只挂载 data/output？**

项目的配置文件、prompt 模板等已经打包在 Docker 镜像中，只有向量数据库因为体积过大无法上传到 GitHub，需要单独挂载：

- ✅ **已在镜像中**：settings.yaml、prompts/、.env.example 等配置文件
- ❌ **需要挂载**：data/output/lancedb/ 向量数据库（体积大，未在仓库）
- 🔄 **自动创建**：首次运行时，如果目录不存在会自动创建

## 📖 使用指南

### 1. 上传文档并构建索引

```bash
# 方式 1：通过 API 上传
curl -X POST "http://localhost:8080/api/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your-document.txt" \
  -F "access_key=duping"

# 方式 2：直接放入 data/input 目录
cp your-document.txt data/input/
```

### 2. 执行索引构建

```bash
# 通过 API 触发索引构建
curl -X POST "http://localhost:8080/api/index" \
  -H "Content-Type: application/json" \
  -d '{"access_key": "duping"}'
```

### 3. 查询知识图谱

```bash
# 本地搜索
curl -X POST "http://localhost:8080/api/query/local" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "你的问题",
    "access_key": "hanhaochen"
  }'

# 全局搜索
curl -X POST "http://localhost:8080/api/query/global" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "你的问题",
    "access_key": "hanhaochen"
  }'
```

### 4. 访问 Web 界面

打开浏览器访问：
- 主页：http://localhost:8080
- API 文档：http://localhost:8080/docs
- 健康检查：http://localhost:8080/api/health

## 📚 API 文档

启动服务后，访问 http://localhost:8080/docs 查看完整的 Swagger API 文档。

### 主要 API 端点

| 端点 | 方法 | 说明 | 权限 |
|------|------|------|------|
| `/api/health` | GET | 健康检查 | 无 |
| `/api/upload` | POST | 上传文档 | UPDATE |
| `/api/index` | POST | 构建索引 | UPDATE |
| `/api/query/local` | POST | 本地搜索 | QUERY |
| `/api/query/global` | POST | 全局搜索 | QUERY |
| `/api/query/drift` | POST | 漂移搜索 | QUERY |
| `/api/nl-to-cypher` | POST | NL2Cypher 查询 | QUERY |

## 🔧 二次开发

本项目基于 Microsoft GraphRAG 进行了深度二次开发，扩展了以下功能：

### 核心功能

1. **PDF 文档支持** - 基于 MinerU 的智能 PDF 解析，支持表格和图片的 LLM 处理
2. **Neo4j 图谱可视化** - 完整的图谱导入、可视化和 NL2Cypher 查询
3. **RESTful API 服务** - 生产级 API 服务和 Nginx 反向代理
4. **多种增强功能** - 异步处理、日志系统、缓存管理等

### 详细文档

查看 [CUSTOM_DEVELOPMENT.md](CUSTOM_DEVELOPMENT.md) 了解：
- PDF 解析的技术架构和实现细节
- Neo4j 图谱导入和可视化方案
- API 服务设计和 Nginx 配置
- 作为智能体工具的集成方式
- 性能优化和开发指南

## 🛠️ 管理命令

### 使用快速启动脚本

项目提供了 `docker-run.sh` 脚本简化管理：

```bash
# 启动服务
./docker-run.sh start

# 停止服务
./docker-run.sh stop

# 重启服务
./docker-run.sh restart

# 查看日志
./docker-run.sh logs

# 查看状态
./docker-run.sh status

# 清理资源
./docker-run.sh clean
```

### Docker Compose 命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps
```

### 容器管理

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs -f graphrag-service

# 进入容器内部
docker exec -it graphrag-service bash

# 停止容器
docker stop graphrag-service

# 删除容器
docker rm graphrag-service

# 查看容器资源使用
docker stats graphrag-service
```

## ❓ 常见问题

### 1. 容器无法启动

**问题**：容器启动后立即退出

**解决方案**：
```bash
# 查看容器日志
docker logs graphrag-service

# 检查环境变量
docker exec graphrag-service env | grep API_KEY

# 确认 data 目录挂载正确
docker exec graphrag-service ls -la /app/data
```

### 2. API 密钥配置错误

**问题**：提示 API 密钥无效

**解决方案**：
- 确认 `.env` 文件中的密钥正确
- 确认 `data/.env` 文件存在（容器内会读取这个文件）
- 重启容器使配置生效

### 3. 端口被占用

**问题**：8080 端口已被占用

**解决方案**：
```bash
# 修改端口映射
docker run -p 9000:80 ...  # 使用 9000 端口

# 或修改 docker-compose.yml
ports:
  - "9000:80"
```

### 4. 数据目录权限问题

**问题**：容器无法写入数据目录

**解决方案**：
```bash
# 修改目录权限
chmod -R 755 ./data ./output

# 或使用 root 用户运行容器
docker run --user root ...
```

### 5. 缺少 prompt 文件

**问题**：查询时提示找不到 prompt 文件

**解决方案**：
- 确保 `data/prompts/` 目录包含所有必需的 prompt 文件
- 确保 `data/prompt_turn_output/` 目录存在
- 从现有环境复制完整的 prompts 目录

### 6. 内存不足

**问题**：容器运行缓慢或崩溃

**解决方案**：
```bash
# 增加 Docker 内存限制
docker run -m 8g ...  # 分配 8GB 内存

# 或在 docker-compose.yml 中配置
services:
  graphrag-service:
    mem_limit: 8g
```

## 🔧 高级配置

### 自定义配置文件

编辑 `data/settings.yaml` 自定义 GraphRAG 行为：

```yaml
# 修改 chunk 大小
chunks:
  size: 500
  overlap: 100

# 修改并发请求数
models:
  default_chat_model:
    concurrent_requests: 25
```

### 集成 Neo4j 可视化

```bash
# 启动 Neo4j 容器
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# 导入数据到 Neo4j
python server/import_to_neo4j.py
```

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📞 支持

- 📧 Email: support@example.com
- 💬 Issues: [GitHub Issues](https://github.com/Frank-Unlimited/GraphRAG/issues)
- 📖 文档: [完整文档](https://github.com/Frank-Unlimited/GraphRAG/wiki)

## 🙏 致谢

本项目基于 [Microsoft GraphRAG](https://github.com/microsoft/graphrag) 构建。

---

**快速链接**
- [CUSTOM_DEVELOPMENT.md](CUSTOM_DEVELOPMENT.md) - 二次开发详细说明
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南详解
- [RUN_DOCKER.md](RUN_DOCKER.md) - Docker 运行详细指南
- [ALIYUN_DEPLOY.md](ALIYUN_DEPLOY.md) - 阿里云部署指南
- [CONTRIBUTING.md](CONTRIBUTING.md) - 贡献指南
