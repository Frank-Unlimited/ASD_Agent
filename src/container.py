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
        try:
            from services.real.sqlite_adapter import SQLiteServiceAdapter
            container.register('sqlite', SQLiteServiceAdapter())
            print("[Container] 使用真实 SQLite 服务")
        except Exception as e:
            print(f"[Container] 加载真实 SQLite 服务失败: {e}，使用 Mock")
            container.register('sqlite', MockSQLiteService())
    else:
        container.register('sqlite', MockSQLiteService())
    
    if settings.use_real_graphiti:
        try:
            from services.Graphiti.adapters import GraphitiServiceAdapter
            container.register('graphiti', GraphitiServiceAdapter())
            print("[Container] 使用真实 Graphiti 服务")
        except Exception as e:
            print(f"[Container] 加载真实 Graphiti 服务失败: {e}，使用 Mock")
            container.register('graphiti', MockGraphitiService())
    else:
        container.register('graphiti', MockGraphitiService())
    
    if settings.use_real_rag:
        # TODO: 实现真实服务后替换
        pass
    else:
        container.register('rag', MockRAGService())
    
    if settings.use_real_video_analysis:
        try:
            from services.real.multimodal_adapter import MultimodalVideoAnalysisService
            container.register('video_analysis', MultimodalVideoAnalysisService())
            print("[Container] 使用真实视频分析服务")
        except Exception as e:
            print(f"[Container] 加载真实视频分析服务失败: {e}，使用 Mock")
            container.register('video_analysis', MockVideoAnalysisService())
    else:
        container.register('video_analysis', MockVideoAnalysisService())
    
    if settings.use_real_speech:
        try:
            from services.real.speech_adapter import AliyunSpeechService
            container.register('speech', AliyunSpeechService())
            print("[Container] 使用真实语音服务")
        except Exception as e:
            print(f"[Container] 加载真实语音服务失败: {e}，使用 Mock")
            container.register('speech', MockSpeechService())
    else:
        container.register('speech', MockSpeechService())
    
    if settings.use_real_document_parser:
        try:
            from services.real.multimodal_adapter import MultimodalDocumentParserService
            container.register('document_parser', MultimodalDocumentParserService())
            print("[Container] 使用真实文档解析服务")
        except Exception as e:
            print(f"[Container] 加载真实文档解析服务失败: {e}，使用 Mock")
            container.register('document_parser', MockDocumentParserService())
    else:
        container.register('document_parser', MockDocumentParserService())
    
    # 业务逻辑层（模块7-16）
    if settings.use_real_assessment:
        try:
            from services.real.assessment_service import RealAssessmentService
            container.register('assessment', RealAssessmentService())
            print("[Container] 使用真实评估服务（基于 LLM）")
        except Exception as e:
            print(f"[Container] 加载真实评估服务失败: {e}，使用 Mock")
            container.register('assessment', MockAssessmentService())
    else:
        container.register('assessment', MockAssessmentService())
    
    container.register('weekly_plan', MockWeeklyPlanService())
    container.register('guidance', MockGuidanceService())
    container.register('observation', MockObservationService())
    container.register('video_validation', MockVideoValidationService())
    container.register('summary', MockSummaryService())
    container.register('memory_update', MockMemoryUpdateService())
    container.register('reassessment', MockReassessmentService())
    
    if settings.use_real_chat:
        try:
            from services.real.chat_service import RealChatAssistantService
            container.register('chat_assistant', RealChatAssistantService())
            print("[Container] 使用真实对话助手（基于 LLM）")
        except Exception as e:
            print(f"[Container] 加载真实对话助手失败: {e}，使用 Mock")
            container.register('chat_assistant', MockChatAssistantService())
    else:
        container.register('chat_assistant', MockChatAssistantService())
    
    container.register('visualization', MockVisualizationService())
    
    # 文件上传服务（始终使用真实实现）
    try:
        from services.FileUpload.service import FileUploadService
        container.register('file_upload', FileUploadService())
        print("[Container] 文件上传服务已注册")
    except Exception as e:
        print(f"[Container] 文件上传服务注册失败: {e}")
    
    # LLM 服务（根据配置动态加载）
    try:
        from services.real.llm_service import get_llm_service
        llm = get_llm_service()
        container.register('llm', llm)
        print(f"[Container] LLM 服务已注册: {settings.llm_model}")
    except Exception as e:
        print(f"[Container] LLM 服务注册失败: {e}")
        print(f"[Container] 请检查 LLM_API_KEY 是否配置")
    
    print("[Container] 所有服务已注册（当前使用 Mock 实现）")
