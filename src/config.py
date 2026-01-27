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
    
    # AI 服务配置
    ai_provider: Literal["deepseek", "openai", "gemini"] = "deepseek"
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # 通义千问配置（用于多模态解析）
    dashscope_api_key: str = ""
    
    # 阿里云服务配置
    aliyun_access_key_id: str = ""
    aliyun_access_key_secret: str = ""
    
    # 阿里云智能语音配置
    aliyun_nls_appkey: str = ""
    aliyun_nls_token: str = ""
    
    # 数据库配置
    sqlite_db_path: str = "./data/asd_intervention.db"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "asd_knowledge"
    postgres_user: str = "postgres"
    postgres_password: str = ""
    
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
