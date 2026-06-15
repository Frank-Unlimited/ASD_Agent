"""
行为观察服务模块

公开两个核心类：
    - ObservationService        ：传统观察记录服务（文字 / 语音 / 快速按钮）
    - ObservationServiceManager ：游戏实时记录系统的整合入口
                                  （事件聚合 + 快照调度 + AI 推断）
"""
from .service import ObservationService
from .service_manager import ObservationServiceManager

__all__ = ["ObservationService", "ObservationServiceManager"]
