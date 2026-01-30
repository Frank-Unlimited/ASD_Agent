"""
平台期检测器
"""
from typing import List, Dict, Any
import numpy as np

from ..models.output import PlateauInfo


class PlateauDetector:
    """平台期检测器"""
    
    def detect_plateau(
        self,
        data_points: List[Dict[str, Any]],
        window_days: int = 14,
        variance_threshold: float = 0.05
    ) -> PlateauInfo:
        """
        检测平台期
        
        定义：连续 N 天内数值变化率 < 阈值
        
        Args:
            data_points: 数据点列表
            window_days: 检测窗口（天）
            variance_threshold: 变化率阈值
            
        Returns:
            PlateauInfo: 平台期信息
        """
        if len(data_points) < window_days:
            return PlateauInfo(
                is_plateau=False,
                duration_days=0,
                suggestion="数据不足"
            )
        
        # 取最近 window_days 的数据
        recent_data = data_points[-window_days:]
        values = [float(p.get('value', 0)) for p in recent_data]
        
        # 计算变异系数 (CV = std / mean)
        mean_val = np.mean(values)
        if mean_val == 0:
            cv = 0
        else:
            cv = np.std(values) / mean_val
        
        is_plateau = cv < variance_threshold
        
        # 如果是平台期，回溯计算持续天数
        duration_days = 0
        if is_plateau:
            for i in range(len(data_points) - window_days, -1, -1):
                window = data_points[i:i + window_days]
                if len(window) < window_days:
                    break
                window_values = [float(p.get('value', 0)) for p in window]
                window_mean = np.mean(window_values)
                window_cv = np.std(window_values) / window_mean if window_mean > 0 else 0
                if window_cv < variance_threshold:
                    duration_days += 1
                else:
                    break
            duration_days += window_days
        
        suggestion = "考虑调整干预策略，尝试新的游戏类型" if is_plateau else "继续当前计划"
        
        return PlateauInfo(
            is_plateau=is_plateau,
            duration_days=duration_days,
            suggestion=suggestion
        )
