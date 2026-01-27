"""
配置管理模块
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """应用配置"""
    
    # 服务配置
    port: int = 7860
    environment: Literal["development", "production", "test"] = "development"
    
    # LLM 统一配置（所有模块使用这些配置）
    llm_api_key: str = ""
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen-plus"
    llm_small_model: str = "qwen-flash"
    llm_embedding_model: str = "text-embedding-v3"
    llm_embedding_dim: int = 1536
    
    # 阿里云服务配置（用于语音、多模态等特定服务）
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    aliyun_nls_appkey: str = ""
    aliyun_nls_token: str = ""
    dashscope_api_key: str = ""  # 用于多模态服务
    
    # 数据库配置
    sqlite_db_path: str = "./data/asd_intervention.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "asd_knowledge"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    
    # Neo4j 配置（Graphiti）
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # 服务开关（Mock/Real）
    use_real_sqlite: bool = False
    use_real_graphiti: bool = False
    use_real_rag: bool = False
    use_real_video_analysis: bool = False
    use_real_speech: bool = False
    use_real_document_parser: bool = False
    
    # 业务服务开关
    use_real_assessment: bool = False
    use_real_chat: bool = False
    
    # JWT 配置
    jwt_secret: str = "default-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 10080  # 7天
    
    # 文件上传配置
    upload_dir: str = "./uploads"
    max_file_size: int = 104857600  # 100MB
    
    # Redis 配置（可选）
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
