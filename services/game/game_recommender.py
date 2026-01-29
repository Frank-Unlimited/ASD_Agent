"""
游戏推荐服务
负责评估孩子状态、分析趋势、生成个性化游戏方案

依赖的基础服务：
- Graphiti: 获取画像和趋势分析
- SQLite: 存储游戏方案
- LLM: 生成详细游戏方案
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.models.game import (
    GamePlan,
    GameRecommendRequest,
    GameRecommendResponse,
    GameStep,
    GamePrecaution,
    GameGoal,
    GameStatus,
    TargetDimension,
)
from src.models.profile import ChildProfile

# 导入基础服务API
from services.Graphiti.api_interface import (
    build_context,
    get_recent_memories,
    analyze_trends,
    detect_milestones,
)


class GameRecommenderService:
    """游戏推荐服务"""

    def __init__(
        self,
        sqlite_service: Any,  # SQLite服务
        llm_service: Any,  # LLM服务
    ):
        """
        初始化游戏推荐服务

        Args:
            sqlite_service: SQLite数据库服务
            llm_service: LLM服务（用于生成游戏方案）
        """
        self.sqlite = sqlite_service
        self.llm = llm_service

    async def recommend_game(
        self,
        request: GameRecommendRequest
    ) -> GameRecommendResponse:
        """
        推荐游戏

        核心流程（用户需求）：
        1. 评估孩子当前状态（从Graphiti获取画像和最近观察）
        2. 分析趋势（各维度的发展趋势）
        3. 识别目标维度和兴趣点
        4. 生成详细的游戏方案（步骤、注意事项、目标）
        5. 保存到SQLite
        6. 返回游戏方案和推荐理由

        Args:
            request: 游戏推荐请求

        Returns:
            GameRecommendResponse: 游戏推荐响应
        """
        print(f"\n[GameRecommender] 开始为孩子 {request.child_id} 推荐游戏")

        # 1. 获取孩子档案
        child_data = await self.sqlite.get_child(request.child_id)
        if not child_data:
            raise ValueError(f"孩子档案不存在: {request.child_id}")

        child_profile = ChildProfile(**child_data["portrait"])

        # 2. 从Graphiti构建上下文（评估当前状态 + 分析趋势）
        context = await build_context(request.child_id)
        recent_memories = await get_recent_memories(request.child_id, days=7)
        milestones = await detect_milestones(request.child_id)

        print(f"[GameRecommender] 上下文构建完成，最近{len(recent_memories)}条记忆，{len(milestones)}个里程碑")

        # 3. 识别目标维度和兴趣点
        target_dimension, interests_to_use = await self._identify_target_and_interests(
            child_profile=child_profile,
            context=context,
            recent_memories=recent_memories,
            focus_dimension=request.focus_dimension
        )

        print(f"[GameRecommender] 目标维度: {target_dimension}, 兴趣点: {interests_to_use}")

        # 4. 生成游戏方案（使用LLM）
        game_plan = await self._generate_game_plan(
            child_profile=child_profile,
            target_dimension=target_dimension,
            interests=interests_to_use,
            context=context,
            recent_memories=recent_memories,
            duration_preference=request.duration_preference
        )

        # 5. 保存到SQLite
        await self.sqlite.save_weekly_plan({
            "planId": game_plan.game_id,
            "childId": request.child_id,
            "planData": game_plan.dict()
        })

        print(f"[GameRecommender] 游戏方案已保存: {game_plan.game_id}")

        # 6. 生成趋势摘要和推荐理由
        trend_summary = self._generate_trend_summary(context, recent_memories)
        recommendation_reason = self._generate_recommendation_reason(
            target_dimension, interests_to_use, context
        )

        return GameRecommendResponse(
            game_plan=game_plan,
            trend_summary=trend_summary,
            recommendation_reason=recommendation_reason,
            message="游戏推荐成功"
        )

    # ============ 私有方法 ============

    async def _identify_target_and_interests(
        self,
        child_profile: ChildProfile,
        context: Dict[str, Any],
        recent_memories: List[Dict[str, Any]],
        focus_dimension: Optional[TargetDimension] = None
    ) -> tuple[TargetDimension, List[str]]:
        """
        识别目标维度和可利用的兴趣点

        策略：
        1. 如果用户指定了focus_dimension，使用指定的
        2. 否则，根据趋势分析选择需要提升的维度
        3. 提取孩子的兴趣点

        Returns:
            (target_dimension, interests_to_use)
        """
        # 确定目标维度
        if focus_dimension:
            target_dimension = focus_dimension
        else:
            # 从趋势中选择需要关注的维度
            recent_trends = context.get("recentTrends", {})

            # 优先选择declining或stable的维度
            for dim, trend_data in recent_trends.items():
                if trend_data.get("trend") in ["declining", "stable"]:
                    try:
                        target_dimension = TargetDimension(dim)
                        break
                    except ValueError:
                        continue
            else:
                # 如果没有需要关注的，选择第一个有数据的维度
                for dim in recent_trends.keys():
                    try:
                        target_dimension = TargetDimension(dim)
                        break
                    except ValueError:
                        continue
                else:
                    # 如果都没有，默认选择eye_contact
                    target_dimension = TargetDimension.EYE_CONTACT

        # 提取兴趣点
        interests_to_use = []

        # 从档案中获取兴趣点
        for interest in child_profile.interests:
            interests_to_use.append(interest.name)

        # 从最近观察中提取提到的兴趣点
        for memory in recent_memories[:10]:  # 只看最近10条
            content = memory.get("content", "")
            # 简单的关键词匹配（实际可以用更复杂的方法）
            if "喜欢" in content or "感兴趣" in content:
                # 这里可以进一步提取具体的兴趣点
                pass

        # 如果没有兴趣点，使用默认的
        if not interests_to_use:
            interests_to_use = ["游戏", "玩具"]

        return target_dimension, interests_to_use[:3]  # 最多3个兴趣点

    async def _generate_game_plan(
        self,
        child_profile: ChildProfile,
        target_dimension: TargetDimension,
        interests: List[str],
        context: Dict[str, Any],
        recent_memories: List[Dict[str, Any]],
        duration_preference: Optional[int] = None
    ) -> GamePlan:
        """
        使用LLM生成详细的游戏方案

        Args:
            child_profile: 孩子档案
            target_dimension: 目标维度
            interests: 兴趣点列表
            context: 当前上下文
            recent_memories: 最近记忆
            duration_preference: 期望时长（分钟）

        Returns:
            GamePlan: 游戏方案
        """
        # 构建提示词
        dimension_names = {
            "eye_contact": "眼神接触",
            "joint_attention": "共同注意力",
            "social_interaction": "社交互动",
            "language": "语言能力",
            "imitation": "模仿能力",
            "emotional_regulation": "情绪调节",
            "play_skills": "游戏技能",
            "sensory": "感觉统合",
            "motor_skills": "运动技能",
            "cognitive": "认知能力",
        }

        prompt = f"""
你是一位专业的ASD（自闭症谱系障碍）儿童干预专家。请为以下孩子设计一个地板游戏方案。

## 孩子信息
- 姓名: {child_profile.name}
- 年龄: {(datetime.now() - datetime.fromisoformat(child_profile.birth_date)).days / 365:.1f}岁
- 诊断: {child_profile.diagnosis or '未知'}
- 兴趣点: {', '.join(interests)}

## 当前状态和趋势
{self._format_context_for_llm(context, recent_memories)}

## 设计要求
1. **目标维度**: {dimension_names.get(target_dimension.value, target_dimension.value)}
2. **利用兴趣点**: {', '.join(interests)}
3. **时长**: {duration_preference or 15}分钟左右
4. **重点**:
   - 挖掘孩子的兴趣点
   - 针对{dimension_names.get(target_dimension.value, target_dimension.value)}维度的提升
   - 基于最近观察到的趋势

## 输出格式（JSON）
请生成一个详细的地板游戏方案，包含：

{{
    "title": "游戏标题（简短有趣）",
    "description": "游戏简介（2-3句话）",
    "design_rationale": "设计依据（为什么推荐这个游戏，基于哪些观察和趋势）",
    "steps": [
        {{
            "step_number": 1,
            "title": "步骤标题",
            "description": "详细描述这一步要做什么",
            "duration_minutes": 3,
            "key_points": ["关键要点1", "关键要点2"],
            "parent_actions": ["家长需要做的动作1", "家长需要做的动作2"],
            "expected_child_response": "期待孩子的反应",
            "tips": ["小贴士1", "小贴士2"]
        }}
    ],
    "precautions": [
        {{
            "category": "安全",
            "content": "注意事项内容",
            "priority": "high"
        }}
    ],
    "goals": {{
        "primary_goal": "主要目标",
        "secondary_goals": ["次要目标1", "次要目标2"],
        "success_criteria": ["成功标准1", "成功标准2"]
    }},
    "materials_needed": ["所需材料1", "所需材料2"],
    "environment_setup": "环境布置建议"
}}

注意事项：
- 步骤要具体可操作，适合家长在家实施
- 充分利用孩子的兴趣点
- 注意安全和孩子的情绪
- 步骤数量：3-5步为宜
- 只返回JSON，不要其他文字
"""

        try:
            # 调用LLM生成
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.7,  # 适中的温度，保持创造性和稳定性
                response_format="json"
            )

            # 解析JSON
            data = json.loads(response)

            # 生成game_id
            game_id = f"game-{uuid.uuid4().hex[:12]}"

            # 转换为GamePlan
            game_plan = GamePlan(
                game_id=game_id,
                child_id=child_profile.child_id,
                title=data["title"],
                description=data["description"],
                estimated_duration=duration_preference or sum(
                    step.get("duration_minutes", 3) for step in data["steps"]
                ),
                target_dimension=target_dimension,
                interest_points_used=interests,
                design_rationale=data["design_rationale"],
                steps=[GameStep(**step) for step in data["steps"]],
                precautions=[GamePrecaution(**p) for p in data.get("precautions", [])],
                goals=GameGoal(**data["goals"]),
                materials_needed=data.get("materials_needed", []),
                environment_setup=data.get("environment_setup"),
                status=GameStatus.RECOMMENDED,
                trend_analysis_summary=self._generate_trend_summary(context, recent_memories)
            )

            return game_plan

        except Exception as e:
            print(f"[GameRecommender] LLM生成游戏方案失败: {e}，使用降级方案")
            # 降级方案：返回一个简单的默认游戏
            return self._create_fallback_game_plan(
                child_profile, target_dimension, interests, duration_preference
            )

    def _format_context_for_llm(
        self,
        context: Dict[str, Any],
        recent_memories: List[Dict[str, Any]]
    ) -> str:
        """格式化上下文为LLM可读的文本"""
        lines = []

        # 趋势
        lines.append("### 各维度趋势")
        trends = context.get("recentTrends", {})
        for dim, trend_data in trends.items():
            lines.append(f"- {dim}: {trend_data.get('trend', 'unknown')}")

        # 关注点
        attention_points = context.get("attentionPoints", [])
        if attention_points:
            lines.append("\n### 需要关注")
            for point in attention_points:
                lines.append(f"- {point}")

        # 最近观察
        lines.append("\n### 最近观察（7天内）")
        for memory in recent_memories[:5]:  # 只展示最近5条
            lines.append(f"- {memory.get('content', '')}")

        return "\n".join(lines)

    def _generate_trend_summary(
        self,
        context: Dict[str, Any],
        recent_memories: List[Dict[str, Any]]
    ) -> str:
        """生成趋势分析摘要"""
        trends = context.get("recentTrends", {})
        improving = [dim for dim, data in trends.items() if data.get("trend") == "improving"]
        declining = [dim for dim, data in trends.items() if data.get("trend") == "declining"]

        summary = f"根据最近7天的{len(recent_memories)}条观察记录，"

        if improving:
            summary += f"{', '.join(improving)}维度呈现改善趋势；"

        if declining:
            summary += f"{', '.join(declining)}维度需要关注；"

        if not improving and not declining:
            summary += "各维度表现稳定。"

        return summary

    def _generate_recommendation_reason(
        self,
        target_dimension: TargetDimension,
        interests: List[str],
        context: Dict[str, Any]
    ) -> str:
        """生成推荐理由"""
        dimension_names = {
            "eye_contact": "眼神接触",
            "joint_attention": "共同注意力",
            "social_interaction": "社交互动",
            "language": "语言能力",
            "imitation": "模仿能力",
            "emotional_regulation": "情绪调节",
            "play_skills": "游戏技能",
            "sensory": "感觉统合",
            "motor_skills": "运动技能",
            "cognitive": "认知能力",
        }

        reason = f"推荐此游戏的理由：\n"
        reason += f"1. 重点提升{dimension_names.get(target_dimension.value, target_dimension.value)}能力\n"
        reason += f"2. 结合孩子对{', '.join(interests)}的兴趣，增强参与度\n"
        reason += f"3. 基于最近的观察数据和趋势分析"

        return reason

    def _create_fallback_game_plan(
        self,
        child_profile: ChildProfile,
        target_dimension: TargetDimension,
        interests: List[str],
        duration_preference: Optional[int]
    ) -> GamePlan:
        """创建降级游戏方案"""
        game_id = f"game-{uuid.uuid4().hex[:12]}"

        return GamePlan(
            game_id=game_id,
            child_id=child_profile.child_id,
            title="互动游戏",
            description="基于孩子兴趣的简单互动游戏",
            estimated_duration=duration_preference or 15,
            target_dimension=target_dimension,
            interest_points_used=interests,
            design_rationale="基于孩子的兴趣点设计",
            steps=[
                GameStep(
                    step_number=1,
                    title="准备阶段",
                    description="准备游戏材料，营造轻松氛围",
                    duration_minutes=3,
                    key_points=["保持轻松", "观察孩子状态"],
                    parent_actions=["准备材料"],
                    tips=["根据孩子反应调整"]
                )
            ],
            precautions=[
                GamePrecaution(
                    category="安全",
                    content="注意材料安全",
                    priority="high"
                )
            ],
            goals=GameGoal(
                primary_goal=f"提升{target_dimension.value}能力",
                secondary_goals=["增强亲子互动"],
                success_criteria=["孩子积极参与"]
            ),
            materials_needed=["常见玩具"],
            environment_setup="安静舒适的空间",
            status=GameStatus.RECOMMENDED
        )
