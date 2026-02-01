"""
游戏方案和会话数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class GameStatus(str, Enum):
    """游戏状态"""
    RECOMMENDED = "recommended"  # 已推荐
    SCHEDULED = "scheduled"  # 已安排（待实施）
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class TargetDimension(str, Enum):
    """目标维度（与ObservationDimension对应）"""
    EYE_CONTACT = "eye_contact"
    JOINT_ATTENTION = "joint_attention"
    SOCIAL_INTERACTION = "social_interaction"
    LANGUAGE = "language"
    IMITATION = "imitation"
    EMOTIONAL_REGULATION = "emotional_regulation"
    PLAY_SKILLS = "play_skills"
    SENSORY = "sensory"
    MOTOR_SKILLS = "motor_skills"
    COGNITIVE = "cognitive"


class GameStep(BaseModel):
    """游戏步骤"""
    step_number: int = Field(..., description="步骤序号", ge=1)
    title: str = Field(..., description="步骤标题")
    description: str = Field(..., description="详细描述")
    duration_minutes: Optional[int] = Field(None, description="预计时长（分钟）")
    key_points: List[str] = Field(default_factory=list, description="关键要点")
    parent_actions: List[str] = Field(default_factory=list, description="家长需要做的动作")
    expected_child_response: Optional[str] = Field(None, description="期待孩子的反应")
    tips: List[str] = Field(default_factory=list, description="小贴士")


class GamePrecaution(BaseModel):
    """注意事项"""
    category: str = Field(..., description="类别（如'安全'、'情绪'、'环境'）")
    content: str = Field(..., description="具体内容")
    priority: str = Field(default="normal", description="优先级（high/normal/low）")


class GameGoal(BaseModel):
    """游戏目标"""
    primary_goal: str = Field(..., description="主要目标")
    secondary_goals: List[str] = Field(default_factory=list, description="次要目标")
    success_criteria: List[str] = Field(default_factory=list, description="成功标准")


class GamePlan(BaseModel):
    """游戏方案"""
    game_id: str = Field(..., description="游戏方案唯一ID")
    child_id: str = Field(..., description="孩子ID")

    # 基础信息
    title: str = Field(..., description="游戏标题")
    description: str = Field(..., description="游戏简介")
    estimated_duration: int = Field(..., description="预计总时长（分钟）")

    # 目标和依据
    target_dimension: TargetDimension = Field(..., description="主要目标维度")
    additional_dimensions: List[TargetDimension] = Field(
        default_factory=list,
        description="额外涉及的维度"
    )
    interest_points_used: List[str] = Field(
        default_factory=list,
        description="利用的兴趣点"
    )
    design_rationale: str = Field(..., description="设计依据（为什么推荐这个游戏）")

    # 游戏内容
    steps: List[GameStep] = Field(..., description="游戏步骤")
    precautions: List[GamePrecaution] = Field(
        default_factory=list,
        description="注意事项"
    )
    goals: GameGoal = Field(..., description="游戏目标")

    # 材料和环境
    materials_needed: List[str] = Field(default_factory=list, description="所需材料")
    environment_setup: Optional[str] = Field(None, description="环境布置建议")

    # 状态
    status: GameStatus = Field(default=GameStatus.RECOMMENDED, description="游戏状态")
    scheduled_date: Optional[datetime] = Field(None, description="计划实施日期")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    recommended_by: str = Field(default="AI", description="推荐来源")

    # 趋势分析依据
    trend_analysis_summary: Optional[str] = Field(
        None,
        description="趋势分析摘要（推荐此游戏的数据依据）"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ParentObservation(BaseModel):
    """家长观察记录"""
    timestamp: datetime = Field(default_factory=datetime.now, description="观察时间")
    content: str = Field(..., description="观察内容")
    child_behavior: Optional[str] = Field(None, description="孩子的表现")
    parent_feeling: Optional[str] = Field(None, description="家长的感受")


class VideoAnalysisSummary(BaseModel):
    """视频分析摘要"""
    video_path: str = Field(..., description="视频文件路径")
    duration_seconds: int = Field(..., description="视频时长（秒）")
    key_moments: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="关键时刻（时间戳、描述、截图）"
    )
    behavior_analysis: Optional[str] = Field(None, description="行为分析")
    emotional_analysis: Optional[str] = Field(None, description="情绪分析")
    ai_insights: List[str] = Field(default_factory=list, description="AI洞察")


class GameSession(BaseModel):
    """游戏会话（实施记录）"""
    session_id: str = Field(..., description="会话唯一ID")
    game_id: str = Field(..., description="关联的游戏方案ID")
    child_id: str = Field(..., description="孩子ID")

    # 时间信息
    start_time: datetime = Field(..., description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    actual_duration: Optional[int] = Field(None, description="实际时长（分钟）")

    # 观察记录
    parent_observations: List[ParentObservation] = Field(
        default_factory=list,
        description="家长观察记录"
    )

    # 视频分析
    has_video: bool = Field(default=False, description="是否有视频")
    video_analysis: Optional[VideoAnalysisSummary] = Field(
        None,
        description="视频分析结果"
    )

    # 状态
    status: GameStatus = Field(default=GameStatus.IN_PROGRESS, description="会话状态")

    # 总结和评估
    session_summary: Optional[str] = Field(None, description="会话总结")
    child_engagement_score: Optional[float] = Field(
        None,
        description="孩子参与度评分（0-10）",
        ge=0,
        le=10
    )
    goal_achievement_score: Optional[float] = Field(
        None,
        description="目标达成度评分（0-10）",
        ge=0,
        le=10
    )
    parent_satisfaction_score: Optional[float] = Field(
        None,
        description="家长满意度评分（0-10）",
        ge=0,
        le=10
    )

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 备注
    notes: Optional[str] = Field(None, description="备注")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GameCalendarItem(BaseModel):
    """游戏日历条目"""
    game_id: str
    title: str
    target_dimension: TargetDimension
    status: GameStatus
    scheduled_date: Optional[datetime]
    estimated_duration: int
    session_count: int = Field(default=0, description="已实施次数")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GameRecommendRequest(BaseModel):
    """游戏推荐请求"""
    child_id: str
    focus_dimension: Optional[TargetDimension] = Field(
        None,
        description="希望重点关注的维度（可选）"
    )
    duration_preference: Optional[int] = Field(
        None,
        description="期望时长（分钟，可选）"
    )


class GameRecommendResponse(BaseModel):
    """游戏推荐响应"""
    game_plan: GamePlan
    trend_summary: str = Field(..., description="趋势分析摘要")
    recommendation_reason: str = Field(..., description="推荐理由")
    message: str = "游戏推荐成功"


class SessionStartRequest(BaseModel):
    """开始游戏会话请求"""
    game_id: str
    child_id: str


class SessionObservationRequest(BaseModel):
    """添加会话观察请求"""
    session_id: str
    content: str
    child_behavior: Optional[str] = None
    parent_feeling: Optional[str] = None


class SessionEndRequest(BaseModel):
    """结束游戏会话请求"""
    session_id: str
    video_path: Optional[str] = None
    child_engagement_score: Optional[float] = None
    goal_achievement_score: Optional[float] = None
    parent_satisfaction_score: Optional[float] = None
    notes: Optional[str] = None


class SessionResponse(BaseModel):
    """游戏会话响应"""
    session_id: str
    game_id: str
    child_id: str
    status: GameStatus
    start_time: datetime
    end_time: Optional[datetime]
    message: str

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DimensionProgress(BaseModel):
    """维度进展评估"""
    dimension: TargetDimension = Field(..., description="目标维度")
    dimension_name: str = Field(..., description="维度名称")
    performance_score: float = Field(..., ge=0, le=10, description="本次表现评分")
    progress_description: str = Field(..., description="进展描述")
    highlights: List[str] = Field(default_factory=list, description="亮点表现")
    challenges: List[str] = Field(default_factory=list, description="遇到的挑战")


class GameSessionSummary(BaseModel):
    """游戏会话总结（LLM 生成的结构化总结）"""
    
    # 整体评价
    overall_assessment: str = Field(..., description="整体评价（200-300字）")
    success_level: str = Field(..., description="成功程度（excellent/good/fair/poor）")
    
    # 目标达成情况
    goal_achievement: Dict[str, Any] = Field(..., description="目标达成情况")
    
    # 各维度表现
    dimension_progress: List[DimensionProgress] = Field(
        ..., 
        description="各维度进展评估"
    )
    
    # 孩子表现分析
    child_performance: Dict[str, Any] = Field(..., description="孩子表现分析")
    
    # 亮点时刻
    highlights: List[str] = Field(
        default_factory=list,
        description="本次游戏的亮点时刻（3-5个）"
    )
    
    # 需要改进的地方
    areas_for_improvement: List[str] = Field(
        default_factory=list,
        description="需要改进的地方（2-3个）"
    )
    
    # 家长表现反馈
    parent_feedback: Optional[str] = Field(
        None,
        description="对家长表现的反馈和建议"
    )
    
    # 下次建议
    recommendations_for_next: List[str] = Field(
        default_factory=list,
        description="下次游戏的建议（3-5条）"
    )
    
    # 趋势观察
    trend_observation: Optional[str] = Field(
        None,
        description="结合历史数据的趋势观察"
    )
    
    # 兴趣验证（新增）
    interest_verification: Dict[str, Any] = Field(
        default_factory=dict,
        description="兴趣点验证结果"
    )
    
    # 意外发现（新增）
    unexpected_discoveries: List[str] = Field(
        default_factory=list,
        description="游戏中的意外发现（新兴趣点）"
    )
    
    # 试错结果（新增）
    interest_trial_result: Optional[Dict[str, Any]] = Field(
        None,
        description="如果本次游戏是兴趣试错，给出验证结论"
    )
    
    # 数据依据
    data_sources_used: List[str] = Field(
        default_factory=list,
        description="使用的数据来源（用于透明度）"
    )


class GameSummaryRequest(BaseModel):
    """游戏总结请求"""
    session_id: str = Field(..., description="游戏会话ID")


class GameSummaryResponse(BaseModel):
    """游戏总结响应"""
    session_id: str
    game_id: str
    child_id: str
    summary: GameSessionSummary
    message: str = "游戏总结生成成功"
