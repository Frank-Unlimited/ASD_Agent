"""
快照交互 API（游戏实施阶段）

定时快照机制：在游戏过程中按调度模式间隔提示家长记录儿童参与度，
家长可从 invested/moderate/disengaged 三档中选择，或选择跳过。

调度策略：
- normal:  3 分钟（默认）
- dense:   5 分钟（家长点击频繁，减少打扰）
- sparse:  2 分钟（数据稀少，主动提醒）

自适应规则（占位实现）：
- 最近 5 分钟内行为事件 >= 8 -> 切换为 dense
- 最近 5 分钟内行为事件 <= 1 -> 切换为 sparse
- 其他 -> normal
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.game_session import SESSION_STORE
from src.models.behavior_record import (
    EngagementLevel,
    SchedulerMode,
    SnapshotRecord,
)


router = APIRouter(prefix="/api/snapshot", tags=["快照交互（实施阶段）"])


# ============ 内存存储 ============

# session_id -> List[SnapshotRecord]
SNAPSHOT_STORE: Dict[str, List[SnapshotRecord]] = {}

# session_id -> 当前调度模式
MODE_STORE: Dict[str, SchedulerMode] = {}


# ============ 调度间隔配置（分钟） ============

INTERVALS_CONFIG: Dict[str, int] = {
    SchedulerMode.NORMAL.value: 3,
    SchedulerMode.DENSE.value: 5,
    SchedulerMode.SPARSE.value: 2,
}


# ============ 请求/响应模型 ============

class SnapshotResponseReq(BaseModel):
    """家长对快照的回应"""
    session_id: str = Field(..., description="会话ID")
    engagement_level: Optional[EngagementLevel] = Field(
        None, description="参与度等级；skipped=true 时可省略"
    )
    skipped: bool = Field(False, description="是否跳过本次快照")


class StandardResp(BaseModel):
    """标准响应包装"""
    success: bool
    data: Optional[dict] = None
    message: str = ""


# ============ 内部工具 ============

def _ensure_session_exists(session_id: str) -> None:
    """确保会话存在，否则抛 404"""
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")


def _decide_mode(session_id: str) -> SchedulerMode:
    """
    根据会话最近活动情况决定调度模式（占位算法）。

    真实实现应基于 BehaviorRecord 的历史频率。这里基于会话的累计事件数粗略估算。
    """
    session = SESSION_STORE.get(session_id)
    if session is None:
        return SchedulerMode.NORMAL

    duration_min = max(
        (datetime.now() - session.start_time).total_seconds() / 60.0, 1.0
    )
    rate = session.total_events / duration_min  # events per minute

    if rate >= 1.5:
        return SchedulerMode.DENSE
    if rate <= 0.2:
        return SchedulerMode.SPARSE
    return SchedulerMode.NORMAL


def _compute_next_snapshot(session_id: str, mode: SchedulerMode) -> datetime:
    """根据上一次快照时间和当前模式计算下一次快照时间"""
    interval = INTERVALS_CONFIG[mode.value]
    snapshots = SNAPSHOT_STORE.get(session_id, [])
    if snapshots:
        last_ts = snapshots[-1].timestamp
    else:
        session = SESSION_STORE.get(session_id)
        last_ts = session.start_time if session else datetime.now()
    return last_ts + timedelta(minutes=interval)


# ============ API 端点 ============

@router.post("/response")
async def submit_snapshot_response(req: SnapshotResponseReq) -> StandardResp:
    """
    提交家长对快照的回应

    家长可以选择参与度等级（invested/moderate/disengaged），或选择跳过。
    """
    _ensure_session_exists(req.session_id)

    if not req.skipped and req.engagement_level is None:
        raise HTTPException(
            status_code=422,
            detail="未跳过时必须提供 engagement_level",
        )

    mode = _decide_mode(req.session_id)
    MODE_STORE[req.session_id] = mode

    record = SnapshotRecord(
        id=f"snap_{uuid4().hex[:12]}",
        timestamp=datetime.now(),
        session_id=req.session_id,
        engagement_level=None if req.skipped else req.engagement_level,
        skipped=req.skipped,
        scheduler_mode=mode,
    )
    SNAPSHOT_STORE.setdefault(req.session_id, []).append(record)

    return StandardResp(
        success=True,
        data=record.model_dump(mode="json"),
        message="快照回应已记录" if not req.skipped else "已跳过本次快照",
    )


@router.get("/next/{session_id}")
async def get_next_snapshot(session_id: str) -> StandardResp:
    """
    查询下次快照时间和当前调度模式

    返回：next_snapshot_time / current_mode / intervals_config
    """
    _ensure_session_exists(session_id)

    mode = _decide_mode(session_id)
    MODE_STORE[session_id] = mode
    next_ts = _compute_next_snapshot(session_id, mode)

    return StandardResp(
        success=True,
        data={
            "session_id": session_id,
            "next_snapshot_time": next_ts.isoformat(),
            "current_mode": mode.value,
            "intervals_config": INTERVALS_CONFIG,
            "snapshots_count": len(SNAPSHOT_STORE.get(session_id, [])),
        },
        message="获取下次快照时间成功",
    )
