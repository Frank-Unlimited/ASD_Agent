# ReAct 模式改造 — 游戏推荐 Agent

## 目标

将 `generateFloorGamePlan` 和 `analyzeInterestDimensions` 从"单次预取注入"模式改为 **ReAct 循环**：LLM 自主决定调用哪些工具、调用几次，直到获得足够信息后输出最终 JSON。

---

## 两种模式对比

```
旧模式（单次）
  调用方  →  预取 memory + 预取 search  →  构建大 prompt  →  LLM 单次输出 JSON

新模式（ReAct）
  调用方  →  给 LLM 任务 + 工具清单
               ↓
           LLM 思考：我需要什么信息？
               ↓
           tool_call: fetchMemory("...")
               ↓
           执行工具 → 返回结果给 LLM
               ↓
           LLM 再思考：还需要什么？
               ↓
           tool_call: fetchKnowledge("...")
               ↓
           执行工具 → 返回结果
               ↓
           LLM: 信息足够了 → 输出最终 JSON
```

---

## 工具定义

| 工具 | 实现 | 说明 |
|------|------|------|
| `fetchMemory(query)` | `fetchMemoryFacts()` + `formatMemoryFactsForPrompt()` | 搜索 graphiti 记忆层 |
| `fetchKnowledge(query)` | `bochaSearchService.searchAndFormat()` | 联网搜索外部知识 |

> **TODO**：`fetchKnowledge` 后续并行接入 RAG 知识库

---

## 改动文件清单

### 1. `qwenStreamClient.ts` — 新增 `chatWithTools()`

现有 `chat()` 只返回 `string`（不带 tool_calls）。新增方法：

```typescript
chatWithTools(messages, options) → Promise<{
  content: string;
  toolCalls: ToolCall[];
  finishReason: string;   // 'stop' | 'tool_calls' | ...
}>
```

不改动现有 `chat()` / `streamChat()`，向后兼容。

---

### 2. `gameRecommendConversationalAgent.ts` — 主要改动

**新增：**
- `REACT_TOOLS` — 工具描述数组（传给 LLM 的 tool schema）
- `executeTool(name, args, childName)` — 工具执行器，路由到 memory / knowledge
- `runReActLoop(systemPrompt, userMessage, childName, maxIterations=5)` — 通用 ReAct 循环
  - 每轮：调用 `chatWithTools(messages, { tools: REACT_TOOLS })`
  - `finishReason === 'tool_calls'`：执行所有 tool_calls，把结果追加 messages，继续
  - `finishReason === 'stop'`：返回 `content`（最终 JSON 文本）
  - 超过 maxIterations：追加一条 "请现在输出最终 JSON" 强制收尾

**修改：**
- `analyzeInterestDimensions` → 调用 `runReActLoop`，初始 prompt 含 childProfile + dimensionMetrics，不再预取 memory
- `generateFloorGamePlan` → 调用 `runReActLoop`，初始 prompt 含 childProfile + 目标 + 偏好，不再预取 memory 和 search

---

### 3. `floorGamePlanPrompt.ts` — 新增 `buildFloorGamePlanReActPrompt()`

去掉 `memorySection` / `searchResults` 参数（由 LLM 自主获取），改为添加工具使用指引：

```
...孩子信息 + 目标维度 + 策略 + 家长偏好...

【可用工具】
- fetchMemory：搜索孩子的历史游戏记录和参与规律
- fetchKnowledge：搜索外部 DIR/Floortime 游戏方案

请先收集足够信息，再输出以下 JSON 格式的游戏方案：
{...JSON schema 示例...}
```

原有 `buildFloorGamePlanPrompt()` 保留不动（其他地方可能复用）。

---

### 4. `interestAnalysisPrompt.ts` — 新增 `buildInterestAnalysisReActPrompt()`

同上，去掉 `memorySection`，加工具指引，保留 `dimensionMetrics`（这是数值型结构化数据，非历史文本，仍在初始 prompt 中注入）。

---

## ReAct 循环关键参数

| 参数 | 值 | 说明 |
|------|----|------|
| `maxIterations` | 5 | 最多 5 轮 tool 调用 |
| `tool_choice` | `'auto'` | 由 LLM 决定是否调用 |
| `response_format` | 不使用 | ReAct 阶段不强制 JSON schema，最终内容用 `cleanLLMResponse()` 解析 |
| memory 结果数 | 15 | 与现有保持一致 |
| knowledge 搜索数 | 5 | 博查 top-5 条目 |
