"""
游戏推荐和管理 API

API层负责：
1. 调用GameRecommenderService推荐游戏
2. 调用GameSessionService管理游戏会话
3. 使用FileUploadService上传视频文件
4. 返回响应
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Body
from typing import Optional

from src.models.game import (
    GameRecommendRequest,
    GameRecommendResponse,
    GamePlan,
    SessionStartRequest,
    SessionObservationRequest,
    SessionEndRequest,
    SessionResponse,
    GameSummaryRequest,
    GameSummaryResponse,
)
from src.container import container

router = APIRouter(prefix="/api/game", tags=["游戏推荐和管理"])


@router.post("/recommend", response_model=GameRecommendResponse)
async def recommend_game(
    request: GameRecommendRequest
):
    """
    推荐游戏

    核心流程：
    1. 评估孩子当前状态（从Graphiti获取画像和最近观察）
    2. 分析趋势（各维度的发展趋势）
    3. 识别目标维度和兴趣点
    4. 使用LLM生成详细的游戏方案（步骤、注意事项、目标）
    5. 保存到SQLite
    6. 返回游戏方案和推荐理由

    返回的游戏方案包含：
    - 详细的步骤（每一步做什么、家长如何引导、期待孩子的反应）
    - 注意事项（安全、情绪、环境等）
    - 游戏目标和成功标准
    - 所需材料和环境布置
    """
    try:
        game_recommender = container.get('game_recommender')
        
        # 初始化 Memory 服务（如果还没有）
        if game_recommender.memory_service is None:
            from services.Memory.service import get_memory_service
            game_recommender.memory_service = await get_memory_service()
            print("[API] Memory 服务已初始化")
        
        result = await game_recommender.recommend_game(request)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"游戏推荐失败: {str(e)}")


@router.get("/calendar/{child_id}")
async def get_game_calendar(child_id: str):
    """
    获取游戏日历

    返回该孩子的所有游戏方案，包括：
    - 已推荐但未实施的游戏（状态：recommended）
    - 已安排待实施的游戏（状态：scheduled）
    - 进行中的游戏（状态：in_progress）
    - 已完成的游戏（状态：completed）
    """
    try:
        # TODO: 实现游戏日历查询
        # 从SQLite查询该孩子的所有游戏方案
        return {
            "child_id": child_id,
            "games": [],
            "message": "功能开发中"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取游戏日历失败: {str(e)}")


@router.patch("/{game_id}/status")
async def update_game_status(
    game_id: str,
    status: str = Body(..., description="新状态（scheduled/in_progress/completed/cancelled）"),
    scheduled_date: Optional[str] = Body(None, description="计划实施日期（YYYY-MM-DD HH:MM:SS）")
):
    """
    更新游戏状态

    用途：
    1. 将推荐的游戏标记为"待实施"（scheduled）
    2. 将游戏标记为"已取消"（cancelled）
    3. 更新计划实施日期
    """
    try:
        # TODO: 实现游戏状态更新
        return {
            "game_id": game_id,
            "status": status,
            "message": "游戏状态已更新"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新游戏状态失败: {str(e)}")


# ============ 游戏会话管理 ============

@router.post("/session/start", response_model=SessionResponse)
async def start_game_session(
    request: SessionStartRequest
):
    """
    开始游戏会话

    当家长准备实施某个游戏时调用此接口。
    系统会：
    1. 创建会话记录
    2. 更新游戏状态为IN_PROGRESS
    3. 返回session_id供后续使用
    """
    try:
        game_session = container.get('game_session')
        result = await game_session.start_session(request)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"开始游戏会话失败: {str(e)}")


@router.post("/session/{session_id}/observation")
async def add_session_observation(
    session_id: str,
    request: SessionObservationRequest
):
    """
    添加会话观察记录

    在游戏进行过程中，家长可以随时添加观察记录。
    记录内容包括：
    - 观察内容
    - 孩子的行为表现
    - 家长的感受
    """
    try:
        game_session = container.get('game_session')
        result = await game_session.add_observation(session_id, request)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加观察记录失败: {str(e)}")


@router.post("/session/end", response_model=SessionResponse)
async def end_game_session(
    session_id: str = Body(..., description="会话ID"),
    video: Optional[UploadFile] = File(None, description="游戏视频（可选）"),
    child_engagement_score: Optional[float] = Body(None, description="孩子参与度评分（0-10）"),
    goal_achievement_score: Optional[float] = Body(None, description="目标达成度评分（0-10）"),
    parent_satisfaction_score: Optional[float] = Body(None, description="家长满意度评分（0-10）"),
    notes: Optional[str] = Body(None, description="备注")
):
    """
    结束游戏会话

    当游戏结束时调用此接口。
    系统会：
    1. 记录结束时间和评分
    2. 如果上传了视频，进行AI分析
    3. 保存会话记录到SQLite
    4. 保存到Graphiti知识图谱（用于后续趋势分析）
    5. 返回会话总结
    """
    try:
        # 如果有视频，先上传
        video_path = None
        if video:
            file_upload_service = container.get('file_upload')
            upload_result = await file_upload_service.upload_file(
                file=video,
                category="video"
            )
            video_path = upload_result['file_path']
            print(f"[API] 游戏视频已上传: {video_path}")

        # 结束会话
        game_session = container.get('game_session')
        request_obj = SessionEndRequest(
            session_id=session_id,
            video_path=video_path,
            child_engagement_score=child_engagement_score,
            goal_achievement_score=goal_achievement_score,
            parent_satisfaction_score=parent_satisfaction_score,
            notes=notes
        )
        result = await game_session.end_session(request_obj)

        return result

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"结束游戏会话失败: {str(e)}")


# ============ 游戏总结 ============

@router.post("/summarize", response_model=GameSummaryResponse)
async def summarize_game_session(
    request: GameSummaryRequest
):
    """
    生成游戏会话总结
    
    使用 LLM 分析游戏会话数据，生成详细的总结报告。
    包括：
    - 整体评价
    - 目标达成情况
    - 各维度进展
    - 亮点和改进建议
    - 下次游戏建议
    """
    try:
        game_summarizer = container.get('game_summarizer')
        
        # 初始化 Memory 服务（如果还没有）
        if game_summarizer.memory_service is None:
            from services.Memory.service import get_memory_service
            game_summarizer.memory_service = await get_memory_service()
            print("[API] Memory 服务已初始化")
        
        result = await game_summarizer.summarize_session(request)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"游戏总结失败: {str(e)}")
