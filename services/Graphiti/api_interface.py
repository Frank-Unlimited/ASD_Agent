"""
Graphiti API 接口
对外暴露的功能函数
"""
from typing import Any, Dict, List
from datetime import datetime, timedelta
import asyncio

try:
    from .service import get_service
except ImportError:
    from service import get_service


# ============ 记忆管理 ============

async def save_memories(child_id: str, memories: List[Dict[str, Any]]) -> None:
    """
    批量保存记忆到 Graphiti
    
    Args:
        child_id: 孩子ID
        memories: 记忆列表，每个记忆包含:
            - timestamp: 时间戳
            - type: 类型 (observation/milestone/feedback)
            - content: 内容描述
            - metadata: 元数据
    """
    service = get_service()
    
    # 为每个记忆创建 episode
    for memory in memories:
        episode_name = f"{child_id}_{memory.get('type', 'observation')}_{memory.get('timestamp')}"
        episode_content = _format_memory_content(memory)
        reference_time = datetime.fromisoformat(memory.get('timestamp', datetime.now().isoformat()))
        
        await service.add_episode(
            child_id=child_id,
            episode_name=episode_name,
            episode_content=episode_content,
            reference_time=reference_time
        )
    
    print(f"[Graphiti API] 成功保存 {len(memories)} 条记忆")


async def get_recent_memories(child_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """
    获取最近的记忆
    
    Args:
        child_id: 孩子ID
        days: 最近多少天
        
    Returns:
        记忆列表
    """
    service = get_service()
    
    # 搜索相关记忆
    memories = await service.search_memories(
        query=f"孩子 {child_id} 的观察记录和进展",
        num_results=50
    )
    
    # 过滤时间范围
    from datetime import timezone
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=days)
    filtered_memories = []
    
    for memory in memories:
        if memory.get('created_at'):
            try:
                created_at = datetime.fromisoformat(memory['created_at'])
                # 如果是 naive datetime，添加 UTC 时区
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
                
                if created_at >= cutoff_time:
                    filtered_memories.append({
                        "timestamp": memory['created_at'],
                        "type": "observation",
                        "content": memory['fact'],
                        "source": memory['source_node'],
                        "target": memory['target_node'],
                        "confidence": 0.8
                    })
            except (ValueError, TypeError):
                # 忽略无效的时间戳
                continue
    
    print(f"[Graphiti API] 找到 {len(filtered_memories)} 条最近记忆")
    return filtered_memories


# ============ 趋势分析 ============

async def analyze_trends(child_id: str, dimension: str) -> Dict[str, Any]:
    """
    分析某个维度的趋势
    
    Args:
        child_id: 孩子ID
        dimension: 维度名称 (如 eye_contact, two_way_communication)
        
    Returns:
        趋势分析结果
    """
    service = get_service()
    
    # 搜索该维度相关的记忆
    memories = await service.search_memories(
        query=f"孩子 {child_id} 在 {dimension} 维度的表现和变化",
        num_results=30
    )
    
    # 简单的趋势分析（实际应该更复杂）
    if len(memories) > 0:
        # 这里简化处理，实际应该分析时序数据
        trend = "improving" if len(memories) > 10 else "stable"
        rate = len(memories) / 30.0
    else:
        trend = "unknown"
        rate = 0.0
    
    return {
        "dimension": dimension,
        "trend": trend,
        "rate": rate,
        "dataPoints": len(memories),
        "lastUpdated": datetime.now().isoformat()
    }


# ============ 里程碑检测 ============

async def detect_milestones(child_id: str) -> List[Dict[str, Any]]:
    """
    检测里程碑事件
    
    Args:
        child_id: 孩子ID
        
    Returns:
        里程碑列表
    """
    service = get_service()
    
    # 搜索里程碑相关的记忆
    memories = await service.search_memories(
        query=f"孩子 {child_id} 的重要突破、首次出现、显著进步",
        num_results=20
    )
    
    # 转换为里程碑格式
    milestones = []
    for memory in memories:
        if "首次" in memory['fact'] or "突破" in memory['fact'] or "进步" in memory['fact']:
            milestones.append({
                "timestamp": memory.get('created_at'),
                "type": "breakthrough",
                "description": memory['fact'],
                "dimension": "unknown",  # 需要从内容中提取
                "significance": "high"
            })
    
    print(f"[Graphiti API] 检测到 {len(milestones)} 个里程碑")
    return milestones


# ============ 平台期检测 ============

async def detect_plateau(child_id: str, dimension: str) -> Dict[str, Any]:
    """
    检测平台期
    
    Args:
        child_id: 孩子ID
        dimension: 维度名称
        
    Returns:
        平台期检测结果
    """
    # 获取最近的趋势
    trend_result = await analyze_trends(child_id, dimension)
    
    # 简单判断：如果趋势是 stable 且数据点较多，可能是平台期
    is_plateau = (
        trend_result["trend"] == "stable" and 
        trend_result["dataPoints"] > 15
    )
    
    return {
        "dimension": dimension,
        "isPlateau": is_plateau,
        "duration": 3 if is_plateau else 0,  # 简化处理
        "suggestion": "考虑调整干预策略" if is_plateau else "继续当前计划"
    }


# ============ 上下文构建 ============

async def build_context(child_id: str) -> Dict[str, Any]:
    """
    构建当前上下文
    
    Args:
        child_id: 孩子ID
        
    Returns:
        上下文数据（包含趋势、关注点、活跃目标等）
    """
    # 并行获取多个维度的数据
    dimensions = [
        "eye_contact",
        "two_way_communication",
        "emotional_regulation"
    ]
    
    # 获取趋势
    trend_tasks = [analyze_trends(child_id, dim) for dim in dimensions]
    trends = await asyncio.gather(*trend_tasks)
    
    # 获取里程碑
    milestones = await detect_milestones(child_id)
    
    # 获取最近记忆
    recent_memories = await get_recent_memories(child_id, days=7)
    
    # 构建上下文
    context = {
        "recentTrends": {
            dim: trend 
            for dim, trend in zip(dimensions, trends)
        },
        "attentionPoints": _extract_attention_points(trends),
        "activeGoals": _extract_active_goals(recent_memories),
        "recentMilestones": milestones[:3],  # 最近3个里程碑
        "lastUpdated": datetime.now().isoformat()
    }
    
    print(f"[Graphiti API] 上下文构建完成")
    return context


# ============ 辅助函数 ============

def _format_memory_content(memory: Dict[str, Any]) -> str:
    """格式化记忆内容为文本"""
    content = memory.get('content', '')
    memory_type = memory.get('type', 'observation')
    timestamp = memory.get('timestamp', '')
    
    return f"""
时间: {timestamp}
类型: {memory_type}
内容: {content}
元数据: {memory.get('metadata', {})}
"""


def _extract_attention_points(trends: List[Dict[str, Any]]) -> List[str]:
    """从趋势中提取关注点"""
    attention_points = []
    
    for trend in trends:
        if trend.get("trend") == "declining":
            attention_points.append(f"{trend['dimension']} 需要关注")
        elif trend.get("trend") == "improving":
            attention_points.append(f"{trend['dimension']} 进展良好")
    
    return attention_points


def _extract_active_goals(memories: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """从记忆中提取活跃目标"""
    # 简化处理，实际应该从记忆中智能提取
    return [
        {
            "goal": "提升眼神接触频率",
            "status": "in_progress",
            "progress": 0.6
        }
    ]


# ============ 记忆清空 ============

async def clear_memories(child_id: str) -> None:
    """
    清空指定孩子的所有记忆
    
    Args:
        child_id: 孩子ID
    """
    service = get_service()
    
    # 使用 Neo4j 直接删除所有相关节点和边
    # 注意：这是一个危险操作，需要谨慎使用
    query = """
    MATCH (n)
    WHERE n.group_id = $child_id OR n.source_description CONTAINS $child_id
    DETACH DELETE n
    """
    
    try:
        # 执行删除查询
        async with service.client.driver.session() as session:
            await session.run(query, child_id=child_id)
        
        print(f"[Graphiti API] 已清空孩子 {child_id} 的所有记忆")
    except Exception as e:
        print(f"[Graphiti API] 清空记忆失败: {e}")
        raise
