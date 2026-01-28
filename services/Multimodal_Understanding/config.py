"""配置模块"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class MultimodalConfig:
    """多模态解析配置类"""
    
    api_key: Optional[str] = None
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    model: str = "qwen3-vl-plus"
    enable_thinking: bool = False
    thinking_budget: int = 81920
    stream: bool = True
    timeout: int = 60
    
    def __post_init__(self):
        """初始化后处理"""
        if self.api_key is None:
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
            if not self.api_key:
                raise ValueError("API key not found. Set DASHSCOPE_API_KEY environment variable.")
    
    @classmethod
    def from_env(cls) -> 'MultimodalConfig':
        """从环境变量创建配置"""
        return cls(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL", cls.base_url),
            model=os.getenv("DASHSCOPE_MODEL", cls.model)
        )
