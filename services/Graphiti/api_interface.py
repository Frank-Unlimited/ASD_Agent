"""
Graphiti API 接口
对外暴露的功能函数 - 完全重构版本
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from .service import get_service
from .models.output import (
    DimensionTrend,
    TrendAnalysisResult,
    TrendSummary,
    Milestone,
    Correlation
)


# ============ 数据存储接口 ============

async def save_observations(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    保存观察数据（新标准接口）
    
    Args:
        input_data: 标准输入 JSON，格式见设计文档第3节
            {
                "child_id": "child-001",
                "timestamp": "2026-01-29T14:30:00Z",
                "source": "observation_agent",
                "session_id": "session-20260129-001",
                "observations": [
                    {
                        "dimension": "eye_contact",
                        "value": 8,
                        "value_type": "score",
                        "context": "积木游戏中主动看向家长",
                        "confidence": 0.85
                    }
                ],
                "milestone": {
                    "detected": true,
                    "type": "first_time",
                    "description": "首次主动发起眼神接触",
                    "dimension": "eye_contact"
                }
            }
    
    Returns:
        {"success": True, "message": "..."}
    """
    service = await get_service()
    
    try:
        await service.save_observations(input_data)
        observation_count = len(input_data.get('observations', []))
        return {
            "success": True,
            "message": f"成功保存 {observation_count} 条观察记录"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"保存失败: {str(e)}"
        }


# ============ 趋势分析接口 ============

async def get_full_trend(child_id: str) -> Dict[str, Any]:
    """
    获取完整趋势分析
    
    Args:
        child_id: 孩子ID
    
    Returns:
        完整趋势分析结果（JSON格式）
    """
    service = await get_service()
    
    try:
        result = await service.get_full_trend(child_id)
        
        # 转换为 JSON 可序列化的格式
        return {
            "success": True,
            "data": _serialize_trend_analysis_result(result)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取趋势失败: {str(e)}"
        }


async def get_dimension_trend(
    child_id: str,
    dimension: str,
    include_data_points: bool = True
) -> Dict[str, Any]:
    """
    获取单维度趋势
    
    Args:
        child_id: 孩子ID
        dimension: 维度名称
        include_data_points: 是否包含原始数据点
    
    Returns:
        单维度趋势数据（JSON格式）
    """
    service = await get_service()
    
    try:
        result = await service.get_dimension_trend(child_id, dimension, include_data_points)
        
        return {
            "success": True,
            "data": _serialize_dimension_trend(result)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取维度趋势失败: {str(e)}"
        }


async def get_quick_summary(child_id: str) -> Dict[str, Any]:
    """
    获取快速摘要
    
    Args:
        child_id: 孩子ID
    
    Returns:
        趋势摘要（JSON格式）
    """
    service = await get_service()
    
    try:
        result = await service.get_quick_summary(child_id)
        
        return {
            "success": True,
            "data": _serialize_trend_summary(result)
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取摘要失败: {str(e)}"
        }


# ============ 里程碑接口 ============

async def get_milestones(
    child_id: str,
    days: Optional[int] = None,
    dimension: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取里程碑
    
    Args:
        child_id: 孩子ID
        days: 最近多少天（None 表示全部）
        dimension: 指定维度（None 表示全部）
    
    Returns:
        里程碑列表（JSON格式）
    """
    service = await get_service()
    
    try:
        result = await service.get_milestones(child_id, days, dimension)
        
        return {
            "success": True,
            "data": [_serialize_milestone(m) for m in result]
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取里程碑失败: {str(e)}"
        }


# ============ 关联分析接口 ============

async def get_correlations(
    child_id: str,
    min_correlation: float = 0.3
) -> Dict[str, Any]:
    """
    获取维度关联
    
    Args:
        child_id: 孩子ID
        min_correlation: 最小相关系数阈值
    
    Returns:
        关联列表（JSON格式）
    """
    service = await get_service()
    
    try:
        correlations_data = await service.storage.get_correlations(child_id, min_correlation)
        
        correlations = [
            {
                "dimension_a": c.get("dimension_a"),
                "dimension_b": c.get("dimension_b"),
                "correlation": c.get("correlation"),
                "lag_days": c.get("lag_days"),
                "relationship": c.get("relationship"),
                "confidence": c.get("confidence"),
                "p_value": c.get("p_value")
            }
            for c in correlations_data
        ]
        
        return {
            "success": True,
            "data": correlations
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"获取关联失败: {str(e)}"
        }


async def refresh_correlations(child_id: str) -> Dict[str, Any]:
    """
    刷新关联分析
    
    Args:
        child_id: 孩子ID
    
    Returns:
        操作结果
    """
    service = await get_service()
    
    try:
        await service.refresh_correlations(child_id)
        
        return {
            "success": True,
            "message": "关联分析已刷新"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"刷新关联失败: {str(e)}"
        }


# ============ 工具函数 ============

async def clear_child_data(child_id: str) -> Dict[str, Any]:
    """
    清空孩子的所有数据
    
    Args:
        child_id: 孩子ID
    
    Returns:
        操作结果
    """
    service = await get_service()
    
    try:
        await service.storage.clear_child_data(child_id)
        
        return {
            "success": True,
            "message": f"已清空孩子 {child_id} 的所有数据"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"清空数据失败: {str(e)}"
        }


# ============ 序列化辅助函数 ============

def _serialize_trend_info(trend: Any) -> Dict[str, Any]:
    """序列化 TrendInfo"""
    return {
        "direction": trend.direction,
        "rate": trend.rate,
        "confidence": trend.confidence,
        "p_value": trend.p_value
    }


def _serialize_plateau_info(plateau: Any) -> Dict[str, Any]:
    """序列化 PlateauInfo"""
    return {
        "is_plateau": plateau.is_plateau,
        "duration_days": plateau.duration_days,
        "suggestion": plateau.suggestion
    }


def _serialize_anomaly_info(anomaly: Any) -> Dict[str, Any]:
    """序列化 AnomalyInfo"""
    return {
        "has_anomaly": anomaly.has_anomaly,
        "anomaly_type": anomaly.anomaly_type,
        "anomaly_value": anomaly.anomaly_value,
        "anomaly_date": anomaly.anomaly_date,
        "interpretation": anomaly.interpretation
    }


def _serialize_data_point(point: Any) -> Dict[str, Any]:
    """序列化 DataPoint"""
    return {
        "timestamp": point.timestamp,
        "value": point.value,
        "source": point.source,
        "confidence": point.confidence,
        "context": point.context
    }


def _serialize_dimension_trend(trend: DimensionTrend) -> Dict[str, Any]:
    """序列化 DimensionTrend"""
    return {
        "dimension": trend.dimension,
        "display_name": trend.display_name,
        "category": trend.category,
        "current_value": trend.current_value,
        "baseline_value": trend.baseline_value,
        "total_improvement": trend.total_improvement,
        "trend_7d": _serialize_trend_info(trend.trend_7d),
        "trend_30d": _serialize_trend_info(trend.trend_30d),
        "trend_90d": _serialize_trend_info(trend.trend_90d),
        "plateau": _serialize_plateau_info(trend.plateau),
        "anomaly": _serialize_anomaly_info(trend.anomaly),
        "data_points": [_serialize_data_point(p) for p in trend.data_points],
        "data_point_count": trend.data_point_count
    }


def _serialize_milestone(milestone: Milestone) -> Dict[str, Any]:
    """序列化 Milestone"""
    return {
        "milestone_id": milestone.milestone_id,
        "dimension": milestone.dimension,
        "type": milestone.type,
        "description": milestone.description,
        "timestamp": milestone.timestamp,
        "significance": milestone.significance
    }


def _serialize_trend_summary(summary: TrendSummary) -> Dict[str, Any]:
    """序列化 TrendSummary"""
    return {
        "attention_dimensions": summary.attention_dimensions,
        "improving_dimensions": summary.improving_dimensions,
        "stable_dimensions": summary.stable_dimensions,
        "overall_status": summary.overall_status,
        "recommendation": summary.recommendation
    }


def _serialize_trend_analysis_result(result: TrendAnalysisResult) -> Dict[str, Any]:
    """序列化 TrendAnalysisResult"""
    return {
        "child_id": result.child_id,
        "child_name": result.child_name,
        "analysis_time": result.analysis_time,
        "dimensions": {
            dim: _serialize_dimension_trend(trend)
            for dim, trend in result.dimensions.items()
        },
        "recent_milestones": [_serialize_milestone(m) for m in result.recent_milestones],
        "total_milestones": result.total_milestones,
        "correlations": result.correlations,  # 已经是字典格式
        "summary": _serialize_trend_summary(result.summary)
    }


# ============ 兼容旧API的适配函数 ============

async def save_memories(child_id: str, memories: List[Dict[str, Any]]) -> None:
    """
    兼容旧API: 保存记忆
    
    将旧格式的memories转换为新格式的observations
    
    旧格式:
    {
        "content": "描述文本",
        "type": "observation/milestone/improvement",
        "timestamp": "ISO时间",
        "metadata": {...}
    }
    
    新格式:
    {
        "child_id": "...",
        "timestamp": "...",
        "source": "...",
        "observations": [
            {
                "dimension": "...",
                "value": ...,
                "value_type": "score/count/duration",
                "context": "...",
                "confidence": 0.8
            }
        ],
        "milestone": {...}
    }
    """
    service = await get_service()
    
    # 按时间戳分组memories
    grouped_by_time = {}
    for memory in memories:
        timestamp = memory.get("timestamp", datetime.now().isoformat())
        if timestamp not in grouped_by_time:
            grouped_by_time[timestamp] = []
        grouped_by_time[timestamp].append(memory)
    
    # 转换并保存每组
    for timestamp, memory_group in grouped_by_time.items():
        # 构建新格式的输入
        input_data = {
            "child_id": child_id,
            "timestamp": timestamp,
            "source": memory_group[0].get("metadata", {}).get("source", "legacy_api"),
            "session_id": memory_group[0].get("metadata", {}).get("session_id"),
            "observations": []
        }
        
        # 转换每个memory
        milestone_detected = False
        for memory in memory_group:
            content = memory.get("content", "")
            memory_type = memory.get("type", "observation")
            metadata = memory.get("metadata", {})
            
            # 尝试从content和metadata中提取维度和值
            dimension = metadata.get("dimension", "other")
            
            # 尝试从metadata中获取值
            value = metadata.get("level") or metadata.get("score") or metadata.get("engagement_score") or metadata.get("achievement_score")
            
            # 如果没有明确的值,尝试从content中推断
            if value is None:
                # 简单的启发式: 查找数字
                import re
                numbers = re.findall(r'\d+\.?\d*', content)
                if numbers:
                    value = float(numbers[0])
                else:
                    value = 5.0  # 默认中等值
            
            # 确定value_type
            value_type = "score"
            if "次" in content or "count" in str(metadata):
                value_type = "count"
            elif "分钟" in content or "duration" in str(metadata):
                value_type = "duration"
            
            # 添加观察
            observation = {
                "dimension": dimension,
                "value": float(value),
                "value_type": value_type,
                "context": content,
                "confidence": metadata.get("confidence", 0.7)
            }
            input_data["observations"].append(observation)
            
            # 检查是否是里程碑
            if memory_type in ["milestone", "breakthrough"] and not milestone_detected:
                input_data["milestone"] = {
                    "detected": True,
                    "type": "breakthrough" if memory_type == "breakthrough" else "significant_improvement",
                    "description": content,
                    "dimension": dimension
                }
                milestone_detected = True
        
        # 保存到新系统
        if input_data["observations"]:
            await service.save_observations(input_data)


async def build_context(child_id: str) -> Dict[str, Any]:
    """
    兼容旧API: 构建上下文
    
    返回格式:
    {
        "recentTrends": {
            "dimension_name": {
                "trend": "improving/stable/declining",
                "rate": 0.15,
                "current_value": 7.5
            }
        },
        "attentionPoints": ["需要关注的点1", "需要关注的点2"],
        "activeGoals": [...],
        "recentMilestones": [...]
    }
    """
    service = await get_service()
    
    # 获取完整趋势分析
    full_trend = await service.get_full_trend(child_id)
    
    # 转换为旧格式
    recent_trends = {}
    for dim_name, dim_trend in full_trend.dimensions.items():
        recent_trends[dim_name] = {
            "trend": dim_trend.trend_30d.direction,
            "rate": dim_trend.trend_30d.rate,
            "current_value": dim_trend.current_value
        }
    
    # 构建关注点
    attention_points = []
    for dim_name in full_trend.summary.attention_dimensions:
        dim_trend = full_trend.dimensions.get(dim_name)
        if dim_trend:
            if dim_trend.plateau.is_plateau:
                attention_points.append(f"{dim_trend.display_name}出现平台期，已持续{dim_trend.plateau.duration_days}天")
            elif dim_trend.trend_30d.direction == "declining":
                attention_points.append(f"{dim_trend.display_name}呈下降趋势，需要关注")
    
    # 获取最近里程碑
    recent_milestones = [
        {
            "description": m.description,
            "dimension": m.dimension,
            "timestamp": m.timestamp,
            "type": m.type
        }
        for m in full_trend.recent_milestones
    ]
    
    return {
        "recentTrends": recent_trends,
        "attentionPoints": attention_points,
        "activeGoals": [],  # 新系统不再维护goals
        "recentMilestones": recent_milestones
    }


async def get_recent_memories(child_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    兼容旧API: 获取最近记忆
    
    返回格式:
    [
        {
            "content": "描述文本",
            "type": "observation",
            "timestamp": "ISO时间",
            "metadata": {...}
        }
    ]
    """
    service = await get_service()
    
    # 获取所有维度的数据点
    memories = []
    
    # 获取完整趋势(包含数据点)
    full_trend = await service.get_full_trend(child_id)
    
    # 从每个维度提取最近的数据点
    from datetime import datetime, timedelta
    cutoff_time = datetime.now() - timedelta(days=days)
    
    for dim_name, dim_trend in full_trend.dimensions.items():
        for point in dim_trend.data_points:
            point_time = datetime.fromisoformat(point.timestamp.replace('Z', '+00:00'))
            if point_time >= cutoff_time:
                memories.append({
                    "content": point.context or f"{dim_trend.display_name}: {point.value}",
                    "type": "observation",
                    "timestamp": point.timestamp,
                    "metadata": {
                        "dimension": dim_name,
                        "value": point.value,
                        "source": point.source,
                        "confidence": point.confidence
                    }
                })
    
    # 按时间排序
    memories.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return memories


async def analyze_trends(child_id: str) -> Dict[str, Any]:
    """
    兼容旧API: 分析趋势
    
    返回格式:
    {
        "dimensions": {
            "dimension_name": {
                "trend": "improving/stable/declining",
                "rate": 0.15,
                "current_value": 7.5,
                "baseline_value": 6.0
            }
        }
    }
    """
    service = await get_service()
    
    # 获取完整趋势
    full_trend = await service.get_full_trend(child_id)
    
    # 转换为旧格式
    dimensions = {}
    for dim_name, dim_trend in full_trend.dimensions.items():
        dimensions[dim_name] = {
            "trend": dim_trend.trend_30d.direction,
            "rate": dim_trend.trend_30d.rate,
            "current_value": dim_trend.current_value,
            "baseline_value": dim_trend.baseline_value
        }
    
    return {
        "dimensions": dimensions
    }


async def detect_milestones(child_id: str) -> List[Dict[str, Any]]:
    """
    兼容旧API: 检测里程碑
    
    返回格式:
    [
        {
            "description": "描述",
            "dimension": "维度",
            "timestamp": "时间",
            "type": "类型"
        }
    ]
    """
    service = await get_service()
    
    # 获取最近30天的里程碑
    milestones = await service.get_milestones(child_id, days=30)
    
    # 转换为旧格式
    return [
        {
            "description": m.description,
            "dimension": m.dimension,
            "timestamp": m.timestamp,
            "type": m.type
        }
        for m in milestones
    ]
