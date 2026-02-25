# Backend 架构文档

> backend/ 下现有两个独立 Python 服务，互不依赖，均由前端发起调用。

---

## 服务总览

| 服务 | 文件 | 端口 | 协议 | 用途 |
|------|------|------|------|------|
| Memory Service | `memory_service.py` | 8000 | HTTP (FastAPI) | Graphiti 记忆层：写入/搜索干预历史 |
| Realtime WS | `qwen_realtime_websocket.py` | 8766 | WebSocket | AI 视频通话：代理 Qwen-Omni-Realtime |

启动方式：
```
# Memory Service
uvicorn memory_service:app --port 8000 --reload

# Realtime WebSocket
python qwen_realtime_websocket.py
```

---

## Memory Service (`memory_service.py`)

### 核心设计：FIFO Queue + Graphiti

写入操作不能并发（graphiti 要求顺序性），因此采用异步队列解耦：

```
Frontend  ──POST /api/memory/write──▶  FIFO Queue  ──worker──▶  Graphiti (Neo4j)
                                            │
                                     _pending_buffer
                                     (立即对 search 可见)
```

**写入流程：**
1. 请求入队，同时写入 `_pending_buffer`，立即返回 202
2. 单一 worker (`_queue_worker`) 按入队顺序逐一调用 `graphiti.add_episode()`
3. 写入完成后从 `_pending_buffer` 移除（无论成功失败）

**搜索响应结构：**

```
search 返回 = [ pending_buffer 原文 ] + [ graphiti 精炼 facts ]
                  ↑ 最新、未提炼          ↑ 已实体提取、时序建模
```

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/memory/write` | POST | 写入记忆，202 立即返回 |
| `/api/memory/search` | POST | 语义搜索，返回 `FactItem[]` |
| `/api/memory/queue/status` | GET | 调试：查看当前队列状态 |
| `/healthcheck` | GET | 健康检查，含队列积压量 |

### FactItem 结构

| 字段 | 类型 | 含义 |
|------|------|------|
| `text` | string | 事实内容（graphiti 提炼句 或 pending 原文） |
| `valid_at` | ISO 8601 \| null | 事实生效时间（对应事件发生时间） |
| `invalid_at` | ISO 8601 \| null | 事实失效时间（null = 当前有效） |
| `pending` | bool | true = 在队列中，尚未被 graphiti 提取 |

### Graphiti 实体提取指令

通过 `custom_extraction_instructions` 约束提取行为：
- 以孩子姓名为主实体
- 兴趣维度只识别 8 个标准英文名（Visual / Auditory / Tactile / Motor / Construction / Order / Cognitive / Social）
- 边（关系）标注情感倾向（strongly positive → strongly negative）
- 若新事实与旧事实矛盾，明确声明，使旧边被 graphiti 标记为 `invalid_at`

### group_id 隔离

前端传入账号 ID（`user_xxxxxxxx`）作为 `group_id`，多用户数据在 graphiti 内按此隔离。
含非 ASCII 字符的 group_id 自动 MD5 哈希为安全字符串。

### 依赖栈

```
graphiti-core[neo4j]  ──▶  Neo4j (bolt://localhost:7687)
                            DashScope API (LLM 提取 + Embedding + Reranker)
```

LLM 配置通过 `.env` 注入（`LLM_MODEL`, `LLM_SMALL_MODEL`, `LLM_EMBEDDING_MODEL`），
底层使用 OpenAI-compatible 接口，可替换为任意兼容服务商。

---

## Realtime WebSocket (`qwen_realtime_websocket.py`)

### 角色

纯代理层：前端无法直接使用 Qwen-Omni-Realtime 的 Python SDK，由此服务桥接。

```
前端 (AIVideoCall 组件)
  ──WS ws://localhost:8766──▶  qwen_realtime_websocket.py
                                    │
                                    ▼
                              DashScope SDK
                              Qwen-Omni-Realtime
```

### 主要职责

1. 接收前端的孩子信息、游戏信息、历史信息，调用 `build_system_prompt()` 构建 AI 角色扮演 prompt
2. 将前端的音频/视频流转发至 Qwen-Omni-Realtime
3. 将模型输出（音频 + 文本）实时推回前端

---

## 前端与 Backend 的交互边界

| 前端模块 | 调用目标 | 触发时机 |
|---------|---------|---------|
| `memoryService.ts` | Memory Service :8000 | 行为记录 / 游戏复盘 / 综合评估 / 医疗报告保存后（fire-and-forget） |
| `memoryService.ts` | Memory Service :8000 | Agent 调用前 fetch 相关记忆注入 prompt |
| `AIVideoCall` 组件 | Realtime WS :8766 | 游戏页面发起 AI 视频通话时 |

> 其余所有 Agent 调用（兴趣分析、游戏设计、综合评估等）直接访问 DashScope API，不经过 backend。

---

## 环境变量（`.env`，参考 `.env.example`）

| 变量 | 用途 |
|------|------|
| `NEO4J_URI / USER / PASSWORD` | Graphiti 图数据库连接 |
| `DASHSCOPE_API_KEY` | Realtime WS + Memory Service 共用 |
| `LLM_MODEL / LLM_SMALL_MODEL` | Graphiti 实体提取模型 |
| `LLM_EMBEDDING_MODEL` | Graphiti 向量化模型 |
