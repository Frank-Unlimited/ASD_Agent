# ASD 地板时光干预辅助系统

基于 LangGraph 的多 Agent 协同干预系统，使用 Graphiti 记忆网络实现时序知识图谱。

## 项目结构

```
ASD_Agent/
├── frontend/          # 前端应用 (React + Vite)
│   ├── services/     # 前端服务层
│   ├── App.tsx       # 主应用组件
│   └── package.json  # 前端依赖
│
└── backend/          # 后端服务 (FastAPI + LangGraph)
    ├── src/          # 源代码
    │   ├── api/      # API 路由
    │   ├── models/   # 数据模型
    │   └── main.py   # 应用入口
    ├── services/     # 业务服务
    │   ├── Memory/   # Graphiti 记忆网络
    │   ├── Chat/     # 对话服务
    │   ├── game/     # 游戏推荐
    │   └── ...
    ├── tests/        # 测试文件
    └── requirements.txt
```

## 快速开始

### 前置要求

- Python 3.11+
- Node.js 18+
- Docker (用于 Neo4j)

### 1. 启动后端

```bash
cd backend

# 创建虚拟环境
conda create -n asd_agent python=3.11
conda activate asd_agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API Key 等

# 启动 Neo4j
docker run -d \
  --name neo4j-graphiti \
  -p 7688:7687 \
  -p 7475:7474 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# 初始化 Graphiti
python scripts/init_graphiti_neo4j.py

# 启动后端服务
python src/main.py
```

后端将在 `http://localhost:7860` 启动。

#### 启动 AI 视频通话服务（可选）

如果需要使用 AI 视频通话功能，需要额外启动 Qwen-Omni-Realtime WebSocket 服务器：

```bash
cd backend

# 确保已安装视频通话依赖
pip install dashscope websockets pyaudio

# 配置阿里云 API Key（如果还没配置）
# 在 .env 文件中添加：
# DASHSCOPE_API_KEY=your-dashscope-api-key

# 启动视频通话服务器（在新的终端窗口）
python qwen_realtime_websocket.py
```

视频通话服务器将在 `ws://localhost:8766` 启动。

**功能说明**：
- 🎥 实时视频通话：AI 可以看到并理解视频画面
- 🎤 语音交互：支持实时语音识别和 AI 语音回复
- 🧠 行为观察：AI 实时观察儿童行为并提供干预建议
- 📱 最小化模式：可缩小到右下角，不影响其他功能使用

**注意事项**：
- 需要摄像头和麦克风权限
- 使用阿里云 Qwen-Omni-Turbo-Realtime 模型
- 视频帧每 2 秒发送 1 帧
- 详细调试信息见 `frontend/QWEN_REALTIME_DEBUG.md`

### 2. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API Key

# 启动开发服务器
npm run dev
```

前端将在 `http://localhost:3000` 启动。

## 详细文档

- [后端文档](./backend/README.md) - 后端架构、API 文档、部署指南
- [前端文档](./frontend/README.md) - 前端架构、组件说明、开发指南

## 核心功能

- 🧠 **智能对话**: 基于 LangGraph 的多 Agent 对话系统
- 📊 **行为分析**: 自动识别和分析儿童行为模式
- 🎮 **游戏推荐**: 基于兴趣维度的个性化游戏推荐
- 📈 **发展评估**: DIR/Floortime 六大能力维度评估
- 🔗 **记忆网络**: Graphiti 时序知识图谱，长期记忆管理
- 🎤 **语音交互**: 阿里云语音识别和合成
- 📷 **多模态理解**: 图片和视频分析
- 🎥 **AI 视频通话**: 实时视频观察和语音交互（基于 Qwen-Omni-Realtime）

## 技术栈

### 前端
- React 18
- TypeScript
- Vite
- Recharts (数据可视化)
- Lucide Icons

### 后端
- FastAPI
- LangGraph
- Graphiti (时序知识图谱)
- Neo4j (图数据库)
- SQLite (关系数据库)
- Qwen / DeepSeek / OpenAI (LLM)

## 开发指南

### 前端开发

```bash
cd frontend
npm run dev      # 启动开发服务器
npm run build    # 构建生产版本
npm run preview  # 预览生产版本
```

### 后端开发

```bash
cd backend
python src/main.py           # 启动后端
pytest tests/ -v             # 运行测试
python scripts/init_graphiti_neo4j.py  # 初始化数据库
```

## 环境变量配置

### 后端 (.env)

```bash
# LLM 配置
LLM_API_KEY=your-api-key
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-plus

# DashScope API Key (用于视频通话)
DASHSCOPE_API_KEY=your-dashscope-api-key

# Neo4j 配置
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# 服务开关
USE_REAL_GRAPHITI=true
USE_REAL_SQLITE=true
```

### 前端 (.env)

```bash
# DashScope API
VITE_DASHSCOPE_API_KEY=your-api-key
VITE_DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# 阿里云语音服务
VITE_ALIYUN_NLS_APPKEY=your-appkey
VITE_ALIYUN_NLS_TOKEN=your-token

# Gemini API
GEMINI_API_KEY=your-gemini-api-key
```

## 许可证

MIT License

## 联系方式

- GitHub: https://github.com/Frank-Unlimited/ASD_Agent
- Issues: https://github.com/Frank-Unlimited/ASD_Agent/issues
