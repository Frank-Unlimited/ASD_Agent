"""
LLM Function Call 工具集
为 LLM 提供可调用的工具函数
"""
from .sqlite_tools import get_sqlite_tools, SQLITE_TOOLS, SQLITE_EXECUTORS
from .graphiti_tools import get_graphiti_tools, GRAPHITI_TOOLS, GRAPHITI_EXECUTORS
from .video_tools import get_video_tools, VIDEO_TOOLS, VIDEO_EXECUTORS
from .rag_tools import get_rag_tools, RAG_TOOLS, RAG_EXECUTORS
from .executor import ToolExecutor, get_tool_executor
from .interface import (
    ToolsInterface,
    get_tools_interface,
    get_tools_for_llm,
    execute_function_call,
    execute_tool_calls,
    execute_tool_calls_from_message
)

__all__ = [
    # 工具模块
    'get_sqlite_tools',
    'get_graphiti_tools',
    'get_video_tools',
    'get_rag_tools',
    'get_all_tools',
    
    # 执行器
    'ToolExecutor',
    'get_tool_executor',
    
    # 对外接口（推荐使用）
    'ToolsInterface',
    'get_tools_interface',
    'get_tools_for_llm',
    'execute_function_call',
    'execute_tool_calls',
    'execute_tool_calls_from_message',
]


def get_all_tools():
    """获取所有工具的 schemas 和 executors"""
    sqlite = get_sqlite_tools()
    graphiti = get_graphiti_tools()
    video = get_video_tools()
    rag = get_rag_tools()
    
    # 合并所有 schemas
    all_schemas = (
        sqlite['schemas'] + 
        graphiti['schemas'] + 
        video['schemas'] + 
        rag['schemas']
    )
    
    # 合并所有 executors
    all_executors = {
        **sqlite['executors'],
        **graphiti['executors'],
        **video['executors'],
        **rag['executors'],
    }
    
    return {
        'schemas': all_schemas,
        'executors': all_executors
    }

