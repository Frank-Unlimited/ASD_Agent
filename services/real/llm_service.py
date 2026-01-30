"""
LLM 服务 - 兼容性导入
此文件保留用于向后兼容，实际实现已移至 services/LLM_Service/
"""
from services.LLM_Service import (
    LLMService,
    get_llm_service,
    reset_llm_service,
    Tool,
    ToolRegistry,
    get_rag_tools
)

__all__ = [
    'LLMService',
    'get_llm_service',
    'reset_llm_service',
    'Tool',
    'ToolRegistry',
    'get_rag_tools'
]
