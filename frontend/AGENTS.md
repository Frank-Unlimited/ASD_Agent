# ASD Agent - Architecture Guide

> DIR/Floortime 自闭症儿童干预辅助系统。纯前端 SPA，数据存 localStorage，LLM 驱动。

---

## System Overview

```
家长
 │
 ▼
┌──────────────── App.tsx (Orchestrator) ────────────────┐
│                                                        │
│  页面: Chat │ Games │ Behaviors │ Radar │ Calendar │ Profile │
│                                                        │
│  Tool Call Router ──┬── analyze_interest               │
│                     ├── plan_floor_game                │
│                     ├── log_behavior                   │
│                     ├── generate_assessment            │
│                     └── navigate_page                  │
└─────────┬──────────────────────────────────────────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
 Agents     Storage Services
    │           │
    ▼           ▼
 qwenStreamClient ──→ DashScope API (qwen3-omni-flash)
```

---

## Core Flow: Chat + Tool Calling

```
家长消息 → qwenStreamClient.streamChat (SSE + function calling)
              │
              ├─ 普通回复 → 流式渲染
              │
              └─ tool_call → App.tsx Router
                    │
                    ├─ analyze_interest ──→ 兴趣维度分析 → 展示分析卡片 → 家长确认
                    ├─ plan_floor_game ──→ 联网搜索 + 游戏设计 → 展示实施卡片
                    ├─ log_behavior ────→ 行为→维度映射 → 存储 + 更新画像
                    ├─ generate_assessment → 综合评估 → 生成报告
                    └─ navigate_page ───→ 页面跳转
```

---

## Agents

| Agent | 文件 | 输入 | 输出 |
|-------|------|------|------|
| **对话** | `qwenService.ts` → `sendQwenMessage` | 消息 + 历史 + 档案 | 流式文本 / tool_call |
| **兴趣分析** | `gameRecommendConversationalAgent.ts` | 档案 + 维度指标 + 行为 | `InterestAnalysisResult` |
| **游戏计划** | `gameRecommendConversationalAgent.ts` | 目标维度 + 策略 + 偏好 | `GameImplementationPlan` |
| **游戏评估** | `qwenService.ts` → `evaluateSession` | 互动日志 `LogEntry[]` | `EvaluationResult` |
| **行为分析** | `behaviorAnalysisAgent.ts` | 行为描述 | `BehaviorAnalysis` |
| **综合评估** | `assessmentAgent.ts` | `HistoricalDataSummary` | `ComprehensiveAssessment` |
| **游戏推荐** | `gameRecommendAgent.ts` | 评估 + 偏好 | `GameRecommendation` |

所有 Agent 底层调用 `qwenStreamClient.chat()` (非流式 JSON) 或 `.streamChat()` (流式)。

---

## Game Lifecycle

```
聊天推荐                      游戏页面                    历史数据
────────                    ──────────                  ──────────
analyze_interest            GamePage (App.tsx)
      │                          │
      ▼                          │
plan_floor_game                  │
      │                          │
      ▼                          │
FloorGame (pending)  ──────→  开始游戏 (更新 dtstart)
 dtstart: 当前时间                 │
 dtend: ''                    记录 LogEntry[]
      │                          │
      │                     完成 → performAnalysis()
      │                          │
      │                     evaluateSession(logs)
      │                          │
      │                          ▼
FloorGame (completed)  ←──  updateGame({ 
 dtend: 结束时间                evaluation, 
                              status: 'completed',
                              dtend: 当前时间 })
      │
      ▼
collectHistoricalData()  ──→  从 FloorGame.evaluation 提取
```

**关键**：
- `dtstart` 和 `dtend` 使用完整 ISO 时间字符串（含年月日时分秒）
- 推荐时设置 `dtstart` 为当前时间，`dtend` 为空字符串
- 开始游戏时更新 `dtstart`，结束时更新 `dtend`
- `EvaluationResult` 存在 `FloorGame.evaluation` 字段中，不单独存储

---

## 8 Interest Dimensions

```
Visual · Auditory · Tactile · Motor · Construction · Order · Cognitive · Social
```

每条 `BehaviorAnalysis` 映射多个维度，每维度含：
- **weight** (0-1)：关联度
- **intensity** (-1 ~ +1)：兴趣方向（正=喜欢，负=讨厌）

`calculateDimensionMetrics()` 聚合为 strength (0-100) 和 exploration (0-100)。

---

## Game Recommendation: 2-Step Flow

```
Step 1: analyze_interest
  输入: childProfile + dimensionMetrics + recentBehaviors
  规则: 强度≥60 → leverage | 40-59且探索<50 → explore | <40 → avoid
  输出: 8维度分析 + 分类 + 3-5条干预建议
          │
          ▼ 家长确认维度 + 策略
Step 2: plan_floor_game
  输入: targetDimensions + strategy + searchResults(联网) + parentPreferences
  输出: gameTitle + goal + summary + steps[](5-8步)
          │
          ▼
  存入 floorGameStorage → 可在 Games 页面开始游戏
```

---

## Data Layer

### localStorage

| Key | 管理方 | 数据 |
|-----|--------|------|
| `asd_floortime_child_profile` | App.tsx 直接读写 | `ChildProfile` |
| `asd_floortime_interests_v1` | App.tsx 直接读写 | 兴趣画像 (8维度分数) |
| `asd_floortime_abilities_v1` | App.tsx 直接读写 | 能力画像 (6项DIR能力) |
| `asd_floortime_chat_history` | `chatStorage.ts` | 聊天记录 (≤100条) |
| `asd_floortime_behaviors` | `behaviorStorage.ts` | `BehaviorAnalysis[]` |
| `asd_floortime_medical_reports` | `reportStorage.ts` | `Report[]` |
| `asd_floor_games` | `floorGameStorage.ts` | `FloorGame[]`（含 evaluation） |
| `asd_comprehensive_assessments` | `assessmentStorage.ts` | 综合评估 (≤20条) |
| `asd_game_recommendations` | `assessmentStorage.ts` | 游戏推荐 (≤10条) |

### sessionStorage（临时跨工具传递）

| Key | 用途 |
|-----|------|
| `interest_analysis_context` | analyze_interest 上下文 → plan_floor_game 读取 |
| `interest_analysis_result` | 分析结果缓存 |

---

## LLM Integration

| 组件 | 模型 | 用途 |
|------|------|------|
| `qwenStreamClient` | qwen3-omni-flash | 流式对话 + Function Calling + 结构化 JSON |
| `dashscopeClient` | DashScope 多模态 | 图片/视频分析、报告 OCR |
| `speechService` | 阿里云 NLS | 语音转文字 |

API endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1`

---

## Card Rendering

Chat 消息中通过标记嵌入交互卡片：

```
:::INTEREST_ANALYSIS:{json}:::         → 兴趣维度分析卡片 (强度/探索度条形图 + 建议按钮)
:::GAME_IMPLEMENTATION_PLAN:{json}:::  → 游戏实施方案卡片 (步骤列表 + 开始按钮)
```

---

## File Map

```
frontend/src/
├── App.tsx                    主入口：页面路由 + 工具调用分发 + 状态管理
├── main.tsx                   Vite 入口
│
├── types/index.ts             所有 TS 类型
│
├── services/
│   ├── qwenStreamClient.ts    Qwen SSE 流式客户端（底层）
│   ├── qwenService.ts         对话/评估/推荐高层封装
│   ├── qwenSchemas.ts         ChatTools 定义 + JSON Schema
│   ├── api.ts                 API 入口（代理到 qwenService）
│   ├── dashscopeClient.ts     多模态分析客户端
│   ├── speechService.ts       语音识别
│   │
│   ├── gameRecommendConversationalAgent.ts   兴趣分析 + 游戏计划
│   ├── behaviorAnalysisAgent.ts              行为→维度映射
│   ├── assessmentAgent.ts                    综合评估
│   ├── gameRecommendAgent.ts                 游戏推荐
│   ├── onlineSearchService.ts                联网游戏搜索 (searchGamesOnline)
│   │
│   ├── historicalDataHelper.ts   历史数据聚合 + 维度指标计算
│   ├── radarChartService.ts      雷达图数据生成
│   │
│   ├── floorGameStorage.ts       FloorGame 持久化（含 evaluation）
│   ├── behaviorStorage.ts        行为记录持久化
│   ├── chatStorage.ts            聊天记录持久化
│   ├── assessmentStorage.ts      评估/推荐持久化
│   ├── reportStorage.ts          医疗报告持久化
│   ├── assessment.ts             统一 re-export 入口
│   │
│   ├── fileUpload.ts             文件上传校验
│   └── multimodalService.ts      图片/视频分析
│
├── prompts/                      Prompt 模板
│   ├── chatSystemPrompt.ts
│   ├── conversationalSystemPrompt.ts
│   ├── interestAnalysisPrompt.ts
│   ├── floorGamePlanPrompt.ts
│   ├── implementationPlanPrompt.ts
│   ├── asd-report-analysis.ts
│   ├── diagnosis-analysis.ts
│   └── multimodal-analysis.ts
│
├── components/
│   ├── RadarChartPage.tsx        雷达图可视化
│   └── CalendarPage.tsx          日历页面（周视图+月历+时间轴）
│
├── hooks/
│   └── useStreamChat.ts          流式对话 Hook
│
└── utils/
    ├── helpers.ts                UI/日期工具
    ├── clearCache.ts             缓存清理
    └── seedTestData.ts           测试数据生成
```

---

## Recent Updates

### 2026-02-19: AI 视频通话功能与上下文增强

#### 1. AI 视频通话核心功能 (AIVideoCall.tsx)

**背景**：家长在执行地板游戏时需要实时指导，传统文字聊天无法满足即时性和情境感知需求。

**方案**：集成阿里云 Qwen-Omni-Realtime 多模态实时通话能力，实现视频+语音双向互动，AI 可实时观察孩子行为并给出指导。

**核心能力**：
- 实时视频采集（720p@30fps）→ 每3秒发送一帧给 AI
- 实时音频采集（16kHz PCM16）→ 流式发送，支持 VAD 语音检测
- 双向语音对话：用户说话 → AI 实时转录 → AI 生成回复（文本+语音）
- 用户打断机制：检测到用户说话时立即停止 AI 音频播放
- 聊天记录持久化：对话历史自动保存到 `FloorGame.chat_history_in_game`

**技术实现**：
```
前端 (React)
  ├─ 视频采集: getUserMedia → Canvas → JPEG Base64
  ├─ 音频采集: AudioContext (16kHz) → PCM16 → WebSocket
  ├─ VAD 检测: 振幅阈值 + 连续帧计数 → speech_start/speech_end
  └─ 音频播放: AudioContext (24kHz) → 队列播放 → 支持打断

后端 (Python WebSocket)
  ├─ qwen_realtime_websocket.py: WebSocket 服务器 (端口 8766)
  ├─ 使用官方 dashscope SDK: OmniRealtimeConversation
  ├─ 动态系统提示词: build_system_prompt(child_info, game_info, history_info)
  └─ 事件转发: 阿里云事件 ↔ 前端 WebSocket
```

**系统提示词增强**：
- 孩子信息：姓名、年龄、诊断、能力水平（6维度）、兴趣倾向（8维度）、最近行为
- 游戏计划：游戏名称、训练目标、游戏步骤（分步指导）、所需材料
- 历史经验：之前有效的策略、孩子的挑战领域
- 角色定位：地板时光干预师，实时观察、及时反馈、灵活引导
- 核心原则：跟随孩子兴趣，不强求完成游戏，对话式交流（非指令式）

**文件变更**：
- 新增：`frontend/src/components/AIVideoCall.tsx` (600+ 行)
- 新增：`frontend/src/services/qwenRealtimeService.ts` (WebSocket 客户端)
- 新增：`frontend/src/services/videoCallContextHelper.ts` (上下文数据收集)
- 新增：`backend/qwen_realtime_websocket.py` (WebSocket 服务器)
- 修改：`frontend/src/App.tsx` (集成视频通话入口)
- 修改：`frontend/src/types/index.ts` (FloorGame 添加 `chat_history_in_game` 字段)

#### 2. 上下文数据收集辅助 (videoCallContextHelper.ts)

**问题**：AI 视频通话需要完整的孩子画像和游戏信息，但数据分散在多个 storage 中。

**方案**：创建统一的上下文收集函数 `collectVideoCallContext()`，自动聚合所有相关数据。

**收集内容**：
- 孩子信息：从 `ChildProfile` 提取基本信息，从 `BehaviorAnalysis[]` 计算兴趣画像，从 `FloorGame[]` 计算能力分数
- 游戏信息：当前游戏的标题、目标、步骤、材料
- 历史信息：最近5个游戏的评估结果、成功策略、挑战领域

**核心函数**：
```typescript
calculateInterestProfile(behaviors) → 8维度兴趣分数（weight + intensity）
calculateAbilityScores(games) → 6维度能力分数（从评估中提取）
extractSuccessfulStrategies(games) → 高分游戏的有效策略
identifyChallenges(games) → 低分游戏的挑战领域
formatRecentBehaviors(behaviors) → 简短的行为描述列表
```

**使用场景**：
- AI 视频通话启动时调用，构建完整上下文
- 后续可扩展到其他需要完整画像的场景（如综合评估、游戏推荐）

#### 3. 游戏结束按钮整合与确认对话框

**问题**：游戏页面有多个"结束游戏"按钮（顶部、底部、视频通话内），用户容易误触，且缺少确认机制。

**方案**：整合所有结束按钮的逻辑，添加统一的确认对话框，防止误操作导致数据丢失。

**实施**：
- 所有"结束游戏"按钮调用统一的 `handleEndGame()` 函数
- 弹出确认对话框："确定要结束游戏吗？游戏记录将被保存。"
- 用户确认后才执行结束逻辑（保存评估、更新状态、跳转页面）
- 视频通话内的"结束通话"按钮也触发游戏结束流程

**文件变更**：
- 修改：`frontend/src/App.tsx` (添加确认对话框逻辑)

---

### 2026-02-15: 日历页面重构与游戏时间字段改造

#### 1. 游戏时间字段改造 (FloorGame)

**问题**：原 `date: string` 字段无法准确记录游戏开始和结束时间，导致日历展示和时长计算不准确。

**方案**：将单一 `date` 字段拆分为 `dtstart` 和 `dtend` 两个 ISO 时间字符串字段，分别记录游戏开始和结束的完整时间戳。

**实施**：
- 修改 `FloorGame` 类型定义，添加 `dtstart` 和 `dtend` 字段
- 在 `floorGameStorage.ts` 中添加数据迁移逻辑，自动将旧数据的 `date` 转换为 `dtstart`
- 游戏推荐时设置 `dtstart` 为当前时间，`dtend` 为空字符串
- 游戏开始时更新 `dtstart`，游戏结束时更新 `dtend`

**影响范围**：`types/index.ts`、`floorGameStorage.ts`、`gameRecommendConversationalAgent.ts`、`App.tsx`

#### 2. 日历页面全面重构 (CalendarPage.tsx)

**问题**：原日历页面使用模拟数据，功能简陋，缺少时间轴视图和行为详情展示。

**方案**：创建全新的日历组件，采用苹果日历风格，集成真实数据源（游戏+行为）。

**核心功能**：周视图、月历视图、时间轴视图（0:00-24:00）、游戏/行为事件卡片、行为详情模态框

**数据集成**：从 `behaviorStorageService` 和 `floorGameStorageService` 读取数据，根据 `dtstart`/`dtend` 计算时长和位置

**UI/UX 优化**：渐变背景、毛玻璃效果、自定义滚动条、悬停动画、自动滚动到 0:00

**文件变更**：新增 `CalendarPage.tsx` (600+ 行)，修改 `App.tsx`

---

## Key Design Decisions

1. **纯前端架构** — 后端已弃用，所有数据存 localStorage
2. **LLM 驱动交互** — Qwen Function Calling 自动选择工具，无硬编码路由
3. **行为→维度累积** — 每条行为实时映射 8 维度，长期追踪兴趣变化
4. **两步游戏推荐** — 先分析维度再设计游戏，家长参与决策
5. **评估归属游戏** — `EvaluationResult` 存在 `FloorGame.evaluation`，不单独存储
6. **统一行为存储** — 所有行为数据统一通过 `behaviorStorageService` 读写
7. **结构化 JSON 输出** — Agent 使用 `response_format: json_object` 约束输出
