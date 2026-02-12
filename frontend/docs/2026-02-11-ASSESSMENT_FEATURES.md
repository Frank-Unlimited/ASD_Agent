# 孩子现状评估功能说明

## 概述
系统通过多种方式对 ASD 儿童的现状进行全面评估，包括兴趣维度分析、能力维度评估、行为记录和互动质量评估。

---

## 一、评估维度

### 1. 兴趣维度（Interest Dimensions）
**8 大兴趣维度**：
- **Visual（视觉）**：对视觉刺激的兴趣（如颜色、光影、旋转物体）
- **Auditory（听觉）**：对声音的兴趣（如音乐、特定声音）
- **Tactile（触觉）**：对触觉刺激的兴趣（如质地、温度）
- **Motor（运动）**：对身体运动的兴趣（如跳跃、旋转）
- **Construction（建构）**：对建构活动的兴趣（如积木、拼图）
- **Order（秩序）**：对秩序和规律的兴趣（如排列、分类）
- **Cognitive（认知）**：对认知挑战的兴趣（如解谜、学习）
- **Social（社交）**：对社交互动的兴趣（如与人互动、模仿）

**数据结构**：
```typescript
export type UserInterestProfile = Record<InterestDimensionType, number>;
// 示例：{ Visual: 15, Auditory: 8, Tactile: 5, ... }
```

**评估方式**：
- 通过行为记录累积分数
- 每个行为的关联度（weight）乘以系数（5）累加
- 分数越高表示该维度的兴趣越强

### 2. 能力维度（Ability Dimensions）
**DIR/Floortime 6 大能力维度**：
- **自我调节**：情绪管理和自我控制能力（0-100分）
- **亲密感**：与他人建立情感连接的能力（0-100分）
- **双向沟通**：基础的来回互动能力（0-100分）
- **复杂沟通**：使用符号和语言进行沟通的能力（0-100分）
- **情绪思考**：理解和表达情绪的能力（0-100分）
- **逻辑思维**：逻辑推理和问题解决能力（0-100分）

**数据结构**：
```typescript
export type UserAbilityProfile = Record<AbilityDimensionType, number>;
// 示例：{ '自我调节': 80, '亲密感': 90, '双向沟通': 75, ... }
```

**评估方式**：
- 通过游戏互动和报告分析更新
- 每次更新可以增加或减少分数（scoreChange）
- 分数范围限制在 0-100 之间

---

## 二、评估方式

### 1. 初始评估（欢迎页面）

#### 方式 A：上传医疗报告
**流程**：
1. 用户上传医疗评估报告图片（JPG/PNG）
2. 系统使用 OCR 提取报告文字
3. AI 分析报告内容，生成：
   - OCR 提取结果（完整文字）
   - 报告摘要（一句话）
   - 孩子画像（100-200字）
4. 保存到 localStorage（MedicalReport 类型）

**技术实现**：
- 使用 `multimodalService.parseImage()` 进行图片分析
- Prompt：`ASD_REPORT_ANALYSIS_PROMPT`
- 输出格式：JSON（ocr, summary, profile）

**代码位置**：
- `frontend/src/App.tsx` - PageWelcome 组件
- `frontend/src/services/multimodalService.ts`
- `frontend/src/prompts/asd-report-analysis.ts`

#### 方式 B：口述孩子情况
**流程**：
1. 家长用文字描述孩子的情况
2. AI 分析描述内容，生成孩子画像
3. 保存到儿童档案的 diagnosis 字段

**技术实现**：
- 使用 `api.analyzeVerbalInput()` 进行分析
- Prompt：`VERBAL_DESCRIPTION_ANALYSIS_PROMPT`
- 输出格式：纯文本（300字以内）

**代码位置**：
- `frontend/src/App.tsx` - PageWelcome 组件
- `frontend/src/services/api.ts`
- `frontend/src/prompts/diagnosis-analysis.ts`

### 2. 行为记录评估（AI 对话）

**触发条件**：
- 家长在聊天中描述孩子的任何具体行为
- 例如："孩子正在玩积木"、"他一直盯着旋转的风扇"

**评估流程**：
1. AI 自动调用 `log_behavior` 工具
2. 提取行为描述
3. 分析关联的兴趣维度：
   - **关联度（weight）**：0.1-1.0，表示行为与维度的关联程度
   - **强度（intensity）**：-1.0到1.0，表示孩子的喜好程度
   - **推理（reasoning）**：解释关联原因和情绪态度
4. 保存到行为数据库（behaviorStorage）
5. 更新兴趣档案（interestProfile）

**数据结构**：
```typescript
export interface BehaviorAnalysis {
  behavior: string;           // 行为描述
  matches: InterestMatch[];   // 关联的兴趣维度
  timestamp?: string;         // 记录时间
  source?: 'GAME' | 'REPORT' | 'CHAT';  // 来源
  id?: string;                // 唯一标识
}

export interface InterestMatch {
  dimension: InterestDimensionType;  // 兴趣维度
  weight: number;                    // 关联度 0.1-1.0
  intensity: number;                 // 强度 -1.0到1.0
  reasoning: string;                 // 推理说明
}
```

**代码位置**：
- `frontend/src/App.tsx` - PageAIChat 组件，onToolCall 处理
- `frontend/src/services/qwenService.ts` - SYSTEM_INSTRUCTION_BASE
- `frontend/src/services/qwenSchemas.ts` - LogBehaviorTool
- `frontend/src/services/behaviorStorage.ts`

### 3. 游戏互动评估（游戏结束后）

**评估内容**：
1. **综合互动分（score）**：0-100分
   - 反馈质量分（feedbackScore）：互动质量、回应及时性、情感连结
   - 探索广度分（explorationScore）：行为多样性、尝试新事物的意愿

2. **兴趣分析（interestAnalysis）**：
   - 从游戏记录中提取行为
   - 分析每个行为关联的兴趣维度

3. **能力更新（abilityUpdates）**：
   - 根据游戏目标更新对应的能力维度
   - 例如：自我调节游戏 → 更新"自我调节"能力

**评估流程**：
1. 游戏结束，收集互动记录（logs）
2. 调用 `api.analyzeSession(logs)` 进行评估
3. 显示评估结果（分数、总结、建议）
4. 更新成长曲线（trendData）
5. 更新兴趣档案和能力档案

**代码位置**：
- `frontend/src/App.tsx` - PageGames 组件，GameState.SUMMARY
- `frontend/src/services/qwenService.ts` - evaluateSession()
- `frontend/src/services/api.ts` - analyzeSession()

### 4. 报告分析评估（档案页面）

**评估流程**：
1. 用户在档案页面上传报告（图片或文档）
2. 系统分析报告内容
3. 提取兴趣更新和能力更新
4. 更新档案数据

**技术实现**：
- 使用 `api.analyzeReport(reportText)` 进行分析
- 返回 `ProfileUpdate` 结构
- 包含 interestUpdates 和 abilityUpdates

**代码位置**：
- `frontend/src/App.tsx` - PageAIChat 组件，handleFileUpload
- `frontend/src/services/qwenService.ts` - analyzeReport()
- `frontend/src/services/api.ts`

---

## 三、数据存储

### 1. 儿童档案（ChildProfile）
**存储位置**：`localStorage` - `asd_floortime_child_profile`

**数据结构**：
```typescript
export interface ChildProfile {
  name: string;           // 姓名
  gender: string;         // 性别
  birthDate: string;      // 出生日期 YYYY-MM-DD
  diagnosis: string;      // 孩子画像/诊断描述
  avatar: string;         // 头像 URL
  createdAt: string;      // 创建时间
}
```

### 2. 兴趣档案（InterestProfile）
**存储位置**：`localStorage` - `asd_floortime_interests_v1`

**数据结构**：
```typescript
{
  Visual: 15,
  Auditory: 8,
  Tactile: 5,
  Motor: 12,
  Construction: 20,
  Order: 10,
  Cognitive: 7,
  Social: 6
}
```

### 3. 能力档案（AbilityProfile）
**存储位置**：`localStorage` - `asd_floortime_abilities_v1`

**数据结构**：
```typescript
{
  '自我调节': 80,
  '亲密感': 90,
  '双向沟通': 75,
  '复杂沟通': 65,
  '情绪思考': 70,
  '逻辑思维': 60
}
```

### 4. 行为记录（BehaviorAnalysis）
**存储位置**：`localStorage` - `asd_floortime_behaviors`

**数据结构**：数组，每个元素包含：
```typescript
{
  id: "20260210_123456_abc123",
  behavior: "兴奋地玩积木",
  matches: [
    {
      dimension: "Construction",
      weight: 1.0,
      intensity: 1.0,
      reasoning: "直接进行建构活动，表现出强烈兴趣"
    }
  ],
  timestamp: "2026-02-10T12:34:56.789Z",
  source: "CHAT"
}
```

### 5. 医疗报告（MedicalReport）
**存储位置**：`localStorage` - `asd_floortime_reports`

**数据结构**：数组，每个元素包含：
```typescript
{
  id: "report_20260210_123456",
  imageUrl: "base64...",
  ocrResult: "报告文字内容",
  summary: "报告摘要",
  diagnosis: "孩子画像",
  date: "2026-02-10",
  type: "hospital",
  createdAt: "2026-02-10T12:34:56.789Z"
}
```

---

## 四、评估结果展示

### 1. 档案页面（PageProfile）
**展示内容**：
- 基本信息（姓名、年龄、性别）
- 最新画像（来自最新报告或初始评估）
- 报告列表（历史报告）

**功能**：
- 导入新报告
- 查看报告详情
- 导出评估报告

### 2. 行为数据页面（PageBehaviors）
**展示内容**：
- 统计卡片（总记录数、游戏记录、报告记录）
- 筛选器（按兴趣维度、按来源）
- 行为列表（时间倒序）

**行为详情弹窗**：
- 行为描述
- 兴趣维度分析：
  - 关联度（单向进度条）
  - 强度（双向进度条，中心线为中性点）
  - 推理说明
- 元数据（记录时间、数据来源）

### 3. 游戏总结页面（GameState.SUMMARY）
**展示内容**：
- 综合互动分（大数字显示）
- 分数分解（反馈质量分、探索广度分）
- 总结和建议
- 兴趣探索度分析（提取的行为和关联维度）
- 成长曲线（更新后的趋势图）

---

## 五、AI 评估 Agent

### 1. Evaluation Agent (Session)
**功能**：评估游戏互动会话

**输入**：互动记录（LogEntry[]）

**输出**：
```typescript
{
  score: number;              // 综合得分 0-100
  feedbackScore: number;      // 反馈质量分 0-100
  explorationScore: number;   // 探索广度分 0-100
  summary: string;            // 总结
  suggestion: string;         // 建议
  interestAnalysis: BehaviorAnalysis[];  // 兴趣分析
}
```

**代码位置**：`frontend/src/services/qwenService.ts` - evaluateSession()

### 2. Evaluation Agent (Report)
**功能**：分析医疗报告并更新档案

**输入**：报告文字内容

**输出**：
```typescript
{
  source: 'REPORT',
  interestUpdates: BehaviorAnalysis[];  // 兴趣更新
  abilityUpdates: AbilityUpdate[];      // 能力更新
}
```

**代码位置**：`frontend/src/services/qwenService.ts` - analyzeReport()

### 3. Diagnosis Agent
**功能**：分析报告或口述，生成孩子画像

**输入**：报告文字或家长描述

**输出**：孩子画像文本（300字以内）

**代码位置**：
- `frontend/src/services/api.ts` - analyzeReportForDiagnosis()
- `frontend/src/services/api.ts` - analyzeVerbalInput()

---

## 六、评估数据流

```
用户输入
  ↓
┌─────────────────────────────────────┐
│ 1. 初始评估（欢迎页面）              │
│    - 上传报告 → OCR + AI分析         │
│    - 口述情况 → AI分析               │
│    → 生成孩子画像                    │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 2. 持续评估（AI对话）                │
│    - 描述行为 → log_behavior工具     │
│    → 提取兴趣维度（weight + intensity）│
│    → 保存行为记录                    │
│    → 更新兴趣档案                    │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 3. 互动评估（游戏结束）              │
│    - 收集互动记录 → evaluateSession  │
│    → 计算互动分数                    │
│    → 提取兴趣分析                    │
│    → 更新能力档案                    │
│    → 更新成长曲线                    │
└─────────────────────────────────────┘
  ↓
┌─────────────────────────────────────┐
│ 4. 报告评估（档案页面）              │
│    - 上传报告 → analyzeReport        │
│    → 提取兴趣和能力更新              │
│    → 更新档案数据                    │
└─────────────────────────────────────┘
  ↓
数据存储（localStorage）
  - ChildProfile
  - InterestProfile
  - AbilityProfile
  - BehaviorAnalysis[]
  - MedicalReport[]
```

---

## 七、待实现功能

### 1. 后端集成
- [ ] 将数据保存到 SQLite 数据库
- [ ] 实现后端 API 接口
- [ ] 数据同步和备份

### 2. 高级评估
- [ ] 定期评估报告生成（周报、月报）
- [ ] 发展趋势分析（长期追踪）
- [ ] 对比分析（与同龄儿童对比）

### 3. 可视化增强
- [ ] 兴趣雷达图（8维度）
- [ ] 能力雷达图（6维度）
- [ ] 时间轴展示（发展历程）

### 4. 智能推荐
- [ ] 基于评估结果推荐游戏
- [ ] 基于评估结果推荐干预策略
- [ ] 个性化训练计划生成

---

## 八、使用建议

### 对于家长
1. **初始设置**：完整填写孩子信息，上传医疗报告或详细描述孩子情况
2. **日常使用**：在 AI 对话中随时描述孩子的行为，系统会自动记录和分析
3. **游戏互动**：定期进行地板游戏，系统会评估互动质量并更新能力档案
4. **定期回顾**：查看行为数据页面，了解孩子的兴趣变化和发展趋势

### 对于开发者
1. **数据一致性**：确保所有评估数据都通过 `handleProfileUpdate()` 统一处理
2. **错误处理**：所有 AI 调用都应有 fallback 机制
3. **性能优化**：大量行为记录时考虑分页加载
4. **隐私保护**：敏感数据加密存储，考虑数据导出和删除功能
