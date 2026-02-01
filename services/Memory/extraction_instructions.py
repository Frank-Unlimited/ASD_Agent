"""
Graphiti-core 提取指令
用于指导 LLM 如何从文本中提取实体和关系
"""

# ========== 行为记录提取指令 ==========

BEHAVIOR_EXTRACTION_INSTRUCTIONS = """
# 行为记录提取指令

## 目标
从家长的自然语言观察记录中提取结构化的行为信息。

**重要原则**：观察记录只提取基础实体（Behavior、Object、Person），
不提取 Interest 和 Function。这些高级关联由评估层建立。

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

### 3. Person（人物）- 如果提到其他人则提取
- **person_name**: 人物名称（如：妈妈、爸爸、李老师）
- **role**: 角色（facilitator引导者/participant参与者/observer观察者）
- **interaction_quality**: 互动质量（positive/negative/neutral）

## 提取关系类型

### 1. 孩子 -> 展现 -> 行为
- 属性：observation_time（观察时间）

### 2. 行为 -> 涉及对象 -> 对象
- 属性：interaction_type（互动类型）

### 3. 行为 -> 涉及人物 -> 人物
- 属性：role（角色）, interaction_quality（互动质量）

## 提取原则

1. **准确性优先**: 只提取文本中明确提到或可以合理推断的信息
2. **避免过度推断**: 如果不确定，不要强行提取
3. **保持客观**: 基于观察事实，不添加主观判断
4. **关注细节**: 注意时间、地点、人物、对象等细节
5. **识别首次**: 特别注意"第一次"、"首次"等关键词
6. **不提取高级关联**: 不要提取 Interest 和 Function，这些由评估层建立

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

- 关系:
  - 孩子 -> 展现 -> 行为
  - 行为 -> 涉及对象 -> 积木

**注意**: 不提取 Interest（如 social、construction）和 Function（如 eye_contact、social_initiation），
这些关联将由评估服务在分析历史数据时建立。
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
