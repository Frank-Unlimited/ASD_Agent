"""
SQLite 数据库工具
提供数据库增删改查的 Function Call 工具
"""
from typing import Dict, Any, List
from src.container import container


# ============ 工具定义（OpenAI Function Calling Schema）============

SQLITE_TOOLS = {
    "get_child_profile": {
        "type": "function",
        "function": {
            "name": "get_child_profile",
            "description": "获取孩子的档案信息，包括基本信息、诊断、兴趣等",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的唯一标识ID"
                    }
                },
                "required": ["child_id"]
            }
        }
    },
    
    "save_child_profile": {
        "type": "function",
        "function": {
            "name": "save_child_profile",
            "description": "保存或更新孩子的档案信息。必须提供完整的 profile 对象，包含 child_id 和 name 字段。",
            "parameters": {
                "type": "object",
                "properties": {
                    "profile": {
                        "type": "object",
                        "description": "孩子的完整档案信息对象",
                        "properties": {
                            "child_id": {
                                "type": "string",
                                "description": "孩子的唯一标识ID，必填"
                            },
                            "name": {
                                "type": "string",
                                "description": "孩子的姓名，必填"
                            },
                            "age": {
                                "type": "number",
                                "description": "孩子的年龄（岁）"
                            },
                            "gender": {
                                "type": "string",
                                "description": "性别"
                            },
                            "diagnosis": {
                                "type": "string",
                                "description": "诊断信息，如：ASD轻度、ASD中度"
                            },
                            "interests": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "孩子的兴趣爱好列表"
                            }
                        },
                        "required": ["child_id", "name"]
                    }
                },
                "required": ["profile"]
            }
        }
    },
    
    "create_session": {
        "type": "function",
        "function": {
            "name": "create_session",
            "description": "创建一个新的干预会话记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    },
                    "game_id": {
                        "type": "string",
                        "description": "游戏的ID"
                    }
                },
                "required": ["child_id", "game_id"]
            }
        }
    },
    
    "update_session": {
        "type": "function",
        "function": {
            "name": "update_session",
            "description": "更新会话信息，如状态、观察记录等",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "会话ID"
                    },
                    "data": {
                        "type": "object",
                        "description": "要更新的数据"
                    }
                },
                "required": ["session_id", "data"]
            }
        }
    },
    
    "get_session_history": {
        "type": "function",
        "function": {
            "name": "get_session_history",
            "description": "获取孩子的历史会话记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "孩子的ID"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "返回的记录数量限制",
                        "default": 10
                    }
                },
                "required": ["child_id"]
            }
        }
    },
    
    "delete_child": {
        "type": "function",
        "function": {
            "name": "delete_child",
            "description": "删除孩子的档案及相关数据（谨慎使用）",
            "parameters": {
                "type": "object",
                "properties": {
                    "child_id": {
                        "type": "string",
                        "description": "要删除的孩子ID"
                    }
                },
                "required": ["child_id"]
            }
        }
    }
}


# ============ 工具执行器 ============

async def execute_get_child_profile(child_id: str) -> Dict[str, Any]:
    """执行：获取孩子档案"""
    service = container.get('sqlite')
    return await service.get_child(child_id)


async def execute_save_child_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """执行：保存孩子档案"""
    # 验证必需字段
    if 'child_id' not in profile:
        return {
            "success": False,
            "error": "缺少必需字段 'child_id'。请提供完整的 profile 对象，例如：{\"child_id\": \"xxx\", \"name\": \"xxx\"}"
        }
    if 'name' not in profile:
        return {
            "success": False,
            "error": "缺少必需字段 'name'。请提供完整的 profile 对象，例如：{\"child_id\": \"xxx\", \"name\": \"xxx\"}"
        }
    
    try:
        service = container.get('sqlite')
        await service.save_child(profile)
        return {
            "success": True,
            "message": f"成功保存孩子 {profile['name']} 的档案",
            "child_id": profile['child_id']
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"保存失败: {str(e)}"
        }


async def execute_create_session(child_id: str, game_id: str) -> Dict[str, Any]:
    """执行：创建会话"""
    service = container.get('sqlite')
    session_id = await service.create_session(child_id, game_id)
    return {"success": True, "session_id": session_id}


async def execute_update_session(session_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """执行：更新会话"""
    service = container.get('sqlite')
    await service.update_session(session_id, data)
    return {"success": True, "message": "会话更新成功"}


async def execute_get_session_history(child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """执行：获取会话历史"""
    service = container.get('sqlite')
    return await service.get_session_history(child_id, limit)


async def execute_delete_child(child_id: str) -> Dict[str, Any]:
    """执行：删除孩子档案"""
    service = container.get('sqlite')
    await service.delete_child(child_id)
    return {"success": True, "message": f"已删除孩子 {child_id} 的档案"}


# ============ 工具注册 ============

SQLITE_EXECUTORS = {
    "get_child_profile": execute_get_child_profile,
    "save_child_profile": execute_save_child_profile,
    "create_session": execute_create_session,
    "update_session": execute_update_session,
    "get_session_history": execute_get_session_history,
    "delete_child": execute_delete_child,
}


def get_sqlite_tools() -> Dict[str, Any]:
    """获取 SQLite 工具定义和执行器"""
    return {
        "schemas": list(SQLITE_TOOLS.values()),
        "executors": SQLITE_EXECUTORS
    }
