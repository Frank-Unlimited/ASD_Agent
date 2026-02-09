"""
基础接口定义
所有服务接口的基类
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseService(ABC):
    """服务基类"""
    
    @abstractmethod
    def get_service_name(self) -> str:
        """获取服务名称"""
        pass
    
    @abstractmethod
    def get_service_version(self) -> str:
        """获取服务版本"""
        pass
