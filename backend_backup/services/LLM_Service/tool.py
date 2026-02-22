"""
工具定义类
将工具定义和执行函数绑定在一起
"""
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass
import asyncio
import inspect


@dataclass
class Tool:
    """
    工具类 - 绑定定义和执行
    
    Attributes:
        name: 工具名称
        description: 工具描述
        parameters: 参数定义（JSON Schema）
        function: 执行函数（同步或异步）
    """
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Callable
    
    def to_openai_format(self) -> Dict[str, Any]:
        """转换为 OpenAI Function Calling 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    async def execute(self, **kwargs) -> Any:
        """
        执行工具
        
        Args:
            **kwargs: 工具参数
            
        Returns:
            执行结果
        """
        try:
            # 判断是否是异步函数
            if asyncio.iscoroutinefunction(self.function):
                result = await self.function(**kwargs)
            else:
                result = self.function(**kwargs)
            
            return result
            
        except Exception as e:
            raise Exception(f"工具 '{self.name}' 执行失败: {str(e)}")


class ToolRegistry:
    """工具注册中心"""
    
    def __init__(self):
        """初始化注册中心"""
        self.tools: Dict[str, Tool] = {}
    
    def register(self, tool: Tool) -> None:
        """
        注册工具
        
        Args:
            tool: Tool 对象
        """
        self.tools[tool.name] = tool
        print(f"[Tool Registry] 注册工具: {tool.name}")
    
    def register_batch(self, tools: list[Tool]) -> None:
        """
        批量注册工具
        
        Args:
            tools: Tool 对象列表
        """
        for tool in tools:
            self.register(tool)
    
    def get(self, name: str) -> Optional[Tool]:
        """
        获取工具
        
        Args:
            name: 工具名称
            
        Returns:
            Tool 对象或 None
        """
        return self.tools.get(name)
    
    def get_all(self) -> list[Tool]:
        """获取所有工具"""
        return list(self.tools.values())
    
    def get_definitions(self) -> list[Dict[str, Any]]:
        """获取所有工具定义（OpenAI 格式）"""
        return [tool.to_openai_format() for tool in self.tools.values()]
    
    async def execute(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            执行结果
        """
        tool = self.get(name)
        if not tool:
            raise ValueError(f"工具 '{name}' 未注册")
        
        return await tool.execute(**arguments)


__all__ = ['Tool', 'ToolRegistry']
