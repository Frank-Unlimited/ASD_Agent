"""
LLM Prompts 模板
用于智能解析家长的观察记录
"""

# ============ 行为解析 Prompt ============

BEHAVIOR_PARSE_PROMPT = """你是一个专业的 ASD 儿童行为分析师。请分析家长的观察记录，提取结构化信息。

【输入】
{raw_input}

【任务】
1. 判断事件类型（从以下选择一个）：
   - social: 社交互动相关（如：主动分享、眼神接触、回应他人）
   - emotion: 情绪表达相关（如：开心、生气、哭泣、焦虑）
   - communication: 沟通表达相关（如：说话、手势、指认）
   - firstTime: 首次出现的新行为
   - other: 其他类型

2. 判断重要性（从以下选择一个）：
   - breakthrough: 突破性进步（首次出现的积极行为，具有里程碑意义）
   - improvement: 改善（已有行为的提升或频率增加）
   - normal: 正常（日常行为，无特殊意义）
   - concern: 关注点（负面事件、退步、需要关注的行为）

3. 提取涉及的对象（玩具/物品名称，如果没有则返回空数组）
   **重要**：对象包括但不限于：
   - 玩具：积木、球、玩具车、娃娃、拼图等
   - 书籍：绘本、图书、故事书、卡片等
   - 日常物品：镜子、水杯、勺子、衣服等
   - 电子产品：平板、手机、电视等
   - 其他物品：任何孩子接触、使用、观察的具体物品
   
   **提取规则**：
   - 如果描述中提到具体物品名称，必须提取
   - "听绘本" → 提取"绘本"
   - "玩积木" → 提取"积木"
   - "看电视" → 提取"电视"

4. 推断相关的兴趣类别（从以下8类中选择，可多选）：
   - visual: 视觉类（彩色积木、拼图、光影玩具、旋转齿轮）
   - auditory: 听觉类（儿歌、乐器、自然音、机械声）
   - tactile: 触觉类（黏土、沙子、水、软胶玩具）
   - motor: 运动类（滑梯、秋千、蹦床、骑车、抛接球）
   - construction: 建构类（乐高、磁力片、积木、拆装玩具）
   - order: 秩序类（排序玩具、分类盒、叠叠乐）
   - cognitive: 认知类（数字卡片、字母书、地图、动物模型）
   - social: 社交类（回合制游戏、角色扮演、互动绘本）

5. 推断相关的功能维度（从以下选择，可多选）：
   感觉能力：visual_response, auditory_response, tactile_response, pain_response, taste_smell
   社交能力：eye_contact, social_initiation, social_response, joint_attention, peer_interaction, empathy
   语言能力：receptive_language, expressive_language, nonverbal_communication, conversation_skills
   运动能力：gross_motor, fine_motor, body_coordination, motor_planning
   情绪能力：emotional_expression, emotional_regulation, anxiety_level, frustration_tolerance, self_awareness
   自理能力：eating, toileting, dressing, hygiene, safety_awareness

6. 生成简洁的行为描述（20字以内，客观描述行为本身）

7. 提取上下文信息：
   - activity: 正在进行的活动（如：积木游戏、户外玩耍）
   - location: 地点（如：家里客厅、幼儿园、康复中心）
   - duration: 持续时间（如果提到）

【输出格式】
请以 JSON 格式返回，不要包含任何其他文字：
{{
    "event_type": "...",
    "significance": "...",
    "description": "...",
    "objects_involved": ["...", "..."],
    "related_interests": ["...", "..."],
    "related_functions": ["...", "..."],
    "context": {{
        "activity": "...",
        "location": "...",
        "duration": "..."
    }},
    "ai_analysis": {{
        "category": "行为类别（如：主动社交互动、情绪调节、语言表达）",
        "impact": "对孩子发展的意义（如：从被动回应转向主动发起）",
        "first_time": true/false
    }}
}}
"""

# ============ 负面事件检测 Prompt ============

NEGATIVE_EVENT_DETECT_PROMPT = """你是一个专业的 ASD 儿童心理分析师。请分析这段描述，判断是否是负面事件，并提取关键信息。

【输入】
{raw_input}

【负面事件定义】
可能对孩子造成心理影响的事件，包括但不限于：
- 家长情绪失控（吼叫、发脾气、打骂）
- 孩子受惊吓或创伤（被吓哭、恐惧、退缩）
- 游戏中的负面体验（强迫、压力过大、失败挫折）
- 同伴冲突（被欺负、被排斥）
- 感官过载（噪音、人群、刺激过强）

【关键词识别】
负面关键词：吼、哭、害怕、退缩、自责、失控、发脾气、吓、拒绝、抗拒、崩溃、尖叫

【任务】
1. 判断是否是负面事件（true/false）
   - 如果包含负面关键词，通常是负面事件
   - 如果家长表达自责、后悔，通常是负面事件

2. 判断严重程度：
   - low: 轻微（孩子短暂不适，很快恢复）
   - medium: 中等（孩子明显不适，需要时间恢复）
   - high: 严重（孩子受惊吓、哭泣、拒绝互动，可能造成心理影响）

3. 预估影响持续天数（3-14天）：
   - low: 3-5天
   - medium: 5-7天
   - high: 7-14天

4. 提取触发因素（可能触发回忆的活动/人物/情境/对象）：
   - 活动类：如"积木游戏"、"户外活动"、"高难度任务"
   - 人物类：如"妈妈参与"、"爸爸在场"、"老师引导"
   - 情境类：如"要求配合"、"时间压力"、"人多环境"
   - 对象类：如"特定玩具"、"特定声音"

5. 分析家长情绪（从描述中提取）：
   - 如：焦虑、疲惫、自责、愤怒、无助、后悔

6. 判断是否需要支持（true/false）：
   - 如果家长表达自责、后悔、无助，通常需要支持
   - 如果事件严重程度为 high，通常需要支持

7. 记录孩子的反应（从描述中提取）：
   - 如：哭泣、退缩、拒绝互动、眼神回避、身体僵硬

【输出格式】
请以 JSON 格式返回，不要包含任何其他文字：
{{
    "is_negative_event": true/false,
    "severity": "low/medium/high",
    "impact_duration_days": 7,
    "triggers": ["...", "...", "..."],
    "parent_emotion": "...",
    "parent_needs_support": true/false,
    "child_reaction": "...",
    "avoidance_suggestions": ["建议1", "建议2"]
}}

【注意】
- 如果不是负面事件，只需返回 {{"is_negative_event": false}}
- 触发因素要具体，便于后续游戏推荐时避让
"""

# ============ 兴趣维度映射 ============

INTEREST_CATEGORIES = {
    "visual": "视觉类",
    "auditory": "听觉类",
    "tactile": "触觉类",
    "motor": "运动类",
    "construction": "建构类",
    "order": "秩序类",
    "cognitive": "认知类",
    "social": "社交类"
}

# ============ 功能维度映射 ============

FUNCTION_DIMENSIONS = {
    # 感觉能力（5个）
    "visual_response": "视觉反应",
    "auditory_response": "听觉反应",
    "tactile_response": "触觉反应",
    "pain_response": "痛觉反应",
    "taste_smell": "味觉嗅觉",
    
    # 社交能力（6个）
    "eye_contact": "眼神接触",
    "social_initiation": "社交主动性",
    "social_response": "社交回应",
    "joint_attention": "共同注意",
    "peer_interaction": "同伴互动",
    "empathy": "共情能力",
    
    # 语言能力（4个）
    "receptive_language": "语言理解",
    "expressive_language": "语言表达",
    "nonverbal_communication": "非语言沟通",
    "conversation_skills": "对话技巧",
    
    # 运动能力（4个）
    "gross_motor": "大运动",
    "fine_motor": "精细运动",
    "body_coordination": "身体协调",
    "motor_planning": "运动计划",
    
    # 情绪能力（5个）
    "emotional_expression": "情绪表达",
    "emotional_regulation": "情绪调节",
    "anxiety_level": "焦虑水平",
    "frustration_tolerance": "挫折容忍",
    "self_awareness": "自我意识",
    
    # 自理能力（5个）
    "eating": "进食",
    "toileting": "如厕",
    "dressing": "穿衣",
    "hygiene": "卫生",
    "safety_awareness": "安全意识"
}

# ============ 兴趣挖掘 Prompt ============

INTEREST_MINING_PROMPT = """你是一个专业的 ASD 儿童兴趣分析师。请分析孩子最近的行为记录，挖掘兴趣偏好和趋势。

【行为记录摘要】
{behaviors_summary}

【8类兴趣维度】
1. visual（视觉类）：彩色积木、拼图、光影玩具、旋转齿轮、条纹图案、动画片段
2. auditory（听觉类）：儿歌、乐器声、自然音、机械声、有声书、节奏打击乐
3. tactile（触觉类）：黏土、沙子、水、软胶玩具、毛绒材质、光滑积木
4. motor（运动类）：滑梯、秋千、蹦床、骑车、抛接球、转圈游戏
5. construction（建构类）：乐高、磁力片、积木、拆装玩具、折纸、齿轮组
6. order（秩序类）：排序玩具、分类盒、叠叠乐、物品摆放游戏
7. cognitive（认知类）：数字卡片、字母书、地图、车标图、动物模型
8. social（社交类）：回合制游戏、角色扮演玩具、互动绘本

【任务】
1. 评估每个兴趣类别的水平（high/medium/low/none）
2. 列出每个类别下孩子喜欢的具体物品
3. 识别兴趣趋势（emerging/stable/declining）
4. 生成总结和建议

【输出格式】
请以 JSON 格式返回：
{{
    "interests": {{
        "visual": {{
            "level": "high/medium/low/none",
            "items": ["具体物品1", "具体物品2"],
            "evidence_count": 5,
            "notes": "简短说明"
        }},
        "auditory": {{ ... }},
        "tactile": {{ ... }},
        "motor": {{ ... }},
        "construction": {{ ... }},
        "order": {{ ... }},
        "cognitive": {{ ... }},
        "social": {{ ... }}
    }},
    "trends": {{
        "emerging": ["social"],
        "stable": ["visual", "construction"],
        "declining": []
    }},
    "summary": {{
        "dominant_interests": ["visual", "construction"],
        "potential_interests": ["social"],
        "recommendations": [
            "利用视觉兴趣带动社交互动",
            "通过建构游戏培养合作能力"
        ]
    }}
}}
"""

# ============ 功能趋势分析 Prompt ============

FUNCTION_TREND_PROMPT = """你是一个专业的 ASD 儿童发展评估师。请分析孩子最近的行为记录，评估功能维度的表现和趋势。

【行为记录摘要】
{behaviors_summary}

【上次评估结果】
{previous_assessment}

【33个功能维度】
感觉能力（5个）：visual_response, auditory_response, tactile_response, pain_response, taste_smell
社交能力（6个）：eye_contact, social_initiation, social_response, joint_attention, peer_interaction, empathy
语言能力（4个）：receptive_language, expressive_language, nonverbal_communication, conversation_skills
运动能力（4个）：gross_motor, fine_motor, body_coordination, motor_planning
情绪能力（5个）：emotional_expression, emotional_regulation, anxiety_level, frustration_tolerance, self_awareness
自理能力（5个）：eating, toileting, dressing, hygiene, safety_awareness

【评分标准】
0-10分，其中：
- 0-3分：需要大量支持
- 4-6分：需要部分支持
- 7-8分：基本独立
- 9-10分：完全独立

【任务】
1. 评估每个维度的当前得分（0-10分）
2. 与上次评估对比，判断趋势（improving/stable/declining）
3. 列出每个维度的证据行为ID
4. 计算6大类的平均分
5. 生成总结和建议

【输出格式】
请以 JSON 格式返回：
{{
    "dimensions": {{
        "visual_response": {{
            "score": 7.5,
            "trend": "improving/stable/declining",
            "evidence_count": 3,
            "notes": "简短说明"
        }},
        "eye_contact": {{ ... }},
        ... (其他31个维度)
    }},
    "category_scores": {{
        "sensory": {{"avg": 6.5, "trend": "stable"}},
        "social": {{"avg": 5.2, "trend": "improving"}},
        "language": {{"avg": 4.8, "trend": "stable"}},
        "motor": {{"avg": 7.1, "trend": "stable"}},
        "emotional": {{"avg": 5.5, "trend": "improving"}},
        "self_care": {{"avg": 4.2, "trend": "stable"}}
    }},
    "summary": {{
        "strengths": ["视觉反应", "大运动"],
        "challenges": ["语言表达", "自理能力"],
        "improving_areas": ["眼神接触", "情绪调节"],
        "focus_recommendations": [
            "继续强化眼神接触训练",
            "增加语言表达机会"
        ]
    }}
}}
"""

# ============ 综合评估 Prompt ============

COMPREHENSIVE_ASSESSMENT_PROMPT = """你是一个专业的 ASD 儿童综合评估师。请基于兴趣挖掘和功能趋势分析，生成综合评估报告。

【兴趣挖掘结果】
{interest_mining}

【功能趋势分析】
{function_trend}

【最近游戏总结】
{recent_games}

【上次综合评估】
{previous_assessment}

【任务】
1. 综合分析孩子的优势领域
2. 识别需要关注的挑战领域
3. 确定训练优先级（基于兴趣和功能的交叉分析）
4. 生成具体的干预建议
5. 总结整体进展

【输出格式】
请以 JSON 格式返回：
{{
    "strengths": [
        {{
            "area": "视觉认知",
            "description": "对彩色积木和拼图表现出高度兴趣，视觉反应得分7.5",
            "leverage_strategy": "利用视觉优势带动其他领域发展"
        }}
    ],
    "challenges": [
        {{
            "area": "语言表达",
            "description": "语言表达得分4.8，主动表达较少",
            "intervention_priority": "high/medium/low"
        }}
    ],
    "priorities": [
        {{
            "rank": 1,
            "dimension": "eye_contact",
            "reason": "近期有改善趋势，可以通过视觉兴趣强化",
            "target_score": 8.0,
            "timeline": "4周"
        }}
    ],
    "recommendations": [
        "通过积木游戏增加眼神接触机会",
        "利用孩子对视觉刺激的兴趣，设计互动游戏",
        "在建构活动中融入语言表达训练"
    ],
    "progress_summary": {{
        "overall_trend": "positive/stable/concerning",
        "key_achievements": ["首次主动递积木", "眼神接触频率增加"],
        "areas_needing_attention": ["语言表达", "情绪调节"],
        "next_steps": "继续强化社交互动，增加语言输入"
    }}
}}
"""

# ============ 游戏总结 Prompt ============

GAME_SUMMARY_PROMPT = """你是一个专业的地板时光游戏分析师。请基于游戏信息、视频分析和家长反馈，生成游戏总结。

【游戏信息】
{game_info}

【视频分析结果】
{video_analysis}

【家长反馈】
{parent_feedback}

【任务】
1. 评估孩子参与度（0-10分）
2. 评估目标达成情况（0-10分）
3. 识别关键时刻（突破/挑战）
4. 提取需要记录的关键行为
5. 生成下次改进建议

【输出格式】
请以 JSON 格式返回：
{{
    "engagement_score": 8.5,
    "goal_achievement_score": 7.0,
    "highlights": [
        "🌟 首次主动递积木给家长",
        "📈 眼神接触5次，比上次增加2次",
        "💪 专注时长达到15分钟"
    ],
    "concerns": [
        "中途出现短暂的情绪波动",
        "对某个步骤表现出抗拒"
    ],
    "key_behaviors": [
        {{
            "timestamp": "02:15",
            "description": "主动递积木并眼神注视",
            "significance": "breakthrough",
            "event_type": "social"
        }}
    ],
    "session_summary": "本次游戏孩子参与度高，首次出现主动递积木行为，这是一个重要的社交主动性突破。眼神接触频率也有明显提升。建议下次继续使用积木，进一步强化这个行为。",
    "improvement_suggestions": [
        "下次可以增加游戏难度，引入更多互动环节",
        "注意观察孩子的情绪信号，及时调整节奏",
        "可以尝试引入其他视觉类玩具，扩展兴趣范围"
    ],
    "parent_notes": "家长反馈孩子今天状态很好，建议继续保持这个游戏频率"
}}
"""
