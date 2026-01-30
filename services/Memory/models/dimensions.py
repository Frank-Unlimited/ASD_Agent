"""
维度配置定义
包含8类兴趣维度和33个功能维度的配置
"""
from typing import Dict, Any, List


# ============ 8类兴趣维度配置 ============

INTEREST_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    "visual": {
        "display_name": "视觉类",
        "description": "对视觉刺激的兴趣",
        "examples": ["彩色积木", "拼图", "光影玩具", "绘本", "旋转齿轮", "条纹图案", "动画片段"]
    },
    "auditory": {
        "display_name": "听觉类",
        "description": "对听觉刺激的兴趣",
        "examples": ["儿歌", "乐器声", "自然音", "机械声", "有声书", "节奏打击乐", "人声故事"]
    },
    "tactile": {
        "display_name": "触觉类",
        "description": "对触觉刺激的兴趣",
        "examples": ["黏土", "沙子", "水", "软胶玩具", "毛绒材质", "光滑积木", "纹理卡片"]
    },
    "motor": {
        "display_name": "运动类",
        "description": "对运动活动的兴趣",
        "examples": ["滑梯", "秋千", "蹦床", "骑车", "抛接球", "转圈游戏", "感统平衡木"]
    },
    "construction": {
        "display_name": "建构类",
        "description": "对建构活动的兴趣",
        "examples": ["乐高", "磁力片", "积木", "拆装玩具", "折纸", "手工材料", "齿轮组"]
    },
    "order": {
        "display_name": "秩序类",
        "description": "对秩序和规律的兴趣",
        "examples": ["排序玩具", "分类盒", "叠叠乐", "物品摆放游戏", "流程卡片"]
    },
    "cognitive": {
        "display_name": "认知类",
        "description": "对认知学习的兴趣",
        "examples": ["数字卡片", "字母书", "地图", "车标图", "动物模型", "实验玩具"]
    },
    "social": {
        "display_name": "社交类",
        "description": "对社交互动的兴趣",
        "examples": ["回合制游戏（传球/躲猫猫）", "角色扮演玩具", "互动绘本"]
    }
}


# ============ 33个功能维度配置 ============

FUNCTION_DIMENSIONS: Dict[str, Dict[str, Any]] = {
    # 感觉能力（5个）
    "visual_response": {
        "display_name": "视觉反应",
        "category": "sensory",
        "description": "凝视、回避、余光",
        "scale_source": "ABC-6,34,44,52,57 / CARS-7"
    },
    "auditory_response": {
        "display_name": "听觉反应",
        "category": "sensory",
        "description": "对声音敏感/迟钝",
        "scale_source": "ABC-10,21,39 / CARS-8"
    },
    "tactile_response": {
        "display_name": "触觉反应",
        "category": "sensory",
        "description": "触摸偏好/回避",
        "scale_source": "ABC-51 / CARS-9"
    },
    "pain_response": {
        "display_name": "痛觉反应",
        "category": "sensory",
        "description": "过敏/迟钝",
        "scale_source": "ABC-26 / CARS-9"
    },
    "taste_smell": {
        "display_name": "味觉嗅觉",
        "category": "sensory",
        "description": "舔、闻物品",
        "scale_source": "ABC-51 / CARS-9"
    },
    
    # 社交互动（6个）
    "eye_contact": {
        "display_name": "眼神接触",
        "category": "social",
        "description": "眼神交流的频率和质量",
        "scale_source": "ABC-24,47 / CARS-1 / M-CHAT-10"
    },
    "social_smile": {
        "display_name": "社交性微笑",
        "category": "social",
        "description": "回应性和主动性微笑",
        "scale_source": "ABC-7 / M-CHAT-12"
    },
    "social_interest": {
        "display_name": "社交兴趣",
        "category": "social",
        "description": "对他人的兴趣",
        "scale_source": "ABC-3,38 / CARS-1 / M-CHAT-2"
    },
    "imitation": {
        "display_name": "模仿能力",
        "category": "social",
        "description": "动作和语言模仿",
        "scale_source": "ABC-33 / CARS-2 / M-CHAT-13"
    },
    "joint_attention": {
        "display_name": "共同注意力",
        "category": "social",
        "description": "分享注意力焦点",
        "scale_source": "M-CHAT-7,9,15,17"
    },
    "social_initiation": {
        "display_name": "社交发起",
        "category": "social",
        "description": "主动发起社交互动",
        "scale_source": "ABC-3 / M-CHAT-19"
    },
    
    # 语言沟通（6个）
    "language_comprehension": {
        "display_name": "语言理解",
        "category": "language",
        "description": "对指令和语言的理解",
        "scale_source": "ABC-4,20,37 / M-CHAT-21"
    },
    "language_expression": {
        "display_name": "语言表达",
        "category": "language",
        "description": "主动语言表达能力",
        "scale_source": "ABC-42,56 / CARS-11"
    },
    "pronoun_use": {
        "display_name": "代词使用",
        "category": "language",
        "description": "代词的正确使用",
        "scale_source": "ABC-8,18"
    },
    "echolalia": {
        "display_name": "仿说",
        "category": "language",
        "description": "重复语言/仿说",
        "scale_source": "ABC-32,46,48"
    },
    "non_verbal_communication": {
        "display_name": "非语言沟通",
        "category": "language",
        "description": "手势、指向等",
        "scale_source": "ABC-29 / CARS-12 / M-CHAT-6"
    },
    "speech_prosody": {
        "display_name": "语音语调",
        "category": "language",
        "description": "说话的节奏和语调",
        "scale_source": "ABC-11 / CARS-11"
    },
    
    # 运动躯体（6个）
    "stereotyped_movement": {
        "display_name": "刻板动作",
        "category": "motor",
        "description": "拍手、旋转、摇摆等",
        "scale_source": "ABC-1,12,16,22,40 / CARS-4"
    },
    "body_coordination": {
        "display_name": "身体协调性",
        "category": "motor",
        "description": "动作协调程度",
        "scale_source": "ABC-13 / CARS-4"
    },
    "activity_level": {
        "display_name": "活动水平",
        "category": "motor",
        "description": "过度活跃或不足",
        "scale_source": "CARS-13"
    },
    "gait_posture": {
        "display_name": "步态姿势",
        "category": "motor",
        "description": "脚尖走路等异常步态",
        "scale_source": "ABC-16,30 / CARS-4"
    },
    "self_injury": {
        "display_name": "自伤行为",
        "category": "motor",
        "description": "撞头、咬手等",
        "scale_source": "ABC-35"
    },
    "aggression": {
        "display_name": "攻击行为",
        "category": "motor",
        "description": "对他人的攻击",
        "scale_source": "ABC-31"
    },
    
    # 情绪适应（5个）
    "emotional_expression": {
        "display_name": "情绪表达",
        "category": "emotional",
        "description": "情绪的外在表达",
        "scale_source": "CARS-3"
    },
    "emotional_response": {
        "display_name": "情绪反应",
        "category": "emotional",
        "description": "情绪反应的适当性",
        "scale_source": "ABC-17 / CARS-3"
    },
    "anxiety_level": {
        "display_name": "焦虑水平",
        "category": "emotional",
        "description": "焦虑和不安程度",
        "scale_source": "ABC-43 / CARS-10"
    },
    "change_adaptation": {
        "display_name": "环境适应",
        "category": "emotional",
        "description": "对环境变化的适应",
        "scale_source": "ABC-14 / CARS-6"
    },
    "frustration_tolerance": {
        "display_name": "挫折耐受",
        "category": "emotional",
        "description": "对挫折的耐受程度",
        "scale_source": "ABC-23,36"
    },
    
    # 自理能力（5个）
    "toileting": {
        "display_name": "如厕能力",
        "category": "self_care",
        "description": "大小便控制",
        "scale_source": "ABC-41"
    },
    "dressing": {
        "display_name": "穿衣能力",
        "category": "self_care",
        "description": "自己穿脱衣物",
        "scale_source": "ABC-45"
    },
    "feeding": {
        "display_name": "进食能力",
        "category": "self_care",
        "description": "独立进食",
        "scale_source": "-"
    },
    "safety_awareness": {
        "display_name": "安全意识",
        "category": "self_care",
        "description": "对危险的意识",
        "scale_source": "ABC-49"
    },
    "routine_skills": {
        "display_name": "日常技能",
        "category": "self_care",
        "description": "日常技能学习保持",
        "scale_source": "ABC-2"
    }
}


# 功能维度分类
FUNCTION_CATEGORIES = {
    "sensory": {
        "display_name": "感觉能力",
        "dimensions": ["visual_response", "auditory_response", "tactile_response", "pain_response", "taste_smell"]
    },
    "social": {
        "display_name": "社交互动",
        "dimensions": ["eye_contact", "social_smile", "social_interest", "imitation", "joint_attention", "social_initiation"]
    },
    "language": {
        "display_name": "语言沟通",
        "dimensions": ["language_comprehension", "language_expression", "pronoun_use", "echolalia", "non_verbal_communication", "speech_prosody"]
    },
    "motor": {
        "display_name": "运动躯体",
        "dimensions": ["stereotyped_movement", "body_coordination", "activity_level", "gait_posture", "self_injury", "aggression"]
    },
    "emotional": {
        "display_name": "情绪适应",
        "dimensions": ["emotional_expression", "emotional_response", "anxiety_level", "change_adaptation", "frustration_tolerance"]
    },
    "self_care": {
        "display_name": "自理能力",
        "dimensions": ["toileting", "dressing", "feeding", "safety_awareness", "routine_skills"]
    }
}


# ============ 辅助函数 ============

def get_interest_display_name(interest_name: str) -> str:
    """获取兴趣维度的显示名称"""
    return INTEREST_DIMENSIONS.get(interest_name, {}).get("display_name", interest_name)


def get_function_display_name(function_name: str) -> str:
    """获取功能维度的显示名称"""
    return FUNCTION_DIMENSIONS.get(function_name, {}).get("display_name", function_name)


def get_all_interest_names() -> List[str]:
    """获取所有兴趣维度名称"""
    return list(INTEREST_DIMENSIONS.keys())


def get_all_function_names() -> List[str]:
    """获取所有功能维度名称"""
    return list(FUNCTION_DIMENSIONS.keys())


def get_functions_by_category(category: str) -> List[str]:
    """获取某个类别下的所有功能维度"""
    return FUNCTION_CATEGORIES.get(category, {}).get("dimensions", [])
