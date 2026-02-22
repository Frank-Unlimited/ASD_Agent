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
    use_mock: bool = False
    
    def __post_init__(self):
        """初始化后处理"""
        if self.api_key is None:
            self.api_key = os.getenv("DASHSCOPE_API_KEY")
            
        # 如果不是真实模式，或者 KEY 是占位符，自动进入 Mock 模式
        if os.getenv("USE_REAL_MULTIMODAL", "false").lower() != "true":
            self.use_mock = True
        elif not self.api_key or "your-dashscope-api-key" in self.api_key:
            self.use_mock = True
            
        if not self.use_mock and not self.api_key:
            raise ValueError("API key not found. Set DASHSCOPE_API_KEY environment variable or USE_REAL_MULTIMODAL=false.")
    
    @classmethod
    def from_env(cls) -> 'MultimodalConfig':
        """从环境变量创建配置"""
        use_real = os.getenv("USE_REAL_MULTIMODAL", "false").lower() == "true"
        return cls(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url=os.getenv("DASHSCOPE_BASE_URL", cls.base_url),
            model=os.getenv("DASHSCOPE_MODEL", cls.model),
            use_mock=not use_real
        )
