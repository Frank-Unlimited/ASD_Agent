"""
RAG 工具集
"""
from typing import List, Dict, Any
from services.LLM_Service.tool import Tool
from src.container import container


# ============ RAG 工具函数 ============

async def search_games(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """检索游戏知识库"""
    rag_service = container.get('rag')
    return await rag_service.search_games(query, top_k=top_k)


# ============ 工具定义 ============

def get_rag_tools() -> List[Tool]:
    """
    获取 RAG 工具集
    
    Returns:
        Tool 对象列表
    """
    return [
        Tool(
            name="search_games",
            description="检索游戏知识库，查找适合的 ASD 干预游戏。可以根据发展维度、难度、兴趣等条件搜索",
            parameters={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询，描述游戏需求、特征、目标维度或孩子兴趣"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量，默认10条",
                        "default": 10
                    }
                },
                "required": ["query"]
            },
            function=search_games
        )
    ]


__all__ = ['get_rag_tools']
