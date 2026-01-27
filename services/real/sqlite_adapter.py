"""
SQLite 真实服务适配器
"""
import sys
import os

# 添加 SQLite 模块路径
sqlite_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'SQLite'))
if sqlite_path not in sys.path:
    sys.path.insert(0, sqlite_path)

try:
    from adapters import SQLiteServiceAdapter
finally:
    # 清理路径
    if sqlite_path in sys.path:
        sys.path.remove(sqlite_path)

__all__ = ['SQLiteServiceAdapter']
