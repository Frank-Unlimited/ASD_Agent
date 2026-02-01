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
        
        新架构：
        1. Game Summarizer 生成总结文本（已完成）
        2. 调用 Memory 的 store_game_summary() 存储
        """
        try:
            # 构建总结文本（自然语言）
            summary_text = self._build_summary_text(session, summary)
            
            # 准备元数据
            metadata = {
                "session_duration": f"{session.actual_duration}分钟" if session.actual_duration else "未知",
                "engagement_score": summary.engagement_score if hasattr(summary, 'engagement_score') else 0,
                "success_level": summary.success_level,
                "parent_notes": session.parent_notes if hasattr(session, 'parent_notes') else ""
            }
            
            # 调用 Memory 服务的新接口 store_game_summary()
            result = await self.memory_service.store_game_summary(
                child_id=session.child_id,
                game_id=session.game_id,
                summary_text=summary_text,
                metadata=metadata
            )
            
            print(f"[GameSummarizer] 游戏总结已保存到 Memory: episode_id={result['episode_id']}")
            
        except Exception as e:
            print(f"[GameSummarizer] 保存游戏总结到 Memory 失败: {e}")
            import traceback
            traceback.print_exc()
            # 不抛出异常，允许总结继续
    
    def _build_summary_text(
        self,
        session: GameSession,
        summary: GameSessionSummary
    ) -> str:
        """
        构建游戏总结的自然语言文本
        
        Args:
            session: 游戏会话
            summary: 总结数据
            
        Returns:
            自然语言总结文本
        """
        text_parts = []
        
        # 基本信息
        text_parts.append(f"# 游戏会话总结")
        text_parts.append(f"\n游戏ID: {session.game_id}")
        text_parts.append(f"会话ID: {session.session_id}")
        text_parts.append(f"时长: {session.actual_duration}分钟" if session.actual_duration else "时长: 未知")
        
        # 整体评估
        text_parts.append(f"\n## 整体评估")
        text_parts.append(summary.overall_assessment)
        
        # 成功程度
        text_parts.append(f"\n## 成功程度")
        text_parts.append(f"评级: {summary.success_level}")
        
        # 参与度
        if hasattr(summary, 'engagement_score'):
            text_parts.append(f"\n## 参与度")
            text_parts.append(f"评分: {summary.engagement_score}/10")
        
        # 亮点时刻
        if summary.highlights:
            text_parts.append(f"\n## 亮点时刻")
            for i, highlight in enumerate(summary.highlights, 1):
                text_parts.append(f"{i}. {highlight}")
        
        # 挑战与困难
        if summary.challenges:
            text_parts.append(f"\n## 挑战与困难")
            for i, challenge in enumerate(summary.challenges, 1):
                text_parts.append(f"{i}. {challenge}")
        
        # 改进建议
        if summary.improvement_suggestions:
            text_parts.append(f"\n## 改进建议")
            for i, suggestion in enumerate(summary.improvement_suggestions, 1):
                text_parts.append(f"{i}. {suggestion}")
        
        # 家长反馈
        if hasattr(session, 'parent_notes') and session.parent_notes:
            text_parts.append(f"\n## 家长反馈")
            text_parts.append(session.parent_notes)
        
        return "\n".join(text_parts)


__all__ = ['GameSummarizer']
