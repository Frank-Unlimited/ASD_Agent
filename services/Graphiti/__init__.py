"""
Graphiti 记忆网络模块
基于 graphiti-core 实现的时序记忆图谱
"""

from .api_interface import (
    save_memories,
    get_recent_memories,
    analyze_trends,
    detect_milestones,
    detect_plateau,
    build_context,
)

from .adapters import GraphitiServiceAdapter

__all__ = [
    'save_memories',
    'get_recent_memories',
    'analyze_trends',
    'detect_milestones',
    'detect_plateau',
    'build_context',
    'GraphitiServiceAdapter',
]

__version__ = '1.0.0'
