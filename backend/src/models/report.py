"""
报告生成数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ReportType(str, Enum):
    """报告类型"""
    MEDICAL = "medical"  # 医生版报告
    PARENT = "parent"  # 家长版报告
    SUMMARY = "summary"  # 阶段总结报告


class ReportFormat(str, Enum):
    """报告格式"""
    PDF = "pdf"
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"


class ChartType(str, Enum):
    """图表类型"""
    LINE = "line"  # 折线图
    RADAR = "radar"  # 雷达图
    BAR = "bar"  # 柱状图
    HEATMAP = "heatmap"  # 热力图
    SCATTER = "scatter"  # 散点图


class ChartData(BaseModel):
    """图表数据"""
    chart_type: ChartType = Field(..., description="图表类型")
    title: str = Field(..., description="图表标题")
    data: Dict[str, Any] = Field(..., description="图表数据（JSON格式）")
    description: Optional[str] = Field(None, description="图表说明")


class DevelopmentDimensionReport(BaseModel):
    """发展维度报告"""
    dimension_id: str = Field(..., description="维度ID")
    dimension_name: str = Field(..., description="维度名称")
    current_level: float = Field(..., description="当前水平（0-10）", ge=0, le=10)
    initial_level: Optional[float] = Field(None, description="初始水平", ge=0, le=10)
    change: Optional[float] = Field(None, description="变化值")
    trend: str = Field(..., description="趋势（improving/stable/declining）")
    key_observations: List[str] = Field(default_factory=list, description="关键观察")
    milestones_achieved: List[str] = Field(default_factory=list, description="已达成里程碑")
    recommendations: List[str] = Field(default_factory=list, description="建议")


class InterventionSummary(BaseModel):
    """干预总结"""
    total_sessions: int = Field(..., description="总会话数")
    total_duration_hours: float = Field(..., description="总时长（小时）")
    games_implemented: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="实施的游戏列表"
    )
    most_effective_game: Optional[str] = Field(None, description="最有效的游戏")
    avg_engagement_score: Optional[float] = Field(
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


class ObservationSummary(BaseModel):
    """观察记录总结"""
    total_observations: int = Field(..., description="总观察次数")
    voice_observations: int = Field(default=0, description="语音观察次数")
    text_observations: int = Field(default=0, description="文字观察次数")
    video_observations: int = Field(default=0, description="视频观察次数")
    breakthrough_count: int = Field(default=0, description="突破性进展次数")
    concern_count: int = Field(default=0, description="需要关注的次数")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")


class MedicalReport(BaseModel):
    """医生版报告"""
    report_id: str = Field(..., description="报告唯一ID")
    child_id: str = Field(..., description="孩子ID")
    report_type: ReportType = Field(default=ReportType.MEDICAL, description="报告类型")

    # 基础信息
    child_name: str = Field(..., description="孩子姓名")
    gender: str = Field(..., description="性别")
    birth_date: str = Field(..., description="出生日期")
    age: str = Field(..., description="年龄")
    diagnosis: Optional[str] = Field(None, description="诊断")

    # 报告时间范围
    report_period_start: str = Field(..., description="报告周期开始日期")
    report_period_end: str = Field(..., description="报告周期结束日期")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")

    # 发展维度评估
    development_dimensions: List[DevelopmentDimensionReport] = Field(
        ...,
        description="各发展维度评估"
    )

    # 观察记录总结
    observation_summary: ObservationSummary = Field(..., description="观察记录总结")

    # 干预总结
    intervention_summary: InterventionSummary = Field(..., description="干预总结")

    # 整体评估
    overall_progress: str = Field(..., description="总体进展评估")
    strengths: List[str] = Field(default_factory=list, description="优势领域")
    areas_for_improvement: List[str] = Field(default_factory=list, description="需要改善的领域")

    # 趋势图表
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")

    # 专业建议
    clinical_recommendations: List[str] = Field(
        default_factory=list,
        description="临床建议"
    )
    next_assessment_date: Optional[str] = Field(
        None,
        description="建议下次评估日期"
    )

    # 附加信息
    notes: Optional[str] = Field(None, description="备注")
    appendices: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="附录（详细数据、图片等）"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ParentReport(BaseModel):
    """家长版报告（简化版）"""
    report_id: str = Field(..., description="报告唯一ID")
    child_id: str = Field(..., description="孩子ID")
    report_type: ReportType = Field(default=ReportType.PARENT, description="报告类型")

    # 基础信息
    child_name: str = Field(..., description="孩子姓名")
    report_period_start: str = Field(..., description="报告周期开始日期")
    report_period_end: str = Field(..., description="报告周期结束日期")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")

    # 进步亮点
    highlights: List[str] = Field(default_factory=list, description="进步亮点")

    # 发展情况（简化）
    development_summary: str = Field(..., description="发展情况总结")

    # 游戏实施情况
    games_completed: int = Field(..., description="完成的游戏数")
    favorite_games: List[str] = Field(default_factory=list, description="孩子最喜欢的游戏")

    # 下一步建议
    recommendations: List[str] = Field(default_factory=list, description="家长可以做的事")

    # 图表（简化）
    charts: List[ChartData] = Field(default_factory=list, description="图表数据")

    # 鼓励的话
    encouragement: Optional[str] = Field(None, description="鼓励的话")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReportGenerateRequest(BaseModel):
    """报告生成请求"""
    child_id: str
    report_type: ReportType
    start_date: str = Field(..., description="开始日期（YYYY-MM-DD）")
    end_date: str = Field(..., description="结束日期（YYYY-MM-DD）")
    format: ReportFormat = Field(default=ReportFormat.PDF, description="报告格式")
    include_charts: bool = Field(default=True, description="是否包含图表")
    include_raw_data: bool = Field(default=False, description="是否包含原始数据")


class ReportResponse(BaseModel):
    """报告生成响应"""
    report_id: str
    child_id: str
    report_type: ReportType
    format: ReportFormat
    file_path: Optional[str] = Field(None, description="报告文件路径（如果是PDF/HTML）")
    data: Optional[Any] = Field(None, description="报告数据（如果是JSON）")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")
    message: str = "报告生成成功"

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ReportDownloadRequest(BaseModel):
    """报告下载请求"""
    report_id: str


class ReportListResponse(BaseModel):
    """报告列表响应"""
    child_id: str
    reports: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="报告列表 [{report_id, type, date, file_path}]"
    )
    total: int = Field(default=0, description="报告总数")
