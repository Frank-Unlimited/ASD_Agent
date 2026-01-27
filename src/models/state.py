"""
LangGraph State 定义
动态的时序数据结构，而非静态字段
"""
from typing import TypedDict, List, Dict, Any, Optional, Literal
from datetime import datetime


# ============ 基础数据结构 ============

class MetricDataPoint(TypedDict):
    """时序指标数据点"""
    timestamp: str
    value: Any  # 可以是数字或字符串
    source: Literal['assessment', 'parentObservation', 'videoAI', 'gameSession']
    confidence: float
    context: Optional[str]
    evidence: Optional[List[str]]


class MetricAnalysis(TypedDict):
    """指标分析结果"""
    trend: Literal['improving', 'stable', 'declining', 'fluctuating']
    rate: float
    lastMilestone: Optional[str]
    nextGoal: Optional[str]


class MetricTimeSeries(TypedDict):
    """时序指标结构"""
    metricId: str
    metricName: str
    description: str
    dataPoints: List[MetricDataPoint]
    analysis: Optional[MetricAnalysis]


class ObservationEvent(TypedDict):
    """微观观察事件"""
    eventId: str
    timestamp: str
    eventType: Literal['behavior', 'emotion', 'communication', 'social', 'firstTime']
    description: str
    significance: Literal['breakthrough', 'improvement', 'normal', 'concern']
    evidence: Dict[str, Any]  # {source, clips, transcript}
    aiInsight: Optional[Dict[str, Any]]


class ChildProfile(TypedDict):
    """孩子基础信息"""
    childId: str
    name: str
    age: float
    birthDate: str
    diagnosis: str
    interests: List[str]
    customDimensions: Dict[str, Any]


class EmotionalMilestones(TypedDict):
    """六大情绪发展里程碑"""
    selfRegulation: MetricTimeSeries
    intimacy: MetricTimeSeries
    twoWayCommunication: MetricTimeSeries
    complexCommunication: MetricTimeSeries
    emotionalIdeas: MetricTimeSeries
    logicalThinking: MetricTimeSeries


class ChildTimeline(TypedDict):
    """孩子的活档案 - 时间线而非快照"""
    profile: ChildProfile
    metrics: Dict[str, Any]  # {emotionalMilestones, customDimensions}
    microObservations: List[ObservationEvent]


class CurrentContext(TypedDict):
    """当前上下文（从Graphiti加载，缓存在State）"""
    recentTrends: Dict[str, Any]
    attentionPoints: List[str]
    activeGoals: List[Dict[str, Any]]
    lastUpdated: Optional[str]


class VideoAnalysisResult(TypedDict):
    """视频分析结果"""
    duration: str
    highlights: List[Dict[str, Any]]
    metrics: Dict[str, Any]


class SessionSummary(TypedDict):
    """游戏总结"""
    date: str
    game: str
    duration: str
    highlights: List[str]
    concerns: List[str]
    overallAssessment: str
    comparisonWithLast: Optional[str]


class CurrentSession(TypedDict):
    """当前会话数据"""
    sessionId: Optional[str]
    gameId: Optional[str]
    gameName: Optional[str]
    status: Optional[Literal['pending', 'in_progress', 'ended', 'analyzing']]
    startTime: Optional[str]
    endTime: Optional[str]
    hasVideo: Optional[bool]
    videoPath: Optional[str]
    guidanceLog: Optional[List[Dict[str, Any]]]
    realTimeObservations: Optional[List[ObservationEvent]]
    quickObservations: Optional[List[Dict[str, Any]]]
    voiceObservations: Optional[List[Dict[str, Any]]]
    videoAnalysisResult: Optional[VideoAnalysisResult]
    validatedObservations: Optional[List[ObservationEvent]]
    preliminarySummary: Optional[Dict[str, Any]]
    feedbackForm: Optional[Dict[str, Any]]
    parentFeedback: Optional[Dict[str, Any]]
    finalSummary: Optional[SessionSummary]
    archivedData: Optional[Dict[str, Any]]


class WeeklyPlan(TypedDict):
    """周计划"""
    planId: str
    weekStartDate: str
    weekEndDate: str
    weeklyGoal: Dict[str, Any]
    dailyPlans: List[Dict[str, Any]]
    status: Literal['draft', 'active', 'completed']
    progress: Dict[str, Any]


class WorkflowControl(TypedDict):
    """工作流控制"""
    currentNode: str
    nextNode: Optional[str]
    isHITLPaused: bool
    checkpointId: Optional[str]
    needsAdjustment: Optional[bool]


# ============ 主 State 结构 ============

class DynamicInterventionState(TypedDict):
    """
    动态干预 State
    核心原则：State 是活的时序数据，不是死板的字段
    """
    # 孩子的"活"档案 - 时间线而非快照
    childTimeline: ChildTimeline
    
    # 当前上下文（从Graphiti加载，缓存在State）
    currentContext: CurrentContext
    
    # 当前会话
    currentSession: CurrentSession
    
    # 周计划
    currentWeeklyPlan: Optional[WeeklyPlan]
    
    # 会话历史（缓存）
    sessionHistory: Optional[List[Dict[str, Any]]]
    
    # 对话历史
    conversationHistory: Optional[List[Dict[str, Any]]]
    
    # 工作流控制
    workflow: WorkflowControl
    
    # 临时数据（用于节点间传递）
    tempData: Optional[Dict[str, Any]]
