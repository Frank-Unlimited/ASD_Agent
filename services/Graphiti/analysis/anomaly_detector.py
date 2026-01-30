"""
异常波动检测器
"""
from typing import List, Dict, Any, Literal
import numpy as np

from ..models.output import AnomalyInfo


class AnomalyDetector:
    """异常波动检测器"""
    
    def detect_anomaly(
        self,
        data_points: List[Dict[str, Any]],
        std_threshold: float = 2.0
    ) -> AnomalyInfo:
        """
        检测异常波动
        
        定义：数值偏离均值超过 N 个标准差
        
        Args:
            data_points: 数据点列表
            std_threshold: 标准差阈值
            
        Returns:
            AnomalyInfo: 异常信息
        """
        if len(data_points) < 5:
            return AnomalyInfo(
                has_anomaly=False,
                anomaly_type="none",
                anomaly_value=0.0,
                anomaly_date="",
                interpretation="数据不足"
            )
        
        values = [float(p.get('value', 0)) for p in data_points]
        mean_val = np.mean(values)
        std_val = np.std(values)
        
        if std_val == 0:
            return AnomalyInfo(
                has_anomaly=False,
                anomaly_type="none",
                anomaly_value=0.0,
                anomaly_date="",
                interpretation="数据无波动"
            )
        
        # 检查最近的数据点
        recent_point = data_points[-1]
        recent_value = float(recent_point.get('value', 0))
        z_score = (recent_value - mean_val) / std_val
        
        if abs(z_score) > std_threshold:
            anomaly_type: Literal["spike", "drop", "none"] = "spike" if z_score > 0 else "drop"
            interpretation = (
                "可能是突破性进步，建议关注" if anomaly_type == "spike"
                else "可能是状态波动或数据问题，建议核实"
            )
            
            return AnomalyInfo(
                has_anomaly=True,
                anomaly_type=anomaly_type,
                anomaly_value=recent_value,
                anomaly_date=recent_point.get('timestamp', ''),
                interpretation=interpretation
            )
        
        return AnomalyInfo(
            has_anomaly=False,
            anomaly_type="none",
            anomaly_value=0.0,
            anomaly_date="",
            interpretation="无异常"
        )
