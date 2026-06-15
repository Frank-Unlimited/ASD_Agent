"""
AI 推断与探测问题 API（游戏实施阶段）

包含两类资源：
1. AIInferenceRecord：AI 自动推断（家长可确认/否定）
2. AIProbeQuestion：AI 主动发起的探测问题（家长选择选项作答）

本模块通过容器中注册的 ObservationServiceManager 获取 AIInferenceEngine 实例，
支持真实 LLM 推断结果生成；不可用时安全降级到内存字典模式。
"""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.api.game_session import SESSION_STORE
from src.models.behavior_record import (
    AIInferenceRecord,
    AIProbeQuestion,
    GamePhase,
)


# 推断与探测共享同一个 router 前缀使用方式：
# - /api/ai-inference/...
# - /api/ai-probe/...
# 出于“一个文件一个 router 注册”的简洁性，这里用一个 router 暴露两组路径。
router = APIRouter(tags=["AI 推断与探测（实施阶段）"])


# ============ 内存存储（兼容降级模式） ============

# session_id -> List[AIInferenceRecord]
INFERENCE_STORE: Dict[str, List[AIInferenceRecord]] = {}

# inference_id -> AIInferenceRecord
INFERENCE_INDEX: Dict[str, AIInferenceRecord] = {}

# session_id -> List[AIProbeQuestion]
PROBE_STORE: Dict[str, List[AIProbeQuestion]] = {}

# probe_id -> AIProbeQuestion
PROBE_INDEX: Dict[str, AIProbeQuestion] = {}


# ============ 获取 AI 推断引擎实例 ============

def _get_inference_engine():
    """
    从容器中获取 AIInferenceEngine 实例。

    如果 ObservationServiceManager 未注册，返回 None（降级到内存字典模式）。
    """
    try:
        from src.container import container
        if container.has('observation_manager'):
            manager = container.get('observation_manager')
            return manager.inference_engine
    except Exception:
        pass
    return None


# ============ 请求/响应模型 ============

class ConfirmInferenceReq(BaseModel):
    """确认/否定推断"""
    is_confirmed: bool = Field(..., description="True=确认 / False=否定")


class ProbeRespondReq(BaseModel):
    """回应探测问题"""
    selected_option: str = Field(..., description="家长选择的选项文本")


class GenerateInferenceReq(BaseModel):
    """主动触发 AI 推断生成"""
    session_id: str = Field(..., description="会话ID")


class GenerateProbeReq(BaseModel):
    """主动触发 AI 探测问题生成"""
    session_id: str = Field(..., description="会话ID")


class StandardResp(BaseModel):
    """标准响应包装"""
    success: bool
    data: Optional[dict] = None
    message: str = ""


class StandardListResp(BaseModel):
    """列表响应"""
    success: bool
    data: List[dict] = Field(default_factory=list)
    message: str = ""


# ============ 内部工具 ============

def _ensure_session_exists(session_id: str) -> None:
    """确保会话存在，否则抛 404"""
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail=f"会话不存在: {session_id}")


# ============ 测试/工具端点（便于前端联调） ============

class CreateInferenceReq(BaseModel):
    """手动创建一条 AI 推断（占位接口，便于前端联调；正式由 LLM 服务调用）"""
    session_id: str
    inference_text: str
    inference_type: str = "行为推断"
    valence: int = 0
    confidence: float = 0.6


@router.post("/api/ai-inference/_create", include_in_schema=True)
async def create_inference(req: CreateInferenceReq) -> StandardResp:
    """
    占位创建 AI 推断（仅供联调使用）

    生产环境中此接口由后端 LLM 服务内部调用，前端不应直接使用。
    """
    _ensure_session_exists(req.session_id)
    record = AIInferenceRecord(
        id=f"inf_{uuid4().hex[:12]}",
        timestamp=datetime.now(),
        session_id=req.session_id,
        inference_text=req.inference_text,
        inference_type=req.inference_type,
        valence=req.valence,
        confidence=req.confidence,
    )
    INFERENCE_STORE.setdefault(req.session_id, []).append(record)
    INFERENCE_INDEX[record.id] = record

    # 同步会话的推断计数
    session = SESSION_STORE.get(req.session_id)
    if session is not None:
        session.ai_inferences_count += 1

    return StandardResp(
        success=True,
        data=record.model_dump(mode="json"),
        message="AI 推断已创建",
    )


@router.post("/api/ai-inference/generate")
async def generate_inference(req: GenerateInferenceReq) -> StandardResp:
    """
    主动触发 AI 推断生成（通过 LLM 或规则引擎）。

    如果推断引擎可用，将调用真实 LLM 服务生成推断；
    LLM 不可用或调用失败时自动降级到规则推断。
    """
    _ensure_session_exists(req.session_id)
    engine = _get_inference_engine()
    if engine is None:
        return StandardResp(
            success=False,
            data=None,
            message="AI 推断引擎未初始化，请先启动会话",
        )

    record = await engine.generate_inference(req.session_id)
    if record is None:
        return StandardResp(
            success=True,
            data=None,
            message="未满足推断条件（频率限制或数据不足）",
        )

    # 同步到 API 层内存存储（保持已有 GET 接口兼容）
    INFERENCE_STORE.setdefault(req.session_id, []).append(record)
    INFERENCE_INDEX[record.id] = record

    # 同步会话计数
    session = SESSION_STORE.get(req.session_id)
    if session is not None:
        session.ai_inferences_count += 1

    return StandardResp(
        success=True,
        data=record.model_dump(mode="json"),
        message="AI 推断已生成",
    )


# ============ AI 推断端点 ============

@router.get("/api/ai-inference/{session_id}")
async def list_inferences(session_id: str) -> StandardListResp:
    """获取该会话的全部 AI 推断列表（合并引擎内部与内存存储）"""
    _ensure_session_exists(session_id)

    # 合并两个数据源：引擎内部存储 + API 层内存存储
    seen_ids: set = set()
    all_records: list = []

    # 优先从推断引擎获取（包含自动触发的推断）
    engine = _get_inference_engine()
    if engine is not None:
        for r in engine.get_inferences(session_id):
            if r.id not in seen_ids:
                seen_ids.add(r.id)
                all_records.append(r)

    # 补充 API 层内存存储中的记录（包含手动创建的）
    for r in INFERENCE_STORE.get(session_id, []):
        if r.id not in seen_ids:
            seen_ids.add(r.id)
            all_records.append(r)

    # 按时间排序
    all_records.sort(key=lambda x: x.timestamp)

    return StandardListResp(
        success=True,
        data=[r.model_dump(mode="json") for r in all_records],
        message=f"共 {len(all_records)} 条推断",
    )


@router.put("/api/ai-inference/{inference_id}/confirm")
async def confirm_inference(
    inference_id: str, req: ConfirmInferenceReq
) -> StandardResp:
    """
    确认/否定某条 AI 推断

    is_confirmed=True  -> 家长确认推断成立
    is_confirmed=False -> 家长否定推断
    """
    # 尝试通过推断引擎确认
    engine = _get_inference_engine()
    if engine is not None:
        engine.confirm_inference(inference_id, req.is_confirmed)

    # 同时更新内存存储
    record = INFERENCE_INDEX.get(inference_id)
    if record is None:
        # 如果内存存储中找不到，可能是引擎内部生成的
        if engine is not None:
            return StandardResp(
                success=True,
                data={"inference_id": inference_id, "is_confirmed": req.is_confirmed},
                message="推断确认状态已更新",
            )
        raise HTTPException(status_code=404, detail=f"推断不存在: {inference_id}")

    record.is_confirmed = req.is_confirmed
    return StandardResp(
        success=True,
        data=record.model_dump(mode="json"),
        message="推断确认状态已更新",
    )


# ============ AI 探测问题端点 ============

class CreateProbeReq(BaseModel):
    """手动创建一条 AI 探测问题（占位接口，便于前端联调）"""
    session_id: str
    question_text: str
    options: List[str]
    game_phase: Optional[GamePhase] = None


@router.post("/api/ai-probe/_create", include_in_schema=True)
async def create_probe(req: CreateProbeReq) -> StandardResp:
    """占位创建 AI 探测问题（仅供联调使用）"""
    _ensure_session_exists(req.session_id)
    if not req.options:
        raise HTTPException(status_code=422, detail="探测问题必须提供至少一个选项")

    probe = AIProbeQuestion(
        id=f"probe_{uuid4().hex[:12]}",
        timestamp=datetime.now(),
        session_id=req.session_id,
        question_text=req.question_text,
        options=req.options,
        game_phase=req.game_phase,
    )
    PROBE_STORE.setdefault(req.session_id, []).append(probe)
    PROBE_INDEX[probe.id] = probe
    return StandardResp(
        success=True,
        data=probe.model_dump(mode="json"),
        message="探测问题已创建",
    )


@router.get("/api/ai-probe/{session_id}")
async def get_pending_probe(session_id: str) -> StandardResp:
    """
    获取该会话当前待回答的探测问题

    优先从 AIInferenceEngine 获取；如不可用则回退到内存存储。
    """
    _ensure_session_exists(session_id)

    # 优先尝试从推断引擎获取
    engine = _get_inference_engine()
    if engine is not None:
        probe = engine.get_pending_probe(session_id)
        if probe is not None:
            return StandardResp(
                success=True,
                data=probe.model_dump(mode="json") if hasattr(probe, 'model_dump') else {
                    "id": probe.id,
                    "timestamp": probe.timestamp.isoformat() if probe.timestamp else None,
                    "session_id": probe.session_id,
                    "question_text": probe.question_text,
                    "options": probe.options,
                    "selected_option": probe.selected_option,
                    "game_phase": probe.game_phase.value if probe.game_phase else None,
                },
                message="获取探测问题成功",
            )

    # 回退到内存存储
    pending = [
        p for p in PROBE_STORE.get(session_id, []) if p.selected_option is None
    ]
    if not pending:
        return StandardResp(success=True, data=None, message="当前无待回答的探测问题")

    latest = max(pending, key=lambda x: x.timestamp)
    return StandardResp(
        success=True,
        data=latest.model_dump(mode="json"),
        message="获取探测问题成功",
    )


@router.post("/api/ai-probe/generate")
async def generate_probe(req: GenerateProbeReq) -> StandardResp:
    """
    主动触发 AI 探测问题生成（通过 LLM 或规则引擎）。

    如果推断引擎可用，将调用真实 LLM 服务生成探测问题；
    LLM 不可用或调用失败时自动降级到规则模板。
    """
    _ensure_session_exists(req.session_id)
    engine = _get_inference_engine()
    if engine is None:
        return StandardResp(
            success=False,
            data=None,
            message="AI 推断引擎未初始化，请先启动会话",
        )

    probe = await engine.generate_probe_question(req.session_id)
    if probe is None:
        return StandardResp(
            success=True,
            data=None,
            message="未满足探测触发条件（已有未回答探测或无触发条件）",
        )

    # 同步到 API 层内存存储
    PROBE_STORE.setdefault(req.session_id, []).append(probe)
    PROBE_INDEX[probe.id] = probe

    return StandardResp(
        success=True,
        data=probe.model_dump(mode="json") if hasattr(probe, 'model_dump') else {
            "id": probe.id,
            "timestamp": probe.timestamp.isoformat() if probe.timestamp else None,
            "session_id": probe.session_id,
            "question_text": probe.question_text,
            "options": probe.options,
            "selected_option": probe.selected_option,
            "game_phase": probe.game_phase.value if probe.game_phase else None,
        },
        message="AI 探测问题已生成",
    )


@router.post("/api/ai-probe/{probe_id}/respond")
async def respond_probe(probe_id: str, req: ProbeRespondReq) -> StandardResp:
    """回应探测问题（写入家长选择的选项）"""
    # 优先尝试通过推断引擎响应
    engine = _get_inference_engine()
    if engine is not None:
        engine.respond_to_probe(probe_id, req.selected_option)

    # 同时更新内存存储
    probe = PROBE_INDEX.get(probe_id)
    if probe is None:
        # 如果内存存储中找不到，可能是由引擎生成的，返回成功
        if engine is not None:
            return StandardResp(
                success=True,
                data={"probe_id": probe_id, "selected_option": req.selected_option},
                message="探测问题已记录",
            )
        raise HTTPException(status_code=404, detail=f"探测问题不存在: {probe_id}")

    if probe.selected_option is not None:
        raise HTTPException(status_code=400, detail="该探测问题已被回答")

    if req.selected_option not in probe.options:
        raise HTTPException(
            status_code=422,
            detail=f"选项无效，必须为以下之一: {probe.options}",
        )

    probe.selected_option = req.selected_option
    return StandardResp(
        success=True,
        data=probe.model_dump(mode="json"),
        message="探测问题已记录",
    )
