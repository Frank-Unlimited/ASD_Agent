"""
Memory 服务的 LLM 输出 Schema
定义智能写入方法的结构化输出格式
"""
from typing import List, Dict, Optional
from pydantic import BaseModel, Field


# ============ record_behavior 的输出 Schema ============

class BehaviorContext(BaseModel):
    """行为上下文"""
    activity: Optional[str] = Field(None, description="正在进行的活动")
    location: Optional[str] = Field(None, description="地点")
    duration: Optional[str] = Field(None, description="持续时间")


class AIAnalysis(BaseModel):
    """AI 分析结果"""
    category: str = Field(..., description="行为类别")
    impact: str = Field(..., description="对孩子发展的意义")
    first_time: bool = Field(..., description="是否首次出现")


class BehaviorParseOutput(BaseModel):
    """行为解析输出"""
    event_type: str = Field(..., description="事件类型：social/emotion/communication/firstTime/other")
    significance: str = Field(..., description="重要性：breakthrough/improvement/normal/concern")
    description: str = Field(..., description="简洁的行为描述（20字以内）")
    objects_involved: List[str] = Field(default_factory=list, description="涉及的对象（玩具/物品名称）")
    related_interests: List[str] = Field(default_factory=list, description="相关的兴趣类别")
    related_functions: List[str] = Field(default_factory=list, description="相关的功能维度")
    context: BehaviorContext = Field(default_factory=BehaviorContext, description="上下文信息")
    ai_analysis: AIAnalysis = Field(..., description="AI 分析")


# ============ summarize_game 的输出 Schema ============

class KeyBehavior(BaseModel):
    """关键行为"""
    timestamp: str = Field(..., description="时间戳")
    description: str = Field(..., description="行为描述")
    significance: str = Field(..., description="重要性：breakthrough/improvement/normal/concern")
    event_type: str = Field(..., description="事件类型")


class GameSummaryOutput(BaseModel):
    """游戏总结输出"""
    engagement_score: float = Field(..., description="参与度得分（0-10）", ge=0, le=10)
    goal_achievement_score: float = Field(..., description="目标达成得分（0-10）", ge=0, le=10)
    highlights: List[str] = Field(default_factory=list, description="亮点时刻")
    concerns: List[str] = Field(default_factory=list, description="关注点")
    key_behaviors: List[KeyBehavior] = Field(default_factory=list, description="关键行为")
    session_summary: str = Field(..., description="游戏总结")
    improvement_suggestions: List[str] = Field(default_factory=list, description="改进建议")
    parent_notes: Optional[str] = Field(None, description="家长备注")


# ============ generate_assessment (interest_mining) 的输出 Schema ============

class InterestDetail(BaseModel):
    """兴趣详情"""
    level: str = Field(..., description="水平：high/medium/low/none")
    items: List[str] = Field(default_factory=list, description="具体物品")
    evidence_count: int = Field(0, description="证据数量")
    notes: Optional[str] = Field(None, description="简短说明")


class InterestTrends(BaseModel):
    """兴趣趋势"""
    emerging: List[str] = Field(default_factory=list, description="新兴兴趣")
    stable: List[str] = Field(default_factory=list, description="稳定兴趣")
    declining: List[str] = Field(default_factory=list, description="下降兴趣")


class InterestSummary(BaseModel):
    """兴趣总结"""
    dominant_interests: List[str] = Field(default_factory=list, description="主导兴趣")
    potential_interests: List[str] = Field(default_factory=list, description="潜在兴趣")
    recommendations: List[str] = Field(default_factory=list, description="建议")


class InterestMiningOutput(BaseModel):
    """兴趣挖掘输出"""
    interests: Dict[str, InterestDetail] = Field(..., description="8类兴趣维度")
    trends: InterestTrends = Field(..., description="兴趣趋势")
    summary: InterestSummary = Field(..., description="总结")


# ============ generate_assessment (trend_analysis) 的输出 Schema ============

class DimensionDetail(BaseModel):
    """功能维度详情"""
    score: float = Field(..., description="得分（0-10）", ge=0, le=10)
    trend: str = Field(..., description="趋势：improving/stable/declining")
    evidence_count: int = Field(0, description="证据数量")
    notes: Optional[str] = Field(None, description="简短说明")


class CategoryScore(BaseModel):
    """类别得分"""
    avg: float = Field(..., description="平均分", ge=0, le=10)
    trend: str = Field(..., description="趋势：improving/stable/declining")


class FunctionSummary(BaseModel):
    """功能总结"""
    strengths: List[str] = Field(default_factory=list, description="优势领域")
    challenges: List[str] = Field(default_factory=list, description="挑战领域")
    improving_areas: List[str] = Field(default_factory=list, description="改善领域")
    focus_recommendations: List[str] = Field(default_factory=list, description="重点建议")


class FunctionTrendOutput(BaseModel):
    """功能趋势分析输出"""
    dimensions: Dict[str, DimensionDetail] = Field(..., description="33个功能维度")
    category_scores: Dict[str, CategoryScore] = Field(..., description="6大类得分")
    summary: FunctionSummary = Field(..., description="总结")


# ============ generate_assessment (comprehensive) 的输出 Schema ============

class StrengthArea(BaseModel):
    """优势领域"""
    area: str = Field(..., description="领域名称")
    description: str = Field(..., description="描述")
    leverage_strategy: str = Field(..., description="利用策略")


class ChallengeArea(BaseModel):
    """挑战领域"""
    area: str = Field(..., description="领域名称")
    description: str = Field(..., description="描述")
    intervention_priority: str = Field(..., description="干预优先级：high/medium/low")


class Priority(BaseModel):
    """训练优先级"""
    rank: int = Field(..., description="排名")
    dimension: str = Field(..., description="维度名称")
    reason: str = Field(..., description="原因")
    target_score: float = Field(..., description="目标得分", ge=0, le=10)
    timeline: str = Field(..., description="时间线")


class ProgressSummary(BaseModel):
    """进展总结"""
    overall_trend: str = Field(..., description="整体趋势：positive/stable/concerning")
    key_achievements: List[str] = Field(default_factory=list, description="关键成就")
    areas_needing_attention: List[str] = Field(default_factory=list, description="需要关注的领域")
    next_steps: str = Field(..., description="下一步")


class ComprehensiveAssessmentOutput(BaseModel):
    """综合评估输出"""
    strengths: List[StrengthArea] = Field(default_factory=list, description="优势领域")
    challenges: List[ChallengeArea] = Field(default_factory=list, description="挑战领域")
    priorities: List[Priority] = Field(default_factory=list, description="训练优先级")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    progress_summary: ProgressSummary = Field(..., description="进展总结")


# ============ import_profile 的输出 Schema ============

class ProfileInterests(BaseModel):
    """档案兴趣"""
    visual: str = Field("none", description="视觉类：high/medium/low/none")
    auditory: str = Field("none", description="听觉类：high/medium/low/none")
    tactile: str = Field("none", description="触觉类：high/medium/low/none")
    motor: str = Field("none", description="运动类：high/medium/low/none")
    construction: str = Field("none", description="建构类：high/medium/low/none")
    order: str = Field("none", description="秩序类：high/medium/low/none")
    cognitive: str = Field("none", description="认知类：high/medium/low/none")
    social: str = Field("none", description="社交类：high/medium/low/none")


class ProfileFunctionCategory(BaseModel):
    """档案功能类别"""
    avg: float = Field(0, description="平均分（0-10）", ge=0, le=10)
    notes: str = Field("", description="简短说明")


class ProfileImportOutput(BaseModel):
    """档案导入输出"""
    name: str = Field(default="未命名", description="孩子姓名（从档案中提取）")
    age: Optional[int] = Field(None, description="年龄（从档案中提取）")
    overall_assessment: str = Field(..., description="整体评估（200字以内）")
    strengths: List[str] = Field(default_factory=list, description="优势领域")
    challenges: List[str] = Field(default_factory=list, description="挑战领域")
    interests: ProfileInterests = Field(default_factory=ProfileInterests, description="兴趣偏好")
    function_dimensions: Dict[str, ProfileFunctionCategory] = Field(
        default_factory=dict,
        description="功能维度（sensory/social/language/motor/emotional/self_care）"
    )
    recommendations: List[str] = Field(default_factory=list, description="建议")


__all__ = [
    'BehaviorParseOutput',
    'GameSummaryOutput',
    'InterestMiningOutput',
    'FunctionTrendOutput',
    'ComprehensiveAssessmentOutput',
    'ProfileImportOutput'
]
