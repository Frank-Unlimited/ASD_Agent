"""
评估相关的数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class AssessmentType(str, Enum):
    """评估类型"""
    COMPREHENSIVE = "comprehensive"  # 完整评估（手动触发）
    LIGHTWEIGHT = "lightweight"      # 轻量级评估（游戏后自动）


class InterestBreadth(str, Enum):
    """兴趣广度"""
    NARROW = "narrow"      # 狭窄
    MODERATE = "moderate"  # 中等
    DIVERSE = "diverse"    # 多样


class TrendDirection(str, Enum):
    """趋势方向"""
    INCREASING = "increasing"  # 上升
    STABLE = "stable"          # 稳定
    DECREASING = "decreasing"  # 下降


class ConfidenceLevel(str, Enum):
    """置信度"""
    HIGH = "high"      # 高
    MEDIUM = "medium"  # 中
    LOW = "low"        # 低


# ============ 兴趣挖掘相关 ============

class InterestObject(BaseModel):
    """兴趣对象"""
    name: str = Field(..., description="对象名称")
    verified: bool = Field(..., description="是否在游戏中验证为真实兴趣")
    engagement: float = Field(..., description="参与度评分", ge=0, le=10)
    note: Optional[str] = Field(None, description="备注")


class InterestDimensionData(BaseModel):
    """单个兴趣维度的数据"""
    dimension_name: str = Field(..., description="兴趣维度名称")
    strength: float = Field(..., description="考虑衰减后的加权强度", ge=0, le=10)
    trend: TrendDirection = Field(..., description="趋势")
    confidence: ConfidenceLevel = Field(..., description="置信度")
    key_objects: List[InterestObject] = Field(default_factory=list, description="关键对象")
    breadth_note: Optional[str] = Field(None, description="广度评价")


class InterestHeatmap(BaseModel):
    """兴趣热力图数据（兴趣挖掘 Agent 的输出）"""
    dimensions: Dict[str, InterestDimensionData] = Field(..., description="8个兴趣维度的数据")
    overall_breadth: InterestBreadth = Field(..., description="整体兴趣广度")
    new_discoveries: List[str] = Field(default_factory=list, description="新发现的兴趣点")
    interest_verification: List[str] = Field(default_factory=list, description="兴趣验证结果")
    analysis_summary: str = Field(..., description="分析总结")


# ============ 功能分析相关 ============

class BreakthroughMoment(BaseModel):
    """突破性时刻"""
    date: str = Field(..., description="日期")
    type: str = Field(..., description="突破类型（主动性/持续性/泛化性/复杂性）")
    description: str = Field(..., description="描述")


class DimensionTrendData(BaseModel):
    """单个功能维度的趋势数据"""
    dimension_name: str = Field(..., description="维度名称")
    current_level: float = Field(..., description="当前水平", ge=0, le=10)
    baseline: float = Field(..., description="基线水平", ge=0, le=10)
    change: str = Field(..., description="变化量（如 +3.5）")
    trend: TrendDirection = Field(..., description="趋势")
    confidence: ConfidenceLevel = Field(..., description="置信度")
    data_points: List[Dict[str, Any]] = Field(default_factory=list, description="时间序列数据点")
    breakthrough_moments: List[BreakthroughMoment] = Field(default_factory=list, description="突破性时刻")


class DimensionTrends(BaseModel):
    """功能维度趋势数据（功能分析 Agent 的输出）"""
    active_dimensions: Dict[str, DimensionTrendData] = Field(..., description="活跃维度的趋势数据")
    top_improving: List[Dict[str, Any]] = Field(default_factory=list, description="进步最快的维度")
    needs_attention: List[Dict[str, Any]] = Field(default_factory=list, description="需要关注的维度")
    dimension_correlations: List[str] = Field(default_factory=list, description="维度之间的关联")
    analysis_summary: str = Field(..., description="分析总结")


# ============ 综合评估相关 ============

class NextPhaseGoal(BaseModel):
    """下阶段目标"""
    dimension: str = Field(..., description="目标维度")
    current: float = Field(..., description="当前水平")
    target: float = Field(..., description="目标水平")
    timeline: str = Field(..., description="时间线")
    strategy: str = Field(..., description="策略")


class AssessmentReport(BaseModel):
    """完整评估报告（综合评估 Agent 的输出）"""
    assessment_id: str = Field(..., description="评估ID")
    child_id: str = Field(..., description="孩子ID")
    assessment_type: AssessmentType = Field(..., description="评估类型")
    time_range: Dict[str, str] = Field(..., description="时间范围")
    
    # 整体评价
    overall_assessment: str = Field(..., description="整体发展评价（200-300字）")
    overall_score: float = Field(..., description="综合评分", ge=0, le=10)
    
    # 兴趣分析
    interest_analysis: Dict[str, Any] = Field(..., description="兴趣分析（包含热力图数据）")
    
    # 功能维度分析
    dimension_analysis: Dict[str, Any] = Field(..., description="功能维度分析（包含趋势数据）")
    
    # 突破性进步
    breakthroughs: List[Dict[str, Any]] = Field(default_factory=list, description="突破性进步")
    
    # 游戏表现总结
    game_performance: Optional[Dict[str, Any]] = Field(None, description="游戏表现总结")
    
    # 干预建议
    recommendations: List[str] = Field(..., description="干预建议（3-5条）")
    
    # 下阶段目标
    next_phase_goals: List[NextPhaseGoal] = Field(default_factory=list, description="下阶段目标")
    
    # 与上次评估对比
    comparison_with_previous: Optional[Dict[str, Any]] = Field(None, description="与上次评估对比")
    
    # 数据来源
    data_sources: Dict[str, Any] = Field(..., description="数据来源")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    generated_by: str = Field(default="AI", description="生成者")
    version: str = Field(default="1.0", description="版本")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# ============ API 请求/响应 ============

class AssessmentRequest(BaseModel):
    """评估请求"""
    child_id: str = Field(..., description="孩子ID")
    assessment_type: AssessmentType = Field(default=AssessmentType.COMPREHENSIVE, description="评估类型")
    time_range_days: int = Field(default=30, description="时间范围（天数）")


class AssessmentResponse(BaseModel):
    """评估响应"""
    assessment_id: str
    child_id: str
    timestamp: datetime
    report: AssessmentReport
    interest_heatmap: Optional[InterestHeatmap] = None
    dimension_trends: Optional[DimensionTrends] = None
    message: str = "评估生成成功"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }



class AssessmentHistoryRequest(BaseModel):
    """评估历史请求"""
    child_id: str = Field(..., description="孩子ID")
    assessment_type: Optional[AssessmentType] = Field(None, description="评估类型（可选）")
    limit: int = Field(default=10, description="返回数量限制")


class AssessmentHistoryResponse(BaseModel):
    """评估历史响应"""
    child_id: str
    assessments: List[Dict[str, Any]]
    total: int
    message: str = "评估历史获取成功"
