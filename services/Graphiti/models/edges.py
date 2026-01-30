"""
图边类型定义
"""
from enum import Enum


class EdgeType(Enum):
    """边类型枚举"""
    HAS_DIMENSION = "HAS_DIMENSION"          # Child -> Dimension
    HAS_OBSERVATION = "HAS_OBSERVATION"      # Dimension -> Observation
    TRIGGERS = "TRIGGERS"                    # Observation -> Milestone
    CORRELATES_WITH = "CORRELATES_WITH"      # Dimension <-> Dimension
