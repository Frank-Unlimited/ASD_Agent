"""
Tools 对外接口层
提供简洁的 API 供 LLM 调用工具
"""
import json
from typing import List, Dict, Any, Optional
from tools.executor import get_tool_executor


class ToolsInterface:
    """工具接口层"""
    
    def __init__(self):
        """初始化工具接口"""
        self.executor = get_tool_executor()
    
    def get_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        获取工具列表（用于填充 LLM Function Call）
        
        Returns:
            工具 schema 列表，可直接传给 LLM 的 tools 参数
            
        Example:
            >>> interface = ToolsInterface()
            >>> tools = interface.get_tools_for_llm()
            >>> # 传给 LLM
            >>> response = client.chat.completions.create(
            ...     model="gpt-4",
            ...     messages=[...],
            ...     tools=tools
            ... )
        """
        return self.executor.get_tool_schemas()
    
    async def execute_function_call(
        self, 
        function_name: str, 
        function_arguments: str
    ) -> Dict[str, Any]:
        """
        执行单个 Function Call
        
        Args:
            function_name: 函数名称
            function_arguments: 函数参数（JSON 字符串）
            
        Returns:
            执行结果
            
        Example:
            >>> result = await interface.execute_function_call(
            ...     function_name="get_child_profile",
            ...     function_arguments='{"child_id": "test-001"}'
            ... )
        """
        try:
            # 解析参数
            arguments = json.loads(function_arguments)
            
            # 执行工具
            result = await self.executor.execute_tool(function_name, arguments)
            
            return {
                "success": True,
                "result": result
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"参数解析失败: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_tool_calls(
        self, 
        tool_calls: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        批量执行 LLM 返回的 Tool Calls
        
        Args:
            tool_calls: LLM 返回的 tool_calls 列表，格式：
                [
                    {
                        "id": "call_xxx",
                        "type": "function",
                        "function": {
                            "name": "get_child_profile",
                            "arguments": '{"child_id": "test-001"}'
                        }
                    }
                ]
        
        Returns:
            工具执行结果列表，可直接添加到 messages 中返回给 LLM：
                [
                    {
                        "tool_call_id": "call_xxx",
                        "role": "tool",
                        "name": "get_child_profile",
                        "content": "{...}"
                    }
                ]
        
        Example:
            >>> # 1. LLM 返回 tool_calls
            >>> response = await client.chat.completions.create(...)
            >>> message = response.choices[0].message
            >>> 
            >>> # 2. 执行工具
            >>> if message.tool_calls:
            ...     results = await interface.execute_tool_calls(message.tool_calls)
            ...     
            ...     # 3. 将结果返回给 LLM
            ...     messages.append(message)
            ...     messages.extend(results)
            ...     
            ...     final_response = await client.chat.completions.create(
            ...         model="gpt-4",
            ...         messages=messages
            ...     )
        """
        return await self.executor.execute_tool_calls(tool_calls)
    
    async def execute_tool_calls_from_message(
        self, 
        message: Any
    ) -> List[Dict[str, Any]]:
        """
        从 LLM 消息对象中提取并执行 Tool Calls
        
        Args:
            message: LLM 返回的 message 对象（包含 tool_calls 属性）
            
        Returns:
            工具执行结果列表
            
        Example:
            >>> response = await client.chat.completions.create(...)
            >>> message = response.choices[0].message
            >>> 
            >>> if message.tool_calls:
            ...     results = await interface.execute_tool_calls_from_message(message)
        """
        if not hasattr(message, 'tool_calls') or not message.tool_calls:
            return []
        
        # 转换为字典格式
        tool_calls = []
        for tc in message.tool_calls:
            tool_calls.append({
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            })
        
        return await self.execute_tool_calls(tool_calls)
    
    def get_tool_info(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取工具信息
        
        Args:
            tool_name: 工具名称，如果为 None 则返回所有工具信息
            
        Returns:
            工具信息
        """
        schemas = self.executor.get_tool_schemas()
        
        if tool_name is None:
            # 返回所有工具的简要信息
            return {
                "total": len(schemas),
                "tools": [
                    {
                        "name": schema["function"]["name"],
                        "description": schema["function"]["description"]
                    }
                    for schema in schemas
                ]
            }
        else:
            # 返回指定工具的详细信息
            for schema in schemas:
                if schema["function"]["name"] == tool_name:
                    return schema["function"]
            
            return {"error": f"工具 '{tool_name}' 不存在"}


# 全局接口实例
_interface_instance = None


def get_tools_interface() -> ToolsInterface:
    """获取工具接口实例（单例）"""
    global _interface_instance
    if _interface_instance is None:
        _interface_instance = ToolsInterface()
    return _interface_instance


# ============ 便捷函数 ============

def get_tools_for_llm() -> List[Dict[str, Any]]:
    """
    便捷函数：获取工具列表
    
    Example:
        >>> from tools.interface import get_tools_for_llm
        >>> tools = get_tools_for_llm()
    """
    return get_tools_interface().get_tools_for_llm()


async def execute_function_call(
    function_name: str, 
    function_arguments: str
) -> Dict[str, Any]:
    """
    便捷函数：执行单个 Function Call
    
    Example:
        >>> from tools.interface import execute_function_call
        >>> result = await execute_function_call(
        ...     "get_child_profile",
        ...     '{"child_id": "test-001"}'
        ... )
    """
    return await get_tools_interface().execute_function_call(
        function_name, 
        function_arguments
    )


async def execute_tool_calls(tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    便捷函数：批量执行 Tool Calls
    
    Example:
        >>> from tools.interface import execute_tool_calls
        >>> results = await execute_tool_calls(message.tool_calls)
    """
    return await get_tools_interface().execute_tool_calls(tool_calls)


async def execute_tool_calls_from_message(message: Any) -> List[Dict[str, Any]]:
    """
    便捷函数：从消息对象执行 Tool Calls
    
    Example:
        >>> from tools.interface import execute_tool_calls_from_message
        >>> results = await execute_tool_calls_from_message(message)
    """
    return await get_tools_interface().execute_tool_calls_from_message(message)
