"""
数据模型定义
包括 State、数据库模型等
"""

# Profile models
from src.models.profile import (
    Gender,
    DiagnosisLevel,
    DevelopmentDimension,
    InterestCategory,
    InterestPoint,
    ParsedProfileData,
    ChildProfile,
    ProfileUpdateRequest,
    ProfileCreateResponse,
)

# Interest library
from src.models.interest_library import (
    StandardInterest,
    STANDARD_INTERESTS,
    get_interest_by_key,
    get_interests_by_category,
    search_interests,
    get_all_categories,
)

# Observation models
from src.models.observation import (
    ObservationType,
    ObservationDimension,
    ObservationSignificance,
    EmotionalState,
    StructuredObservationData,
    Observation,
    VoiceObservationRequest,
    TextObservationRequest,
    ObservationResponse,
    ObservationListResponse,
)

# Game models
from src.models.game import (
    GameStatus,
    TargetDimension,
    GameStep,
    GamePrecaution,
    GameGoal,
    GamePlan,
    ParentObservation,
    VideoAnalysisSummary,
    GameSession,
    GameCalendarItem,
    GameRecommendRequest,
    GameRecommendResponse,
    SessionStartRequest,
    SessionObservationRequest,
    SessionEndRequest,
    SessionResponse,
)

# Analysis models
from src.models.analysis import (
    TrendDirection,
    TimelineDataPoint,
    DimensionTimeline,
    InterestHeatmapData,
    InterventionEffect,
    ComprehensiveAnalysis,
    TimelineRequest,
    HeatmapRequest,
    InterventionEffectRequest,
    AnalysisResponse,
)

# Report models
from src.models.report import (
    ReportType,
    ReportFormat,
    ChartType,
    ChartData,
    DevelopmentDimensionReport,
    InterventionSummary,
    ObservationSummary,
    MedicalReport,
    ParentReport,
    ReportGenerateRequest,
    ReportResponse,
    ReportDownloadRequest,
    ReportListResponse,
)

__all__ = [
    # Profile
    "Gender",
    "DiagnosisLevel",
    "DevelopmentDimension",
    "InterestPoint",
    "ParsedProfileData",
    "ChildProfile",
    "ProfileUpdateRequest",
    "ProfileCreateResponse",
    # Interest library
    "InterestCategory",
    "StandardInterest",
    "STANDARD_INTERESTS",
    "get_interest_by_key",
    "get_interests_by_category",
    "search_interests",
    "get_all_categories",
    # Observation
    "ObservationType",
    "ObservationDimension",
    "ObservationSignificance",
    "EmotionalState",
    "StructuredObservationData",
    "Observation",
    "VoiceObservationRequest",
    "TextObservationRequest",
    "ObservationResponse",
    "ObservationListResponse",
    # Game
    "GameStatus",
    "TargetDimension",
    "GameStep",
    "GamePrecaution",
    "GameGoal",
    "GamePlan",
    "ParentObservation",
    "VideoAnalysisSummary",
    "GameSession",
    "GameCalendarItem",
    "GameRecommendRequest",
    "GameRecommendResponse",
    "SessionStartRequest",
    "SessionObservationRequest",
    "SessionEndRequest",
    "SessionResponse",
    # Analysis
    "TrendDirection",
    "TimelineDataPoint",
    "DimensionTimeline",
    "InterestHeatmapData",
    "InterventionEffect",
    "ComprehensiveAnalysis",
    "TimelineRequest",
    "HeatmapRequest",
    "InterventionEffectRequest",
    "AnalysisResponse",
    # Report
    "ReportType",
    "ReportFormat",
    "ChartType",
    "ChartData",
    "DevelopmentDimensionReport",
    "InterventionSummary",
    "ObservationSummary",
    "MedicalReport",
    "ParentReport",
    "ReportGenerateRequest",
    "ReportResponse",
    "ReportDownloadRequest",
    "ReportListResponse",
]
