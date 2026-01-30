"""
维度配置定义
"""
from typing import Dict, Any, Optional


# 维度配置字典
DIMENSION_CONFIG: Dict[str, Dict[str, Any]] = {
    # 六大情绪里程碑
    "self_regulation": {
        "display_name": "自我调节",
        "category": "milestone",
        "description": "情绪和行为的自我控制能力",
        "value_type": "score",
        "max_value": 10
    },
    "intimacy": {
        "display_name": "亲密关系",
        "category": "milestone",
        "description": "与照护者建立情感联结的能力",
        "value_type": "score",
        "max_value": 10
    },
    "two_way_communication": {
        "display_name": "双向沟通",
        "category": "milestone",
        "description": "基本的一来一回互动能力",
        "value_type": "score",
        "max_value": 10
    },
    "complex_communication": {
        "display_name": "复杂沟通",
        "category": "milestone",
        "description": "多轮、复杂的沟通交流",
        "value_type": "score",
        "max_value": 10
    },
    "emotional_ideas": {
        "display_name": "情绪想法",
        "category": "milestone",
        "description": "表达和理解情绪的能力",
        "value_type": "score",
        "max_value": 10
    },
    "logical_thinking": {
        "display_name": "逻辑思维",
        "category": "milestone",
        "description": "因果推理和逻辑表达能力",
        "value_type": "score",
        "max_value": 10
    },

    # 行为观察维度
    "eye_contact": {
        "display_name": "眼神接触",
        "category": "behavior",
        "description": "与他人眼神交流的频率和时长",
        "value_type": "score",
        "max_value": 10
    },
    "spontaneous_smile": {
        "display_name": "主动微笑",
        "category": "behavior",
        "description": "自发的社交性微笑",
        "value_type": "count",
        "max_value": None
    },
    "verbal_attempt": {
        "display_name": "语言尝试",
        "category": "behavior",
        "description": "主动发声或说话的尝试",
        "value_type": "count",
        "max_value": None
    },
    "repetitive_behavior": {
        "display_name": "刻板行为",
        "category": "behavior",
        "description": "重复性动作或行为模式",
        "value_type": "score",
        "max_value": 10,
        "inverse": True  # 数值越低越好
    },
    "sensory_response": {
        "display_name": "感官反应",
        "category": "behavior",
        "description": "对感官刺激的反应模式",
        "value_type": "score",
        "max_value": 10
    },
    "social_initiation": {
        "display_name": "社交发起",
        "category": "behavior",
        "description": "主动发起社交互动",
        "value_type": "count",
        "max_value": None
    }
}


# 里程碑类型配置
MILESTONE_TYPES = {
    "first_time": {
        "display_name": "首次出现",
        "description": "该行为/能力首次被观察到",
        "significance": "high"
    },
    "breakthrough": {
        "display_name": "突破性进步",
        "description": "显著超越以往水平的表现",
        "significance": "high"
    },
    "significant_improvement": {
        "display_name": "显著改善",
        "description": "持续稳定的明显进步",
        "significance": "medium"
    },
    "consistency": {
        "display_name": "稳定表现",
        "description": "某项能力达到稳定可重复的水平",
        "significance": "medium"
    }
}


def get_display_name(dimension: str) -> str:
    """获取维度的显示名称"""
    config = DIMENSION_CONFIG.get(dimension, {})
    return config.get("display_name", dimension)


def get_dimension_config(dimension: str) -> Optional[Dict[str, Any]]:
    """获取维度配置"""
    return DIMENSION_CONFIG.get(dimension)


def get_all_dimensions() -> list:
    """获取所有维度名称"""
    return list(DIMENSION_CONFIG.keys())
