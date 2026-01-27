"""
Mock 服务实现
用于快速验证架构，返回假数据
"""
from services.mock.sqlite_service import MockSQLiteService
from services.mock.graphiti_service import MockGraphitiService
from services.mock.rag_service import MockRAGService
from services.mock.infrastructure_services import (
    MockVideoAnalysisService,
    MockSpeechService,
    MockDocumentParserService,
)
from services.mock.business_services import (
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

__all__ = [
    # Infrastructure (模块1-6)
    'MockSQLiteService',
    'MockGraphitiService',
    'MockRAGService',
    'MockVideoAnalysisService',
    'MockSpeechService',
    'MockDocumentParserService',
    
    # Business (模块7-16)
    'MockAssessmentService',
    'MockWeeklyPlanService',
    'MockGuidanceService',
    'MockObservationService',
    'MockVideoValidationService',
    'MockSummaryService',
    'MockMemoryUpdateService',
    'MockReassessmentService',
    'MockChatAssistantService',
    'MockVisualizationService',
]
