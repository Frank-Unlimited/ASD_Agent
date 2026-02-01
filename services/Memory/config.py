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
    
    # LLM 配置（用于 Graphiti-core）
    llm_api_key: str = os.getenv("LLM_API_KEY", "")
    llm_base_url: str = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    llm_model: str = os.getenv("LLM_MODEL", "qwen-plus")
    llm_small_model: str = os.getenv("LLM_SMALL_MODEL", "qwen-flash")
    llm_embedding_model: str = os.getenv("LLM_EMBEDDING_MODEL", "text-embedding-v3")
    llm_embedding_dim: int = int(os.getenv("LLM_EMBEDDING_DIM", "1536"))
    
    # 功能开关
    enable_llm: bool = os.getenv("MEMORY_ENABLE_LLM", "true").lower() == "true"
