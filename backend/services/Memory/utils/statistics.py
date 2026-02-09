"""
统计函数工具
"""
from typing import List
import numpy as np


def calculate_mean(values: List[float]) -> float:
    """计算均值"""
    if not values:
        return 0.0
    return float(np.mean(values))


def calculate_std(values: List[float]) -> float:
    """计算标准差"""
    if not values:
        return 0.0
    return float(np.std(values))
