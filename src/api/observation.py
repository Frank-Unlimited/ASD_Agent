"""
观察记录 API

API层负责：
1. 使用FileUploadService上传语音文件
2. 调用ObservationService处理业务逻辑
3. 返回响应
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Body

from src.models.observation import (
    VoiceObservationRequest,
    TextObservationRequest,
    ObservationResponse,
    ObservationListResponse,
)
from src.container import container

router = APIRouter(prefix="/api/observation", tags=["观察记录"])


@router.post("/voice", response_model=ObservationResponse)
async def record_voice_observation(
    child_id: str = Body(..., description="孩子ID"),
    file: UploadFile = File(..., description="语音文件"),
    session_id: str = Body(None, description="关联的游戏会话ID（可选）"),
    game_id: str = Body(None, description="关联的游戏ID（可选）"),
    parent_notes: str = Body(None, description="家长补充备注（可选）"),
):
    """
    记录语音观察

    流程：
    1. 使用FileUploadService保存语音文件
    2. 调用ObservationService处理：
       - 语音转文字
       - LLM提取结构化数据
       - 保存到SQLite和Graphiti
    3. 返回观察记录

    注意：语音文件需要是PCM格式，16000Hz采样率
    """
    try:
        # 1. 使用FileUploadService上传语音文件
        file_upload_service = container.get('file_upload')
        upload_result = await file_upload_service.upload_file(
            file=file,
            category="audio"  # 语音文件归类为audio
        )

        print(f"[API] 语音文件已上传: {upload_result['file_path']}")

        # 2. 调用ObservationService处理
        observation_service = container.get('observation')
        request = VoiceObservationRequest(
            child_id=child_id,
            audio_file_path=upload_result['file_path'],
            session_id=session_id,
            game_id=game_id,
            parent_notes=parent_notes
        )
        result = await observation_service.record_voice_observation(request)

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音观察记录失败: {str(e)}")


@router.post("/text", response_model=ObservationResponse)
async def record_text_observation(
    request: TextObservationRequest
):
    """
    记录文字观察

    流程：
    1. 调用ObservationService处理：
       - LLM提取结构化数据
       - 保存到SQLite和Graphiti
    2. 返回观察记录
    """
    try:
        observation_service = container.get('observation')
        result = await observation_service.record_text_observation(request)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"文字观察记录失败: {str(e)}")


@router.get("/{child_id}/history", response_model=ObservationListResponse)
async def get_observation_history(
    child_id: str,
    limit: int = 50,
    offset: int = 0
):
    """
    获取观察历史记录

    Args:
        child_id: 孩子ID
        limit: 返回数量限制（默认50）
        offset: 偏移量（默认0）

    Returns:
        ObservationListResponse: 观察记录列表
    """
    try:
        observation_service = container.get('observation')
        result = await observation_service.get_observation_history(
            child_id=child_id,
            limit=limit,
            offset=offset
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取观察历史失败: {str(e)}")
