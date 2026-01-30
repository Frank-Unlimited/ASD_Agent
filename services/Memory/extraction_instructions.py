"""
Graphiti-core 提取指令
用于指导 LLM 如何从文本中提取实体和关系
"""

# ========== 行为记录提取指令 ==========

BEHAVIOR_EXTRACTION_INSTRUCTIONS = """
# 行为记录提取指令

## 目标
从家长的自然语言观察记录中提取结构化的行为信息。

## 提取实体类型

### 1. Behavior（行为）- 必须提取
- **event_type**: 根据行为内容判断类型
  - social: 涉及社交互动（如：主动递东西、眼神接触、分享）
  - emotion: 情绪表达（如：笑、哭、生气）
  - communication: 沟通表达（如：说话、指向、手势）
  - firstTime: 首次出现的行为（文本中明确提到"第一次"）
  - other: 其他类型
  
- **description**: 简洁描述行为（30字以内）
  
- **significance**: 判断重要性
  - breakthrough: 突破性进步（首次出现、重大改善）
  - improvement: 有改善（比之前好）
  - normal: 常规行为
  - concern: 需要关注（退步、问题行为）
  
- **emotional_state**: 孩子的情绪（如：开心、焦虑、平静）
- **duration_seconds**: 如果文本提到时长，提取秒数
- **context_notes**: 其他上下文信息

### 2. Object（对象）- 如果提到物品则提取
- **object_name**: 对象名称（如：积木、球、音乐盒）
- **category**: 对象类别（玩具、工具、书籍等）
- **interaction_type**: 互动方式（使用、观察、拒绝等）

### 3. Interest（兴趣维度）- 根据行为推断
根据行为内容推断体现的兴趣维度：
- **visual**: 视觉类（看、观察、颜色、图案）
- **auditory**: 听觉类（听、音乐、声音）
- **tactile**: 触觉类（摸、触感、质地）
- **motor**: 运动类（跑、跳、爬、平衡）
- **construction**: 建构类（搭建、拼装、组合）
- **order**: 秩序类（排序、分类、整理）
- **cognitive**: 认知类（数字、字母、因果关系）
- **social**: 社交类（互动、分享、合作）

每个兴趣维度需要：
- **intensity**: 强度（0-10分）
- **duration_seconds**: 持续时长（如果能推断）
- **is_primary**: 是否为主要兴趣

### 4. Function（功能维度）- 根据行为推断
根据行为内容推断反映的功能维度（33个功能维度中选择相关的）：

**感觉能力（sensory）**:
- visual_tracking: 视觉追踪
- auditory_response: 听觉反应
- tactile_sensitivity: 触觉敏感度
- sensory_integration: 感觉统合
- pain_awareness: 痛觉意识

**社交互动（social）**:
- eye_contact: 眼神接触
- social_smile: 社交性微笑
- social_interest: 社交兴趣
- social_initiation: 社交主动性
- joint_attention: 共同注意
- imitation: 模仿能力

**语言沟通（language）**:
- language_comprehension: 语言理解
- language_expression: 语言表达
- non_verbal_communication: 非语言沟通
- conversation_skills: 对话技能
- pragmatic_language: 语用能力
- echolalia: 回声语言

**运动躯体（motor）**:
- gross_motor: 大运动
- fine_motor: 精细动作
- body_coordination: 身体协调
- motor_planning: 运动计划
- balance: 平衡能力
- hand_eye_coordination: 手眼协调

**情绪适应（emotional）**:
- emotional_expression: 情绪表达
- emotional_regulation: 情绪调节
- frustration_tolerance: 挫折容忍
- anxiety_level: 焦虑水平
- mood_stability: 情绪稳定性

**自理能力（self_care）**:
- eating_skills: 进食技能
- toileting_skills: 如厕技能
- dressing_skills: 穿衣技能
- hygiene_skills: 卫生技能
- sleep_patterns: 睡眠模式

每个功能维度需要：
- **score**: 评分（0-10分）
- **strength**: 表现强度（0-1）

### 5. Person（人物）- 如果提到其他人则提取
- **person_name**: 人物名称（如：妈妈、爸爸、李老师）
- **role**: 角色（facilitator引导者/participant参与者/observer观察者）
- **interaction_quality**: 互动质量（positive/negative/neutral）

## 提取关系类型

### 1. 孩子 -> 展现 -> 行为
- 属性：observation_time（观察时间）

### 2. 行为 -> 涉及对象 -> 对象
- 属性：interaction_type（互动类型）

### 3. 行为 -> 体现兴趣 -> 兴趣维度
- 属性：intensity（强度）, duration_seconds（持续时长）

### 4. 行为 -> 体现功能 -> 功能维度
- 属性：score（评分）, strength（强度）

### 5. 行为 -> 涉及人物 -> 人物
- 属性：role（角色）, interaction_quality（互动质量）

## 提取原则

1. **准确性优先**: 只提取文本中明确提到或可以合理推断的信息
2. **避免过度推断**: 如果不确定，不要强行提取
3. **保持客观**: 基于观察事实，不添加主观判断
4. **关注细节**: 注意时间、地点、人物、对象等细节
5. **识别首次**: 特别注意"第一次"、"首次"等关键词

## 示例

**输入**: "今天小明主动把积木递给我，还看着我的眼睛笑了，这是第一次！"

**提取结果**:
- Behavior:
  - event_type: "social"
  - description: "主动递积木并眼神接触"
  - significance: "breakthrough"
  - emotional_state: "开心"
  
- Object:
  - object_name: "积木"
  - category: "玩具"
  - interaction_type: "使用"
  
- Interest:
  - interest_name: "social"
  - intensity: 9.0
  - is_primary: true
  
  - interest_name: "construction"
  - intensity: 6.0
  - is_primary: false
  
- Function:
  - function_name: "eye_contact"
  - score: 8.0
  - strength: 0.9
  
  - function_name: "social_initiation"
  - score: 9.0
  - strength: 0.95
  
  - function_name: "social_smile"
  - score: 8.0
  - strength: 0.85

- 关系:
  - 孩子 -> 展现 -> 行为
  - 行为 -> 涉及对象 -> 积木
  - 行为 -> 体现兴趣 -> social
  - 行为 -> 体现兴趣 -> construction
  - 行为 -> 体现功能 -> eye_contact
  - 行为 -> 体现功能 -> social_initiation
  - 行为 -> 体现功能 -> social_smile
"""


# ========== 游戏总结提取指令 ==========

GAME_SUMMARY_EXTRACTION_INSTRUCTIONS = """
# 游戏总结提取指令

## 目标
从游戏实施数据（游戏设计、视频分析、家长反馈）中提取结构化的总结信息。

## 提取实体类型

### 1. GameSummary（游戏总结）- 必须提取
- **session_summary**: 游戏会话总结（100-200字）
- **engagement_score**: 参与度评分（0-10分）
- **goal_achievement_score**: 目标达成度评分（0-10分）
- **highlights**: 亮点时刻列表
- **concerns**: 需要关注的问题列表
- **improvement_suggestions**: 改进建议列表

### 2. KeyBehavior（关键行为）- 提取游戏中的关键时刻
- **timestamp**: 时间戳（如：02:15）
- **description**: 行为描述
- **event_type**: 事件类型
- **significance**: 重要性

## 提取原则

1. **综合分析**: 结合游戏设计、视频分析、家长反馈
2. **客观评价**: 基于实际表现评分
3. **具体建议**: 提供可操作的改进建议
4. **关注进步**: 识别突破性时刻和改善点
"""


# ========== 评估生成提取指令 ==========

ASSESSMENT_EXTRACTION_INSTRUCTIONS = """
# 评估生成提取指令

## 目标
从历史行为数据中生成综合评估。

## 提取实体类型

### 1. Assessment（评估）- 必须提取
- **assessment_type**: 评估类型
- **summary**: 评估总结
- **key_findings**: 关键发现列表
- **recommendations**: 建议列表
- **confidence_score**: 置信度（0-1）

## 评估类型

### interest_mining（兴趣挖掘）
分析孩子的兴趣偏好，识别：
- 主要兴趣维度
- 兴趣强度和持续性
- 兴趣发展趋势
- 可利用的兴趣点

### function_trend（功能趋势）
分析功能维度的发展趋势，识别：
- 进步的功能维度
- 需要加强的功能维度
- 功能发展速度
- 功能之间的关联

### comprehensive（综合评估）
全面评估孩子的发展状况，包括：
- 整体发展水平
- 优势和劣势
- 发展趋势
- 干预建议

## 提取原则

1. **数据驱动**: 基于历史行为数据
2. **趋势分析**: 关注变化和发展
3. **个性化**: 针对孩子的特点
4. **可操作**: 提供具体的干预建议
"""


# ========== 负面事件提取指令 ==========

NEGATIVE_EVENT_EXTRACTION_INSTRUCTIONS = """
# 负面事件提取指令

## 目标
识别和提取负面事件信息，用于游戏推荐时的避让。

## 负面事件标识

当文本中出现以下情况时，标记为负面事件：
1. 家长情绪失控（吼叫、发脾气）
2. 孩子受惊吓、哭泣、退缩
3. 游戏失败、挫折反应
4. 拒绝配合、抗拒
5. 明确的负面情绪（焦虑、恐惧、愤怒）

## 额外提取信息

对于负面事件，需要额外提取：
- **severity**: 严重程度（high/medium/low）
- **impact_duration_days**: 预计影响天数
- **triggers**: 触发因素列表（活动、对象、人物、情境）
- **parent_emotion**: 家长情绪
- **parent_needs_support**: 家长是否需要支持
- **child_reaction**: 孩子的反应
- **avoidance_needed**: 是否需要避让
- **avoidance_period_days**: 避让期天数
- **alternative_activities**: 替代活动建议

## 提取原则

1. **敏感识别**: 准确识别负面事件
2. **影响评估**: 评估事件的严重程度和影响
3. **触发分析**: 识别具体的触发因素
4. **支持建议**: 提供家长支持和替代方案
"""
