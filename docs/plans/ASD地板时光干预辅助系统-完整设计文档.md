# ASD地板时光干预辅助系统 - 完整设计文档

**项目名称**：ASD儿童地板时光家庭干预辅助系统
**文档日期**：2025-01-25
**文档版本**：v2.0（合并版）
**服务对象**：残联组织、ASD儿童家长、ASD专业医生
**核心定位**：基于LangGraph多Agent协同的智能成长追踪与干预系统

---

## 目录

1. [项目概述](#1-项目概述)
2. [核心业务流程](#2-核心业务流程)
3. [核心痛点分析](#3-核心痛点分析)
4. [系统总体架构](#4-系统总体架构)
5. [动态State设计](#5-动态state设计)
6. [多Agent系统设计](#6-多agent系统设计)
7. [微观变化捕捉系统](#7-微观变化捕捉系统)
8. [LangGraph工作流编排](#8-langgraph工作流编排)
9. [技术栈与实现](#9-技术栈与实现)
10. [前端架构方案](#10-前端架构方案)
11. [部署架构](#11-部署架构)
12. [实施计划](#12-实施计划)

---

## 1. 项目概述

### 1.1 背景知识

**ASD（孤独症谱系障碍）**是一种在婴幼儿时期就会显现的神经发育障碍，核心特征包括：

- **社交沟通困难**：叫名字没反应、语言发育迟缓、不会使用手势、难以与同龄人互动
- **重复受限行为**：刻板动作、维持固定流程、强烈兴趣偏好、感官反应异常

**地板时光（DIR/Floortime）**是由美国儿童精神病学家斯坦利·格林斯潘提出的以孩子为中心的发展性干预模式，核心理念是：

- **三大支柱**：发展（Development）、个体差异（Individual Differences）、人际关系（Relationships）
- **六大情绪发展里程碑**：自我调节、亲密关系、双向沟通、复杂沟通、情绪想法、逻辑思考
- **核心方法**：放下主导权，跟随孩子兴趣，通过游戏建立情感联结

### 1.2 项目定位

为残联提供普惠性ASD家庭干预解决方案，主要用户是**家长**（日常使用），医生通过导出报告进行异步指导（暂不需要独立医生端）。

### 1.3 核心价值主张

**从"数据记录器"到"敏锐的成长观察者"**

- **捕捉微观变化**：不只记录量表分数，而是敏锐捕捉每个孩子的微小成长细节
- **动态时序追踪**：建立完整时间线，可视化展示进步轨迹
- **个性化干预**：每个孩子都是独特的个体，系统动态适配其特点
- **专业赋能家长**：让普通家长也能像专业治疗师一样精准干预

---

## 2. 核心业务流程

系统围绕以下核心流程设计，这是项目的主线任务：


### 2.1 主流程：地板游戏干预闭环

```
┌─────────────────────────────────────────────────────────────┐
│                    核心干预流程                              │
└─────────────────────────────────────────────────────────────┘

第一步：建立孩子画像
├─ 解读医院报告/填写量表
├─ AI分析生成多维度观察框架
└─ 输出：孩子的初始画像（能力、兴趣、关注点）

第二步：推荐地板游戏
├─ 基于孩子画像和最新观察
├─ RAG检索游戏知识库
└─ 输出：个性化游戏方案（目标、玩法、注意事项）

第三步：实施地板游戏
├─ 语音指引家长游戏步骤
├─ 实时记录孩子表现（快捷按钮/语音）
├─ 视频录制游戏过程
└─ 输出：游戏过程数据（指引日志、观察记录、视频）

第四步：总结游戏过程
├─ AI分析视频（行为、情绪、互动）
├─ 结合家长记录生成总结
├─ 识别亮点和需要关注的地方
└─ 输出：本次游戏总结报告

第五步：家长填写反馈表
├─ AI生成个性化反馈问题
├─ 家长填写主观感受和观察
└─ 输出：家长反馈数据

第六步：再次评估孩子
├─ 融合游戏数据、视频分析、家长反馈
├─ 更新孩子画像（能力、兴趣、进展）
├─ 对比历史数据识别变化趋势
└─ 输出：更新后的孩子画像 + 下一步建议

第七步：形成闭环
└─ 返回第二步，推荐新游戏（基于最新画像）

┌─────────────────────────────────────────────────────────────┐
│                    辅助功能                                  │
└─────────────────────────────────────────────────────────────┘

辅助功能1：随时记录孩子情况
├─ 语音/文字记录日常观察
├─ AI分析识别兴趣点、里程碑
└─ 自动融入孩子画像

辅助功能2：可视化成长路线
├─ 多维度雷达图
├─ 时间线展示里程碑
├─ 趋势分析和进展报告
└─ 导出医学报告（给医生）
```

### 2.2 流程设计原则

1. **闭环驱动**：每次游戏都会更新孩子画像，影响下一次推荐
2. **人机协作**：AI负责分析和建议，家长负责执行和反馈
3. **持续优化**：系统通过不断积累数据，越用越精准
4. **微观捕捉**：不只看大的变化，更关注每个细微进步

---

## 3. 核心痛点分析

### 3.1 家长面临的四大痛点

#### 痛点1：专业知识匮乏
- **问题**：家长不懂儿童神经发育、发展心理学，对"跟随兴趣""打开-关闭沟通圈"等原则只停留在字面理解
- **后果**：要么完全放任不管，要么用成人想法强行干预，违背地板时光核心逻辑

#### 痛点2：不知道孩子对什么感兴趣
- **问题**：孩子对常规玩具"没反应"，兴趣表现隐蔽、重复、感官导向（盯着风扇、转车轮、摸材质）
- **后果**：家长能观察到行为，但不知道如何描述，看不到规律和趋势

#### 痛点3：培训费用高昂
- **问题**：专业培训动辄几千到几万元，普通家庭难以承担
- **后果**：只能东拼西凑网上碎片化知识，干预缺乏系统性和专业性

#### 痛点4：医家协同断裂
- **问题**：医生培训内容通用化，与孩子实际情况脱节；家长缺乏专业表达能力，无法精准反馈孩子表现
- **后果**：医生指导无法落地，家长困惑无人解答

#### 痛点5：个性化干预缺失
- **问题**：每个ASD孩子的症状、能力、兴趣都截然不同，标准化方案无法适配
- **后果**：干预偏离孩子核心需求，效果大打折扣

### 3.2 解决方案思路

通过**AI多Agent协同系统**，搭建医生、家长与孩子之间的联动桥梁，实现干预过程的标准化、个性化与可追溯。

---

## 4. 系统总体架构

### 4.1 架构设计理念

**从"固定档案"转向"动态生命体"**

将每个孩子视为持续变化的个体，系统核心能力是**敏锐捕捉变化**，而非仅仅记录静态数据。

### 4.2 三层架构

```
┌─────────────────────────────────────────────────┐
│                    前端层                        │
│  React + TypeScript + Ant Design Mobile        │
│  - 移动端优先设计                                │
│  - 实时语音指引                                  │
│  - 视频录制与上传                                │
│  - 可视化成长展示                                │
└────────────────┬────────────────────────────────┘
                 │ HTTPS + WebSocket
┌────────────────▼────────────────────────────────┐
│                   后端层                         │
│  Node.js + Express + LangGraph                  │
│  ┌──────────────────────────────────────┐      │
│  │   多Agent协同系统                     │      │
│  │   - 评估Agent                         │      │
│  │   - 推荐Agent                         │      │
│  │   - 观察捕获Agent                     │      │
│  │   - 实时指引Agent                     │      │
│  │   - 视频分析Agent                     │      │
│  │   - 总结Agent                         │      │
│  │   - 反馈表Agent                       │      │
│  │   - 记忆更新Agent                     │      │
│  │   - 再评估Agent                       │      │
│  │   - 可视化Agent                       │      │
│  └──────────────────────────────────────┘      │
│  - State驱动的工作流                            │
│  - 人机协作暂停点                                │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│                   数据层                         │
│  ┌─────────────┐  ┌──────────────┐              │
│  │   SQLite    │  │ PostgreSQL   │              │
│  │  用户数据   │  │  + pgvector  │              │
│  │  干预记录   │  │  游戏知识库  │              │
│  └─────────────┘  └──────┬───────┘              │
│                         │                        │
│                  ┌──────▼───────┐               │
│                  │   Graphiti   │               │
│                  │  长期记忆    │               │
│                  │  时序追踪    │               │
│                  └──────────────┘               │
└─────────────────────────────────────────────────┘
```

### 4.3 核心技术特性

| 特性 | 实现方式 | 价值 |
|------|---------|------|
| **动态State** | 灵活的时序数据结构 | 捕捉微观变化，支持个性化维度扩展 |
| **LangGraph工作流** | 状态驱动的Agent协同 | 信息连贯，支持中断恢复 |
| **Graphiti记忆** | 时序图数据库 | 自动识别里程碑，分析因果关联 |
| **人机协作** | 关键节点暂停等待家长反馈 | AI不会"自说自话"，确保准确性 |
| **多模态融合** | 视频+语音+文字 | 全方位观察孩子，提升分析准确性 |


---

## 5. 动态State设计

### 5.1 设计理念

传统State是**固定的字段**（如`name`, `age`, `score`），而本系统的State是**活的时序数据**：

```typescript
// ❌ 传统State - 死板的字段
const traditionalState = {
  childName: "辰辰",
  age: 2,
  eyeContactScore: 35  // 孤立的数字
};

// ✅ 动态State - 时序数据
const dynamicState = {
  childTimeline: {
    metrics: {
      eyeContact: {
        dataPoints: [
          {timestamp: "2024-01-01", value: 2, source: "assessment"},
          {timestamp: "2024-01-15", value: 5, source: "videoAI"},
          {timestamp: "2024-01-23", value: 8, source: "gameSession"}
        ],
        analysis: {
          trend: "improving",
          rate: 0.22,
          lastMilestone: "2024-01-23:首次主动发起互动"
        }
      }
    }
  }
};
```

### 5.2 核心State结构

```typescript
interface DynamicInterventionState {
  // 孩子的"活"档案 - 不是字段，而是时间线
  childTimeline: {
    // 基础信息（相对稳定）
    profile: {
      name: string;
      age: number;
      diagnosis: string;
      interests: string[];
    };

    // 动态指标图谱 - 每个指标都是时序数据
    metrics: {
      // 六大情绪发展里程碑（格林斯潘）
      emotionalMilestones: {
        selfRegulation: MetricTimeSeries;
        intimacy: MetricTimeSeries;
        twoWayCommunication: MetricTimeSeries;
        complexCommunication: MetricTimeSeries;
        emotionalIdeas: MetricTimeSeries;
        logicalThinking: MetricTimeSeries;
      };

      // 可扩展维度 - 根据每个孩子的独特情况动态添加
      customDimensions: {
        [dimensionKey: string]: MetricTimeSeries;
        // 例如：sensorySensitivity, eyeContactDuration,
        // spontaneousSmiles, verbalInitiation等
      };
    };

    // 微观观察记录库 - 捕捉每个细节
    microObservations: ObservationEvent[];
  };

  // 当前工作上下文
  currentContext: {
    recentTrends: object;  // AI识别的最新趋势
    attentionPoints: string[];  // 值得关注的亮点
    activeGoals: object[];  // 当前聚焦的目标
  };

  // 当前会话
  currentSession: {
    selectedGame?: object;
    guidanceLog?: object[];
    realTimeObservations?: ObservationEvent[];
    sessionSummary?: SessionSummary;
    parentFeedback?: object;
  };

  // 历史记录
  interventionHistory: Array<object>;
}

// 时序指标结构
interface MetricTimeSeries {
  metricId: string;
  metricName: string;
  description: string;

  // 数据点流 - 每次观察都会添加
  dataPoints: Array<{
    timestamp: string;
    value: number | string;
    source: 'assessment' | 'parentObservation' | 'videoAI' | 'gameSession';
    confidence: number;
    context?: string;
    evidence?: string[];
  }>;

  // 自动分析结果
  analysis?: {
    trend: 'improving' | 'stable' | 'declining' | 'fluctuating';
    rate: number;
    lastMilestone?: string;
    nextGoal?: string;
  };
}

// 微观观察事件
interface ObservationEvent {
  eventId: string;
  timestamp: string;
  eventType: 'behavior' | 'emotion' | 'communication' | 'social' | 'firstTime';
  description: string;
  significance: 'breakthrough' | 'improvement' | 'normal' | 'concern';
  evidence: {
    source: string;
    clips?: VideoClip[];
    transcript?: string;
  };
  aiInsight?: {
    category: string;
    impact: string;
    connection?: string;
  };
}
```

### 5.3 State流转示例

一次完整的干预流程会不断更新State：

```typescript
// 1. 初评估后
childTimeline.metrics.emotionalMilestones.eyeContact.dataPoints = [
  {timestamp: "2024-01-01", value: 2, source: "assessment"}
];

// 2. 第一次干预后
childTimeline.metrics.emotionalMilestones.eyeContact.dataPoints.push(
  {timestamp: "2024-01-15", value: 5, source: "videoAI"}
);

// 3. 第二次干预后（突破性进展）
childTimeline.metrics.emotionalMilestones.eyeContact.dataPoints.push(
  {timestamp: "2024-01-23", value: 8, source: "gameSession"}
);

childTimeline.microObservations.push({
  eventId: "obs_20240123_143022",
  timestamp: "2024-01-23T14:30:22Z",
  eventType: "firstTime",
  description: "孩子第一次主动递积木",
  significance: "breakthrough",
  evidence: {source: "video", clips: [{start: 142, end: 145}]}
});

// 4. 自动分析趋势
childTimeline.metrics.emotionalMilestones.eyeContact.analysis = {
  trend: "improving",
  rate: 0.22,
  lastMilestone: "2024-01-23:首次主动发起互动"
};

// 5. 更新关注点
currentContext.attentionPoints = [
  "🌟 突破：首次主动发起互动",
  "📈 双向沟通快速提升（+22%/月）"
];
```

---

## 6. 多Agent系统设计

### 6.1 Agent列表与职责

根据核心业务流程，系统设计以下Agent：

| Agent | 职责 | 对应流程步骤 | 输入 | 输出 |
|-------|------|-------------|------|------|
| **初评估Agent** | 建立孩子画像 | 第一步 | 医院报告/量表 | 多维度观察框架 |
| **推荐Agent** | 智能游戏推荐 | 第二步 | 孩子画像+最新观察 | 个性化游戏方案 |
| **实时指引Agent** | 游戏过程指导 | 第三步 | 游戏步骤+实时观察 | 语音提示+引导 |
| **观察捕获Agent** | 记录孩子表现 | 第三步（并行） | 快捷按钮+语音+视频 | 微观观察事件 |
| **视频分析Agent** | AI视频分析 | 第四步 | 录制视频 | 行为+情绪分析 |
| **总结Agent** | 单次干预汇总 | 第四步 | 所有游戏数据 | 成长快照 |
| **反馈表Agent** | 智能问卷生成 | 第五步 | 干预总结 | 个性化反馈表 |
| **记忆更新Agent** | Graphiti融合 | 第六步 | 新观察+反馈 | 更新后的记忆网络 |
| **再评估Agent** | 更新孩子画像 | 第六步 | 全部历史数据 | 进展报告+下一步计划 |
| **可视化Agent** | 成长故事呈现 | 辅助功能2 | 记忆数据 | 多维度可视化 |

### 6.2 核心Agent详解

#### Agent 1：初评估Agent（第一步）

**核心职责**：解读报告/量表，建立孩子的初始画像

**处理流程**：
1. 解析结构化数据（CARS-2、ADOS-2量表）
2. NLP分析质性描述（提取行为细节）
3. 动态创建观察维度
4. 设置变化检测阈值
5. 规划数据采集策略

**输出示例**：
```typescript
{
  childTimeline: {
    profile: {
      name: "辰辰",
      age: 2.5,
      diagnosis: "ASD轻度",
      interests: ["旋转物体", "水流"]
    },
    metrics: {
      emotionalMilestones: {
        selfRegulation: {dataPoints: [{timestamp: "2024-01-01", value: 3, source: "assessment"}]},
        eyeContact: {dataPoints: [{timestamp: "2024-01-01", value: 2, source: "assessment"}]}
      },
      customDimensions: {
        sensorySensitivity: MetricTimeSeries,  // 根据家长描述动态创建
        repetitiveBehaviors: MetricTimeSeries
      }
    }
  },
  currentContext: {
    attentionPoints: [
      "重点关注：眼神接触和情绪调节",
      "初期目标：建立情感联结，减少刻板行为"
    ]
  }
}
```

#### Agent 2：推荐Agent（第二步）

**核心职责**：基于孩子画像和最新观察，推荐个性化游戏

**推荐逻辑**：
```python
def recommend_games(state):
    # 1. 优先级排序（哪些能力需要重点提升）
    priority_scores = calculate_priority(state.recentTrends)

    # 2. RAG检索游戏库（匹配孩子兴趣和目标能力）
    candidates = rag_search(priority_scores, state.childTimeline.profile.interests)

    # 3. 多目标优化（效果+兴趣匹配度）
    for game in candidates:
        game.score = calculate_game_score(game, state, priority_scores)
        game.reasoning = generate_reasoning(game, state)

    # 4. 生成周计划或单次推荐
    return top_k(candidates, k=3)
```

**推荐理由透明化**：
```
推荐游戏：积木传递游戏

基于最近观察：
✓ 眼神接触正在改善（+15%/周），应保持动能
✓ 双向沟通仍是短板，需要强化
✓ 孩子对积木有兴趣，匹配度高

推荐目标：将眼神接触从"被动回应"提升到"主动发起"
```

#### Agent 3：实时指引Agent（第三步）

**核心职责**：游戏过程中语音引导 + 实时捕捉亮点

**工作模式**：
- 游戏前：语音播报目标、步骤、注意事项
- 游戏中：监听家长反馈，提供即时提示
- 推荐话术 vs 避免话术

**推荐话术**：
- "看看孩子会怎么做，跟随他的节奏"
- "哇，孩子有反应了！继续保持"
- "你做得很好，再等等看孩子会怎么回应"

**避免话术**：
- "看着妈妈/爸爸"（命令式）
- "这样做不对"（否定式）
- "快一点"（催促式）


#### Agent 4：观察捕获Agent（第三步，并行运行）

**核心职责**：在游戏过程中，实时记录孩子的微观表现

**三种记录方式**：

1. **快捷按钮**（零门槛）
```
游戏界面底部常驻按钮：
[😊 微笑] [👀 眼神] [🗣️ 出声] [🤝 互动] [😢 情绪]

家长点击 → AI自动记录时间戳和上下文
```

2. **语音记录**（最推荐）
```
家长说："今天玩积木的时候，辰辰突然抬头看了我一眼，大概有2秒钟"

AI生成结构化记录：
{
  timestamp: "2024-01-24 14:32",
  context: "积木游戏中",
  behavior: "主动眼神接触",
  duration: "约2秒",
  significance: "首次主动发起",
  tags: ["眼神接触", "主动互动", "突破"]
}
```

3. **智能引导式记录**（降低描述门槛）
```
系统：今天有什么想记录的吗？
家长：感觉孩子今天有点不一样
系统：能回忆一下是在什么场景下吗？
家长：洗澡的时候
系统：孩子在洗澡时有什么具体表现？
[展示选项，家长多选]
```

**输出**：微观观察事件流

#### Agent 5：视频分析Agent（第四步）

**核心职责**：AI分析游戏视频，提取行为和情绪数据

**分析维度**：
- 表情识别（微笑、哭泣、专注）
- 眼神追踪（眼神接触时长、频率）
- 肢体动作（主动互动、刻板行为）
- 声音分析（发声频率、语言尝试）

**输出示例**：
```typescript
{
  videoAnalysis: {
    duration: "15:23",
    highlights: [
      {time: "02:15", event: "主动眼神接触", duration: "3秒"},
      {time: "08:42", event: "微笑回应", confidence: 0.92},
      {time: "12:30", event: "主动递积木", significance: "breakthrough"}
    ],
    metrics: {
      eyeContactCount: 5,
      smileCount: 8,
      verbalAttempts: 2
    }
  }
}
```

#### Agent 6：总结Agent（第四步）

**核心职责**：融合所有数据，生成本次游戏的成长快照

**输入源**：
- 实时指引日志
- 观察捕获记录
- 视频分析结果

**输出示例**：
```typescript
{
  sessionSummary: {
    date: "2024-01-24",
    game: "积木传递游戏",
    duration: "15分钟",
    highlights: [
      "🌟 首次主动递积木（12:30）",
      "📈 眼神接触5次（比上次+2次）",
      "😊 微笑回应8次"
    ],
    concerns: [],
    overallAssessment: "孩子今天状态很好，主动互动明显增加",
    comparisonWithLast: "眼神接触频率提升40%"
  }
}
```

#### Agent 7：反馈表Agent（第五步）

**核心职责**：基于游戏总结，生成个性化反馈问题

**智能问卷生成**：
```typescript
// 根据总结中的亮点和关注点，动态生成问题
{
  feedbackForm: {
    questions: [
      {
        id: "q1",
        type: "rating",
        question: "今天孩子的眼神接触比平时多，你感觉到了吗？",
        scale: [1, 2, 3, 4, 5],
        labels: ["完全没注意到", "有一点", "明显感觉到"]
      },
      {
        id: "q2",
        type: "open",
        question: "孩子主动递积木时，你当时是什么感受？"
      },
      {
        id: "q3",
        type: "choice",
        question: "你觉得今天的游戏时长（15分钟）怎么样？",
        options: ["太短", "刚好", "太长"]
      }
    ]
  }
}
```

**人机协作暂停点**：
- 系统生成反馈表后，进入等待状态
- 家长填写完成后，系统恢复运行

#### Agent 8：记忆更新Agent（第六步）

**核心职责**：将新数据融入Graphiti记忆网络

**处理流程**：
```python
async def update_memory(state):
    graphiti = get_graphiti_client()

    # 1. 创建记忆节点
    for obs in state.currentSession.microObservations:
        node_id = await graphiti.add_node(obs)

        # 2. 建立关联关系
        relationships = await find_relationships(obs, state)
        for rel in relationships:
            await graphiti.add_edge(node_id, rel.target, rel.type)

    # 3. 更新时序指标
    for metric in state.childTimeline.metrics:
        trend_analysis = await graphiti.analyze_trend(metric)
        state.childTimeline.metrics[metric].analysis = trend_analysis

    # 4. 检测里程碑
    milestones = await detect_milestones(state)

    # 5. 推断因果关联
    causal_links = await infer_causality(state)

    return state
```

#### Agent 9：再评估Agent（第六步）

**核心职责**：综合历史数据，更新孩子画像，制定下一步计划

**输出示例**：
```typescript
{
  reEvaluation: {
    progressReport: {
      since_baseline: {
        eyeContact: '+65%',
        twoWayCommunication: '+40%'
      },
      overallVelocity: '中速稳步提升'
    },
    dimensionHealth: {
      eyeContact: {score: 8.5, status: 'excellent', action: 'maintain'},
      emotionalRegulation: {score: 5.8, status: 'needs_attention', action: 'change_strategy'}
    },
    nextSteps: [
      {
        dimension: 'eyeContact',
        action: 'maintain',
        strategy: '继续当前游戏类型，保持干预频率'
      },
      {
        dimension: 'emotionalRegulation',
        action: 'change_strategy',
        suggestedGames: ['情绪脸谱游戏', '深压活动']
      }
    ]
  }
}
```

**闭环触发**：
- 如果某个维度需要调整 → 返回推荐Agent，推荐新游戏
- 如果整体良好 → 继续当前计划

#### Agent 10：可视化Agent（辅助功能2）

**核心职责**：将孩子的成长数据可视化呈现

**可视化类型**：
1. **多维度雷达图**：展示六大情绪发展里程碑的当前水平
2. **时间线**：标注重要里程碑和突破性事件
3. **趋势图**：展示各项指标的变化曲线
4. **热力图**：展示微观进步的密集程度
5. **因果网络图**：展示干预与效果的关联

---

## 7. 微观变化捕捉系统

### 7.1 系统定位

**核心理念**：在家长已经与孩子建立情感联结的基础上，作为敏锐的记录者和专业分析师。

**AI的角色边界**：
- ✅ **记录**：把家长的口语化描述转化为专业记录
- ✅ **分析**：用专业知识识别肉眼看不到的规律
- ✅ **提醒**：提示家长可能遗漏的观察维度
- ❌ **不替代**：不替代家长的观察和情感联结
- ❌ **不主导**：不主动"诊断"或"下结论"

### 7.2 三种分析能力

#### 分析1：首次出现检测（里程碑识别）

**场景**：家长每天记录，但不知道哪些是"突破"

**AI分析**：
```javascript
// 输入：30天的观察记录
[
  {date: "01-01", behavior: "被动眼神接触", ...},
  {date: "01-15", behavior: "被动眼神接触", ...},
  {date: "01-23", behavior: "主动眼神接触", ...}  // AI识别这是里程碑！
]

// AI输出：
{
  milestoneDetected: {
    behavior: "主动眼神接触",
    firstOccurrence: "2024-01-23",
    significance: "breakthrough",
    context: "积木游戏中，递积木时看向家长",
    comparison: "此前30天只有被动眼神接触",
    celebrationMessage: "🌟 这是孩子的第一次主动眼神接触！这是情感联结的重要突破"
  }
}
```

**呈现给家长**：
```
┌─────────────────────────────────┐
│ 🎉 今天有个重要发现！           │
├─────────────────────────────────┤
│ 辰辰第一次主动和你眼神接触了！   │
│                                 │
│ 这是我们记录的第15次游戏，      │
│ 此前他都是被动看你，            │
│ 今天他主动看向你——              │
│ 这是情感联结的重要突破！🌟      │
│                                 │
│ [查看历史记录] [分享给医生]     │
└─────────────────────────────────┘
```

#### 分析2：频率与趋势分析

**场景**：家长觉得"孩子好像没什么变化"

**AI分析**：
```javascript
{
  metric: "主动微笑",
  timeline: [
    {week1: 平均0.5次/游戏},
    {week2: 平均1.2次/游戏},
    {week3: 平均2.1次/游戏},
    {week4: 平均3.5次/游戏}
  ],
  trend: "improving",
  growthRate: "+140% over 4 weeks",
  insight: "微笑频率每周稳定增长，孩子的情绪表达能力正在快速提升"
}
```

**呈现给家长**：
```
┌─────────────────────────────────┐
│ 📈 孩子正在进步！                │
├─────────────────────────────────┤
│ 主动微笑                        │
│ Week 1  ▓░░░░  0.5次/游戏       │
│ Week 2  ▓▓░░░  1.2次/游戏       │
│ Week 3  ▓▓▓▓░  2.1次/游戏       │
│ Week 4  ▓▓▓▓▓  3.5次/游戏       │
│                                 │
│ 🌟 4周内增长了140%！            │
│ 孩子的情绪表达能力正在提升      │
│                                 │
│ [查看详细数据]                  │
└─────────────────────────────────┘
```

#### 分析3：关联分析（识别因果）

**场景**：家长不知道某种行为为什么出现/消失

**AI分析**：
```javascript
{
  correlation: {
    when: ["游戏时间<15分钟", "上午时段"],
    then: "孩子更容易出现主动互动",
    confidence: 0.82,
    insight: "孩子在上午精力充沛时，且游戏时长不超过15分钟时，互动意愿更强",
    suggestion: "可以尝试将重点游戏安排在上午，控制在15分钟内"
  }
}
```

**呈现给家长**：
```
┌─────────────────────────────────┐
│ 💡 发现了一个规律！              │
├─────────────────────────────────┤
│ 当游戏在上午进行，且不超过15分钟 │
│ 时，辰辰的主动互动会增加60%      │
│                                 │
│ 建议：                          │
│ • 把重点游戏安排在上午          │
│ • 单次游戏控制在15分钟内        │
│                                 │
│ [采纳建议] [继续观察]           │
└─────────────────────────────────┘
```

### 7.3 行动建议闭环

#### 场景1：发现进步 → 保持动能

**触发条件**：AI检测到某个维度有显著改善

**系统建议**：
```
┌─────────────────────────────────┐
│ 🎯 下一步建议                    │
├─────────────────────────────────┤
│ 眼神接触正在快速进步！继续保持   │
│                                 │
│ 本周安排：                      │
│ ✅ 继续积木传递游戏（3次/周）   │
│ ✅ 每次眼神接触时微笑回应        │
│ ✅ 尝试在游戏中增加等待时间      │
│    （给孩子主动发起的机会）      │
│                                 │
│ 预期目标：                      │
│ 主动眼神接触达到5次/游戏        │
│                                 │
│ [采纳建议] [自定义计划]          │
└─────────────────────────────────┘
```

#### 场景2：发现平台期 → 调整策略

**触发条件**：某个维度连续3周无明显变化

**系统建议**：
```
┌─────────────────────────────────┐
│ ⚠️ 双向沟通进入平台期            │
├─────────────────────────────────┤
│ 过去3周保持在1.2次/游戏，        │
│ 建议尝试新游戏类型               │
│                                 │
│ 推荐游戏1：躲猫猫游戏 ⭐优先     │
│ 原理：利用孩子对'消失-出现'的    │
│       兴趣，引导他主动参与       │
│                                 │
│ [查看玩法] [加入计划]            │
│                                 │
│ 推荐游戏2：传递物品游戏          │
│ 原理：建立'递过来-还给我'的      │
│       双向沟通模式               │
│                                 │
│ [查看玩法] [加入计划]            │
└─────────────────────────────────┘
```

#### 场景3：发现新兴趣点 → 立即利用

**触发条件**：识别到新的、稳定出现的兴趣信号

**系统建议**：
```
┌─────────────────────────────────┐
│ ✨ 发现新兴趣：水流！            │
├─────────────────────────────────┤
│ 从最近的记录中，我们发现辰辰    │
│ 对水流表现出强烈且稳定的兴趣    │
│                                 │
│ 证据：                          │
│ • 洗澡时盯着水龙头5秒+          │
│ • 用手接水，重复3次             │
│ • 关水后哭闹                    │
│                                 │
│ 建议利用这一兴趣：              │
│                                 │
│ 🎮 水上漂流游戏                 │
│ 目标：培养共同注意力            │
│ 玩法：在浴缸放漂浮玩具，一起    │
│       推玩具、看它移动          │
│                                 │
│ [加入下周计划]                  │
└─────────────────────────────────┘
```


---

## 8. LangGraph工作流编排

### 8.1 完整工作流架构

整个干预流程是一个**LangGraph有向循环图**，严格对应核心业务流程：

```
┌─────────────┐
│ 初评估Agent │ ← 第一步：建立孩子画像
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 推荐Agent   │ ← 第二步：推荐地板游戏
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│ 开始游戏会话                     │ ← 第三步：实施地板游戏
│                                 │
│ ┌─────────────┐  ┌────────────┐│
│ │实时指引Agent│  │观察捕获Agent││
│ │(主线程)     │  │(并行运行)  ││
│ └─────────────┘  └────────────┘│
└──────┬──────────────────────────┘
       │
       ▼ (家长点击结束)
┌─────────────┐
│ 结束会话    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│ 视频分析Agent + 总结Agent        │ ← 第四步：总结游戏过程
│ (并行处理)                       │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────┐
│反馈表Agent  │ ← 第五步：生成反馈表
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│ [人机协作暂停点]    │ ← 等待家长填写反馈
└──────┬──────────────┘
       │ (家长提交)
       ▼
┌─────────────────────────────────┐
│ 记忆更新Agent + 再评估Agent      │ ← 第六步：更新孩子画像
│ (串行处理)                       │
└──────┬──────────────────────────┘
       │
   ┌───┴────┐
   │ 条件分支│ ← 第七步：形成闭环
   ├─► 需要调整 ──> 推荐Agent (返回第二步)
   │
   └─► 继续当前 ──> 可视化Agent
       │
       ▼
┌─────────────┐
│ END         │ 保存Checkpoint
└─────────────┘
```

### 8.2 关键特性实现

#### 特性1：人机协作暂停点

```typescript
// 反馈表节点
async function waitForFeedbackAgent(state) {
  const feedbackForm = await generateFeedbackForm(state);
  await saveCheckpoint(state);

  return {
    ...state,
    currentSession: { feedbackForm, feedbackStatus: 'pending' },
    waitForUser: true  // 触发暂停
  };
}

// 条件边
workflow.addConditionalEdges(
  'wait_feedback',
  (state) => state.waitForUser ? 'pause' : 'continue',
  { pause: 'pause_node', continue: 'update_memory' }
);

// 恢复API
app.post('/api/feedback/:sessionId/submit', async (req, res) => {
  const savedState = await loadCheckpoint(sessionId);
  savedState.currentSession.parentFeedback = req.body;
  savedState.waitForUser = false;

  const result = await workflow.invoke(savedState, {
    configurable: { thread_id: sessionId }
  });

  res.json(result);
});
```

#### 特性2：条件分支（闭环触发）

```typescript
workflow.addConditionalEdges(
  're_evaluate',
  (state) => {
    const needsAdjustment = Object.values(
      state.reEvaluation.dimensionHealth
    ).some(d => d.status === 'needs_attention');

    return needsAdjustment ? 'recommend_new' : 'continue_current';
  },
  {
    recommend_new: 'recommend_games',  // 返回第二步
    continue_current: 'generate_visualization'
  }
);
```

#### 特性3：Checkpoint机制（支持中断恢复）

```typescript
import { MemorySaver } from "@langchain/langgraph-checkpoint";

const checkpointer = new MemorySaver();
const app = workflow.compile({ checkpointer });

// 运行（带thread_id）
const result = await app.invoke(initialState, {
  configurable: { thread_id: 'intervention_session_20240123' }
});

// 从checkpoint恢复
const resumed = await app.invoke(null, {
  configurable: { thread_id: 'intervention_session_20240123' }
});
```

### 8.3 State流转完整示例

一次完整的干预流程State变化：

```
1. 初评估 → 建立childTimeline（metrics + microObservations）
2. 推荐 → currentContext.selectedGames
3. 游戏开始 → currentSession初始化
4. 实时指引 + 观察（并行）→ currentSession.guidanceLog + microObservations
5. 结束游戏 → currentSession.endTime + videoPath
6. 视频分析 + 总结（并行）→ currentSession.videoAnalysis + sessionSummary
7. 生成反馈表 → currentSession.feedbackForm + waitForUser=true
8. [暂停] → 家长填写反馈
9. 恢复 → 记忆更新 → childTimeline新增dataPoints + analysis更新
10. 再评估 → currentContext.reEvaluation + nextSteps
11. 条件分支 → 如需调整返回推荐，否则可视化
12. 保存Checkpoint → END
```

---

## 9. 技术栈与实现

### 9.1 后端技术栈

```json
{
  "core": {
    "runtime": "Node.js >= 18",
    "framework": "Express.js ^4.18",
    "language": "TypeScript ^5.0"
  },
  "langchain": {
    "@langchain/core": "^0.1.0",
    "@langchain/langgraph": "^0.0.20",
    "@langchain/openai": "^0.0.10"
  },
  "ai_services": {
    "llm": "OpenAI GPT-4",
    "embedding": "OpenAI text-embedding-3-small",
    "vision": "OpenAI GPT-4V",
    "speech": "阿里云语音服务"
  },
  "database": {
    "sqlite": "better-sqlite3 ^9.0",
    "vector_db": "pgvector + PostgreSQL",
    "cache": "redis ^7.0 (可选)"
  },
  "graphiti": {
    "@graphiti/core": "^0.1.0"
  },
  "video_processing": {
    "ffmpeg": "^1.1.0"
  },
  "authentication": {
    "bcrypt": "^5.1.0",
    "jsonwebtoken": "^9.0.0",
    "aliyun-sms": "^2.0.0"
  }
}
```

### 9.2 数据库设计

#### SQLite表结构

```sql
-- 用户表
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone_number VARCHAR(20) UNIQUE NOT NULL,
  nickname VARCHAR(50),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 孩子档案表
CREATE TABLE child_profiles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  child_name VARCHAR(50) NOT NULL,
  birth_date DATE NOT NULL,
  diagnosis TEXT,
  custom_dimensions TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 微观观察记录表
CREATE TABLE micro_observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  child_id INTEGER NOT NULL,
  session_id INTEGER,
  timestamp DATETIME NOT NULL,
  event_type VARCHAR(50),
  description TEXT NOT NULL,
  significance VARCHAR(20),
  source VARCHAR(20),
  evidence TEXT,
  ai_insight TEXT,
  FOREIGN KEY (child_id) REFERENCES child_profiles(id)
);

-- 时序指标数据表
CREATE TABLE metric_datapoints (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  child_id INTEGER NOT NULL,
  metric_id VARCHAR(100) NOT NULL,
  timestamp DATETIME NOT NULL,
  value TEXT NOT NULL,
  value_type VARCHAR(10),
  source VARCHAR(20),
  confidence REAL,
  FOREIGN KEY (child_id) REFERENCES child_profiles(id)
);

-- 干预会话表
CREATE TABLE intervention_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  child_id INTEGER NOT NULL,
  session_date DATETIME NOT NULL,
  game_id VARCHAR(50),
  status VARCHAR(20),
  video_path TEXT,
  video_analysis_status VARCHAR(20),
  FOREIGN KEY (child_id) REFERENCES child_profiles(id)
);
```

#### PostgreSQL + pgvector

```sql
-- 游戏知识库表
CREATE TABLE games (
  id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(50),
  target_dimensions TEXT[],
  themes TEXT[],
  embedding vector(1536)
);

-- 向量相似度搜索索引
CREATE INDEX games_embedding_idx
ON games USING ivfflat (embedding vector_cosine_ops);
```

### 9.3 核心API设计

```typescript
// ===== 用户认证 =====
POST   /api/auth/send-code        // 发送验证码
POST   /api/auth/verify-login     // 验证码登录

// ===== 评估管理（第一步）=====
POST   /api/assessments/import    // 导入医院报告
POST   /api/assessments/questionnaire  // 填写内置量表

// ===== 游戏推荐（第二步）=====
POST   /api/recommendations       // 获取游戏推荐

// ===== 干预会话（第三步）=====
POST   /api/sessions              // 创建新会话
PUT    /api/sessions/:id/start    // 开始会话
PUT    /api/sessions/:id/end      // 结束会话

// ===== 实时指引（第三步）=====
WebSocket /api/ws/guidance/:sessionId

// ===== 观察记录（第三步）=====
POST   /api/observations/voice    // 语音记录上传
POST   /api/observations/quick    // 快捷按钮记录
POST   /api/observations/guided   // 引导式记录会话

// ===== 视频处理（第四步）=====
POST   /api/videos/upload         // 上传游戏视频
GET    /api/videos/:id/status     // 查询分析状态

// ===== 反馈表（第五步）=====
POST   /api/feedback/:sessionId/submit   // 提交反馈

// ===== 观察分析（辅助功能1）=====
GET    /api/observations/analysis/latest // 获取最新分析
GET    /api/observations/milestones      // 获取里程碑列表
GET    /api/observations/trends/:metric  // 获取趋势分析

// ===== 兴趣图谱（辅助功能1）=====
GET    /api/interests/profile     // 获取兴趣画像
POST   /api/interests/confirm     // 确认潜在兴趣

// ===== 可视化（辅助功能2）=====
GET    /api/visualizations/:childId/radar
GET    /api/visualizations/:childId/timeline
GET    /api/visualizations/:childId/report

// ===== 导出 =====
GET    /api/export/:childId/report        // 导出PDF报告
GET    /api/export/:childId/medical       // 导出医学报告
```

---

## 10. 前端架构方案

### 10.1 技术选型

```
React 18 + TypeScript
  ↓
Ant Design Mobile (移动端优先)
  ↓
Zustand (本地状态) + React Query (服务端状态)
  ↓
Vite (快速构建)
```

### 10.2 项目结构

```
src/
├── pages/
│   ├── Auth/                    # 登录注册
│   ├── Dashboard/               # 主页
│   ├── Assessment/              # 评估（第一步）
│   ├── Recommendations/         # 游戏推荐（第二步）
│   ├── Intervention/            # 干预执行（第三步，核心）
│   │   └── GameSession.tsx     # 游戏会话页面
│   ├── Feedback/                # 反馈表（第五步）
│   ├── Observation/             # 观察记录（辅助功能1）
│   ├── Progress/                # 进展可视化（辅助功能2）
│   └── Profile/                 # 个人中心
│
├── components/
│   ├── intervention/
│   │   ├── VideoRecorder.tsx
│   │   ├── VoicePlayer.tsx
│   │   └── FeedbackButtons.tsx
│   ├── observation/
│   │   ├── QuickRecordBar.tsx
│   │   ├── VoiceRecorder.tsx
│   │   └── GuidedRecordModal.tsx
│   └── visualization/
│       ├── RadarChart.tsx
│       ├── TimelineView.tsx
│       └── TrendChart.tsx
│
├── stores/
│   ├── authStore.ts
│   ├── sessionStore.ts
│   └── observationStore.ts
│
├── services/
│   ├── api.ts
│   ├── intervention.ts
│   ├── observation.ts
│   └── progress.ts
│
└── hooks/
    ├── useWebSocket.ts
    ├── useVideoRecorder.ts
    └── useObservationCapture.ts
```

### 10.3 核心页面设计

#### 页面1：游戏干预页面（第三步）

```
┌─────────────────────────────┐
│ [返回]  积木传递游戏     [≡] │
├─────────────────────────────┤
│ 🎯 目标：建立情感联结        │
│ ⏱️ 已进行：15分钟            │
├─────────────────────────────┤
│ [语音指引播放中...]          │
│ 💬 跟随孩子的节奏            │
├─────────────────────────────┤
│ 快捷记录：                  │
│ ┌───┐ ┌───┐ ┌───┐ ┌───┐    │
│ │😊 │ │😢 │ │👀 │ │🗣️ │    │
│ └───┘ └───┘ └───┘ └───┘    │
│  笑了  哭了 眼神  说话      │
├─────────────────────────────┤
│ [🎥 录制中... 00:15:23]     │
├─────────────────────────────┤
│ [⏸️ 暂停]  [⏹️ 结束游戏]    │
└─────────────────────────────┘
```

#### 页面2：反馈表页面（第五步）

```
┌─────────────────────────────┐
│ 游戏反馈   [保存草稿]        │
├─────────────────────────────┤
│ 今天的游戏总结：             │
│ 🌟 首次主动递积木            │
│ 📈 眼神接触5次（+2次）       │
│ 😊 微笑回应8次               │
├─────────────────────────────┤
│ 1. 今天孩子的眼神接触比平时  │
│    多，你感觉到了吗？        │
│    ○ 完全没注意到            │
│    ● 有一点                  │
│    ○ 明显感觉到              │
│                             │
│ 2. 孩子主动递积木时，你当时  │
│    是什么感受？              │
│    [文本输入框...]          │
│                             │
│ 3. 你觉得今天的游戏时长      │
│    （15分钟）怎么样？        │
│    ○ 太短 ● 刚好 ○ 太长     │
├─────────────────────────────┤
│ [提交反馈]                  │
└─────────────────────────────┘
```

#### 页面3：进展可视化页面（辅助功能2）

```
┌─────────────────────────────┐
│ 辰辰的成长历程   [导出报告]  │
├─────────────────────────────┤
│ 📊 核心维度雷达图           │
│ ┌─────────────────────┐     │
│ │      ╱╲            │     │
│ │    ╱  ╲    社交    │     │
│ │   ╱────╲           │     │
│ │  沟通  情绪        │     │
│ │   ╲────╱           │     │
│ │    ╲  ╱            │     │
│ │      ╲╱            │     │
│ │ [▶️播放1个月变化]   │     │
│ └─────────────────────┘     │
│                             │
│ 🌟 里程碑时间线             │
│ 2024-01-23 ★ 首次主动互动   │
│ ┃          [视频▶️]         │
│ 2024-01-15 ★ 眼神接触3秒    │
│                             │
│ 📈 微观进步热力图            │
│ ┌─────────────────────┐     │
│ │ 微笑次数   ▓▓▓▓▓░░    │     │
│ │ 眼神时长   ▓▓▓▓░░░    │     │
│ │ 主动互动   ▓▓▓░░░░    │     │
│ └─────────────────────┘     │
└─────────────────────────────┘
```

### 10.4 WebSocket集成

```typescript
// hooks/useWebSocket.ts
export const useInterventionWebSocket = (sessionId: string) => {
  const [guidance, setGuidance] = useState(null);
  const [observations, setObservations] = useState([]);

  useEffect(() => {
    const socket = io(`${API_URL}/guidance/${sessionId}`);

    // 接收实时指引
    socket.on('guidance_step', (step) => {
      setGuidance(step);
      speakText(step.instruction);  // 语音播报
    });

    // 接收AI观察提示
    socket.on('observation_detected', (obs) => {
      showToast({ message: obs.description });
    });

    // 接收庆祝提示
    socket.on('celebrate', ({ message }) => {
      showConfetti();
      showToast({ message, type: 'success' });
    });

    return () => socket.disconnect();
  }, [sessionId]);

  const sendFeedback = (feedback) => {
    socket.emit('parent_feedback', { sessionId, feedback });
  };

  return { guidance, sendFeedback };
};
```


### 10.5 视频录制方案

```typescript
// hooks/useVideoRecorder.ts
export const useVideoRecorder = () => {
  const [isRecording, setIsRecording] = useState(false);

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },  // 后置摄像头
      audio: true
    });

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start(1000);  // 每秒一个切片
    setIsRecording(true);
  };

  const stopRecording = async () => {
    const blob = new Blob(chunks, { type: 'video/webm' });
    await uploadVideo(blob);
    setIsRecording(false);
  };

  return { isRecording, startRecording, stopRecording };
};
```

---

## 11. 部署架构

### 11.1 整体部署架构

```
┌─────────────────────────────────┐
│           用户层                │
│  ┌──────────┐    ┌──────────┐  │
│  │ 家长手机端│    │  医生端  │  │
│  │ (浏览器) │    │  (预留)  │  │
│  └─────┬────┘    └──────────┘  │
└────────┼────────────────────────┘
         │ HTTPS
┌────────▼────────────────────────┐
│         接入层                   │
│  ┌─────────────────────────┐   │
│  │  Nginx (反向代理+SSL)   │   │
│  └────────────┬────────────┘   │
└───────────────┼─────────────────┘
                │
      ┌─────────┼─────────┐
      │         │         │
┌─────▼───┐ ┌──▼──────┐ ┌─▼────────┐
│前端容器  │ │后端容器  │ │PostgreSQL│
│ (React) │ │(Node.js) │ │+pgvector │
└─────────┘ └──┬──────┘ └──────────┘
               │
      ┌────────┼────────┐
      │        │        │
┌─────▼──┐ ┌──▼────┐ ┌──▼──────┐
│ SQLite │ │Graphiti│ │ Redis   │
└────────┘ │记忆   │ │ (可选)  │
           └────────┘ └─────────┘
```

### 11.2 Docker Compose配置

```yaml
version: '3.8'

services:
  # 前端容器
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    environment:
      - VITE_API_URL=https://api.yourdomain.com

  # 后端容器
  backend:
    build: ./backend
    ports:
      - "4000:4000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=/app/data/database.db
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    depends_on:
      - postgres

  # PostgreSQL + pgvector
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_USER=graphiti
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=graphiti
    volumes:
      - postgres_data:/var/lib/postgresql/data

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
```

### 11.3 部署步骤

#### 开发期（内网穿透）

```bash
# 1. 本地启动
cd backend && npm run dev  # localhost:4000
cd frontend && npm run dev  # localhost:3000

# 2. frp内网穿透
# 客户端配置
[common]
server_addr = your-cloud-server-ip
server_port = 7000

[web1]
type = http
local_port = 3000
custom_domains = dev.yourdomain.com

[api]
type = http
local_port = 4000
custom_domains = api-dev.yourdomain.com

# 3. 启动frp
./frpc -c frpc.ini
```

#### 生产环境（云服务器）

```bash
# 1. 准备服务器
# 安装Docker和Docker Compose
# 配置域名和SSL证书

# 2. 构建并启动
docker-compose build
docker-compose up -d

# 3. 查看日志
docker-compose logs -f backend

# 4. 数据备份（定时任务）
crontab -e
# 0 2 * * * /path/to/backup-script.sh
```

### 11.4 性能优化

**前端优化**：
- 代码分割（React.lazy）
- 图片懒加载、WebP格式
- React Query缓存（5分钟staleTime）
- PWA支持（离线可用）

**后端优化**：
- 视频处理队列（Bull + Redis，并发3）
- Redis缓存热点数据（1小时TTL）
- 数据库连接池
- 响应压缩（gzip）

### 11.5 安全性考虑

```typescript
// 1. JWT认证
app.use(authenticateToken);

// 2. 数据验证
const schema = Joi.object({
  childName: Joi.string().required(),
  age: Joi.number().min(0).max(18).required()
});

// 3. 敏感数据脱敏
const maskedPhone = phone.replace(/(\d{3})\d{4}(\d{4})/, '$1****$2');

// 4. 视频文件安全
// - 病毒扫描
// - 访问权限控制
// - 定期清理

// 5. 隐私保护
// - 符合《个人信息保护法》
// - 家长同意书
// - 数据匿名化
```

---

## 12. 实施计划

### 12.1 MVP阶段（3个月）

**目标**：验证核心价值，快速迭代

**范围**：
- ✅ 简化账号系统（手机号登录）
- ✅ 初评估Agent（导入医院报告）
- ✅ 推荐Agent（自建知识库，50个游戏）
- ✅ 实时指引Agent（语音交互）
- ✅ 观察捕获Agent（快捷按钮+语音记录）
- ✅ 视频录制+上传+异步分析
- ✅ 总结Agent+反馈表
- ✅ 记忆更新+再评估
- ✅ 基础可视化（雷达图、时间线）
- ✅ 首次出现检测（里程碑）
- ✅ 基础趋势分析
- ❌ 暂不实现：实时视频分析、医生端、引导式记录、复杂关联分析

**技术栈简化**：
- AI服务：OpenAI API（快速开发）
- 视频分析：基础版（表情识别）
- 部署：内网穿透（本地开发）

### 12.2 V1.0阶段（6个月）

**新增功能**：
- ✅ 实时视频分析Agent
- ✅ 引导式记录
- ✅ 关联分析和因果推断
- ✅ 兴趣演变追踪
- ✅ 智能观察提醒（"今天该关注什么"）
- ✅ 高级可视化（热力图、因果网络）
- ✅ 导出医学报告（PDF）
- ✅ 数据备份与恢复
- ✅ 性能优化（队列、缓存）

**技术升级**：
- 考虑本地化AI模型（降低成本）
- Docker生产部署
- SSL证书配置

### 12.3 V2.0阶段（12个月）

**医生端**：
- ✅ 独立医生界面
- ✅ 批量查看患儿档案
- ✅ 在线指导反馈

**高级功能**：
- ✅ 多患儿管理（一个家庭多个孩子）
- ✅ 家长社区（经验分享）
- ✅ 康复机构协作（机构账号）

### 12.4 开发里程碑

| 阶段 | 时间 | 交付物 | 验收标准 |
|------|------|--------|---------|
| 需求确认 | 第1周 | 需求文档 | 痛点明确、方案可行 |
| 架构设计 | 第2周 | 设计文档 | 本文档 |
| 环境搭建 | 第3周 | 开发环境 | LangGraph工作流跑通 |
| Agent开发 | 第4-8周 | 10个Agent | 单元测试通过 |
| 前端开发 | 第6-10周 | Web应用 | 核心页面可用 |
| 联调测试 | 第11周 | 测试报告 | 主要bug修复 |
| MVP发布 | 第12周 | 可演示系统 | 家长可完整使用 |

### 12.5 核心开发任务清单

#### 第一阶段：基础架构（第3周）

- [ ] 搭建Node.js + Express项目
- [ ] 配置TypeScript
- [ ] 集成LangGraph
- [ ] 配置SQLite数据库
- [ ] 配置PostgreSQL + pgvector
- [ ] 集成Graphiti
- [ ] 配置OpenAI API
- [ ] 搭建React + Vite项目
- [ ] 配置Ant Design Mobile

#### 第二阶段：核心Agent开发（第4-8周）

**第一步：评估**
- [ ] 初评估Agent（解析报告/量表）
- [ ] 动态创建观察维度
- [ ] 建立初始State

**第二步：推荐**
- [ ] 游戏知识库（50个游戏）
- [ ] RAG检索实现
- [ ] 推荐Agent（优先级排序+匹配）

**第三步：实施**
- [ ] 实时指引Agent（语音播报）
- [ ] 观察捕获Agent（快捷按钮+语音）
- [ ] WebSocket实时通信
- [ ] 视频录制功能

**第四步：总结**
- [ ] 视频分析Agent（基础版）
- [ ] 总结Agent（融合数据）

**第五步：反馈**
- [ ] 反馈表Agent（智能问卷生成）
- [ ] 人机协作暂停点

**第六步：再评估**
- [ ] 记忆更新Agent（Graphiti融合）
- [ ] 再评估Agent（更新画像）
- [ ] 首次出现检测
- [ ] 趋势分析

**第七步：闭环**
- [ ] 条件分支逻辑
- [ ] Checkpoint机制

#### 第三阶段：前端开发（第6-10周）

- [ ] 登录注册页面
- [ ] 主页（Dashboard）
- [ ] 评估页面（导入报告/填写量表）
- [ ] 游戏推荐页面
- [ ] 游戏干预页面（核心）
  - [ ] 语音指引播放
  - [ ] 快捷记录按钮
  - [ ] 视频录制
- [ ] 反馈表页面
- [ ] 观察记录页面
- [ ] 进展可视化页面
  - [ ] 雷达图
  - [ ] 时间线
  - [ ] 趋势图

#### 第四阶段：联调测试（第11周）

- [ ] 完整流程测试
- [ ] 性能测试
- [ ] 安全测试
- [ ] 用户体验测试

#### 第五阶段：MVP发布（第12周）

- [ ] 部署到测试环境
- [ ] 用户试用
- [ ] 收集反馈
- [ ] 迭代优化

---

## 附录

### A. 核心设计原则总结

1. **以核心流程为主线**
   - 系统围绕"评估→推荐→实施→总结→反馈→再评估"的闭环设计
   - 所有功能都服务于这个核心流程

2. **家长是主角，AI是助手**
   - 家长建立情感联结，AI负责记录和分析
   - AI不会"自说自话"下结论，而是呈现证据让家长判断

3. **记录门槛极低**
   - 语音、快捷按钮、引导式，多种方式适配不同场景
   - 哪怕只有一个模糊印象，也能开始记录

4. **让看不见的变可见**
   - 首次出现检测 → 让家长知道这是里程碑
   - 趋势分析 → 让家长看到"没变化"其实是"慢速进步"
   - 关联分析 → 让家长发现肉眼看不到的规律

5. **从记录到行动的闭环**
   - 不是为了记录而记录
   - 每个分析都导向具体的下一步建议
   - 让观察真正服务于干预

6. **动态适配每个孩子**
   - 不是固定的字段，而是活的时间线
   - 支持个性化维度扩展
   - 每个孩子都有独特的成长轨迹

### B. 参考文献资源

文档中引用的研究文献和专业知识来源：
- 斯坦利·格林斯潘《地板时光：如何帮助孤独症及相关障碍儿童沟通与思考》
- 南京市儿童医院康复医学科《儿童孤独症谱系障碍综合康复技术》
- 贾美香《探寻孤独症干预的系统破局》
- 佘丽、袁晓《"地板时光"在自闭症儿童家庭干预中的应用》

### C. 技术文档参考

- LangGraph官方文档：https://langchain-ai.github.io/langgraph/
- Graphiti文档：https://github.com/getzep/graphiti
- pgvector文档：https://github.com/pgvector/pgvector
- OpenAI API文档：https://platform.openai.com/docs

### D. 联系方式

- 项目负责人：[待定]
- 技术负责人：[待定]
- 邮箱：[待定]

---

**文档结束**

本文档详细描述了ASD地板时光干预辅助系统的完整设计方案，从核心业务流程出发，涵盖了痛点分析、系统架构、Agent设计、微观变化捕捉、工作流编排、技术实现、前端设计、部署方案和实施计划。系统的核心理念是**围绕"评估→推荐→实施→总结→反馈→再评估"的闭环，通过AI多Agent协同，让家长能够像专业治疗师一样精准干预，同时敏锐捕捉每个孩子的微小成长细节**。
