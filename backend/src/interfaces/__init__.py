"""
所有模块接口定义
按照设计文档，定义17个模块的接口
"""
from src.interfaces.base import BaseService
from src.interfaces.infrastructure import (
    ISQLiteService,
    IGraphitiService,
    IKnowledgeRAGService,
    IVideoAnalysisService,
    ISpeechService,
    IDocumentParserService,
)
from src.interfaces.business import (
    IAssessmentService,
    IWeeklyPlanService,
    IGuidanceService,
    IObservationService,
    IVideoValidationService,
    ISummaryService,
    IMemoryUpdateService,
    IReassessmentService,
    IChatAssistantService,
    IVisualizationService,
)

__all__ = [
    # Base
    'BaseService',
    
    # Infrastructure (模块1-6)
    'ISQLiteService',
    'IGraphitiService',
    'IKnowledgeRAGService',
    'IVideoAnalysisService',
    'ISpeechService',
    'IDocumentParserService',
    
    # Business (模块7-16)
    'IAssessmentService',
    'IWeeklyPlanService',
    'IGuidanceService',
    'IObservationService',
    'IVideoValidationService',
    'ISummaryService',
    'IMemoryUpdateService',
    'IReassessmentService',
    'IChatAssistantService',
    'IVisualizationService',
]
