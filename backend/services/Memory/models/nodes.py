"""
Graphiti 节点模型定义
基于记忆驱动架构的7种核心节点类型
"""
from dataclasses import dataclass, field
from typing import Optional, Literal, Dict, List, Any
from datetime import datetime


@dataclass
class Person:
    """
    人物节点 - 系统中的所有参与者
    
    包括：孩子、家长、老师、朋友、兄弟姐妹等
    """
    node_type: str = "Person"
    person_id: str = ""
    person_type: Literal["child", "parent", "teacher", "peer", "sibling", "other"] = "child"
    name: str = ""
    role: str = ""  # 具体角色，如"妈妈"、"爸爸"、"主治疗师"、"小明（朋友）"
    basic_info: Dict[str, Any] = field(default_factory=dict)
    # basic_info 包含: age, gender, relationship_to_child 等
    created_at: str = ""


@dataclass
class Behavior:
    """
    行为节点 - 观察到的具体行为事件
    """
    node_type: str = "Behavior"
    behavior_id: str = ""
    child_id: str = ""
    timestamp: str = ""
    event_type: Literal["social", "emotion", "communication", "firstTime", "other"] = "other"
    description: str = ""
    raw_input: str = ""
    input_type: Literal["voice", "text", "quick_button", "video_ai"] = "text"
    significance: Literal["breakthrough", "improvement", "normal", "concern"] = "normal"
    ai_analysis: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    evidence: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Object:
    """
    对象节点 - 玩具、物品等实体对象
    
    注意：category 不在节点上，而是通过边关联到兴趣维度
    """
    node_type: str = "Object"
    object_id: str = ""
    name: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    usage: Dict[str, Any] = field(default_factory=dict)
    # usage 包含: total_games, last_used, effectiveness


@dataclass
class InterestDimension:
    """
    兴趣维度节点 - 8类兴趣的固定节点
    
    系统中只有8个兴趣维度节点（固定）：
    - visual（视觉类）
    - auditory（听觉类）
    - tactile（触觉类）
    - motor（运动类）
    - construction（建构类）
    - order（秩序类）
    - cognitive（认知类）
    - social（社交类）
    
    注意：评估数据不在节点上，而是在边的属性中
    """
    node_type: str = "InterestDimension"
    interest_id: str = ""
    name: Literal["visual", "auditory", "tactile", "motor", "construction", "order", "cognitive", "social"] = "visual"
    display_name: str = ""
    description: str = ""


@dataclass
class FunctionDimension:
    """
    功能维度节点 - 33个功能维度的固定节点
    
    系统中有33个功能维度节点（固定），分为6大类：
    - sensory（感觉能力）：5个维度
    - social（社交互动）：6个维度
    - language（语言沟通）：6个维度
    - motor（运动躯体）：6个维度
    - emotional（情绪适应）：5个维度
    - self_care（自理能力）：5个维度
    
    注意：评估数据不在节点上，而是在边的属性中
    """
    node_type: str = "FunctionDimension"
    function_id: str = ""
    name: str = ""  # 如 "eye_contact", "social_smile" 等
    display_name: str = ""
    category: Literal["sensory", "social", "language", "motor", "emotional", "self_care"] = "social"
    description: str = ""


@dataclass
class FloorTimeGame:
    """
    地板游戏节点 - 游戏方案及实施记录
    """
    node_type: str = "FloorTimeGame"
    game_id: str = ""
    child_id: str = ""
    name: str = ""
    description: str = ""
    created_at: str = ""
    status: Literal["recommended", "scheduled", "in_progress", "completed", "cancelled"] = "recommended"
    design: Dict[str, Any] = field(default_factory=dict)
    # design 包含: target_dimension, goals, interest_points_used, recommended_objects, steps, materials_needed, precautions
    implementation: Dict[str, Any] = field(default_factory=dict)
    # implementation 包含: implementer_id, participants, session_date, actual_duration, video_analysis, parent_feedback, scores, behavior_ids, session_summary


@dataclass
class ChildAssessment:
    """
    儿童评估节点 - 综合评估结果
    
    注意：具体的维度评估数据不在节点上，而是在边的属性中
    """
    node_type: str = "ChildAssessment"
    assessment_id: str = ""
    child_id: str = ""
    assessor_id: str = ""
    timestamp: str = ""
    assessment_type: Literal["comprehensive", "interest_mining", "trend_analysis", "initial"] = "comprehensive"
    analysis: Dict[str, Any] = field(default_factory=dict)
    recommendations: Dict[str, Any] = field(default_factory=dict)
    
    # 初始评估相关字段
    summary: str = ""
    strengths: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    fedc_level: Optional[int] = None
    dimension_scores: Dict[str, Any] = field(default_factory=dict)
    interests: List[str] = field(default_factory=list)
    created_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# 节点类型映射
NODE_TYPES = {
    "Person": Person,
    "Behavior": Behavior,
    "Object": Object,
    "InterestDimension": InterestDimension,
    "FunctionDimension": FunctionDimension,
    "FloorTimeGame": FloorTimeGame,
    "ChildAssessment": ChildAssessment
}
