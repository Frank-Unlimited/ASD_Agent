"""
Graphiti 图存储模块 - v3.0 记忆驱动架构

核心功能：
- 7种节点类型：Person, Behavior, Object, InterestDimension, FunctionDimension, FloorTimeGame, ChildAssessment
- 固定维度节点：8个兴趣维度 + 33个功能维度
- 时间序列追溯：通过边的时间戳记录历史变化
- 负面事件处理：完整的负面事件记录规范
- 人物关联优化：支持4种角色（facilitator/participant/observer/trigger）

注意：此模块只负责图数据库操作，业务逻辑请使用 services/Memory 模块
"""

# 导出核心模型
from .models.nodes import Person, Behavior, Object, InterestDimension, FunctionDimension, FloorTimeGame, ChildAssessment
from .models.edges import EdgeType
from .models.dimensions import INTEREST_DIMENSIONS, FUNCTION_DIMENSIONS

# 导出存储层
from .storage.graph_storage import GraphStorage

__all__ = [
    # 节点模型
    'Person', 'Behavior', 'Object', 'InterestDimension', 'FunctionDimension', 'FloorTimeGame', 'ChildAssessment',
    # 边类型
    'EdgeType',
    # 维度定义
    'INTEREST_DIMENSIONS', 'FUNCTION_DIMENSIONS',
    # 存储层
    'GraphStorage',
]
