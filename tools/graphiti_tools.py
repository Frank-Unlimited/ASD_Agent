"""
Graphiti 记忆网络工具
提供记忆增删改查的 Function Call 工具
"""
from typing import Dict, Any, List
from src.container import container


# ============ 工具定义 ============

GRAPHITI_TOOLS = {
    "save_memories": {
        "type": "function",
        "function": {
            "name": "save_memories",
            "description": "保存孩子的观察记忆到知识图谱，用于记录干预过程中的重要观察",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    },
                    "memories": {
                        "type": "array",
                        "description": "记忆列表",
                        "items": {
                            "type": "object",
                            "properties": {
                                "timestamp": {
                                    "type": "string",
                                    "description": "时间戳，ISO 8601 格式"
                                },
                                "type": {
                                    "type": "string",
                                    "description": "记忆类型：observation（观察）、milestone（里程碑）、feedback（反馈）"
                                },
                                "content": {
                                    "type": "string",
                                    "description": "记忆内容描述"
                                }
                            },
                            "required": ["timestamp", "type", "content"]
                        }
                    }
                },
                "required": ["child_id", "memories"]
            }
        }
    },
    
    "get_recent_memories": {
        "type": "function",
        "function": {
            "name": "get_recent_memories",
            "description": "获取孩子最近的记忆，用于了解近期的干预情况和进展",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    },
                    "days": {
                        "type": "integer",
                        "description": "获取最近多少天的记忆",
                        "default": 7
                    }
                },
                "required": ["child_id"]
            }
        }
    },
    
    "build_context": {
        "type": "function",
        "function": {
            "name": "build_context",
            "description": "构建孩子的当前上下文，包括趋势分析、关注点、活跃目标等，用于制定干预计划",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    }
                },
                "required": ["child_id"]
            }
        }
    },
    
    "analyze_trends": {
        "type": "function",
        "function": {
            "name": "analyze_trends",
            "description": "分析孩子在某个维度的发展趋势（如眼神接触、双向沟通等）",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    },
                    "dimension": {
                        "type": "string",
                        "description": "要分析的维度，如：眼神接触、双向沟通、情绪调节等"
                    }
                },
                "required": ["child_id", "dimension"]
            }
        }
    },
    
    "detect_milestones": {
        "type": "function",
        "function": {
            "name": "detect_milestones",
            "description": "检测孩子的里程碑事件，识别重要的突破和进步",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    }
                },
                "required": ["child_id"]
            }
        }
    },
    
    "clear_memories": {
        "type": "function",
        "function": {
            "name": "clear_memories",
            "description": "清空孩子的所有记忆（谨慎使用，不可恢复）",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    }
                },
                "required": ["child_id"]
            }
        }
    }
}


# ============ 工具执行器 ============

async def execute_save_memories(child_id: str, memories: List[Dict[str, Any]]) -> Dict[str, Any]:
    """执行：保存记忆"""
    service = container.get('graphiti')
    await service.save_memories(child_id, memories)
    return {"success": True, "message": f"成功保存 {len(memories)} 条记忆"}


async def execute_get_recent_memories(child_id: str, days: int = 7) -> List[Dict[str, Any]]:
    """执行：获取最近记忆"""
    service = container.get('graphiti')
    return await service.get_recent_memories(child_id, days)


async def execute_build_context(child_id: str) -> Dict[str, Any]:
    """执行：构建上下文"""
    service = container.get('graphiti')
    return await service.build_context(child_id)


async def execute_analyze_trends(child_id: str, dimension: str) -> Dict[str, Any]:
    """执行：分析趋势"""
    service = container.get('graphiti')
    return await service.analyze_trends(child_id, dimension)


async def execute_detect_milestones(child_id: str) -> List[Dict[str, Any]]:
    """执行：检测里程碑"""
    service = container.get('graphiti')
    return await service.detect_milestones(child_id)


async def execute_clear_memories(child_id: str) -> Dict[str, Any]:
    """执行：清空记忆"""
    service = container.get('graphiti')
    await service.clear_memories(child_id)
    return {"success": True, "message": f"已清空孩子 {child_id} 的所有记忆"}


# ============ 工具注册 ============

GRAPHITI_EXECUTORS = {
    "save_memories": execute_save_memories,
    "get_recent_memories": execute_get_recent_memories,
    "build_context": execute_build_context,
    "analyze_trends": execute_analyze_trends,
    "detect_milestones": execute_detect_milestones,
    "clear_memories": execute_clear_memories,
}


def get_graphiti_tools() -> Dict[str, Any]:
    """获取 Graphiti 工具定义和执行器"""
    return {
        "schemas": list(GRAPHITI_TOOLS.values()),
        "executors": GRAPHITI_EXECUTORS
    }
