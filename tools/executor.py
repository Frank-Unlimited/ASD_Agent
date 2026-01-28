"""
工具执行器管理器
统一管理所有 Function Call 工具的执行
"""
import json
from typing import Dict, Any, List


class ToolExecutor:
    """工具执行器"""
    
    def __init__(self):
        """初始化工具执行器"""
        # 延迟导入，避免循环依赖
        from tools.sqlite_tools import get_sqlite_tools
        from tools.graphiti_tools import get_graphiti_tools
        from tools.video_tools import get_video_tools
        from tools.rag_tools import get_rag_tools
        
        sqlite = get_sqlite_tools()
        graphiti = get_graphiti_tools()
        video = get_video_tools()
        rag = get_rag_tools()
        
        # 合并所有 schemas
        self.schemas = (
            sqlite['schemas'] + 
            graphiti['schemas'] + 
            video['schemas'] + 
            rag['schemas']
        )
        
        # 合并所有 executors
        self.executors = {
            **sqlite['executors'],
            **graphiti['executors'],
            **video['executors'],
            **rag['executors'],
        }
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """获取所有工具的 schema 定义（用于 LLM Function Calling）"""
        return self.schemas
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
            
        Raises:
            ValueError: 工具不存在
            Exception: 工具执行失败
        """
        if tool_name not in self.executors:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        executor = self.executors[tool_name]
        
        try:
            # 执行工具
            result = await executor(**arguments)
            return result
        except Exception as e:
            raise Exception(f"工具 '{tool_name}' 执行失败: {str(e)}")
    
    async def execute_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        批量执行工具调用（处理 LLM 返回的 tool_calls）
        
        Args:
            tool_calls: LLM 返回的工具调用列表，格式：
                [
                    {
                        "id": "call_xxx",
                        "type": "function",
                        "function": {
                            "name": "get_child_profile",
                            "arguments": "{\"child_id\": \"test-001\"}"
                        }
                    }
                ]
        
        Returns:
            工具执行结果列表，格式：
                [
                    {
                        "tool_call_id": "call_xxx",
                        "role": "tool",
                        "name": "get_child_profile",
                        "content": "{...}"
                    }
                ]
        """
        results = []
        
        for tool_call in tool_calls:
            tool_call_id = tool_call.get('id')
            function = tool_call.get('function', {})
            tool_name = function.get('name')
            arguments_str = function.get('arguments', '{}')
            
            try:
                # 解析参数
                arguments = json.loads(arguments_str)
                
                # 执行工具
                result = await self.execute_tool(tool_name, arguments)
                
                # 构建响应
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps(result, ensure_ascii=False)
                })
                
            except Exception as e:
                # 错误响应
                results.append({
                    "tool_call_id": tool_call_id,
                    "role": "tool",
                    "name": tool_name,
                    "content": json.dumps({
                        "error": str(e),
                        "success": False
                    }, ensure_ascii=False)
                })
        
        return results


# 全局工具执行器实例
_executor_instance = None


def get_tool_executor() -> ToolExecutor:
    """获取工具执行器实例（单例）"""
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = ToolExecutor()
    return _executor_instance
