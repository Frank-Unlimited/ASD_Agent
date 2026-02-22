"""
业务逻辑层 API 路由
提供 10 个业务逻辑服务的 REST API 端点
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.container import container

router = APIRouter(prefix="/api/business", tags=["business"])


# ============ 模块7: 初始评估模块 ============

class BuildPortraitRequest(BaseModel):
    parsed_data: Dict[str, Any]

class CreateObservationFrameworkRequest(BaseModel):
    portrait: Dict[str, Any]


@router.post("/assessment/build_portrait")
async def assessment_build_portrait(request: BuildPortraitRequest):
    """构建孩子画像"""
    try:
        service = container.get('assessment')
        result = await service.build_portrait(request.parsed_data)
        return {
            "success": True,
            "data": result,
            "message": "孩子画像构建完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"构建失败: {str(e)}")


@router.post("/assessment/create_observation_framework")
async def assessment_create_observation_framework(request: CreateObservationFrameworkRequest):
    """创建观察框架"""
    try:
        service = container.get('assessment')
        result = await service.create_observation_framework(request.portrait)
        return {
            "success": True,
            "data": result,
            "message": "观察框架创建完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


# ============ 模块8: 周计划推荐模块 ============

class GenerateWeeklyPlanRequest(BaseModel):
    child_id: str
    child_profile: Dict[str, Any]
    current_context: Dict[str, Any]
    last_week_performance: Optional[Dict[str, Any]] = None

class CalculatePriorityDimensionsRequest(BaseModel):
    metrics: Dict[str, Any]
    trends: Dict[str, Any]


@router.post("/weekly_plan/generate")
async def weekly_plan_generate(request: GenerateWeeklyPlanRequest):
    """生成周计划"""
    try:
        service = container.get('weekly_plan')
        result = await service.generate_weekly_plan(
            request.child_id,
            request.child_profile,
            request.current_context,
            request.last_week_performance
        )
        return {
            "success": True,
            "data": result,
            "message": "周计划生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/weekly_plan/calculate_priority_dimensions")
async def weekly_plan_calculate_priority(request: CalculatePriorityDimensionsRequest):
    """计算优先维度"""
    try:
        service = container.get('weekly_plan')
        result = await service.calculate_priority_dimensions(request.metrics, request.trends)
        return {
            "success": True,
            "data": result,
            "message": f"计算出 {len(result)} 个优先维度"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算失败: {str(e)}")


# ============ 模块9: 实时指引模块 ============

class GetStepGuidanceRequest(BaseModel):
    game_id: str
    step: int
    context: Dict[str, Any]

class RecommendPhrasesRequest(BaseModel):
    situation: str
    child_profile: Dict[str, Any]


@router.post("/guidance/get_step_guidance")
async def guidance_get_step_guidance(request: GetStepGuidanceRequest):
    """获取步骤指引"""
    try:
        service = container.get('guidance')
        result = await service.get_step_guidance(request.game_id, request.step, request.context)
        return {
            "success": True,
            "data": result,
            "message": "步骤指引获取完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/guidance/recommend_phrases")
async def guidance_recommend_phrases(request: RecommendPhrasesRequest):
    """推荐话术"""
    try:
        service = container.get('guidance')
        result = await service.recommend_phrases(request.situation, request.child_profile)
        return {
            "success": True,
            "data": result,
            "message": "话术推荐完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


# ============ 模块10: 观察捕获模块 ============

class CaptureQuickObservationRequest(BaseModel):
    session_id: str
    observation_type: str
    timestamp: str

class CaptureVoiceObservationRequest(BaseModel):
    session_id: str
    audio_path: str

class StructureObservationRequest(BaseModel):
    raw_text: str
    context: Dict[str, Any]


@router.post("/observation/capture_quick")
async def observation_capture_quick(request: CaptureQuickObservationRequest):
    """捕获快捷观察"""
    try:
        service = container.get('observation')
        result = await service.capture_quick_observation(
            request.session_id,
            request.observation_type,
            request.timestamp
        )
        return {
            "success": True,
            "data": result,
            "message": "快捷观察捕获完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"捕获失败: {str(e)}")


@router.post("/observation/capture_voice")
async def observation_capture_voice(request: CaptureVoiceObservationRequest):
    """捕获语音观察"""
    try:
        service = container.get('observation')
        result = await service.capture_voice_observation(request.session_id, request.audio_path)
        return {
            "success": True,
            "data": result,
            "message": "语音观察捕获完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"捕获失败: {str(e)}")


@router.post("/observation/structure")
async def observation_structure(request: StructureObservationRequest):
    """结构化观察内容"""
    try:
        service = container.get('observation')
        result = await service.structure_observation(request.raw_text, request.context)
        return {
            "success": True,
            "data": result,
            "message": "观察内容结构化完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结构化失败: {str(e)}")


# ============ 模块11: 视频分析与验证模块 ============

class AnalyzeAndValidateRequest(BaseModel):
    session_id: str
    video_path: str
    quick_observations: List[Dict[str, Any]]

class CrossValidateRequest(BaseModel):
    quick_observations: List[Dict[str, Any]]
    video_analysis: Dict[str, Any]


@router.post("/video_validation/analyze_and_validate")
async def video_validation_analyze_and_validate(request: AnalyzeAndValidateRequest):
    """分析视频并验证观察"""
    try:
        service = container.get('video_validation')
        result = await service.analyze_and_validate(
            request.session_id,
            request.video_path,
            request.quick_observations
        )
        return {
            "success": True,
            "data": result,
            "message": "视频分析与验证完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/video_validation/cross_validate")
async def video_validation_cross_validate(request: CrossValidateRequest):
    """交叉验证"""
    try:
        service = container.get('video_validation')
        result = await service.cross_validate(request.quick_observations, request.video_analysis)
        return {
            "success": True,
            "data": result,
            "message": "交叉验证完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"验证失败: {str(e)}")


# ============ 模块12: 总结生成模块 ============

class GeneratePreliminarySummaryRequest(BaseModel):
    session_id: str
    session_data: Dict[str, Any]
    historical_data: Dict[str, Any]

class GenerateFeedbackFormRequest(BaseModel):
    preliminary_summary: Dict[str, Any]

class GenerateFinalSummaryRequest(BaseModel):
    session_id: str
    all_data: Dict[str, Any]
    parent_feedback: Dict[str, Any]


@router.post("/summary/generate_preliminary")
async def summary_generate_preliminary(request: GeneratePreliminarySummaryRequest):
    """生成初步总结"""
    try:
        service = container.get('summary')
        result = await service.generate_preliminary_summary(
            request.session_id,
            request.session_data,
            request.historical_data
        )
        return {
            "success": True,
            "data": result,
            "message": "初步总结生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/summary/generate_feedback_form")
async def summary_generate_feedback_form(request: GenerateFeedbackFormRequest):
    """生成反馈表"""
    try:
        service = container.get('summary')
        result = await service.generate_feedback_form(request.preliminary_summary)
        return {
            "success": True,
            "data": result,
            "message": "反馈表生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/summary/generate_final")
async def summary_generate_final(request: GenerateFinalSummaryRequest):
    """生成最终总结"""
    try:
        service = container.get('summary')
        result = await service.generate_final_summary(
            request.session_id,
            request.all_data,
            request.parent_feedback
        )
        return {
            "success": True,
            "data": result,
            "message": "最终总结生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


# ============ 模块13: 记忆更新模块 ============

class UpdateMemoryRequest(BaseModel):
    child_id: str
    session_data: Dict[str, Any]

class RefreshContextRequest(BaseModel):
    child_id: str


@router.post("/memory_update/update")
async def memory_update_update(request: UpdateMemoryRequest):
    """更新记忆网络"""
    try:
        service = container.get('memory_update')
        result = await service.update_memory(request.child_id, request.session_data)
        return {
            "success": True,
            "data": result,
            "message": "记忆网络更新完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/memory_update/refresh_context")
async def memory_update_refresh_context(request: RefreshContextRequest):
    """刷新上下文"""
    try:
        service = container.get('memory_update')
        result = await service.refresh_context(request.child_id)
        return {
            "success": True,
            "data": result,
            "message": "上下文刷新完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新失败: {str(e)}")


# ============ 模块14: 再评估模块 ============

class ReassessChildRequest(BaseModel):
    child_id: str
    session_data: Dict[str, Any]
    current_context: Dict[str, Any]

class UpdatePortraitRequest(BaseModel):
    child_id: str
    reassessment_result: Dict[str, Any]

class CheckAdjustmentNeededRequest(BaseModel):
    reassessment_result: Dict[str, Any]


@router.post("/reassessment/reassess_child")
async def reassessment_reassess_child(request: ReassessChildRequest):
    """重新评估孩子"""
    try:
        service = container.get('reassessment')
        result = await service.reassess_child(
            request.child_id,
            request.session_data,
            request.current_context
        )
        return {
            "success": True,
            "data": result,
            "message": "再评估完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")


@router.post("/reassessment/update_portrait")
async def reassessment_update_portrait(request: UpdatePortraitRequest):
    """更新画像"""
    try:
        service = container.get('reassessment')
        result = await service.update_portrait(request.child_id, request.reassessment_result)
        return {
            "success": True,
            "data": result,
            "message": "画像更新完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/reassessment/check_adjustment_needed")
async def reassessment_check_adjustment_needed(request: CheckAdjustmentNeededRequest):
    """检查是否需要调整计划"""
    try:
        service = container.get('reassessment')
        result = await service.check_adjustment_needed(request.reassessment_result)
        return {
            "success": True,
            "data": {"adjustment_needed": result},
            "message": "检查完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查失败: {str(e)}")


# ============ 模块15: 对话助手模块 ============

class ChatRequest(BaseModel):
    child_id: str
    user_message: str
    conversation_history: List[Dict[str, Any]]

class RouteQueryRequest(BaseModel):
    query: str


@router.post("/chat_assistant/chat")
async def chat_assistant_chat(request: ChatRequest):
    """对话"""
    try:
        service = container.get('chat_assistant')
        result = await service.chat(
            request.child_id,
            request.user_message,
            request.conversation_history
        )
        return {
            "success": True,
            "data": result,
            "message": "对话完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对话失败: {str(e)}")


@router.post("/chat_assistant/route_query")
async def chat_assistant_route_query(request: RouteQueryRequest):
    """路由查询"""
    try:
        service = container.get('chat_assistant')
        result = await service.route_query(request.query)
        return {
            "success": True,
            "data": {"query_type": result},
            "message": "查询路由完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"路由失败: {str(e)}")


# ============ 模块16: 可视化与报告模块 ============

class GenerateRadarChartRequest(BaseModel):
    child_id: str
    metrics: Dict[str, Any]

class GenerateTimelineRequest(BaseModel):
    child_id: str
    milestones: List[Dict[str, Any]]

class GenerateTrendChartRequest(BaseModel):
    child_id: str
    dimension: str
    time_range: str

class GenerateParentReportRequest(BaseModel):
    child_id: str
    time_range: str

class GenerateMedicalReportRequest(BaseModel):
    child_id: str
    time_range: str


@router.post("/visualization/generate_radar_chart")
async def visualization_generate_radar_chart(request: GenerateRadarChartRequest):
    """生成雷达图数据"""
    try:
        service = container.get('visualization')
        result = await service.generate_radar_chart(request.child_id, request.metrics)
        return {
            "success": True,
            "data": result,
            "message": "雷达图数据生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/visualization/generate_timeline")
async def visualization_generate_timeline(request: GenerateTimelineRequest):
    """生成时间线数据"""
    try:
        service = container.get('visualization')
        result = await service.generate_timeline(request.child_id, request.milestones)
        return {
            "success": True,
            "data": result,
            "message": "时间线数据生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/visualization/generate_trend_chart")
async def visualization_generate_trend_chart(request: GenerateTrendChartRequest):
    """生成趋势图数据"""
    try:
        service = container.get('visualization')
        result = await service.generate_trend_chart(
            request.child_id,
            request.dimension,
            request.time_range
        )
        return {
            "success": True,
            "data": result,
            "message": "趋势图数据生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/visualization/generate_parent_report")
async def visualization_generate_parent_report(request: GenerateParentReportRequest):
    """生成家长版报告"""
    try:
        service = container.get('visualization')
        result = await service.generate_parent_report(request.child_id, request.time_range)
        return {
            "success": True,
            "data": {"report_path": result},
            "message": "家长版报告生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")


@router.post("/visualization/generate_medical_report")
async def visualization_generate_medical_report(request: GenerateMedicalReportRequest):
    """生成医生版报告"""
    try:
        service = container.get('visualization')
        result = await service.generate_medical_report(request.child_id, request.time_range)
        return {
            "success": True,
            "data": {"report_path": result},
            "message": "医生版报告生成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
