"""
数据转换函数
用于将 Graphiti-core 的提取结果转换为原有的返回格式
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


def extract_event_type(episode_result: Any) -> str:
    """
    从 Graphiti episode 结果中提取事件类型
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        事件类型字符串
    """
    # 从提取的节点中查找 Behavior 实体
    for node in episode_result.nodes:
        if "Behavior" in node.labels:
            return node.attributes.get("event_type", "other")
    
    return "other"


def extract_description(episode_result: Any) -> str:
    """
    从 Graphiti episode 结果中提取行为描述
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        行为描述字符串
    """
    for node in episode_result.nodes:
        if "Behavior" in node.labels:
            return node.attributes.get("description", "")
    
    return ""


def extract_significance(episode_result: Any) -> str:
    """
    从 Graphiti episode 结果中提取重要性
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        重要性字符串
    """
    for node in episode_result.nodes:
        if "Behavior" in node.labels:
            return node.attributes.get("significance", "normal")
    
    return "normal"


def extract_objects(episode_result: Any) -> List[str]:
    """
    从 Graphiti episode 结果中提取涉及的对象
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        对象名称列表
    """
    objects = []
    
    for node in episode_result.nodes:
        if "Object" in node.labels:
            objects.append(node.attributes.get("object_name", ""))
    
    return objects


def extract_interests(episode_result: Any) -> List[str]:
    """
    从 Graphiti episode 结果中提取相关兴趣
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        兴趣维度名称列表
    """
    interests = []
    
    for node in episode_result.nodes:
        if "Interest" in node.labels:
            interests.append(node.attributes.get("interest_name", ""))
    
    return interests


def extract_functions(episode_result: Any) -> List[str]:
    """
    从 Graphiti episode 结果中提取相关功能
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        功能维度名称列表
    """
    functions = []
    
    for node in episode_result.nodes:
        if "Function" in node.labels:
            functions.append(node.attributes.get("function_name", ""))
    
    return functions


def build_ai_analysis(episode_result: Any) -> Dict[str, Any]:
    """
    从 Graphiti episode 结果构建 AI 分析数据
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        AI 分析字典
    """
    analysis = {
        "extracted_entities": len(episode_result.nodes),
        "extracted_relationships": len(episode_result.edges),
        "extraction_timestamp": datetime.now().isoformat(),
        "entities_by_type": {}
    }
    
    # 统计各类型实体数量
    for node in episode_result.nodes:
        # labels 是一个列表，包含 'Entity' 和具体类型
        for label in node.labels:
            if label != 'Entity':  # 跳过通用的 Entity 标签
                if label not in analysis["entities_by_type"]:
                    analysis["entities_by_type"][label] = 0
                analysis["entities_by_type"][label] += 1
    
    return analysis


def build_game_summary_content(
    game: Dict[str, Any],
    video_analysis: Optional[Dict[str, Any]],
    parent_feedback: Optional[Dict[str, Any]]
) -> str:
    """
    构建游戏总结的 episode 内容
    
    Args:
        game: 游戏信息
        video_analysis: 视频分析结果
        parent_feedback: 家长反馈
        
    Returns:
        episode 内容字符串
    """
    content_parts = []
    
    # 游戏基本信息
    content_parts.append(f"# 游戏信息")
    content_parts.append(f"游戏名称：{game.get('name', 'N/A')}")
    content_parts.append(f"游戏描述：{game.get('description', 'N/A')}")
    
    if game.get('design'):
        design = game['design']
        content_parts.append(f"目标维度：{design.get('target_dimension', 'N/A')}")
        if design.get('goals'):
            content_parts.append(f"主要目标：{design['goals'].get('primary_goal', 'N/A')}")
    
    # 视频分析
    if video_analysis:
        content_parts.append(f"\n# 视频分析")
        content_parts.append(f"时长：{video_analysis.get('duration', 'N/A')}")
        
        if video_analysis.get('key_moments'):
            content_parts.append(f"\n关键时刻：")
            for moment in video_analysis['key_moments']:
                content_parts.append(f"- [{moment.get('time', 'N/A')}] {moment.get('description', 'N/A')}")
    
    # 家长反馈
    if parent_feedback:
        content_parts.append(f"\n# 家长反馈")
        if parent_feedback.get('notes'):
            content_parts.append(parent_feedback['notes'])
    
    return "\n".join(content_parts)


def extract_summary_data(episode_result: Any) -> Dict[str, Any]:
    """
    从 Graphiti episode 结果中提取游戏总结数据
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        总结数据字典
    """
    summary_data = {
        "summary": "",
        "engagement_score": 0.0,
        "goal_achievement_score": 0.0,
        "highlights": [],
        "concerns": [],
        "improvement_suggestions": [],
        "key_behaviors": []
    }
    
    # 从节点中提取 GameSummary 实体
    for node in episode_result.nodes:
        if "GameSummary" in node.labels:
            summary_data["summary"] = node.attributes.get("session_summary", "")
            summary_data["engagement_score"] = node.attributes.get("engagement_score", 0.0)
            summary_data["goal_achievement_score"] = node.attributes.get("goal_achievement_score", 0.0)
            summary_data["highlights"] = node.attributes.get("highlights", [])
            summary_data["concerns"] = node.attributes.get("concerns", [])
            summary_data["improvement_suggestions"] = node.attributes.get("improvement_suggestions", [])
        
        elif "KeyBehavior" in node.labels:
            summary_data["key_behaviors"].append({
                "timestamp": node.attributes.get("timestamp", ""),
                "description": node.attributes.get("description", ""),
                "event_type": node.attributes.get("event_type", "other"),
                "significance": node.attributes.get("significance", "normal")
            })
    
    return summary_data


def build_assessment_content(
    child_id: str,
    assessment_type: str,
    historical_data: Dict[str, Any]
) -> str:
    """
    构建评估的 episode 内容
    
    Args:
        child_id: 孩子ID
        assessment_type: 评估类型
        historical_data: 历史数据（包含从 Graphiti 搜索得到的事实）
        
    Returns:
        episode 内容字符串
    """
    content_parts = []
    
    content_parts.append(f"# {assessment_type} 评估")
    content_parts.append(f"孩子ID：{child_id}")
    content_parts.append(f"评估时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 历史事实数据（从 Graphiti 搜索获得）
    if historical_data.get('facts'):
        content_parts.append(f"\n## 历史观察事实")
        content_parts.append(historical_data['facts'])
    
    # 评估类型说明
    if assessment_type == "interest_mining":
        content_parts.append(f"\n## 评估目标")
        content_parts.append("分析孩子的兴趣偏好，识别主要兴趣维度、兴趣强度和持续性、兴趣发展趋势、可利用的兴趣点。")
    elif assessment_type == "trend_analysis":
        content_parts.append(f"\n## 评估目标")
        content_parts.append("分析功能维度的发展趋势，识别进步的功能维度、需要加强的功能维度、功能发展速度、功能之间的关联。")
    elif assessment_type == "comprehensive":
        content_parts.append(f"\n## 评估目标")
        content_parts.append("全面评估孩子的发展状况，包括整体发展水平、优势和劣势、发展趋势、干预建议。")
    
    return "\n".join(content_parts)


def extract_assessment_data(episode_result: Any) -> Dict[str, Any]:
    """
    从 Graphiti episode 结果中提取评估数据
    
    Args:
        episode_result: Graphiti add_episode() 的返回结果
        
    Returns:
        评估数据字典
    """
    assessment_data = {
        "assessment_type": "",
        "summary": "",
        "key_findings": [],
        "recommendations": [],
        "confidence_score": 0.0,
        "analysis": {}
    }
    
    # 从节点中提取 Assessment 实体
    for node in episode_result.nodes:
        if "Assessment" in node.labels:
            assessment_data["assessment_type"] = node.attributes.get("assessment_type", "")
            assessment_data["summary"] = node.attributes.get("assessment_summary", "")
            assessment_data["key_findings"] = node.attributes.get("key_findings", [])
            assessment_data["recommendations"] = node.attributes.get("recommendations", [])
            assessment_data["confidence_score"] = node.attributes.get("confidence_score", 0.0)
            
            # 构建 analysis 字段（保持向后兼容）
            assessment_data["analysis"] = {
                "summary": assessment_data["summary"],
                "key_findings": assessment_data["key_findings"],
                "recommendations": assessment_data["recommendations"]
            }
    
    return assessment_data


def get_assessment_instructions(assessment_type: str) -> str:
    """
    根据评估类型获取对应的提取指令
    
    Args:
        assessment_type: 评估类型
        
    Returns:
        提取指令字符串
    """
    from .extraction_instructions import ASSESSMENT_EXTRACTION_INSTRUCTIONS
    
    # 可以根据不同的评估类型返回不同的指令
    # 目前统一使用基础指令
    return ASSESSMENT_EXTRACTION_INSTRUCTIONS


def convert_behavior_to_dict(behavior: Any) -> Dict[str, Any]:
    """
    将 Behavior 节点转换为字典格式
    
    Args:
        behavior: Behavior 节点对象
        
    Returns:
        字典格式的行为数据
    """
    if hasattr(behavior, '__dict__'):
        return {
            "behavior_id": getattr(behavior, 'behavior_id', ''),
            "child_id": getattr(behavior, 'child_id', ''),
            "timestamp": getattr(behavior, 'timestamp', ''),
            "event_type": getattr(behavior, 'event_type', 'other'),
            "description": getattr(behavior, 'description', ''),
            "raw_input": getattr(behavior, 'raw_input', ''),
            "input_type": getattr(behavior, 'input_type', 'text'),
            "significance": getattr(behavior, 'significance', 'normal'),
            "ai_analysis": getattr(behavior, 'ai_analysis', {}),
            "context": getattr(behavior, 'context', {}),
            "evidence": getattr(behavior, 'evidence', {})
        }
    
    return behavior if isinstance(behavior, dict) else {}


def convert_game_to_dict(game: Any) -> Dict[str, Any]:
    """
    将 Game 节点转换为字典格式
    
    Args:
        game: Game 节点对象
        
    Returns:
        字典格式的游戏数据
    """
    if hasattr(game, '__dict__'):
        return {
            "game_id": getattr(game, 'game_id', ''),
            "child_id": getattr(game, 'child_id', ''),
            "name": getattr(game, 'name', ''),
            "description": getattr(game, 'description', ''),
            "created_at": getattr(game, 'created_at', ''),
            "status": getattr(game, 'status', 'draft'),
            "design": getattr(game, 'design', {}),
            "implementation": getattr(game, 'implementation', {})
        }
    
    return game if isinstance(game, dict) else {}


def convert_assessment_to_dict(assessment: Any) -> Dict[str, Any]:
    """
    将 Assessment 节点转换为字典格式
    
    Args:
        assessment: Assessment 节点对象
        
    Returns:
        字典格式的评估数据
    """
    if hasattr(assessment, '__dict__'):
        return {
            "assessment_id": getattr(assessment, 'assessment_id', ''),
            "child_id": getattr(assessment, 'child_id', ''),
            "assessment_type": getattr(assessment, 'assessment_type', ''),
            "timestamp": getattr(assessment, 'timestamp', ''),
            "analysis": getattr(assessment, 'analysis', {}),
            "data_range": getattr(assessment, 'data_range', {}),
            "confidence": getattr(assessment, 'confidence', 0.0)
        }
    
    return assessment if isinstance(assessment, dict) else {}
