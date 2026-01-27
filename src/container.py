"""
依赖注入容器
管理所有服务实例，支持 Mock/Real 切换
"""
from typing import Dict, Any, Type
from src.config import settings


class ServiceContainer:
    """服务容器"""
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
    
    def register(self, name: str, service: Any) -> None:
        """注册服务"""
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """获取服务"""
        if name not in self._services:
            raise KeyError(f"Service '{name}' not found in container")
        return self._services[name]
    
    def has(self, name: str) -> bool:
        """检查服务是否存在"""
        return name in self._services


# 全局容器实例
container = ServiceContainer()


def init_services():
    """
    初始化所有服务
    根据配置决定使用 Mock 还是 Real 实现
    """
    from services.mock import (
        MockSQLiteService,
        MockGraphitiService,
        MockRAGService,
        MockVideoAnalysisService,
        MockSpeechService,
        MockDocumentParserService,
        MockAssessmentService,
        MockWeeklyPlanService,
        MockGuidanceService,
        MockObservationService,
        MockVideoValidationService,
        MockSummaryService,
        MockMemoryUpdateService,
        MockReassessmentService,
        MockChatAssistantService,
        MockVisualizationService,
    )
    
    # 基础设施层（模块1-6）
    if settings.use_real_sqlite:
        # TODO: 实现真实服务后替换
        # from services.real.sqlite_service import RealSQLiteService
        # container.register('sqlite', RealSQLiteService())
        pass
    else:
        container.register('sqlite', MockSQLiteService())
    
    if settings.use_real_graphiti:
        # TODO: 实现真实服务后替换
        pass
    else:
        container.register('graphiti', MockGraphitiService())
    
    if settings.use_real_rag:
        # TODO: 实现真实服务后替换
        pass
    else:
        container.register('rag', MockRAGService())
    
    if settings.use_real_video_analysis:
        from services.Multimodal_Understanding.adapters import MultimodalVideoAnalysisService
        container.register('video_analysis', MultimodalVideoAnalysisService())
    else:
        container.register('video_analysis', MockVideoAnalysisService())
    
    if settings.use_real_speech:
        # TODO: 实现真实服务后替换
        pass
    else:
        container.register('speech', MockSpeechService())
    
    if settings.use_real_document_parser:
        from services.Multimodal_Understanding.adapters import MultimodalDocumentParserService
        container.register('document_parser', MultimodalDocumentParserService())
    else:
        container.register('document_parser', MockDocumentParserService())
    
    # 业务逻辑层（模块7-16）- 目前都使用 Mock
    container.register('assessment', MockAssessmentService())
    container.register('weekly_plan', MockWeeklyPlanService())
    container.register('guidance', MockGuidanceService())
    container.register('observation', MockObservationService())
    container.register('video_validation', MockVideoValidationService())
    container.register('summary', MockSummaryService())
    container.register('memory_update', MockMemoryUpdateService())
    container.register('reassessment', MockReassessmentService())
    container.register('chat_assistant', MockChatAssistantService())
    container.register('visualization', MockVisualizationService())
    
    print("[Container] 所有服务已注册（当前使用 Mock 实现）")
