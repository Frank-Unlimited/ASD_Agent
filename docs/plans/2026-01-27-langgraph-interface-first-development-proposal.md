# LangGraph 接口先行开发提案

**文档日期**: 2026-01-27
**版本**: v1.0
**目标**: 基于接口先行原则的 LangGraph 框架开发方案

---

## 目录

1. [架构决策](#1-架构决策)
2. [项目目录结构](#2-项目目录结构)
3. [State 定义](#3-state-定义)
4. [接口定义](#4-接口定义)
5. [多 Graph 架构](#5-多-graph-架构)
6. [依赖注入与服务容器](#6-依赖注入与服务容器)
7. [开发顺序与并行策略](#7-开发顺序与并行策略)

---

## 1. 架构决策

### 1.1 技术选型

| 决策项 | 选择 | 理由 |
|-------|------|------|
| 后端语言 | Python | LangGraph 原生支持，AI 生态成熟 |
| 工作流架构 | 单 Graph 顺序编排 | 2-3人团队，结构清晰，调试方便 |
| 多 Graph 设计 | 主 Graph + 辅助 Graph | 支持随时操作（查看状态、快速记录） |
| 持久化 | SQLite + Graphiti | 结构化数据 + 时序记忆 |

### 1.2 多 Graph 架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                         用户操作                             │
├──────────┬──────────┬──────────┬──────────┬─────────────────┤
│ 查看状态  │ 快速记录  │ 生成周计划 │ 开始游戏  │ 对话助手        │
└────┬─────┴────┬─────┴────┬─────┴────┬─────┴───────┬─────────┘
     │          │          │          │             │
     ▼          ▼          ▼          ▼             ▼
┌─────────┐ ┌─────────┐ ┌─────────┐ ┌───────────┐ ┌─────────┐
│ Query   │ │ Record  │ │ Plan    │ │GameSession│ │  Chat   │
│ Graph   │ │ Graph   │ │ Graph   │ │  Graph    │ │  Graph  │
│ (只读)  │ │ (写入)  │ │ (生成)  │ │(主流程)   │ │ (对话)  │
└────┬────┘ └────┬────┘ └────┬────┘ └─────┬─────┘ └────┬────┘
     │          │          │             │            │
     └──────────┴──────────┴─────────────┴────────────┘
                           │
                           ▼
                ┌─────────────────────┐
                │   共享数据层         │
                │  SQLite + Graphiti  │
                └─────────────────────┘
```

---

## 2. 项目目录结构

```
asd_agent/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 入口
│   └── config.py                  # 配置管理
│
├── graph/                         # LangGraph 框架层
│   ├── __init__.py
│   ├── state.py                   # State 定义
│   ├── workflows/                 # 多 Graph 定义
│   │   ├── __init__.py
│   │   ├── assessment_graph.py    # 初始评估
│   │   ├── plan_graph.py          # 周计划生成
│   │   ├── game_session_graph.py  # 游戏会话（主流程）
│   │   ├── record_graph.py        # 快速记录
│   │   ├── query_graph.py         # 查看状态
│   │   └── chat_graph.py          # 对话助手
│   ├── nodes/                     # 节点函数
│   │   ├── __init__.py
│   │   ├── assessment.py
│   │   ├── weekly_plan.py
│   │   ├── game_session.py
│   │   ├── observation.py
│   │   ├── video_analysis.py
│   │   ├── summary.py
│   │   ├── feedback.py
│   │   ├── memory_update.py
│   │   └── re_evaluation.py
│   └── edges.py                   # 条件边定义
│
├── interfaces/                    # 接口定义层
│   ├── __init__.py
│   ├── i_sqlite_service.py
│   ├── i_graphiti_service.py
│   ├── i_rag_service.py
│   ├── i_video_service.py
│   ├── i_speech_service.py
│   ├── i_document_parser.py
│   └── i_llm_service.py
│
├── services/                      # 服务实现层
│   ├── __init__.py
│   ├── container.py               # 依赖注入容器
│   ├── mock/                      # Mock 实现
│   │   ├── __init__.py
│   │   ├── sqlite_mock.py
│   │   ├── graphiti_mock.py
│   │   ├── rag_mock.py
│   │   ├── video_mock.py
│   │   ├── speech_mock.py
│   │   ├── document_mock.py
│   │   └── llm_mock.py
│   ├── impl/                      # 真实实现
│   │   ├── __init__.py
│   │   ├── sqlite_impl.py
│   │   ├── graphiti_impl.py
│   │   ├── rag_impl.py
│   │   ├── video_impl.py
│   │   ├── speech_impl.py
│   │   ├── document_impl.py
│   │   └── llm_impl.py
│   └── realtime/                  # 实时交互
│       ├── __init__.py
│       └── game_websocket.py
│
├── models/                        # 数据模型
│   ├── __init__.py
│   ├── child.py
│   ├── session.py
│   ├── weekly_plan.py
│   └── observation.py
│
├── prompts/                       # LLM Prompt 模板
│   ├── assessment.py
│   ├── summary.py
│   └── feedback.py
│
├── data/                          # 数据文件
│   ├── asd.db                     # SQLite 数据库
│   ├── checkpoints.db             # LangGraph Checkpoint
│   └── games.json                 # 游戏知识库（初始数据）
│
└── tests/
    ├── test_workflows/
    └── test_services/
```

---

## 3. State 定义

```python
# graph/state.py
from typing import TypedDict, Optional, List, Literal
from datetime import datetime


class ChildProfile(TypedDict):
    """孩子画像"""
    child_id: str
    name: str
    age: float
    diagnosis: str
    interests: List[str]
    milestones: dict  # 6大情绪发展里程碑评分
    custom_dimensions: dict
    strengths: List[str]
    weaknesses: List[str]
    observation_framework: List[str]


class CurrentSession(TypedDict):
    """当前游戏会话"""
    session_id: str
    game_id: str
    game_name: str
    start_time: Optional[str]
    end_time: Optional[str]
    daily_goal: str
    guidance_log: List[dict]
    observations: List[dict]
    video_path: Optional[str]
    video_analysis: Optional[dict]
    validated_observations: Optional[List[dict]]
    preliminary_summary: Optional[dict]
    feedback_form: Optional[dict]
    parent_feedback: Optional[dict]
    final_summary: Optional[dict]


class GameSessionState(TypedDict):
    """游戏会话 Graph State"""
    # 孩子数据
    child_id: str
    child_profile: Optional[ChildProfile]

    # 时序指标
    metrics: Optional[dict]

    # 当前上下文
    current_context: Optional[dict]

    # 会话历史
    session_history: Optional[List[dict]]

    # 周计划
    weekly_plan: Optional[dict]
    current_daily_plan: Optional[dict]

    # 当前会话
    current_session: Optional[CurrentSession]

    # 流程控制
    current_step: str
    wait_for_user: bool
    user_input: Optional[dict]

    # 再评估结果
    re_evaluation: Optional[dict]
    needs_adjustment: bool

    # 错误处理
    error: Optional[str]


class RecordState(TypedDict):
    """快速记录 Graph State"""
    child_id: str
    record_type: Literal["voice", "text", "quick_button"]
    content: str
    audio_path: Optional[str]
    parsed_observation: Optional[dict]
    saved: bool
    memory_updated: bool


class QueryState(TypedDict):
    """查询状态 Graph State"""
    child_id: str
    child_profile: Optional[dict]
    metrics: Optional[dict]
    recent_sessions: Optional[List[dict]]
    trends: Optional[dict]
    milestones: Optional[List[dict]]


class PlanState(TypedDict):
    """周计划 Graph State"""
    child_id: str
    week_start: str
    child_profile: Optional[dict]
    current_context: Optional[dict]
    last_week_performance: Optional[dict]
    priority_dimensions: Optional[List[str]]
    candidate_games: Optional[List[dict]]
    weekly_plan: Optional[dict]
```

---

## 4. 接口定义

### 4.1 基础设施层接口（6个）

```python
# interfaces/i_sqlite_service.py
from abc import ABC, abstractmethod
from typing import Optional, List

class ISQLiteService(ABC):
    """SQLite 数据管理接口（模块1）"""

    @abstractmethod
    async def get_child(self, child_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def save_child(self, profile: dict) -> None:
        pass

    @abstractmethod
    async def create_session(self, child_id: str, game_id: str) -> str:
        pass

    @abstractmethod
    async def get_session(self, session_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def save_session(self, session: dict) -> None:
        pass

    @abstractmethod
    async def save_observation(self, observation: dict) -> None:
        pass

    @abstractmethod
    async def get_observations(self, session_id: str) -> List[dict]:
        pass

    @abstractmethod
    async def get_weekly_plan(self, child_id: str, week_start: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def save_weekly_plan(self, plan: dict) -> str:
        pass

    @abstractmethod
    async def get_session_history(self, child_id: str, limit: int = 10) -> List[dict]:
        pass


# interfaces/i_graphiti_service.py
class IGraphitiService(ABC):
    """Graphiti 记忆网络接口（模块2）"""

    @abstractmethod
    async def save_memories(self, child_id: str, memories: List[dict]) -> None:
        pass

    @abstractmethod
    async def get_recent_memories(self, child_id: str, days: int) -> List[dict]:
        pass

    @abstractmethod
    async def analyze_trends(self, child_id: str, dimension: str) -> dict:
        pass

    @abstractmethod
    async def detect_milestones(self, child_id: str) -> List[dict]:
        pass

    @abstractmethod
    async def detect_plateau(self, child_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def build_context(self, child_id: str) -> dict:
        pass


# interfaces/i_rag_service.py
class IRAGService(ABC):
    """知识库与RAG检索接口（模块3）"""

    @abstractmethod
    async def search_games(self, query: str, filters: Optional[dict] = None, top_k: int = 10) -> List[dict]:
        pass

    @abstractmethod
    async def search_games_by_dimension(self, dimension: str, difficulty: str, top_k: int = 5) -> List[dict]:
        pass

    @abstractmethod
    async def get_game(self, game_id: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def search_methodology(self, query: str, top_k: int = 5) -> List[dict]:
        pass

    @abstractmethod
    async def search_across_layers(self, query: str, layers: List[str], top_k: int = 10) -> List[dict]:
        pass


# interfaces/i_video_service.py
class IVideoAnalysisService(ABC):
    """AI视频解析接口（模块4）"""

    @abstractmethod
    async def analyze_video(self, video_path: str, child_profile: dict, focus_points: List[str]) -> dict:
        pass


# interfaces/i_speech_service.py
class ISpeechService(ABC):
    """语音处理接口（模块5）"""

    @abstractmethod
    async def speech_to_text(self, audio_path: str) -> str:
        pass

    @abstractmethod
    async def text_to_speech(self, text: str, voice: str = "female") -> str:
        pass


# interfaces/i_document_parser.py
class IDocumentParserService(ABC):
    """文档解析接口（模块6）"""

    @abstractmethod
    async def parse_report(self, file_path: str, file_type: str) -> dict:
        pass

    @abstractmethod
    async def parse_scale(self, scale_data: dict, scale_type: str) -> dict:
        pass


# interfaces/i_llm_service.py
class ILLMService(ABC):
    """大模型调用接口"""

    @abstractmethod
    async def generate(self, prompt: str, system: Optional[str] = None, temperature: float = 0.7) -> str:
        pass

    @abstractmethod
    async def generate_structured(self, prompt: str, output_schema: dict, system: Optional[str] = None) -> dict:
        pass
```

---

## 5. 多 Graph 架构

### 5.1 GameSessionGraph（主流程）

```python
# graph/workflows/game_session_graph.py
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver

def create_game_session_graph():
    workflow = StateGraph(GameSessionState)

    # === 游戏前 ===
    workflow.add_node("init_session", init_session_node)
    workflow.add_node("load_game", load_game_node)
    workflow.add_node("prepare_guidance", prepare_guidance_node)

    # === 游戏后 ===
    workflow.add_node("process_game_end", process_game_end_node)
    workflow.add_node("analyze_video", analyze_video_node)
    workflow.add_node("validate_observations", validate_observations_node)
    workflow.add_node("generate_summary", generate_summary_node)
    workflow.add_node("generate_feedback_form", generate_feedback_form_node)
    workflow.add_node("process_feedback", process_feedback_node)
    workflow.add_node("update_memory", update_memory_node)
    workflow.add_node("re_evaluate", re_evaluate_node)

    # === 边 ===
    workflow.add_edge("init_session", "load_game")
    workflow.add_edge("load_game", "prepare_guidance")

    workflow.add_edge("process_game_end", "analyze_video")
    workflow.add_edge("analyze_video", "validate_observations")
    workflow.add_edge("validate_observations", "generate_summary")
    workflow.add_edge("generate_summary", "generate_feedback_form")

    workflow.add_edge("process_feedback", "update_memory")
    workflow.add_edge("update_memory", "re_evaluate")
    workflow.add_edge("re_evaluate", END)

    workflow.set_entry_point("init_session")

    return workflow.compile(
        checkpointer=SqliteSaver.from_conn_string("data/checkpoints.db"),
        interrupt_after=["prepare_guidance", "generate_feedback_form"]
    )
```

**流程说明**：

```
┌─────────────────────────────────────────────────────────────────┐
│                      GameSessionGraph                           │
│                                                                 │
│  [init_session] → [load_game] → [prepare_guidance]              │
│                                        ↓                        │
│                              ⏸️ INTERRUPT                        │
│                         "游戏准备就绪，等待开始"                   │
│                                        ↓                        │
│         ┌──────────────────────────────────────────────┐        │
│         │  游戏进行中（WebSocket 实时交互，不在 Graph）  │        │
│         │  - 实时指引推送（模块9）                      │        │
│         │  - 观察记录接收（模块10）并行                 │        │
│         └──────────────────────────────────────────────┘        │
│                                        ↓                        │
│                         用户点击"结束游戏"                       │
│                                        ↓                        │
│  [process_game_end] → [analyze_video] → [validate_observations] │
│           ↓                                                     │
│  [generate_summary] → [generate_feedback_form]                  │
│                                        ↓                        │
│                              ⏸️ INTERRUPT                        │
│                          "等待用户填写反馈"                       │
│                                        ↓                        │
│  [process_feedback] → [update_memory] → [re_evaluate] → END    │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 辅助 Graph

```python
# graph/workflows/record_graph.py
def create_record_graph():
    workflow = StateGraph(RecordState)

    workflow.add_node("parse_input", parse_input_node)
    workflow.add_node("extract_observation", extract_observation_node)
    workflow.add_node("save_to_db", save_to_db_node)
    workflow.add_node("update_memory", update_memory_node)

    workflow.add_edge("parse_input", "extract_observation")
    workflow.add_edge("extract_observation", "save_to_db")
    workflow.add_edge("save_to_db", "update_memory")
    workflow.add_edge("update_memory", END)

    workflow.set_entry_point("parse_input")
    return workflow.compile()


# graph/workflows/query_graph.py
def create_query_graph():
    workflow = StateGraph(QueryState)

    workflow.add_node("load_profile", load_profile_node)
    workflow.add_node("load_metrics", load_metrics_node)
    workflow.add_node("analyze_trends", analyze_trends_node)
    workflow.add_node("generate_report", generate_report_node)

    workflow.add_edge("load_profile", "load_metrics")
    workflow.add_edge("load_metrics", "analyze_trends")
    workflow.add_edge("analyze_trends", "generate_report")
    workflow.add_edge("generate_report", END)

    workflow.set_entry_point("load_profile")
    return workflow.compile()


# graph/workflows/plan_graph.py
def create_plan_graph():
    workflow = StateGraph(PlanState)

    workflow.add_node("load_context", load_context_node)
    workflow.add_node("analyze_priority", analyze_priority_node)
    workflow.add_node("search_games", search_games_node)
    workflow.add_node("generate_plan", generate_plan_node)
    workflow.add_node("save_plan", save_plan_node)

    workflow.add_edge("load_context", "analyze_priority")
    workflow.add_edge("analyze_priority", "search_games")
    workflow.add_edge("search_games", "generate_plan")
    workflow.add_edge("generate_plan", "save_plan")
    workflow.add_edge("save_plan", END)

    workflow.set_entry_point("load_context")
    return workflow.compile()
```

### 5.3 WebSocket 实时交互

```python
# services/realtime/game_websocket.py
class GameWebSocketHandler:
    """游戏进行时的实时交互处理（模块9+模块10并行）"""

    def __init__(self, speech_service, sqlite_service, rag_service):
        self.speech = speech_service
        self.sqlite = sqlite_service
        self.rag = rag_service

    async def handle_session(self, websocket, session_id: str):
        await websocket.accept()

        session = await self.sqlite.get_session(session_id)
        game = await self.rag.get_game(session["game_id"])
        steps = game["steps"]
        current_step = 0

        await self._send_guidance(websocket, steps[current_step])

        while True:
            data = await websocket.receive_json()

            if data["type"] == "observation":
                # 并行接收观察记录
                await self._save_observation(session_id, data)

            elif data["type"] == "next_step":
                current_step += 1
                if current_step < len(steps):
                    await self._send_guidance(websocket, steps[current_step])

            elif data["type"] == "end_game":
                await websocket.close()
                break

    async def _send_guidance(self, ws, step: dict):
        audio_path = await self.speech.text_to_speech(step["instruction"])
        await ws.send_json({
            "type": "guidance",
            "step": step,
            "audio_url": audio_path
        })

    async def _save_observation(self, session_id: str, data: dict):
        await self.sqlite.save_observation({
            "session_id": session_id,
            "timestamp": data["timestamp"],
            "type": data["observation_type"],
            "source": data["source"],
            "content": data.get("content")
        })
```

---

## 6. 依赖注入与服务容器

```python
# app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # 服务模式：mock / real
    SQLITE_MODE: str = "mock"
    GRAPHITI_MODE: str = "mock"
    RAG_MODE: str = "mock"
    VIDEO_MODE: str = "mock"
    SPEECH_MODE: str = "mock"
    DOCUMENT_MODE: str = "mock"
    LLM_MODE: str = "mock"

    # 真实服务配置
    DATABASE_PATH: str = "data/asd.db"
    GRAPHITI_URL: str = "http://localhost:8000"
    DEEPSEEK_API_KEY: str = ""
    ALIYUN_ACCESS_KEY: str = ""

    class Config:
        env_file = ".env"

settings = Settings()


# services/container.py
class ServiceContainer:
    """服务容器 - 统一管理所有服务实例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_services()
        return cls._instance

    def _init_services(self):
        from app.config import settings
        from services.mock import *
        from services.impl import *

        self._sqlite = SQLiteImpl(settings.DATABASE_PATH) if settings.SQLITE_MODE == "real" else SQLiteMock()
        self._graphiti = GraphitiImpl(settings.GRAPHITI_URL) if settings.GRAPHITI_MODE == "real" else GraphitiMock()
        self._rag = RAGImpl() if settings.RAG_MODE == "real" else RAGMock()
        self._video = VideoImpl() if settings.VIDEO_MODE == "real" else VideoMock()
        self._speech = SpeechImpl(settings.ALIYUN_ACCESS_KEY) if settings.SPEECH_MODE == "real" else SpeechMock()
        self._document = DocumentImpl() if settings.DOCUMENT_MODE == "real" else DocumentMock()
        self._llm = LLMImpl(settings.DEEPSEEK_API_KEY) if settings.LLM_MODE == "real" else LLMMock()

    @property
    def sqlite(self): return self._sqlite
    @property
    def graphiti(self): return self._graphiti
    @property
    def rag(self): return self._rag
    @property
    def video(self): return self._video
    @property
    def speech(self): return self._speech
    @property
    def document(self): return self._document
    @property
    def llm(self): return self._llm

container = ServiceContainer()
```

---

## 7. 开发顺序与并行策略

### 7.1 角色分工（2-3人）

| 角色 | 职责 |
|-----|------|
| A（框架负责人） | LangGraph 多 Graph 架构、State 设计、节点编排、API 路由、WebSocket |
| B（基础设施） | SQLite、Graphiti、RAG、文档解析 |
| C（AI能力） | 视频分析、语音处理、LLM Prompt（可与B合并） |

### 7.2 四周冲刺计划

#### 第1周：骨架搭建 + 全 Mock 跑通

| 角色 | 任务 | 产出 |
|-----|------|-----|
| A | 项目结构、接口定义、服务容器 | `interfaces/`、`container.py` |
| A | 5个 Graph 骨架 | `graph/workflows/*.py` |
| B | 所有 Mock 实现 | `services/mock/*.py` |
| C | Mock + Prompt 模板 | `prompts/` |

**验收**：全 Mock 跑通完整流程

#### 第2周：核心存储 + 评估链路

| 角色 | 任务 | 产出 |
|-----|------|-----|
| A | 节点逻辑完善、WebSocket 框架 | 健壮的节点代码 |
| B | SQLite 真实实现、文档解析真实实现 | `impl/sqlite_impl.py` |
| C | LLM 真实实现（DeepSeek） | `impl/llm_impl.py` |

**验收**：评估链路真实可用

#### 第3周：RAG + 游戏流程

| 角色 | 任务 | 产出 |
|-----|------|-----|
| A | GameSessionGraph 调试、Checkpoint 测试 | 游戏流程可用 |
| B | RAG 真实实现、50个游戏数据 | `impl/rag_impl.py` |
| C | 语音处理真实实现 | `impl/speech_impl.py` |

**验收**：能真实玩一次游戏

#### 第4周：记忆闭环 + MVP

| 角色 | 任务 | 产出 |
|-----|------|-----|
| A | 闭环逻辑、辅助 Graph 完善 | 完整闭环 |
| B | Graphiti 真实实现 | `impl/graphiti_impl.py` |
| C | 视频分析基础版 | `impl/video_impl.py` |

**验收**：MVP 完整可用

### 7.3 并行开发保障

```
关键原则：接口一旦定义，不轻易改动

第1周定义接口 → 第2-4周各自实现 → 通过容器切换 Mock/Real
```

---

## 附录：API 设计

```python
# app/main.py
from fastapi import FastAPI, WebSocket
from graph.workflows import *

app = FastAPI()

# 初始化 Graphs
query_graph = create_query_graph()
record_graph = create_record_graph()
plan_graph = create_plan_graph()
game_session_graph = create_game_session_graph()

@app.get("/child/{child_id}/status")
async def get_child_status(child_id: str):
    """随时查看孩子状态"""
    return await query_graph.ainvoke({"child_id": child_id})

@app.post("/child/{child_id}/record")
async def quick_record(child_id: str, content: str, record_type: str):
    """随时快速记录"""
    return await record_graph.ainvoke({
        "child_id": child_id,
        "content": content,
        "record_type": record_type
    })

@app.post("/child/{child_id}/weekly-plan")
async def generate_weekly_plan(child_id: str, week_start: str):
    """生成周计划"""
    return await plan_graph.ainvoke({
        "child_id": child_id,
        "week_start": week_start
    })

@app.post("/child/{child_id}/game/start")
async def start_game(child_id: str, game_id: str):
    """开始游戏会话"""
    thread_id = f"{child_id}-game-{uuid.uuid4().hex[:8]}"
    config = {"configurable": {"thread_id": thread_id}}
    result = await game_session_graph.ainvoke(
        {"child_id": child_id, "game_id": game_id},
        config
    )
    return {"thread_id": thread_id, "result": result}

@app.post("/game/{thread_id}/end")
async def end_game(thread_id: str, observations: list, video_path: str = None):
    """结束游戏"""
    config = {"configurable": {"thread_id": thread_id}}
    return await game_session_graph.ainvoke(
        {"user_input": {"observations": observations, "video_path": video_path}},
        config
    )

@app.post("/game/{thread_id}/feedback")
async def submit_feedback(thread_id: str, feedback: dict):
    """提交反馈"""
    config = {"configurable": {"thread_id": thread_id}}
    return await game_session_graph.ainvoke(
        {"user_input": {"feedback": feedback}},
        config
    )

@app.websocket("/ws/game/{session_id}")
async def game_websocket(websocket: WebSocket, session_id: str):
    """游戏实时交互"""
    handler = GameWebSocketHandler(
        container.speech,
        container.sqlite,
        container.rag
    )
    await handler.handle_session(websocket, session_id)
```

---

**文档结束**
