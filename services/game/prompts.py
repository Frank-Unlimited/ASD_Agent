"""
游戏推荐 Prompt 模板
"""
from typing import Optional, Any
from src.models.profile import ChildProfile


def build_game_recommendation_prompt(
    child_profile: ChildProfile,
    recent_assessments: Optional[str],
    recent_games: Optional[str],
    focus_dimension: Optional[str],
    duration_preference: Optional[int]
) -> str:
    """
    构建游戏推荐的 System Prompt
    
    Args:
        child_profile: 孩子档案
        recent_assessments: 近期评估结果摘要（从 MemoryService 获取）
        recent_games: 近期游戏总结（从 MemoryService 获取）
        focus_dimension: 用户希望关注的维度
        duration_preference: 用户期望的时长（分钟）
        
    Returns:
        System Prompt 字符串
    """
    # 构建孩子档案信息
    profile_info = f"""
## 孩子档案
- 姓名：{child_profile.name}
- 年龄：{_calculate_age(child_profile.birth_date)}
- 诊断：{child_profile.diagnosis or '未知'} ({child_profile.diagnosis_level.value if child_profile.diagnosis_level else '未知程度'})
"""
    
    # 发展维度信息
    if child_profile.development_dimensions:
        profile_info += "\n### 发展维度评估\n"
        for dim in child_profile.development_dimensions:
            level_desc = f"{dim.current_level}/10" if dim.current_level else "未评估"
            profile_info += f"- {dim.dimension_name}: {level_desc}\n"
    
    # 兴趣点信息
    if child_profile.interests:
        profile_info += "\n### 兴趣点\n"
        for interest in child_profile.interests:
            intensity_desc = f"(强度: {interest.intensity}/10)" if interest.intensity else ""
            profile_info += f"- {interest.name} {intensity_desc}\n"

    # 近期评估信息
    assessment_info = ""
    if recent_assessments:
        assessment_info = f"""
## 近期评估趋势
{recent_assessments}
"""
    else:
        assessment_info = """
## 近期评估趋势
暂无近期评估数据。
"""
    
    # 近期游戏信息
    game_history_info = ""
    if recent_games:
        game_history_info = f"""
## 近期游戏总结
{recent_games}
"""
    else:
        game_history_info = """
## 近期游戏总结
暂无近期游戏记录。
"""
    
    # 用户偏好
    preference_info = "\n## 本次推荐要求\n"
    if focus_dimension:
        preference_info += f"- 重点关注维度：{focus_dimension}\n"
    if duration_preference:
        preference_info += f"- 期望时长：{duration_preference} 分钟\n"
    if not focus_dimension and not duration_preference:
        preference_info += "- 无特殊要求，请根据孩子当前情况推荐最合适的游戏\n"
    
    # 组装完整 Prompt
    system_prompt = f"""
你是一位经验丰富的 ASD（自闭症谱系障碍）儿童地板时光干预专家。
你的任务是根据孩子的档案、近期评估趋势和游戏历史，推荐一个完整的地板时光游戏方案。

**重要：请用中文回复，所有游戏内容、步骤、建议都必须使用中文。**

{profile_info}

{assessment_info}

{game_history_info}

{preference_info}

## 推荐要求

1. **个性化设计**：
   - 充分考虑孩子的兴趣点，将其融入游戏设计
   - 根据发展维度评估，选择合适的难度和目标
   - 参考近期评估趋势，针对性地设计干预内容

2. **游戏结构**：
   - 提供清晰的游戏步骤（3-8 个步骤）
   - 每个步骤包含：标题、详细描述、家长动作、期待孩子反应、小贴士
   - 明确所需材料和环境布置

3. **目标明确**：
   - 设定主要目标和次要目标
   - 提供可衡量的成功标准
   - 说明设计依据（为什么推荐这个游戏）

4. **安全和注意事项**：
   - 提供安全注意事项
   - 提醒情绪调节要点
   - 给出环境准备建议

5. **使用 RAG 工具**：
   - 你可以使用 search_games 工具检索游戏知识库
   - 参考已有的成功案例和游戏模板
   - 但要根据孩子的具体情况进行个性化调整

**请用中文设计一个完整的游戏方案，以 JSON 格式返回。所有字段内容都必须是中文。**
"""
    
    return system_prompt.strip()


def _calculate_age(birth_date: str) -> str:
    """计算年龄"""
    from datetime import datetime
    try:
        birth = datetime.fromisoformat(birth_date.replace('Z', '+00:00'))
        today = datetime.now()
        age_years = today.year - birth.year
        age_months = today.month - birth.month
        
        if age_months < 0:
            age_years -= 1
            age_months += 12
        
        if age_years > 0:
            return f"{age_years}岁{age_months}个月"
        else:
            return f"{age_months}个月"
    except:
        return "未知"


__all__ = ['build_game_recommendation_prompt']



def build_game_summary_prompt(
    child_profile: ChildProfile,
    game_plan: Any,  # GamePlan
    session: Any,  # GameSession
    recent_assessments: Optional[str],
    recent_games: Optional[str]
) -> str:
    """
    构建游戏总结的 System Prompt
    
    Args:
        child_profile: 孩子档案
        game_plan: 游戏原始方案
        session: 游戏会话（包含实施数据）
        recent_assessments: 近期评估结果摘要（从 MemoryService 获取）
        recent_games: 近期游戏总结（从 MemoryService 获取）
        
    Returns:
        System Prompt 字符串
    """
    # 构建孩子档案信息
    profile_info = f"""
## 孩子档案
- 姓名：{child_profile.name}
- 年龄：{_calculate_age(child_profile.birth_date)}
- 诊断：{child_profile.diagnosis or '未知'} ({child_profile.diagnosis_level.value if child_profile.diagnosis_level else '未知程度'})
"""
    
    # 发展维度信息
    if child_profile.development_dimensions:
        profile_info += "\n### 发展维度基线\n"
        for dim in child_profile.development_dimensions:
            level_desc = f"{dim.current_level}/10" if dim.current_level else "未评估"
            profile_info += f"- {dim.dimension_name}: {level_desc}\n"
    
    # 兴趣点信息
    if child_profile.interests:
        profile_info += "\n### 兴趣点\n"
        for interest in child_profile.interests:
            intensity_desc = f"(强度: {interest.intensity}/10)" if interest.intensity else ""
            profile_info += f"- {interest.name} {intensity_desc}\n"
    
    # 游戏原始方案
    game_plan_info = f"""
## 游戏原始方案
### 基本信息
- 游戏标题：{game_plan.title}
- 游戏描述：{game_plan.description}
- 预计时长：{game_plan.estimated_duration} 分钟
- 主要目标维度：{game_plan.target_dimension.value}

### 游戏目标
- 主要目标：{game_plan.goals.primary_goal}
"""
    
    if game_plan.goals.secondary_goals:
        game_plan_info += "- 次要目标：\n"
        for goal in game_plan.goals.secondary_goals:
            game_plan_info += f"  * {goal}\n"
    
    if game_plan.goals.success_criteria:
        game_plan_info += "- 成功标准：\n"
        for criteria in game_plan.goals.success_criteria:
            game_plan_info += f"  * {criteria}\n"
    
    # 游戏步骤
    game_plan_info += "\n### 游戏步骤\n"
    for step in game_plan.steps:
        game_plan_info += f"{step.step_number}. {step.title}\n"
        game_plan_info += f"   {step.description[:100]}...\n"
    
    # 设计依据
    game_plan_info += f"\n### 设计依据\n{game_plan.design_rationale}\n"
    
    # 实施数据
    actual_duration = session.actual_duration or "未记录"
    duration_diff = ""
    if session.actual_duration and game_plan.estimated_duration:
        diff = session.actual_duration - game_plan.estimated_duration
        duration_diff = f"（{'超出' if diff > 0 else '少于'}预期 {abs(diff)} 分钟）"
    
    implementation_info = f"""
## 实施数据
### 基本信息
- 实施日期：{session.start_time.strftime('%Y-%m-%d %H:%M')}
- 实际时长：{actual_duration} 分钟 {duration_diff}
- 会话状态：{session.status.value}
"""
    
    # 家长观察记录
    if session.parent_observations:
        implementation_info += "\n### 家长观察记录（实时记录）\n"
        for obs in session.parent_observations:
            time_str = obs.timestamp.strftime('%H:%M')
            implementation_info += f"\n**[{time_str}]** {obs.content}\n"
            if obs.child_behavior:
                implementation_info += f"- 孩子表现：{obs.child_behavior}\n"
            if obs.parent_feeling:
                implementation_info += f"- 家长感受：{obs.parent_feeling}\n"
    else:
        implementation_info += "\n### 家长观察记录\n暂无实时观察记录。\n"
    
    # AI 视频分析
    if session.has_video and session.video_analysis:
        va = session.video_analysis
        implementation_info += f"""
### AI 视频分析
- 视频时长：{va.duration_seconds} 秒
"""
        if va.behavior_analysis:
            implementation_info += f"- 行为分析：{va.behavior_analysis}\n"
        if va.emotional_analysis:
            implementation_info += f"- 情绪分析：{va.emotional_analysis}\n"
        if va.ai_insights:
            implementation_info += "- AI 洞察：\n"
            for insight in va.ai_insights:
                implementation_info += f"  * {insight}\n"
        if va.key_moments:
            implementation_info += f"- 关键时刻数量：{len(va.key_moments)} 个\n"
    else:
        implementation_info += "\n### AI 视频分析\n暂无视频分析数据。\n"
    
    # 家长反馈表
    implementation_info += "\n### 家长反馈表\n"
    if session.child_engagement_score is not None:
        implementation_info += f"- 孩子参与度评分：{session.child_engagement_score}/10\n"
    if session.goal_achievement_score is not None:
        implementation_info += f"- 目标达成度评分：{session.goal_achievement_score}/10\n"
    if session.parent_satisfaction_score is not None:
        implementation_info += f"- 家长满意度评分：{session.parent_satisfaction_score}/10\n"
    if session.notes:
        implementation_info += f"- 备注：{session.notes}\n"
    
    if (session.child_engagement_score is None and 
        session.goal_achievement_score is None and 
        session.parent_satisfaction_score is None):
        implementation_info += "暂无家长评分数据。\n"
    
    # 历史上下文
    context_info = ""
    if recent_assessments:
        context_info += f"""
## 近期评估结果
{recent_assessments}
"""
    else:
        context_info += """
## 近期评估结果
暂无近期评估数据。
"""
    
    if recent_games:
        context_info += f"""
## 近期游戏总结
{recent_games}
"""
    else:
        context_info += """
## 近期游戏总结
暂无近期游戏记录。
"""
    
    # 组装完整 Prompt
    system_prompt = f"""
你是一位经验丰富的 ASD（自闭症谱系障碍）儿童地板时光干预专家和评估师。
你的任务是基于游戏实施数据，生成客观、专业、可操作的总结报告。

**重要：请用中文回复，所有总结内容都必须使用中文。**

{profile_info}

{game_plan_info}

{implementation_info}

{context_info}

## 总结要求

1. **客观性**：
   - 基于实际数据和观察，避免主观臆断
   - 引用具体的行为、时刻和数据
   - 区分事实陈述和推测

2. **具体性**：
   - 描述具体行为，而非抽象评价
   - 引用具体时间点和场景
   - 提供可量化的观察

3. **平衡性**：
   - 既要肯定亮点和进步
   - 也要客观指出挑战和改进空间
   - 避免过度乐观或悲观

4. **可操作性**：
   - 建议要具体、可执行
   - 提供明确的下一步行动
   - 考虑家长的实际操作能力

5. **趋势性**：
   - 结合历史数据（如果有）
   - 观察进展趋势
   - 识别模式和规律

6. **家长友好**：
   - 语言温暖、鼓励
   - 避免过多专业术语
   - 提供情感支持

7. **数据完整性处理**：
   - 如果某些数据缺失（如视频分析、家长观察），基于现有数据进行总结
   - 在 data_sources_used 字段中列出实际使用的数据来源
   - 不要编造不存在的数据

## 输出格式

请以 JSON 格式返回完整的总结报告，包含以下字段：

- overall_assessment: 整体评价（200-300字，全面总结本次游戏）
- success_level: 成功程度（excellent/good/fair/poor）
- goal_achievement: 目标达成情况（包含 primary_goal_achieved, achievement_details 等）
- dimension_progress: 各维度进展评估（数组，每个维度的表现）
- child_performance: 孩子表现分析（参与度、情绪状态、注意力等）
- highlights: 亮点时刻（3-5个）
- areas_for_improvement: 需要改进的地方（2-3个）
- parent_feedback: 对家长表现的反馈和建议
- recommendations_for_next: 下次游戏的建议（3-5条）
- trend_observation: 趋势观察（如果有历史数据）
- data_sources_used: 使用的数据来源列表

**请用中文生成完整的总结报告，以 JSON 格式返回。**
"""
    
    return system_prompt.strip()
