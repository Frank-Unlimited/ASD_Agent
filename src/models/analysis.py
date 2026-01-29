"""
趋势分析数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class TrendDirection(str, Enum):
    """趋势方向"""
    IMPROVING = "improving"  # 改善
    STABLE = "stable"  # 稳定
    DECLINING = "declining"  # 下降
    FLUCTUATING = "fluctuating"  # 波动


class TimelineDataPoint(BaseModel):
    """时间线数据点"""
    date: str = Field(..., description="日期（YYYY-MM-DD）")
    timestamp: datetime = Field(..., description="时间戳")
    value: float = Field(..., description="数值（0-10）", ge=0, le=10)
    source: str = Field(..., description="数据来源（observation/assessment/game_session）")
    description: Optional[str] = Field(None, description="描述")
    evidence: List[str] = Field(default_factory=list, description="证据/观察记录")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DimensionTimeline(BaseModel):
    """发展维度时间线"""
    dimension_id: str = Field(..., description="维度ID")
    dimension_name: str = Field(..., description="维度名称")
    data_points: List[TimelineDataPoint] = Field(..., description="数据点列表")

    # 趋势分析
    trend: TrendDirection = Field(..., description="总体趋势")
    trend_description: str = Field(..., description="趋势描述")
    change_rate: Optional[float] = Field(
        None,
        description="变化率（每周）"
    )

    # 里程碑
    milestones: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="里程碑事件"
    )
    next_milestone: Optional[str] = Field(None, description="下一个里程碑")

    # 统计信息
    current_value: Optional[float] = Field(None, description="当前值")
    highest_value: Optional[float] = Field(None, description="历史最高值")
    lowest_value: Optional[float] = Field(None, description="历史最低值")
    average_value: Optional[float] = Field(None, description="平均值")

    # 时间范围
    start_date: str = Field(..., description="开始日期")
    end_date: str = Field(..., description="结束日期")


class InterestHeatmapData(BaseModel):
    """兴趣点热力图数据"""
    interest_name: str = Field(..., description="兴趣点名称")
    intensity_over_time: List[Dict[str, Any]] = Field(
        ...,
        description="时间序列强度数据 [{date, intensity}]"
    )
    current_intensity: float = Field(..., description="当前强度（0-10）", ge=0, le=10)
    trend: TrendDirection = Field(..., description="趋势方向")
    mention_count: int = Field(..., description="被提及次数")
    first_mentioned: str = Field(..., description="首次提及日期")
    last_mentioned: str = Field(..., description="最近提及日期")


class InterventionEffect(BaseModel):
    """干预效果"""
    game_id: str = Field(..., description="游戏ID")
    game_title: str = Field(..., description="游戏标题")
    target_dimension: str = Field(..., description="目标维度")
    session_count: int = Field(..., description="实施次数")

    # 效果评估
    before_score: Optional[float] = Field(
        None,
        description="干预前评分",
        ge=0,
        le=10
    )
    after_score: Optional[float] = Field(
        None,
        description="干预后评分",
        ge=0,
        le=10
    )
    improvement: Optional[float] = Field(
        None,
        description="提升幅度"
    )

    # 参与度和满意度
    avg_engagement: Optional[float] = Field(
        None,
        description="平均参与度",
        ge=0,
        le=10
    )
    avg_goal_achievement: Optional[float] = Field(
        None,
        description="平均目标达成度",
        ge=0,
        le=10
    )
    avg_parent_satisfaction: Optional[float] = Field(
        None,
        description="平均家长满意度",
        ge=0,
        le=10
    )

    # 时间范围
    first_session_date: str = Field(..., description="首次实施日期")
    last_session_date: str = Field(..., description="最近实施日期")

    # 效果描述
    effect_summary: Optional[str] = Field(None, description="效果总结")
    recommendations: List[str] = Field(
        default_factory=list,
        description="建议（是否继续、调整等）"
    )


class ComprehensiveAnalysis(BaseModel):
    """综合分析报告"""
    child_id: str = Field(..., description="孩子ID")
    analysis_date: datetime = Field(default_factory=datetime.now, description="分析日期")
    time_range: Dict[str, str] = Field(..., description="时间范围 {start, end}")

    # 各维度时间线
    dimension_timelines: List[DimensionTimeline] = Field(
        ...,
        description="各发展维度时间线"
    )

    # 兴趣热力图
    interest_heatmaps: List[InterestHeatmapData] = Field(
        ...,
        description="兴趣点热力图数据"
    )

    # 干预效果对比
    intervention_effects: List[InterventionEffect] = Field(
        ...,
        description="各游戏干预效果"
    )

    # 总体评估
    overall_progress: TrendDirection = Field(..., description="总体进展")
    overall_summary: str = Field(..., description="总体总结")
    key_improvements: List[str] = Field(default_factory=list, description="关键进步")
    areas_of_concern: List[str] = Field(default_factory=list, description="需要关注的领域")
    next_steps: List[str] = Field(default_factory=list, description="下一步建议")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TimelineRequest(BaseModel):
    """时间线查询请求"""
    child_id: str
    dimension_id: Optional[str] = Field(None, description="维度ID（可选，不填则返回所有维度）")
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")


class HeatmapRequest(BaseModel):
    """热力图查询请求"""
    child_id: str
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")


class InterventionEffectRequest(BaseModel):
    """干预效果查询请求"""
    child_id: str
    game_id: Optional[str] = Field(None, description="游戏ID（可选，不填则返回所有游戏）")
    start_date: Optional[str] = Field(None, description="开始日期（YYYY-MM-DD）")
    end_date: Optional[str] = Field(None, description="结束日期（YYYY-MM-DD）")


class AnalysisResponse(BaseModel):
    """分析响应"""
    child_id: str
    analysis_type: str = Field(..., description="分析类型（timeline/heatmap/intervention）")
    data: Any = Field(..., description="分析数据")
    message: str = "分析完成"
