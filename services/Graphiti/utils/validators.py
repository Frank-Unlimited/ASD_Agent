"""
数据验证工具
"""
from typing import Dict, Any
from ..models.nodes import Person, Behavior, Object, FloorTimeGame, ChildAssessment


def validate_person(person: Person) -> None:
    """
    验证人物节点数据
    
    Args:
        person: 人物节点
        
    Raises:
        ValueError: 数据验证失败
    """
    if not person.name:
        raise ValueError("name 不能为空")
    
    if person.person_type not in ["child", "parent", "teacher", "peer", "sibling", "other"]:
        raise ValueError(f"person_type 必须是 child/parent/teacher/peer/sibling/other 之一，当前是 '{person.person_type}'")


def validate_behavior(behavior: Behavior) -> None:
    """
    验证行为节点数据
    
    Args:
        behavior: 行为节点
        
    Raises:
        ValueError: 数据验证失败
    """
    if not behavior.child_id:
        raise ValueError("child_id 不能为空")
    
    if not behavior.description:
        raise ValueError("description 不能为空")
    
    if behavior.event_type not in ["social", "emotion", "communication", "firstTime", "other"]:
        raise ValueError(f"event_type 必须是 social/emotion/communication/firstTime/other 之一，当前是 '{behavior.event_type}'")
    
    if behavior.input_type not in ["voice", "text", "quick_button", "video_ai"]:
        raise ValueError(f"input_type 必须是 voice/text/quick_button/video_ai 之一，当前是 '{behavior.input_type}'")
    
    if behavior.significance not in ["breakthrough", "improvement", "normal", "concern"]:
        raise ValueError(f"significance 必须是 breakthrough/improvement/normal/concern 之一，当前是 '{behavior.significance}'")


def validate_object(obj: Object) -> None:
    """
    验证对象节点数据
    
    Args:
        obj: 对象节点
        
    Raises:
        ValueError: 数据验证失败
    """
    if not obj.name:
        raise ValueError("name 不能为空")


def validate_node_data(node_type: str, data: Dict[str, Any]) -> bool:
    """
    验证节点数据完整性（字典格式）
    
    Args:
        node_type: 节点类型
        data: 节点数据
        
    Returns:
        是否有效
    """
    required_fields = {
        "Person": ["person_id", "person_type", "name"],
        "Behavior": ["behavior_id", "child_id", "timestamp", "description"],
        "Object": ["object_id", "name"],
        "InterestDimension": ["interest_id", "name", "display_name"],
        "FunctionDimension": ["function_id", "name", "display_name", "category"],
        "FloorTimeGame": ["game_id", "child_id", "name"],
        "ChildAssessment": ["assessment_id", "child_id", "timestamp"]
    }
    
    if node_type not in required_fields:
        return False
    
    for field in required_fields[node_type]:
        if field not in data or not data[field]:
            return False
    
    return True


def validate_edge_data(edge_type: str, properties: Dict[str, Any]) -> bool:
    """
    验证边数据完整性
    
    Args:
        edge_type: 边类型
        properties: 边属性
        
    Returns:
        是否有效
    """
    # 核心边需要时间戳
    time_required_edges = ["具有兴趣", "具有功能", "评估兴趣", "评估功能"]
    
    if edge_type in time_required_edges:
        if "timestamp" not in properties or not properties["timestamp"]:
            return False
    
    # 具有兴趣边需要 level
    if edge_type == "具有兴趣":
        if "level" not in properties:
            return False
    
    # 具有功能边需要 score
    if edge_type == "具有功能":
        if "score" not in properties:
            return False
    
    return True
