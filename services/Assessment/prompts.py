"""
评估模块 Prompt 模板
"""
import json
from typing import Optional, List, Dict, Any
from src.models.assessment import InterestHeatmap, DimensionTrends


def serialize_for_json(obj):
    """
    递归处理对象，将 DateTime、mappingproxy 等不可序列化的对象转换为可序列化格式
    
    Args:
        obj: 要序列化的对象
        
    Returns:
        可 JSON 序列化的对象
    """
    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, 'isoformat'):  # DateTime 对象
        return obj.isoformat()
    elif isinstance(obj, type(type.__dict__)):  # mappingproxy
        return dict(obj)
    elif hasattr(obj, '__dict__') and not isinstance(obj, type):  # Pydantic 模型等（排除类本身）
        return serialize_for_json(obj.__dict__)
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    else:
        # 尝试转换为字符串
        try:
            return str(obj)
        except:
            return f"<non-serializable: {type(obj).__name__}>"


def build_interest_mining_prompt(
    behaviors: List[Dict[str, Any]],
    recent_games: List[Dict[str, Any]],
    previous_interest: Optional[Dict[str, Any]],
    time_range_days: int
) -> str:
    """
    构建兴趣挖掘 Agent 的 Prompt
    
    重点：
    - 智能衰减（持续兴趣不衰减，短暂兴趣快速衰减）
    - 识别真实兴趣 vs 假设兴趣
    - 发现意外兴趣
    - 评估兴趣广度
    """
    
    # 构建行为摘要
    behaviors_summary = ""
    if behaviors:
        behaviors_summary = "### 最近的行为记录\n"
        for b in behaviors[:30]:  # 只取前30条
            timestamp = b.get('timestamp', '')
            description = b.get('description', '')
            event_type = b.get('event_type', '')
            significance = b.get('significance', '')
            behaviors_summary += f"- [{timestamp}] {description} (类型: {event_type}, 重要性: {significance})\n"
    else:
        behaviors_summary = "### 最近的行为记录\n暂无行为记录。\n"
    
    # 构建游戏摘要
    games_summary = ""
    if recent_games:
        games_summary = "### 最近的游戏总结\n"
        for g in recent_games[:5]:  # 只取前5个
            name = g.get('name', '未命名游戏')
            status = g.get('status', 'unknown')
            implementation = g.get('implementation', {})
            summary = implementation.get('summary', '')
            games_summary += f"\n**游戏：{name}** (状态: {status})\n"
            if summary:
                games_summary += f"总结：{summary[:200]}...\n"
            
            # 提取兴趣验证结果
            highlights = implementation.get('highlights', [])
            if highlights:
                games_summary += "亮点：\n"
                for h in highlights[:3]:
                    games_summary += f"  - {h}\n"
    else:
        games_summary = "### 最近的游戏总结\n暂无游戏记录。\n"
    
    # 构建上一次兴趣评估
    previous_summary = ""
    if previous_interest:
        previous_summary = f"""
### 上一次兴趣评估（用于对比）
{json.dumps(serialize_for_json(previous_interest), ensure_ascii=False, indent=2)}
"""
    else:
        previous_summary = "### 上一次兴趣评估\n暂无历史评估数据。\n"
    
    # 组装完整 Prompt
    system_prompt = f"""
你是一位专业的 ASD（自闭症谱系障碍）儿童兴趣分析师。
你的任务是基于行为记录和游戏总结，挖掘孩子的真实兴趣，生成兴趣热力图数据。

**重要：请用中文回复。**

## 数据范围
- 时间范围：最近 {time_range_days} 天
- 数据来源：行为记录、游戏总结、历史评估

{behaviors_summary}

{games_summary}

{previous_summary}

## 分析要求

### 1. 智能衰减（核心）
- **持续兴趣**：如果孩子在多次行为记录或游戏中反复表现出对某个对象的兴趣，该兴趣的强度**不应衰减**，甚至应该**增强**
- **短暂兴趣**：如果孩子只在某一次行为中表现出兴趣，后续没有再出现，该兴趣应该**快速衰减**
- **时间权重**：越近期的行为，权重越高
- **质量权重**：主动性、持续时间、参与度高的行为，权重更高

### 2. 真实兴趣 vs 假设兴趣
- **真实兴趣**：孩子主动参与、持续时间长、参与度高、情绪积极
- **假设兴趣**：档案中标记为兴趣，但实际游戏中反应冷淡、参与度低
- **明确标注**：在 `interest_type` 字段中标注 "verified"（已验证）或 "assumed"（假设）

### 3. 意外发现
- 游戏中的"意外时刻"往往揭示孩子的真实兴趣
- 比如对包装纸、背景音乐、光影变化、玩具盒子的图案等
- 这些意外发现比预设的兴趣点更重要
- 在 `unexpected_interests` 字段中列出所有意外发现

### 4. 兴趣广度（重要）
- 孤独症孩子的兴趣很难挖掘，兴趣多样性特别重要
- 评估兴趣的广度：孩子的兴趣是否局限在某一类对象？
- 在 `breadth_analysis` 字段中给出兴趣广度评估
- 如果兴趣过于狭窄，在建议中提出扩展兴趣的方向

### 5. 数据稀疏性处理
- 假设家长初期只提供少量数据（5-10条行为记录）
- 即使数据少，也要给出有价值的洞察
- 明确标注数据量和置信度
- 在 `data_quality` 字段中说明数据量和分析的可靠性

### 6. 趋势判断
- 对比上一次兴趣评估（如果有）
- 判断每个兴趣的趋势：上升（increasing）、稳定（stable）、下降（decreasing）
- 在 `trend` 字段中标注趋势

## 输出格式

请以 JSON 格式返回兴趣热力图数据，**必须包含**以下字段：

- interests: 兴趣点列表（数组）
  - interest_name: 兴趣名称
  - intensity: 强度（0-10，考虑衰减后的加权分数）
  - trend: 趋势（increasing/stable/decreasing）
  - interest_type: 类型（verified/assumed）
  - evidence: 证据列表（具体的行为或游戏时刻）
  - last_observed: 最后观察时间
  - frequency: 出现频率
  - engagement_quality: 参与质量（high/medium/low）

- unexpected_interests: 意外发现的兴趣点（数组）
  - interest_name: 兴趣名称
  - discovery_context: 发现场景
  - potential: 潜力评估

- breadth_analysis: 兴趣广度分析
  - total_interests: 总兴趣数量
  - diversity_score: 多样性评分（0-10）
  - dominant_categories: 主导类别
  - expansion_suggestions: 扩展建议

- data_quality: 数据质量说明
  - total_behaviors: 行为记录数量
  - total_games: 游戏数量
  - confidence_level: 置信度（high/medium/low）
  - notes: 备注

- summary: 总结（200字以内）

**请用中文生成完整的兴趣热力图分析报告，以 JSON 格式返回。**
"""
    
    return system_prompt.strip()



def build_dimension_analysis_prompt(
    behaviors: List[Dict[str, Any]],
    recent_games: List[Dict[str, Any]],
    previous_function: Optional[Dict[str, Any]],
    time_range_days: int
) -> str:
    """
    构建功能分析 Agent 的 Prompt
    
    重点：
    - 识别质变（主动性、持续性、泛化性、复杂性）
    - 弹性判断（即使数据少也给出初步判断）
    - 维度关联
    """
    
    # 构建行为摘要
    behaviors_summary = ""
    if behaviors:
        behaviors_summary = "### 最近的行为记录\n"
        for b in behaviors[:30]:  # 只取前30条
            timestamp = b.get('timestamp', '')
            description = b.get('description', '')
            event_type = b.get('event_type', '')
            significance = b.get('significance', '')
            ai_analysis = b.get('ai_analysis', {})
            behaviors_summary += f"- [{timestamp}] {description} (类型: {event_type}, 重要性: {significance})\n"
            if ai_analysis:
                behaviors_summary += f"  AI分析: {json.dumps(serialize_for_json(ai_analysis), ensure_ascii=False)}\n"
    else:
        behaviors_summary = "### 最近的行为记录\n暂无行为记录。\n"
    
    # 构建游戏摘要
    games_summary = ""
    if recent_games:
        games_summary = "### 最近的游戏总结\n"
        for g in recent_games[:5]:  # 只取前5个
            name = g.get('name', '未命名游戏')
            status = g.get('status', 'unknown')
            implementation = g.get('implementation', {})
            summary = implementation.get('summary', '')
            target_dimension = g.get('design', {}).get('target_dimension', '')
            games_summary += f"\n**游戏：{name}** (目标维度: {target_dimension}, 状态: {status})\n"
            if summary:
                games_summary += f"总结：{summary[:200]}...\n"
    else:
        games_summary = "### 最近的游戏总结\n暂无游戏记录。\n"
    
    # 构建上一次功能评估
    previous_summary = ""
    if previous_function:
        previous_summary = f"""
### 上一次功能评估（用于对比）
{json.dumps(serialize_for_json(previous_function), ensure_ascii=False, indent=2)}
"""
    else:
        previous_summary = "### 上一次功能评估\n暂无历史评估数据。\n"
    
    # 组装完整 Prompt
    system_prompt = f"""
你是一位专业的 ASD（自闭症谱系障碍）儿童发展评估师。
你的任务是基于行为记录和游戏总结，分析孩子在各个功能维度的表现和趋势。

**重要：请用中文回复。**

## 数据范围
- 时间范围：最近 {time_range_days} 天
- 数据来源：行为记录、游戏总结、历史评估

{behaviors_summary}

{games_summary}

{previous_summary}

## 分析要求

### 1. 识别质变（核心）
关注行为的**质**而非**量**，重点分析以下四个维度：

- **主动性（Initiative）**：从被动到主动
  - 被动：需要家长引导、提示才会参与
  - 主动：自己发起行为、主动寻求互动
  - 质变标志：孩子开始主动发起某个行为

- **持续性（Persistence）**：从短暂到持久
  - 短暂：只能维持几秒钟或几分钟
  - 持久：能够持续较长时间（10分钟以上）
  - 质变标志：持续时间显著增加

- **泛化性（Generalization）**：从特定情境到多种情境
  - 特定：只在某个特定场景下表现
  - 泛化：能在多种场景下表现相同能力
  - 质变标志：能力开始迁移到新场景

- **复杂性（Complexity）**：从简单到复杂
  - 简单：单一动作、简单模仿
  - 复杂：多步骤、创造性、灵活应用
  - 质变标志：行为复杂度显著提升

### 2. 识别活跃维度
- 根据数据，识别哪些维度有明显的活动和进展
- 不要强行分析所有33个维度，只关注有数据支持的维度
- 在 `active_dimensions` 字段中列出活跃维度

### 3. 趋势判断
- 对比上一次功能评估（如果有）
- 判断每个维度的趋势：上升（improving）、稳定（stable）、下降（declining）
- 在 `trend` 字段中标注趋势
- 提供趋势的证据和分析

### 4. 维度关联
- 分析不同维度之间的关联
- 比如：眼神接触的改善是否带动了社交互动的提升？
- 在 `dimension_correlations` 字段中说明维度之间的关联

### 5. 数据稀疏性处理（重要）
- 假设家长初期只提供少量数据（5-10条行为记录）
- 即使数据少，也要给出有价值的初步判断
- 使用"弹性判断"：明确标注置信度，给出初步结论
- 在 `data_quality` 字段中说明数据量和分析的可靠性

### 6. 避免过度解读
- 如果某个维度没有数据，不要编造
- 明确标注"数据不足"或"暂无观察"
- 在 `notes` 字段中说明数据限制

## 输出格式

请以 JSON 格式返回功能维度趋势数据，**必须包含**以下字段：

- dimensions: 维度列表（数组，只包含有数据的维度）
  - dimension_name: 维度名称
  - current_level: 当前水平（0-10）
  - trend: 趋势（improving/stable/declining）
  - quality_changes: 质变分析
    - initiative: 主动性变化
    - persistence: 持续性变化
    - generalization: 泛化性变化
    - complexity: 复杂性变化
  - evidence: 证据列表（具体的行为或游戏时刻）
  - confidence: 置信度（high/medium/low）

- active_dimensions: 活跃维度列表（有明显活动的维度）

- dimension_correlations: 维度关联分析（数组）
  - dimension_a: 维度A
  - dimension_b: 维度B
  - correlation_type: 关联类型（positive/negative/neutral）
  - description: 关联描述

- data_quality: 数据质量说明
  - total_behaviors: 行为记录数量
  - total_games: 游戏数量
  - confidence_level: 整体置信度（high/medium/low）
  - notes: 备注

- summary: 总结（200字以内）

**请用中文生成完整的功能维度趋势分析报告，以 JSON 格式返回。**
"""
    
    return system_prompt.strip()


def build_comprehensive_assessment_prompt(
    interest_heatmap: InterestHeatmap,
    dimension_trends: DimensionTrends,
    recent_games: List[Dict[str, Any]],
    previous_assessment: Optional[Dict[str, Any]],
    time_range_days: int
) -> str:
    """
    构建综合评估 Agent 的 Prompt
    
    重点：
    - 三明治结构（肯定→关注→建议）
    - 家长友好
    - 可操作建议
    """
    
    # 构建兴趣热力图摘要
    interest_summary = f"""
### 兴趣热力图分析（Agent 1 输出）
{json.dumps(serialize_for_json(interest_heatmap.dict()), ensure_ascii=False, indent=2)}
"""
    
    # 构建功能维度趋势摘要
    dimension_summary = f"""
### 功能维度趋势分析（Agent 2 输出）
{json.dumps(serialize_for_json(dimension_trends.dict()), ensure_ascii=False, indent=2)}
"""
    
    # 构建游戏摘要
    games_summary = ""
    if recent_games:
        games_summary = "### 最近的游戏总结\n"
        for g in recent_games[:5]:  # 只取前5个
            name = g.get('name', '未命名游戏')
            status = g.get('status', 'unknown')
            implementation = g.get('implementation', {})
            summary = implementation.get('summary', '')
            games_summary += f"\n**游戏：{name}** (状态: {status})\n"
            if summary:
                games_summary += f"总结：{summary[:200]}...\n"
    else:
        games_summary = "### 最近的游戏总结\n暂无游戏记录。\n"
    
    # 构建上一次综合评估
    previous_summary = ""
    if previous_assessment:
        serializable_assessment = serialize_for_json(previous_assessment)
        previous_summary = f"""
### 上一次综合评估（用于对比）
{json.dumps(serializable_assessment, ensure_ascii=False, indent=2)}
"""
    else:
        previous_summary = "### 上一次综合评估\n暂无历史评估数据。\n"
    
    # 组装完整 Prompt
    system_prompt = f"""
你是一位经验丰富的 ASD（自闭症谱系障碍）儿童综合评估师。
你的任务是整合兴趣分析和功能分析的结果，生成家长友好的综合评估报告。

**重要：请用中文回复。**

## 数据范围
- 时间范围：最近 {time_range_days} 天
- 数据来源：兴趣热力图、功能维度趋势、游戏总结、历史评估

{interest_summary}

{dimension_summary}

{games_summary}

{previous_summary}

## 评估要求

### 1. 三明治结构（核心）
评估报告必须采用"三明治"结构，让家长感受到支持和鼓励：

**第一层：肯定（Affirmation）**
- 开头先肯定孩子的进步和亮点
- 具体描述孩子做得好的地方
- 让家长感受到孩子的成长
- 语气温暖、鼓励

**第二层：关注（Concerns）**
- 客观指出需要关注的领域
- 不要使用负面词汇（如"问题"、"缺陷"）
- 使用中性词汇（如"需要关注"、"可以改进"）
- 提供具体的观察和证据

**第三层：建议（Suggestions）**
- 提供具体、可操作的建议
- 建议要切实可行，考虑家长的实际能力
- 给出明确的下一步行动
- 语气积极、充满希望

### 2. 家长友好
- 避免过多专业术语
- 使用通俗易懂的语言
- 提供具体的例子和场景
- 语气温暖、支持

### 3. 可操作性
- 建议要具体、可执行
- 提供明确的步骤和方法
- 考虑家长的时间和精力
- 优先级明确

### 4. 整合分析
- 将兴趣分析和功能分析结合起来
- 发现兴趣和功能之间的关联
- 提供整体的发展图景

### 5. 趋势观察
- 对比上一次评估（如果有）
- 指出进步和变化
- 识别长期趋势

## 输出格式

请以 JSON 格式返回完整评估报告，**必须包含**以下字段：

- overall_assessment: 整体发展评价（300-500字，采用三明治结构）
  - 第一段：肯定和亮点
  - 第二段：需要关注的领域
  - 第三段：积极的展望和鼓励

- strengths: 优势领域（数组，3-5个）
  - area: 领域名称
  - description: 具体描述
  - evidence: 证据

- areas_of_focus: 需要关注的领域（数组，2-3个）
  - area: 领域名称
  - description: 具体描述
  - why_important: 为什么重要
  - evidence: 证据

- recommendations: 可操作建议（数组，5-8条）
  - category: 类别（interest_expansion/skill_development/daily_practice/game_design）
  - title: 建议标题
  - description: 详细描述
  - action_steps: 具体步骤（数组）
  - priority: 优先级（high/medium/low）
  - expected_outcome: 预期效果

- interest_development_plan: 兴趣发展计划
  - current_interests: 当前兴趣总结
  - expansion_directions: 扩展方向（数组）
  - integration_suggestions: 如何将兴趣融入干预

- skill_development_plan: 技能发展计划
  - priority_dimensions: 优先发展的维度（数组）
  - quality_focus: 质变关注点
  - practice_suggestions: 练习建议

- next_steps: 下一步行动（数组，3-5条）
  - step: 步骤描述
  - timeline: 时间线
  - success_criteria: 成功标准

- parent_support: 给家长的话
  - encouragement: 鼓励的话
  - tips: 小贴士（数组）

**请用中文生成完整的综合评估报告，以 JSON 格式返回。语气要温暖、支持、充满希望。**
"""
    
    return system_prompt.strip()


__all__ = [
    'build_interest_mining_prompt',
    'build_dimension_analysis_prompt',
    'build_comprehensive_assessment_prompt'
]
