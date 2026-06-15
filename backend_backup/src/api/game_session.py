"""
游戏会话管理 API（游戏实施阶段）

负责游戏实施阶段的会话生命周期管理：
1. 创建新会话（含动态按钮配置）
2. 查询会话状态与统计
3. 结束会话并生成摘要

注意：当前使用内存字典存储，后续会接入真实数据库（接口保持不变）。
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.models.behavior_record import GameSessionExtended


router = APIRouter(prefix="/api/game/session", tags=["游戏会话管理（实施阶段）"])


# ============ 内存存储（占位） ============

# session_id -> GameSessionExtended
SESSION_STORE: Dict[str, GameSessionExtended] = {}


# ============ 请求/响应模型 ============

class SessionStartReq(BaseModel):
    """创建游戏会话的请求体"""
    child_id: str = Field(..., description="儿童ID")
    game_type: str = Field(..., description="游戏类型，如 building/role_play/sensory")
    game_name: str = Field(..., description="游戏名称")
    planned_duration_minutes: int = Field(20, ge=1, le=180, description="计划时长（分钟）")


class SessionCompleteResp(BaseModel):
    """结束会话的响应数据"""
    session_id: str
    total_events: int
    engagement_score: Optional[float]
    ai_summary: Optional[str]
    duration_minutes: float


class StandardResp(BaseModel):
    """标准响应包装"""
    success: bool
    data: Optional[dict] = None
    message: str = ""


# ============ 内部工具 ============

def _build_dynamic_buttons(game_type: str) -> List[dict]:
    """
    根据游戏类型生成动态按钮配置。

    动态按钮与游戏类型强相关，用于补充固定按钮无法覆盖的场景。
    """
    presets = {
        "building": [
            {"id": "stack_block", "label": "搭积木", "icon": "🧱", "valence": 1},
            {"id": "knock_down", "label": "推倒", "icon": "💥", "valence": 0},
            {"id": "color_match", "label": "颜色配对", "icon": "🎨", "valence": 1},
        ],
        "role_play": [
            {"id": "role_take", "label": "进入角色", "icon": "🎭", "valence": 1},
            {"id": "dialogue", "label": "对话", "icon": "💬", "valence": 1},
            {"id": "role_break", "label": "出戏", "icon": "🚪", "valence": -1},
        ],
        "sensory": [
            {"id": "touch_explore", "label": "触觉探索", "icon": "✋", "valence": 1},
            {"id": "sensory_avoid", "label": "感觉回避", "icon": "🙈", "valence": -1},
        ],
        "music": [
            {"id": "rhythm_follow", "label": "跟节奏", "icon": "🎵", "valence": 1},
            {"id": "sing_along", "label": "跟唱", "icon": "🎤", "valence": 1},
        ],
        "outdoor": [
            {"id": "run_chase", "label": "追逐", "icon": "🏃", "valence": 1},
            {"id": "stop_freeze", "label": "停顿", "icon": "🛑", "valence": 0},
        ],
    }
    return presets.get(game_type, [
        {"id": "custom_positive", "label": "积极行为", "icon": "⭐", "valence": 1},
        {"id": "custom_neutral", "label": "中性行为", "icon": "🔘", "valence": 0},
    ])


def _get_session_or_404(session_id: str) -> GameSessionExtended:
    """根据 session_id 获取会话，不存在抛 404"""
    session = SESSION_STORE.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")
    return session


# ============ API 端点 ============

@router.post("/start")
async def start_session(req: SessionStartReq) -> StandardResp:
    """
    创建新游戏会话

    返回：会话信息（含固定按钮 + 根据游戏类型生成的动态按钮）
    """
    try:
        session_id = f"sess_{uuid4().hex[:12]}"
        session = GameSessionExtended(
            session_id=session_id,
            child_id=req.child_id,
            game_type=req.game_type,
            game_name=req.game_name,
            start_time=datetime.now(),
            planned_duration_minutes=req.planned_duration_minutes,
            dynamic_buttons=_build_dynamic_buttons(req.game_type),
        )
        SESSION_STORE[session_id] = session

        # 同步启动 AI 推断引擎的会话跟踪
        try:
            from src.container import container
            if container.has('observation_manager'):
                manager = container.get('observation_manager')
                await manager.start_session(
                    session_id=session_id,
                    child_id=req.child_id,
                    game_type=req.game_type,
                    game_name=req.game_name,
                    planned_duration=req.planned_duration_minutes,
                )
        except Exception as e:
            # 推断引擎启动失败不影响会话创建
            import logging
            logging.getLogger(__name__).warning(
                "[game_session] AI 推断引擎会话启动失败（已忽略）: %s", e
            )

        return StandardResp(
            success=True,
            data=session.model_dump(mode="json"),
            message="会话创建成功",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建会话失败: {e}")


@router.get("/{session_id}")
async def get_session(session_id: str) -> StandardResp:
    """获取会话当前状态及统计信息"""
    session = _get_session_or_404(session_id)

    # 实时计算运行时长
    end = session.end_time or datetime.now()
    duration_minutes = (end - session.start_time).total_seconds() / 60.0

    payload = session.model_dump(mode="json")
    payload["duration_minutes"] = round(duration_minutes, 2)
    payload["is_active"] = session.end_time is None

    return StandardResp(
        success=True,
        data=payload,
        message="获取会话状态成功",
    )


@router.post("/{session_id}/complete")
async def complete_session(session_id: str) -> StandardResp:
    """
    结束游戏会话

    生成摘要：total_events / engagement_score / ai_summary。
    （AI 摘要为占位实现，后续接入真实 LLM 服务时仅替换内部实现）
    """
    session = _get_session_or_404(session_id)

    if session.end_time is not None:
        raise HTTPException(status_code=400, detail="会话已结束，不能重复结束")

    session.end_time = datetime.now()

    # 同步结束 AI 推断引擎的会话跟踪
    try:
        from src.container import container
        if container.has('observation_manager'):
            manager = container.get('observation_manager')
            await manager.end_session(session_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            "[game_session] AI 推断引擎会话结束失败（已忽略）: %s", e
        )
    # 占位：参与度评分 = 累计事件数映射到 0-100，后续替换为真实算法
    if session.engagement_score is None:
        session.engagement_score = min(100.0, session.total_events * 5.0)

    # 占位：AI 摘要
    if session.ai_summary is None:
        session.ai_summary = (
            f"会话 {session_id} 共记录 {session.total_events} 次行为事件，"
            f"AI 推断 {session.ai_inferences_count} 条，参与度评分 {session.engagement_score:.1f}。"
        )

    duration_minutes = (session.end_time - session.start_time).total_seconds() / 60.0
    summary = SessionCompleteResp(
        session_id=session_id,
        total_events=session.total_events,
        engagement_score=session.engagement_score,
        ai_summary=session.ai_summary,
        duration_minutes=round(duration_minutes, 2),
    )

    return StandardResp(
        success=True,
        data=summary.model_dump(),
        message="会话已结束",
    )
