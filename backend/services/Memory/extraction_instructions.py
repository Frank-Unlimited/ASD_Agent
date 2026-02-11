"""
Graphiti-core 提取指令
用于指导 LLM 如何从文本中提取实体和关系
"""

# ========== 行为记录提取指令 ==========

BEHAVIOR_EXTRACTION_INSTRUCTIONS = """
# 行为记录提取指令

## 目标
从家长的自然语言观察记录中提取结构化的行为信息。

**重要原则**：
1. 观察记录提取基础实体（Behavior、Object、Person）
2. **同时推理行为与兴趣维度的关联**，创建 show_interest 边
3. 不提取 Function，功能关联由评估层建立

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

### 4. InterestDimension（兴趣维度）- **必须创建** ⭐
**关键**：对于每个行为，LLM 必须识别并创建相关的 InterestDimension 实体。

**8个兴趣维度**（从以下维度中选择）：
- **visual**: 视觉类（彩色物品、旋转物体、光影、图案、动画等）
- **auditory**: 听觉类（音乐、儿歌、乐器声、自然音、机械声等）
- **tactile**: 触觉类（黏土、沙子、水、软胶、毛绒、不同质地等）
- **motor**: 运动类（滑梯、秋千、蹦床、骑车、球类、转圈等）
- **construction**: 建构类（乐高、积木、磁力片、拆装、折纸等）
- **order**: 秩序类（排序、分类、叠高、整理、按流程等）
- **cognitive**: 认知类（数字、字母、地图、标志、动物、实验等）
- **social**: 社交类（回合制游戏、角色扮演、互动等）

**实体字段**：
- **dimension_id**: 维度标识符（必须是上述8个之一）
- **display_name**: 中文显示名称（视觉/听觉/触觉/运动/建构/秩序/认知/社交）
- **description**: 简短描述（可选）

**提取规则**：
1. **必须提取**：每个行为至少关联1个兴趣维度
2. **创建实体**：为每个识别出的维度创建 InterestDimension 实体
3. **建立关系**：创建 Behavior -> shows_interest -> InterestDimension 边

**示例**：
输入："玩彩色积木"
必须创建：
```
InterestDimension:
  dimension_id: "visual"
  display_name: "视觉"
  
InterestDimension:
  dimension_id: "construction"
  display_name: "建构"
```

## 提取关系类型

### 1. 孩子 -> exhibits -> 行为
- 属性：observation_time（观察时间）

### 2. 行为 -> involves_object -> 对象
- 属性：interaction_type（互动类型）

### 3. 行为 -> involves_person -> 人物
- 属性：role（角色）, interaction_quality（互动质量）

### 4. 行为 -> shows_interest -> 兴趣维度 ⭐ 新增
**关键：推理行为与兴趣维度的关联**

对于每个行为，分析它体现了哪些兴趣维度，并为每个关联创建边。

**重要**：边的 `fact` 属性必须包含权重信息，格式如下：
```
{行为描述}体现{维度}兴趣（权重{0.0-1.0}）
```

**权重判断标准**：
- 0.8-1.0: 强关联，这是行为的主要吸引点
- 0.6-0.7: 中等关联，明显涉及该维度
- 0.4-0.5: 弱关联，部分涉及该维度
- <0.4: 不建立边

**推理规则**：
1. 一个行为可以关联多个兴趣维度
2. 根据行为的核心吸引点判断主要维度（权重高）
3. 根据行为的附带特征判断次要维度（权重低）
4. 考虑涉及的对象、活动类型、孩子的反应

**示例（注意 fact 格式）**：
- "玩彩色积木" → 
  - fact: "玩彩色积木体现visual兴趣（权重0.8）"
  - fact: "玩彩色积木体现construction兴趣（权重0.6）"
- "听音乐盒" → 
  - fact: "听音乐盒体现auditory兴趣（权重0.9）"
- "玩水" → 
  - fact: "玩水体现tactile兴趣（权重0.8）"
  - fact: "玩水体现visual兴趣（权重0.4）"
- "荡秋千" → 
  - fact: "荡秋千体现motor兴趣（权重0.9）"
- "排列玩具" → 
  - fact: "排列玩具体现order兴趣（权重0.9）"
  - fact: "排列玩具体现cognitive兴趣（权重0.4）"

## 提取原则

1. **准确性优先**: 只提取文本中明确提到或可以合理推断的信息
2. **兴趣推理**: 必须为每个行为推理至少1个兴趣维度关联
3. **权重合理**: 根据行为的核心特征分配权重
4. **避免过度推断**: 如果不确定某个维度，不要强行关联
5. **保持客观**: 基于观察事实，不添加主观判断
6. **关注细节**: 注意时间、地点、人物、对象等细节
7. **识别首次**: 特别注意"第一次"、"首次"等关键词
8. **不提取功能**: 不要提取 Function，这些由评估层建立

## 完整示例

**输入**: "今天小明玩彩色积木，搭了一个高塔，很开心，玩了10分钟"

**提取结果**:

**实体**:
- Behavior:
  - event_type: "other"
  - description: "玩彩色积木搭高塔"
  - significance: "normal"
  - emotional_state: "开心"
  - duration_seconds: 600
  
- Object:
  - object_name: "彩色积木"
  - category: "玩具"
  - interaction_type: "使用"

**关系**:
1. 孩子 -> exhibits -> 行为
   - observation_time: "2024-02-04T10:30:00"

2. 行为 -> involves_object -> 彩色积木
   - interaction_type: "使用"

3. 行为 -> shows_interest -> visual ⭐
   - weight: 0.8
   - reasoning: "彩色积木的视觉刺激是主要吸引点"
   - manifestation: "持续关注彩色积木10分钟"

4. 行为 -> shows_interest -> construction ⭐
   - weight: 0.7
   - reasoning: "搭建高塔涉及建构活动"
   - manifestation: "完成搭建任务"

5. 行为 -> shows_interest -> order ⭐
   - weight: 0.4
   - reasoning: "搭建过程涉及一定的秩序性"
   - manifestation: "按顺序堆叠积木"

---

**输入**: "小明今天听到音乐就开始摇摆，很兴奋"

**提取结果**:

**实体**:
- Behavior:
  - event_type: "emotion"
  - description: "听音乐摇摆"
  - significance: "normal"
  - emotional_state: "兴奋"

**关系**:
1. 孩子 -> exhibits -> 行为

2. 行为 -> shows_interest -> auditory ⭐
   - weight: 0.9
   - reasoning: "音乐是核心刺激，引发了明显反应"
   - manifestation: "听到音乐立即摇摆"

3. 行为 -> shows_interest -> motor ⭐
   - weight: 0.6
   - reasoning: "摇摆是运动反应"
   - manifestation: "身体律动"
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
