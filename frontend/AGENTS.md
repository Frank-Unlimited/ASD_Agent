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
FloorGame (pending)  ──────→  开始游戏
      │                          │
      │                     记录 LogEntry[]
      │                          │
      │                     完成 → performAnalysis()
      │                          │
      │                     evaluateSession(logs)
      │                          │
      │                          ▼
FloorGame (completed)  ←──  updateGame({ evaluation, status })
      │
      ▼
collectHistoricalData()  ──→  从 FloorGame.evaluation 提取
```

**关键**：`EvaluationResult` 存在 `FloorGame.evaluation` 字段中，不单独存储。

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
│   └── RadarChartPage.tsx        雷达图可视化
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

## Key Design Decisions

1. **纯前端架构** — 后端已弃用，所有数据存 localStorage
2. **LLM 驱动交互** — Qwen Function Calling 自动选择工具，无硬编码路由
3. **行为→维度累积** — 每条行为实时映射 8 维度，长期追踪兴趣变化
4. **两步游戏推荐** — 先分析维度再设计游戏，家长参与决策
5. **评估归属游戏** — `EvaluationResult` 存在 `FloorGame.evaluation`，不单独存储
6. **统一行为存储** — 所有行为数据统一通过 `behaviorStorageService` 读写
7. **结构化 JSON 输出** — Agent 使用 `response_format: json_object` 约束输出
