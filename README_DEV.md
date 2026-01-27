# ASD 地板时光干预辅助系统 - 开发文档

## 项目结构

```
.
├── src/
│   ├── interfaces/          # 所有模块接口定义（17个模块）
│   ├── langgraph/          # LangGraph 工作流编排
│   ├── models/             # 数据模型（State、数据库模型）
│   ├── api/                # API 路由
│   ├── container.py        # 依赖注入容器
│   ├── config.py           # 配置管理
│   └── main.py             # FastAPI 应用入口
├── services/
│   ├── mock/               # Mock 实现（用于快速验证）
│   ├── real/               # 真实实现（逐步替换）
│   └── GraphRag/           # GraphRAG 相关服务
├── docs/                   # 设计文档
├── tests/                  # 测试文件
├── requirements.txt        # Python 依赖
├── .env.example           # 环境变量示例
└── README.md              # 项目说明

```

## 开发流程（接口先行）

### 第1周：接口定义 + 全 Mock + 框架搭建

**目标**：跑通完整流程（全 Mock 数据）

**任务**：
1. 定义所有 17 个模块的接口（`src/interfaces/`）
2. 实现所有模块的 Mock 版本（`services/mock/`）
3. 搭建 LangGraph 基础框架（`src/langgraph/`）
4. 实现依赖注入容器（`src/container.py`）
5. 实现核心节点（调用接口）
6. 跑通完整 7 步闭环（全 Mock 数据）

### 第2-4周：替换核心模块

**目标**：核心功能可用

**优先替换**：
- ✅ 模块1: SQLite 真实实现
- ✅ 模块6: 文档解析真实实现
- ✅ 模块3: RAG 真实实现（至少游戏库）
- ✅ 模块7: 初始评估真实实现

### 第5-8周：替换重要模块

**目标**：游戏流程可用

**优先替换**：
- ✅ 模块5: 语音处理真实实现
- ✅ 模块8: 周计划推荐真实实现
- ✅ 模块9: 实时指引真实实现
- ✅ 模块10: 观察捕获真实实现
- ✅ 模块12: 总结生成真实实现

### 第9-12周：替换完善模块

**目标**：完整闭环

**优先替换**：
- ✅ 模块2: Graphiti 真实实现
- ✅ 模块13: 记忆更新真实实现
- ✅ 模块14: 再评估真实实现

### 第13-16周：替换锦上添花模块

**目标**：全功能

**优先替换**：
- ✅ 模块4: 视频分析真实实现
- ✅ 模块11: 视频验证真实实现
- ✅ 模块15: 对话助手真实实现
- ✅ 模块16: 可视化报告真实实现

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，填入必要的配置
```

### 3. 运行开发服务器

```bash
# 开发模式（自动重载）
python -m src.main

# 或使用 uvicorn
uvicorn src.main:app --reload --port 7860
```

### 4. 访问 API 文档

打开浏览器访问：
- Swagger UI: http://localhost:7860/docs
- ReDoc: http://localhost:7860/redoc

## 配置切换 Mock/Real

通过环境变量控制使用 Mock 还是真实实现：

```bash
# 全部使用 Mock（第1周）
USE_REAL_SQLITE=false
USE_REAL_GRAPHITI=false
USE_REAL_RAG=false
# ... 其他都是 false

# 使用真实 SQLite 和 RAG（第2-4周）
USE_REAL_SQLITE=true
USE_REAL_RAG=true

# 逐步增加真实模块（第5-16周）
USE_REAL_SQLITE=true
USE_REAL_RAG=true
USE_REAL_SPEECH=true
# ...
```

## 17 个模块列表

### 第一层：基础设施层（6个模块）

1. **模块1**: SQLite 数据管理模块
2. **模块2**: Graphiti 记忆网络模块
3. **模块3**: 知识库与 RAG 模块
4. **模块4**: AI 视频解析模块
5. **模块5**: 语音处理模块
6. **模块6**: 文档解析模块

### 第二层：业务逻辑层（10个模块）

7. **模块7**: 初始评估模块
8. **模块8**: 周计划推荐模块
9. **模块9**: 实时指引模块
10. **模块10**: 观察捕获模块
11. **模块11**: 视频分析与验证模块
12. **模块12**: 总结生成模块
13. **模块13**: 记忆更新模块
14. **模块14**: 再评估模块
15. **模块15**: 对话助手模块
16. **模块16**: 可视化与报告模块

### 第三层：LangGraph 工作流层（1个模块）

17. **模块17**: LangGraph 主工作流

## 开发原则

1. **接口先行**：先定义接口，再实现
2. **Mock 驱动**：用 Mock 快速验证架构
3. **渐进式替换**：一个个替换真实实现
4. **持续集成**：每替换一个模块就测试
5. **灵活配置**：通过环境变量控制 Mock/Real

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_services.py

# 查看测试覆盖率
pytest --cov=src tests/
```

## 代码规范

```bash
# 格式化代码
black src/

# 检查代码风格
flake8 src/

# 类型检查
mypy src/
```

## 参考文档

详细设计文档请查看 `docs/plans/` 目录：
- `ASD地板时光干预辅助系统-完整设计文档.md`
- `2026-01-26-MVP功能模块与技术架构设计.md`
- `模块化架构与开发顺序设计.md`
