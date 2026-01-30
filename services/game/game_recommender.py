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
        profile_service: Any,
        # memory_service: Any,  # TODO: MemoryService 还未实现
        sqlite_service: Any
    ):
        """
        初始化游戏推荐服务
        
        Args:
            profile_service: 档案服务
            sqlite_service: SQLite 服务
        """
        self.profile_service = profile_service
        # self.memory_service = memory_service  # TODO
        self.sqlite = sqlite_service
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
        
        # 1. 获取孩子档案
        profile = await self.profile_service.get_profile(request.child_id)
        if not profile:
            raise ValueError(f"孩子档案不存在: {request.child_id}")
        
        print(f"[GameRecommender] 获取档案成功: {profile.name}")
        
        # 2. 获取近期评估和游戏总结
        # TODO: 从 MemoryService 获取
        recent_assessments = None  # await self.memory_service.get_recent_assessments(request.child_id)
        recent_games = None  # await self.memory_service.get_recent_games_summary(request.child_id)
        
        # 3. 构建 System Prompt
        system_prompt = build_game_recommendation_prompt(
            child_profile=profile,
            recent_assessments=recent_assessments,
            recent_games=recent_games,
            focus_dimension=request.focus_dimension.value if request.focus_dimension else None,
            duration_preference=request.duration_preference
        )
        
        print(f"[GameRecommender] System Prompt 构建完成，长度: {len(system_prompt)}")
        
        # 4. 构建 Output Schema（从 GamePlan 动态生成）
        output_schema = pydantic_to_json_schema(
            model=GamePlan,
            schema_name="GamePlan",
            description="完整的地板时光游戏方案"
        )
        
        print(f"[GameRecommender] Output Schema 构建完成")
        
        # 5. 构建用户消息
        user_message = "请为这个孩子推荐一个地板时光游戏方案。"
        if request.focus_dimension:
            user_message += f" 重点关注 {request.focus_dimension.value} 维度。"
        if request.duration_preference:
            user_message += f" 期望时长约 {request.duration_preference} 分钟。"
        
        # 6. 调用 LLM（带工具执行）
        print(f"[GameRecommender] 开始调用 LLM...")
        
        result = await self.llm.call_with_tool_execution(
            system_prompt=system_prompt,
            user_message=user_message,
            tools=get_rag_tools(),
            output_schema=output_schema,
            temperature=0.7,
            max_tokens=4000
        )
        
        print(f"[GameRecommender] LLM 调用完成")
        
        # 7. 解析结果
        if not result.get("structured_output"):
            raise ValueError("LLM 未返回结构化输出")
        
        game_data = result["structured_output"]
        
        # 8. 补充必要字段
        game_id = f"game-{uuid.uuid4().hex[:12]}"
        game_data["game_id"] = game_id
        game_data["child_id"] = request.child_id
        game_data["status"] = GameStatus.RECOMMENDED.value
        game_data["created_at"] = datetime.now().isoformat()
        game_data["recommended_by"] = "AI"
        
        # 9. 创建 GamePlan 对象
        game_plan = GamePlan(**game_data)
        
        print(f"[GameRecommender] 游戏方案生成成功: {game_plan.title}")
        
        # 10. 保存到 SQLite
        await self._save_game_plan(game_plan)
        
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
        # TODO: 根据 SQLite 服务的实际接口调整
        # 这里假设有一个 save_game_plan 方法
        try:
            await self.sqlite.save_game_plan({
                "game_id": game_plan.game_id,
                "child_id": game_plan.child_id,
                "data": game_plan.dict()
            })
            print(f"[GameRecommender] 游戏方案已保存到数据库: {game_plan.game_id}")
        except Exception as e:
            print(f"[GameRecommender] 保存游戏方案失败: {e}")
            # 不抛出异常，允许推荐继续


__all__ = ['GameRecommender']
