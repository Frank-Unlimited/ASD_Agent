"""
观察记录数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ObservationType(str, Enum):
    """观察类型"""
    VOICE = "voice"  # 语音观察
    TEXT = "text"  # 文字观察
    VIDEO = "video"  # 视频观察
    QUICK = "quick"  # 快捷观察


class ObservationDimension(str, Enum):
    """观察维度（对应ASD发展领域）"""
    EYE_CONTACT = "eye_contact"  # 眼神接触
    JOINT_ATTENTION = "joint_attention"  # 共同注意力
    SOCIAL_INTERACTION = "social_interaction"  # 社交互动
    LANGUAGE = "language"  # 语言能力
    IMITATION = "imitation"  # 模仿能力
    EMOTIONAL_REGULATION = "emotional_regulation"  # 情绪调节
    PLAY_SKILLS = "play_skills"  # 游戏技能
    SENSORY = "sensory"  # 感觉统合
    MOTOR_SKILLS = "motor_skills"  # 运动技能
    COGNITIVE = "cognitive"  # 认知能力
    OTHER = "other"  # 其他


class ObservationSignificance(str, Enum):
    """观察重要性"""
    BREAKTHROUGH = "breakthrough"  # 突破性进展
    IMPROVEMENT = "improvement"  # 改善
    NORMAL = "normal"  # 正常表现
    CONCERN = "concern"  # 需要关注
    REGRESSION = "regression"  # 退步


class EmotionalState(str, Enum):
    """情绪状态"""
    HAPPY = "happy"  # 开心
    CALM = "calm"  # 平静
    EXCITED = "excited"  # 兴奋
    FRUSTRATED = "frustrated"  # 沮丧
    ANXIOUS = "anxious"  # 焦虑
    ANGRY = "angry"  # 生气
    NEUTRAL = "neutral"  # 中性


class StructuredObservationData(BaseModel):
    """LLM提取的结构化观察数据"""
    dimensions: List[ObservationDimension] = Field(
        default_factory=list,
        description="涉及的发展维度"
    )
    behaviors: List[str] = Field(
        default_factory=list,
        description="观察到的具体行为"
    )
    emotional_state: Optional[EmotionalState] = Field(
        None,
        description="孩子的情绪状态"
    )
    significance: ObservationSignificance = Field(
        default=ObservationSignificance.NORMAL,
        description="观察的重要性"
    )
    key_points: List[str] = Field(
        default_factory=list,
        description="关键要点"
    )
    interests_mentioned: List[str] = Field(
        default_factory=list,
        description="提到的兴趣点"
    )
    context: Optional[str] = Field(
        None,
        description="情境描述（在做什么活动、环境如何等）"
    )
    duration: Optional[str] = Field(
        None,
        description="持续时间（如'3分钟'、'整个上午'）"
    )


class Observation(BaseModel):
    """观察记录"""
    observation_id: str = Field(..., description="观察记录唯一ID")
    child_id: str = Field(..., description="孩子ID")

    # 观察元数据
    type: ObservationType = Field(..., description="观察类型")
    timestamp: datetime = Field(default_factory=datetime.now, description="观察时间")

    # 原始内容
    raw_content: str = Field(..., description="原始内容（语音转文字或直接输入的文字）")
    audio_file_path: Optional[str] = Field(None, description="音频文件路径（如果是语音观察）")

    # 结构化数据（由LLM提取）
    structured_data: Optional[StructuredObservationData] = Field(
        None,
        description="LLM提取的结构化数据"
    )

    # 关联信息
    session_id: Optional[str] = Field(
        None,
        description="关联的游戏会话ID（如果是在游戏中的观察）"
    )
    game_id: Optional[str] = Field(
        None,
        description="关联的游戏ID"
    )

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    processed: bool = Field(default=False, description="是否已处理（存入Graphiti）")
    graphiti_saved: bool = Field(default=False, description="是否已保存到Graphiti")

    # 标签和备注
    tags: List[str] = Field(default_factory=list, description="标签")
    parent_notes: Optional[str] = Field(None, description="家长补充备注")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class VoiceObservationRequest(BaseModel):
    """语音观察请求"""
    child_id: str
    audio_file_path: str
    session_id: Optional[str] = None
    game_id: Optional[str] = None
    parent_notes: Optional[str] = None


class TextObservationRequest(BaseModel):
    """文字观察请求"""
    child_id: str
    content: str
    session_id: Optional[str] = None
    game_id: Optional[str] = None
    parent_notes: Optional[str] = None


class ObservationResponse(BaseModel):
    """观察记录响应"""
    observation_id: str
    child_id: str
    type: ObservationType
    timestamp: datetime
    raw_content: str
    structured_data: Optional[StructuredObservationData]
    message: str = "观察记录成功"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ObservationListResponse(BaseModel):
    """观察记录列表响应"""
    child_id: str
    total: int
    observations: List[Observation]
    date_range: Optional[Dict[str, str]] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
