# Graphiti 数据模型设计文档

> 日期：2026-01-29
> 状态：待实现
> 目标：基于ABC、CARS、M-CHAT量表，设计全面的ASD儿童评估数据结构

---

## 一、设计背景

### 现有问题
- 当前Graphiti模块数据结构过于简单（仅12个维度）
- 无法覆盖专业量表的评估范围
- 缺少兴趣点、异常事件、生理背景等重要数据类型

### 设计依据
- ABC量表（孤独症行为评定量表）：57项，5个能力维度
- CARS量表（儿童孤独症评定量表）：15项详细评估
- M-CHAT量表（修订版孤独症筛查量表）：23项早期筛查

### 设计原则
- 按功能领域重新归纳量表维度
- 兴趣点统一记录，用属性标签区分
- 异常事件全覆盖（行为、退步、新刻板、身体）
- 生理数据作为背景因素关联到观察/事件
- 保留Greenspan 6阶段里程碑，建立与维度的映射

---

## 二、整体图结构

```
Child (孩子)
│
├──[HAS_DOMAIN]──→ Domain (功能领域)
│                    │
│                    └──[HAS_DIMENSION]──→ Dimension (子维度)
│                                            │
│                                            └──[HAS_OBSERVATION]──→ Observation (观察)
│
├──[HAS_INTEREST]──→ Interest (兴趣点)
│                      │
│                      └──[HAS_CHANGE]──→ InterestChange (兴趣变化)
│
├──[HAS_INCIDENT]──→ Incident (异常事件)
│
├──[HAS_MILESTONE]──→ Milestone (里程碑)
│
└──[IN_CONTEXT]──→ PhysioContext (生理背景)
```

### 边关系
- `Dimension ──[MAPS_TO]──→ Milestone`：维度映射到里程碑阶段
- `Observation ──[IN_CONTEXT]──→ PhysioContext`：观察关联生理背景
- `Incident ──[IN_CONTEXT]──→ PhysioContext`：异常事件关联生理背景
- `Dimension ──[CORRELATES_WITH]──→ Dimension`：维度间关联

---

## 三、功能领域与子维度（33个维度）

### 3.1 感觉能力（Sensory）- 5个维度

| 维度ID | 显示名称 | 说明 | 量表来源 |
|--------|----------|------|----------|
| visual_response | 视觉反应 | 凝视、回避、余光 | ABC-6,34,44,52,57 / CARS-7 |
| auditory_response | 听觉反应 | 对声音敏感/迟钝 | ABC-10,21,39 / CARS-8 |
| tactile_response | 触觉反应 | 触摸偏好/回避 | ABC-51 / CARS-9 |
| pain_response | 痛觉反应 | 过敏/迟钝 | ABC-26 / CARS-9 |
| taste_smell | 味觉嗅觉 | 舔、闻物品 | ABC-51 / CARS-9 |

### 3.2 社交互动（Social）- 6个维度

| 维度ID | 显示名称 | 说明 | 量表来源 |
|--------|----------|------|----------|
| eye_contact | 眼神接触 | 眼神交流的频率和质量 | ABC-24,47 / CARS-1 / M-CHAT-10 |
| social_smile | 社交性微笑 | 回应性和主动性微笑 | ABC-7 / M-CHAT-12 |
| social_interest | 社交兴趣 | 对他人的兴趣 | ABC-3,38 / CARS-1 / M-CHAT-2 |
| imitation | 模仿能力 | 动作和语言模仿 | ABC-33 / CARS-2 / M-CHAT-13 |
| joint_attention | 共同注意力 | 分享注意力焦点 | M-CHAT-7,9,15,17 |
| social_initiation | 社交发起 | 主动发起社交互动 | ABC-3 / M-CHAT-19 |

### 3.3 语言沟通（Language）- 6个维度

| 维度ID | 显示名称 | 说明 | 量表来源 |
|--------|----------|------|----------|
| language_comprehension | 语言理解 | 对指令和语言的理解 | ABC-4,20,37 / M-CHAT-21 |
| language_expression | 语言表达 | 主动语言表达能力 | ABC-42,56 / CARS-11 |
| pronoun_use | 代词使用 | 代词的正确使用 | ABC-8,18 |
| echolalia | 仿说 | 重复语言/仿说 | ABC-32,46,48 |
| non_verbal_communication | 非语言沟通 | 手势、指向等 | ABC-29 / CARS-12 / M-CHAT-6 |
| speech_prosody | 语音语调 | 说话的节奏和语调 | ABC-11 / CARS-11 |

### 3.4 运动躯体（Motor）- 6个维度

| 维度ID | 显示名称 | 说明 | 量表来源 |
|--------|----------|------|----------|
| stereotyped_movement | 刻板动作 | 拍手、旋转、摇摆等 | ABC-1,12,16,22,40 / CARS-4 |
| body_coordination | 身体协调性 | 动作协调程度 | ABC-13 / CARS-4 |
| activity_level | 活动水平 | 过度活跃或不足 | CARS-13 |
| gait_posture | 步态姿势 | 脚尖走路等异常步态 | ABC-16,30 / CARS-4 |
| self_injury | 自伤行为 | 撞头、咬手等 | ABC-35 |
| aggression | 攻击行为 | 对他人的攻击 | ABC-31 |

### 3.5 情绪适应（Emotional）- 5个维度

| 维度ID | 显示名称 | 说明 | 量表来源 |
|--------|----------|------|----------|
| emotional_expression | 情绪表达 | 情绪的外在表达 | CARS-3 |
| emotional_response | 情绪反应 | 情绪反应的适当性 | ABC-17 / CARS-3 |
| anxiety_level | 焦虑水平 | 焦虑和不安程度 | ABC-43 / CARS-10 |
| change_adaptation | 环境适应 | 对环境变化的适应 | ABC-14 / CARS-6 |
| frustration_tolerance | 挫折耐受 | 对挫折的耐受程度 | ABC-23,36 |

### 3.6 自理能力（Self-care）- 5个维度

| 维度ID | 显示名称 | 说明 | 量表来源 |
|--------|----------|------|----------|
| toileting | 如厕能力 | 大小便控制 | ABC-41 |
| dressing | 穿衣能力 | 自己穿脱衣物 | ABC-45 |
| feeding | 进食能力 | 独立进食 | - |
| safety_awareness | 安全意识 | 对危险的意识 | ABC-49 |
| routine_skills | 日常技能 | 日常技能学习保持 | ABC-2 |

---

## 四、节点模型定义

### 4.1 Child（孩子）

```python
@dataclass
class Child:
    node_type: str = "Child"
    child_id: str = ""           # 唯一标识
    name: str = ""               # 姓名
    created_at: str = ""         # 创建时间
```

### 4.2 Domain（功能领域）

```python
@dataclass
class Domain:
    node_type: str = "Domain"
    domain_id: str = ""          # 如 "domain-sensory"
    child_id: str = ""           # 所属孩子
    name: str = ""               # 英文名: sensory, social, language, motor, emotional, self_care
    display_name: str = ""       # 中文名: 感觉能力, 社交互动, 语言沟通, 运动躯体, 情绪适应, 自理能力
    description: str = ""        # 领域描述
```

### 4.3 Dimension（子维度）

```python
@dataclass
class Dimension:
    node_type: str = "Dimension"
    dimension_id: str = ""       # 如 "dim-eye_contact-child-001"
    child_id: str = ""           # 所属孩子
    domain: str = ""             # 所属领域: sensory, social, language, motor, emotional, self_care
    name: str = ""               # 维度名称（英文）
    display_name: str = ""       # 显示名称（中文）
    description: str = ""        # 维度描述
    value_type: str = "score"    # 值类型: score, count, duration, boolean
    max_value: Optional[float] = 10  # 最大值（score类型）
    inverse: bool = False        # 是否反向（值越低越好）
    scale_sources: List[str] = field(default_factory=list)  # 量表来源
    baseline_value: Optional[float] = None
    baseline_date: Optional[str] = None
```

### 4.4 Observation（观察记录）

```python
@dataclass
class Observation:
    node_type: str = "Observation"
    observation_id: str = ""     # 唯一标识
    child_id: str = ""           # 所属孩子
    dimension: str = ""          # 所属维度
    value: float = 0.0           # 观察值
    value_type: str = "score"    # 值类型
    timestamp: str = ""          # 观察时间
    source: str = ""             # 数据来源: observation_agent, game_session, video_analysis, manual
    context: Optional[str] = None  # 观察上下文
    confidence: float = 0.8      # 置信度
    session_id: Optional[str] = None  # 关联会话
```

### 4.5 Interest（兴趣点）

```python
@dataclass
class Interest:
    node_type: str = "Interest"
    interest_id: str = ""        # 唯一标识
    child_id: str = ""           # 所属孩子
    name: str = ""               # 兴趣名称（如"火车"、"旋转物品"、"水"）
    category: str = ""           # 兴趣类型: sensory, object, activity, topic, social
    intensity: str = "moderate"  # 强度: low, moderate, high, obsessive
    is_restricted: bool = False  # 是否受限/刻板
    usability: str = "medium"    # 干预可利用性: low, medium, high
    status: str = "active"       # 状态: active, fading, disappeared
    first_observed: str = ""     # 首次观察时间
    description: str = ""        # 描述
```

### 4.6 InterestChange（兴趣变化）

```python
@dataclass
class InterestChange:
    node_type: str = "InterestChange"
    change_id: str = ""          # 唯一标识
    interest_id: str = ""        # 所属兴趣
    timestamp: str = ""          # 变化时间
    change_type: str = ""        # 变化类型: emerged, intensified, broadened, faded, disappeared
    from_value: str = ""         # 变化前状态
    to_value: str = ""           # 变化后状态
    note: str = ""               # 备注
```

### 4.7 Incident（异常事件）

```python
@dataclass
class Incident:
    node_type: str = "Incident"
    incident_id: str = ""        # 唯一标识
    child_id: str = ""           # 所属孩子
    timestamp: str = ""          # 发生时间
    category: str = ""           # 类别: behavior, regression, new_stereotypy, physical
    severity: str = "moderate"   # 严重程度: mild, moderate, severe
    description: str = ""        # 事件描述
    related_dimension: Optional[str] = None  # 关联维度

    # behavior 类型字段
    behavior_type: Optional[str] = None      # meltdown, tantrum, aggression, self_injury, escape
    duration_minutes: Optional[int] = None   # 持续时长
    trigger: Optional[str] = None            # 触发因素
    intervention: Optional[str] = None       # 干预措施

    # regression 类型字段
    from_level: Optional[float] = None       # 原有水平
    to_level: Optional[float] = None         # 退步后水平
    duration_days: Optional[int] = None      # 持续天数
    recovered: Optional[bool] = None         # 是否恢复

    # new_stereotypy 类型字段
    behavior_name: Optional[str] = None      # 行为名称
    frequency: Optional[str] = None          # 频率: occasional, frequent, constant

    # physical 类型字段
    symptom: Optional[str] = None            # 症状
    medical_attention: Optional[bool] = None # 是否就医
```

### 4.8 PhysioContext（生理背景）

```python
@dataclass
class PhysioContext:
    node_type: str = "PhysioContext"
    context_id: str = ""         # 唯一标识
    child_id: str = ""           # 所属孩子
    date: str = ""               # 日期（按天记录）

    # 睡眠
    sleep_quality: Optional[str] = None      # poor, fair, good
    sleep_hours: Optional[float] = None      # 睡眠时长
    sleep_issues: Optional[str] = None       # 入睡难、夜醒、早醒

    # 其他
    appetite: Optional[str] = None           # poor, normal, good
    energy_level: Optional[str] = None       # low, normal, high
    health_status: Optional[str] = None      # healthy, mild_sick, sick
    health_symptoms: Optional[str] = None    # 症状描述

    # 用药
    medication_name: Optional[str] = None    # 药名
    medication_note: Optional[str] = None    # 备注

    note: str = ""               # 其他备注
```

### 4.9 Milestone（里程碑）

```python
@dataclass
class Milestone:
    node_type: str = "Milestone"
    milestone_id: str = ""       # 唯一标识
    child_id: str = ""           # 所属孩子
    stage: int = 1               # Greenspan阶段: 1-6
    stage_name: str = ""         # 阶段名称
    dimension: Optional[str] = None  # 关联维度
    type: str = "first_time"     # 类型: first_time, breakthrough, significant_improvement, consistency
    description: str = ""        # 描述
    timestamp: str = ""          # 达成时间
    significance: str = "high"   # 重要性: high, medium, low
```

---

## 五、边类型定义

```python
class EdgeType(Enum):
    # 层级关系
    HAS_DOMAIN = "HAS_DOMAIN"              # Child → Domain
    HAS_DIMENSION = "HAS_DIMENSION"        # Domain → Dimension
    HAS_OBSERVATION = "HAS_OBSERVATION"    # Dimension → Observation

    # 兴趣关系
    HAS_INTEREST = "HAS_INTEREST"          # Child → Interest
    HAS_CHANGE = "HAS_CHANGE"              # Interest → InterestChange

    # 事件关系
    HAS_INCIDENT = "HAS_INCIDENT"          # Child → Incident

    # 里程碑关系
    HAS_MILESTONE = "HAS_MILESTONE"        # Child → Milestone
    MAPS_TO = "MAPS_TO"                    # Dimension → Milestone (weight: primary/secondary)

    # 上下文关系
    IN_CONTEXT = "IN_CONTEXT"              # Observation/Incident → PhysioContext

    # 关联关系
    CORRELATES_WITH = "CORRELATES_WITH"    # Dimension ↔ Dimension
```

---

## 六、维度与里程碑映射

### Greenspan 6阶段

| 阶段 | 名称 | 英文 | 核心能力 |
|------|------|------|----------|
| 1 | 自我调节 | self_regulation | 自我调节与对世界的兴趣 |
| 2 | 亲密关系 | intimacy | 亲密关系与依恋 |
| 3 | 双向沟通 | two_way_communication | 双向沟通 |
| 4 | 复杂沟通 | complex_communication | 复杂沟通与问题解决 |
| 5 | 情绪想法 | emotional_ideas | 情绪想法与符号表达 |
| 6 | 逻辑思维 | logical_thinking | 逻辑思维与现实检验 |

### 映射表

| 维度 | 主要映射 | 次要映射 |
|------|----------|----------|
| **感觉能力** | | |
| visual_response | 阶段1 | - |
| auditory_response | 阶段1 | - |
| tactile_response | 阶段1 | - |
| pain_response | 阶段1 | - |
| taste_smell | 阶段1 | - |
| **社交互动** | | |
| eye_contact | 阶段2 | 阶段3 |
| social_smile | 阶段2 | - |
| social_interest | 阶段2 | - |
| imitation | 阶段3 | 阶段4 |
| joint_attention | 阶段3 | 阶段4 |
| social_initiation | 阶段3 | 阶段4 |
| **语言沟通** | | |
| language_comprehension | 阶段3 | 阶段4 |
| language_expression | 阶段4 | 阶段5 |
| pronoun_use | 阶段5 | - |
| echolalia | 阶段3 | - |
| non_verbal_communication | 阶段3 | - |
| speech_prosody | 阶段4 | - |
| **运动躯体** | | |
| stereotyped_movement | 阶段1 | - |
| body_coordination | 阶段1 | - |
| activity_level | 阶段1 | - |
| gait_posture | 阶段1 | - |
| self_injury | 阶段1 | - |
| aggression | 阶段1 | 阶段2 |
| **情绪适应** | | |
| emotional_expression | 阶段5 | 阶段6 |
| emotional_response | 阶段2 | 阶段5 |
| anxiety_level | 阶段1 | 阶段2 |
| change_adaptation | 阶段1 | - |
| frustration_tolerance | 阶段1 | 阶段4 |
| **自理能力** | | |
| toileting | 阶段4 | - |
| dressing | 阶段4 | - |
| feeding | 阶段1 | - |
| safety_awareness | 阶段4 | 阶段6 |
| routine_skills | 阶段4 | - |

---

## 七、数据模型汇总

### 节点类型（9种）

| 节点 | 说明 | 数量级 |
|------|------|--------|
| Child | 孩子 | 少量 |
| Domain | 功能领域 | 6个（固定） |
| Dimension | 子维度 | 33个（固定） |
| Observation | 观察记录 | 持续增长 |
| Milestone | 里程碑 | 6阶段 + 达成记录 |
| Interest | 兴趣点 | 每孩子若干 |
| InterestChange | 兴趣变化 | 持续增长 |
| Incident | 异常事件 | 持续增长 |
| PhysioContext | 生理背景 | 按天记录 |

### 边类型（10种）

| 边 | 关系 | 说明 |
|----|------|------|
| HAS_DOMAIN | Child → Domain | 孩子拥有功能领域 |
| HAS_DIMENSION | Domain → Dimension | 领域包含维度 |
| HAS_OBSERVATION | Dimension → Observation | 维度下的观察 |
| HAS_INTEREST | Child → Interest | 孩子的兴趣 |
| HAS_CHANGE | Interest → InterestChange | 兴趣变化记录 |
| HAS_INCIDENT | Child → Incident | 异常事件 |
| HAS_MILESTONE | Child → Milestone | 里程碑达成 |
| MAPS_TO | Dimension → Milestone | 维度映射到里程碑 |
| IN_CONTEXT | Observation/Incident → PhysioContext | 关联生理背景 |
| CORRELATES_WITH | Dimension ↔ Dimension | 维度间关联 |

---

## 八、与现有系统的对比

| 方面 | 现有系统 | 新设计 |
|------|----------|--------|
| 维度数量 | 12个 | 33个 |
| 维度组织 | 扁平 | 层次化（领域→维度） |
| 兴趣追踪 | 无 | Interest + InterestChange |
| 异常事件 | 无 | Incident（4种类型） |
| 生理背景 | 无 | PhysioContext |
| 里程碑映射 | 无 | MAPS_TO 边 |
| 量表覆盖 | 部分 | ABC + CARS + M-CHAT |

---

## 九、后续实现步骤

1. **更新 models/ 目录**
   - 新增 `domains.py`：领域配置
   - 更新 `dimensions.py`：33个维度定义
   - 更新 `nodes.py`：新节点类型
   - 更新 `edges.py`：新边类型

2. **更新 storage/ 目录**
   - `graph_storage.py`：新增节点/边的CRUD操作
   - `index_manager.py`：新增索引

3. **更新 service.py**
   - 新增兴趣、异常事件、生理背景的API
   - 更新观察保存逻辑

4. **数据迁移**
   - 将现有12个维度映射到新的33个维度
   - 创建Domain节点层级

---

## 十、参考资料

- ABC量表（孤独症行为评定量表）
- CARS量表（儿童孤独症评定量表）
- M-CHAT量表（修订版孤独症筛查量表）
- Greenspan DIR模型
