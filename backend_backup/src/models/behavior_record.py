"""
游戏实施阶段实时行为状态记录数据模型

定义了游戏过程中用于记录儿童行为事件、定时快照、AI推断和探测问题的数据结构。
这些模型服务于"游戏实时记录系统"，在家长实施地板时光游戏时，
通过按钮点击、定时快照和AI推断三种方式采集儿童行为数据。
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class EventSource(str, Enum):
    """行为事件来源"""
    PARENT_CLICK = "parent_click"          # 家长主动点击按钮
    TIMED_SNAPSHOT = "timed_snapshot"      # 定时快照采集
    AI_PROBE_RESPONSE = "ai_probe_response"  # AI探测问题的回答
    AI_INFERRED = "ai_inferred"            # AI自动推断


class GamePhase(str, Enum):
    """游戏阶段"""
    EXPLORATION = "exploration"       # 探索阶段
    INTERACTION = "interaction"       # 互动阶段
    CLIMAX = "climax"                # 高潮阶段
    CLOSURE = "closure"              # 收尾阶段


class EngagementLevel(str, Enum):
    """参与度等级"""
    INVESTED = "invested"            # 投入
    MODERATE = "moderate"            # 一般
    DISENGAGED = "disengaged"        # 脱离


class SchedulerMode(str, Enum):
    """快照调度模式"""
    NORMAL = "normal"                # 正常模式 3min
    DENSE = "dense"                  # 密集模式 5min（家长点击频繁，减少打扰）
    SPARSE = "sparse"                # 稀疏模式 2min（数据稀少，主动提醒）


class BehaviorRecord(BaseModel):
    """游戏过程中的行为事件记录"""
    id: Optional[str] = None
    timestamp: datetime
    session_id: str
    game_type: str
    event_type: str                  # 眼神接触/主动互动/情绪正面/情绪负面/...
    detail: Optional[str] = None     # 二级细节（长按展开时选择）
    valence: int = Field(ge=-1, le=1)  # +1正面/0中性/-1负面
    source: EventSource
    confidence: float = Field(ge=0.0, le=1.0)
    game_phase: Optional[GamePhase] = None
    related_interest: Optional[str] = None
    is_confirmed: Optional[bool] = None  # None=未确认, True=已确认, False=已否定


class SnapshotRecord(BaseModel):
    """定时快照记录"""
    id: Optional[str] = None
    timestamp: datetime
    session_id: str
    engagement_level: Optional[EngagementLevel] = None  # None表示跳过
    skipped: bool = False
    scheduler_mode: SchedulerMode = SchedulerMode.NORMAL


class GameSessionExtended(BaseModel):
    """游戏会话扩展信息（用于实时记录阶段）"""
    session_id: str
    child_id: str
    game_type: str
    game_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    planned_duration_minutes: int = 20

    # 动态按钮配置
    fixed_buttons: list = Field(default_factory=lambda: [
        {"id": "eye_contact", "label": "眼神", "icon": "👀", "valence": 1},
        {"id": "interaction", "label": "互动", "icon": "🤝", "valence": 1},
        {"id": "positive", "label": "积极", "icon": "😊", "valence": 1},
        {"id": "withdrawal", "label": "退缩", "icon": "😟", "valence": -1},
    ])
    dynamic_buttons: list = Field(default_factory=list)  # AI生成的动态按钮

    # 会话统计
    total_events: int = 0
    ai_inferences_count: int = 0
    engagement_score: Optional[float] = None  # 0-100
    ai_summary: Optional[str] = None


class AIInferenceRecord(BaseModel):
    """AI推断记录"""
    id: Optional[str] = None
    timestamp: datetime
    session_id: str
    inference_text: str              # 推断内容
    inference_type: str              # 行为推断/阶段推断/模式推断
    valence: int = 0                 # 推断情感倾向
    confidence: float = 0.5
    is_confirmed: Optional[bool] = None  # 家长确认状态


class AIProbeQuestion(BaseModel):
    """AI探测问题"""
    id: Optional[str] = None
    timestamp: datetime
    session_id: str
    question_text: str
    options: list[str]               # 预设选项
    selected_option: Optional[str] = None  # 家长选择的答案
    game_phase: Optional[GamePhase] = None
