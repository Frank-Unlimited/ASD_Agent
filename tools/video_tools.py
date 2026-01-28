"""
视频分析工具
提供多模态视频解析的 Function Call 工具
"""
from typing import Dict, Any
from src.container import container


# ============ 工具定义 ============

VIDEO_TOOLS = {
    "analyze_video": {
        "type": "function",
        "function": {
            "name": "analyze_video",
            "description": "分析干预视频，识别孩子的行为、情绪、互动模式等，生成结构化的分析报告",
            "parameters": {
                "type": "object",
                "properties": {
                    "video_path": {
                        "type": "string",
                        "description": "视频文件路径或URL"
                    },
                    "context": {
                        "type": "object",
                        "description": "上下文信息，包含 child_id, game_id 等",
                        "properties": {
                            "child_id": {"type": "string"},
                            "game_id": {"type": "string"},
                            "session_id": {"type": "string"}
                        }
                    }
                },
                "required": ["video_path", "context"]
            }
        }
    }
}


# ============ 工具执行器 ============

async def execute_analyze_video(video_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """执行：分析视频"""
    service = container.get('video_analysis')
    return await service.analyze_video(video_path, context)


# ============ 工具注册 ============

VIDEO_EXECUTORS = {
    "analyze_video": execute_analyze_video,
}


def get_video_tools() -> Dict[str, Any]:
    """获取视频分析工具定义和执行器"""
    return {
        "schemas": list(VIDEO_TOOLS.values()),
        "executors": VIDEO_EXECUTORS
    }
