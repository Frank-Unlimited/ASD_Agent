"""
RAG 知识库查询工具
提供方法论、游戏、量表、案例检索的 Function Call 工具
"""
from typing import Dict, Any, List, Optional
from src.container import container


# ============ 工具定义 ============

RAG_TOOLS = {
    "search_methodology": {
        "type": "function",
        "function": {
            "name": "search_methodology",
            "description": "检索地板时光方法论知识库，获取干预理论、技巧、原则等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询，如：地板时光核心原则、如何建立眼神接触"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    
    "search_games": {
        "type": "function",
        "function": {
            "name": "search_games",
            "description": "检索游戏知识库，根据关键词查找适合的干预游戏",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询，如：积木游戏、角色扮演"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    
    "search_games_by_dimension": {
        "type": "function",
        "function": {
            "name": "search_games_by_dimension",
            "description": "按发展维度和难度检索游戏，用于针对性干预",
            "parameters": {
                "type": "object",
                "properties": {
                    "dimension": {
                        "type": "string",
                        "description": "发展维度，如：眼神接触、双向沟通、情绪调节、社交互动"
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "难度等级：easy（简单）、medium（中等）、hard（困难）"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 10
                    }
                },
                "required": ["dimension", "difficulty"]
            }
        }
    },
    
    "search_games_by_interest": {
        "type": "function",
        "function": {
            "name": "search_games_by_interest",
            "description": "根据孩子的兴趣检索游戏，提高参与度",
            "parameters": {
                "type": "object",
                "properties": {
                    "interest": {
                        "type": "string",
                        "description": "孩子的兴趣，如：汽车、动物、音乐"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 10
                    }
                },
                "required": ["interest"]
            }
        }
    },
    
    "get_game_details": {
        "type": "function",
        "function": {
            "name": "get_game_details",
            "description": "获取游戏的详细信息，包括玩法、目标、注意事项等",
            "parameters": {
                "type": "object",
                "properties": {
                    "game_id": {
                        "type": "string",
                        "description": "游戏ID"
                    }
                },
                "required": ["game_id"]
            }
        }
    },
    
    "search_scale": {
        "type": "function",
        "function": {
            "name": "search_scale",
            "description": "检索评估量表知识库，如 CARS、ABC 等",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询，如：CARS量表、社交能力评估"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    
    "search_cases": {
        "type": "function",
        "function": {
            "name": "search_cases",
            "description": "检索成功案例知识库，学习其他家庭的干预经验",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索查询，如：眼神接触改善案例、语言发展案例"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    }
}


# ============ 工具执行器 ============

async def execute_search_methodology(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """执行：检索方法论"""
    service = container.get('rag')
    return await service.search_methodology(query, top_k)


async def execute_search_games(query: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """执行：检索游戏"""
    service = container.get('rag')
    return await service.search_games(query, filters=None, top_k=top_k)


async def execute_search_games_by_dimension(
    dimension: str, 
    difficulty: str, 
    top_k: int = 10
) -> List[Dict[str, Any]]:
    """执行：按维度检索游戏"""
    service = container.get('rag')
    return await service.search_games_by_dimension(dimension, difficulty, top_k)


async def execute_search_games_by_interest(interest: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """执行：按兴趣检索游戏"""
    service = container.get('rag')
    return await service.search_games_by_interest(interest, top_k)


async def execute_get_game_details(game_id: str) -> Dict[str, Any]:
    """执行：获取游戏详情"""
    service = container.get('rag')
    return await service.get_game(game_id)


async def execute_search_scale(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """执行：检索量表"""
    service = container.get('rag')
    return await service.search_scale(query, top_k)


async def execute_search_cases(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """执行：检索案例"""
    service = container.get('rag')
    return await service.search_cases(query, top_k)


# ============ 工具注册 ============

RAG_EXECUTORS = {
    "search_methodology": execute_search_methodology,
    "search_games": execute_search_games,
    "search_games_by_dimension": execute_search_games_by_dimension,
    "search_games_by_interest": execute_search_games_by_interest,
    "get_game_details": execute_get_game_details,
    "search_scale": execute_search_scale,
    "search_cases": execute_search_cases,
}


def get_rag_tools() -> Dict[str, Any]:
    """获取 RAG 工具定义和执行器"""
    return {
        "schemas": list(RAG_TOOLS.values()),
        "executors": RAG_EXECUTORS
    }
