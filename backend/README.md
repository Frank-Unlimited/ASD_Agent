# ASD Memory Service — 记忆层说明文档

基于 [graphiti-core](https://github.com/getzep/graphiti) 的时序感知记忆层，为 ASD/DIR Floortime 干预应用提供跨时间的事实性记忆存储与检索。

---

## 架构概览

```
前端写入触发点
  行为记录 / 游戏复盘 / 综合评估 / 医疗报告
        │
        │  POST /api/memory/write (202 立即返回)
        ▼
  ┌─────────────────────────────────┐
  │         memory_service.py       │
  │                                 │
  │  _pending_buffer (list)◄────────┤
  │        │                        │
  │  asyncio.Queue (FIFO)           │
  │        │                        │
  │  _queue_worker (单一协程)       │
  │        │顺序写入，不并发         │
  └────────┼────────────────────────┘
           │
           ▼
        Neo4j + graphiti-core
        (实体提取 / 时序边 / 失效机制)


前端读取（assessmentAgent）
  POST /api/memory/search
        │
        ├── pending_buffer 中的原始文本（pending=true）← 最新，未提炼
        └── graphiti 已处理的精炼事实（pending=false）← 带 valid_at / invalid_at
```

### 设计要点

| 特性 | 说明 |
|------|------|
| **FIFO 顺序写入** | graphiti 要求 episode 顺序入库，单一 worker 协程保证不并发写入 |
| **即时可见（pending buffer）** | 写入请求一入队，内容立即对 search 可见，不等 graphiti 处理完成 |
| **双层搜索结果** | `pending=true`（原始观察）+ `pending=false`（提炼事实）一次返回 |
| **时序感知** | graphiti 自动管理 `valid_at` / `invalid_at`，旧事实被新事实覆盖时记录失效时间 |
| **fire-and-forget** | 前端不等写入响应，主流程不阻塞 |
| **group_id 隔离** | 中文 group_id 自动 MD5 哈希，保证多用户数据隔离 |

---

## 环境准备

### 1. 启动 Neo4j（Docker）

```bash
docker start <neo4j容器名>
# 或首次创建：
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/你的密码 \
  neo4j:5.26
```

确认可访问：`http://localhost:7474`（Neo4j Browser）

### 2. 配置环境变量

复制 `backend/.env.example` → `backend/.env`，填写：

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=你的Neo4j密码

DASHSCOPE_API_KEY=sk-xxx          # 阿里云 DashScope API Key
LLM_MODEL=qwen-plus               # 用于 graphiti 实体提取
LLM_SMALL_MODEL=qwen-turbo        # 用于轻量任务
LLM_EMBEDDING_MODEL=text-embedding-v3
```

### 3. 安装依赖

```bash
cd backend/
pip install -r requirements.txt
# 或
uv sync
```

`requirements.txt` 关键依赖：
```
graphiti-core[neo4j]>=0.3.0
neo4j>=5.26.0
fastapi
uvicorn
python-dotenv
```

### 4. 启动服务

```bash
cd backend/
uvicorn memory_service:app --port 8000 --reload
```

服务就绪后访问 `http://localhost:8000/healthcheck` 确认状态。

---

## API 参考

### `GET /healthcheck`

健康检查，同时返回当前队列状态。

**响应示例：**
```json
{
  "status": "healthy",
  "queue_pending": 2,
  "buffer_size": 2
}
```

---

### `POST /api/memory/write`

将一条观察记录推入 FIFO 队列，**立即返回 202**，不等 graphiti 处理。

**请求体：**
```json
{
  "group_id": "xiaoming",
  "content": "小明今天展示了以下行为：...",
  "reference_time": "2026-02-25T10:00:00+08:00"
}
```

| 字段 | 说明 |
|------|------|
| `group_id` | 用户/儿童标识。中文会自动 MD5 哈希（`grp_` + 12位）|
| `content` | 自然语言观察文本，graphiti 据此提取实体和边 |
| `reference_time` | **事件发生时间**（ISO 8601），非入库时间 |

**响应示例（202 Accepted）：**
```json
{
  "success": true,
  "status": "queued",
  "episode_id": "uuid-...",
  "queue_position": 1
}
```

---

### `POST /api/memory/search`

搜索记忆，返回 **pending buffer 原文** + **graphiti 精炼事实**。

**请求体：**
```json
{
  "group_id": "xiaoming",
  "query": "小明在各兴趣维度上的历史表现",
  "num_results": 10
}
```

**响应示例：**
```json
{
  "facts": [
    {
      "text": "小明今天展示了以下行为：...",
      "valid_at": "2026-02-25T10:00:00+00:00",
      "invalid_at": null,
      "pending": true
    },
    {
      "text": "小明对Construction维度表现出强烈正向兴趣",
      "valid_at": "2026-01-15T00:00:00+00:00",
      "invalid_at": null,
      "pending": false
    },
    {
      "text": "小明对Auditory维度表现出明显回避",
      "valid_at": "2025-11-01T00:00:00+00:00",
      "invalid_at": "2026-01-20T00:00:00+00:00",
      "pending": false
    }
  ]
}
```

| 字段 | 含义 |
|------|------|
| `pending=true` | 已入队但 graphiti 尚未处理的原始观察文本 |
| `pending=false, invalid_at=null` | graphiti 已提炼的**当前有效**事实 |
| `pending=false, invalid_at≠null` | graphiti 已提炼的**历史事实**（被新事实覆盖） |

---

### `GET /api/memory/queue/status`

调试接口，查看当前队列和 pending buffer 详情。

**响应示例：**
```json
{
  "queue_size": 1,
  "pending_buffer": [
    {
      "id": "uuid-...",
      "episode_name": "memory-2026-02-25T10:00:00",
      "group_id": "xiaoming",
      "reference_time": "2026-02-25T10:00:00+00:00",
      "queued_at": "2026-02-25T10:00:05+00:00",
      "content_preview": "小明今天展示了以下行为：反复..."
    }
  ]
}
```

---

## 前端写入触发点

所有写入均为 **fire-and-forget**（不等待响应，失败静默忽略），不阻塞主流程。

**写入辅助函数（`frontend/src/App.tsx`）：**

```typescript
// 通用写入封装
function writeMemory(content: string, referenceTime: string) {
  const groupId = getUserGroupId();  // 从 localStorage 读取儿童姓名
  fetch('http://localhost:8000/api/memory/write', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ group_id: groupId, content, reference_time: referenceTime }),
  }).catch(() => {});
}
```

### 触发点 1：行为记录

**位置**：`App.tsx` → `onToolCall` → `case 'log_behavior':` → `onProfileUpdate` 之后

```typescript
writeMemory(
  buildBehaviorContent(behaviorAnalysis, currentChildProfile),
  behaviorAnalysis.timestamp
);
```

**自然语言格式：**
```
{child_name}今天展示了以下行为：{behavior}。
兴趣维度分析：
- Construction维度——强烈正向（主动选择积木，持续专注20分钟，{reasoning}）
- Visual维度——轻微正向（偶尔观察颜色排列）
```

---

### 触发点 2：综合评估

**位置**：`App.tsx` → `case 'generate_assessment':` → `saveAssessment(assessment)` 之后

```typescript
writeMemory(
  buildAssessmentContent(assessment, currentChildProfile),
  assessment.timestamp
);
```

**自然语言格式：**
```
对{child_name}的综合发展评估：
当前画像：{current_profile}
评估摘要：{summary}
干预建议：{next_step_suggestion}
```

---

### 触发点 3：医疗报告

**位置**：`App.tsx` → `reportStorageService.saveReport(report)` 之后

```typescript
writeMemory(
  buildMedicalReportContent(report, childName),
  report.date
);
```

> 注意：使用 `report.date`（报告出具日期），而非入库时间。这是 graphiti 双时间模型的核心价值。

**自然语言格式：**
```
{child_name}的医疗报告（{report_type}，{date}）显示：
{summary}
诊断特征：{diagnosis}
专业建议：{next_step_suggestion}
```

---

### 触发点 4：游戏复盘

**位置**：`App.tsx` → `performAnalysis()` → `setGameReview(reviewResult)` 之后

```typescript
writeMemory(
  buildGameReviewContent(floorGame, reviewResult, currentChildProfile),
  floorGame.dtend ?? floorGame.dtstart ?? new Date().toISOString()
);
```

**自然语言格式：**
```
{child_name}参与了「{game_title}」游戏，目标是{goal}。
游戏时长约{duration}分钟，效果良好（参与度82/100）。
观察到：{review_summary_key_points}
建议：continue（继续）。
下一步：{next_step_suggestion}
```

---

## 前端读取集成

目前已在 `assessmentAgent.ts` 中集成记忆读取。

**位置**：`frontend/src/services/assessmentAgent.ts` → `generateComprehensiveAssessment()` 入口

```typescript
const memoryFacts: MemoryFact[] = await fetchMemoryFacts(
  childProfile.name,
  `${childProfile.name}在各兴趣维度上的历史表现、变化趋势和发展阶段`,
  20
);
```

**不可用时降级**：`fetchMemoryFacts` 设置 5s 超时，失败时静默返回空数组，不影响评估流程。

---

## Prompt 注入结构

`formatMemoryFactsForPrompt(facts)` 将搜索结果格式化为三段式文本块注入 LLM prompt：

```
【跨时间记忆（graphiti 提取，涵盖完整干预历程）】

**最新观察（已记录，graphiti 处理中，共 N 条）**
注意：这些是尚未被提炼的原始观察，包含完整上下文，是最新的事实来源。
- [2026-02-25] 小明今天展示了以下行为：...

**当前有效事实（graphiti 提炼，按时间升序）**
- [2026-01-15] 小明对Construction维度表现出强烈正向兴趣
- [2026-02-10] 小明对Social维度从回避转为轻微接受

**历史事实（已被新事实覆盖，仅供感知变化幅度）**
- [2025-11-01→2026-01-20] 小明对Auditory维度表现出明显回避
```

| 段落 | 来源 | 用途 |
|------|------|------|
| 最新观察 | `pending=true`，原始 episode 文本 | 最新状态，尚未提炼 |
| 当前有效事实 | `pending=false, invalid_at=null` | 评估现状的主要依据 |
| 历史事实 | `pending=false, invalid_at≠null` | 感知变化幅度（如从回避到接受） |

---

## graphiti 提取指令

所有 `add_episode()` 调用共用同一条 `custom_extraction_instructions`：

```
This content contains observations about an ASD child receiving DIR/Floortime
intervention. Extract only meaningful, lasting facts about the child.

ENTITY EXTRACTION:
- Extract the child's name as the primary entity.
- When interest dimensions are referenced, extract them using only these
  canonical English names: Visual, Auditory, Tactile, Motor, Construction,
  Order, Cognitive, Social.

EDGE EXTRACTION:
- Focus on facts that reveal the child's characteristics, preferences,
  behavioral patterns, or intervention outcomes.
- For child-dimension relationships, include emotional valence in the fact:
  strongly positive, mildly positive, neutral, mildly negative, strongly negative.
- When a fact signals a change from a prior pattern, state it explicitly
  so outdated facts can be superseded.
```

---

## 测试

### 快速健康检查

```bash
curl http://localhost:8000/healthcheck
```

### 写入一条记忆

```bash
curl -X POST http://localhost:8000/api/memory/write \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "test-child",
    "content": "test-child今天展示了以下行为：主动选择积木并持续专注搭建20分钟。\n兴趣维度分析：\n- Construction维度——强烈正向（主动参与，高度专注）",
    "reference_time": "2026-02-25T10:00:00+08:00"
  }'
```

### 搜索记忆

```bash
curl -X POST http://localhost:8000/api/memory/search \
  -H "Content-Type: application/json" \
  -d '{
    "group_id": "test-child",
    "query": "兴趣维度表现",
    "num_results": 10
  }'
```

### 业务场景完整测试

```bash
cd backend/
python test_business_memory.py
```

测试覆盖：99天干预历程、6条跨时间记忆写入、事实时序覆盖验证（`invalid_at` 机制）、4个 Agent 查询场景。

---

## 注意事项

1. **graphiti 处理时间**：单条 episode 提取约 5–30s（LLM 调用），期间数据已通过 pending buffer 对搜索可见。
2. **顺序性保证**：graphiti 不支持并发 `add_episode()`，FIFO worker 确保严格顺序写入。
3. **Windows 编码**：运行测试脚本时需设置 `PYTHONIOENCODING=utf-8`。
4. **Neo4j 版本**：需要 5.26+ 才能使用 graphiti 的全部特性。
5. **中文 group_id**：会被自动哈希（`grp_` + MD5前12位），两端调用保持一致（前端传原始中文名，后端自动规范化）。
