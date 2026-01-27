"""
Graphiti 配置管理
"""
from typing import Optional
from pydantic import BaseModel


class GraphitiConfig(BaseModel):
    """Graphiti 配置"""
    
    # Neo4j 连接配置
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # LLM 配置（从环境变量读取）
    ai_provider: str = "qwen"  # deepseek, openai, gemini, qwen
    
    # 记忆检索配置
    default_memory_days: int = 7
    max_search_results: int = 50
    
    # 趋势分析配置
    trend_analysis_window: int = 30  # 天
    milestone_threshold: float = 0.7  # 里程碑显著性阈值
    
    class Config:
        env_prefix = "GRAPHITI_"
