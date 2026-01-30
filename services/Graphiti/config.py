"""
Graphiti 配置管理
"""
import os
from typing import Optional
from pydantic import BaseModel


class GraphitiConfig(BaseModel):
    """Graphiti 配置"""
    
    # Neo4j 连接配置
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # 查询配置
    default_limit: int = 100  # 默认查询限制
    max_limit: int = 1000     # 最大查询限制
    
    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 缓存过期时间（秒）
    
    class Config:
        env_prefix = "GRAPHITI_"
