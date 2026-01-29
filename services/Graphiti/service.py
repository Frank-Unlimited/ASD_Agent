"""
Graphiti 核心服务实现
完全重构版本 - 基于自定义图结构
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
import uuid

from .config import GraphitiConfig
from .storage.graph_storage import GraphStorage
from .storage.index_manager import IndexManager
from .analysis.trend_analyzer import TrendAnalyzer
from .analysis.plateau_detector import PlateauDetector
from .analysis.anomaly_detector import AnomalyDetector
from .analysis.correlation_analyzer import CorrelationAnalyzer
from .models.output import (
    DataPoint,
    TrendInfo,
    DimensionTrend,
    Milestone as MilestoneOutput,
    TrendAnalysisResult,
    TrendSummary
)
from .models.dimensions import get_display_name, get_dimension_config

# 从项目配置读取 Neo4j 设置
from src.config import settings


class GraphitiService:
    """Graphiti 核心服务"""
    
    def __init__(self, config: Optional[GraphitiConfig] = None):
        """
        初始化 Graphiti 服务
        
        Args:
            config: Graphiti 配置，如果为 None 则使用默认配置
        """
        self.config = config or GraphitiConfig(
            neo4j_uri=settings.neo4j_uri,
            neo4j_user=settings.neo4j_user,
            neo4j_password=settings.neo4j_password
        )
        
        # 初始化存储层
        self.storage = GraphStorage(
            uri=self.config.neo4j_uri,
            user=self.config.neo4j_user,
            password=self.config.neo4j_password
        )
        
        # 初始化索引管理器
        self.index_manager = IndexManager(self.storage.driver)
        
        # 初始化分析器
        self.trend_analyzer = TrendAnalyzer(self.storage)
        self.plateau_detector = PlateauDetector()
        self.anomaly_detector = AnomalyDetector()
        self.correlation_analyzer = CorrelationAnalyzer(self.storage)
        
        print(f"[Graphiti Service] 已连接到 Neo4j: {self.config.neo4j_uri}")
    
    async def initialize(self) -> None:
        """初始化服务（创建索引等）"""
        await self.index_manager.create_indexes()
        print("[Graphiti Service] 服务初始化完成")
    
    async def close(self):
        """关闭连接"""
        await self.storage.close()
    
    # ============ 数据存储接口 ============
    
    async def save_observations(self, input_data: Dict[str, Any]) -> None:
        """
        保存观察数据
        
        Args:
            input_data: 标准输入 JSON，包含:
                - child_id: 孩子ID
                - timestamp: 时间戳
                - source: 数据来源
                - session_id: 会话ID（可选）
                - observations: 观察记录列表
                - milestone: 里程碑信息（可选）
                - metadata: 元数据（可选）
        """
        child_id = input_data.get('child_id')
        if not child_id:
            raise ValueError("child_id is required")
        
        # 1. 确保 Child 节点存在
        await self.storage.ensure_child_node(child_id)
        
        # 2. 处理每个观察记录
        observations = input_data.get('observations', [])
        last_observation_id = None
        
        for obs in observations:
            dimension = obs.get('dimension')
            if not dimension:
                continue
            
            # 确保 Dimension 节点存在
            await self.storage.ensure_dimension_node(child_id, dimension)
            
            # 创建 Observation 节点
            observation_id = await self.storage.create_observation_node(
                child_id=child_id,
                dimension=dimension,
                value=obs.get('value'),
                value_type=obs.get('value_type', 'score'),
                timestamp=input_data.get('timestamp'),
                source=input_data.get('source'),
                context=obs.get('context'),
                confidence=obs.get('confidence', 0.8),
                session_id=input_data.get('session_id')
            )
            
            last_observation_id = observation_id
        
        # 3. 处理里程碑
        milestone_data = input_data.get('milestone', {})
        if milestone_data.get('detected'):
            await self.storage.create_milestone_node(
                child_id=child_id,
                dimension=milestone_data.get('dimension'),
                milestone_type=milestone_data.get('type', 'first_time'),
                description=milestone_data.get('description', ''),
                timestamp=input_data.get('timestamp'),
                significance=milestone_data.get('significance', 'high'),
                observation_id=last_observation_id
            )
        
        print(f"[Graphiti Service] 成功保存 {len(observations)} 条观察记录")
    
    # ============ 趋势分析接口 ============
    
    async def get_dimension_trend(
        self,
        child_id: str,
        dimension: str,
        include_data_points: bool = True
    ) -> DimensionTrend:
        """
        获取单维度趋势
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            include_data_points: 是否包含原始数据点
            
        Returns:
            DimensionTrend: 该维度的完整趋势数据
        """
        # 获取多时间窗口趋势
        trends = await self.trend_analyzer.analyze_multi_window_trend(child_id, dimension)
        
        # 获取所有观察数据
        all_observations = await self.storage.get_observations(child_id=child_id, dimension=dimension)
        
        # 计算当前值（最近7天均值）
        now = datetime.now(timezone.utc)
        recent_7d = [
            obs for obs in all_observations
            if datetime.fromisoformat(obs.get('timestamp', '')).replace(tzinfo=timezone.utc) >= now - timedelta(days=7)
        ]
        current_value = sum(obs.get('value', 0) for obs in recent_7d) / len(recent_7d) if recent_7d else 0.0
        
        # 获取基线值
        dimension_info = await self.storage.get_observations(child_id=child_id, dimension=dimension, limit=1)
        baseline_value = dimension_info[0].get('value', 0) if dimension_info else 0.0
        
        # 计算总体提升
        total_improvement = (current_value - baseline_value) / baseline_value if baseline_value > 0 else 0.0
        
        # 平台期检测
        data_points_for_analysis = [
            {"timestamp": obs.get("timestamp"), "value": obs.get("value")}
            for obs in all_observations
        ]
        plateau = self.plateau_detector.detect_plateau(
            data_points_for_analysis,
            window_days=self.config.plateau_window_days,
            variance_threshold=self.config.plateau_variance_threshold
        )
        
        # 异常检测
        anomaly = self.anomaly_detector.detect_anomaly(
            data_points_for_analysis,
            std_threshold=self.config.anomaly_std_threshold
        )
        
        # 准备数据点
        data_points = []
        if include_data_points:
            data_points = [
                DataPoint(
                    timestamp=obs.get('timestamp', ''),
                    value=obs.get('value', 0),
                    source=obs.get('source', ''),
                    confidence=obs.get('confidence', 0.8),
                    context=obs.get('context')
                )
                for obs in all_observations
            ]
        
        # 获取维度配置
        config = get_dimension_config(dimension)
        
        return DimensionTrend(
            dimension=dimension,
            display_name=get_display_name(dimension),
            category=config.get('category', 'behavior') if config else 'behavior',
            current_value=current_value,
            baseline_value=baseline_value,
            total_improvement=total_improvement,
            trend_7d=trends['trend_7d'],
            trend_30d=trends['trend_30d'],
            trend_90d=trends['trend_90d'],
            plateau=plateau,
            anomaly=anomaly,
            data_points=data_points,
            data_point_count=len(all_observations)
        )
    
    async def get_full_trend(self, child_id: str) -> TrendAnalysisResult:
        """
        获取完整趋势分析
        
        Args:
            child_id: 孩子ID
            
        Returns:
            TrendAnalysisResult: 包含所有维度趋势、里程碑、关联的完整结果
        """
        # 获取所有维度
        dimensions = await self.storage.get_child_dimensions(child_id)
        
        # 获取各维度趋势
        dimension_trends = {}
        for dim in dimensions:
            dimension_trends[dim] = await self.get_dimension_trend(child_id, dim, include_data_points=False)
        
        # 获取最近里程碑
        milestones_data = await self.storage.get_milestones(child_id=child_id, limit=10)
        recent_milestones = [
            MilestoneOutput(
                milestone_id=m.get('milestone_id', ''),
                dimension=m.get('dimension', ''),
                type=m.get('type', ''),
                description=m.get('description', ''),
                timestamp=m.get('timestamp', ''),
                significance=m.get('significance', 'medium')
            )
            for m in milestones_data
        ]
        
        # 获取关联
        correlations_data = await self.storage.get_correlations(
            child_id=child_id,
            min_correlation=self.config.correlation_threshold
        )
        
        # 生成摘要
        summary = self._generate_summary(dimension_trends)
        
        return TrendAnalysisResult(
            child_id=child_id,
            child_name="",  # 需要从其他地方获取
            analysis_time=datetime.now(timezone.utc).isoformat(),
            dimensions=dimension_trends,
            recent_milestones=recent_milestones,
            total_milestones=len(milestones_data),
            correlations=[],  # 从 correlations_data 转换
            summary=summary
        )
    
    async def get_quick_summary(self, child_id: str) -> TrendSummary:
        """
        获取快速摘要
        
        Args:
            child_id: 孩子ID
            
        Returns:
            TrendSummary: 简要摘要
        """
        # 获取所有维度
        dimensions = await self.storage.get_child_dimensions(child_id)
        
        # 获取各维度趋势
        dimension_trends = {}
        for dim in dimensions:
            dimension_trends[dim] = await self.get_dimension_trend(child_id, dim, include_data_points=False)
        
        return self._generate_summary(dimension_trends)
    
    def _generate_summary(self, dimension_trends: Dict[str, DimensionTrend]) -> TrendSummary:
        """
        生成趋势摘要
        
        Args:
            dimension_trends: 维度趋势字典
            
        Returns:
            TrendSummary: 趋势摘要
        """
        attention_dimensions = []
        improving_dimensions = []
        stable_dimensions = []
        
        for dim, trend in dimension_trends.items():
            if trend.trend_30d.direction == "declining" or trend.plateau.is_plateau:
                attention_dimensions.append(dim)
            elif trend.trend_30d.direction == "improving":
                improving_dimensions.append(dim)
            else:
                stable_dimensions.append(dim)
        
        # 判断整体状态
        if len(improving_dimensions) > len(attention_dimensions) * 2:
            overall_status = "excellent"
        elif len(improving_dimensions) > len(attention_dimensions):
            overall_status = "good"
        else:
            overall_status = "attention_needed"
        
        # 生成建议
        recommendation = self._generate_recommendation(
            attention_dimensions,
            improving_dimensions,
            dimension_trends
        )
        
        return TrendSummary(
            attention_dimensions=attention_dimensions,
            improving_dimensions=improving_dimensions,
            stable_dimensions=stable_dimensions,
            overall_status=overall_status,
            recommendation=recommendation
        )
    
    def _generate_recommendation(
        self,
        attention_dimensions: List[str],
        improving_dimensions: List[str],
        dimension_trends: Dict[str, DimensionTrend]
    ) -> str:
        """生成综合建议"""
        parts = []
        
        if improving_dimensions:
            improving_names = [get_display_name(d) for d in improving_dimensions[:3]]
            parts.append(f"{', '.join(improving_names)}进展良好，建议继续当前游戏类型")
        
        if attention_dimensions:
            attention_names = [get_display_name(d) for d in attention_dimensions[:2]]
            parts.append(f"{', '.join(attention_names)}需要关注，可尝试调整干预策略")
        
        return "；".join(parts) if parts else "继续当前计划"
    
    # ============ 关联分析接口 ============
    
    async def refresh_correlations(self, child_id: str) -> None:
        """
        刷新关联分析
        
        Args:
            child_id: 孩子ID
        """
        correlations = await self.correlation_analyzer.analyze_all_correlations(
            child_id=child_id,
            min_data_points=self.config.correlation_min_points,
            significance_threshold=self.config.correlation_threshold
        )
        
        await self.correlation_analyzer.store_correlations(child_id, correlations)
        print(f"[Graphiti Service] 已刷新 {len(correlations)} 个关联关系")
    
    # ============ 里程碑接口 ============
    
    async def get_milestones(
        self,
        child_id: str,
        days: Optional[int] = None,
        dimension: Optional[str] = None
    ) -> List[MilestoneOutput]:
        """
        获取里程碑
        
        Args:
            child_id: 孩子ID
            days: 最近多少天（None 表示全部）
            dimension: 指定维度（None 表示全部）
            
        Returns:
            List[Milestone]: 里程碑列表
        """
        start_time = None
        if days:
            start_time = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        
        milestones_data = await self.storage.get_milestones(
            child_id=child_id,
            dimension=dimension,
            start_time=start_time
        )
        
        return [
            MilestoneOutput(
                milestone_id=m.get('milestone_id', ''),
                dimension=m.get('dimension', ''),
                type=m.get('type', ''),
                description=m.get('description', ''),
                timestamp=m.get('timestamp', ''),
                significance=m.get('significance', 'medium')
            )
            for m in milestones_data
        ]


# 全局服务实例（单例模式）
_service_instance: Optional[GraphitiService] = None


async def get_service(config: Optional[GraphitiConfig] = None) -> GraphitiService:
    """获取 Graphiti 服务实例（单例）"""
    global _service_instance
    
    if _service_instance is None:
        _service_instance = GraphitiService(config)
        await _service_instance.initialize()
    
    return _service_instance
