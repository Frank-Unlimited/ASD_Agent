"""
输出数据模型

定义Graphiti v2.0对外输出的数据结构。
这些模型用于API响应,为上层业务服务提供结构化的分析结果。
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal


@dataclass
class DataPoint:
    """
    数据点
    
    时间序列中的单个观察数据点。
    
    属性:
        timestamp: 观察时间,ISO 8601格式
        value: 观察值
        source: 数据来源(如"observation_agent", "game_session")
        confidence: 置信度(0-1)
        context: 观察上下文描述
    """
    timestamp: str
    value: float
    source: str
    confidence: float
    context: Optional[str] = None


@dataclass
class TrendInfo:
    """
    趋势信息
    
    描述某个时间窗口内的趋势方向和统计显著性。
    使用线性回归分析计算趋势。
    
    属性:
        direction: 趋势方向
            - "improving": 上升趋势(斜率>0且显著)
            - "stable": 稳定(斜率接近0或不显著)
            - "declining": 下降趋势(斜率<0且显著)
        rate: 变化率(每天的平均变化量)
            - 正值表示上升
            - 负值表示下降
            - 接近0表示稳定
        confidence: 置信度(0-1)
            - 基于R²值,表示趋势的可靠程度
            - >0.7: 高置信度
            - 0.3-0.7: 中等置信度
            - <0.3: 低置信度
        p_value: 统计显著性p值
            - <0.05: 统计显著
            - >=0.05: 不显著
    
    示例:
        TrendInfo(
            direction="improving",
            rate=0.15,  # 每天提升0.15分
            confidence=0.85,
            p_value=0.002
        )
    """
    direction: Literal["improving", "stable", "declining"]
    rate: float                 # 变化率
    confidence: float           # 置信度 0-1
    p_value: float              # 统计显著性


@dataclass
class PlateauInfo:
    """
    平台期信息
    
    检测维度是否进入平台期(进展停滞)。
    平台期定义: 连续N天变化幅度小于阈值。
    
    属性:
        is_plateau: 是否处于平台期
        duration_days: 平台期持续天数
        suggestion: 干预建议
            - 如"建议调整游戏类型或增加难度"
    
    示例:
        PlateauInfo(
            is_plateau=True,
            duration_days=12,
            suggestion="建议调整游戏类型,尝试新的干预策略"
        )
    """
    is_plateau: bool
    duration_days: int
    suggestion: str


@dataclass
class AnomalyInfo:
    """
    异常信息
    
    检测时间序列中的异常值(突然的大幅波动)。
    使用统计方法(如Z-score)识别异常。
    
    属性:
        has_anomaly: 是否存在异常
        anomaly_type: 异常类型
            - "spike": 突然上升
            - "drop": 突然下降
            - "none": 无异常
        anomaly_value: 异常值
        anomaly_date: 异常发生日期
        interpretation: 异常解释
            - 如"可能是特殊事件导致的临时波动"
    
    示例:
        AnomalyInfo(
            has_anomaly=True,
            anomaly_type="spike",
            anomaly_value=9.5,
            anomaly_date="2026-01-15",
            interpretation="该天表现异常优秀,可能是特殊活动的影响"
        )
    """
    has_anomaly: bool
    anomaly_type: Literal["spike", "drop", "none"]
    anomaly_value: float
    anomaly_date: str
    interpretation: str


@dataclass
class DimensionTrend:
    """
    单维度趋势
    
    某个发展维度的完整趋势分析结果。
    包含当前状态、历史趋势、平台期检测、异常检测等。
    
    属性:
        dimension: 维度名称(英文),如"eye_contact"
        display_name: 显示名称(中文),如"眼神接触"
        category: 维度分类
            - "milestone": 里程碑类维度
            - "behavior": 行为类维度
        current_value: 当前值(最近7天均值)
        baseline_value: 基线值(首次观察值)
        total_improvement: 总体提升幅度
            - 计算公式: (current_value - baseline_value) / baseline_value
            - 如0.5表示提升了50%
        trend_7d: 最近7天趋势
        trend_30d: 最近30天趋势
        trend_90d: 最近90天趋势
        plateau: 平台期检测结果
        anomaly: 异常检测结果
        data_points: 原始数据点列表(用于绘图)
        data_point_count: 数据点总数
    
    示例:
        DimensionTrend(
            dimension="eye_contact",
            display_name="眼神接触",
            current_value=7.5,
            baseline_value=3.0,
            total_improvement=1.5,  # 提升150%
            trend_30d=TrendInfo(direction="improving", rate=0.15),
            data_point_count=30
        )
    """
    dimension: str                      # 维度ID
    display_name: str                   # 显示名称（中文）
    category: str                       # milestone | behavior

    # 数值信息
    current_value: float                # 当前值（最近7天均值）
    baseline_value: float               # 基线值（首次评估）
    total_improvement: float            # 总体提升百分比

    # 多时间窗口趋势
    trend_7d: TrendInfo                 # 短期趋势
    trend_30d: TrendInfo                # 中期趋势
    trend_90d: TrendInfo                # 长期趋势

    # 状态标记
    plateau: PlateauInfo                # 平台期信息
    anomaly: AnomalyInfo                # 异常信息

    # 数据序列（供可视化）
    data_points: List[DataPoint]        # 时间序列数据
    data_point_count: int               # 数据点总数


@dataclass
class Milestone:
    """
    里程碑
    
    孩子发展过程中的重要时刻或突破性进展。
    
    属性:
        milestone_id: 里程碑唯一标识符
        dimension: 相关维度
        type: 里程碑类型
            - "first_time": 首次出现
            - "breakthrough": 突破性进展
            - "significant_improvement": 显著改善
            - "consistency": 持续稳定
        description: 里程碑描述
        timestamp: 发生时间
        significance: 重要性
            - "high": 高(突破性进展)
            - "medium": 中(明显改善)
            - "low": 低(小进步)
    """
    milestone_id: str
    dimension: str
    type: str                           # first_time | breakthrough | significant_improvement
    description: str
    timestamp: str
    significance: str                   # high | medium | low


@dataclass
class Correlation:
    """
    维度关联
    
    两个维度之间的相关关系。
    使用时滞相关分析(lagged correlation)检测因果关系。
    
    属性:
        dimension_a: 维度A
        dimension_b: 维度B
        correlation: 相关系数(-1到1)
            - >0.7: 强正相关
            - 0.3-0.7: 中等正相关
            - -0.3到0.3: 弱相关或无关
            - <-0.3: 负相关
        lag_days: 时滞天数
            - 0: 同步相关
            - >0: A领先B
            - <0: B领先A
        relationship: 关系描述
            - 如"eye_contact领先two_way_communication 5天"
        confidence: 置信度(0-1)
    
    示例:
        Correlation(
            dimension_a="eye_contact",
            dimension_b="two_way_communication",
            correlation=0.85,
            lag_days=5,
            relationship="eye_contact领先two_way_communication 5天",
            confidence=0.92
        )
    """
    dimension_a: str
    dimension_b: str
    correlation: float                  # -1 到 1
    lag_days: int                       # 时滞天数
    relationship: str                   # 关系描述
    confidence: float


@dataclass
class TrendSummary:
    """
    趋势摘要
    
    对所有维度的整体评估和建议。
    用于快速了解孩子的发展状况。
    
    属性:
        attention_dimensions: 需要关注的维度列表
            - 包括下降趋势或平台期的维度
        improving_dimensions: 进展良好的维度列表
            - 包括上升趋势的维度
        stable_dimensions: 稳定的维度列表
            - 包括无明显变化的维度
        overall_status: 整体状态
            - "excellent": 所有维度进展良好
            - "good": 大部分维度进展良好
            - "attention_needed": 部分维度需要关注
        recommendation: 综合建议
            - 基于趋势分析生成的干预建议
    
    示例:
        TrendSummary(
            attention_dimensions=["eye_contact", "self_regulation"],
            improving_dimensions=["repetitive_behavior"],
            stable_dimensions=["emotional_ideas"],
            overall_status="attention_needed",
            recommendation="刻板行为进展良好,建议继续当前游戏类型；眼神接触需要关注,可尝试调整干预策略"
        )
    """
    attention_dimensions: List[str]     # 需要关注的维度（下降或平台期）
    improving_dimensions: List[str]     # 进展良好的维度
    stable_dimensions: List[str]        # 稳定的维度
    overall_status: str                 # excellent | good | attention_needed
    recommendation: str                 # 综合建议


@dataclass
class TrendAnalysisResult:
    """
    完整趋势分析结果
    
    包含孩子所有维度的完整分析结果。
    这是Graphiti v2.0的核心输出,用于生成干预计划。
    
    属性:
        child_id: 孩子ID
        child_name: 孩子姓名
        analysis_time: 分析时间,ISO 8601格式
        dimensions: 各维度的趋势分析
            - key: 维度名称
            - value: DimensionTrend对象
        recent_milestones: 最近的里程碑列表
        total_milestones: 里程碑总数
        correlations: 维度关联列表
        summary: 趋势摘要
    
    用途:
        - 游戏推荐服务: 根据趋势选择目标维度
        - 报告生成: 生成发展报告
        - 家长端展示: 可视化孩子进展
    
    示例:
        TrendAnalysisResult(
            child_id="child-001",
            child_name="小明",
            analysis_time="2026-01-29T14:30:00Z",
            dimensions={
                "eye_contact": DimensionTrend(...),
                "two_way_communication": DimensionTrend(...)
            },
            recent_milestones=[...],
            total_milestones=5,
            correlations=[...],
            summary=TrendSummary(...)
        )
    """
    child_id: str
    child_name: str
    analysis_time: str

    # 各维度趋势
    dimensions: Dict[str, DimensionTrend]

    # 里程碑
    recent_milestones: List[Milestone]
    total_milestones: int

    # 跨维度关联
    correlations: List[Correlation]

    # 综合指标（供上层决策）
    summary: TrendSummary
