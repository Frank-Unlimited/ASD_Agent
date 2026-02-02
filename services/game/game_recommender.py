"""
游戏推荐服务
"""
import uuid
from datetime import datetime
from typing import Optional, Any

from src.models.game import (
    GamePlan,
    GameRecommendRequest,
    GameRecommendResponse,
    GameStatus,
    TargetDimension
)
from src.models.profile import ChildProfile
from services.LLM_Service import get_llm_service
from services.LLM_Service.tools.rag_tools import get_rag_tools
from .prompts import build_game_recommendation_prompt
from .schema_builder import pydantic_to_json_schema


class GameRecommender:
    """游戏推荐服务"""
    
    def __init__(
        self,
        sqlite_service: Any,
        memory_service: Any
    ):
        """
        初始化游戏推荐服务
        
        Args:
            sqlite_service: SQLite 服务（获取孩子档案）
            memory_service: Memory 服务（获取评估和游戏历史）
        """
        self.sqlite = sqlite_service
        self.memory_service = memory_service
        self.llm = get_llm_service()
    
    async def recommend_game(
        self,
        request: GameRecommendRequest
    ) -> GameRecommendResponse:
        """
        推荐游戏
        
        流程：
        1. 获取孩子档案
        2. 获取近期评估和游戏总结（TODO: 从 MemoryService）
        3. 构建 System Prompt
        4. 调用 LLM（带 RAG 工具 + Output Schema）
        5. 生成 GamePlan
        6. 保存到 SQLite
        7. 返回推荐结果
        
        Args:
            request: 游戏推荐请求
            
        Returns:
            GameRecommendResponse: 推荐结果
        """
        print(f"\n[GameRecommender] 开始推荐游戏: child_id={request.child_id}")
        
        # 1. 获取孩子档案（从 SQLite）
        profile = self.sqlite.get_child(request.child_id)
        if not profile:
            raise ValueError(f"孩子档案不存在: {request.child_id}")
        
        print(f"[GameRecommender] 获取档案成功: {profile.name}")
        
        # 2. 获取近期评估和游戏总结
        recent_assessments = await self.memory_service.get_latest_assessment(
            child_id=request.child_id,
            assessment_type="comprehensive"
        )
        recent_games = await self.memory_service.get_recent_games(
            child_id=request.child_id,
            limit=5
        )
        
        # 3. 构建 System Prompt
        system_prompt = build_game_recommendation_prompt(
            child_profile=profile,
            recent_assessments=recent_assessments,
            recent_games=recent_games,
            focus_dimension=request.focus_dimension.value if request.focus_dimension else None,
            duration_preference=request.duration_preference
        )
        
        print(f"[GameRecommender] System Prompt 构建完成，长度: {len(system_prompt)}")
        
        # 4. 获取游戏库
        from .library_service import GameLibraryService
        library_service = GameLibraryService()
        library_games = library_service.list_games()
        library_summary = "\n".join([f"- ID: {g['id']}, 标题: {g['title']}, 目标: {g['target_dimension'].value}" for g in library_games])

        # 5. 构建用户消息
        user_message = f"""
请根据孩子的情况，从以下游戏库中选择最合适的一个游戏。

游戏库列表：
{library_summary}

请返回所选游戏的 ID 以及推荐理由。
"""
        if request.focus_dimension:
            user_message += f"\n重点关注 {request.focus_dimension.value} 维度。"
            
        # 6. 构建 Output Schema (只需要 ID 和理由)
        selection_schema = {
            "name": "GameSelection",
            "description": "从库中选择游戏的决策",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "selected_game_id": {"type": "string", "description": "所选游戏的库 ID"},
                    "recommendation_reason": {"type": "string", "description": "为什么选择这个游戏的详细理由"},
                    "adaptation_suggestions": {"type": "string", "description": "针对这个孩子的个性化调整建议"}
                },
                "required": ["selected_game_id", "recommendation_reason", "adaptation_suggestions"],
                "additionalProperties": False
            }
        }

        # 7. 调用 LLM
        print(f"[GameRecommender] 开始调用 LLM 进行选择...")
        result = await self.llm.call_with_tool_execution(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=get_rag_tools(),
            output_schema=selection_schema,
            temperature=0.3, # 降低随机性，更精准选择
            max_tokens=1000
        )
        
        # 8. 解析结果并实例化
        selection = result.get("structured_output")
        if not selection or "selected_game_id" not in selection:
             raise ValueError("LLM 未能从库中选择有效的游戏")
             
        game_id = selection["selected_game_id"]
        game_plan = library_service.select_game_for_child(game_id, request.child_id)
        
        if not game_plan:
            # 如果 ID 幻觉了，尝试匹配标题或回退到第一个
            print(f"[GameRecommender] ⚠️ LLM 选择了不存在的 ID: {game_id}，尝试查找匹配项...")
            game_plan = library_service.select_game_for_child("game-001", request.child_id)
            
        # 9. 补充推荐理由和建议
        game_plan.design_rationale = selection["recommendation_reason"]
        game_plan.trend_analysis_summary = selection["adaptation_suggestions"]
        
        print(f"[GameRecommender] 游戏选择完成: {game_plan.title} ({game_id})")
        
        print(f"[GameRecommender] 游戏方案生成成功: {game_plan.title}")
        
        # 10. 保存到 SQLite
        await self._save_game_plan(game_plan)
        
        # 11. 保存到 Memory（Graphiti）
        await self._save_game_to_memory(game_plan)
        
        # 11. 构建响应
        response = GameRecommendResponse(
            game_plan=game_plan,
            trend_summary=game_plan.trend_analysis_summary or "暂无趋势分析数据",
            recommendation_reason=game_plan.design_rationale,
            message="游戏推荐成功"
        )
        
        print(f"[GameRecommender] 推荐完成: {game_id}")
        
        return response
    
    async def _save_game_plan(self, game_plan: GamePlan) -> None:
        """
        保存游戏方案到 SQLite
        
        Args:
            game_plan: 游戏方案
        """
        try:
            # TODO: 根据 SQLite 服务的实际接口调整
            # 暂时跳过，因为 SQLite 服务还没有 save_game_plan 方法
            print(f"[GameRecommender] ⚠️ SQLite 保存游戏方案功能待实现: {game_plan.game_id}")
        except Exception as e:
            print(f"[GameRecommender] 保存游戏方案失败: {e}")
            # 不抛出异常，允许推荐继续
    
    async def _save_game_to_memory(self, game_plan: GamePlan) -> None:
        """
        保存游戏方案到 Memory（Graphiti）
        
        Args:
            game_plan: 游戏方案
        """
        try:
            # 转换 GamePlan 为 Memory 服务需要的格式
            game_data = {
                "game_id": game_plan.game_id,
                "child_id": game_plan.child_id,
                "name": game_plan.title,
                "description": game_plan.description,
                "created_at": game_plan.created_at,
                "status": game_plan.status,
                "design": {
                    "target_dimension": game_plan.target_dimension.value if game_plan.target_dimension else None,
                    "goals": game_plan.goals.dict() if game_plan.goals else {},
                    "steps": [step.dict() for step in game_plan.steps] if game_plan.steps else [],
                    "materials_needed": game_plan.materials_needed or [],
                    "design_rationale": game_plan.design_rationale,
                    "trend_analysis_summary": game_plan.trend_analysis_summary
                },
                "implementation": {}  # 推荐时还没有实施数据
            }
            
            await self.memory_service.save_game(game_data)
            print(f"[GameRecommender] 游戏方案已保存到 Memory: {game_plan.game_id}")
        except Exception as e:
            print(f"[GameRecommender] 保存游戏方案到 Memory 失败: {e}")
            # 不抛出异常，允许推荐继续


__all__ = ['GameRecommender']
