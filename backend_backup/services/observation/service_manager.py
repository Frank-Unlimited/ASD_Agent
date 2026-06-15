"""
观察服务管理器（ObservationServiceManager）

整合三个子服务为单一入口：
    - EventAggregator   ：事件聚合 + 双写（SQLite + memory_service）+ 事件广播
    - SnapshotScheduler ：自适应快照频率调度
    - AIInferenceEngine ：基于事件流生成 AI 推断 / 探测问题

事件流向：
    parent_click / probe_response
        → EventAggregator.record_event
            → 监听器 1：AIInferenceEngine.on_event（async）— 累计事件，必要时生成推断
            → 监听器 2：_on_event_for_scheduler（sync）— 通知调度器有用户活动

设计要点：
    - EventAggregator 内部使用 iscoroutine 检测，因此监听器既可同步也可异步。
    - 三个子服务均可独立替换 / 测试；本类仅承担"组合 + 生命周期"。
    - start_session 是 async（与 record_event 调用风格保持一致），便于 FastAPI 路由直接 await。
"""
from __future__ import annotations

import logging
from typing import Any, Optional

try:
    from backend_backup.src.models.behavior_record import BehaviorRecord
except ImportError:  # 兼容相对路径
    from src.models.behavior_record import BehaviorRecord  # type: ignore

from .ai_inference_engine import AIInferenceEngine
from .event_aggregator import EventAggregator
from .snapshot_scheduler import SnapshotScheduler


logger = logging.getLogger(__name__)


class ObservationServiceManager:
    """观察服务管理器 — 整合事件聚合、快照调度、AI 推断三个子服务。"""

    def __init__(
        self,
        db_path: Optional[str] = None,
        memory_service_url: Optional[str] = None,
        llm_service: Any = None,
    ) -> None:
        """
        初始化三个子服务并完成事件监听绑定。

        Args:
            db_path: SQLite 数据库路径（透传给 EventAggregator）。
            memory_service_url: memory_service 基础 URL（透传给 EventAggregator）。
            llm_service: LLM 服务实例（注入 AIInferenceEngine）。
                         如果为 None，会尝试自动从项目 LLM_Service 模块创建。
        """
        # 如果未显式传入 llm_service，尝试自动创建
        if llm_service is None:
            llm_service = self._try_create_llm_service()

        self.event_aggregator = EventAggregator(
            db_path=db_path,
            memory_service_url=memory_service_url,
        )
        self.snapshot_scheduler = SnapshotScheduler()
        self.inference_engine = AIInferenceEngine(llm_service=llm_service)

        # 监听器 1：事件聚合器 → AI 推断引擎（异步回调）
        self.event_aggregator.register_listener(self.inference_engine.on_event)
        # 监听器 2：事件聚合器 → 快照调度器（同步回调）
        self.event_aggregator.register_listener(self._on_event_for_scheduler)

        logger.info(
            "[ObservationServiceManager] 初始化完成 db_path=%s memory_url=%s llm=%s",
            db_path,
            memory_service_url,
            llm_service is not None,
        )

    @staticmethod
    def _try_create_llm_service() -> Any:
        """
        尝试从项目现有 LLM_Service 模块创建 LLM 服务实例。

        失败时返回 None（优雅降级到规则推断）。
        """
        try:
            from services.LLM_Service.service import get_llm_service
            service = get_llm_service()
            logger.info("[ObservationServiceManager] 自动创建 LLM 服务成功")
            return service
        except Exception as exc:
            logger.warning(
                "[ObservationServiceManager] 自动创建 LLM 服务失败，将使用规则推断: %s",
                exc,
            )
            return None

    # ------------------------------------------------------------------
    # 会话生命周期
    # ------------------------------------------------------------------

    async def start_session(
        self,
        session_id: str,
        child_id: str,
        game_type: str,
        game_name: str,
        planned_duration: int,
        child_history: Optional[dict] = None,
    ) -> None:
        """
        启动一个游戏会话：在三个子服务中同步初始化上下文。

        Args:
            session_id: 会话唯一标识。
            child_id: 儿童 ID（Graphiti group_id）。
            game_type: 游戏类型（影响动态按钮 / 探测模板）。
            game_name: 游戏名称（用于日志展示）。
            planned_duration: 计划时长（分钟），用于阶段识别。
            child_history: 历史基线信息，可选。
        """
        self.event_aggregator.start_session(session_id, child_id, game_type)
        self.snapshot_scheduler.start_session(session_id)
        self.inference_engine.start_session(
            session_id=session_id,
            game_type=game_type,
            planned_duration_minutes=planned_duration,
            child_history=child_history,
        )
        logger.info(
            "[ObservationServiceManager] 会话启动 session=%s child=%s game=%s(%s) duration=%dmin",
            session_id,
            child_id,
            game_name,
            game_type,
            planned_duration,
        )

    async def end_session(self, session_id: str) -> dict:
        """
        结束会话：依次收集三个子服务的统计并合并返回。

        Returns:
            合并后的统计字典；键名冲突时后写入者覆盖前者，故顺序为
            event_stats → snapshot_stats → inference_stats，
            最终保留各服务的特征字段。
        """
        event_stats = self.event_aggregator.end_session(session_id) or {}
        snapshot_stats = self.snapshot_scheduler.end_session(session_id) or {}
        inference_stats = self.inference_engine.end_session(session_id) or {}

        merged = {**event_stats, **snapshot_stats, **inference_stats}
        logger.info(
            "[ObservationServiceManager] 会话结束 session=%s "
            "events=%d snapshots=%d inferences=%d",
            session_id,
            event_stats.get("total_events", 0),
            snapshot_stats.get("total_snapshots", 0),
            inference_stats.get("total_inferences", 0),
        )
        return merged

    # ------------------------------------------------------------------
    # 内部回调
    # ------------------------------------------------------------------

    def _on_event_for_scheduler(self, event: BehaviorRecord) -> None:
        """事件 → 调度器的同步桥接：通知"有用户活动"。"""
        try:
            self.snapshot_scheduler.notify_activity(event.session_id)
        except Exception as exc:  # pragma: no cover - 不阻塞主流程
            logger.warning(
                "[ObservationServiceManager] 调度器通知失败（已忽略） session=%s: %s",
                event.session_id,
                exc,
            )

    # ------------------------------------------------------------------
    # 资源清理
    # ------------------------------------------------------------------

    async def aclose(self) -> None:
        """关闭底层资源（HTTP client 等）。"""
        try:
            await self.event_aggregator.aclose()
        except Exception as exc:  # pragma: no cover
            logger.warning("[ObservationServiceManager] aclose 失败: %s", exc)


__all__ = ["ObservationServiceManager"]
