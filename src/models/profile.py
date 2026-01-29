"""
孩子档案数据模型
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Gender(str, Enum):
    """性别枚举"""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class DiagnosisLevel(str, Enum):
    """诊断级别"""
    MILD = "mild"  # 轻度
    MODERATE = "moderate"  # 中度
    SEVERE = "severe"  # 重度
    SUSPECTED = "suspected"  # 疑似
    NOT_DIAGNOSED = "not_diagnosed"  # 未诊断


class DevelopmentDimension(BaseModel):
    """发展维度"""
    dimension_id: str = Field(..., description="维度ID（如eye_contact, language等）")
    dimension_name: str = Field(..., description="维度名称")
    current_level: Optional[float] = Field(None, description="当前水平（0-10）", ge=0, le=10)
    description: Optional[str] = Field(None, description="详细描述")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")


class InterestPoint(BaseModel):
    """兴趣点"""
    interest_id: str = Field(..., description="兴趣点ID")
    name: str = Field(..., description="兴趣点名称（如'水流'、'旋转物体'）")
    intensity: float = Field(..., description="兴趣强度（0-10）", ge=0, le=10)
    discovered_date: Optional[datetime] = Field(None, description="发现日期")
    description: Optional[str] = Field(None, description="详细描述")
    tags: List[str] = Field(default_factory=list, description="标签")


class ParsedProfileData(BaseModel):
    """从档案图片/文档中解析出的数据"""
    diagnosis: Optional[str] = Field(None, description="诊断结果")
    diagnosis_level: Optional[DiagnosisLevel] = Field(None, description="诊断级别")
    birth_date: Optional[str] = Field(None, description="出生日期（YYYY-MM-DD）")
    assessment_date: Optional[str] = Field(None, description="评估日期")
    key_findings: List[str] = Field(default_factory=list, description="关键发现")
    development_dimensions: List[DevelopmentDimension] = Field(
        default_factory=list,
        description="发展维度评估"
    )
    interests: List[str] = Field(default_factory=list, description="兴趣点列表")
    recommendations: List[str] = Field(default_factory=list, description="医生建议")
    raw_text: Optional[str] = Field(None, description="原始解析文本")


class ChildProfile(BaseModel):
    """孩子档案（完整信息）"""
    child_id: str = Field(..., description="孩子唯一ID")
    name: str = Field(..., description="孩子姓名")
    gender: Gender = Field(..., description="性别")
    birth_date: str = Field(..., description="出生日期（YYYY-MM-DD）")

    # 诊断信息
    diagnosis: Optional[str] = Field(None, description="诊断结果")
    diagnosis_level: Optional[DiagnosisLevel] = Field(None, description="诊断级别")
    diagnosis_date: Optional[str] = Field(None, description="诊断日期")

    # 发展维度
    development_dimensions: List[DevelopmentDimension] = Field(
        default_factory=list,
        description="各发展维度当前状态"
    )

    # 兴趣点
    interests: List[InterestPoint] = Field(
        default_factory=list,
        description="兴趣点列表"
    )

    # 档案文件
    archive_files: List[str] = Field(
        default_factory=list,
        description="档案文件路径列表（图片、PDF等）"
    )

    # 元数据
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    # 额外信息
    notes: Optional[str] = Field(None, description="家长备注")
    custom_fields: Dict[str, Any] = Field(default_factory=dict, description="自定义字段")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProfileUpdateRequest(BaseModel):
    """档案更新请求"""
    name: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[str] = None
    diagnosis: Optional[str] = None
    diagnosis_level: Optional[DiagnosisLevel] = None
    notes: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = None


class ProfileCreateResponse(BaseModel):
    """档案创建响应"""
    child_id: str
    name: str
    parsed_data: ParsedProfileData
    message: str = "档案创建成功"
