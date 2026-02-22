"""
SQLite 数据管理模块
管理所有结构化数据的存储和查询
"""

from .api_interface import (
    get_child,
    save_child,
    create_session,
    get_session,
    update_session,
    save_weekly_plan,
    get_weekly_plan,
    save_observation,
    get_session_history,
)

from .config import SQLiteConfig

__all__ = [
    'get_child',
    'save_child',
    'create_session',
    'get_session',
    'update_session',
    'save_weekly_plan',
    'get_weekly_plan',
    'save_observation',
    'get_session_history',
    'SQLiteConfig',
]

__version__ = '1.0.0'
