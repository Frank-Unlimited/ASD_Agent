# 记忆驱动架构设计文档

**文档日期**：2026-01-30
**文档版本**：v1.0
**设计目标**：重构系统架构，以"记忆"为核心，实现模块间通过记忆交换数据

---

## 1. 核心理念

### 1.1 记忆驱动架构

所有模块不直接通信，而是通过读写"记忆"来交换数据。记忆存储在 Graphiti 时序知识图谱中。

```
┌─────────────────────────────────────────────────────────┐
│                      业务模块层                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐       │
│  │导入模块 │ │评估模块 │ │游戏模块 │ │导出模块 │       │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘       │
└───────┼──────────┼──────────┼──────────┼───────────────┘
        │          │          │          │
        ▼          ▼          ▼          ▼
┌─────────────────────────────────────────────────────────┐
│                    记忆服务层                            │
│                   MemoryService                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 按节点类型的读写接口 + LLM智能解析                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────────────────────────┐
│                    Graphiti 存储层                       │
│              时序知识图谱 + Neo4j                        │
└─────────────────────────────────────────────────────────┘
```

### 1.2 记忆写入策略

**只有4种情况写入记忆：**

1. **导入行为 - 读入档案/量表**
   - 写入：人物节点、功能维度节点（初始评估）、兴趣维度节点（初始兴趣）

2. **导入行为 - 日常记录**
   - 写入：行为节点（LLM解析后）

3. **地板游戏总结**
   - 写入：更新游戏节点的 implementation、将关键行为写入行为节点

4. **孩子评估结果**
   - 兴趣挖掘 → 兴趣维度节点
   - 趋势分析 → 功能维度节点
   - 综合评估 → 儿童评估节点

**不直接写入记忆**：
- 游戏实施中的 ParentObservation（暂存在 GameSession，总结时统一处理）
- 游戏推荐（只读取记忆生成方案）
- 导出报告（只读）

---

## 2. 记忆节点定义

### 2.1 节点类型概览

| 节点类型 | 说明 | 时间策略 |
|---------|------|---------|
| 人物 | 孩子基础档案 | 单例，更新 |
| 行为 | 观察记录 | 每次创建新节点 |
| 对象 | 玩具/物品 | 按需创建 |
| 兴趣维度 | 8类兴趣评估快照 | 每次评估创建新节点 |
| 功能维度 | 33维度评估快照 | 每次评估创建新节点 |
| 地板游戏 | 游戏详情+实施总结 | 每次创建新节点 |
| 儿童评估 | 综合评估结果 | 每次评估创建新节点 |

### 2.2 节点关系结构

```
[人物:孩子] ──展现──→ [行为]
    │                    │
    │                    └──涉及──→ [对象]
    │                    └──体现──→ [兴趣维度]
    │                    └──反映──→ [功能维度]
    │
    ├──参与──→ [地板游戏] ──使用──→ [对象]
    │              │        ──训练──→ [功能维度]
    │              │        ──激发──→ [兴趣维度]
    │
    └──接受──→ [儿童评估] ──评估──→ [功能维度]
                          ──发现──→ [兴趣维度]
```

---

## 3. 节点数据结构

### 3.1 人物节点（孩子档案）

```python
{
    "child_id": "child_001",
    "name": "辰辰",
    "birth_date": "2022-06-15",
    "gender": "male",
    "diagnosis": "ASD轻度",
    "diagnosis_date": "2024-01-01",
    "created_at": "2024-01-10",

    # 基础信息（相对稳定）
    "basic_info": {
        "height": 95,
        "weight": 14,
        "medical_history": "..."
    }
}
```

### 3.2 行为节点

```python
{
    # === 基础信息 ===
    "behavior_id": "bh_20240129_143022",
    "child_id": "...",
    "timestamp": "2024-01-29T14:30:22Z",

    # === 行为描述 ===
    "event_type": "social",  # behavior/emotion/communication/social/firstTime
    "description": "孩子主动递积木给妈妈，同时抬头看了一眼",
    "raw_input": "今天玩积木时，辰辰突然把积木递给我，还看了我一眼",
    "input_type": "voice",  # voice/text/quick_button/video_ai

    # === 行为分析 ===
    "significance": "breakthrough",  # breakthrough/improvement/normal/concern
    "ai_analysis": {
        "category": "主动社交互动",
        "impact": "从被动回应转向主动发起",
        "first_time": True
    },

    # === 关联维度 ===
    "related_dimensions": {
        "interest": ["construction"],
        "function": ["eye_contact", "social_initiation"]
    },

    # === 关联对象 ===
    "objects_involved": ["积木"],

    # === 上下文 ===
    "context": {
        "activity": "积木游戏",
        "location": "家里客厅",
        "game_id": "game_xxx",
        "duration": "约3秒"
    },

    # === 证据 ===
    "evidence": {
        "video_clip": {"start": 142, "end": 145},
        "transcript": "..."
    }
}
```

### 3.3 对象节点

```python
{
    "object_id": "obj_001",
    "name": "彩色积木",
    "category": "construction",  # 对应兴趣类别
    "description": "12色木质积木套装",

    # 使用统计（自动更新）
    "usage": {
        "total_games": 15,
        "last_used": "2024-01-29",
        "effectiveness": "high"
    }
}
```

### 3.4 兴趣维度节点

```python
{
    # === 基础信息 ===
    "interest_id": "int_20240129",
    "child_id": "...",
    "timestamp": "2024-01-29",

    # === 8类兴趣评估 ===
    "categories": {
        "visual": {
            "level": "high",  # high/medium/low/none
            "items": ["彩色积木", "旋转齿轮", "动画片段"],
            "evidence_ids": ["bh_001", "bh_002"]
        },
        "auditory": {
            "level": "medium",
            "items": ["儿歌", "机械声"],
            "evidence_ids": ["bh_003"]
        },
        "tactile": {"level": "low", "items": [], "evidence_ids": []},
        "motor": {"level": "medium", "items": ["蹦床"], "evidence_ids": []},
        "construction": {"level": "high", "items": ["乐高", "积木"], "evidence_ids": []},
        "order": {"level": "low", "items": [], "evidence_ids": []},
        "cognitive": {"level": "medium", "items": ["动物模型"], "evidence_ids": []},
        "social": {"level": "low", "items": [], "evidence_ids": []}
    },

    # === 趋势分析（与上次对比） ===
    "trends": {
        "emerging": ["social"],
        "stable": ["visual", "construction"],
        "declining": []
    },

    # === 来源 ===
    "source": "interest_mining",  # assessment/interest_mining/manual
    "related_assessment_id": "assess_xxx"
}
```

**兴趣维度参考**：
1. 视觉类：彩色积木/拼图/光影玩具/绘本/旋转齿轮/条纹图案/动画片段
2. 听觉类：儿歌/乐器声/自然音/机械声/有声书/节奏打击乐/人声故事
3. 触觉类：黏土/沙子/水/软胶玩具/毛绒材质/光滑积木/纹理卡片
4. 运动类：滑梯/秋千/蹦床/骑车/抛接球/转圈游戏/感统平衡木
5. 建构类：乐高/磁力片/积木/拆装玩具/折纸/手工材料/齿轮组
6. 秩序类：排序玩具/分类盒/叠叠乐/物品摆放游戏/流程卡片
7. 认知类：数字卡片/字母书/地图/车标图/动物模型/实验玩具
8. 社交类：回合制游戏（传球/躲猫猫）/角色扮演玩具/互动绘本

### 3.5 功能维度节点

```python
{
    # === 基础信息 ===
    "function_id": "func_20240129",
    "child_id": "...",
    "timestamp": "2024-01-29",

    # === 6大类33维度评估 ===
    "dimensions": {
        # 感觉能力（5个）
        "sensory": {
            "visual_response": {"score": 3, "evidence_ids": ["bh_001"]},
            "auditory_response": {"score": 2, "evidence_ids": []},
            "tactile_response": {"score": 4, "evidence_ids": []},
            "pain_response": {"score": 3, "evidence_ids": []},
            "taste_smell": {"score": 2, "evidence_ids": []}
        },
        # 社交互动（6个）
        "social": {
            "eye_contact": {"score": 4, "evidence_ids": ["bh_002", "bh_003"]},
            "social_smile": {"score": 3, "evidence_ids": []},
            "social_interest": {"score": 2, "evidence_ids": []},
            "imitation": {"score": 3, "evidence_ids": []},
            "joint_attention": {"score": 2, "evidence_ids": []},
            "social_initiation": {"score": 2, "evidence_ids": ["bh_004"]}
        },
        # 语言沟通（6个）
        "language": {
            "language_comprehension": {"score": 0, "evidence_ids": []},
            "language_expression": {"score": 0, "evidence_ids": []},
            "pronoun_use": {"score": 0, "evidence_ids": []},
            "echolalia": {"score": 0, "evidence_ids": []},
            "non_verbal_communication": {"score": 0, "evidence_ids": []},
            "speech_prosody": {"score": 0, "evidence_ids": []}
        },
        # 运动躯体（6个）
        "motor": {
            "stereotyped_movement": {"score": 0, "evidence_ids": []},
            "body_coordination": {"score": 0, "evidence_ids": []},
            "activity_level": {"score": 0, "evidence_ids": []},
            "gait_posture": {"score": 0, "evidence_ids": []},
            "self_injury": {"score": 0, "evidence_ids": []},
            "aggression": {"score": 0, "evidence_ids": []}
        },
        # 情绪适应（5个）
        "emotional": {
            "emotional_expression": {"score": 0, "evidence_ids": []},
            "emotional_response": {"score": 0, "evidence_ids": []},
            "anxiety_level": {"score": 0, "evidence_ids": []},
            "change_adaptation": {"score": 0, "evidence_ids": []},
            "frustration_tolerance": {"score": 0, "evidence_ids": []}
        },
        # 自理能力（5个）
        "self_care": {
            "toileting": {"score": 0, "evidence_ids": []},
            "dressing": {"score": 0, "evidence_ids": []},
            "feeding": {"score": 0, "evidence_ids": []},
            "safety_awareness": {"score": 0, "evidence_ids": []},
            "routine_skills": {"score": 0, "evidence_ids": []}
        }
    },

    # === 类别汇总 ===
    "category_scores": {
        "sensory": {"avg": 2.8, "trend": "stable"},
        "social": {"avg": 2.7, "trend": "improving"},
        "language": {"avg": 2.2, "trend": "stable"},
        "motor": {"avg": 3.1, "trend": "stable"},
        "emotional": {"avg": 2.5, "trend": "improving"},
        "self_care": {"avg": 2.0, "trend": "stable"}
    },

    # === 来源 ===
    "source": "trend_analysis",  # assessment/trend_analysis/manual
    "related_assessment_id": "assess_xxx"
}
```

**功能维度参考**：

| 大类 | 维度ID | 显示名称 | 说明 | 量表来源 |
|------|--------|---------|------|---------|
| 感觉能力 | visual_response | 视觉反应 | 凝视、回避、余光 | ABC-6,34,44,52,57 / CARS-7 |
| 感觉能力 | auditory_response | 听觉反应 | 对声音敏感/迟钝 | ABC-10,21,39 / CARS-8 |
| 感觉能力 | tactile_response | 触觉反应 | 触摸偏好/回避 | ABC-51 / CARS-9 |
| 感觉能力 | pain_response | 痛觉反应 | 过敏/迟钝 | ABC-26 / CARS-9 |
| 感觉能力 | taste_smell | 味觉嗅觉 | 舔、闻物品 | ABC-51 / CARS-9 |
| 社交互动 | eye_contact | 眼神接触 | 眼神交流的频率和质量 | ABC-24,47 / CARS-1 / M-CHAT-10 |
| 社交互动 | social_smile | 社交性微笑 | 回应性和主动性微笑 | ABC-7 / M-CHAT-12 |
| 社交互动 | social_interest | 社交兴趣 | 对他人的兴趣 | ABC-3,38 / CARS-1 / M-CHAT-2 |
| 社交互动 | imitation | 模仿能力 | 动作和语言模仿 | ABC-33 / CARS-2 / M-CHAT-13 |
| 社交互动 | joint_attention | 共同注意力 | 分享注意力焦点 | M-CHAT-7,9,15,17 |
| 社交互动 | social_initiation | 社交发起 | 主动发起社交互动 | ABC-3 / M-CHAT-19 |
| 语言沟通 | language_comprehension | 语言理解 | 对指令和语言的理解 | ABC-4,20,37 / M-CHAT-21 |
| 语言沟通 | language_expression | 语言表达 | 主动语言表达能力 | ABC-42,56 / CARS-11 |
| 语言沟通 | pronoun_use | 代词使用 | 代词的正确使用 | ABC-8,18 |
| 语言沟通 | echolalia | 仿说 | 重复语言/仿说 | ABC-32,46,48 |
| 语言沟通 | non_verbal_communication | 非语言沟通 | 手势、指向等 | ABC-29 / CARS-12 / M-CHAT-6 |
| 语言沟通 | speech_prosody | 语音语调 | 说话的节奏和语调 | ABC-11 / CARS-11 |
| 运动躯体 | stereotyped_movement | 刻板动作 | 拍手、旋转、摇摆等 | ABC-1,12,16,22,40 / CARS-4 |
| 运动躯体 | body_coordination | 身体协调性 | 动作协调程度 | ABC-13 / CARS-4 |
| 运动躯体 | activity_level | 活动水平 | 过度活跃或不足 | CARS-13 |
| 运动躯体 | gait_posture | 步态姿势 | 脚尖走路等异常步态 | ABC-16,30 / CARS-4 |
| 运动躯体 | self_injury | 自伤行为 | 撞头、咬手等 | ABC-35 |
| 运动躯体 | aggression | 攻击行为 | 对他人的攻击 | ABC-31 |
| 情绪适应 | emotional_expression | 情绪表达 | 情绪的外在表达 | CARS-3 |
| 情绪适应 | emotional_response | 情绪反应 | 情绪反应的适当性 | ABC-17 / CARS-3 |
| 情绪适应 | anxiety_level | 焦虑水平 | 焦虑和不安程度 | ABC-43 / CARS-10 |
| 情绪适应 | change_adaptation | 环境适应 | 对环境变化的适应 | ABC-14 / CARS-6 |
| 情绪适应 | frustration_tolerance | 挫折耐受 | 对挫折的耐受程度 | ABC-23,36 |
| 自理能力 | toileting | 如厕能力 | 大小便控制 | ABC-41 |
| 自理能力 | dressing | 穿衣能力 | 自己穿脱衣物 | ABC-45 |
| 自理能力 | feeding | 进食能力 | 独立进食 | - |
| 自理能力 | safety_awareness | 安全意识 | 对危险的意识 | ABC-49 |
| 自理能力 | routine_skills | 日常技能 | 日常技能学习保持 | ABC-2 |

### 3.6 地板游戏节点

```python
{
    # === 游戏基础信息 ===
    "game_id": "...",
    "child_id": "...",
    "name": "彩色积木塔",
    "description": "通过积木传递建立双向沟通...",
    "created_at": "2024-01-29",
    "status": "completed",  # recommended/scheduled/in_progress/completed/cancelled

    # === 游戏详情（推荐时生成） ===
    "design": {
        # 目标设定
        "target_dimension": "eye_contact",
        "additional_dimensions": ["joint_attention", "social_interaction"],
        "goals": {
            "primary_goal": "建立眼神接触的主动性",
            "secondary_goals": ["延长注意力时长", "..."],
            "success_criteria": ["主动眼神接触3次以上", "..."]
        },

        # 设计依据
        "interest_points_used": ["visual", "construction"],
        "design_rationale": "基于孩子对积木的兴趣，结合近期眼神接触改善趋势...",
        "trend_analysis_summary": "眼神接触近2周提升22%，建议保持动能...",

        # 游戏内容
        "estimated_duration": 15,
        "steps": [
            {
                "step_number": 1,
                "title": "建立兴趣",
                "description": "展示彩色积木，吸引孩子注意...",
                "duration_minutes": 3,
                "key_points": ["观察孩子反应", "..."],
                "parent_actions": ["慢慢展示积木", "..."],
                "expected_child_response": "目光跟随积木移动",
                "tips": ["不要急于推进", "..."]
            }
        ],

        # 材料和环境
        "materials_needed": ["彩色积木", "收纳盒"],
        "environment_setup": "安静的地面空间，减少干扰...",

        # 注意事项
        "precautions": [
            {"category": "安全", "content": "注意积木边角", "priority": "high"},
            {"category": "情绪", "content": "如孩子烦躁，及时停止", "priority": "high"}
        ]
    },

    # === 实施总结（游戏结束后更新） ===
    "implementation": {
        "session_date": "2024-01-29",
        "start_time": "14:00",
        "end_time": "14:18",
        "actual_duration": 18,

        # 视频分析
        "video_id": "...",
        "video_analysis": {
            "video_path": "...",
            "duration_seconds": 1080,
            "key_moments": [
                {"time": "02:15", "event": "主动眼神接触", "duration": "3秒"},
                {"time": "12:30", "event": "主动递积木", "significance": "breakthrough"}
            ],
            "behavior_analysis": "...",
            "emotional_analysis": "...",
            "ai_insights": ["首次主动发起互动", "..."]
        },

        # 家长反馈
        "parent_feedback": {
            "engagement_level": 4,
            "mood": "positive",
            "observations": "孩子今天特别专注...",
            "questions_answered": [...]
        },

        # 评分
        "child_engagement_score": 8.5,
        "goal_achievement_score": 7.0,
        "parent_satisfaction_score": 9.0,

        # 游戏中记录的行为（关联到行为记忆节点）
        "behavior_ids": ["bh_001", "bh_002"],

        # Agent生成的总结
        "session_summary": "本次游戏孩子参与度高，首次出现主动递积木行为...",
        "highlights": ["🌟 首次主动递积木", "📈 眼神接触5次"],
        "concerns": [],
        "notes": "..."
    },

    # === 关联的评估 ===
    "related_assessment_id": "...",
    "recommended_by": "AI",
    "scheduled_date": "2024-01-29"
}
```

### 3.7 儿童评估节点（综合评估）

```python
{
    # === 基础信息 ===
    "assessment_id": "...",
    "child_id": "...",
    "timestamp": "2024-01-29",
    "assessment_type": "comprehensive",

    # === 功能维度评估（关联到具体记忆） ===
    "dimension_assessments": {
        "eye_contact": {
            "current_score": 3,
            "trend": "improving",
            "evidence_ids": ["behavior_123", "behavior_456"],
            "game_ids": ["game_789"]
        }
        # ... 其他32个维度
    },

    # === 兴趣画像（关联到兴趣挖掘结果） ===
    "interest_profile": {
        "high_interest": ["visual", "construction"],
        "emerging_interest": ["social_game"],
        "evidence_ids": ["behavior_xxx", "game_yyy"]
    },

    # === 关联的记忆节点 ===
    "related_memories": {
        "behaviors": ["id1", "id2"],
        "games": ["id3", "id4"],
        "previous_assessments": ["id5"]
    },

    # === Agent 生成的分析 ===
    "analysis": {
        "strengths": [...],
        "focus_areas": [...],
        "insights": "..."
    },

    # === 下阶段建议 ===
    "recommendations": {
        "target_dimensions": ["eye_contact", "joint_attention"],
        "suggested_interest_leverage": ["用视觉类兴趣带动社交"],
        "game_direction": "..."
    }
}
```

---

## 4. 记忆服务接口设计

### 4.1 MemoryService 类定义

```python
class MemoryService:
    """记忆服务 - 集成 LLM 的智能读写"""

    def __init__(self, graphiti: Graphiti, llm: LLMService):
        self.graphiti = graphiti
        self.llm = llm

    # ========== 智能写入（LLM 解析）==========

    async def record_behavior(
        self,
        child_id: str,
        raw_input: str,           # 原始输入
        input_type: str,          # voice/text/quick_button
        context: dict = None      # 可选上下文
    ) -> BehaviorNode:
        """LLM 解析自然语言 → 结构化行为节点"""

    async def record_voice_observation(
        self,
        child_id: str,
        audio_file: str
    ) -> BehaviorNode:
        """语音转文字 + LLM 解析"""

    async def generate_assessment(
        self,
        child_id: str,
        assessment_type: str      # comprehensive/interest_mining/trend_analysis
    ) -> AssessmentNode:
        """LLM 综合评估 → 评估节点"""

    async def summarize_game(
        self,
        game_id: str,
        video_analysis: dict = None,
        parent_feedback: dict = None
    ) -> GameNode:
        """LLM 生成游戏总结 → 更新游戏节点"""

    # ========== 基础读写 ==========

    # 人物
    async def get_child(self, child_id: str) -> ChildNode
    async def save_child(self, child: ChildNode) -> str

    # 行为
    async def get_behaviors(self, child_id: str, filters: BehaviorFilter) -> List[BehaviorNode]

    # 对象
    async def save_object(self, obj: ObjectNode) -> str
    async def get_objects(self, child_id: str) -> List[ObjectNode]

    # 兴趣维度
    async def save_interest(self, interest: InterestNode) -> str
    async def get_latest_interest(self, child_id: str) -> InterestNode
    async def get_interest_history(self, child_id: str, limit: int) -> List[InterestNode]

    # 功能维度
    async def save_function(self, func: FunctionNode) -> str
    async def get_latest_function(self, child_id: str) -> FunctionNode
    async def get_function_history(self, child_id: str, limit: int) -> List[FunctionNode]

    # 地板游戏
    async def save_game(self, game: GameNode) -> str
    async def get_game(self, game_id: str) -> GameNode
    async def get_recent_games(self, child_id: str, limit: int) -> List[GameNode]

    # 儿童评估
    async def save_assessment(self, assessment: AssessmentNode) -> str
    async def get_latest_assessment(self, child_id: str) -> AssessmentNode
    async def get_assessment_history(self, child_id: str, limit: int) -> List[AssessmentNode]
```

---

## 5. 业务模块与记忆的交互流程

### 5.1 导入模块

```
┌─────────────────────────────────────────────────────────┐
│                      导入模块                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 读入档案/量表（Agent参与）                           │
│     输入：量表/档案图片                                  │
│     ┌──────────────────────────────────────┐           │
│     │ 多模态LLM解析 → 提取孩子信息和评估数据  │           │
│     └──────────────────────────────────────┘           │
│     写入记忆：                                          │
│     • memory.save_child(child_node)                    │
│     • memory.save_function(function_node)  # 初始评估   │
│     • memory.save_interest(interest_node)  # 初始兴趣   │
│                                                         │
│  2. 日常记录                                            │
│     输入：自然语言（语音/文字）                          │
│     ┌──────────────────────────────────────┐           │
│     │ memory.record_behavior(raw_input)    │           │
│     │ 或 memory.record_voice_observation() │           │
│     └──────────────────────────────────────┘           │
│     自动：LLM解析 → 结构化行为节点 → 建立维度关联        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 导出模块

```
┌─────────────────────────────────────────────────────────┐
│                      导出模块                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  导出详细报告                                            │
│  ┌──────────────────────────────────────┐              │
│  │ 读取记忆：                            │              │
│  │ • memory.get_child(child_id)         │              │
│  │ • memory.get_assessment_history()    │              │
│  │ • memory.get_function_history()      │              │
│  │ • memory.get_interest_history()      │              │
│  │ • memory.get_recent_games()          │              │
│  │ • memory.get_behaviors(全部)          │              │
│  └──────────────────────────────────────┘              │
│                    ↓                                    │
│  ┌──────────────────────────────────────┐              │
│  │ LLM 生成结构化报告                    │              │
│  │ • 发展历程                            │              │
│  │ • 各维度趋势图表                      │              │
│  │ • 里程碑时间线                        │              │
│  │ • 专业建议                            │              │
│  └──────────────────────────────────────┘              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.3 评估模块

```
┌─────────────────────────────────────────────────────────┐
│                      评估模块                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 兴趣挖掘（Agent参与）                                │
│     ┌──────────────────────────────────────┐           │
│     │ 读取记忆：                            │           │
│     │ • memory.get_latest_interest()       │           │
│     │ • memory.get_behaviors(related_to_interest)      │
│     └──────────────────────────────────────┘           │
│                    ↓                                    │
│     LLM 分析：捕捉无意识偏好，挖掘兴趣变化趋势            │
│                    ↓                                    │
│     输出：兴趣热力图数据                                 │
│     写入：memory.save_interest(new_interest_node)       │
│                                                         │
│  2. 趋势分析（Agent参与）                                │
│     ┌──────────────────────────────────────┐           │
│     │ 读取记忆：                            │           │
│     │ • memory.get_function_history()      │           │
│     │ • memory.get_behaviors(related_to_function)      │
│     └──────────────────────────────────────┘           │
│                    ↓                                    │
│     LLM 分析：功能维度趋势，挖掘成长点                   │
│                    ↓                                    │
│     输出：趋势折线图数据                                 │
│     写入：memory.save_function(new_function_node)       │
│                                                         │
│  3. 综合评估（Agent参与）                                │
│     ┌──────────────────────────────────────┐           │
│     │ 读取记忆：                            │           │
│     │ • memory.get_latest_interest()  # 兴趣挖掘结果    │
│     │ • memory.get_latest_function()  # 趋势分析结果    │
│     │ • memory.get_recent_games()     # 近期游戏总结    │
│     │ • memory.get_latest_assessment() # 上次评估      │
│     └──────────────────────────────────────┘           │
│                    ↓                                    │
│     LLM 综合分析：评估现状，生成结论和建议               │
│                    ↓                                    │
│     输出：评估结果（每个结论关联证据）                   │
│     写入：memory.save_assessment(assessment_node)       │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 5.4 游戏模块

```
┌─────────────────────────────────────────────────────────┐
│                      游戏模块                            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. 推荐游戏（Agent参与）                                │
│     ┌──────────────────────────────────────┐           │
│     │ 读取记忆：                            │           │
│     │ • memory.get_latest_assessment()     │           │
│     │ • memory.get_recent_games()          │           │
│     └──────────────────────────────────────┘           │
│                    ↓                                    │
│     LLM + RAG → 输出游戏详情                            │
│     写入：memory.save_game(game_node)                   │
│                                                         │
│  2. 实施游戏（沿用现有设计）                             │
│     ┌──────────────────────────────────────┐           │
│     │ 现有模块：                            │           │
│     │ • GameSession 管理会话生命周期        │           │
│     │ • 实时语音指引                        │           │
│     │ • ParentObservation 记录观察         │           │
│     │ • 视频录制                            │           │
│     └──────────────────────────────────────┘           │
│                                                         │
│  3. 总结游戏（Agent参与）                                │
│     ┌──────────────────────────────────────┐           │
│     │ 输入：                                │           │
│     │ • GameSession 数据                   │           │
│     │ • AI 视频分析结果                     │           │
│     │ • 家长反馈表                          │           │
│     └──────────────────────────────────────┘           │
│                    ↓                                    │
│     memory.summarize_game()                            │
│     • LLM 整合 GameSession + 视频分析 + 反馈            │
│     • 生成总结，更新游戏节点                            │
│     • 将关键行为写入记忆：memory.record_behavior()      │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**游戏模块的生命周期**：
```
推荐 → recommended → 实施 → in_progress → 总结 → completed
         ↓                    ↓                  ↓
    save_game()        (GameSession暂存)   summarize_game()
```

---

## 6. 下一步实施计划

### 6.1 实施优先级

1. **Phase 1: 记忆服务基础**
   - 定义节点数据模型（Pydantic）
   - 实现 MemoryService 基础读写接口
   - 集成 Graphiti

2. **Phase 2: 智能写入**
   - 实现 record_behavior() - LLM 解析行为
   - 实现 generate_assessment() - LLM 评估
   - 实现 summarize_game() - LLM 游戏总结

3. **Phase 3: 业务模块适配**
   - 导入模块对接记忆服务
   - 评估模块对接记忆服务
   - 游戏模块对接记忆服务
   - 导出模块对接记忆服务

### 6.2 技术要点

- **Graphiti 节点类型映射**：将7种节点类型映射到 Graphiti 的 Entity 类型
- **关系自动建立**：写入时根据 evidence_ids、related_dimensions 自动创建边
- **LLM Prompt 设计**：为行为解析、评估生成、游戏总结设计专用 Prompt

---

**文档结束**
