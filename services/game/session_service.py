"""
游戏会话服务
管理会话生命周期、记录观察并触发总结
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.models.game import (
    GameSession, 
    GameStatus, 
    ParentObservation, 
    SessionStartRequest,
    SessionObservationRequest,
    SessionEndRequest
)

class GameSessionService:
    def __init__(self, sqlite_service: Any, game_summarizer: Any):
        self.sqlite = sqlite_service
        self.summarizer = game_summarizer

    async def start_session(self, request: SessionStartRequest) -> str:
        """
        开始一个新的游戏会话
        """
        session_id = self.sqlite.create_game_session(
            child_id=request.child_id,
            game_id=request.game_id
        )
        return session_id

    async def add_observation(self, request: SessionObservationRequest) -> bool:
        """
        添加家长观察记录 (表情或语音)
        """
        session = self.sqlite.get_game_session(request.session_id)
        if not session:
            return False
        
        # 将 Dict 转换为列表（如果还不是的话）
        observations = session.get('parent_observations', [])
        if not isinstance(observations, list):
            observations = []
            
        new_obs = ParentObservation(
            timestamp=datetime.now(),
            content=request.content,
            child_behavior=request.child_behavior,
            parent_feeling=request.parent_feeling
        )
        
        observations.append(new_obs.dict())
        
        self.sqlite.update_game_session(request.session_id, {
            'parent_observations': observations
        })
        return True

    async def end_session(self, request: SessionEndRequest) -> bool:
        """
        结束会话并触发后续分析（可选）
        """
        session = self.sqlite.get_game_session(request.session_id)
        if not session:
            return False
            
        start_time = datetime.fromisoformat(session['start_time'])
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds() / 60)
        
        updates = {
            'end_time': end_time.isoformat(),
            'actual_duration': duration,
            'status': GameStatus.COMPLETED,
            'child_engagement_score': request.child_engagement_score,
            'goal_achievement_score': request.goal_achievement_score,
            'parent_satisfaction_score': request.parent_satisfaction_score,
            'notes': request.notes
        }
        
        if request.video_path:
            updates['video_path'] = request.video_path
            updates['has_video'] = True
            
        self.sqlite.update_game_session(request.session_id, updates)
        
        # 自动触发游戏总结
        # Note: 实际项目中可能通过任务队列异步处理，这里我们直接调用
        try:
            from src.models.game import GameSummaryRequest
            await self.summarizer.summarize_session(GameSummaryRequest(session_id=request.session_id))
        except Exception as e:
            print(f"[GameSessionService] ⚠️ 自动生成总结失败: {e}")
            # 即使总结失败，会话也算结束了
            
        return True
