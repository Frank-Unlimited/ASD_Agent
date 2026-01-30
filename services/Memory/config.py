"""
Memory 服务配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class MemoryConfig:
    """Memory 服务配置"""
    
    # Neo4j 配置（从 Graphiti 继承）
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7688")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # 功能开关
    enable_llm: bool = os.getenv("MEMORY_ENABLE_LLM", "true").lower() == "true"
