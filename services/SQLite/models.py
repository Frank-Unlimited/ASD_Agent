"""
数据模型定义
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChildProfile(BaseModel):
    """孩子档案模型"""
    child_id: str = Field(..., description="孩子ID")
    name: str = Field(..., description="孩子姓名")
    age: int = Field(..., description="年龄（月）")
    gender: str = Field(..., description="性别")
    diagnosis: Optional[str] = Field(None, description="诊断信息")
    
    # 6大维度评分（1-10分）
    eye_contact: Optional[float] = Field(None, description="眼神接触")
    two_way_communication: Optional[float] = Field(None, description="双向沟通")
    emotional_expression: Optional[float] = Field(None, description="情绪表达")
    problem_solving: Optional[float] = Field(None, description="问题解决")
    creative_thinking: Optional[float] = Field(None, description="创造性思维")
    logical_thinking: Optional[float] = Field(None, description="逻辑思维")
    
    # 自定义维度
    custom_dimensions: Optional[Dict[str, float]] = Field(None, description="自定义维度")
    
    # 画像信息
    strengths: Optional[List[str]] = Field(None, description="优势")
    weaknesses: Optional[List[str]] = Field(None, description="短板")
    interests: Optional[List[str]] = Field(None, description="兴趣")
    observation_framework: Optional[Dict[str, Any]] = Field(None, description="观察框架")
    focus_points: Optional[List[str]] = Field(None, description="关注点")
    
    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="其他元数据")


class Session(BaseModel):
    """干预会话模型"""
    session_id: str = Field(..., description="会话ID")
    child_id: str = Field(..., description="孩子ID")
    game_id: str = Field(..., description="游戏ID")
    game_name: Optional[str] = Field(None, description="游戏名称")
    
    # 会话状态
    status: str = Field("not_started", description="状态: not_started/in_progress/completed/analyzed")
    
    # 时间信息
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[int] = Field(None, description="时长（秒）")
    
    # 观察记录
    quick_observations: Optional[List[Dict[str, Any]]] = Field(None, description="快捷观察记录")
    voice_observations: Optional[List[Dict[str, Any]]] = Field(None, description="语音观察记录")
    
    # 视频相关
    has_video: bool = Field(False, description="是否有视频")
    video_path: Optional[str] = Field(None, description="视频路径")
    video_analysis: Optional[Dict[str, Any]] = Field(None, description="视频分析结果")
    verified_observations: Optional[List[Dict[str, Any]]] = Field(None, description="已验证的观察")
    
    # 总结相关
    preliminary_summary: Optional[Dict[str, Any]] = Field(None, description="初步总结")
    feedback_form: Optional[Dict[str, Any]] = Field(None, description="反馈表")
    parent_feedback: Optional[Dict[str, Any]] = Field(None, description="家长反馈")
    final_summary: Optional[Dict[str, Any]] = Field(None, description="最终总结")
    
    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="其他元数据")


class WeeklyPlan(BaseModel):
    """周计划模型"""
    plan_id: str = Field(..., description="计划ID")
    child_id: str = Field(..., description="孩子ID")
    week_start: datetime = Field(..., description="周开始日期")
    week_end: datetime = Field(..., description="周结束日期")
    
    # 计划目标
    weekly_goal: Optional[str] = Field(None, description="本周总目标")
    focus_dimensions: Optional[List[str]] = Field(None, description="重点提升维度")
    
    # 每日计划
    daily_plans: List[Dict[str, Any]] = Field(..., description="7天游戏计划")
    
    # 状态
    status: str = Field("active", description="状态: active/completed/cancelled")
    completion_rate: Optional[float] = Field(None, description="完成率")
    
    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="其他元数据")


class Observation(BaseModel):
    """观察记录模型"""
    observation_id: str = Field(..., description="观察ID")
    session_id: str = Field(..., description="会话ID")
    child_id: str = Field(..., description="孩子ID")
    
    # 观察类型
    observation_type: str = Field(..., description="类型: quick/voice/video")
    
    # 观察内容
    timestamp: datetime = Field(..., description="时间戳")
    content: str = Field(..., description="观察内容")
    structured_data: Optional[Dict[str, Any]] = Field(None, description="结构化数据")
    
    # 验证状态
    is_verified: bool = Field(False, description="是否已验证")
    verification_source: Optional[str] = Field(None, description="验证来源")
    
    # 元数据
    created_at: Optional[datetime] = Field(None, description="创建时间")
    metadata: Optional[Dict[str, Any]] = Field(None, description="其他元数据")
