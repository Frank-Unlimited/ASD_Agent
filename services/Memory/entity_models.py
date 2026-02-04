"""
Graphiti-core 实体模型定义
用于 add_episode() 的自动提取
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Literal


class BehaviorEntityModel(BaseModel):
    """行为实体模型 - 用于从文本中提取行为信息"""
    
    event_type: Literal["social", "emotion", "communication", "firstTime", "other"] = Field(
        ...,
        description="事件类型：social(社交互动)/emotion(情绪表达)/communication(沟通表达)/firstTime(首次出现)/other(其他)"
    )
    
    description: str = Field(
        ...,
        description="行为的简洁描述（30字以内）"
    )
    
    significance: Literal["breakthrough", "improvement", "normal", "concern"] = Field(
        ...,
        description="重要性：breakthrough(突破性进步)/improvement(改善)/normal(常规)/concern(需关注)"
    )
    
    emotional_state: Optional[str] = Field(
        None,
        description="孩子的情绪状态（如：开心、焦虑、平静等）"
    )
    
    duration_seconds: Optional[int] = Field(
        None,
        description="行为持续时长（秒）"
    )
    
    context_notes: Optional[str] = Field(
        None,
        description="上下文备注"
    )


class ObjectEntityModel(BaseModel):
    """对象实体模型 - 用于提取涉及的物品/玩具"""
    
    object_name: str = Field(
        ...,
        description="对象名称（如：积木、球、音乐盒）"
    )
    
    category: Optional[str] = Field(
        None,
        description="对象类别（如：玩具、工具、书籍）"
    )
    
    interaction_type: Optional[str] = Field(
        None,
        description="互动方式（如：使用、观察、拒绝）"
    )


class InterestEntityModel(BaseModel):
    """[DEPRECATED] 旧的兴趣实体模型 - 请使用 InterestDimensionEntityModel"""
    
    interest_name: Literal["visual", "auditory", "tactile", "motor", "construction", "order", "cognitive", "social"] = Field(
        ...,
        description="兴趣维度名称"
    )
    
    intensity: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="兴趣强度（0-10分）"
    )
    
    duration_seconds: Optional[int] = Field(
        None,
        description="持续时长（秒）"
    )
    
    is_primary: bool = Field(
        True,
        description="是否为主要兴趣"
    )


class InterestDimensionEntityModel(BaseModel):
    """兴趣维度实体模型 - 由 LLM 动态创建
    
    注意：Graphiti 的 name 字段是保护字段，不能在模型中定义
    因此使用 dimension_id 作为维度标识符
    """
    
    dimension_id: Literal["visual", "auditory", "tactile", "motor", "construction", "order", "cognitive", "social"] = Field(
        ...,
        description="兴趣维度标识符（8个维度之一）"
    )
    
    display_name: str = Field(
        ...,
        description="维度的中文显示名称（如：视觉、听觉、触觉等）"
    )
    
    description: Optional[str] = Field(
        None,
        description="该维度的简短描述"
    )


class FunctionEntityModel(BaseModel):
    """功能实体模型 - 用于识别反映的功能维度"""
    
    function_name: str = Field(
        ...,
        description="功能维度名称（如：eye_contact, social_smile等）"
    )
    
    score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="功能评分（0-10分）"
    )
    
    strength: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="表现强度（0-1）"
    )


class PersonEntityModel(BaseModel):
    """人物实体模型 - 用于识别涉及的人物"""
    
    person_name: str = Field(
        ...,
        description="人物名称（如：妈妈、爸爸、李老师）"
    )
    
    role: Optional[str] = Field(
        None,
        description="在事件中的角色（如：facilitator引导者/participant参与者/observer观察者）"
    )
    
    interaction_quality: Optional[Literal["positive", "negative", "neutral"]] = Field(
        None,
        description="互动质量"
    )


class GameSummaryEntityModel(BaseModel):
    """游戏总结实体模型"""
    
    session_summary: str = Field(
        ...,
        description="游戏会话总结（100-200字）"
    )
    
    engagement_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="参与度评分（0-10分）"
    )
    
    goal_achievement_score: float = Field(
        ...,
        ge=0.0,
        le=10.0,
        description="目标达成度评分（0-10分）"
    )
    
    highlights: List[str] = Field(
        default_factory=list,
        description="亮点时刻列表"
    )
    
    concerns: List[str] = Field(
        default_factory=list,
        description="需要关注的问题列表"
    )
    
    improvement_suggestions: List[str] = Field(
        default_factory=list,
        description="改进建议列表"
    )


class KeyBehaviorEntityModel(BaseModel):
    """关键行为实体模型 - 游戏中的关键时刻"""
    
    timestamp: str = Field(
        ...,
        description="时间戳（如：02:15）"
    )
    
    description: str = Field(
        ...,
        description="行为描述"
    )
    
    event_type: Literal["social", "emotion", "communication", "firstTime", "other"] = Field(
        ...,
        description="事件类型"
    )
    
    significance: Literal["breakthrough", "improvement", "normal", "concern"] = Field(
        ...,
        description="重要性"
    )


class AssessmentEntityModel(BaseModel):
    """评估实体模型"""
    
    assessment_type: str = Field(
        ...,
        description="评估类型（如：interest_mining, function_trend）"
    )
    
    assessment_summary: str = Field(
        ...,
        description="评估总结"
    )
    
    key_findings: List[str] = Field(
        default_factory=list,
        description="关键发现列表"
    )
    
    recommendations: List[str] = Field(
        default_factory=list,
        description="建议列表"
    )
    
    confidence_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="置信度（0-1）"
    )


# 边模型定义

class ExhibitEdgeModel(BaseModel):
    """展现边模型 - 孩子展现行为"""
    observation_time: str = Field(..., description="观察时间")


class InvolveObjectEdgeModel(BaseModel):
    """涉及对象边模型 - 行为涉及对象"""
    interaction_type: str = Field(..., description="互动类型")


class ShowInterestEdgeModel(BaseModel):
    """体现兴趣边模型 - 行为体现兴趣
    
    这个边连接 Behavior 节点和 InterestDimension 节点，
    表达行为对某个兴趣维度的贡献程度。
    
    边的权重用于计算兴趣维度的探索度：
    exploration_score = Σ(weight_i) * diversity_factor
    """
    
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="关联权重：这个行为对该兴趣维度的贡献度（0-1）"
    )
    
    reasoning: Optional[str] = Field(
        None,
        description="推理依据：为什么这个行为体现了该兴趣维度"
    )
    
    manifestation: Optional[str] = Field(
        None,
        description="具体表现：行为如何体现兴趣（如：'持续观察5分钟'、'主动寻找'）"
    )


class ShowFunctionEdgeModel(BaseModel):
    """体现功能边模型 - 行为体现功能"""
    score: float = Field(..., ge=0.0, le=10.0, description="评分")
    strength: float = Field(..., ge=0.0, le=1.0, description="强度")


class InvolvePersonEdgeModel(BaseModel):
    """涉及人物边模型 - 行为涉及人物"""
    role: str = Field(..., description="角色")
    interaction_quality: str = Field(..., description="互动质量")
