# ASD Agent - Architecture Guide

> DIR/Floortime 自闭症儿童干预辅助系统。纯前端 SPA，数据存 localStorage，LLM 驱动�?

---

## System Overview

```
家长
 �?
 �?
┌──────────────── App.tsx (Orchestrator) ────────────────�?
�?                                                       �?
�? 页面: Chat �?Games �?Behaviors �?Radar �?Calendar �?Profile �?
�?                                                       �?
�? Tool Call Router ──┬── analyze_interest               �?
�?                    ├── plan_floor_game                �?
�?                    ├── log_behavior                   �?
�?                    ├── generate_assessment            �?
�?                    └── navigate_page                  �?
└─────────┬──────────────────────────────────────────────�?
          �?
    ┌─────┴─────�?
    �?          �?
 Agents     Storage Services
    �?          �?
    �?          �?
 qwenStreamClient ──�?DashScope API (qwen3-omni-flash)
```

---

## Core Flow: Chat + Tool Calling

```
家长消息 �?qwenStreamClient.streamChat (SSE + function calling)
              �?
              ├─ 普通回�?�?流式渲染
              �?
              └─ tool_call �?App.tsx Router
                    �?
                    ├─ analyze_interest ──�?兴趣维度分析 �?展示分析卡片 �?家长确认
                    ├─ plan_floor_game ──�?联网搜索 + 游戏设计 �?展示实施卡片
                    ├─ log_behavior ────�?行为→维度映�?�?存储 + 更新画像
                    ├─ generate_assessment �?综合评估 �?生成报告
                    └─ navigate_page ───�?页面跳转
```

---

## Agents

| Agent | 文件 | 输入 | 输出 |
|-------|------|------|------|
| **对话** | `qwenService.ts` �?`sendQwenMessage` | 消息 + 历史 + 档案 | 流式文本 / tool_call |
| **兴趣分析** | `gameRecommendConversationalAgent.ts` | 档案 + 维度指标 + 行为 | `InterestAnalysisResult` |
| **游戏计划** | `gameRecommendConversationalAgent.ts` | 目标维度 + 策略 + 偏好 | `GameImplementationPlan` |
| **游戏评估** | `qwenService.ts` �?`evaluateSession` | 互动日志 `LogEntry[]` | `EvaluationResult` |
| **行为分析** | `behaviorAnalysisAgent.ts` | 行为描述 | `BehaviorAnalysis` |
| **综合评估** | `assessmentAgent.ts` | `HistoricalDataSummary` | `ComprehensiveAssessment` |
| **游戏推荐** | `gameRecommendAgent.ts` | 评估 + 偏好 | `GameRecommendation` |
| **游戏审查** | `gameReviewAgent.ts` | 游戏方案 + 背景 | 审查意见/反馈 |
| **联网搜索** | `bochaSearchService.ts` / `onlineSearchService.ts` | 关键词 | 网页搜索结果/游戏案例 |

所�?Agent 底层调用 `qwenStreamClient.chat()` (非流�?JSON) �?`.streamChat()` (流式)�?

---

## Game Lifecycle

```
聊天推荐                      游戏页面                    历史数据
────────                    ──────────                  ──────────
analyze_interest            GamePage (App.tsx)
      �?                         �?
      �?                         �?
plan_floor_game                  �?
      �?                         �?
      �?                         �?
FloorGame (pending)  ──────�? 开始游�?(更新 dtstart)
 dtstart: 当前时间                 �?
 dtend: ''                    记录 LogEntry[]
      �?                         �?
      �?                    完成 �?performAnalysis()
      �?                         �?
      �?                    evaluateSession(logs)
      �?                         �?
      �?                         �?
FloorGame (completed)  ←──  updateGame({ 
 dtend: 结束时间                evaluation, 
                              status: 'completed',
                              dtend: 当前时间 })
      �?
      �?
collectHistoricalData()  ──�? �?FloorGame.evaluation 提取
```

**关键**�?
- `dtstart` �?`dtend` 使用完整 ISO 时间字符串（含年月日时分秒）
- 推荐时设�?`dtstart` 为当前时间，`dtend` 为空字符�?
- 开始游戏时更新 `dtstart`，结束时更新 `dtend`
- `EvaluationResult` 存在 `FloorGame.evaluation` 字段中，不单独存�?

---

## 8 Interest Dimensions

```
Visual · Auditory · Tactile · Motor · Construction · Order · Cognitive · Social
```

每条 `BehaviorAnalysis` 映射多个维度，每维度含：
- **weight** (0-1)：关联度
- **intensity** (-1 ~ +1)：兴趣方向（�?喜欢，负=讨厌�?

`calculateDimensionMetrics()` 聚合�?strength (0-100) �?exploration (0-100)�?

---

## Game Recommendation: 2-Step Flow

```
Step 1: analyze_interest
  输入: childProfile + dimensionMetrics + recentBehaviors
  规则: 强度�?0 �?leverage | 40-59且探�?50 �?explore | <40 �?avoid
  输出: 8维度分析 + 分类 + 3-5条干预建�?
          �?
          �?AI 自动根据分析生成游戏方案
Step 2: plan_floor_game
  输入: targetDimensions + strategy + searchResults(Google Search) + parentPreferences
  输出: gameTitle + goal + summary + steps[](5-8�?
          �?
          �?
  存入 floorGameStorage �?点击“开始游戏”直接进�?(跳过 Step 确认)
```

---

## Data Layer

### localStorage

| Key | 管理�?| 数据 |
|-----|--------|------|
| `asd_floortime_child_profile` | App.tsx 直接读写 | `ChildProfile` |
| `asd_floortime_interests_v1` | App.tsx 直接读写 | 兴趣画像 (8维度分数) |
| `asd_floortime_abilities_v1` | App.tsx 直接读写 | 能力画像 (6项DIR能力) |
| `asd_floortime_chat_history` | `chatStorage.ts` | 聊天记录 (�?00�? |
| `asd_floortime_behaviors` | `behaviorStorage.ts` | `BehaviorAnalysis[]` |
| `asd_floortime_medical_reports` | `reportStorage.ts` | `Report[]` |
| `asd_floor_games` | `floorGameStorage.ts` | `FloorGame[]`（含 evaluation�?|
| `asd_comprehensive_assessments` | `assessmentStorage.ts` | 综合评估 (�?0�? |
| `asd_game_recommendations` | `assessmentStorage.ts` | 游戏推荐 (�?0�? |

### sessionStorage（临时跨工具传递）

| Key | 用�?|
|-----|------|
| `interest_analysis_context` | analyze_interest 上下�?�?plan_floor_game 读取 |
| `interest_analysis_result` | 分析结果缓存 |

---

## LLM Integration

| 组件 | 模型 | 用�?|
|------|------|------|
| `qwenStreamClient` | qwen3-omni-flash | 流式对话 + Function Calling + 结构�?JSON |
| `dashscopeClient` | DashScope 多模�?| 图片/视频分析、报�?OCR |
| `speechService` | 阿里�?NLS | 语音转文�?|

API endpoint: `https://dashscope.aliyuncs.com/compatible-mode/v1`

---

## Card Rendering

Chat 消息中通过标记嵌入交互卡片�?

```
:::INTEREST_ANALYSIS:{json}:::         �?兴趣维度分析卡片 (强度/探索度条形图 + 建议按钮)
:::GAME_IMPLEMENTATION_PLAN:{json}:::  �?游戏实施方案卡片 (步骤列表 + 开始按�?
```

---

## File Map

```
frontend/src/
├── App.tsx                    主入口：页面路由 + 工具调用分发 + 状态管�?
├── main.tsx                   Vite 入口
�?
├── types/index.ts             所�?TS 类型
�?
├── services/
�?  ├── qwenStreamClient.ts    Qwen SSE 流式客户端（底层�?
�?  ├── qwenService.ts         对话/评估/推荐高层封装
�?  ├── qwenSchemas.ts         ChatTools 定义 + JSON Schema
�?  ├── api.ts                 API 入口（代理到 qwenService�?
�?  ├── dashscopeClient.ts     多模态分析客户端
�?  ├── speechService.ts       语音识别
�?  �?
�?  ├── gameRecommendConversationalAgent.ts   兴趣分析 + 游戏计划
�?  ├── behaviorAnalysisAgent.ts              行为→维度映�?
�?  ├── assessmentAgent.ts                    综合评估
�?  ├── gameRecommendAgent.ts                 游戏推荐
�?  ├── onlineSearchService.ts                联网游戏搜索 (searchGamesOnline)
�?  �?
�?  ├── historicalDataHelper.ts   历史数据聚合 + 维度指标计算
�?  ├── radarChartService.ts      雷达图数据生�?
�?  �?
�?  ├── floorGameStorage.ts       FloorGame 持久化（�?evaluation�?
�?  ├── behaviorStorage.ts        行为记录持久�?
�?  ├── chatStorage.ts            聊天记录持久�?
�?  ├── assessmentStorage.ts      评估/推荐持久�?
�?  ├── reportStorage.ts          医疗报告持久�?
�?  ├── imageStorage.ts           多媒体资源存储管�?
�?  ├── assessment.ts             统一 re-export 入口
�?  �?
�?  ├── fileUpload.ts             文件上传校验
�?  ├── multimodalService.ts      图片/视频分析
�?  └── stepImageService.ts       游戏步骤配图/视觉增强服务
�?
├── prompts/                      Prompt 模板
�?  ├── chatSystemPrompt.ts
�?  ├── conversationalSystemPrompt.ts
�?  ├── interestAnalysisPrompt.ts
�?  ├── floorGamePlanPrompt.ts
�?  ├── implementationPlanPrompt.ts
�?  ├── asd-report-analysis.ts
�?  ├── diagnosis-analysis.ts
�?  └── multimodal-analysis.ts
�?
├── components/
�?  ├── RadarChartPage.tsx        雷达图可视化
�?  └── CalendarPage.tsx          日历页面（周视图+月历+时间轴）
�?
├── hooks/
�?  └── useStreamChat.ts          流式对话 Hook
�?
└── utils/
    ├── helpers.ts                UI/日期工具
    ├── clearCache.ts             缓存清理
    └── seedTestData.ts           测试数据生成
```

---

## Recent Updates

### 2026-02-27: RAG 知识库集成与并行检索架构

**背景**：游戏推荐和干预指导需要专业的 DIR/Floortime 理论支持，但联网搜索结果质量参差不齐，缺乏权威性和系统性。

**问题分析**：
1. 联网搜索（博查AI）虽然覆盖面广，但内容质量不稳定，需要 LLM 二次筛选
2. 专业知识（DIR 理论、游戏方案、案例库）分散在多个文档中，无法快速检索
3. 单一知识来源无法同时满足"权威性"和"时效性"需求

**解决方案**：引入阿里云百炼 RAG 知识库，与联网搜索并行调用，形成"专业知识库 + 网络资源"的双轨检索架构。

**技术实施**：

#### 1. 后端 RAG 服务 (backend/rag_service.py)

**架构设计**：
```
前端 knowledgeService
    ├─ 博查联网搜索 (直接调用) ────┐
    │                             │
    └─ RAG 检索 (HTTP 请求) ──────┤─ 并行异步
        │                         │
        ▼                         │
    后端 rag_service.py           │
        │                         │
        └─ 阿里云 Retrieve API ───┘
```

**核心功能**：
- 独立的 FastAPI 服务，运行在端口 8001
- 使用阿里云百炼 SDK (`alibabacloud-bailian20231229`) 调用 Retrieve API
- 支持向量检索 (DenseSimilarityTopK) 和关键词检索 (SparseSimilarityTopK)
- 支持重排序 (Reranking) 提升结果相关度（当前因 SDK 参数问题暂时关闭）
- 健康检查接口 (`/healthcheck`) 和调试接口 (`/api/rag/info`)

**API 端点**：
- `POST /api/rag/search`：检索知识库，返回文本切片列表
- `GET /healthcheck`：服务状态检查
- `GET /api/rag/info`：配置信息查看

**请求参数**：
```typescript
{
  query: string;              // 查询文本
  index_id?: string;          // 知识库 ID（可选，默认使用环境变量）
  top_k: number;              // 返回结果数量（默认 5）
  enable_reranking: boolean;  // 是否启用重排序（默认 false）
  dense_similarity_top_k: number;   // 向量检索 Top K（默认 50）
  sparse_similarity_top_k: number;  // 关键词检索 Top K（默认 50）
}
```

**响应格式**：
```typescript
{
  nodes: Array<{
    text: string;           // 文本切片内容
    score: number;          // 相关度分数 (0-1)
    metadata: {
      doc_name: string;     // 文档名称
      title: string;        // 标题
      doc_id: string;       // 文档 ID
      page_number: number[];// 页码
      // ... 其他元数据
    }
  }>;
  success: boolean;
  message?: string;
  request_id?: string;
}
```

**环境变量配置**：
```env
# 阿里云百炼 RAG 知识库配置
ALIBABA_CLOUD_ACCESS_KEY_ID=your-access-key-id
ALIBABA_CLOUD_ACCESS_KEY_SECRET=your-access-key-secret
ALIBABA_WORKSPACE_ID=your-workspace-id
ALIBABA_INDEX_ID=your-index-id
```

**知识库内容**（6 大模块）：
1. **地板游戏方案库**：按兴趣维度分类的结构化游戏设计模板，含目标、材料、步骤、变体
2. **DIR/Floortime 理论与实践指南**：FEDCI 功能性情绪发展阶段理论、跟随孩子引领原则、情感互动策略
3. **行为观察与分析指南**：8 大兴趣维度识别标准、情感倾向判定规则、发展阶段映射
4. **能力评估标准**：各维度能力基线、进步指标、退步预警信号
5. **家长指导话术与策略**：不同场景的引导语模板、常见误区纠正、情绪调节技巧
6. **案例库**：真实干预案例的匿名化记录，含初始状态、干预过程、效果评估、经验总结

#### 2. 前端 RAG 客户端 (frontend/src/services/ragService.ts)

**核心功能**：
- HTTP 客户端，调用后端 RAG 服务
- 支持健康检查 (`isConfigured()`)
- 支持格式化输出 (`searchAndFormat()`)

**使用示例**：
```typescript
import { ragService } from './ragService';

// 检索知识库
const nodes = await ragService.search('DIR Floortime 理论', { topK: 5 });

// 格式化为文本摘要
const formatted = await ragService.searchAndFormat('地板游戏方案', 5);
// 输出：
// 1. [相关度: 89.5%] 地板时光（DIR/Floor time）——6个通用碎片...
//    来源: 孤独症的综合治疗
```

#### 3. 统一知识检索服务 (frontend/src/services/knowledgeService.ts)

**核心功能**：并行调用联网搜索 + RAG 知识库，合并结果。

**架构设计**：
```typescript
knowledgeService.search(query)
    ├─ bochaSearchService.searchAndFormat(query, 5)  // 联网搜索
    └─ ragService.searchAndFormat(query, 5)          // RAG 检索
         ↓
    Promise.allSettled() 并行执行
         ↓
    合并结果：RAG 优先（权威性），联网搜索补充（时效性）
```

**结果合并策略**：
```
【专业知识库】
1. [相关度: 89.5%] DIR 理论核心内容...
   来源: 孤独症的综合治疗

【网络资源】
1. DIR/Floortime 最新研究进展...
   来源: 知乎 🔗 查看原文
```

**使用示例**：
```typescript
import { knowledgeService } from './knowledgeService';

const result = await knowledgeService.search('DIR Floortime 理论', {
  useWeb: true,   // 是否使用联网搜索
  useRAG: true,   // 是否使用 RAG
  webCount: 5,    // 联网搜索结果数
  ragCount: 5     // RAG 结果数
});

console.log(result.combined);  // 合并后的结果
```

#### 4. 游戏推荐 Agent 集成 (gameRecommendConversationalAgent.ts)

**核心改动**：将 `fetchKnowledge` 工具从单一联网搜索升级为并行检索。

**修改前**：
```typescript
fetchKnowledge: async (args) => {
  const result = await bochaSearchService.searchAndFormat(query, 5);
  return result || '（暂无相关搜索结果）';
}
```

**修改后**：
```typescript
fetchKnowledge: async (args) => {
  const result = await knowledgeService.search(query, {
    useWeb: true,
    useRAG: true,
    webCount: 5,
    ragCount: 5
  });
  return result.combined || '（暂无相关搜索结果）';
}
```

**ReAct 循环流程**：
```
LLM 思考：我需要什么信息？
    ↓
tool_call: fetchKnowledge("DIR Floortime 游戏方案")
    ↓
并行调用：RAG 检索 + 联网搜索
    ↓
返回合并结果给 LLM
    ↓
LLM 基于专业知识 + 网络资源生成游戏方案
```

#### 5. 测试页面 (frontend/test-rag-api.html)

**核心功能**：
- 服务状态监控（RAG 服务、SDK 状态、客户端状态）
- RAG 知识库检索测试
- 并行检索测试（RAG + 博查搜索）
- 原始响应查看（JSON 格式）
- 快速查询按钮（DIR 理论、游戏方案、兴趣维度等）

**UI 特点**：
- 渐变紫色主题，响应式设计
- 卡片式布局，实时状态反馈
- 分别展示 RAG 和网络搜索结果
- 显示相关度分数和文档来源

**使用方式**：
1. 确保 RAG 服务运行在 `http://localhost:8001`
2. 打开 `frontend/test-rag-api.html`
3. 点击"🌐 并行检索 (RAG + 网络)"按钮
4. 查看专业知识库和网络资源的检索结果

#### 6. 技术栈与依赖

**后端依赖**：
```txt
alibabacloud-bailian20231229>=2.8.1
alibabacloud-tea-openapi>=0.4.15
alibabacloud-credentials>=0.3.0
```

**前端依赖**：无额外依赖（使用原生 fetch API）

**启动命令**：
```bash
# 后端 RAG 服务
cd backend
uvicorn rag_service:app --port 8001 --reload

# 前端（已有）
cd frontend
npm run dev
```

**文件变更**：
- 新增：`backend/rag_service.py` (RAG 服务)
- 新增：`frontend/src/services/ragService.ts` (RAG 客户端)
- 新增：`frontend/src/services/knowledgeService.ts` (统一检索入口)
- 新增：`frontend/test-rag-api.html` (测试页面)
- 修改：`frontend/src/services/gameRecommendConversationalAgent.ts` (集成 RAG)
- 修改：`backend/requirements.txt` (添加 SDK 依赖)
- 修改：`backend/.env.example` (添加 RAG 配置)

**核心价值**：
1. **权威性提升**：专业知识库提供经过验证的 DIR/Floortime 理论和实践指南
2. **时效性保障**：联网搜索补充最新的研究进展和社区经验
3. **检索效率**：并行调用减少等待时间，提升用户体验
4. **降级保护**：任一服务不可用时，另一服务仍可正常工作
5. **可扩展性**：统一的 `knowledgeService` 接口，便于后续添加更多知识源

**已知问题**：
- 阿里云 SDK 的 `RetrieveRequestRerank` 参数设置存在问题，暂时关闭重排序功能
- 后续可通过升级 SDK 或使用 HTTP 直接调用解决

---

### 2026-02-23: 联网搜索服务迁移（Google → 博查AI）

**背景**：原 Google Custom Search API 在国内需要梯子且需绑定信用卡启用计费，虽有免费额度但访问受限，影响联网游戏搜索功能的可用性和稳定性。

**问题分析**：
1. Google API 域名被墙，国内用户无法直接访问
2. 需要 Azure 账号绑定信用卡才能使用（即使免费额度内）
3. API Key 配置复杂，频繁出现 403/400 权限错误
4. 搜索结果偏向国际内容，中文 DIR/Floortime 资源覆盖不足

**解决方案**：迁移至博查AI搜索服务（https://open.bocha.cn），专为国内 AI 应用设计的搜索 API。

**技术实施**：
```
旧架构: googleSearchService.ts → Google Custom Search API (需梯子)
         ↓
新架构: bochaSearchService.ts → 博查AI API (api.bocha.cn, 国内直连)
```

**核心改动**：
- 创建 `bochaSearchService.ts`：封装博查AI搜索接口，支持时间范围过滤、摘要生成、网站白名单/黑名单
- 修改 `onlineSearchService.ts`：将搜索调用从 `googleSearchService` 切换至 `bochaSearchService`
- 更新 `.env` 配置：替换 `VITE_GOOGLE_SEARCH_API_KEY` 为 `VITE_BOCHA_API_KEY`
- 删除 `googleSearchService.ts` 及相关测试文件

**博查AI优势**：
- 国内直连无需梯子，响应速度快（<1s）
- 专为 AI 优化，返回结构化 JSON（兼容 Bing Search API 格式）
- 支持详细摘要生成（`summary: true`），减少 LLM 解析负担
- 中文内容覆盖更全面，包含百度百科、知乎、搜狐等权威来源
- 支持时间范围过滤（`freshness: oneDay/oneWeek/oneMonth/oneYear`）

**数据流验证**：
```
用户请求 → bochaSearchService.search()
         ↓
博查AI返回10条真实网页（标题+URL+摘要+来源）
         ↓
LLM解析网页内容 → 生成5个结构化游戏方案
         ↓
返回前3个游戏供推荐系统使用
```

**测试工具**：新增 `test-bocha-api.html` 独立测试页面，支持基础搜索和带摘要搜索两种模式。

**文件变更**：
- 新增：`frontend/src/services/bochaSearchService.ts`
- 修改：`frontend/src/services/onlineSearchService.ts`
- 修改：`frontend/.env`
- 删除：`frontend/src/services/googleSearchService.ts`
- 新增：`frontend/test-bocha-api.html`
- 新增：`博查AI搜索_配置说明.md`

---

### 2026-02-23: 游戏结束流程优化

**问题**：游戏结束后自动跳转到日历页面，打断用户与 AI 助手的连续对话流程，不符合"游戏-反馈-讨论"的自然交互逻辑。

**方案**：修改游戏结束后的页面跳转目标，从 `Page.CALENDAR` 改为 `Page.CHAT`，让用户在游戏结束后直接返回聊天界面继续与 AI 讨论游戏效果、获取改进建议或开始下一轮推荐。

**实施**：修改 `App.tsx` 中 `PageGames` 组件的 `onBack` 回调，将 `setCurrentPage(Page.CALENDAR)` 改为 `setCurrentPage(Page.CHAT)`。

**用户体验提升**：游戏结束 → 查看评估结果 → 点击"返回游戏库" → 自动跳转到聊天界面 → 继续与 AI 对话，形成闭环。

---

### 2026-02-19: AI 视频通话功能与上下文增强

#### 1. AI 视频通话核心功能 (AIVideoCall.tsx)

**背景**：家长在执行地板游戏时需要实时指导，传统文字聊天无法满足即时性和情境感知需求�?

**方案**：集成阿里云 Qwen-Omni-Realtime 多模态实时通话能力，实现视�?语音双向互动，AI 可实时观察孩子行为并给出指导�?

**核心能力**�?
- 实时视频采集�?20p@30fps）→ �?秒发送一帧给 AI
- 实时音频采集�?6kHz PCM16）→ 流式发送，支持 VAD 语音检�?
- 双向语音对话：用户说�?�?AI 实时转录 �?AI 生成回复（文�?语音�?
- 用户打断机制：检测到用户说话时立即停�?AI 音频播放
- 聊天记录持久化：对话历史自动保存�?`FloorGame.chat_history_in_game`

**技术实�?*�?
```
前端 (React)
  ├─ 视频采集: getUserMedia �?Canvas �?JPEG Base64
  ├─ 音频采集: AudioContext (16kHz) �?PCM16 �?WebSocket
  ├─ VAD 检�? 振幅阈�?+ 连续帧计�?�?speech_start/speech_end
  └─ 音频播放: AudioContext (24kHz) �?队列播放 �?支持打断

后端 (Python WebSocket)
  ├─ qwen_realtime_websocket.py: WebSocket 服务�?(端口 8766)
  ├─ 使用官方 dashscope SDK: OmniRealtimeConversation
  ├─ 动态系统提示词: build_system_prompt(child_info, game_info, history_info)
  └─ 事件转发: 阿里云事�?�?前端 WebSocket
```

**系统提示词增�?*�?
- 孩子信息：姓名、年龄、诊断、能力水平（6维度）、兴趣倾向�?维度）、最近行�?
- 游戏计划：游戏名称、训练目标、游戏步骤（分步指导）、所需材料
- 历史经验：之前有效的策略、孩子的挑战领域
- 角色定位：地板时光干预师，实时观察、及时反馈、灵活引�?
- 核心原则：跟随孩子兴趣，不强求完成游戏，对话式交流（非指令式�?

**文件变更**�?
- 新增：`frontend/src/components/AIVideoCall.tsx` (600+ �?
- 新增：`frontend/src/services/qwenRealtimeService.ts` (WebSocket 客户�?
- 新增：`frontend/src/services/videoCallContextHelper.ts` (上下文数据收�?
- 新增：`backend/qwen_realtime_websocket.py` (WebSocket 服务�?
- 修改：`frontend/src/App.tsx` (集成视频通话入口)
- 修改：`frontend/src/types/index.ts` (FloorGame 添加 `chat_history_in_game` 字段)

#### 2. 上下文数据收集辅�?(videoCallContextHelper.ts)

**问题**：AI 视频通话需要完整的孩子画像和游戏信息，但数据分散在多个 storage 中�?

**方案**：创建统一的上下文收集函数 `collectVideoCallContext()`，自动聚合所有相关数据�?

**收集内容**�?
- 孩子信息：从 `ChildProfile` 提取基本信息，从 `BehaviorAnalysis[]` 计算兴趣画像，从 `FloorGame[]` 计算能力分数
- 游戏信息：当前游戏的标题、目标、步骤、材�?
- 历史信息：最�?个游戏的评估结果、成功策略、挑战领�?

**核心函数**�?
```typescript
calculateInterestProfile(behaviors) �?8维度兴趣分数（weight + intensity�?
calculateAbilityScores(games) �?6维度能力分数（从评估中提取）
extractSuccessfulStrategies(games) �?高分游戏的有效策�?
identifyChallenges(games) �?低分游戏的挑战领�?
formatRecentBehaviors(behaviors) �?简短的行为描述列表
```

**使用场景**�?
- AI 视频通话启动时调用，构建完整上下�?
- 后续可扩展到其他需要完整画像的场景（如综合评估、游戏推荐）

#### 3. 游戏结束按钮整合与确认对话框

**问题**：游戏页面有多个"结束游戏"按钮（顶部、底部、视频通话内），用户容易误触，且缺少确认机制�?

**方案**：整合所有结束按钮的逻辑，添加统一的确认对话框，防止误操作导致数据丢失�?

**实施**�?
- 所�?结束游戏"按钮调用统一�?`handleEndGame()` 函数
- 弹出确认对话框："确定要结束游戏吗？游戏记录将被保存�?
- 用户确认后才执行结束逻辑（保存评估、更新状态、跳转页面）
- 视频通话内的"结束通话"按钮也触发游戏结束流�?

**文件变更**�?
- 修改：`frontend/src/App.tsx` (添加确认对话框逻辑)

---

### 2026-02-19: 联网搜索集成与核心交互简�?

#### 1. 集成 Google Custom Search API
- **真正的联�?*：通过 `googleSearchService.ts` 实现真实网页搜索�?
- **降级保护**：当 API 未配置或超出限额时，自动 fallback �?LLM 自主搜索�?

#### 2. 入场流程极简优化 (App.tsx)
- **取消确认**：去掉了游戏开始前的“情�?能量”问答环节�?
- **一键直�?*：点击“开始游戏”卡片后 0.8s 直接跳转，提升家长使用效率�?

#### 3. 游戏数据哲学调整
- **移除 `expectedOutcome`**：贯�?DIR 系统中“过程重于结果”、“随儿而动”的无偏见干预理念�?

#### 4. 多模态增强与工具修复
- **预览发�?*：支持“先选图 -> 再打�?-> 合并发送”交互�?
- **正则优化**：解决了连续工具调用时的状态覆�?Bug (UI 稳定�?�?


### 2026-02-15: 日历页面重构与游戏时间字段改�?

#### 1. 游戏时间字段改�?(FloorGame)

**问题**：原 `date: string` 字段无法准确记录游戏开始和结束时间，导致日历展示和时长计算不准确�?

**方案**：将单一 `date` 字段拆分�?`dtstart` �?`dtend` 两个 ISO 时间字符串字段，分别记录游戏开始和结束的完整时间戳�?

**实施**�?
- 修改 `FloorGame` 类型定义，添�?`dtstart` �?`dtend` 字段
- �?`floorGameStorage.ts` 中添加数据迁移逻辑，自动将旧数据的 `date` 转换�?`dtstart`
- 游戏推荐时设�?`dtstart` 为当前时间，`dtend` 为空字符�?
- 游戏开始时更新 `dtstart`，游戏结束时更新 `dtend`

**影响范围**：`types/index.ts`、`floorGameStorage.ts`、`gameRecommendConversationalAgent.ts`、`App.tsx`

#### 2. 日历页面全面重构 (CalendarPage.tsx)

**问题**：原日历页面使用模拟数据，功能简陋，缺少时间轴视图和行为详情展示�?

**方案**：创建全新的日历组件，采用苹果日历风格，集成真实数据源（游戏+行为）�?

**核心功能**：周视图、月历视图、时间轴视图�?:00-24:00）、游�?行为事件卡片、行为详情模态框

**数据集成**：从 `behaviorStorageService` �?`floorGameStorageService` 读取数据，根�?`dtstart`/`dtend` 计算时长和位�?

**UI/UX 优化**：渐变背景、毛玻璃效果、自定义滚动条、悬停动画、自动滚动到 0:00

**文件变更**：新�?`CalendarPage.tsx` (600+ �?，修�?`App.tsx`

---

## Key Design Decisions

1. **纯前端架�?* �?后端已弃用，所有数据存 localStorage
2. **LLM 驱动交互** �?Qwen Function Calling 自动选择工具，无硬编码路�?
3. **行为→维度累�?* �?每条行为实时映射 8 维度，长期追踪兴趣变�?
4. **两步游戏推荐** �?先分析维度再设计游戏，家长参与决�?
5. **评估归属游戏** �?`EvaluationResult` 存在 `FloorGame.evaluation`，不单独存储
6. **统一行为存储** �?所有行为数据统一通过 `behaviorStorageService` 读写
7. **结构�?JSON 输出** �?Agent 使用 `response_format: json_object` 约束输出
