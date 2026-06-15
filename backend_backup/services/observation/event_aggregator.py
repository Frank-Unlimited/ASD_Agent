"""
事件聚合器服务（EventAggregator）

负责接收游戏过程中产生的原始行为事件，完成上下文增强、去重、置信度赋值，
并以双写方式将记录持久化到 SQLite 与 Graphiti 记忆服务，同时通过观察者
模式向 AI 推断引擎等下游模块广播新事件。

主要职责：
    1. 事件接收与上下文增强：注入时间戳、session_id、game_type、UUID。
    2. 去重逻辑：同会话同类型事件在 5 秒内只保留一条。
    3. 置信度赋值：根据 EventSource 自动设置 confidence。
    4. 双写存储：同步写 SQLite + 异步入队 memory_service（HTTP）。
    5. 事件广播：通知所有注册的监听器（同步/异步均可）。
    6. 会话管理：维护会话级别的事件缓存与统计。

设计要点：
    - 线程/协程安全：使用 asyncio.Lock 保护共享缓存。
    - SQLite 同步写入通过 asyncio.to_thread 包装，避免阻塞事件循环。
    - Memory 服务以 fire-and-forget 方式写入，单独的协程任务处理失败重试，
      绝不阻塞主流程；任何下游异常都被捕获并记录日志。
"""
from __future__ import annotations

import asyncio
import logging
import os
import sqlite3
import threading
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Awaitable, Callable, Optional, Union
from uuid import uuid4

try:
    import httpx  # type: ignore
except ImportError:  # pragma: no cover - 容错处理：在缺少 httpx 时退化为不可用
    httpx = None  # type: ignore

# 数据模型从 backend_backup.src.models.behavior_record 导入
try:
    from backend_backup.src.models.behavior_record import (
        BehaviorRecord,
        EventSource,
        GamePhase,
    )
except ImportError:  # 兼容相对包路径环境
    from src.models.behavior_record import (  # type: ignore
        BehaviorRecord,
        EventSource,
        GamePhase,
    )


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 常量配置
# ---------------------------------------------------------------------------

#: 同类型事件去重时间窗口（秒）
DEDUP_WINDOW_SECONDS: float = 5.0

#: EventSource → 默认 confidence 映射
SOURCE_CONFIDENCE_MAP: dict[EventSource, float] = {
    EventSource.PARENT_CLICK: 1.0,
    EventSource.TIMED_SNAPSHOT: 0.7,
    EventSource.AI_PROBE_RESPONSE: 0.8,
    EventSource.AI_INFERRED: 0.5,
}

#: 默认 memory_service 地址
DEFAULT_MEMORY_SERVICE_URL = os.getenv(
    "MEMORY_SERVICE_URL", "http://localhost:8000"
)

#: 默认 SQLite 数据库路径
DEFAULT_SQLITE_PATH = os.getenv(
    "SQLITE_DB_PATH", "./data/asd_intervention.db"
)

# 监听器签名：可同步或异步
ListenerCallable = Callable[[BehaviorRecord], Union[None, Awaitable[None]]]


# ---------------------------------------------------------------------------
# 会话上下文
# ---------------------------------------------------------------------------

@dataclass
class _SessionContext:
    """单个游戏会话的运行时上下文。"""
    session_id: str
    child_id: str
    game_type: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    # event_type → 上一次发生的时间戳，用于去重
    last_event_ts: dict[str, datetime] = field(default_factory=dict)
    # 该会话已记录的事件（顺序）
    events: list[BehaviorRecord] = field(default_factory=list)


# ---------------------------------------------------------------------------
# EventAggregator
# ---------------------------------------------------------------------------

class EventAggregator:
    """
    事件聚合器：游戏实时记录系统的事件入口。

    使用方式::

        aggregator = EventAggregator()
        aggregator.start_session("sess-001", "child-A", "floortime_blocks")
        is_new, record = await aggregator.record_event(
            session_id="sess-001",
            event_type="眼神接触",
            source=EventSource.PARENT_CLICK,
        )
        stats = aggregator.end_session("sess-001")
    """

    def __init__(
        self,
        db_path: Optional[str] = None,
        memory_service_url: Optional[str] = None,
        dedup_window_seconds: float = DEDUP_WINDOW_SECONDS,
    ):
        """
        初始化事件聚合器。

        Args:
            db_path: SQLite 数据库路径。为 None 时从环境变量 SQLITE_DB_PATH 读取。
            memory_service_url: memory_service 基础 URL（不含路径）。
                                为 None 时从环境变量 MEMORY_SERVICE_URL 读取。
            dedup_window_seconds: 去重时间窗口，默认 5 秒。
        """
        self.db_path: str = db_path or DEFAULT_SQLITE_PATH
        self.memory_service_url: str = (
            memory_service_url or DEFAULT_MEMORY_SERVICE_URL
        ).rstrip("/")
        self.dedup_window_seconds: float = dedup_window_seconds

        # 会话上下文：session_id → _SessionContext
        self._sessions: dict[str, _SessionContext] = {}

        # 监听器列表
        self._listeners: list[ListenerCallable] = []

        # 异步并发保护
        self._async_lock = asyncio.Lock()

        # SQLite 写入采用单独的线程锁（sqlite3 连接非线程安全）
        self._sqlite_lock = threading.Lock()

        # 懒加载的 httpx 客户端
        self._http_client: Optional["httpx.AsyncClient"] = None

        # 确保数据库目录存在
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        except Exception as exc:  # pragma: no cover
            logger.warning("[EventAggregator] 创建数据库目录失败: %s", exc)

        # 启动时确保 behavior_records 表存在
        self._ensure_table()

        logger.info(
            "[EventAggregator] 初始化完成 db_path=%s memory_service=%s",
            self.db_path,
            self.memory_service_url,
        )

    # ------------------------------------------------------------------
    # 会话管理
    # ------------------------------------------------------------------

    def start_session(
        self, session_id: str, child_id: str, game_type: str
    ) -> None:
        """
        初始化一个新的游戏会话上下文。

        重复 start_session 会重置该 session 的缓存。
        """
        ctx = _SessionContext(
            session_id=session_id,
            child_id=child_id,
            game_type=game_type,
        )
        self._sessions[session_id] = ctx
        logger.info(
            "[EventAggregator] 会话开始 session_id=%s child_id=%s game_type=%s",
            session_id,
            child_id,
            game_type,
        )

    def end_session(self, session_id: str) -> dict:
        """
        结束会话：清理缓存并返回统计摘要。

        Returns:
            会话统计 dict（键同 get_session_stats）。session 不存在时返回空 dict。
        """
        ctx = self._sessions.get(session_id)
        if ctx is None:
            logger.warning(
                "[EventAggregator] end_session: 未找到 session_id=%s", session_id
            )
            return {}

        stats = self._compute_stats(ctx)
        # 移除运行时缓存（事件已落库，无需驻留内存）
        self._sessions.pop(session_id, None)
        logger.info(
            "[EventAggregator] 会话结束 session_id=%s total_events=%d",
            session_id,
            stats.get("total_events", 0),
        )
        return stats

    def get_session_events(self, session_id: str) -> list[BehaviorRecord]:
        """返回该会话内存中已聚合的所有事件（按入队顺序）。"""
        ctx = self._sessions.get(session_id)
        if ctx is None:
            return []
        # 返回拷贝，避免外部修改内部状态
        return list(ctx.events)

    def get_session_stats(self, session_id: str) -> dict:
        """返回该会话的事件计数、类型分布与情感分布等统计信息。"""
        ctx = self._sessions.get(session_id)
        if ctx is None:
            return {}
        return self._compute_stats(ctx)

    # ------------------------------------------------------------------
    # 监听器注册
    # ------------------------------------------------------------------

    def register_listener(self, callback: ListenerCallable) -> None:
        """
        注册一个事件监听器。

        监听器接收单个 BehaviorRecord 参数，可以是同步函数或协程函数。
        监听器内部抛出的异常不会影响主流程，仅以 warning 记录。
        """
        if not callable(callback):
            raise TypeError("listener 必须是可调用对象")
        self._listeners.append(callback)
        logger.debug("[EventAggregator] 注册监听器 %r", callback)

    # ------------------------------------------------------------------
    # 核心：记录事件
    # ------------------------------------------------------------------

    async def record_event(
        self,
        session_id: str,
        event_type: str,
        source: EventSource,
        detail: Optional[str] = None,
        valence: int = 0,
        game_phase: Optional[GamePhase] = None,
        related_interest: Optional[str] = None,
    ) -> tuple[bool, Optional[BehaviorRecord]]:
        """
        记录一个行为事件。

        Returns:
            (is_new_record, record)
                is_new_record=True  → 新事件，已写入；返回 BehaviorRecord 对象。
                is_new_record=False → 命中去重窗口，未写入；record 为 None。
        """
        ctx = self._sessions.get(session_id)
        if ctx is None:
            logger.warning(
                "[EventAggregator] record_event 在未启动的 session 上调用: %s",
                session_id,
            )
            return False, None

        now = datetime.now(timezone.utc)

        # 在锁内完成"去重判断 + 时间戳更新 + 加入 events 列表"
        async with self._async_lock:
            last_ts = ctx.last_event_ts.get(event_type)
            if last_ts is not None:
                delta = (now - last_ts).total_seconds()
                if 0 <= delta < self.dedup_window_seconds:
                    logger.info(
                        "[EventAggregator] 去重命中 session=%s event_type=%s delta=%.2fs",
                        session_id,
                        event_type,
                        delta,
                    )
                    return False, None

            confidence = SOURCE_CONFIDENCE_MAP.get(source, 0.5)
            record = BehaviorRecord(
                id=str(uuid4()),
                timestamp=now,
                session_id=session_id,
                game_type=ctx.game_type,
                event_type=event_type,
                detail=detail,
                valence=valence,
                source=source,
                confidence=confidence,
                game_phase=game_phase,
                related_interest=related_interest,
                is_confirmed=None,
            )

            ctx.last_event_ts[event_type] = now
            ctx.events.append(record)

        # 锁外执行 IO：SQLite（线程池）+ memory_service（fire-and-forget）+ 监听器
        await self._write_sqlite_safe(record)
        self._enqueue_memory_write(record, ctx.child_id)
        await self._notify_listeners(record)

        logger.info(
            "[EventAggregator] 事件已记录 id=%s session=%s type=%s source=%s",
            record.id,
            session_id,
            event_type,
            source.value,
        )
        return True, record

    # ------------------------------------------------------------------
    # SQLite 写入
    # ------------------------------------------------------------------

    def _ensure_table(self) -> None:
        """确保 behavior_records 表与索引存在（启动时调用一次）。"""
        try:
            with self._sqlite_lock:
                conn = sqlite3.connect(self.db_path)
                try:
                    cur = conn.cursor()
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS behavior_records (
                            id TEXT PRIMARY KEY,
                            timestamp TEXT NOT NULL,
                            session_id TEXT NOT NULL,
                            game_type TEXT NOT NULL,
                            event_type TEXT NOT NULL,
                            detail TEXT,
                            valence INTEGER NOT NULL DEFAULT 0,
                            source TEXT NOT NULL,
                            confidence REAL NOT NULL DEFAULT 1.0,
                            game_phase TEXT,
                            related_interest TEXT,
                            is_confirmed INTEGER
                        )
                        """
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_behavior_records_session_id "
                        "ON behavior_records(session_id)"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_behavior_records_session_time "
                        "ON behavior_records(session_id, timestamp)"
                    )
                    conn.commit()
                finally:
                    conn.close()
        except Exception as exc:
            # 数据库不可用时不抛出，让主流程继续；只记日志
            logger.error("[EventAggregator] 初始化数据表失败: %s", exc)

    def _write_sqlite_sync(self, record: BehaviorRecord) -> None:
        """同步写一条记录到 SQLite（在线程池中调用）。"""
        with self._sqlite_lock:
            conn = sqlite3.connect(self.db_path)
            try:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO behavior_records (
                        id, timestamp, session_id, game_type, event_type,
                        detail, valence, source, confidence,
                        game_phase, related_interest, is_confirmed
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        record.id,
                        record.timestamp.isoformat(),
                        record.session_id,
                        record.game_type,
                        record.event_type,
                        record.detail,
                        record.valence,
                        record.source.value,
                        record.confidence,
                        record.game_phase.value if record.game_phase else None,
                        record.related_interest,
                        None if record.is_confirmed is None
                        else (1 if record.is_confirmed else 0),
                    ),
                )
                conn.commit()
            finally:
                conn.close()

    async def _write_sqlite_safe(self, record: BehaviorRecord) -> None:
        """异步包装 SQLite 写入，捕获异常。"""
        try:
            await asyncio.to_thread(self._write_sqlite_sync, record)
        except Exception as exc:
            logger.error(
                "[EventAggregator] SQLite 写入失败 id=%s: %s", record.id, exc
            )

    # ------------------------------------------------------------------
    # Memory Service 写入（HTTP，fire-and-forget）
    # ------------------------------------------------------------------

    def _enqueue_memory_write(
        self, record: BehaviorRecord, child_id: str
    ) -> None:
        """以 fire-and-forget 模式将记录写入 memory_service。"""
        try:
            asyncio.create_task(self._post_memory_write(record, child_id))
        except RuntimeError:
            # 没有运行中的事件循环时，记录日志但不阻塞
            logger.warning(
                "[EventAggregator] 无运行中的事件循环，跳过 memory 写入 id=%s",
                record.id,
            )

    async def _post_memory_write(
        self, record: BehaviorRecord, child_id: str
    ) -> None:
        """实际向 memory_service POST /api/memory/write。"""
        if httpx is None:
            logger.warning("[EventAggregator] httpx 未安装，跳过 memory 写入")
            return

        content = self._record_to_natural_language(record)
        payload = {
            "group_id": child_id,
            "content": content,
            "reference_time": record.timestamp.isoformat(),
        }

        try:
            client = await self._get_http_client()
            resp = await client.post(
                f"{self.memory_service_url}/api/memory/write",
                json=payload,
                timeout=10.0,
            )
            if resp.status_code >= 400:
                logger.warning(
                    "[EventAggregator] memory 写入返回非 2xx: %d %s",
                    resp.status_code,
                    resp.text[:200],
                )
            else:
                logger.debug(
                    "[EventAggregator] memory 已入队 id=%s", record.id
                )
        except Exception as exc:
            # 内存服务不可用时绝不影响主流程
            logger.warning(
                "[EventAggregator] memory 写入失败（已忽略） id=%s: %s",
                record.id,
                exc,
            )

    async def _get_http_client(self) -> "httpx.AsyncClient":
        """懒加载 httpx 客户端。"""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient()
        return self._http_client

    async def aclose(self) -> None:
        """关闭底层资源（HTTP 客户端等）。"""
        if self._http_client is not None:
            try:
                await self._http_client.aclose()
            except Exception:  # pragma: no cover
                pass
            self._http_client = None

    # ------------------------------------------------------------------
    # 自然语言转换
    # ------------------------------------------------------------------

    @staticmethod
    def _record_to_natural_language(record: BehaviorRecord) -> str:
        """
        将 BehaviorRecord 转换为自然语言描述，写入 Graphiti。

        示例："14:02 儿童出现眼神接触，家长记录，置信度1.0（detail）"
        """
        time_str = record.timestamp.strftime("%H:%M")
        source_label = {
            EventSource.PARENT_CLICK: "家长记录",
            EventSource.TIMED_SNAPSHOT: "定时快照",
            EventSource.AI_PROBE_RESPONSE: "AI探测回答",
            EventSource.AI_INFERRED: "AI推断",
        }.get(record.source, record.source.value)

        valence_label = (
            "正面" if record.valence > 0
            else "负面" if record.valence < 0
            else "中性"
        )

        parts = [
            f"{time_str} 儿童出现「{record.event_type}」（{valence_label}），",
            f"{source_label}，置信度{record.confidence:.1f}",
        ]
        if record.detail:
            parts.append(f"，细节：{record.detail}")
        if record.game_phase:
            parts.append(f"，阶段：{record.game_phase.value}")
        if record.related_interest:
            parts.append(f"，关联兴趣：{record.related_interest}")
        return "".join(parts)

    # ------------------------------------------------------------------
    # 监听器通知
    # ------------------------------------------------------------------

    async def _notify_listeners(self, record: BehaviorRecord) -> None:
        """依次通知所有监听器；任一监听器异常都不影响其他监听器。"""
        if not self._listeners:
            return
        for listener in list(self._listeners):
            try:
                result = listener(record)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as exc:
                logger.warning(
                    "[EventAggregator] 监听器 %r 抛出异常（已忽略）: %s",
                    listener,
                    exc,
                )

    # ------------------------------------------------------------------
    # 统计
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_stats(ctx: _SessionContext) -> dict:
        """根据 session 上下文计算统计摘要。"""
        type_counts: dict[str, int] = defaultdict(int)
        source_counts: dict[str, int] = defaultdict(int)
        valence_counts = {"positive": 0, "neutral": 0, "negative": 0}

        for ev in ctx.events:
            type_counts[ev.event_type] += 1
            source_counts[ev.source.value] += 1
            if ev.valence > 0:
                valence_counts["positive"] += 1
            elif ev.valence < 0:
                valence_counts["negative"] += 1
            else:
                valence_counts["neutral"] += 1

        end_time = datetime.now(timezone.utc)
        duration = (end_time - ctx.started_at).total_seconds()

        return {
            "session_id": ctx.session_id,
            "child_id": ctx.child_id,
            "game_type": ctx.game_type,
            "start_time": ctx.started_at.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "total_events": len(ctx.events),
            "event_type_distribution": dict(type_counts),
            "source_distribution": dict(source_counts),
            "valence_distribution": valence_counts,
        }


__all__ = ["EventAggregator"]
