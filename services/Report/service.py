"""
报告生成服务
整合评估结果、游戏总结、行为记录，生成给医生看的完整报告
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uuid
import json

from src.models.report import (
    MedicalReport,
    DevelopmentDimensionReport,
    InterventionSummary,
    ObservationSummary,
    ChartData,
    ChartType,
    ReportType
)


class ReportService:
    """报告生成服务"""
    
    def __init__(self, sqlite_service, memory_service):
        self.sqlite_service = sqlite_service
        self.memory_service = memory_service
    
    async def generate_medical_report(
        self,
        child_id: str,
        start_date: str,
        end_date: str
    ) -> MedicalReport:
        """
        生成医生版报告
        
        Args:
            child_id: 孩子ID
            start_date: 开始日期（YYYY-MM-DD）
            end_date: 结束日期（YYYY-MM-DD）
        
        Returns:
            MedicalReport
        """
        print(f"[ReportService] 开始生成医生版报告: {child_id}")
        
        # 1. 获取孩子档案
        profile = self.sqlite_service.get_child(child_id)
        if not profile:
            raise ValueError(f"孩子档案不存在: {child_id}")
        
        # 2. 获取最新评估
        latest_assessment = await self.memory_service.get_latest_assessment(
            child_id=child_id,
            assessment_type="comprehensive"
        )
        
        # 3. 获取时间范围内的游戏会话
        games = await self._get_games_in_period(child_id, start_date, end_date)
        
        # 4. 获取时间范围内的行为记录
        behaviors = await self._get_behaviors_in_period(child_id, start_date, end_date)
        
        # 5. 生成发展维度报告
        development_dimensions = await self._generate_dimension_reports(
            child_id,
            latest_assessment,
            behaviors
        )
        
        # 6. 生成观察记录总结
        observation_summary = self._generate_observation_summary(behaviors)
        
        # 7. 生成干预总结
        intervention_summary = self._generate_intervention_summary(games)
        
        # 8. 生成整体评估
        overall_progress = self._generate_overall_progress(
            latest_assessment,
            development_dimensions,
            intervention_summary
        )
        
        # 9. 提取优势和改善领域
        strengths, areas_for_improvement = self._extract_strengths_and_areas(
            latest_assessment,
            development_dimensions
        )
        
        # 10. 生成图表数据
        charts = self._generate_charts(
            development_dimensions,
            games,
            behaviors
        )
        
        # 11. 生成临床建议
        clinical_recommendations = self._generate_clinical_recommendations(
            latest_assessment,
            development_dimensions
        )
        
        # 12. 计算年龄
        from datetime import datetime
        birth_date = datetime.strptime(profile.birth_date, "%Y-%m-%d")
        age_years = (datetime.now() - birth_date).days // 365
        age_months = ((datetime.now() - birth_date).days % 365) // 30
        age_str = f"{age_years}岁{age_months}个月"
        
        # 13. 创建报告
        report = MedicalReport(
            report_id=f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
            child_id=child_id,
            child_name=profile.name,
            gender=profile.gender.value,
            birth_date=profile.birth_date,
            age=age_str,
            diagnosis=profile.diagnosis,
            report_period_start=start_date,
            report_period_end=end_date,
            development_dimensions=development_dimensions,
            observation_summary=observation_summary,
            intervention_summary=intervention_summary,
            overall_progress=overall_progress,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            charts=charts,
            clinical_recommendations=clinical_recommendations,
            next_assessment_date=self._calculate_next_assessment_date(end_date)
        )
        
        print(f"[ReportService] 报告生成完成: {report.report_id}")
        return report
    
    async def _get_games_in_period(
        self,
        child_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """获取时间范围内的游戏会话"""
        # 从 Memory 服务获取游戏
        all_games = await self.memory_service.get_recent_games(child_id, limit=100)
        
        # 过滤时间范围
        filtered_games = []
        for game in all_games:
            created_at = game.get("created_at", "")
            # 处理 DateTime 对象或字符串
            if hasattr(created_at, 'strftime'):
                game_date = created_at.strftime("%Y-%m-%d")
            else:
                game_date = str(created_at)[:10]
            
            if start_date <= game_date <= end_date:
                filtered_games.append(game)
        
        return filtered_games
    
    async def _get_behaviors_in_period(
        self,
        child_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict[str, Any]]:
        """获取时间范围内的行为记录"""
        # 从 Memory 服务获取行为
        behaviors = await self.memory_service.get_behaviors(
            child_id=child_id,
            filters={
                "start_time": f"{start_date}T00:00:00Z",
                "end_time": f"{end_date}T23:59:59Z",
                "limit": 500
            }
        )
        return behaviors
    
    async def _generate_dimension_reports(
        self,
        child_id: str,
        latest_assessment: Optional[Dict[str, Any]],
        behaviors: List[Dict[str, Any]]
    ) -> List[DevelopmentDimensionReport]:
        """生成发展维度报告"""
        dimension_reports = []
        
        if not latest_assessment:
            return dimension_reports
        
        # 从评估中提取维度数据
        analysis = latest_assessment.get("analysis", {})
        
        # Agent 2 的功能分析结果
        function_analysis = analysis.get("active_dimensions", {})
        
        for dim_key, dim_data in function_analysis.items():
            # 提取维度信息
            dimension_name = dim_data.get("dimension_name", dim_key)
            current_level = dim_data.get("current_level", 0)
            baseline = dim_data.get("baseline", 0)
            change = dim_data.get("change", 0)
            trend_str = dim_data.get("trend", "stable")
            
            # 从行为记录中提取关键观察
            key_observations = self._extract_key_observations_for_dimension(
                dim_key,
                behaviors
            )
            
            # 生成建议
            recommendations = self._generate_dimension_recommendations(
                dimension_name,
                current_level,
                trend_str
            )
            
            dimension_report = DevelopmentDimensionReport(
                dimension_id=dim_key,
                dimension_name=dimension_name,
                current_level=current_level,
                initial_level=baseline,
                change=change,
                trend=trend_str,
                key_observations=key_observations[:5],  # 最多5条
                milestones_achieved=[],  # TODO: 从评估中提取
                recommendations=recommendations
            )
            
            dimension_reports.append(dimension_report)
        
        return dimension_reports
    
    def _extract_key_observations_for_dimension(
        self,
        dimension_key: str,
        behaviors: List[Dict[str, Any]]
    ) -> List[str]:
        """从行为记录中提取与维度相关的关键观察"""
        observations = []
        
        for behavior in behaviors[:20]:  # 只看最近20条
            # 检查行为是否与该维度相关
            related_functions = behavior.get("ai_analysis", {}).get("related_functions", [])
            if dimension_key in related_functions or any(dimension_key in f for f in related_functions):
                description = behavior.get("description", "")
                timestamp = behavior.get("timestamp", "")
                # 处理 DateTime 对象或字符串
                if hasattr(timestamp, 'strftime'):
                    timestamp_str = timestamp.strftime("%Y-%m-%d")
                else:
                    timestamp_str = str(timestamp)[:10]
                observations.append(f"[{timestamp_str}] {description}")
        
        return observations
    
    def _generate_dimension_recommendations(
        self,
        dimension_name: str,
        current_level: float,
        trend: str
    ) -> List[str]:
        """生成维度建议"""
        recommendations = []
        
        if trend == "increasing":
            recommendations.append(f"继续保持当前干预策略，{dimension_name}呈现良好进展")
        elif trend == "stable":
            recommendations.append(f"考虑调整干预方法，以促进{dimension_name}的进一步发展")
        else:  # declining
            recommendations.append(f"需要重点关注{dimension_name}，建议增加针对性训练")
        
        if current_level < 3:
            recommendations.append(f"建议加强基础能力训练")
        elif current_level < 6:
            recommendations.append(f"可以尝试更复杂的互动活动")
        else:
            recommendations.append(f"表现良好，可以逐步泛化到日常生活场景")
        
        return recommendations
    
    def _generate_observation_summary(
        self,
        behaviors: List[Dict[str, Any]]
    ) -> ObservationSummary:
        """生成观察记录总结"""
        total = len(behaviors)
        voice_count = sum(1 for b in behaviors if b.get("input_type") == "voice")
        text_count = sum(1 for b in behaviors if b.get("input_type") == "text")
        video_count = sum(1 for b in behaviors if b.get("input_type") == "video")
        
        breakthrough_count = sum(
            1 for b in behaviors
            if b.get("significance") == "breakthrough"
        )
        concern_count = sum(
            1 for b in behaviors
            if b.get("significance") == "concern"
        )
        
        # 提取关键发现
        key_findings = []
        for behavior in behaviors:
            if behavior.get("significance") in ["breakthrough", "concern"]:
                description = behavior.get("description", "")
                timestamp = behavior.get("timestamp", "")
                # 处理 DateTime 对象或字符串
                if hasattr(timestamp, 'strftime'):
                    timestamp_str = timestamp.strftime("%Y-%m-%d")
                else:
                    timestamp_str = str(timestamp)[:10]
                key_findings.append(f"[{timestamp_str}] {description}")
        
        return ObservationSummary(
            total_observations=total,
            voice_observations=voice_count,
            text_observations=text_count,
            video_observations=video_count,
            breakthrough_count=breakthrough_count,
            concern_count=concern_count,
            key_findings=key_findings[:10]  # 最多10条
        )
    
    def _generate_intervention_summary(
        self,
        games: List[Dict[str, Any]]
    ) -> InterventionSummary:
        """生成干预总结"""
        total_sessions = len(games)
        
        # 计算总时长
        total_duration = 0
        for game in games:
            implementation = game.get("implementation", {})
            duration = implementation.get("duration_minutes", 0)
            total_duration += duration
        
        total_duration_hours = total_duration / 60
        
        # 提取实施的游戏
        games_implemented = []
        engagement_scores = []
        goal_achievements = []
        
        for game in games:
            implementation = game.get("implementation", {})
            engagement_score = implementation.get("engagement_score", 0)
            goal_achievement = implementation.get("goal_achievement_score", 0)
            
            if engagement_score > 0:
                engagement_scores.append(engagement_score)
            if goal_achievement > 0:
                goal_achievements.append(goal_achievement)
            
            # 处理日期
            created_at = game.get("created_at", "")
            if hasattr(created_at, 'strftime'):
                date_str = created_at.strftime("%Y-%m-%d")
            else:
                date_str = str(created_at)[:10]
            
            games_implemented.append({
                "name": game.get("name", ""),
                "date": date_str,
                "engagement_score": engagement_score,
                "goal_achievement_score": goal_achievement
            })
        
        # 找出最有效的游戏
        most_effective_game = None
        if games_implemented:
            sorted_games = sorted(
                games_implemented,
                key=lambda g: (g.get("goal_achievement_score", 0) + g.get("engagement_score", 0)) / 2,
                reverse=True
            )
            most_effective_game = sorted_games[0].get("name") if sorted_games else None
        
        # 计算平均分
        avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
        avg_goal = sum(goal_achievements) / len(goal_achievements) if goal_achievements else 0
        
        return InterventionSummary(
            total_sessions=total_sessions,
            total_duration_hours=round(total_duration_hours, 1),
            games_implemented=games_implemented,
            most_effective_game=most_effective_game,
            avg_engagement_score=round(avg_engagement, 1) if avg_engagement > 0 else None,
            avg_goal_achievement=round(avg_goal, 1) if avg_goal > 0 else None
        )
    
    def _generate_overall_progress(
        self,
        latest_assessment: Optional[Dict[str, Any]],
        development_dimensions: List[DevelopmentDimensionReport],
        intervention_summary: InterventionSummary
    ) -> str:
        """生成总体进展评估"""
        if not latest_assessment:
            return "暂无评估数据"
        
        analysis = latest_assessment.get("analysis", {})
        overall = analysis.get("overall_assessment", "")
        
        # 添加干预总结
        progress_text = f"{overall}\n\n"
        progress_text += f"**干预情况**：共完成 {intervention_summary.total_sessions} 次地板时光游戏，"
        progress_text += f"累计时长 {intervention_summary.total_duration_hours} 小时。"
        
        if intervention_summary.avg_engagement_score:
            progress_text += f"平均参与度 {intervention_summary.avg_engagement_score}/10，"
        if intervention_summary.avg_goal_achievement:
            progress_text += f"平均目标达成度 {intervention_summary.avg_goal_achievement}/10。"
        
        # 添加维度趋势
        improving_dims = [d for d in development_dimensions if d.trend == "increasing"]
        if improving_dims:
            progress_text += f"\n\n**进步维度**：{', '.join([d.dimension_name for d in improving_dims])}"
        
        return progress_text
    
    def _extract_strengths_and_areas(
        self,
        latest_assessment: Optional[Dict[str, Any]],
        development_dimensions: List[DevelopmentDimensionReport]
    ) -> tuple[List[str], List[str]]:
        """提取优势和改善领域"""
        strengths = []
        areas_for_improvement = []
        
        if latest_assessment:
            analysis = latest_assessment.get("analysis", {})
            strengths = analysis.get("strengths", [])
            areas_for_improvement = analysis.get("challenges", [])
        
        # 从维度中补充
        for dim in development_dimensions:
            if dim.current_level >= 7:
                strengths.append(f"{dim.dimension_name}表现优秀（{dim.current_level}/10）")
            elif dim.current_level < 4:
                areas_for_improvement.append(f"{dim.dimension_name}需要加强（{dim.current_level}/10）")
        
        return strengths[:5], areas_for_improvement[:5]
    
    def _generate_charts(
        self,
        development_dimensions: List[DevelopmentDimensionReport],
        games: List[Dict[str, Any]],
        behaviors: List[Dict[str, Any]]
    ) -> List[ChartData]:
        """生成图表数据"""
        charts = []
        
        # 1. 发展维度雷达图
        if development_dimensions:
            radar_data = {
                "labels": [d.dimension_name for d in development_dimensions],
                "datasets": [
                    {
                        "label": "当前水平",
                        "data": [d.current_level for d in development_dimensions]
                    }
                ]
            }
            
            # 如果有基线数据，添加对比
            if any(d.initial_level for d in development_dimensions):
                radar_data["datasets"].append({
                    "label": "初始水平",
                    "data": [d.initial_level or 0 for d in development_dimensions]
                })
            
            charts.append(ChartData(
                chart_type=ChartType.RADAR,
                title="发展维度评估",
                data=radar_data,
                description="各发展维度的当前水平和初始水平对比"
            ))
        
        # 2. 游戏参与度折线图
        if games:
            game_dates = []
            engagement_scores = []
            
            for g in games:
                created_at = g.get("created_at", "")
                if hasattr(created_at, 'strftime'):
                    game_dates.append(created_at.strftime("%Y-%m-%d"))
                else:
                    game_dates.append(str(created_at)[:10])
                
                engagement_scores.append(
                    g.get("implementation", {}).get("engagement_score", 0)
                )
            
            charts.append(ChartData(
                chart_type=ChartType.LINE,
                title="游戏参与度趋势",
                data={
                    "labels": game_dates,
                    "datasets": [{
                        "label": "参与度",
                        "data": engagement_scores
                    }]
                },
                description="地板时光游戏的参与度变化趋势"
            ))
        
        # 3. 行为记录类型分布
        if behaviors:
            event_types = {}
            for b in behaviors:
                event_type = b.get("event_type", "other")
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            charts.append(ChartData(
                chart_type=ChartType.BAR,
                title="行为记录类型分布",
                data={
                    "labels": list(event_types.keys()),
                    "datasets": [{
                        "label": "次数",
                        "data": list(event_types.values())
                    }]
                },
                description="不同类型行为记录的数量分布"
            ))
        
        return charts
    
    def _generate_clinical_recommendations(
        self,
        latest_assessment: Optional[Dict[str, Any]],
        development_dimensions: List[DevelopmentDimensionReport]
    ) -> List[str]:
        """生成临床建议"""
        recommendations = []
        
        if latest_assessment:
            analysis = latest_assessment.get("analysis", {})
            summary = analysis.get("summary", {})
            recommendations.extend(summary.get("recommendations", []))
        
        # 从维度中补充建议
        for dim in development_dimensions:
            recommendations.extend(dim.recommendations)
        
        # 去重并限制数量
        unique_recommendations = list(dict.fromkeys(recommendations))
        return unique_recommendations[:10]
    
    def _calculate_next_assessment_date(self, end_date: str) -> str:
        """计算建议的下次评估日期（3个月后）"""
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        next_date = end_dt + timedelta(days=90)
        return next_date.strftime("%Y-%m-%d")
