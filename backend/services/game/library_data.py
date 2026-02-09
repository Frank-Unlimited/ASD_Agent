"""
游戏库初始数据
"""
from src.models.game import TargetDimension

GAME_LIBRARY = [
    {
        "id": "game-001",
        "title": "积木高塔轮流堆",
        "description": "和孩子一起轮流搭建积木高塔，在倒塌的惊喜中建立眼神互动。",
        "target_dimension": TargetDimension.JOINT_ATTENTION,
        "estimated_duration": 15,
        "design_rationale": "通过结构化的轮流互动，建立规则感和眼神接触。倒塌的瞬间是极佳的视觉追踪和共同关注契机。",
        "goals": {
            "primary_goal": "建立 3 次以上的眼神对视",
            "secondary_goals": ["练习轮流等待", "提高视觉追踪能力"],
            "success_criteria": ["孩子在轮到自己时能看向家长", "孩子在塔倒时能发出笑声并看向家长"]
        },
        "steps": [
            {
                "step_number": 1,
                "title": "面对面坐好",
                "description": "和孩子面对面坐好，保持视线平齐。如果他在地上，你也趴在地上。",
                "guidance": "位置是关键！确保你能直接看到他的眼睛。",
                "key_points": ["平视", "近距离"],
                "parent_actions": ["寻找平视位置"],
                "tips": ["不要离得太远"]
            },
            {
                "step_number": 2,
                "title": "展示积木",
                "description": "你放一块积木，然后递给孩子一块。动作要慢。",
                "guidance": "拿积木的时候，把积木举到你眼睛旁边，吸引他看你的脸。",
                "key_points": ["慢动作", "视觉引导"],
                "parent_actions": ["举起积木到眼侧"],
                "tips": ["观察孩子的视线是否跟随积木"]
            },
            {
                "step_number": 3,
                "title": "等待对视",
                "description": "等待孩子看你一眼（即使是瞥一眼），再把积木给他。",
                "guidance": "不要催促。如果他不看，轻轻叫名字，或者把积木移到视线中间。",
                "key_points": ["等待耐心", "少量提示"],
                "parent_actions": ["保持静止等待"],
                "tips": ["对视发生时立即给予奖励反馈"]
            }
        ],
        "materials_needed": ["大块彩色积木", "平整的地板"],
        "precautions": [
            {"category": "安全", "content": "选择边缘圆滑的积木，防止磕碰。", "priority": "high"}
        ]
    },
    {
        "id": "game-002",
        "title": "感官泡泡追逐战",
        "description": "利用五彩斑斓的泡泡吸引孩子注意力，通过追逐和戳泡泡进行感官互动。",
        "target_dimension": TargetDimension.SENSORY,
        "estimated_duration": 10,
        "design_rationale": "泡泡具有极强的视觉吸引力，且运动轨迹不可预测，能有效激发孩子的探索欲望和共同关注。",
        "goals": {
            "primary_goal": "提高视觉追踪和手眼协调",
            "secondary_goals": ["增加积极情绪表达", "练习请求动作"],
            "success_criteria": ["孩子能持续追踪泡泡 5 秒以上", "孩子在泡泡消失后能看向家长要求'还要'"]
        },
        "steps": [
            {
                "step_number": 1,
                "title": "吹出大量泡泡",
                "description": "吹出大量泡泡，让孩子去追逐和戳破。",
                "guidance": "吹的时候要慢一点，让孩子有反应的时间。",
                "key_points": ["控制节奏"],
                "parent_actions": ["由少到多吹气"],
                "tips": ["观察孩子的兴奋程度"]
            },
            {
                "step_number": 2,
                "title": "轮流吹泡泡",
                "description": "如果你吹一次，让孩子也吹一次（如果他有精细动作能力）。",
                "guidance": "通过'轮流'加入简单的社交规则。",
                "key_points": ["社交协作"],
                "parent_actions": ["递交吹泡泡棒"],
                "tips": ["即使孩子只是吹不动，也要鼓励这种尝试"]
            }
        ],
        "materials_needed": ["无泪配方便携吹泡泡机/吹管"],
        "precautions": [
            {"category": "安全", "content": "注意地面湿滑，防止滑倒。", "priority": "high"}
        ]
    },
    {
        "id": "game-003",
        "title": "辨别声音魔术",
        "description": "通过识别家庭环境中的常见声音，培养听觉注意力和记忆力。",
        "target_dimension": TargetDimension.COGNITIVE,
        "estimated_duration": 15,
        "design_rationale": "减少视觉干扰，专注于听觉输入，有助于提高孩子的基础认知水平和对环境的敏感度。",
        "goals": {
            "primary_goal": "正确识别 3 种以上的声音来源",
            "secondary_goals": ["练习环境音分辨", "培养安静聆听的习惯"],
            "success_criteria": ["孩子能通过指向或发音识别出声音来源"]
        },
        "steps": [
            {
                "step_number": 1,
                "title": "静下心来听",
                "description": "在客厅里和孩子一起安静坐下，闭上眼睛（如果孩子配合）。",
                "guidance": "引导孩子把注意力集中在耳朵上。",
                "key_points": ["安静环境"],
                "parent_actions": ["做出倾听的手势"],
                "tips": ["可以先从响亮且熟悉的声音开始"]
            },
            {
                "step_number": 2,
                "title": "猜猜妈妈在干嘛",
                "description": "听妈妈在厨房发出的声音：水龙头哗哗声、油烟机隆隆声。",
                "guidance": "用夸张的表情问：'那是谁在叫？'或'妈妈在做什么？'",
                "key_points": ["关联性认知"],
                "parent_actions": ["提问引导"],
                "tips": ["如果孩子不知道，带他去实地观察"]
            }
        ],
        "materials_needed": ["家庭常见的发声物体（水龙头、锅铲等）"],
        "precautions": [
            {"category": "情绪", "content": "避免过大或突然的声音吓到孩子。", "priority": "normal"}
        ]
    }
]
