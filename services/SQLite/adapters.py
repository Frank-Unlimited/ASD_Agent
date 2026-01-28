"""
系统适配器
将 SQLite 模块适配到系统的 ISQLiteService 接口
"""
from typing import Dict, Any, List, Optional

# 导入系统接口
from src.interfaces.infrastructure import ISQLiteService

# 导入核心功能
try:
    from .api_interface import (
        get_child, save_child, delete_child,
        create_session, get_session, update_session,
        save_weekly_plan, get_weekly_plan,
        save_observation,
        get_session_history
    )
except ImportError:
    from api_interface import (
        get_child, save_child, delete_child,
        create_session, get_session, update_session,
        save_weekly_plan, get_weekly_plan,
        save_observation,
        get_session_history
    )


class SQLiteServiceAdapter(ISQLiteService):
    """SQLite 服务适配器"""
    
    def __init__(self):
        """初始化适配器"""
        pass
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "sqlite_service"
    
    def get_service_version(self) -> str:
        """获取服务版本"""
        return "1.0.0"
    
    # ============ 孩子档案管理 ============
    
    async def get_child(self, child_id: str) -> Dict[str, Any]:
        """
        获取孩子档案
        
        Args:
            child_id: 孩子ID
            
        Returns:
            孩子档案字典
        """
        # 调用实际实现（同步转异步）
        result = get_child(child_id)
        if result is None:
            return {}
        return result
    
    async def save_child(self, profile: Dict[str, Any]) -> None:
        """
        保存孩子档案
        
        Args:
            profile: 孩子档案字典
        """
        # 调用实际实现（同步转异步）
        save_child(profile)
    
    async def delete_child(self, child_id: str) -> None:
        """
        删除孩子档案
        
        Args:
            child_id: 孩子ID
        """
        # 调用实际实现（同步转异步）
        delete_child(child_id)
    
    # ============ 会话管理 ============
    
    async def create_session(self, child_id: str, game_id: str) -> str:
        """
        创建干预会话
        
        Args:
            child_id: 孩子ID
            game_id: 游戏ID
            
        Returns:
            会话ID
        """
        # 调用实际实现（同步转异步）
        return create_session(child_id, game_id)
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话信息字典
        """
        # 调用实际实现（同步转异步）
        result = get_session(session_id)
        if result is None:
            return {}
        return result
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """
        更新会话信息
        
        Args:
            session_id: 会话ID
            data: 要更新的数据
        """
        # 调用实际实现（同步转异步）
        update_session(session_id, data)
    
    # ============ 周计划管理 ============
    
    async def save_weekly_plan(self, plan: Dict[str, Any]) -> str:
        """
        保存周计划
        
        Args:
            plan: 周计划字典
            
        Returns:
            计划ID
        """
        # 调用实际实现（同步转异步）
        return save_weekly_plan(plan)
    
    async def get_weekly_plan(self, plan_id: str) -> Dict[str, Any]:
        """
        获取周计划
        
        Args:
            plan_id: 计划ID
            
        Returns:
            周计划字典
        """
        # 调用实际实现（同步转异步）
        result = get_weekly_plan(plan_id)
        if result is None:
            return {}
        return result
    
    # ============ 观察记录管理 ============
    
    async def save_observation(self, observation: Dict[str, Any]) -> str:
        """
        保存观察记录
        
        Args:
            observation: 观察记录字典
            
        Returns:
            观察ID
        """
        # 调用实际实现（同步转异步）
        return save_observation(observation)
    
    # ============ 会话历史查询 ============
    
    async def get_session_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取会话历史
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
            
        Returns:
            会话列表
        """
        # 调用实际实现（同步转异步）
        return get_session_history(child_id, limit)


__all__ = ['SQLiteServiceAdapter']
