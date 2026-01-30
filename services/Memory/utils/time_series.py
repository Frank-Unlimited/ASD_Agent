"""
时间序列处理工具
"""
from typing import List, Dict, Any, Tuple
from datetime import datetime
from collections import defaultdict


def aggregate_daily(data_points: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    按日聚合数据点（取每日最后一条记录）
    
    Args:
        data_points: 数据点列表，每个包含 timestamp 和 value
        
    Returns:
        按日聚合后的数据点列表
    """
    if not data_points:
        return []
    
    # 按日期分组
    daily_data = defaultdict(list)
    
    for point in data_points:
        timestamp = point.get('timestamp', '')
        if not timestamp:
            continue
        
        # 提取日期部分
        try:
            date = timestamp.split('T')[0]  # ISO 8601 格式
            daily_data[date].append(point)
        except Exception:
            continue
    
    # 每天取最后一条记录
    aggregated = []
    for date in sorted(daily_data.keys()):
        points = daily_data[date]
        # 按时间戳排序，取最后一条
        points.sort(key=lambda x: x.get('timestamp', ''))
        aggregated.append(points[-1])
    
    return aggregated


def align_series(
    series_a: List[Dict[str, Any]],
    series_b: List[Dict[str, Any]]
) -> Tuple[List[float], List[float], List[str]]:
    """
    对齐两个时间序列
    
    Args:
        series_a: 时间序列A
        series_b: 时间序列B
        
    Returns:
        (aligned_a, aligned_b, timestamps): 对齐后的数值序列和时间戳
    """
    # 构建时间戳到值的映射
    map_a = {point['timestamp']: point['value'] for point in series_a}
    map_b = {point['timestamp']: point['value'] for point in series_b}
    
    # 找到共同的时间戳
    common_timestamps = sorted(set(map_a.keys()) & set(map_b.keys()))
    
    # 对齐数据
    aligned_a = [map_a[ts] for ts in common_timestamps]
    aligned_b = [map_b[ts] for ts in common_timestamps]
    
    return aligned_a, aligned_b, common_timestamps
