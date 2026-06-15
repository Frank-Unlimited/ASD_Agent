"""
AI 推断引擎服务（AIInferenceEngine）

游戏实时记录系统的"AI 推断"通道。订阅 EventAggregator 的事件流，
基于事件分布、游戏阶段与历史基线生成可解释的推断结果，并按需主动
生成探测问题（Probe）辅助家长补录关键行为。

核心能力：
    1. 游戏阶段识别（基于已进行时间 + 事件密度微调）
    2. 行为模式推断（规则 / LLM 双通道，受频率限制保护）
    3. 探测问题生成（数据稀疏或阶段切换触发）
    4. 动态按钮推荐（按游戏类型 + 历史高频行为排序）

设计要点：
    - LLM 调用通过 ``llm_service`` 注入；为 None 时退化为规则推断。
    - 推断频率限制（默认 ≥120s 一次），避免打扰家长。
    - 所有公开方法均为协程或同步方法，与 EventAggregator 对接友好。
    - 所有状态保存在内存（_sessions / _inference_store / _probe_store）；
      持久化由调用方 / EventAggregator 统一处理。
"""
from __future__ import annotations

import asyncio
import json
import logging
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

try:
    from backend_backup.src.models.behavior_record import (
        AIInferenceRecord,
        AIProbeQuestion,
        BehaviorRecord,
        EventSource,
        GamePhase,
    )
except ImportError:  # 兼容相对包路径环境
    from src.models.behavior_record import (  # type: ignore
        AIInferenceRecord,
        AIProbeQuestion,
        BehaviorRecord,
        EventSource,
        GamePhase,
    )

try:
    from .prompts import (
        BEHAVIOR_INFERENCE_PROMPT,
        PROBE_QUESTION_PROMPT,
        build_inference_user_message,
        build_probe_user_message,
    )
except ImportError:  # pragma: no cover
    from backend_backup.services.observation.prompts import (  # type: ignore
        BEHAVIOR_INFERENCE_PROMPT,
        PROBE_QUESTION_PROMPT,
        build_inference_user_message,
        build_probe_user_message,
    )


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 常量配置
# ---------------------------------------------------------------------------

#: 推断生成最小间隔（秒），保证每 2 分钟最多一条
MIN_INFERENCE_INTERVAL_SECONDS: float = 120.0

#: 数据稀疏判定：超过该秒数无新事件视为稀疏
SPARSE_DATA_WINDOW_SECONDS: float = 180.0

#: 推断使用的"最近事件"窗口（秒）
RECENT_EVENT_WINDOW_SECONDS: float = 300.0

#: 阶段时间占比阈值（按 planned_duration 比例划分）
PHASE_RATIO_BOUNDARIES: list[tuple[float, GamePhase]] = [
    (0.20, GamePhase.EXPLORATION),
    (0.60, GamePhase.INTERACTION),
    (0.85, GamePhase.CLIMAX),
    (1.01, GamePhase.CLOSURE),  # 1.01 兜底，确保末端命中 closure
]

#: 高潮提前判定：interaction 阶段事件密度 ≥ 该值（事件/分钟）则提前进入 climax
CLIMAX_DENSITY_THRESHOLD: float = 4.0


# ---------------------------------------------------------------------------
# 游戏类型 → 动态按钮映射表
# ---------------------------------------------------------------------------

GAME_TYPE_BUTTONS: dict[str, list[dict[str, Any]]] = {
    "积木搭建": [
        {"id": "imitation", "label": "模仿", "icon": "🧩", "valence": 1},
        {"id": "turn_taking", "label": "轮流", "icon": "🔄", "valence": 1},
        {"id": "destruction", "label": "破坏", "icon": "💥", "valence": 0},
    ],
    "追逐游戏": [
        {"id": "initiate", "label": "主动发起", "icon": "🏃", "valence": 1},
        {"id": "follow", "label": "跟随", "icon": "👣", "valence": 1},
        {"id": "escape", "label": "逃避", "icon": "🙈", "valence": -1},
    ],
    "角色扮演": [
        {"id": "role_switch", "label": "角色转换", "icon": "🎭", "valence": 1},
        {"id": "dialogue", "label": "对话", "icon": "💬", "valence": 1},
        {"id": "imagination", "label": "想象力", "icon": "✨", "valence": 1},
    ],
    "感官探索": [
        {"id": "touch_explore", "label": "触觉探索", "icon": "🤲", "valence": 1},
        {"id": "visual_track", "label": "视觉追踪", "icon": "👁️", "valence": 1},
        {"id": "sensory_avoid", "label": "感官回避", "icon": "🚫", "valence": -1},
    ],
    "音乐互动": [
        {"id": "rhythm", "label": "节奏感", "icon": "🎵", "valence": 1},
        {"id": "vocal", "label": "发声", "icon": "🗣️", "valence": 1},
        {"id": "body_move", "label": "身体律动", "icon": "💃", "valence": 1},
    ],
}

#: 默认动态按钮（未匹配游戏类型时）
DEFAULT_DYNAMIC_BUTTONS: list[dict[str, Any]] = [
    {"id": "new_behavior", "label": "新行为", "icon": "⚡", "valence": 1},
    {"id": "pointing", "label": "指向", "icon": "🎯", "valence": 1},
    {"id": "vocalization", "label": "发声", "icon": "🗣️", "valence": 1},
]


# ---------------------------------------------------------------------------
# 推断会话状态
# ---------------------------------------------------------------------------

@dataclass
class InferenceSessionState:
    """单个推断会话的运行时状态。"""

    session_id: str
    game_type: str
    planned_duration_minutes: int = 20
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # 历史基线（如：{"eye_contact_per_min": 1.2, "engagement_avg": 0.7}）
    child_history: dict[str, Any] = field(default_factory=dict)

    # 该会话累积的事件（按时间顺序）
    events: list[BehaviorRecord] = field(default_factory=list)

    # 上一次生成推断的时间戳（用于频率限制）
    last_inference_at: Optional[datetime] = None

    # 当前游戏阶段（最近一次 get_current_phase 计算结果，作为缓存）
    current_phase: GamePhase = GamePhase.EXPLORATION

    # 待回答的探测问题（最多 1 条；回答后清空）
    pending_probe: Optional[AIProbeQuestion] = None

    # 上一次生成探测问题的时间戳
    last_probe_at: Optional[datetime] = None

    # 上一次阶段，用于检测阶段切换以触发探测
    last_phase: GamePhase = GamePhase.EXPLORATION


# ---------------------------------------------------------------------------
# AIInferenceEngine
# ---------------------------------------------------------------------------

class AIInferenceEngine:
    """
    AI 推断引擎。

    使用方式::

        engine = AIInferenceEngine(llm_service=None)  # 注入或留空
        engine.start_session("sess-1", "积木搭建", 20, child_history={...})
        aggregator.register_listener(engine.on_event)
        ...
        await engine.generate_inference("sess-1")
        engine.end_session("sess-1")
    """

    def __init__(self, llm_service: Any = None):
        """
        初始化推断引擎。

        Args:
            llm_service: LLM 服务实例（需提供 ``call`` 协程方法）。
                         为 None 时使用基于规则的简单推断。
        """
        self.llm_service = llm_service
        self._sessions: dict[str, InferenceSessionState] = {}
        self._inference_store: dict[str, list[AIInferenceRecord]] = defaultdict(list)
        self._probe_store: dict[str, list[AIProbeQuestion]] = defaultdict(list)
        self._async_lock = asyncio.Lock()

        logger.info(
            "[AIInferenceEngine] 初始化完成 llm_enabled=%s",
            llm_service is not None,
        )

    # ------------------------------------------------------------------
    # 会话管理
    # ------------------------------------------------------------------

    def start_session(
        self,
        session_id: str,
        game_type: str,
        planned_duration_minutes: int = 20,
        child_history: Optional[dict] = None,
    ) -> None:
        """初始化一个推断会话。重复调用会重置状态。"""
        state = InferenceSessionState(
            session_id=session_id,
            game_type=game_type,
            planned_duration_minutes=planned_duration_minutes,
            child_history=child_history or {},
        )
        self._sessions[session_id] = state
        self._inference_store.setdefault(session_id, [])
        self._probe_store.setdefault(session_id, [])
        logger.info(
            "[AIInferenceEngine] 会话开始 session=%s game_type=%s duration=%dmin",
            session_id,
            game_type,
            planned_duration_minutes,
        )

    def end_session(self, session_id: str) -> dict:
        """结束会话并返回推断统计。"""
        state = self._sessions.get(session_id)
        if state is None:
            logger.warning(
                "[AIInferenceEngine] end_session: 未找到 session=%s", session_id
            )
            return {}

        inferences = self._inference_store.get(session_id, [])
        probes = self._probe_store.get(session_id, [])

        stats = {
            "session_id": session_id,
            "game_type": state.game_type,
            "started_at": state.started_at.isoformat(),
            "ended_at": datetime.now(timezone.utc).isoformat(),
            "total_events": len(state.events),
            "total_inferences": len(inferences),
            "total_probes": len(probes),
            "confirmed_inferences": sum(1 for i in inferences if i.is_confirmed is True),
            "rejected_inferences": sum(1 for i in inferences if i.is_confirmed is False),
            "final_phase": state.current_phase.value,
        }

        self._sessions.pop(session_id, None)
        logger.info(
            "[AIInferenceEngine] 会话结束 session=%s inferences=%d probes=%d",
            session_id,
            stats["total_inferences"],
            stats["total_probes"],
        )
        return stats

    # ------------------------------------------------------------------
    # 事件监听
    # ------------------------------------------------------------------

    async def on_event(self, event: BehaviorRecord) -> None:
        """
        EventAggregator 注册的事件监听回调。

        - 收到事件后追加到会话状态
        - 重新计算当前游戏阶段
        - 如果满足条件则触发推断 / 探测问题
        """
        state = self._sessions.get(event.session_id)
        if state is None:
            # 推断引擎未追踪该会话，忽略即可
            logger.debug(
                "[AIInferenceEngine] 忽略未追踪 session 的事件 session=%s",
                event.session_id,
            )
            return

        async with self._async_lock:
            state.events.append(event)
            new_phase = self._infer_phase(state)
            phase_changed = new_phase != state.current_phase
            state.last_phase = state.current_phase
            state.current_phase = new_phase

        # 阶段切换：尝试生成探测问题
        if phase_changed:
            logger.info(
                "[AIInferenceEngine] 阶段切换 session=%s %s -> %s",
                event.session_id,
                state.last_phase.value,
                new_phase.value,
            )
            try:
                await self.generate_probe_question(event.session_id)
            except Exception as exc:  # pragma: no cover
                logger.warning(
                    "[AIInferenceEngine] 阶段切换探测生成失败: %s", exc
                )

        # 满足频率限制时尝试生成新推断
        if self._should_generate_inference(state):
            try:
                await self.generate_inference(event.session_id)
            except Exception as exc:  # pragma: no cover
                logger.warning("[AIInferenceEngine] 推断生成失败: %s", exc)

    # ------------------------------------------------------------------
    # 阶段识别
    # ------------------------------------------------------------------

    def get_current_phase(self, session_id: str) -> GamePhase:
        """获取（并刷新）当前游戏阶段。"""
        state = self._sessions.get(session_id)
        if state is None:
            return GamePhase.EXPLORATION
        phase = self._infer_phase(state)
        state.current_phase = phase
        return phase

    def _infer_phase(self, state: InferenceSessionState) -> GamePhase:
        """根据已进行时间 + 事件密度推断当前阶段。"""
        now = datetime.now(timezone.utc)
        elapsed = (now - state.started_at).total_seconds()
        total = max(state.planned_duration_minutes * 60.0, 1.0)
        ratio = elapsed / total

        # 基于时间占比的初始阶段
        base_phase = GamePhase.CLOSURE
        for boundary, phase in PHASE_RATIO_BOUNDARIES:
            if ratio < boundary:
                base_phase = phase
                break

        # 如果当前处于 interaction 阶段且最近一分钟事件密度过高 → 提前 climax
        if base_phase == GamePhase.INTERACTION:
            recent_events_count = self._count_events_in_window(
                state, window_seconds=60.0
            )
            density = recent_events_count  # 每分钟事件数
            if density >= CLIMAX_DENSITY_THRESHOLD:
                logger.debug(
                    "[AIInferenceEngine] 高密度提前进入 climax session=%s density=%.1f",
                    state.session_id,
                    density,
                )
                return GamePhase.CLIMAX

        return base_phase

    @staticmethod
    def _count_events_in_window(
        state: InferenceSessionState, window_seconds: float
    ) -> int:
        """统计最近 window_seconds 内的事件数量。"""
        if not state.events:
            return 0
        now = datetime.now(timezone.utc)
        cutoff = now.timestamp() - window_seconds
        return sum(1 for e in state.events if e.timestamp.timestamp() >= cutoff)

    # ------------------------------------------------------------------
    # 推断生成
    # ------------------------------------------------------------------

    def _should_generate_inference(self, state: InferenceSessionState) -> bool:
        """是否满足"可以生成下一条推断"的条件。"""
        if state.last_inference_at is None:
            # 至少累计 3 条事件再开始推断
            return len(state.events) >= 3
        delta = (datetime.now(timezone.utc) - state.last_inference_at).total_seconds()
        return delta >= MIN_INFERENCE_INTERVAL_SECONDS

    async def generate_inference(
        self, session_id: str
    ) -> Optional[AIInferenceRecord]:
        """基于当前状态生成一条推断。受频率限制保护。"""
        state = self._sessions.get(session_id)
        if state is None:
            logger.warning(
                "[AIInferenceEngine] generate_inference: 未找到 session=%s",
                session_id,
            )
            return None

        if not self._should_generate_inference(state):
            logger.debug(
                "[AIInferenceEngine] 推断频率限制未到，跳过 session=%s",
                session_id,
            )
            return None

        # 优先调用 LLM；失败或未注入时退化为规则推断
        record: Optional[AIInferenceRecord] = None
        if self.llm_service is not None:
            try:
                record = await self._generate_inference_via_llm(state)
            except Exception as exc:
                logger.warning(
                    "[AIInferenceEngine] LLM 推断失败，退化为规则推断: %s", exc
                )
                record = None

        if record is None:
            record = self._generate_inference_via_rules(state)

        if record is None:
            return None

        state.last_inference_at = datetime.now(timezone.utc)
        self._inference_store[session_id].append(record)
        logger.info(
            "[AIInferenceEngine] 推断生成 session=%s id=%s text=%s",
            session_id,
            record.id,
            record.inference_text,
        )
        return record

    async def _generate_inference_via_llm(
        self, state: InferenceSessionState
    ) -> Optional[AIInferenceRecord]:
        """通过 LLM 生成推断。要求 ``self.llm_service.call`` 为协程。"""
        if self.llm_service is None:
            return None

        recent = self._recent_events_payload(state)
        payload = {
            "game_type": state.game_type,
            "game_phase": state.current_phase.value,
            "elapsed_minutes": round(
                (datetime.now(timezone.utc) - state.started_at).total_seconds() / 60.0,
                2,
            ),
            "recent_events": recent,
            "baseline": state.child_history or None,
        }

        # 调用 LLM，设置 10 秒超时防止阻塞
        result = await asyncio.wait_for(
            self.llm_service.call(
                system_prompt=BEHAVIOR_INFERENCE_PROMPT,
                user_message=build_inference_user_message(payload),
                output_schema={"type": "object"},
                temperature=0.4,
                max_tokens=400,
            ),
            timeout=10.0,
        )

        # 优先使用结构化输出，其次降级解析 content
        data = result.get("structured_output") if isinstance(result, dict) else None
        if data is None:
            content = (result or {}).get("content") or ""
            data = self._safe_json_loads(content)
        if not isinstance(data, dict):
            return None

        text = (data.get("inference_text") or "").strip()
        if not text:
            return None

        return AIInferenceRecord(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_id=state.session_id,
            inference_text=text,
            inference_type=data.get("inference_type") or "行为推断",
            valence=int(data.get("valence", 0) or 0),
            confidence=float(data.get("confidence", 0.6) or 0.6),
            is_confirmed=None,
        )

    def _generate_inference_via_rules(
        self, state: InferenceSessionState
    ) -> Optional[AIInferenceRecord]:
        """基于规则的简单推断（无 LLM 时的兜底实现）。"""
        recent = [
            e
            for e in state.events
            if (datetime.now(timezone.utc) - e.timestamp).total_seconds()
            <= RECENT_EVENT_WINDOW_SECONDS
        ]
        if not recent:
            return None

        type_counts = Counter(e.event_type for e in recent)
        positive = sum(1 for e in recent if e.valence > 0)
        negative = sum(1 for e in recent if e.valence < 0)
        total = len(recent)
        top_type, top_count = type_counts.most_common(1)[0]

        # 与基线对比（若提供）
        baseline_freq = state.child_history.get("avg_event_per_min") if state.child_history else None
        elapsed_min = max(
            (datetime.now(timezone.utc) - state.started_at).total_seconds() / 60.0,
            0.1,
        )
        cur_freq = total / elapsed_min

        baseline_clause = ""
        if baseline_freq:
            try:
                ratio = cur_freq / float(baseline_freq)
                if ratio >= 1.2:
                    baseline_clause = "（高于基线水平）"
                elif ratio <= 0.8:
                    baseline_clause = "（低于基线水平）"
            except (TypeError, ValueError, ZeroDivisionError):
                baseline_clause = ""

        if positive >= max(2, total * 0.6):
            text = f"参与度较高，主动「{top_type}」频率突出{baseline_clause}"
            valence = 1
            confidence = 0.6
            inference_type = "行为推断"
        elif negative >= max(2, total * 0.5):
            text = f"出现一定退缩或负面信号，需关注情绪状态{baseline_clause}"
            valence = -1
            confidence = 0.55
            inference_type = "模式推断"
        else:
            text = (
                f"当前以「{top_type}」为主（{top_count}次），整体参与平稳"
                f"{baseline_clause}"
            )
            valence = 0
            confidence = 0.5
            inference_type = "行为推断"

        return AIInferenceRecord(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_id=state.session_id,
            inference_text=text,
            inference_type=inference_type,
            valence=valence,
            confidence=confidence,
            is_confirmed=None,
        )

    # ------------------------------------------------------------------
    # 探测问题生成
    # ------------------------------------------------------------------

    async def generate_probe_question(
        self, session_id: str
    ) -> Optional[AIProbeQuestion]:
        """生成探测问题（如果当前条件满足）。"""
        state = self._sessions.get(session_id)
        if state is None:
            logger.warning(
                "[AIInferenceEngine] generate_probe_question: 未找到 session=%s",
                session_id,
            )
            return None

        # 已有未回答的 probe 时，避免叠加
        if state.pending_probe is not None:
            return None

        trigger = self._probe_trigger_reason(state)
        if trigger is None:
            return None

        question: Optional[AIProbeQuestion] = None
        if self.llm_service is not None:
            try:
                question = await self._generate_probe_via_llm(state, trigger)
            except Exception as exc:
                logger.warning(
                    "[AIInferenceEngine] LLM 探测生成失败，退化为规则: %s", exc
                )
                question = None

        if question is None:
            question = self._generate_probe_via_rules(state, trigger)

        if question is None:
            return None

        state.pending_probe = question
        state.last_probe_at = datetime.now(timezone.utc)
        self._probe_store[session_id].append(question)
        logger.info(
            "[AIInferenceEngine] 探测问题生成 session=%s id=%s text=%s trigger=%s",
            session_id,
            question.id,
            question.question_text,
            trigger,
        )
        return question

    def _probe_trigger_reason(
        self, state: InferenceSessionState
    ) -> Optional[str]:
        """判断当前是否需要触发探测问题，返回触发原因或 None。"""
        # 阶段切换触发（last_phase != current_phase 时）
        if state.last_phase != state.current_phase:
            return "phase_transition"

        # 数据稀疏触发：超过窗口无新事件
        last_event_ts = state.events[-1].timestamp if state.events else state.started_at
        idle = (datetime.now(timezone.utc) - last_event_ts).total_seconds()
        if idle >= SPARSE_DATA_WINDOW_SECONDS:
            # 同一稀疏窗口内，避免重复发问
            if (
                state.last_probe_at is None
                or (
                    datetime.now(timezone.utc) - state.last_probe_at
                ).total_seconds()
                >= SPARSE_DATA_WINDOW_SECONDS
            ):
                return "sparse_data"
        return None

    async def _generate_probe_via_llm(
        self, state: InferenceSessionState, trigger: str
    ) -> Optional[AIProbeQuestion]:
        """通过 LLM 生成探测问题。"""
        if self.llm_service is None:
            return None

        payload = {
            "game_type": state.game_type,
            "game_phase": state.current_phase.value,
            "trigger_reason": trigger,
            "recent_events": self._recent_events_payload(state, limit=5),
        }

        # 调用 LLM，设置 10 秒超时防止阻塞
        result = await asyncio.wait_for(
            self.llm_service.call(
                system_prompt=PROBE_QUESTION_PROMPT,
                user_message=build_probe_user_message(payload),
                output_schema={"type": "object"},
                temperature=0.5,
                max_tokens=300,
            ),
            timeout=10.0,
        )

        data = result.get("structured_output") if isinstance(result, dict) else None
        if data is None:
            data = self._safe_json_loads((result or {}).get("content") or "")
        if not isinstance(data, dict):
            return None

        text = (data.get("question_text") or "").strip()
        options = data.get("options") or []
        if not text or not isinstance(options, list) or len(options) < 2:
            return None

        return AIProbeQuestion(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_id=state.session_id,
            question_text=text,
            options=[str(o) for o in options][:4],
            selected_option=None,
            game_phase=state.current_phase,
        )

    def _generate_probe_via_rules(
        self, state: InferenceSessionState, trigger: str
    ) -> Optional[AIProbeQuestion]:
        """基于规则的探测问题模板。"""
        phase = state.current_phase
        game_type = state.game_type

        templates: dict[GamePhase, tuple[str, list[str]]] = {
            GamePhase.EXPLORATION: (
                f"当前在「{game_type}」探索阶段，孩子的初始反应是？",
                ["主动靠近材料", "观望但不参与", "回避或抗拒", "暂未注意"],
            ),
            GamePhase.INTERACTION: (
                f"在「{game_type}」中，孩子是否回应了你的互动？",
                ["主动回应/发起", "被动回应", "无明显回应", "暂未注意"],
            ),
            GamePhase.CLIMAX: (
                f"「{game_type}」高潮阶段，孩子的情感投入如何？",
                ["明显愉悦/兴奋", "平稳参与", "有抗拒或不耐", "暂未注意"],
            ),
            GamePhase.CLOSURE: (
                f"「{game_type}」收尾阶段，孩子能配合过渡吗？",
                ["平稳收尾", "有一定抗拒", "情绪明显波动", "暂未注意"],
            ),
        }

        text, options = templates.get(
            phase,
            (
                f"在「{game_type}」中，当前最显著的行为是？",
                ["主动互动", "被动跟随", "无明显反应", "暂未注意"],
            ),
        )

        # 数据稀疏触发时换更通用的问法
        if trigger == "sparse_data":
            text = (
                f"近 {int(SPARSE_DATA_WINDOW_SECONDS / 60)} 分钟内"
                f"未记录新行为，孩子目前状态如何？"
            )
            options = ["专注游戏中", "走神/离开", "情绪低落", "暂未注意"]

        return AIProbeQuestion(
            id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            session_id=state.session_id,
            question_text=text,
            options=options,
            selected_option=None,
            game_phase=phase,
        )

    # ------------------------------------------------------------------
    # 推断 / 探测查询与确认
    # ------------------------------------------------------------------

    def get_inferences(self, session_id: str) -> list[AIInferenceRecord]:
        """获取会话的所有推断（按时间顺序）。"""
        return list(self._inference_store.get(session_id, []))

    def confirm_inference(
        self, inference_id: str, is_confirmed: bool
    ) -> Optional[AIInferenceRecord]:
        """确认或否定一条推断。"""
        for records in self._inference_store.values():
            for record in records:
                if record.id == inference_id:
                    record.is_confirmed = bool(is_confirmed)
                    logger.info(
                        "[AIInferenceEngine] 推断确认 id=%s confirmed=%s",
                        inference_id,
                        is_confirmed,
                    )
                    return record
        logger.warning(
            "[AIInferenceEngine] confirm_inference: 未找到 id=%s", inference_id
        )
        return None

    def get_pending_probe(self, session_id: str) -> Optional[AIProbeQuestion]:
        """获取当前待回答的探测问题。"""
        state = self._sessions.get(session_id)
        if state is None:
            return None
        return state.pending_probe

    def respond_to_probe(self, probe_id: str, selected_option: str) -> None:
        """回应探测问题（更新 selected_option 并清空 pending）。"""
        for session_id, probes in self._probe_store.items():
            for probe in probes:
                if probe.id == probe_id:
                    probe.selected_option = selected_option
                    state = self._sessions.get(session_id)
                    if state is not None and state.pending_probe is not None:
                        if state.pending_probe.id == probe_id:
                            state.pending_probe = None
                    logger.info(
                        "[AIInferenceEngine] 探测问题已回应 id=%s option=%s",
                        probe_id,
                        selected_option,
                    )
                    return
        logger.warning(
            "[AIInferenceEngine] respond_to_probe: 未找到 id=%s", probe_id
        )

    # ------------------------------------------------------------------
    # 动态按钮推荐
    # ------------------------------------------------------------------

    def recommend_dynamic_buttons(
        self, game_type: str, child_history: Optional[dict] = None
    ) -> list[dict]:
        """
        根据游戏类型 + 历史高频行为推荐动态按钮列表。

        Args:
            game_type: 游戏类型（与 GAME_TYPE_BUTTONS 的键匹配）
            child_history: 可选的儿童历史数据，用于按高频行为重排：
                ``{"frequent_behaviors": ["imitation", "turn_taking"]}``

        Returns:
            按钮 dict 列表（每项含 id/label/icon/valence）
        """
        buttons = list(
            GAME_TYPE_BUTTONS.get(game_type, DEFAULT_DYNAMIC_BUTTONS)
        )

        # 历史高频行为：按提供的顺序前置
        if child_history and isinstance(child_history.get("frequent_behaviors"), list):
            frequent: list[str] = list(child_history["frequent_behaviors"])
            order = {bid: idx for idx, bid in enumerate(frequent)}
            buttons.sort(
                key=lambda b: order.get(b.get("id"), len(order) + 1)
            )

        # 复制返回，避免外部修改污染常量
        return [dict(b) for b in buttons]

    # ------------------------------------------------------------------
    # 工具方法
    # ------------------------------------------------------------------

    def _recent_events_payload(
        self, state: InferenceSessionState, limit: int = 20
    ) -> list[dict]:
        """构造给 LLM 的最近事件载荷。"""
        cutoff_ts = (
            datetime.now(timezone.utc).timestamp() - RECENT_EVENT_WINDOW_SECONDS
        )
        recent = [
            e for e in state.events if e.timestamp.timestamp() >= cutoff_ts
        ][-limit:]
        return [
            {
                "event_type": e.event_type,
                "valence": e.valence,
                "source": e.source.value if isinstance(e.source, EventSource) else str(e.source),
                "timestamp": e.timestamp.isoformat(),
                "detail": e.detail,
            }
            for e in recent
        ]

    @staticmethod
    def _safe_json_loads(content: str) -> Any:
        """容错地解析 JSON，自动剥离 ```json 代码块。"""
        if not content:
            return None
        text = content.strip()
        if text.startswith("```json"):
            text = text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif text.startswith("```"):
            text = text.split("```", 1)[1].split("```", 1)[0].strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None


__all__ = [
    "AIInferenceEngine",
    "InferenceSessionState",
    "GAME_TYPE_BUTTONS",
    "DEFAULT_DYNAMIC_BUTTONS",
]
