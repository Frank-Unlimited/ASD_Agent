"""
系统适配器
将 Graphiti 模块适配到系统的 IGraphitiService 接口
"""
from typing import Dict, Any, List

# 导入系统接口
from src.interfaces.infrastructure import IGraphitiService

# 导入核心功能
try:
    from .api_interface import (
        save_memories,
        get_recent_memories,
        analyze_trends,
        detect_milestones,
        detect_plateau,
        build_context,
        clear_memories,
    )
except ImportError:
    from api_interface import (
        save_memories,
        get_recent_memories,
        analyze_trends,
        detect_milestones,
        detect_plateau,
        build_context,
        clear_memories,
    )


class GraphitiServiceAdapter(IGraphitiService):
    """Graphiti 服务适配器"""
    
    def __init__(self):
        """初始化适配器"""
        pass
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "graphiti_service"
    
    def get_service_version(self) -> str:
        """获取服务版本"""
        return "1.0.0"
    
    # ============ 记忆管理 ============
    
    async def save_memories(self, child_id: str, memories: List[Dict[str, Any]]) -> None:
        """
        批量保存记忆（优化：一次性写入）
        
        Args:
            child_id: 孩子ID
            memories: 记忆列表
        """
        await save_memories(child_id, memories)
    
    async def get_recent_memories(self, child_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """
        获取最近记忆
        
        Args:
            child_id: 孩子ID
            days: 最近多少天
            
        Returns:
            记忆列表
        """
        return await get_recent_memories(child_id, days)
    
    # ============ 趋势分析 ============
    
    async def analyze_trends(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """
        分析趋势
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            
        Returns:
            趋势分析结果
        """
        return await analyze_trends(child_id, dimension)
    
    # ============ 里程碑检测 ============
    
    async def detect_milestones(self, child_id: str) -> List[Dict[str, Any]]:
        """
        检测里程碑
        
        Args:
            child_id: 孩子ID
            
        Returns:
            里程碑列表
        """
        return await detect_milestones(child_id)
    
    # ============ 平台期检测 ============
    
    async def detect_plateau(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """
        检测平台期
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            
        Returns:
            平台期检测结果
        """
        return await detect_plateau(child_id, dimension)
    
    # ============ 上下文构建 ============
    
    async def build_context(self, child_id: str) -> Dict[str, Any]:
        """
        构建当前上下文（趋势、关注点等）
        
        Args:
            child_id: 孩子ID
            
        Returns:
            上下文数据
        """
        return await build_context(child_id)
    
    async def clear_memories(self, child_id: str) -> None:
        """
        清空指定孩子的所有记忆
        
        Args:
            child_id: 孩子ID
        """
        await clear_memories(child_id)


__all__ = ['GraphitiServiceAdapter']
