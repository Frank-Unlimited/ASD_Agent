"""
游戏会话管理服务
负责管理游戏的实施过程

依赖的基础服务：
- SQLite: 存储游戏会话数据
- Graphiti: 保存游戏实施记录到知识图谱
- Multimodal_Understanding: 分析视频（可选）
"""
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from src.models.game import (
    GameSession,
    GameStatus,
    ParentObservation,
    VideoAnalysisSummary,
    SessionStartRequest,
    SessionObservationRequest,
    SessionEndRequest,
    SessionResponse,
)

# 导入基础服务API
from services.Graphiti.api_interface import save_memories


class GameSessionService:
    """游戏会话管理服务"""

    def __init__(
        self,
        sqlite_service: Any,  # SQLite服务
    ):
        """
        初始化游戏会话管理服务

        Args:
            sqlite_service: SQLite数据库服务
        """
        self.sqlite = sqlite_service

    async def start_session(
        self,
        request: SessionStartRequest
    ) -> SessionResponse:
        """
        开始游戏会话

        流程：
        1. 创建会话记录
        2. 更新游戏状态为IN_PROGRESS
        3. 保存到SQLite
        4. 返回session_id

        Args:
            request: 开始会话请求

        Returns:
            SessionResponse: 会话响应
        """
        print(f"\n[GameSession] 开始游戏会话: game_id={request.game_id}")

        # 1. 生成session_id
        session_id = f"session-{uuid.uuid4().hex[:12]}"

        # 2. 创建会话记录
        session = GameSession(
            session_id=session_id,
            game_id=request.game_id,
            child_id=request.child_id,
            start_time=datetime.now(),
            parent_observations=[],
            has_video=False,
            status=GameStatus.IN_PROGRESS
        )

        # 3. 保存到SQLite
        await self.sqlite.create_session(
            child_id=request.child_id,
            game_id=request.game_id
        )

        # 更新游戏状态
        # TODO: 需要实现update_game_status方法
        # await self.sqlite.update_game_status(request.game_id, GameStatus.IN_PROGRESS)

        print(f"[GameSession] 会话已创建: {session_id}")

        return SessionResponse(
            session_id=session_id,
            game_id=request.game_id,
            child_id=request.child_id,
            status=GameStatus.IN_PROGRESS,
            start_time=session.start_time,
            end_time=None,
            message="游戏会话已开始"
        )

    async def add_observation(
        self,
        session_id: str,
        request: SessionObservationRequest
    ) -> Dict[str, Any]:
        """
        添加会话观察记录

        Args:
            session_id: 会话ID
            request: 观察请求

        Returns:
            响应
        """
        print(f"\n[GameSession] 添加观察到会话 {session_id}")

        # 获取现有会话
        session_data = await self.sqlite.get_session(session_id)
        if not session_data:
            raise ValueError(f"会话不存在: {session_id}")

        # 创建观察记录
        observation = ParentObservation(
            timestamp=datetime.now(),
            content=request.content,
            child_behavior=request.child_behavior,
            parent_feeling=request.parent_feeling
        )

        # 更新会话（这里简化处理，实际需要更新会话的observations列表）
        # TODO: 实现更新会话的observations列表
        print(f"[GameSession] 观察已添加")

        return {
            "message": "观察记录已添加",
            "observation": observation.dict()
        }

    async def end_session(
        self,
        request: SessionEndRequest
    ) -> SessionResponse:
        """
        结束游戏会话

        流程：
        1. 更新会话状态为COMPLETED
        2. 记录结束时间和评分
        3. 如果有视频，进行AI分析
        4. 保存到SQLite
        5. 保存到Graphiti知识图谱
        6. 返回会话总结

        Args:
            request: 结束会话请求

        Returns:
            SessionResponse: 会话响应
        """
        print(f"\n[GameSession] 结束游戏会话: {request.session_id}")

        # 1. 获取会话数据
        session_data = await self.sqlite.get_session(request.session_id)
        if not session_data:
            raise ValueError(f"会话不存在: {request.session_id}")

        # 2. 更新会话信息
        end_time = datetime.now()
        # TODO: 从session_data中获取start_time计算实际时长
        actual_duration = 15  # 简化处理

        # 3. 处理视频分析（如果有）
        video_analysis = None
        if request.video_path:
            try:
                video_analysis = await self._analyze_video(request.video_path)
            except Exception as e:
                print(f"[GameSession] 视频分析失败: {e}")

        # 4. 更新会话状态
        await self.sqlite.update_session(request.session_id, {
            "status": GameStatus.COMPLETED.value,
            "endTime": end_time.isoformat(),
            "actualDuration": actual_duration,
            "child_engagement_score": request.child_engagement_score,
            "goal_achievement_score": request.goal_achievement_score,
            "parent_satisfaction_score": request.parent_satisfaction_score,
            "notes": request.notes,
            "has_video": request.video_path is not None,
            "video_analysis": video_analysis.dict() if video_analysis else None
        })

        # 5. 保存到Graphiti
        await self._save_session_to_graphiti(
            session_id=request.session_id,
            session_data=session_data,
            video_analysis=video_analysis
        )

        print(f"[GameSession] 会话已结束: {request.session_id}")

        return SessionResponse(
            session_id=request.session_id,
            game_id=session_data.get("gameId"),
            child_id=session_data.get("childId"),
            status=GameStatus.COMPLETED,
            start_time=datetime.fromisoformat(session_data.get("startTime")),
            end_time=end_time,
            message="游戏会话已结束，记录已保存"
        )

    # ============ 私有方法 ============

    async def _analyze_video(
        self,
        video_path: str
    ) -> VideoAnalysisSummary:
        """
        使用Multimodal_Understanding分析视频

        Args:
            video_path: 视频文件路径

        Returns:
            VideoAnalysisSummary: 视频分析摘要
        """
        from services.Multimodal_Understanding.api_interface import parse_video
        from services.Multimodal_Understanding.utils import encode_local_video

        # 编码视频
        video_url = encode_local_video(video_path)

        # 分析视频
        prompt = """
请分析这段ASD儿童干预游戏的视频，提取：
1. 孩子的行为表现
2. 情绪状态
3. 关键时刻（突破性进展、良好互动等）
4. AI洞察和建议

请详细描述观察到的内容。
"""

        analysis_text = parse_video(video_url, prompt)

        # 简化处理：创建分析摘要
        return VideoAnalysisSummary(
            video_path=video_path,
            duration_seconds=300,  # 简化处理
            key_moments=[],
            behavior_analysis=analysis_text,
            emotional_analysis="从视频中分析出的情绪",
            ai_insights=["AI洞察1", "AI洞察2"]
        )

    async def _save_session_to_graphiti(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        video_analysis: Optional[VideoAnalysisSummary] = None
    ) -> None:
        """
        将游戏会话保存到Graphiti知识图谱

        Args:
            session_id: 会话ID
            session_data: 会话数据
            video_analysis: 视频分析结果（可选）
        """
        child_id = session_data.get("childId")
        game_id = session_data.get("gameId")

        memories = []

        # 1. 主要会话记录
        memories.append({
            "content": f"完成了游戏 {game_id}，持续{session_data.get('actualDuration', 0)}分钟",
            "type": "game_session",
            "timestamp": session_data.get("endTime", datetime.now().isoformat()),
            "metadata": {
                "source": "game_session",
                "session_id": session_id,
                "game_id": game_id,
                "engagement_score": session_data.get("child_engagement_score"),
                "achievement_score": session_data.get("goal_achievement_score"),
            }
        })

        # 2. 如果有高分，记录为进展
        if session_data.get("child_engagement_score", 0) >= 8:
            memories.append({
                "content": f"在游戏中表现出很高的参与度（{session_data.get('child_engagement_score')}/10）",
                "type": "improvement",
                "timestamp": session_data.get("endTime", datetime.now().isoformat()),
                "metadata": {
                    "source": "game_session",
                    "session_id": session_id,
                }
            })

        # 3. 视频分析结果
        if video_analysis:
            memories.append({
                "content": f"视频分析：{video_analysis.behavior_analysis}",
                "type": "observation",
                "timestamp": session_data.get("endTime", datetime.now().isoformat()),
                "metadata": {
                    "source": "video_analysis",
                    "session_id": session_id,
                }
            })

        # 保存到Graphiti
        if memories:
            await save_memories(
                child_id=child_id,
                memories=memories
            )
            print(f"[GameSession] 已保存{len(memories)}条游戏记录到Graphiti")
