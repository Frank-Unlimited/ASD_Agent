"""
Graphiti 配置管理
"""
from typing import Optional
from pydantic import BaseModel


class GraphitiConfig(BaseModel):
    """Graphiti 配置"""
    
    # Neo4j 连接配置
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    
    # 趋势分析配置
    trend_min_points_7d: int = 3      # 7天趋势最少数据点
    trend_min_points_30d: int = 7     # 30天趋势最少数据点
    trend_min_points_90d: int = 15    # 90天趋势最少数据点
    
    # 平台期检测配置
    plateau_window_days: int = 14     # 平台期检测窗口（天）
    plateau_variance_threshold: float = 0.05  # 变化率阈值
    
    # 异常检测配置
    anomaly_std_threshold: float = 2.0  # 标准差阈值
    
    # 关联分析配置
    correlation_min_points: int = 10  # 最少数据点
    correlation_threshold: float = 0.3  # 相关性阈值
    correlation_max_lag: int = 14     # 最大时滞天数
    
    class Config:
        env_prefix = "GRAPHITI_"
