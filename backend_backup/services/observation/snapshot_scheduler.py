"""
快照调度器服务（SnapshotScheduler）

为每个活跃的游戏会话管理自适应定时快照频率。

核心能力：
    1. 三种调度模式（NORMAL / DENSE / SPARSE）的状态机切换；
    2. 基于"最近 5 分钟点击次数"与"持续无操作时长"动态调整快照间隔；
    3. 递减打扰策略：连续跳过 3 次后自动降频（6 分钟），家长再次回应后恢复；
    4. 维护每个 session 独立的调度状态，提供供轮询使用的 should_trigger_snapshot
       接口与统计信息。

设计说明：
    - 纯同步实现；轮询线程或定时任务以固定频率调用 should_trigger_snapshot；
    - 模式切换在 notify_activity 与 should_trigger_snapshot 中均会触发评估，
      以保证快照触发前一定先做最新模式判断；
    - 所有时间计算使用本机 datetime.now()。
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

from src.models.behavior_record import (
    EngagementLevel,
    SchedulerMode,
    SnapshotRecord,
)

logger = logging.getLogger(__name__)


# ----------------------------- 调度参数常量 ----------------------------- #

# 各模式对应的快照间隔（分钟）
MODE_INTERVAL_MINUTES: dict[SchedulerMode, int] = {
    SchedulerMode.NORMAL: 3,
    SchedulerMode.DENSE: 5,
    SchedulerMode.SPARSE: 2,
}

# 进入 DENSE 模式的阈值：最近 DENSE_WINDOW_MINUTES 分钟内的点击次数 >= DENSE_CLICK_THRESHOLD
DENSE_WINDOW_MINUTES: int = 5
DENSE_CLICK_THRESHOLD: int = 4

# 进入 SPARSE 模式的阈值：连续 SPARSE_IDLE_MINUTES 分钟无任何操作
SPARSE_IDLE_MINUTES: int = 4

# 递减打扰策略
DEGRADE_SKIP_THRESHOLD: int = 3       # 连续跳过次数阈值
DEGRADED_INTERVAL_MINUTES: int = 6    # 降频后的快照间隔（分钟）


# ----------------------------- 会话调度状态 ----------------------------- #

@dataclass
class SessionSchedulerState:
    """单个会话的调度器状态。"""

    session_id: str
    current_mode: SchedulerMode = SchedulerMode.NORMAL
    last_snapshot_time: datetime = field(default_factory=datetime.now)
    last_activity_time: datetime = field(default_factory=datetime.now)
    consecutive_skips: int = 0
    total_snapshots: int = 0
    total_responses: int = 0
    # 最近 5 分钟内的活动时间戳（用于判断是否进入 DENSE 模式）
    recent_activities: list[datetime] = field(default_factory=list)
    # 是否已降频（连续跳过 DEGRADE_SKIP_THRESHOLD 次后置 True）
    is_degraded: bool = False
    # 会话开始时间，用于统计
    started_at: datetime = field(default_factory=datetime.now)


# ----------------------------- 调度器主类 ----------------------------- #

class SnapshotScheduler:
    """快照调度器：管理多个游戏会话的自适应快照频率。"""

    def __init__(self) -> None:
        # 以 session_id 为键的活跃会话表
        self._sessions: dict[str, SessionSchedulerState] = {}

    # ---------------- 会话生命周期 ---------------- #

    def start_session(self, session_id: str) -> None:
        """初始化会话调度器。

        如果已经存在同名 session，则保留旧状态不覆盖（幂等），并打印警告。
        """
        if session_id in self._sessions:
            logger.warning("[SnapshotScheduler] 会话 %s 已存在，跳过重复初始化", session_id)
            return

        now = datetime.now()
        state = SessionSchedulerState(
            session_id=session_id,
            current_mode=SchedulerMode.NORMAL,
            last_snapshot_time=now,
            last_activity_time=now,
            started_at=now,
        )
        self._sessions[session_id] = state
        logger.info(
            "[SnapshotScheduler] 启动会话调度器 session=%s mode=%s interval=%dmin",
            session_id,
            state.current_mode.value,
            MODE_INTERVAL_MINUTES[state.current_mode],
        )

    def end_session(self, session_id: str) -> dict:
        """结束会话，移除调度状态并返回快照统计。"""
        state = self._sessions.pop(session_id, None)
        if state is None:
            logger.warning("[SnapshotScheduler] 结束会话失败：未找到 session=%s", session_id)
            return {
                "session_id": session_id,
                "total_snapshots": 0,
                "total_responses": 0,
                "skipped": 0,
                "final_mode": None,
                "duration_seconds": 0,
            }

        skipped = state.total_snapshots - state.total_responses
        duration = (datetime.now() - state.started_at).total_seconds()
        stats = {
            "session_id": session_id,
            "total_snapshots": state.total_snapshots,
            "total_responses": state.total_responses,
            "skipped": skipped,
            "final_mode": state.current_mode.value,
            "duration_seconds": duration,
            "is_degraded": state.is_degraded,
        }
        logger.info("[SnapshotScheduler] 结束会话 session=%s stats=%s", session_id, stats)
        return stats

    # ---------------- 活动与快照回应 ---------------- #

    def notify_activity(self, session_id: str) -> None:
        """通知有用户活动（家长点击事件）。

        会更新最近活动时间戳，并尝试触发模式切换判断。
        """
        state = self._sessions.get(session_id)
        if state is None:
            logger.warning("[SnapshotScheduler] notify_activity 找不到 session=%s", session_id)
            return

        now = datetime.now()
        state.last_activity_time = now
        state.recent_activities.append(now)
        # 清理超过 DENSE 评估窗口的旧时间戳
        self._prune_recent_activities(state, now)

        logger.debug(
            "[SnapshotScheduler] 活动事件 session=%s 最近%d分钟点击数=%d",
            session_id,
            DENSE_WINDOW_MINUTES,
            len(state.recent_activities),
        )

        self._evaluate_mode(state, now)

    def record_snapshot_response(
        self,
        session_id: str,
        engagement_level: Optional[EngagementLevel],
        skipped: bool = False,
    ) -> SnapshotRecord:
        """记录一次快照回应。

        Args:
            session_id: 会话 ID。
            engagement_level: 家长选择的参与度等级；为 None 表示没有有效回应。
            skipped: 是否为"跳过"，True 表示家长没有回应这次快照。

        Returns:
            构造好的 SnapshotRecord 对象（由调用方负责落库）。
        """
        state = self._sessions.get(session_id)
        if state is None:
            raise KeyError(f"会话不存在：{session_id}")

        now = datetime.now()
        state.last_snapshot_time = now
        state.total_snapshots += 1

        record = SnapshotRecord(
            timestamp=now,
            session_id=session_id,
            engagement_level=engagement_level,
            skipped=skipped,
            scheduler_mode=state.current_mode,
        )

        if skipped or engagement_level is None:
            # 家长跳过：累计跳过次数；达到阈值则降频
            state.consecutive_skips += 1
            logger.info(
                "[SnapshotScheduler] 快照被跳过 session=%s consecutive_skips=%d mode=%s",
                session_id,
                state.consecutive_skips,
                state.current_mode.value,
            )
            if (
                not state.is_degraded
                and state.consecutive_skips >= DEGRADE_SKIP_THRESHOLD
            ):
                state.is_degraded = True
                logger.info(
                    "[SnapshotScheduler] 触发降频 session=%s 连续跳过%d次 → 间隔提升为%d分钟",
                    session_id,
                    state.consecutive_skips,
                    DEGRADED_INTERVAL_MINUTES,
                )
        else:
            # 家长有效回应：重置跳过计数；如果之前已降频，则恢复正常调度模式频率
            state.total_responses += 1
            state.last_activity_time = now
            state.recent_activities.append(now)
            self._prune_recent_activities(state, now)

            if state.is_degraded:
                logger.info(
                    "[SnapshotScheduler] 解除降频 session=%s 家长再次回应快照 → 恢复%s模式",
                    session_id,
                    state.current_mode.value,
                )
            state.consecutive_skips = 0
            state.is_degraded = False

            # 收到回应后也评估一次模式
            self._evaluate_mode(state, now)

        return record

    # ---------------- 触发判断与查询 ---------------- #

    def should_trigger_snapshot(self, session_id: str) -> bool:
        """检查当前是否应该触发快照（供轮询调用）。"""
        state = self._sessions.get(session_id)
        if state is None:
            return False

        now = datetime.now()
        # 在轮询中也持续评估模式（特别是 SPARSE 的"持续无操作"判断）
        self._evaluate_mode(state, now)

        interval = self._effective_interval(state)
        elapsed = now - state.last_snapshot_time
        return elapsed >= interval

    def get_next_snapshot_info(self, session_id: str) -> dict:
        """获取下次快照信息：时间、当前模式、间隔配置等。"""
        state = self._sessions.get(session_id)
        if state is None:
            return {}

        interval = self._effective_interval(state)
        next_time = state.last_snapshot_time + interval
        return {
            "session_id": session_id,
            "current_mode": state.current_mode.value,
            "is_degraded": state.is_degraded,
            "interval_minutes": interval.total_seconds() / 60,
            "last_snapshot_time": state.last_snapshot_time.isoformat(),
            "next_snapshot_time": next_time.isoformat(),
            "consecutive_skips": state.consecutive_skips,
        }

    def get_session_stats(self, session_id: str) -> dict:
        """获取快照统计。"""
        state = self._sessions.get(session_id)
        if state is None:
            return {}

        skipped = state.total_snapshots - state.total_responses
        duration = (datetime.now() - state.started_at).total_seconds()
        response_rate = (
            state.total_responses / state.total_snapshots
            if state.total_snapshots > 0
            else 0.0
        )
        return {
            "session_id": session_id,
            "current_mode": state.current_mode.value,
            "is_degraded": state.is_degraded,
            "total_snapshots": state.total_snapshots,
            "total_responses": state.total_responses,
            "skipped": skipped,
            "response_rate": round(response_rate, 3),
            "consecutive_skips": state.consecutive_skips,
            "duration_seconds": duration,
            "last_snapshot_time": state.last_snapshot_time.isoformat(),
            "last_activity_time": state.last_activity_time.isoformat(),
        }

    # ----------------------------- 内部方法 ----------------------------- #

    @staticmethod
    def _prune_recent_activities(state: SessionSchedulerState, now: datetime) -> None:
        """裁剪 recent_activities 列表，仅保留 DENSE 窗口内的时间戳。"""
        cutoff = now - timedelta(minutes=DENSE_WINDOW_MINUTES)
        state.recent_activities = [t for t in state.recent_activities if t >= cutoff]

    def _effective_interval(self, state: SessionSchedulerState) -> timedelta:
        """根据当前模式与降频状态计算实际生效的快照间隔。"""
        if state.is_degraded:
            return timedelta(minutes=DEGRADED_INTERVAL_MINUTES)
        return timedelta(minutes=MODE_INTERVAL_MINUTES[state.current_mode])

    def _evaluate_mode(self, state: SessionSchedulerState, now: datetime) -> None:
        """根据最近活动情况评估并切换调度模式。

        判断顺序：
            1. 优先判断是否满足 DENSE（点击频繁）；
            2. 否则判断是否满足 SPARSE（持续无操作）；
            3. 都不满足时回归 NORMAL。
        """
        # 先确保 recent_activities 是裁剪过的
        self._prune_recent_activities(state, now)

        old_mode = state.current_mode
        idle_seconds = (now - state.last_activity_time).total_seconds()
        click_count = len(state.recent_activities)

        if click_count >= DENSE_CLICK_THRESHOLD:
            new_mode = SchedulerMode.DENSE
        elif idle_seconds >= SPARSE_IDLE_MINUTES * 60:
            new_mode = SchedulerMode.SPARSE
        else:
            new_mode = SchedulerMode.NORMAL

        if new_mode != old_mode:
            state.current_mode = new_mode
            logger.info(
                "[SnapshotScheduler] 模式切换 session=%s %s → %s "
                "(最近%d分钟点击=%d, idle=%.1fs, interval=%dmin)",
                state.session_id,
                old_mode.value,
                new_mode.value,
                DENSE_WINDOW_MINUTES,
                click_count,
                idle_seconds,
                MODE_INTERVAL_MINUTES[new_mode],
            )
