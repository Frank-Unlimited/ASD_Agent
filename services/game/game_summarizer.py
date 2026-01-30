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
        sqlite_service: Any,
        memory_service: Any
    ):
        """
        初始化游戏总结服务
        
        Args:
            sqlite_service: SQLite 服务（获取档案和会话）
            memory_service: Memory 服务
        """
        self.sqlite = sqlite_service
        self.memory_service = memory_service
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
        
        # 3. 获取孩子档案（从 SQLite）
        profile = self.sqlite.get_child(session.child_id)
        if not profile:
            raise ValueError(f"孩子档案不存在: {session.child_id}")
        
        print(f"[GameSummarizer] 获取档案成功: {profile.name}")
        
        # 4. 获取历史上下文
        recent_assessments = await self.memory_service.get_latest_assessment(
            child_id=session.child_id,
            assessment_type="comprehensive"
        )
        recent_games = await self.memory_service.get_recent_games(
            child_id=session.child_id,
            limit=5
        )
        
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
        
        # 12. 保存到 Memory（Graphiti）
        await self._save_summary_to_memory(session, summary)
        
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
        try:
            data = self.sqlite.get_game_session(session_id)
            if not data:
                return None
            return GameSession(**data)
        except Exception as e:
            print(f"[GameSummarizer] 获取会话失败: {e}")
            return None
    
    async def _get_game_plan(self, game_id: str) -> Optional[GamePlan]:
        """获取游戏方案"""
        try:
            data = self.sqlite.get_game_plan(game_id)
            if not data:
                return None
            return GamePlan(**data)
        except Exception as e:
            print(f"[GameSummarizer] 获取游戏方案失败: {e}")
            return None
    
    async def _save_session(self, session: GameSession) -> None:
        """保存游戏会话"""
        try:
            self.sqlite.update_game_session(session.session_id, session.dict())
            print(f"[GameSummarizer] 会话已更新到数据库: {session.session_id}")
        except Exception as e:
            print(f"[GameSummarizer] 保存会话失败: {e}")
    
    async def _save_summary_to_memory(
        self,
        session: GameSession,
        summary: GameSessionSummary
    ) -> None:
        """
        将总结保存到 Memory（Graphiti）记忆系统
        
        使用 Memory 服务的 summarize_game() 方法
        """
        try:
            # 准备视频分析数据
            video_analysis = {
                "duration": f"{session.actual_duration}分钟" if session.actual_duration else "未知",
                "key_moments": []
            }
            
            # 从 summary 中提取关键时刻
            if summary.highlights:
                for i, highlight in enumerate(summary.highlights):
                    video_analysis["key_moments"].append({
                        "time": f"{i*5:02d}:00",  # 假设每5分钟一个亮点
                        "description": highlight
                    })
            
            # 准备家长反馈数据
            parent_feedback = {
                "notes": session.parent_notes if hasattr(session, 'parent_notes') else "",
                "engagement_level": summary.engagement_score if hasattr(summary, 'engagement_score') else 0
            }
            
            # 调用 Memory 服务的 summarize_game()
            await self.memory_service.summarize_game(
                game_id=session.game_id,
                video_analysis=video_analysis,
                parent_feedback=parent_feedback
            )
            
            print(f"[GameSummarizer] 游戏总结已保存到 Memory: {session.game_id}")
            
        except Exception as e:
            print(f"[GameSummarizer] 保存游戏总结到 Memory 失败: {e}")
            # 不抛出异常，允许总结继续


__all__ = ['GameSummarizer']
