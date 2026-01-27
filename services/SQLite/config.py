"""
配置管理模块
"""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class SQLiteConfig:
    """SQLite 配置类"""
    
    # 数据库路径
    db_path: Optional[str] = None
    
    # 连接池配置
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    
    # 是否启用 WAL 模式（Write-Ahead Logging）
    enable_wal: bool = True
    
    # 是否启用外键约束
    enable_foreign_keys: bool = True
    
    # 是否自动创建表
    auto_create_tables: bool = True
    
    def __post_init__(self):
        """初始化后处理"""
        if self.db_path is None:
            self.db_path = os.getenv("SQLITE_DB_PATH", "./data/asd_intervention.db")
        
        # 确保数据库目录存在
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'SQLiteConfig':
        """从环境变量创建配置"""
        return cls(
            db_path=os.getenv("SQLITE_DB_PATH", "./data/asd_intervention.db"),
            enable_wal=os.getenv("SQLITE_ENABLE_WAL", "true").lower() == "true",
            enable_foreign_keys=os.getenv("SQLITE_ENABLE_FK", "true").lower() == "true",
            auto_create_tables=os.getenv("SQLITE_AUTO_CREATE", "true").lower() == "true",
        )
