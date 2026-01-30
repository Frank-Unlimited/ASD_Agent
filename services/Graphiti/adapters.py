"""
系统适配器
将 Graphiti 模块适配到系统的 IGraphitiService 接口
"""
from typing import Dict, Any, List, Optional

# 导入系统接口
from src.interfaces.infrastructure import IGraphitiService

# 导入核心功能
from . import api_interface


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
        return "2.0.0"  # 重构版本
    
    # ============ 数据存储接口 ============
    
    async def save_observations(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        保存观察数据
        
        Args:
            input_data: 标准输入 JSON
        
        Returns:
            操作结果
        """
        return await api_interface.save_observations(input_data)
    
    # ============ 趋势分析接口 ============
    
    async def get_full_trend(self, child_id: str) -> Dict[str, Any]:
        """
        获取完整趋势分析
        
        Args:
            child_id: 孩子ID
        
        Returns:
            完整趋势分析结果
        """
        return await api_interface.get_full_trend(child_id)
    
    async def get_dimension_trend(
        self,
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
            单维度趋势数据
        """
        return await api_interface.get_dimension_trend(child_id, dimension, include_data_points)
    
    async def get_quick_summary(self, child_id: str) -> Dict[str, Any]:
        """
        获取快速摘要
        
        Args:
            child_id: 孩子ID
        
        Returns:
            趋势摘要
        """
        return await api_interface.get_quick_summary(child_id)
    
    # ============ 里程碑接口 ============
    
    async def get_milestones(
        self,
        child_id: str,
        days: Optional[int] = None,
        dimension: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取里程碑
        
        Args:
            child_id: 孩子ID
            days: 最近多少天
            dimension: 指定维度
        
        Returns:
            里程碑列表
        """
        return await api_interface.get_milestones(child_id, days, dimension)
    
    # ============ 关联分析接口 ============
    
    async def get_correlations(
        self,
        child_id: str,
        min_correlation: float = 0.3
    ) -> Dict[str, Any]:
        """
        获取维度关联
        
        Args:
            child_id: 孩子ID
            min_correlation: 最小相关系数阈值
        
        Returns:
            关联列表
        """
        return await api_interface.get_correlations(child_id, min_correlation)
    
    async def refresh_correlations(self, child_id: str) -> Dict[str, Any]:
        """
        刷新关联分析
        
        Args:
            child_id: 孩子ID
        
        Returns:
            操作结果
        """
        return await api_interface.refresh_correlations(child_id)
    
    # ============ 工具函数 ============
    
    async def clear_child_data(self, child_id: str) -> Dict[str, Any]:
        """
        清空孩子的所有数据
        
        Args:
            child_id: 孩子ID
        
        Returns:
            操作结果
        """
        return await api_interface.clear_child_data(child_id)


__all__ = ['GraphitiServiceAdapter']
