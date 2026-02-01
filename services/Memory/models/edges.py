"""
Graphiti 边类型定义
定义节点之间的关系类型及其属性
"""
from enum import Enum
from typing import Dict, Any, List
from dataclasses import dataclass, field


class EdgeType(Enum):
    """边类型枚举"""
    # 人物相关
    RELATED_TO = "RELATED_TO"                    # 人物 <-> 人物
    展现 = "展现"                                 # 人物(孩子) -> 行为
    观察 = "观察"                                 # 人物(观察者) -> 行为
    实施 = "实施"                                 # 人物(实施者) -> 地板游戏
    参与 = "参与"                                 # 人物(参与者) -> 地板游戏
    评估 = "评估"                                 # 人物(评估者) -> 儿童评估
    接受 = "接受"                                 # 人物(孩子) -> 儿童评估
    
    # 行为相关
    涉及对象 = "涉及对象"                         # 行为 -> 对象
    涉及人物 = "涉及人物"                         # 行为 -> 人物
    体现兴趣 = "体现兴趣"                         # 行为 -> 兴趣维度
    反映功能 = "反映功能"                         # 行为 -> 功能维度
    
    # 对象相关
    属于兴趣类别 = "属于兴趣类别"                 # 对象 -> 兴趣维度
    
    # 孩子与维度（核心边，数据在边上）
    具有兴趣 = "具有兴趣"                         # 人物(孩子) -> 兴趣维度
    具有功能 = "具有功能"                         # 人物(孩子) -> 功能维度
    
    # 评估与维度（核心边，数据在边上）
    评估兴趣 = "评估兴趣"                         # 儿童评估 -> 兴趣维度
    评估功能 = "评估功能"                         # 儿童评估 -> 功能维度
    
    # 游戏相关
    使用对象 = "使用对象"                         # 地板游戏 -> 对象
    训练功能 = "训练功能"                         # 地板游戏 -> 功能维度
    激发兴趣 = "激发兴趣"                         # 地板游戏 -> 兴趣维度
    产生行为 = "产生行为"                         # 地板游戏 -> 行为


@dataclass
class EdgeProperties:
    """边属性的基类"""
    pass


@dataclass
class RelatedToProps(EdgeProperties):
    """RELATED_TO 边的属性"""
    relationship: str = ""  # parent/teacher/peer/sibling


@dataclass
class ObserveProps(EdgeProperties):
    """观察 边的属性"""
    observation_time: str = ""


@dataclass
class ImplementProps(EdgeProperties):
    """实施 边的属性"""
    implementation_date: str = ""


@dataclass
class ParticipateProps(EdgeProperties):
    """参与 边的属性"""
    participation_role: str = ""


@dataclass
class InvolveObjectProps(EdgeProperties):
    """涉及对象 边的属性"""
    interaction_type: str = ""  # 使用/观察/拒绝


@dataclass
class InvolvePersonProps(EdgeProperties):
    """涉及人物 边的属性"""
    role: str = ""  # 角色：facilitator(引导者)/participant(参与者)/observer(观察者)/trigger(触发者)
    interaction_quality: str = "neutral"  # 互动质量：positive/neutral/negative
    involvement_level: str = "medium"  # 参与程度：high/medium/low
    notes: str = ""  # 备注


@dataclass
class ReflectInterestProps(EdgeProperties):
    """体现兴趣 边的属性"""
    intensity: float = 0.0  # 强度 0-10
    duration: int = 0  # 持续时间（秒）
    positive_response: bool = True


@dataclass
class ReflectFunctionProps(EdgeProperties):
    """反映功能 边的属性"""
    score: float = 0.0  # 评分 0-10
    evidence_strength: float = 0.0  # 证据强度 0-1


@dataclass
class BelongToCategoryProps(EdgeProperties):
    """属于兴趣类别 边的属性"""
    primary: bool = True  # 是否主要类别
    relevance_score: float = 0.0  # 相关度 0-1


@dataclass
class HasInterestProps(EdgeProperties):
    """具有兴趣 边的属性（核心边，数据在这里）"""
    timestamp: str = ""
    level: str = "none"  # high/medium/low/none
    favorite_objects: List[str] = field(default_factory=list)  # 对象ID列表
    preference_scores: Dict[str, float] = field(default_factory=dict)  # {obj_id: score}
    evidence_ids: List[str] = field(default_factory=list)  # 行为ID列表
    trend: str = "stable"  # emerging/stable/declining
    source: str = "manual"  # assessment/interest_mining/manual


@dataclass
class HasFunctionProps(EdgeProperties):
    """具有功能 边的属性（核心边，数据在这里）"""
    timestamp: str = ""
    score: float = 0.0  # 评分 0-10
    baseline_value: float = 0.0  # 基线值
    improvement: float = 0.0  # 提升幅度
    evidence_ids: List[str] = field(default_factory=list)  # 行为ID列表
    trend: str = "stable"  # improving/stable/declining
    source: str = "manual"  # assessment/trend_analysis/manual


@dataclass
class AssessInterestProps(EdgeProperties):
    """评估兴趣 边的属性（评估结果在这里）"""
    level: str = "none"  # high/medium/low/none
    favorite_objects: List[str] = field(default_factory=list)
    preference_scores: Dict[str, float] = field(default_factory=dict)
    evidence_ids: List[str] = field(default_factory=list)
    trend: str = "stable"


@dataclass
class AssessFunctionProps(EdgeProperties):
    """评估功能 边的属性（评估结果在这里）"""
    score: float = 0.0
    evidence_ids: List[str] = field(default_factory=list)
    trend: str = "stable"
    focus_area: bool = False  # 是否重点关注


@dataclass
class UseObjectProps(EdgeProperties):
    """使用对象 边的属性"""
    usage_frequency: int = 0
    effectiveness: float = 0.0


@dataclass
class TrainFunctionProps(EdgeProperties):
    """训练功能 边的属性"""
    target_level: str = "primary"  # primary/secondary
    achievement_score: float = 0.0  # 达成度 0-10


@dataclass
class StimulateInterestProps(EdgeProperties):
    """激发兴趣 边的属性"""
    utilized: bool = True  # 是否利用
    effectiveness: float = 0.0


# 边属性类型映射
EDGE_PROPS_TYPES = {
    EdgeType.RELATED_TO: RelatedToProps,
    EdgeType.观察: ObserveProps,
    EdgeType.实施: ImplementProps,
    EdgeType.参与: ParticipateProps,
    EdgeType.涉及对象: InvolveObjectProps,
    EdgeType.涉及人物: InvolvePersonProps,
    EdgeType.体现兴趣: ReflectInterestProps,
    EdgeType.反映功能: ReflectFunctionProps,
    EdgeType.属于兴趣类别: BelongToCategoryProps,
    EdgeType.具有兴趣: HasInterestProps,
    EdgeType.具有功能: HasFunctionProps,
    EdgeType.评估兴趣: AssessInterestProps,
    EdgeType.评估功能: AssessFunctionProps,
    EdgeType.使用对象: UseObjectProps,
    EdgeType.训练功能: TrainFunctionProps,
    EdgeType.激发兴趣: StimulateInterestProps,
}
