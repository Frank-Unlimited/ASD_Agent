"""
关联分析器
"""
from typing import List, Dict, Any
from itertools import combinations
import numpy as np
from scipy.stats import pearsonr
from scipy.signal import correlate

from ..models.output import Correlation
from ..storage.graph_storage import GraphStorage
from ..utils.time_series import aggregate_daily, align_series


class CorrelationAnalyzer:
    """关联分析器"""
    
    def __init__(self, storage: GraphStorage):
        """
        初始化关联分析器
        
        Args:
            storage: 图存储实例
        """
        self.storage = storage
    
    def calculate_correlation(
        self,
        series_a: List[float],
        series_b: List[float]
    ) -> tuple:
        """
        计算皮尔逊相关系数
        
        Args:
            series_a: 时间序列A
            series_b: 时间序列B
            
        Returns:
            (correlation, p_value)
        """
        if len(series_a) != len(series_b) or len(series_a) < 5:
            return 0.0, 1.0
        
        correlation, p_value = pearsonr(series_a, series_b)
        return correlation, p_value
    
    def calculate_lag(
        self,
        series_a: List[float],
        series_b: List[float],
        max_lag: int = 14
    ) -> int:
        """
        计算时滞（A 领先 B 多少天）
        
        使用互相关分析
        
        Args:
            series_a: 维度 A 的时间序列
            series_b: 维度 B 的时间序列
            max_lag: 最大时滞天数
            
        Returns:
            lag_days: 正数表示 A 领先，负数表示 B 领先
        """
        if len(series_a) < max_lag * 2:
            return 0
        
        # 标准化
        a_norm = (np.array(series_a) - np.mean(series_a)) / (np.std(series_a) + 1e-10)
        b_norm = (np.array(series_b) - np.mean(series_b)) / (np.std(series_b) + 1e-10)
        
        # 互相关
        cross_corr = correlate(a_norm, b_norm, mode='full')
        lags = np.arange(-len(series_a) + 1, len(series_a))
        
        # 只看 ±max_lag 范围
        valid_idx = np.where(np.abs(lags) <= max_lag)[0]
        valid_lags = lags[valid_idx]
        valid_corr = cross_corr[valid_idx]
        
        # 找最大相关对应的 lag
        best_idx = np.argmax(np.abs(valid_corr))
        best_lag = valid_lags[best_idx]
        
        return int(best_lag)
    
    def infer_relationship(self, correlation: float, lag_days: int) -> str:
        """
        推断关系类型
        
        Args:
            correlation: 相关系数
            lag_days: 时滞天数
            
        Returns:
            关系描述
        """
        if abs(correlation) < 0.3:
            return "无明显关联"
        
        direction = "正相关" if correlation > 0 else "负相关"
        
        if abs(lag_days) <= 2:
            return f"同步{direction}"
        elif lag_days > 2:
            return f"A 可能促进 B（{direction}，领先 {lag_days} 天）"
        else:
            return f"B 可能促进 A（{direction}，领先 {-lag_days} 天）"
    
    async def analyze_all_correlations(
        self,
        child_id: str,
        min_data_points: int = 10,
        significance_threshold: float = 0.3
    ) -> List[Correlation]:
        """
        分析所有维度之间的关联
        
        Args:
            child_id: 孩子ID
            min_data_points: 最少数据点
            significance_threshold: 相关性阈值
            
        Returns:
            显著关联列表
        """
        # 获取所有维度
        dimensions = await self.storage.get_child_dimensions(child_id)
        
        # 获取各维度的时间序列数据
        series_data = {}
        for dim in dimensions:
            data = await self.storage.get_observations(child_id=child_id, dimension=dim)
            if len(data) >= min_data_points:
                # 按日聚合（取每日最后一条记录）
                daily_data = aggregate_daily([
                    {"timestamp": obs.get("timestamp"), "value": obs.get("value")}
                    for obs in data
                ])
                series_data[dim] = daily_data
        
        # 计算两两关联
        correlations = []
        for dim_a, dim_b in combinations(series_data.keys(), 2):
            # 对齐时间序列
            aligned_a, aligned_b, timestamps = align_series(
                series_data[dim_a],
                series_data[dim_b]
            )
            
            if len(aligned_a) < min_data_points:
                continue
            
            # 计算相关性
            corr, p_value = self.calculate_correlation(aligned_a, aligned_b)
            
            # 只保留显著相关
            if abs(corr) >= significance_threshold and p_value < 0.05:
                lag = self.calculate_lag(aligned_a, aligned_b)
                relationship = self.infer_relationship(corr, lag)
                
                correlations.append(Correlation(
                    dimension_a=dim_a,
                    dimension_b=dim_b,
                    correlation=round(corr, 3),
                    lag_days=lag,
                    relationship=relationship,
                    confidence=1 - p_value,
                    p_value=round(p_value, 4)
                ))
        
        # 按相关性强度排序
        correlations.sort(key=lambda x: abs(x.correlation), reverse=True)
        
        return correlations
    
    async def store_correlations(self, child_id: str, correlations: List[Correlation]) -> None:
        """
        将关联结果存储到图数据库
        
        Args:
            child_id: 孩子ID
            correlations: 关联列表
        """
        for corr in correlations:
            await self.storage.create_correlation_edge(
                child_id=child_id,
                dimension_a=corr.dimension_a,
                dimension_b=corr.dimension_b,
                correlation=corr.correlation,
                lag_days=corr.lag_days,
                relationship=corr.relationship,
                confidence=corr.confidence,
                p_value=corr.p_value
            )
