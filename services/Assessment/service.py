"""
评估服务 - 三个独立 Agent 的实现
"""
from datetime import datetime
from typing import Optional, Any, Dict, List

from src.models.assessment import (
    AssessmentReport,
    InterestHeatmap,
    DimensionTrends,
    AssessmentRequest,
    AssessmentResponse
)
from services.LLM_Service import get_llm_service
from services.game.schema_builder import pydantic_to_json_schema
from .prompts import (
    build_interest_mining_prompt,
    build_dimension_analysis_prompt,
    build_comprehensive_assessment_prompt
)


class AssessmentService:
    """
    评估服务 - 三个独立 Agent
    
    Agent 1: 兴趣挖掘 Agent（analyze_interests）
    Agent 2: 功能分析 Agent（analyze_dimensions）
    Agent 3: 综合评估 Agent（generate_assessment）
    """
    
    def __init__(
        self,
        sqlite_service: Any,
        memory_service: Any
    ):
        """
        初始化评估服务
        
        Args:
            sqlite_service: SQLite 服务
            memory_service: Memory 服务
        """
        self.sqlite = sqlite_service
        self.memory_service = memory_service
        self.llm = get_llm_service()
    
    async def generate_lightweight_assessment(
        self,
        child_id: str,
        game_id: str
    ) -> Dict[str, Any]:
        """
        轻量级评估 - 游戏后自动触发
        
        只分析游戏相关的维度，不调用完整的三个 Agent
        
        Args:
            child_id: 孩子ID
            game_id: 游戏ID
            
        Returns:
            轻量级评估结果
        """
        print(f"\n[AssessmentService] 开始生成轻量级评估: child_id={child_id}, game_id={game_id}")
        
        # 1. 获取游戏总结
        game = await self.memory_service.get_game(game_id)
        if not game:
            raise ValueError(f"游戏不存在: {game_id}")
        
        # 2. 提取游戏相关的维度和兴趣
        target_dimensions = [game.get("design", {}).get("target_dimension")]
        interest_points = game.get("design", {}).get("interest_points_used", [])
        
        # 3. 构建轻量级评估
        lightweight_result = {
            "assessment_type": "lightweight",
            "child_id": child_id,
            "game_id": game_id,
            "timestamp": datetime.now().isoformat(),
            "target_dimensions": target_dimensions,
            "interest_points": interest_points,
            "summary": game.get("implementation", {}).get("summary", ""),
            "engagement_score": game.get("implementation", {}).get("engagement_score", 0),
            "goal_achievement_score": game.get("implementation", {}).get("goal_achievement_score", 0)
        }
        
        print(f"[AssessmentService] 轻量级评估完成")
        
        return lightweight_result
    
    async def generate_comprehensive_assessment(
        self,
        request: AssessmentRequest
    ) -> AssessmentResponse:
        """
        完整评估 - 手动触发
        
        调用三个 Agent：
        1. 兴趣挖掘 Agent
        2. 功能分析 Agent
        3. 综合评估 Agent
        
        Args:
            request: 评估请求
            
        Returns:
            AssessmentResponse: 完整评估报告
        """
        print(f"\n[AssessmentService] 开始生成完整评估: child_id={request.child_id}")
        
        # 1. 获取孩子档案
        profile = self.sqlite.get_child(request.child_id)
        if not profile:
            raise ValueError(f"孩子档案不存在: {request.child_id}")
        
        print(f"[AssessmentService] 获取档案成功: {profile.name}")
        
        # 2. 调用 Agent 1: 兴趣挖掘
        print(f"[AssessmentService] 调用 Agent 1: 兴趣挖掘...")
        interest_heatmap = await self.analyze_interests(
            child_id=request.child_id,
            time_range_days=request.time_range_days
        )
        
        # 3. 调用 Agent 2: 功能分析
        print(f"[AssessmentService] 调用 Agent 2: 功能分析...")
        dimension_trends = await self.analyze_dimensions(
            child_id=request.child_id,
            time_range_days=request.time_range_days
        )
        
        # 4. 调用 Agent 3: 综合评估
        print(f"[AssessmentService] 调用 Agent 3: 综合评估...")
        assessment_report = await self.generate_assessment(
            child_id=request.child_id,
            interest_heatmap=interest_heatmap,
            dimension_trends=dimension_trends,
            time_range_days=request.time_range_days
        )
        
        # 5. 保存到 SQLite
        assessment_id = f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        assessment_data = {
            "assessment_id": assessment_id,
            "child_id": request.child_id,
            "assessment_type": "comprehensive",
            "timestamp": datetime.now().isoformat(),
            "report": assessment_report.dict(),
            "interest_heatmap": interest_heatmap.dict(),
            "dimension_trends": dimension_trends.dict()
        }
        
        self.sqlite.save_assessment(assessment_data)
        
        # 6. 保存到 Graphiti（使用新接口）
        # 构建评估文本
        assessment_text = self._build_assessment_text(
            profile=profile,
            assessment_report=assessment_report,
            interest_heatmap=interest_heatmap,
            dimension_trends=dimension_trends
        )
        
        # 调用 Memory 的 store_assessment()
        memory_result = await self.memory_service.store_assessment(
            child_id=request.child_id,
            assessment_text=assessment_text,
            assessment_type="comprehensive",
            metadata={
                "time_range_days": request.time_range_days,
                "assessment_id": assessment_id
            }
        )
        
        print(f"[AssessmentService] 评估已保存到 Memory: episode_id={memory_result['episode_id']}")
        
        print(f"[AssessmentService] 完整评估完成: {assessment_id}")
        
        # 7. 构建响应
        response = AssessmentResponse(
            assessment_id=assessment_id,
            child_id=request.child_id,
            timestamp=datetime.now(),
            report=assessment_report,
            interest_heatmap=interest_heatmap,
            dimension_trends=dimension_trends,
            message="评估生成成功"
        )
        
        return response
    
    async def analyze_interests(
        self,
        child_id: str,
        time_range_days: int = 30
    ) -> InterestHeatmap:
        """
        Agent 1: 兴趣挖掘 Agent
        
        职责：
        - 识别真实兴趣 vs 假设兴趣
        - 发现意外兴趣
        - 智能衰减（持续兴趣不衰减，短暂兴趣快速衰减）
        - 评估兴趣广度
        
        Args:
            child_id: 孩子ID
            time_range_days: 时间范围（天）
            
        Returns:
            InterestHeatmap: 兴趣热力图数据
        """
        print(f"\n[Agent 1] 兴趣挖掘 Agent 启动")
        
        # 1. 获取数据
        # 获取最近的行为记录
        behaviors = await self.memory_service.get_behaviors(
            child_id=child_id,
            filters={"limit": 100}
        )
        
        # 获取最近的游戏总结
        recent_games = await self.memory_service.get_recent_games(
            child_id=child_id,
            limit=10
        )
        
        # 获取上一次兴趣评估（用于对比）
        previous_interest = await self.memory_service.get_latest_interest(child_id)
        
        print(f"[Agent 1] 数据收集完成: {len(behaviors)} 条行为, {len(recent_games)} 个游戏")
        
        # 2. 构建 Prompt
        system_prompt = build_interest_mining_prompt(
            behaviors=behaviors,
            recent_games=recent_games,
            previous_interest=previous_interest,
            time_range_days=time_range_days
        )
        
        # 3. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=InterestHeatmap,
            schema_name="InterestHeatmap",
            description="兴趣热力图数据"
        )
        
        # 4. 调用 LLM
        result = await self.llm.call(
            system_prompt=system_prompt,
            user_message="请基于以上数据，生成兴趣热力图分析报告。",
            output_schema=output_schema,
            temperature=0.3,
            max_tokens=2500
        )
        
        # 5. 解析结果
        if not result.get("structured_output"):
            raise ValueError("Agent 1 未返回结构化输出")
        
        interest_data = result["structured_output"]
        interest_heatmap = InterestHeatmap(**interest_data)
        
        print(f"[Agent 1] 兴趣挖掘完成: {len(interest_heatmap.dimensions)} 个兴趣维度")
        
        return interest_heatmap
    
    async def analyze_dimensions(
        self,
        child_id: str,
        time_range_days: int = 30
    ) -> DimensionTrends:
        """
        Agent 2: 功能分析 Agent
        
        职责：
        - 识别活跃维度
        - 判断趋势（上升/稳定/下降）
        - 识别质变（主动性、持续性、泛化性、复杂性）
        - 维度关联分析
        
        Args:
            child_id: 孩子ID
            time_range_days: 时间范围（天）
            
        Returns:
            DimensionTrends: 功能维度趋势数据
        """
        print(f"\n[Agent 2] 功能分析 Agent 启动")
        
        # 1. 获取数据
        # 获取最近的行为记录
        behaviors = await self.memory_service.get_behaviors(
            child_id=child_id,
            filters={"limit": 100}
        )
        
        # 获取最近的游戏总结
        recent_games = await self.memory_service.get_recent_games(
            child_id=child_id,
            limit=10
        )
        
        # 获取上一次功能评估（用于对比）
        previous_function = await self.memory_service.get_latest_function(child_id)
        
        print(f"[Agent 2] 数据收集完成: {len(behaviors)} 条行为, {len(recent_games)} 个游戏")
        
        # 2. 构建 Prompt
        system_prompt = build_dimension_analysis_prompt(
            behaviors=behaviors,
            recent_games=recent_games,
            previous_function=previous_function,
            time_range_days=time_range_days
        )
        
        # 3. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=DimensionTrends,
            schema_name="DimensionTrends",
            description="功能维度趋势数据"
        )
        
        # 4. 调用 LLM
        print(f"[Agent 2] 调用 LLM，Schema: {output_schema.get('json_schema', {}).get('name', 'unknown')}")
        
        result = await self.llm.call(
            system_prompt=system_prompt,
            user_message="请基于以上数据，生成功能维度趋势分析报告。",
            output_schema=output_schema,
            temperature=0.3,
            max_tokens=2500
        )
        
        # 5. 解析结果
        if not result.get("structured_output"):
            print(f"[Agent 2] LLM 完整返回: {result}")
            print(f"[Agent 2] LLM 返回内容: {result.get('content', '')}")
            raise ValueError("Agent 2 未返回结构化输出")
        
        dimension_data = result["structured_output"]
        dimension_trends = DimensionTrends(**dimension_data)
        
        print(f"[Agent 2] 功能分析完成: {len(dimension_trends.active_dimensions)} 个维度")
        
        return dimension_trends
    
    async def generate_assessment(
        self,
        child_id: str,
        interest_heatmap: InterestHeatmap,
        dimension_trends: DimensionTrends,
        time_range_days: int = 30
    ) -> AssessmentReport:
        """
        Agent 3: 综合评估 Agent
        
        职责：
        - 整合 Agent 1 和 Agent 2 的分析结果
        - 生成家长友好的评估报告
        - 提供可操作的建议
        - 使用"三明治"结构（肯定→关注→建议）
        
        Args:
            child_id: 孩子ID
            interest_heatmap: 兴趣热力图（Agent 1 输出）
            dimension_trends: 功能维度趋势（Agent 2 输出）
            time_range_days: 时间范围（天）
            
        Returns:
            AssessmentReport: 完整评估报告
        """
        print(f"\n[Agent 3] 综合评估 Agent 启动")
        
        # 1. 获取数据
        # 获取最近的游戏总结
        recent_games = await self.memory_service.get_recent_games(
            child_id=child_id,
            limit=5
        )
        
        # 获取上一次综合评估（用于对比）
        previous_assessment = await self.memory_service.get_latest_assessment(
            child_id=child_id,
            assessment_type="comprehensive"
        )
        
        print(f"[Agent 3] 数据收集完成: {len(recent_games)} 个游戏")
        
        # 2. 构建 Prompt
        system_prompt = build_comprehensive_assessment_prompt(
            interest_heatmap=interest_heatmap,
            dimension_trends=dimension_trends,
            recent_games=recent_games,
            previous_assessment=previous_assessment,
            time_range_days=time_range_days
        )
        
        # 3. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=AssessmentReport,
            schema_name="AssessmentReport",
            description="完整评估报告"
        )
        
        # 4. 调用 LLM
        result = await self.llm.call(
            system_prompt=system_prompt,
            user_message="请基于以上分析，生成完整的综合评估报告。",
            output_schema=output_schema,
            temperature=0.5,  # 稍高温度，允许更有创造性的建议
            max_tokens=3000
        )
        
        # 5. 解析结果
        if not result.get("structured_output"):
            raise ValueError("Agent 3 未返回结构化输出")
        
        report_data = result["structured_output"]
        assessment_report = AssessmentReport(**report_data)
        
        print(f"[Agent 3] 综合评估完成")
        
        return assessment_report
    
    def _build_assessment_text(
        self,
        profile: Any,
        assessment_report: AssessmentReport,
        interest_heatmap: InterestHeatmap,
        dimension_trends: DimensionTrends
    ) -> str:
        """
        构建评估报告的自然语言文本
        
        Args:
            profile: 孩子档案
            assessment_report: 评估报告
            interest_heatmap: 兴趣热力图
            dimension_trends: 功能维度趋势
            
        Returns:
            自然语言评估文本
        """
        text_parts = []
        
        # 标题
        text_parts.append(f"# {profile.name} 综合评估报告")
        text_parts.append(f"\n评估时间: {datetime.now().strftime('%Y年%m月%d日')}")
        
        # 整体评估
        text_parts.append(f"\n## 整体评估")
        text_parts.append(assessment_report.overall_summary)
        
        # 兴趣分析
        text_parts.append(f"\n## 兴趣分析")
        text_parts.append(f"\n发现 {len(interest_heatmap.dimensions)} 个兴趣维度：")
        
        for dim in interest_heatmap.dimensions[:5]:  # 只显示前5个
            text_parts.append(f"\n### {dim.name}")
            text_parts.append(f"- 强度: {dim.intensity}/10")
            text_parts.append(f"- 类型: {dim.interest_type}")
            if dim.description:
                text_parts.append(f"- 描述: {dim.description}")
        
        # 功能维度分析
        text_parts.append(f"\n## 功能维度分析")
        text_parts.append(f"\n活跃维度数量: {len(dimension_trends.active_dimensions)}")
        
        for dim in dimension_trends.active_dimensions[:5]:  # 只显示前5个
            text_parts.append(f"\n### {dim.dimension_name}")
            text_parts.append(f"- 趋势: {dim.trend}")
            text_parts.append(f"- 当前水平: {dim.current_level}")
            if dim.qualitative_changes:
                text_parts.append(f"- 质变: {', '.join(dim.qualitative_changes)}")
        
        # 进步亮点
        if assessment_report.progress_highlights:
            text_parts.append(f"\n## 进步亮点")
            for i, highlight in enumerate(assessment_report.progress_highlights, 1):
                text_parts.append(f"{i}. {highlight}")
        
        # 需要关注的领域
        if assessment_report.areas_of_concern:
            text_parts.append(f"\n## 需要关注的领域")
            for i, concern in enumerate(assessment_report.areas_of_concern, 1):
                text_parts.append(f"{i}. {concern}")
        
        # 建议
        if assessment_report.recommendations:
            text_parts.append(f"\n## 建议")
            for i, rec in enumerate(assessment_report.recommendations, 1):
                text_parts.append(f"{i}. {rec}")
        
        return "\n".join(text_parts)


__all__ = ['AssessmentService']
