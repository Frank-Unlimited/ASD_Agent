"""
基础设施层 API 路由
提供 7 个基础设施服务的 REST API 端点
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.container import container

router = APIRouter(prefix="/api/infrastructure", tags=["infrastructure"])


# ============ 模块1: SQLite 数据管理模块 ============

class GetChildRequest(BaseModel):
    child_id: str

class SaveChildRequest(BaseModel):
    profile: Dict[str, Any]

class CreateSessionRequest(BaseModel):
    child_id: str
    game_id: str

class GetSessionRequest(BaseModel):
    session_id: str

class UpdateSessionRequest(BaseModel):
    session_id: str
    data: Dict[str, Any]

class SaveWeeklyPlanRequest(BaseModel):
    plan: Dict[str, Any]

class GetWeeklyPlanRequest(BaseModel):
    plan_id: str

class SaveObservationRequest(BaseModel):
    observation: Dict[str, Any]


@router.post("/sqlite/get_child")
async def sqlite_get_child(request: GetChildRequest):
    """获取孩子档案"""
    try:
        service = container.get('sqlite')
        result = await service.get_child(request.child_id)
        return {
            "success": True,
            "data": result,
            "message": "获取孩子档案成功" if result else "孩子档案不存在"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/sqlite/save_child")
async def sqlite_save_child(request: SaveChildRequest):
    """保存孩子档案"""
    try:
        service = container.get('sqlite')
        await service.save_child(request.profile)
        return {
            "success": True,
            "message": "保存孩子档案成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/sqlite/create_session")
async def sqlite_create_session(request: CreateSessionRequest):
    """创建干预会话"""
    try:
        service = container.get('sqlite')
        session_id = await service.create_session(request.child_id, request.game_id)
        return {
            "success": True,
            "data": {"session_id": session_id},
            "message": "创建会话成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


@router.post("/sqlite/get_session")
async def sqlite_get_session(request: GetSessionRequest):
    """获取会话信息"""
    try:
        service = container.get('sqlite')
        result = await service.get_session(request.session_id)
        return {
            "success": True,
            "data": result,
            "message": "获取会话信息成功" if result else "会话不存在"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/sqlite/update_session")
async def sqlite_update_session(request: UpdateSessionRequest):
    """更新会话信息"""
    try:
        service = container.get('sqlite')
        await service.update_session(request.session_id, request.data)
        return {
            "success": True,
            "message": "更新会话成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")


@router.post("/sqlite/save_weekly_plan")
async def sqlite_save_weekly_plan(request: SaveWeeklyPlanRequest):
    """保存周计划"""
    try:
        service = container.get('sqlite')
        plan_id = await service.save_weekly_plan(request.plan)
        return {
            "success": True,
            "data": {"plan_id": plan_id},
            "message": "保存周计划成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.post("/sqlite/get_weekly_plan")
async def sqlite_get_weekly_plan(request: GetWeeklyPlanRequest):
    """获取周计划"""
    try:
        service = container.get('sqlite')
        result = await service.get_weekly_plan(request.plan_id)
        return {
            "success": True,
            "data": result,
            "message": "获取周计划成功" if result else "周计划不存在"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


@router.post("/sqlite/save_observation")
async def sqlite_save_observation(request: SaveObservationRequest):
    """保存观察记录"""
    try:
        service = container.get('sqlite')
        obs_id = await service.save_observation(request.observation)
        return {
            "success": True,
            "data": {"observation_id": obs_id},
            "message": "保存观察记录成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存失败: {str(e)}")


@router.get("/sqlite/session_history/{child_id}")
async def sqlite_get_session_history(child_id: str, limit: int = 10):
    """获取会话历史"""
    try:
        service = container.get('sqlite')
        result = await service.get_session_history(child_id, limit)
        return {
            "success": True,
            "data": result,
            "message": f"获取到 {len(result)} 条会话历史"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


class DeleteChildRequest(BaseModel):
    child_id: str


@router.post("/sqlite/delete_child")
async def sqlite_delete_child(request: DeleteChildRequest):
    """删除孩子档案"""
    try:
        service = container.get('sqlite')
        await service.delete_child(request.child_id)
        return {
            "success": True,
            "message": "删除孩子档案成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")


# ============ 模块3: 知识库与 RAG 模块 ============

class SearchMethodologyRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchGamesRequest(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    top_k: int = 10

class SearchGamesByDimensionRequest(BaseModel):
    dimension: str
    difficulty: str
    top_k: int = 10

class SearchGamesByInterestRequest(BaseModel):
    interest: str
    top_k: int = 10

class SearchScaleRequest(BaseModel):
    query: str
    top_k: int = 5

class SearchCasesRequest(BaseModel):
    query: str
    top_k: int = 5

class GetGameRequest(BaseModel):
    game_id: str


@router.post("/rag/search_methodology")
async def rag_search_methodology(request: SearchMethodologyRequest):
    """检索方法论知识库"""
    try:
        service = container.get('rag')
        result = await service.search_methodology(request.query, request.top_k)
        return {
            "success": True,
            "data": result,
            "message": f"检索到 {len(result)} 条方法论"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/search_games")
async def rag_search_games(request: SearchGamesRequest):
    """检索游戏知识库"""
    try:
        service = container.get('rag')
        result = await service.search_games(request.query, request.filters, request.top_k)
        return {
            "success": True,
            "data": result,
            "message": f"检索到 {len(result)} 个游戏"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/search_games_by_dimension")
async def rag_search_games_by_dimension(request: SearchGamesByDimensionRequest):
    """按维度检索游戏"""
    try:
        service = container.get('rag')
        result = await service.search_games_by_dimension(request.dimension, request.difficulty, request.top_k)
        return {
            "success": True,
            "data": result,
            "message": f"检索到 {len(result)} 个游戏"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/search_games_by_interest")
async def rag_search_games_by_interest(request: SearchGamesByInterestRequest):
    """按兴趣检索游戏"""
    try:
        service = container.get('rag')
        result = await service.search_games_by_interest(request.interest, request.top_k)
        return {
            "success": True,
            "data": result,
            "message": f"检索到 {len(result)} 个游戏"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/search_scale")
async def rag_search_scale(request: SearchScaleRequest):
    """检索量表知识库"""
    try:
        service = container.get('rag')
        result = await service.search_scale(request.query, request.top_k)
        return {
            "success": True,
            "data": result,
            "message": f"检索到 {len(result)} 条量表"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/search_cases")
async def rag_search_cases(request: SearchCasesRequest):
    """检索案例知识库"""
    try:
        service = container.get('rag')
        result = await service.search_cases(request.query, request.top_k)
        return {
            "success": True,
            "data": result,
            "message": f"检索到 {len(result)} 个案例"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检索失败: {str(e)}")


@router.post("/rag/get_game")
async def rag_get_game(request: GetGameRequest):
    """获取游戏详情"""
    try:
        service = container.get('rag')
        result = await service.get_game(request.game_id)
        return {
            "success": True,
            "data": result,
            "message": "获取游戏详情成功" if result else "游戏不存在"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")


# ============ 模块4: AI 视频解析模块 ============

class AnalyzeVideoRequest(BaseModel):
    video_path: str
    context: Dict[str, Any]

class ExtractHighlightsRequest(BaseModel):
    video_path: str
    analysis_result: Dict[str, Any]


@router.post("/video_analysis/analyze_video")
async def video_analysis_analyze_video(request: AnalyzeVideoRequest):
    """分析视频"""
    try:
        service = container.get('video_analysis')
        result = await service.analyze_video(request.video_path, request.context)
        return {
            "success": True,
            "data": result,
            "message": "视频分析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")


@router.post("/video_analysis/extract_highlights")
async def video_analysis_extract_highlights(request: ExtractHighlightsRequest):
    """提取关键片段"""
    try:
        service = container.get('video_analysis')
        result = await service.extract_highlights(request.video_path, request.analysis_result)
        return {
            "success": True,
            "data": result,
            "message": f"提取到 {len(result)} 个关键片段"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取失败: {str(e)}")


# ============ 模块5: 语音处理模块 ============

class SpeechToTextRequest(BaseModel):
    audio_path: str

class TextToSpeechRequest(BaseModel):
    text: str


@router.post("/speech/speech_to_text")
async def speech_speech_to_text(request: SpeechToTextRequest):
    """语音转文字"""
    try:
        service = container.get('speech')
        result = await service.speech_to_text(request.audio_path)
        return {
            "success": True,
            "data": {"text": result},
            "message": "语音识别完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"识别失败: {str(e)}")


@router.post("/speech/text_to_speech")
async def speech_text_to_speech(request: TextToSpeechRequest):
    """文字转语音"""
    try:
        service = container.get('speech')
        result = await service.text_to_speech(request.text)
        return {
            "success": True,
            "data": {"audio_path": result},
            "message": "语音合成完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"合成失败: {str(e)}")


# ============ 模块6: 文档解析模块 ============

class ParseReportRequest(BaseModel):
    file_path: str
    file_type: str

class ParseScaleRequest(BaseModel):
    scale_data: Dict[str, Any]
    scale_type: str


@router.post("/document_parser/parse_report")
async def document_parser_parse_report(request: ParseReportRequest):
    """解析医院报告"""
    try:
        service = container.get('document_parser')
        result = await service.parse_report(request.file_path, request.file_type)
        return {
            "success": True,
            "data": result,
            "message": "报告解析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


@router.post("/document_parser/parse_scale")
async def document_parser_parse_scale(request: ParseScaleRequest):
    """解析量表数据"""
    try:
        service = container.get('document_parser')
        result = await service.parse_scale(request.scale_data, request.scale_type)
        return {
            "success": True,
            "data": result,
            "message": "量表解析完成"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"解析失败: {str(e)}")


# ============ 模块7: 文件上传模块 ============

@router.post("/file_upload/upload")
async def file_upload_upload(
    file: UploadFile = File(...),
    category: Optional[str] = None
):
    """
    上传文件到服务器本地
    
    参数:
        - file: 文件对象（必需）
        - category: 文件分类（可选: image/document/audio/video，不传则自动检测）
    
    返回:
        {
            "file_path": "完整文件路径",
            "filename": "生成的文件名",
            "original_filename": "原始文件名",
            "file_size": 文件大小（字节）,
            "category": "文件分类"
        }
    """
    try:
        service = container.get('file_upload')
        result = await service.upload_file(file, category)
        return {
            "success": True,
            "data": result,
            "message": "文件上传成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")
