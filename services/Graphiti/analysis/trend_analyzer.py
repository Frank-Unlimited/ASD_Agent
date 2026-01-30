"""
趋势分析器
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone
import numpy as np
from scipy import stats

from ..models.output import TrendInfo
from ..storage.graph_storage import GraphStorage


class TrendAnalyzer:
    """趋势分析器"""
    
    def __init__(self, storage: GraphStorage):
        """
        初始化趋势分析器
        
        Args:
            storage: 图存储实例
        """
        self.storage = storage
    
    def calculate_trend(self, data_points: List[Dict[str, Any]], min_points: int = 5) -> TrendInfo:
        """
        计算趋势
        
        Args:
            data_points: 按时间排序的数据点列表，每个包含 timestamp 和 value
            min_points: 最少数据点数量
            
        Returns:
            TrendInfo: 趋势信息
        """
        if len(data_points) < min_points:
            return TrendInfo(
                direction="stable",
                rate=0.0,
                confidence=0.0,
                p_value=1.0
            )
        
        # 提取数值序列
        values = [float(p.get('value', 0)) for p in data_points]
        x = np.arange(len(values))
        
        # 线性回归
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)
        
        # 计算变化率
        early_avg = np.mean(values[:len(values)//3]) if len(values) >= 3 else values[0]
        recent_avg = np.mean(values[-len(values)//3:]) if len(values) >= 3 else values[-1]
        
        if early_avg > 0:
            rate = (recent_avg - early_avg) / early_avg
        else:
            rate = 0.0 if recent_avg == 0 else 1.0
        
        # 判定趋势方向
        # 使用斜率和统计显著性共同判断
        if p_value < 0.05:  # 统计显著
            if slope > 0.05:
                direction = "improving"
            elif slope < -0.05:
                direction = "declining"
            else:
                direction = "stable"
        else:
            direction = "stable"
        
        # 置信度 = R² 值
        confidence = r_value ** 2
        
        return TrendInfo(
            direction=direction,
            rate=float(rate),
            confidence=float(confidence),
            p_value=float(p_value)
        )
    
    async def analyze_multi_window_trend(
        self,
        child_id: str,
        dimension: str
    ) -> Dict[str, TrendInfo]:
        """
        多时间窗口趋势分析
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            
        Returns:
            包含 trend_7d, trend_30d, trend_90d 的字典
        """
        now = datetime.now(timezone.utc)
        
        # 获取各时间窗口的数据
        data_7d = await self._get_observations_in_window(child_id, dimension, now - timedelta(days=7), now)
        data_30d = await self._get_observations_in_window(child_id, dimension, now - timedelta(days=30), now)
        data_90d = await self._get_observations_in_window(child_id, dimension, now - timedelta(days=90), now)
        
        return {
            "trend_7d": self.calculate_trend(data_7d, min_points=3),
            "trend_30d": self.calculate_trend(data_30d, min_points=7),
            "trend_90d": self.calculate_trend(data_90d, min_points=15)
        }
    
    async def _get_observations_in_window(
        self,
        child_id: str,
        dimension: str,
        start_time: datetime,
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """
        获取时间窗口内的观察数据
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            start_time: 开始时间
            end_time: 结束时间
            
        Returns:
            观察数据列表
        """
        observations = await self.storage.get_observations(
            child_id=child_id,
            dimension=dimension,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat()
        )
        
        # 转换为标准格式
        return [
            {
                "timestamp": obs.get("timestamp"),
                "value": obs.get("value")
            }
            for obs in observations
        ]
