# ASD 地板时光干预辅助系统 - 架构设计文档

**文档日期**：2026-01-30  
**版本**：v2.0  
**状态**：实施中

---

## 1. 核心架构原则

### 1.1 数据存储职责划分

系统采用**双存储架构**：SQLite + Graphiti（Neo4j）

#### SQLite：结构化数据存储
- **孩子档案**（ChildProfile）：姓名、年龄、诊断、发展维度基线等
- **游戏方案**（GamePlan）：推荐的游戏详细方案
- **会话记录**（GameSession）：游戏实施的完整记录
- **周计划**（WeeklyPlan）：7天游戏序列
- **用户设置**：系统配置、偏好设置

#### Graphiti（Neo4j）：时序记忆图谱
- **Person 节点**：所有参与者（孩子、家长、老师、朋友等）
- **Behavior 节点**：观察到的行为事件（时序记录）
- **Object 节点**：玩具、物品等实体对象
- **InterestDimension 节点**：8类兴趣维度（固定节点）
- **FunctionDimension 节点**：33个功能维度（固定节点）
- **FloorTimeGame 节点**：游戏总结和关键时刻
- **ChildAssessment 节点**：评估结果快照

### 1.2 为什么这样划分？

**SQLite 存储"是什么"**：
- 孩子的基本信息、当前状态
- 游戏方案的完整内容
- 会话的结构化数据

**Graphiti 存储"发生了什么"**：
- 行为的时序记录
- 维度的变化趋势
- 关系的演化过程

---

## 2. 核心节点定义

### 2.1 Person 节点（Graphiti）

```python
{
    "person_id": "child_001",
    "person_type": "child",  # child/parent/teacher/peer/sibling/other
    "name": "辰辰",
    "role": "patient",
    "basic_info": {
        "age": "3岁6个月",
        "gender": "male",
        "diagnosis": "ASD轻度"
    },
    "created_at": "2024-01-10"
}
```

**用途**：
- 建立关系图谱（谁参与了哪些行为、游戏）
- 记录参与者的基本信息
- 支持多孩子、多家长的场景

**注意**：
- 孩子也是 Person 节点（`person_type="child"`）
- 孩子的详细档案存储在 SQLite 的 ChildProfile 中
- Person 节点只存储用于关系图谱的基本信息

### 2.2 Behavior 节点（Graphiti）

```python
{
    "behavior_id": "bh_20240129_143022",
    "child_id": "child_001",
    "timestamp": "2024-01-29T14:30:22Z",
    "event_type": "social",  # social/emotion/communication/firstTime/other
    "description": "孩子主动递积木给妈妈，同时抬头看了一眼",
    "raw_input": "今天玩积木时，辰辰突然把积木递给我，还看了我一眼",
    "input_type": "text",  # voice/text/quick_button/video_ai
    "significance": "breakthrough",  # breakthrough/improvement/normal/concern
    "ai_analysis": {
        "category": "主动社交互动",
        "impact": "从被动回应转向主动发起"
    },
    "context": {
        "activity": "积木游戏",
        "location": "家里客厅"
    },
    "evidence": {
        "source": "parent_observation"
    }
}
```

**关系**：
- `(Person:child) -[展现]-> (Behavior)`
- `(Behavior) -[涉及对象]-> (Object)`
- `(Behavior) -[体现兴趣]-> (InterestDimension)`
- `(Behavior) -[体现功能]-> (FunctionDimension)`

### 2.3 ChildProfile（SQLite）

```python
{
    "child_id": "child_001",
    "name": "辰辰",
    "gender": "male",
    "birth_date": "2022-06-15",
    "diagnosis": "ASD轻度",
    "diagnosis_level": "mild",
    "diagnosis_date": "2024-01-01",
    
    # 发展维度基线
    "development_dimensions": [
        {
            "dimension_id": "eye_contact",
            "dimension_name": "眼神接触",
            "current_level": 3.5,
            "last_updated": "2024-01-29"
        }
        # ... 其他32个维度
    ],
    
    # 兴趣点
    "interests": [
        {
            "interest_id": "int_001",
            "name": "彩色积木",
            "category": "visual",
            "intensity": 8.5
        }
    ],
    
    "created_at": "2024-01-10",
    "updated_at": "2024-01-29"
}
```

---

## 3. 服务层架构

### 3.1 Memory 服务（核心）

**职责**：
- 提供统一的记忆读写接口
- LLM 智能解析（行为记录、评估生成、游戏总结）
- 封装 Graphiti 操作

**核心方法**：

```python
class MemoryService:
    # 智能写入（LLM 解析）
    async def record_behavior(child_id, raw_input, input_type) -> Behavior
    async def summarize_game(game_id, video_analysis, parent_feedback) -> Game
    async def generate_assessment(child_id, assessment_type) -> Assessment
    
    # 基础读写
    async def get_behaviors(child_id, filters) -> List[Behavior]
    async def get_recent_games(child_id, limit) -> List[Game]
    async def get_latest_assessment(child_id, type) -> Assessment
    
    # 对象管理
    async def save_object(obj) -> str
    async def get_objects(child_id) -> List[Object]
```

**注意**：
- Memory 服务**不管理孩子档案**（ChildProfile）
- 孩子档案由 SQLite 服务管理
- Memory 只管理 Person 节点（用于关系图谱）

### 3.2 SQLite 服务

**职责**：
- 管理结构化数据的 CRUD
- 事务管理
- 数据持久化

**核心方法**：

```python
class SQLiteService:
    # 孩子档案
    async def get_child(child_id) -> ChildProfile
    async def save_child(profile) -> str
    async def update_child(child_id, updates) -> None
    
    # 游戏方案
    async def save_game_plan(plan) -> str
    async def get_game_plan(game_id) -> GamePlan
    async def get_game_calendar(child_id) -> List[GamePlan]
    
    # 会话记录
    async def create_session(child_id, game_id) -> str
    async def get_session(session_id) -> GameSession
    async def update_session(session_id, updates) -> None
```

### 3.3 游戏推荐服务

**依赖**：
- SQLite 服务（获取孩子档案）
- Memory 服务（获取评估和游戏历史）
- LLM 服务（生成游戏方案）

**流程**：

```
1. 从 SQLite 获取孩子档案（ChildProfile）
2. 从 Memory 获取最近评估（get_latest_assessment）
3. 从 Memory 获取游戏历史（get_recent_games）
4. 调用 LLM 生成游戏方案
5. 保存到 SQLite（save_game_plan）
6. 保存到 Memory（save_game）
```

---

## 4. 数据流转示例

### 4.1 行为记录流程

```
用户输入（语音/文字）
    ↓
ObservationService
    ↓
MemoryService.record_behavior()
    ├─ LLM 解析自然语言
    ├─ 创建 Behavior 节点
    ├─ 创建关系：Person -> Behavior
    ├─ 创建关系：Behavior -> Object
    ├─ 创建关系：Behavior -> InterestDimension
    └─ 创建关系：Behavior -> FunctionDimension
```

### 4.2 游戏推荐流程

```
用户请求推荐游戏
    ↓
GameRecommender.recommend_game()
    ├─ SQLiteService.get_child(child_id)  ← 获取档案
    ├─ MemoryService.get_latest_assessment()  ← 获取评估
    ├─ MemoryService.get_recent_games()  ← 获取历史
    ├─ LLM 生成游戏方案
    ├─ SQLiteService.save_game_plan()  ← 保存方案
    └─ MemoryService.save_game()  ← 保存到记忆
```

### 4.3 游戏总结流程

```
游戏结束
    ↓
GameSummarizer.summarize()
    ├─ SQLiteService.get_session()  ← 获取会话数据
    ├─ MemoryService.summarize_game()
    │   ├─ LLM 生成总结
    │   ├─ 更新 FloorTimeGame 节点
    │   └─ 创建关键 Behavior 节点
    └─ SQLiteService.update_session()  ← 更新会话
```

---

## 5. 孩子评估模块设计

### 5.1 核心设计原则

**轻量化设计 - 适应稀疏数据**
- 假设家长初期只提供少量数据（5-10条行为记录）
- Agent 能在数据稀疏的情况下给出有价值的洞察
- 不强求"数据充分"，而是"基于现有数据，尽力分析"

**两级评估体系**
- 轻量级评估：游戏结束后自动触发，只分析游戏相关维度
- 完整评估：手动触发，分析所有可用数据，生成全面报告

### 5.2 三个独立 Agent

评估模块由三个独立的 Agent 组成，每个都有自己的"智能"：

#### Agent 1：兴趣挖掘 Agent

**核心任务**：从原始数据中挖掘兴趣模式

**输入**：
- 时间范围内所有行为记录（包含时间戳、描述、涉及对象）
- 孩子档案中的已知兴趣点（作为参考）
- 近期游戏总结（兴趣验证结果）

**核心能力**：
1. **识别真实兴趣 vs 假设兴趣**
   - 地板游戏是兴趣的"试错"过程
   - 档案中的兴趣点可能在游戏中未得到验证
   - 重点关注孩子的主动性和持续性表现

2. **发现意外兴趣**
   - 游戏中的"意外反应"往往揭示真实兴趣
   - 比如孩子更关注包装纸而非玩具本身

3. **兴趣广度分析**（特别重要）
   - 孤独症孩子的兴趣很难挖掘
   - 兴趣多样性比兴趣深度更重要
   - 评估孩子是否愿意尝试新事物

4. **智能衰减计算**
   - 持续兴趣（每周都出现）：权重不衰减
   - 短暂兴趣（只在某时段出现）：快速衰减
   - 最近2周的数据权重最高

**输出**（热力图数据）：
```
{
  "visual": {
    "strength": 7.5,           // 考虑衰减后的加权强度
    "trend": "increasing",     // 趋势：increasing/stable/decreasing
    "confidence": "medium",    // 置信度（基于数据量）
    "key_objects": [
      {
        "name": "彩色积木",
        "verified": true,      // 在游戏中验证为真实兴趣
        "engagement": 8.5
      },
      {
        "name": "旋转玩具",
        "verified": false,     // 档案中有，但游戏中表现不佳
        "engagement": 3.0,
        "note": "游戏中参与度低，可能不是真实兴趣"
      }
    ]
  },
  // ... 其他7个兴趣维度
  
  "overall_breadth": "narrow",  // narrow/moderate/diverse
  "new_discoveries": ["发现孩子对音乐盒的旋律特别专注"],
  "interest_verification": ["'旋转玩具'兴趣在游戏中未得到验证"]
}
```

#### Agent 2：功能分析 Agent

**核心任务**：从原始数据中分析功能维度表现

**输入**：
- 时间范围内所有行为记录（包含时间戳、描述、表现评分）
- 孩子档案中的功能维度基线
- 近期游戏总结（游戏中的维度表现）

**核心能力**：
1. **识别活跃维度**
   - 不分析所有33个维度，而是识别"哪些维度有足够数据"
   - 数据稀疏的维度标记为"数据不足"
   - 即使数据少（2-3条），也尝试给出初步判断（标注置信度）

2. **判断进步趋势**
   - 不是简单的"分数上升=进步"
   - 理解"进步的质量"：稳定提升？波动中上升？平台期？

3. **识别质的突破**（重点）
   - 主动性：从被动回应到主动发起
   - 持续性：从短暂到持久
   - 泛化性：从特定情境到多种情境
   - 复杂性：从简单到复杂
   - 一次主动发起的眼神接触，比十次被动回应更有意义

4. **维度关联分析**
   - 眼神接触改善 → 社交互动改善（连锁反应）
   - 情绪调节改善 → 多个维度都改善

**输出**（折线图数据）：
```
{
  "dimension_trends": {
    "eye_contact": {
      "current_level": 7.0,
      "baseline": 3.5,
      "change": "+3.5",
      "trend": "improving",
      "confidence": "high",
      "data_points": [
        {"date": "2024-01-01", "score": 3.5, "frequency": 2},
        {"date": "2024-01-29", "score": 7.0, "frequency": 12}
      ],
      "breakthrough_moments": [
        {
          "date": "2024-01-15",
          "type": "主动性突破",
          "description": "首次主动眼神接触超过3秒"
        }
      ]
    }
    // ... 其他活跃维度
  },
  "dimension_correlations": [
    "眼神接触提升带动了社交互动提升"
  ],
  "needs_attention": [
    {"dimension": "language", "note": "数据稀疏，建议增加观察"}
  ]
}
```

#### Agent 3：综合评估 Agent

**核心任务**：整合前两个 Agent 的输出，生成最终评估报告

**输入**：
1. 兴趣挖掘 Agent 的输出
2. 功能分析 Agent 的输出
3. 近期游戏总结（5-10个游戏）
4. 上次评估报告（如果有）
5. 孩子档案

**核心能力**：
1. **整合两个维度的分析**
   - 兴趣和功能如何关联
   - 是否存在"兴趣驱动的进步"

2. **生成家长友好的评价**
   - 采用"三明治"结构：肯定 → 关注 → 建议
   - 语气温暖、专业、不制造焦虑

3. **提供可操作的建议**
   - 不是泛泛而谈，而是具体的行动建议
   - 基于孩子的兴趣和当前水平

4. **设定合理的目标**
   - 有挑战性但可达成
   - 不给家长制造压力

**输出**（结构化评估报告）：
```
{
  "assessment_id": "assess-xxx",
  "assessment_type": "comprehensive",  // comprehensive/lightweight
  "time_range": {"start_date": "...", "end_date": "..."},
  
  "overall_assessment": "辰辰在过去30天内展现出显著进步...",
  "overall_score": 7.2,
  
  "interest_analysis": {
    "summary": "视觉兴趣持续占主导地位...",
    "heatmap_data": {...},
    "breadth_evaluation": "兴趣范围狭窄，建议拓展",
    "key_findings": [...]
  },
  
  "dimension_analysis": {
    "summary": "眼神接触和社交互动进步最为显著...",
    "trend_data": {...},
    "breakthroughs": [...],
    "correlations": [...]
  },
  
  "recommendations": [
    "继续使用视觉兴趣载体（彩色积木）进行干预",
    "加强语言引导，在游戏中增加语言互动环节"
  ],
  
  "next_phase_goals": [...],
  "data_sources": {
    "behavior_records": 156,
    "game_sessions": 8,
    "confidence_level": "medium"
  }
}
```

### 5.3 两级评估体系

#### 轻量级评估（游戏后自动触发）

**触发时机**：每次地板游戏结束后

**分析范围**：
- 只分析本次游戏涉及的维度
- 只分析本次游戏使用的兴趣点
- 不调用兴趣挖掘和功能分析 Agent（太重）

**输出内容**：
- 本次游戏的表现总结（200字以内）
- 兴趣验证结果（这个兴趣点是否有效）
- 维度进展（本次游戏关注的维度表现如何）
- 快速建议（1-2条，针对下次游戏）

**特点**：快速、轻量、针对性强

#### 完整评估（手动触发）

**触发时机**：家长或治疗师主动点击"生成评估报告"

**分析范围**：
- 调用兴趣挖掘 Agent（分析所有兴趣数据）
- 调用功能分析 Agent（分析所有功能维度）
- 整合近期游戏总结
- 对比上次完整评估

**输出内容**：
- 整体发展评价（300字）
- 兴趣分析（热力图 + 广度评估 + 验证结果）
- 功能维度分析（折线图 + 突破识别 + 关联分析）
- 干预建议（3-5条）
- 下阶段目标

**特点**：全面、深入、趋势性强

### 5.4 游戏总结 Agent 的增强

为了支持评估模块，游戏总结 Agent 需要增加以下观察：

**1. 兴趣验证**
- 评估游戏中使用的兴趣点是否有效
- 孩子对这些对象的真实反应如何
- 明确指出"该兴趣点可能需要重新评估"

**2. 意外发现**
- 记录游戏中的"意外时刻"
- 孩子是否对游戏设计之外的事物表现出兴趣
- 这些意外发现可能揭示新的兴趣点

**3. 兴趣试错结果**
- 如果本次游戏是为了验证某个兴趣点
- 明确给出验证结果："验证成功"或"验证失败"

### 5.5 数据存储

**SQLite**：
- 存储评估报告的完整 JSON（方便查询、导出、打印）
- 区分轻量级评估和完整评估
- 保留所有历史评估记录

**Graphiti**：
- 存储 ChildAssessment 节点
- 创建关系：`(Person:child) -[接受评估]-> (ChildAssessment)`
- 创建关系：`(ChildAssessment) -[关注维度]-> (FunctionDimension)`
- 用于趋势分析和推荐依据

---

## 6. 当前实施状态

### 6.1 已完成

✅ Memory 服务核心实现
- 智能写入方法（record_behavior, summarize_game, generate_assessment）
- 基础读写接口
- LLM 集成（使用 output_schema）

✅ Graphiti 存储层
- 7种节点类型定义
- 索引和约束管理
- 关系创建和查询

✅ 行为观察模块
- ObservationService
- API 端点（/api/observation/*）
- 前端测试页面

✅ SQLite 服务
- ChildProfile CRUD（已对齐 src/models/profile.py）
- GamePlan CRUD（游戏方案管理）
- GameSession CRUD（游戏会话管理）
- WeeklyPlan CRUD
- Observation CRUD

✅ 游戏模块
- GameRecommender（游戏推荐）
- GameSummarizer（游戏总结，已增强兴趣观察）
- API 端点（/api/game/*）
- 前端测试页面

⏳ 评估模块（设计完成，待实现）
- 兴趣挖掘 Agent
- 功能分析 Agent
- 综合评估 Agent
- 两级评估体系

⏳ 档案导入模块
- 多模态解析
- 初始评估生成

---

## 7. 关键设计决策

### 6.1 为什么 Person 节点包含孩子？

**原因**：
1. 统一建模：所有参与者都是 Person，简化关系图谱
2. 支持多孩子：系统可以管理多个孩子
3. 关系清晰：`(Person:parent) -[陪伴]-> (Behavior) <-[展现]- (Person:child)`

### 6.2 为什么孩子档案在 SQLite？

**原因**：
1. 结构化数据：档案是相对稳定的结构化信息
2. 查询效率：频繁的档案查询用 SQL 更高效
3. 职责分离：SQLite 管理"状态"，Graphiti 管理"事件"

### 6.3 为什么游戏方案在 SQLite？

**原因**：
1. 完整性：游戏方案是完整的结构化文档
2. 版本管理：方便保存和查询不同版本
3. 实施记录：会话数据需要结构化存储

---

## 7. 下一步计划

1. **实现 SQLite 服务**
   - 定义数据库 schema
   - 实现 ChildProfile CRUD
   - 实现 GamePlan CRUD

2. **完善游戏推荐**
   - 修复 GameRecommender 依赖
   - 优化 Prompt
   - 测试完整流程

3. **实现档案导入**
   - 多模态解析
   - 初始评估生成
   - 数据写入 SQLite + Graphiti

4. **前端测试**
   - 游戏推荐测试页面
   - 档案导入测试页面
   - 完整流程测试

---

**文档结束**


## 7. 关键设计决策

### 7.1 为什么 Person 节点包含孩子？

**原因**：
1. 统一建模：所有参与者都是 Person，简化关系图谱
2. 支持多孩子：系统可以管理多个孩子
3. 关系清晰：`(Person:parent) -[陪伴]-> (Behavior) <-[展现]- (Person:child)`

### 7.2 为什么孩子档案在 SQLite？

**原因**：
1. 结构化数据：档案是相对稳定的结构化信息
2. 查询效率：频繁的档案查询用 SQL 更高效
3. 职责分离：SQLite 管理"状态"，Graphiti 管理"事件"

### 7.3 为什么游戏方案在 SQLite？

**原因**：
1. 完整性：游戏方案是完整的结构化文档
2. 版本管理：方便保存和查询不同版本
3. 实施记录：会话数据需要结构化存储

### 7.4 为什么评估模块采用三个独立 Agent？

**原因**：
1. 职责分离：兴趣挖掘、功能分析、综合评估各有专长
2. 可复用性：兴趣挖掘和功能分析可以独立使用
3. 灵活性：轻量级评估可以跳过前两个 Agent
4. 智能化：每个 Agent 都有自己的"智能"，不是简单统计

### 7.5 为什么强调"兴趣广度"而非"兴趣深度"？

**原因**：
1. 孤独症特点：孤独症孩子的兴趣往往狭窄、刻板
2. 干预目标：拓展兴趣范围比加深单一兴趣更重要
3. 发展需求：兴趣多样性有助于社交和认知发展

### 7.6 为什么地板游戏是"兴趣试错"过程？

**原因**：
1. 档案中的兴趣可能是家长的假设，未必是孩子的真实兴趣
2. 游戏过程中可能发现孩子对某个"预期兴趣"反应冷淡
3. 游戏中的"意外反应"往往揭示真实兴趣
4. 这种验证机制帮助不断修正对孩子兴趣的理解

### 7.7 为什么采用"轻量化"设计？

**原因**：
1. 现实约束：家长初期只能提供少量数据（5-10条行为记录）
2. 用户体验：不能因为"数据不足"就拒绝生成评估
3. 渐进式：随着数据积累，评估质量自然提升
4. 降低门槛：让家长更容易开始使用系统

### 7.8 为什么强调"质变"而非"量变"？

**原因**：
1. 发展规律：孩子的进步往往是质的突破，而非线性增长
2. 数据稀疏：在数据少的情况下，质的观察比量的统计更可靠
3. 家长关注：家长更关心"孩子会主动了"而非"次数增加了"
4. 干预指导：质的突破更能指导下一步干预方向

---

## 8. 下一步计划

1. **实现评估模块**
   - 创建 AssessmentService
   - 实现三个 Agent（兴趣挖掘、功能分析、综合评估）
   - 编写 Prompt 模板
   - 实现两级评估体系

2. **完善游戏总结**
   - 增强兴趣验证观察
   - 记录意外发现
   - 明确试错结果

3. **实现档案导入**
   - 多模态解析
   - 初始评估生成
   - 数据写入 SQLite + Graphiti

4. **前端开发**
   - 评估报告展示页面
   - 热力图组件（兴趣点）
   - 折线图组件（功能维度趋势）
   - 完整流程测试

---

**文档版本**：v3.0  
**最后更新**：2026-01-30  
**状态**：评估模块设计完成，待实现
