"""
游戏总结服务
"""
from datetime import datetime
from typing import Optional, Any

from src.models.game import (
    GameSession,
    GamePlan,
    GameSessionSummary,
    GameSummaryRequest,
    GameSummaryResponse,
    GameStatus
)
from src.models.profile import ChildProfile
from services.LLM_Service import get_llm_service
from .prompts import build_game_summary_prompt
from .schema_builder import pydantic_to_json_schema


class GameSummarizer:
    """游戏总结服务"""
    
    def __init__(
        self,
        profile_service: Any,
        # memory_service: Any,  # TODO: MemoryService 还未实现
        sqlite_service: Any,
        # graphiti_service: Any  # TODO: Graphiti 保存记忆
    ):
        """
        初始化游戏总结服务
        
        Args:
            profile_service: 档案服务
            sqlite_service: SQLite 服务
        """
        self.profile_service = profile_service
        # self.memory_service = memory_service  # TODO
        self.sqlite = sqlite_service
        # self.graphiti = graphiti_service  # TODO
        self.llm = get_llm_service()
    
    async def summarize_session(
        self,
        request: GameSummaryRequest
    ) -> GameSummaryResponse:
        """
        生成游戏会话总结
        
        流程：
        1. 获取 GameSession（验证状态）
        2. 获取 GamePlan
        3. 获取孩子档案
        4. 获取历史上下文（TODO: MemoryService）
        5. 构建 System Prompt
        6. 调用 LLM（带 Output Schema）
        7. 更新 GameSession
        8. 保存到 SQLite
        9. 保存到 Graphiti（TODO）
        10. 返回结果
        
        Args:
            request: 游戏总结请求
            
        Returns:
            GameSummaryResponse: 总结结果
        """
        print(f"\n[GameSummarizer] 开始生成游戏总结: session_id={request.session_id}")
        
        # 1. 获取 GameSession
        session = await self._get_session(request.session_id)
        if not session:
            raise ValueError(f"游戏会话不存在: {request.session_id}")
        
        if session.status != GameStatus.COMPLETED:
            raise ValueError(f"游戏会话未完成，无法生成总结。当前状态: {session.status}")
        
        print(f"[GameSummarizer] 获取会话成功: {session.session_id}")
        
        # 2. 获取 GamePlan
        game_plan = await self._get_game_plan(session.game_id)
        if not game_plan:
            raise ValueError(f"游戏方案不存在: {session.game_id}")
        
        print(f"[GameSummarizer] 获取游戏方案: {game_plan.title}")
        
        # 3. 获取孩子档案
        profile = await self.profile_service.get_profile(session.child_id)
        if not profile:
            raise ValueError(f"孩子档案不存在: {session.child_id}")
        
        print(f"[GameSummarizer] 获取档案成功: {profile.name}")
        
        # 4. 获取历史上下文
        # TODO: 从 MemoryService 获取
        recent_assessments = None  # await self.memory_service.get_recent_assessments(session.child_id)
        recent_games = None  # await self.memory_service.get_recent_games_summary(session.child_id)
        
        # 5. 构建 System Prompt
        system_prompt = build_game_summary_prompt(
            child_profile=profile,
            game_plan=game_plan,
            session=session,
            recent_assessments=recent_assessments,
            recent_games=recent_games
        )
        
        print(f"[GameSummarizer] System Prompt 构建完成，长度: {len(system_prompt)}")
        
        # 6. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=GameSessionSummary,
            schema_name="GameSessionSummary",
            description="游戏会话总结报告"
        )
        
        print(f"[GameSummarizer] Output Schema 构建完成")
        
        # 7. 构建用户消息
        user_message = "请基于以上信息，生成完整的游戏会话总结报告。"
        
        # 8. 调用 LLM
        print(f"[GameSummarizer] 开始调用 LLM...")
        
        result = await self.llm.call(
            system_prompt=system_prompt,
            user_message=user_message,
            output_schema=output_schema,
            temperature=0.3,  # 较低温度，保证客观性
            max_tokens=3000
        )
        
        print(f"[GameSummarizer] LLM 调用完成")
        
        # 9. 解析结果
        if not result.get("structured_output"):
            raise ValueError("LLM 未返回结构化输出")
        
        summary_data = result["structured_output"]
        summary = GameSessionSummary(**summary_data)
        
        print(f"[GameSummarizer] 总结生成成功，成功程度: {summary.success_level}")
        
        # 10. 更新 GameSession
        session.session_summary = summary.overall_assessment
        session.updated_at = datetime.now()
        
        # 11. 保存到 SQLite
        await self._save_session(session)
        
        # 12. 保存到 Graphiti
        # TODO: 将总结保存到 Graphiti 记忆系统
        # await self._save_summary_to_graphiti(session, summary)
        
        # 13. 构建响应
        response = GameSummaryResponse(
            session_id=session.session_id,
            game_id=session.game_id,
            child_id=session.child_id,
            summary=summary,
            message="游戏总结生成成功"
        )
        
        print(f"[GameSummarizer] 总结完成: {request.session_id}")
        
        return response
    
    async def _get_session(self, session_id: str) -> Optional[GameSession]:
        """获取游戏会话"""
        # TODO: 根据 SQLite 服务的实际接口调整
        try:
            data = await self.sqlite.get_game_session(session_id)
            if not data:
                return None
            return GameSession(**data)
        except Exception as e:
            print(f"[GameSummarizer] 获取会话失败: {e}")
            return None
    
    async def _get_game_plan(self, game_id: str) -> Optional[GamePlan]:
        """获取游戏方案"""
        # TODO: 根据 SQLite 服务的实际接口调整
        try:
            data = await self.sqlite.get_game_plan(game_id)
            if not data:
                return None
            return GamePlan(**data["data"])
        except Exception as e:
            print(f"[GameSummarizer] 获取游戏方案失败: {e}")
            return None
    
    async def _save_session(self, session: GameSession) -> None:
        """保存游戏会话"""
        # TODO: 根据 SQLite 服务的实际接口调整
        try:
            await self.sqlite.save_game_session({
                "session_id": session.session_id,
                "data": session.dict()
            })
            print(f"[GameSummarizer] 会话已更新到数据库: {session.session_id}")
        except Exception as e:
            print(f"[GameSummarizer] 保存会话失败: {e}")
    
    # TODO: Graphiti 相关功能
    # async def _save_summary_to_graphiti(
    #     self,
    #     session: GameSession,
    #     summary: GameSessionSummary
    # ) -> None:
    #     """
    #     将总结保存到 Graphiti 记忆系统
    #     
    #     拆分为多条记忆：
    #     1. 整体评价
    #     2. 各维度进展（每个维度一条）
    #     3. 亮点时刻（每个亮点一条）
    #     4. 改进建议
    #     """
    #     memories = []
    #     
    #     # 1. 整体评价
    #     memories.append({
    #         "content": f"游戏总结：{summary.overall_assessment}",
    #         "type": "game_summary",
    #         "timestamp": session.end_time.isoformat(),
    #         "metadata": {
    #             "session_id": session.session_id,
    #             "game_id": session.game_id,
    #             "success_level": summary.success_level
    #         }
    #     })
    #     
    #     # 2. 各维度进展
    #     for dim_progress in summary.dimension_progress:
    #         memories.append({
    #             "content": f"{dim_progress.dimension_name}维度表现：{dim_progress.progress_description}",
    #             "type": "dimension_progress",
    #             "timestamp": session.end_time.isoformat(),
    #             "metadata": {
    #                 "dimension": dim_progress.dimension.value,
    #                 "score": dim_progress.performance_score
    #             }
    #         })
    #     
    #     # 3. 亮点时刻
    #     for highlight in summary.highlights:
    #         memories.append({
    #             "content": f"亮点时刻：{highlight}",
    #             "type": "highlight",
    #             "timestamp": session.end_time.isoformat()
    #         })
    #     
    #     # 保存到 Graphiti
    #     await self.graphiti.save_memories(
    #         child_id=session.child_id,
    #         memories=memories
    #     )
    #     
    #     print(f"[GameSummarizer] 已保存{len(memories)}条记忆到Graphiti")


__all__ = ['GameSummarizer']
