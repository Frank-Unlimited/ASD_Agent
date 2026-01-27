"""
SQLite 数据管理 Mock 实现
"""
from typing import Any, Dict, List
from src.interfaces import ISQLiteService
import uuid
from datetime import datetime


class MockSQLiteService(ISQLiteService):
    """SQLite Mock 服务"""
    
    def __init__(self):
        # 内存存储
        self.children = {}
        self.sessions = {}
        self.weekly_plans = {}
        self.observations = {}
    
    def get_service_name(self) -> str:
        return "MockSQLiteService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def get_child(self, child_id: str) -> Dict[str, Any]:
        """获取孩子档案"""
        print(f"[Mock SQLite] 获取孩子档案: {child_id}")
        
        if child_id in self.children:
            return self.children[child_id]
        
        # 返回假数据
        return {
            "childId": child_id,
            "name": "辰辰",
            "age": 2.5,
            "birthDate": "2023-07-01",
            "diagnosis": "ASD轻度",
            "interests": ["旋转物体", "水流", "积木"],
            "portrait": {
                "strengths": ["视觉记忆好", "对规律敏感"],
                "weaknesses": ["眼神接触少", "语言发育迟缓"],
                "emotionalMilestones": {
                    "selfRegulation": 3,
                    "intimacy": 2,
                    "twoWayCommunication": 2,
                    "complexCommunication": 1,
                    "emotionalIdeas": 1,
                    "logicalThinking": 1
                }
            }
        }
    
    async def save_child(self, profile: Dict[str, Any]) -> None:
        """保存孩子档案"""
        child_id = profile.get("childId")
        print(f"[Mock SQLite] 保存孩子档案: {child_id}")
        self.children[child_id] = profile
    
    async def create_session(self, child_id: str, game_id: str) -> str:
        """创建干预会话"""
        session_id = f"session-{uuid.uuid4().hex[:8]}"
        print(f"[Mock SQLite] 创建会话: {session_id}")
        
        self.sessions[session_id] = {
            "sessionId": session_id,
            "childId": child_id,
            "gameId": game_id,
            "status": "pending",
            "createdAt": datetime.now().isoformat()
        }
        
        return session_id
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        print(f"[Mock SQLite] 获取会话: {session_id}")
        return self.sessions.get(session_id, {})
    
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """更新会话信息"""
        print(f"[Mock SQLite] 更新会话: {session_id}")
        if session_id in self.sessions:
            self.sessions[session_id].update(data)
    
    async def save_weekly_plan(self, plan: Dict[str, Any]) -> str:
        """保存周计划"""
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"
        print(f"[Mock SQLite] 保存周计划: {plan_id}")
        
        plan["planId"] = plan_id
        self.weekly_plans[plan_id] = plan
        
        return plan_id
    
    async def get_weekly_plan(self, plan_id: str) -> Dict[str, Any]:
        """获取周计划"""
        print(f"[Mock SQLite] 获取周计划: {plan_id}")
        return self.weekly_plans.get(plan_id, {})
    
    async def save_observation(self, observation: Dict[str, Any]) -> str:
        """保存观察记录"""
        obs_id = f"obs-{uuid.uuid4().hex[:8]}"
        print(f"[Mock SQLite] 保存观察: {obs_id}")
        
        observation["observationId"] = obs_id
        self.observations[obs_id] = observation
        
        return obs_id
    
    async def get_session_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会话历史"""
        print(f"[Mock SQLite] 获取会话历史: {child_id}, limit={limit}")
        
        # 返回假的历史数据
        return [
            {
                "sessionId": "session-001",
                "date": "2026-01-20",
                "game": "积木传递游戏",
                "summary": "孩子今天状态很好，眼神接触3次"
            },
            {
                "sessionId": "session-002",
                "date": "2026-01-22",
                "game": "球类互动游戏",
                "summary": "孩子主动微笑2次，进步明显"
            }
        ][:limit]
