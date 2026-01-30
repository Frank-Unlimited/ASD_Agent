"""
图节点模型定义

Graphiti v2.0 使用自定义图结构,包含4种核心节点类型:
- Child: 孩子节点(根节点)
- Dimension: 发展维度节点(如眼神接触、社交互动等)
- Observation: 观察数据节点(时间序列数据点)
- Milestone: 里程碑节点(重要进展标记)

图结构:
Child --HAS_DIMENSION--> Dimension --HAS_OBSERVATION--> Observation
Child --HAS_MILESTONE--> Milestone
Dimension --CORRELATES_WITH--> Dimension (关联关系)
"""
from dataclasses import dataclass
from typing import Optional, Literal
from datetime import datetime


@dataclass
class Child:
    """
    孩子节点 - 图的根节点
    
    代表一个接受干预的ASD儿童,是整个知识图谱的中心。
    所有维度、观察和里程碑都关联到这个节点。
    
    属性:
        node_type: 节点类型标识,固定为"Child"
        child_id: 孩子唯一标识符,格式如"child-001"
        name: 孩子姓名
        created_at: 档案创建时间,ISO 8601格式
    
    图关系:
        - (Child)-[:HAS_DIMENSION]->(Dimension): 拥有多个发展维度
        - (Child)-[:HAS_MILESTONE]->(Milestone): 拥有多个里程碑
    """
    node_type: str = "Child"
    child_id: str = ""
    name: str = ""
    created_at: str = ""


@dataclass
class Dimension:
    """
    维度节点 - 发展维度
    
    代表ASD儿童发展的一个维度(如眼神接触、社交互动等)。
    每个维度包含多个时间序列的观察数据点。
    
    属性:
        node_type: 节点类型标识,固定为"Dimension"
        dimension_id: 维度唯一标识符,格式如"dim-eye_contact-child-001"
        child_id: 所属孩子ID
        name: 维度名称(英文),如"eye_contact"
        display_name: 维度显示名称(中文),如"眼神接触"
        category: 维度分类
            - "milestone": 里程碑类维度(如首次主动对视)
            - "behavior": 行为类维度(如眼神接触频率)
        baseline_value: 基线值,首次观察的值,用于计算进步幅度
        baseline_date: 基线日期,首次观察的时间
    
    图关系:
        - (Child)-[:HAS_DIMENSION]->(Dimension): 属于某个孩子
        - (Dimension)-[:HAS_OBSERVATION]->(Observation): 包含多个观察数据点
        - (Dimension)-[:CORRELATES_WITH]->(Dimension): 与其他维度的关联关系
    """
    node_type: str = "Dimension"
    dimension_id: str = ""
    child_id: str = ""
    name: str = ""
    display_name: str = ""
    category: Literal["milestone", "behavior"] = "behavior"
    baseline_value: Optional[float] = None
    baseline_date: Optional[str] = None


@dataclass
class Observation:
    """
    观察节点 - 时间序列数据点
    
    代表某个时刻对某个维度的一次观察记录。
    多个观察节点构成维度的时间序列数据,用于趋势分析。
    
    属性:
        node_type: 节点类型标识,固定为"Observation"
        observation_id: 观察唯一标识符,格式如"obs-xxx"
        child_id: 所属孩子ID
        dimension: 所属维度名称,如"eye_contact"
        value: 观察值
            - score类型: 0-10分
            - count类型: 次数
            - duration类型: 秒数
            - boolean类型: 0或1
        value_type: 值类型
            - "score": 评分(0-10)
            - "count": 计数(次数)
            - "duration": 时长(秒)
            - "boolean": 布尔值(是/否)
        timestamp: 观察时间,ISO 8601格式
        source: 数据来源
            - "observation_agent": 观察记录服务
            - "game_session": 游戏会话
            - "video_analysis": 视频分析
            - "manual": 手动输入
        context: 观察上下文描述,如"积木游戏中主动看向家长"
        confidence: 置信度(0-1),表示观察的可靠程度
        session_id: 关联的会话ID(可选)
    
    图关系:
        - (Dimension)-[:HAS_OBSERVATION]->(Observation): 属于某个维度
    
    示例:
        Observation(
            observation_id="obs-001",
            child_id="child-001",
            dimension="eye_contact",
            value=7.5,
            value_type="score",
            timestamp="2026-01-29T14:30:00Z",
            source="observation_agent",
            context="积木游戏中主动看向家长3次",
            confidence=0.85
        )
    """
    node_type: str = "Observation"
    observation_id: str = ""
    child_id: str = ""
    dimension: str = ""
    value: float = 0.0
    value_type: Literal["score", "count", "duration", "boolean"] = "score"
    timestamp: str = ""
    source: str = ""
    context: Optional[str] = None
    confidence: float = 0.8
    session_id: Optional[str] = None


@dataclass
class Milestone:
    """
    里程碑节点 - 重要进展标记
    
    代表孩子发展过程中的重要时刻或突破性进展。
    里程碑由系统自动检测或手动标记。
    
    属性:
        node_type: 节点类型标识,固定为"Milestone"
        milestone_id: 里程碑唯一标识符,格式如"ms-xxx"
        child_id: 所属孩子ID
        dimension: 相关维度名称,如"eye_contact"
        type: 里程碑类型
            - "first_time": 首次出现(如首次主动对视)
            - "breakthrough": 突破性进展(如从不愿到主动)
            - "significant_improvement": 显著改善(如评分提升3分以上)
            - "consistency": 持续稳定(如连续7天保持高水平)
        description: 里程碑描述,如"首次主动发起眼神接触"
        timestamp: 里程碑发生时间,ISO 8601格式
        significance: 重要性级别
            - "high": 高(突破性进展)
            - "medium": 中(明显改善)
            - "low": 低(小进步)
    
    图关系:
        - (Child)-[:HAS_MILESTONE]->(Milestone): 属于某个孩子
    
    示例:
        Milestone(
            milestone_id="ms-001",
            child_id="child-001",
            dimension="eye_contact",
            type="first_time",
            description="首次主动发起眼神接触",
            timestamp="2026-01-04T10:30:00Z",
            significance="high"
        )
    """
    node_type: str = "Milestone"
    milestone_id: str = ""
    child_id: str = ""
    dimension: str = ""
    type: Literal["first_time", "breakthrough", "significant_improvement", "consistency"] = "first_time"
    description: str = ""
    timestamp: str = ""
    significance: Literal["high", "medium", "low"] = "high"
