"""
API接口模块 - 简洁的函数式接口
"""
from typing import Optional, List, Dict, Any

try:
    from .service import SQLiteService
    from .config import SQLiteConfig
except ImportError:
    from service import SQLiteService
    from config import SQLiteConfig


# 全局实例
_service: Optional[SQLiteService] = None


def _get_service() -> SQLiteService:
    """获取服务实例"""
    global _service
    if _service is None:
        _service = SQLiteService()
    return _service


# ============ 孩子档案管理 ============

def get_child(child_id: str) -> Optional[Dict[str, Any]]:
    """
    获取孩子档案
    
    Args:
        child_id: 孩子ID
        
    Returns:
        孩子档案字典，如果不存在返回None
        
    Example:
        profile = get_child("child-001")
        print(profile['name'], profile['age'])
    """
    service = _get_service()
    return service.get_child(child_id)


def save_child(profile: Dict[str, Any]) -> None:
    """
    保存孩子档案
    
    Args:
        profile: 孩子档案字典，必须包含 child_id
        
    Example:
        save_child({
            'child_id': 'child-001',
            'name': '小明',
            'age': 36,  # 月
            'gender': '男',
            'eye_contact': 5.0,
            'strengths': ['喜欢积木', '专注力好']
        })
    """
    service = _get_service()
    service.save_child(profile)


def delete_child(child_id: str) -> None:
    """
    删除孩子档案
    
    Args:
        child_id: 孩子ID
        
    Example:
        delete_child("child-001")
    """
    service = _get_service()
    service.delete_child(child_id)


# ============ 会话管理 ============

def create_session(child_id: str, game_id: str) -> str:
    """
    创建干预会话
    
    Args:
        child_id: 孩子ID
        game_id: 游戏ID
        
    Returns:
        会话ID
        
    Example:
        session_id = create_session("child-001", "game-001")
    """
    service = _get_service()
    return service.create_session(child_id, game_id)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    获取会话信息
    
    Args:
        session_id: 会话ID
        
    Returns:
        会话信息字典，如果不存在返回None
        
    Example:
        session = get_session("session-abc123")
        print(session['status'], session['start_time'])
    """
    service = _get_service()
    return service.get_session(session_id)


def update_session(session_id: str, data: Dict[str, Any]) -> None:
    """
    更新会话信息
    
    Args:
        session_id: 会话ID
        data: 要更新的数据字典
        
    Example:
        update_session("session-abc123", {
            'status': 'in_progress',
            'start_time': datetime.now(),
            'quick_observations': [
                {'type': 'smile', 'timestamp': '...'}
            ]
        })
    """
    service = _get_service()
    service.update_session(session_id, data)


# ============ 周计划管理 ============

def save_weekly_plan(plan: Dict[str, Any]) -> str:
    """
    保存周计划
    
    Args:
        plan: 周计划字典
        
    Returns:
        计划ID
        
    Example:
        plan_id = save_weekly_plan({
            'child_id': 'child-001',
            'week_start': datetime(2026, 1, 27),
            'week_end': datetime(2026, 2, 2),
            'weekly_goal': '提升眼神接触',
            'daily_plans': [...]
        })
    """
    service = _get_service()
    return service.save_weekly_plan(plan)


def get_weekly_plan(plan_id: str) -> Optional[Dict[str, Any]]:
    """
    获取周计划
    
    Args:
        plan_id: 计划ID
        
    Returns:
        周计划字典，如果不存在返回None
        
    Example:
        plan = get_weekly_plan("plan-xyz789")
        print(plan['weekly_goal'], plan['daily_plans'])
    """
    service = _get_service()
    return service.get_weekly_plan(plan_id)


# ============ 观察记录管理 ============

def save_observation(observation: Dict[str, Any]) -> str:
    """
    保存观察记录
    
    Args:
        observation: 观察记录字典
        
    Returns:
        观察ID
        
    Example:
        obs_id = save_observation({
            'session_id': 'session-abc123',
            'child_id': 'child-001',
            'observation_type': 'quick',
            'timestamp': datetime.now(),
            'content': '孩子微笑了'
        })
    """
    service = _get_service()
    return service.save_observation(observation)


# ============ 会话历史查询 ============

def get_session_history(child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    获取会话历史
    
    Args:
        child_id: 孩子ID
        limit: 返回数量限制
        
    Returns:
        会话列表（按时间倒序）
        
    Example:
        history = get_session_history("child-001", limit=5)
        for session in history:
            print(session['game_name'], session['created_at'])
    """
    service = _get_service()
    return service.get_session_history(child_id, limit)
