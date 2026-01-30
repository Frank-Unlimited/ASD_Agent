"""
查询过滤器定义
用于各种节点的查询过滤
"""
from dataclasses import dataclass, field
from typing import Optional, List, Literal
from datetime import datetime


@dataclass
class BehaviorFilter:
    """行为节点查询过滤器"""
    child_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    event_type: Optional[Literal["social", "emotion", "communication", "firstTime", "other"]] = None
    significance: Optional[Literal["breakthrough", "improvement", "normal", "concern"]] = None
    observer_id: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = 0


@dataclass
class PersonFilter:
    """人物节点查询过滤器"""
    person_type: Optional[Literal["child", "parent", "teacher", "peer", "sibling", "other"]] = None
    related_to_child_id: Optional[str] = None
    role: Optional[str] = None
    limit: Optional[int] = None


@dataclass
class ObjectFilter:
    """对象节点查询过滤器"""
    interest_category: Optional[str] = None  # 通过边查询
    tags: Optional[List[str]] = None
    min_effectiveness: Optional[float] = None
    limit: Optional[int] = None


@dataclass
class GameFilter:
    """地板游戏查询过滤器"""
    child_id: Optional[str] = None
    status: Optional[Literal["recommended", "scheduled", "in_progress", "completed", "cancelled"]] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    implementer_id: Optional[str] = None
    limit: Optional[int] = None


@dataclass
class AssessmentFilter:
    """儿童评估查询过滤器"""
    child_id: Optional[str] = None
    assessment_type: Optional[Literal["comprehensive", "interest_mining", "trend_analysis"]] = None
    assessor_id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    limit: Optional[int] = None
