"""
行为观察 API
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel, Field

from src.container import container
from src.models.behavior_record import (
    BehaviorRecord,
    EventSource,
    GamePhase,
)


router = APIRouter(prefix="/api/observation", tags=["observation"])


# ============ 游戏实施阶段：行为事件存储与去重 ============

# session_id -> List[BehaviorRecord]
BEHAVIOR_STORE: Dict[str, List[BehaviorRecord]] = {}

# (session_id, event_type) -> 最近一次记录的时间戳，用于 5 秒内去重
_LAST_EVENT_TS: Dict[Tuple[str, str], datetime] = {}

# 去重窗口（秒）
DEDUP_WINDOW_SECONDS = 5


# ============ Memory 服务延迟初始化 ============

_memory_service = None

async def get_memory():
    """获取 Memory 服务（延迟初始化）"""
    global _memory_service
    if _memory_service is None:
        from services.Memory.service import get_memory_service
        _memory_service = await get_memory_service()
    return _memory_service


# ============ 请求模型 ============

class TextObservationRequest(BaseModel):
    """文字观察请求"""
    child_id: str
    text: str
    context: Optional[Dict[str, Any]] = None


class QuickButtonRequest(BaseModel):
    """快速按钮请求"""
    child_id: str
    button_type: str
    context: Optional[Dict[str, Any]] = None


class BehaviorRecordRequest(BaseModel):
    """
    游戏实施阶段的行为事件记录请求

    用于接收家长点击按钮/AI推断/快照产生的行为事件。
    字段与 BehaviorRecord 一致，但 id/timestamp 由服务器生成。
    """
    session_id: str = Field(..., description="会话ID")
    game_type: str = Field(..., description="游戏类型")
    event_type: str = Field(..., description="事件类型，如 eye_contact/interaction")
    detail: Optional[str] = Field(None, description="二级细节")
    valence: int = Field(..., ge=-1, le=1, description="+1正面/0中性/-1负面")
    source: EventSource = Field(
        EventSource.PARENT_CLICK, description="事件来源"
    )
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="置信度")
    game_phase: Optional[GamePhase] = Field(None, description="游戏阶段")
    related_interest: Optional[str] = Field(None, description="关联兴趣点")


# ============ API 端点 ============

@router.post("/text")
async def record_text_observation(request: TextObservationRequest):
    """
    记录文字观察
    
    示例：
    ```json
    {
        "child_id": "child_001",
        "text": "今天小明主动把积木递给我，还看着我的眼睛笑了",
        "context": {
            "location": "家里客厅",
            "activity": "积木游戏"
        }
    }
    ```
    """
    print("\n" + "="*80)
    print("[API] POST /api/observation/text")
    print(f"[输入] child_id: {request.child_id}")
    print(f"[输入] text: {request.text}")
    print(f"[输入] context: {request.context}")
    
    try:
        # 获取 Memory 服务
        memory_service = await get_memory()
        
        # 确保 observation_service 有 memory
        observation_service = container.get('observation')
        if observation_service.memory is None:
            observation_service.memory = memory_service
        
        result = await observation_service.record_text_observation(
            child_id=request.child_id,
            text=request.text,
            context=request.context
        )
        
        print(f"[输出] success: {result['success']}")
        print(f"[输出] behavior_id: {result['behavior_id']}")
        print(f"[输出] description: {result['description']}")
        print(f"[输出] event_type: {result['event_type']}")
        print(f"[输出] significance: {result['significance']}")
        print("="*80 + "\n")
        
        return result
    except Exception as e:
        print(f"[错误] {str(e)}")
        print("="*80 + "\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice")
async def record_voice_observation(
    child_id: str,
    audio: UploadFile = File(...),
    context: Optional[str] = None
):
    """
    记录语音观察
    
    上传音频文件，自动转文字并记录
    """
    try:
        import json
        import tempfile
        import os
        
        # 保存上传的音频文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            content = await audio.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        try:
            observation_service = container.get('observation')
            
            # 解析 context
            context_dict = json.loads(context) if context else None
            
            result = await observation_service.record_voice_observation(
                child_id=child_id,
                audio_file=temp_path,
                context=context_dict
            )
            
            return result
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/quick")
async def record_quick_button(request: QuickButtonRequest):
    """
    快速按钮记录
    
    预设按钮类型：
    - eye_contact: 主动眼神接触
    - share_toy: 主动分享玩具
    - emotional_outburst: 情绪波动
    - refuse_interaction: 拒绝互动
    - first_time: 首次新行为
    - breakthrough: 突破性进步
    
    示例：
    ```json
    {
        "child_id": "child_001",
        "button_type": "eye_contact",
        "context": {
            "location": "幼儿园"
        }
    }
    ```
    """
    print("\n" + "="*80)
    print("[API] POST /api/observation/quick")
    print(f"[输入] child_id: {request.child_id}")
    print(f"[输入] button_type: {request.button_type}")
    print(f"[输入] context: {request.context}")
    
    try:
        # 获取 Memory 服务
        memory_service = await get_memory()
        
        observation_service = container.get('observation')
        if observation_service.memory is None:
            observation_service.memory = memory_service
            
        result = await observation_service.record_quick_button(
            child_id=request.child_id,
            button_type=request.button_type,
            context=request.context
        )
        
        print(f"[输出] success: {result['success']}")
        print(f"[输出] behavior_id: {result['behavior_id']}")
        print(f"[输出] description: {result['description']}")
        print("="*80 + "\n")
        
        return result
    except Exception as e:
        print(f"[错误] {str(e)}")
        print("="*80 + "\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent/{child_id}")
async def get_recent_observations(
    child_id: str,
    limit: int = 20,
    event_type: Optional[str] = None,
    significance: Optional[str] = None
):
    """
    获取最近的观察记录
    
    参数：
    - child_id: 孩子ID
    - limit: 返回数量（默认20）
    - event_type: 事件类型过滤（可选）
    - significance: 重要性过滤（可选）
    """
    print("\n" + "="*80)
    print("[API] GET /api/observation/recent/{child_id}")
    print(f"[输入] child_id: {child_id}")
    print(f"[输入] limit: {limit}")
    print(f"[输入] event_type: {event_type}")
    print(f"[输入] significance: {significance}")
    
    try:
        # 获取 Memory 服务
        memory_service = await get_memory()
        
        observation_service = container.get('observation')
        if observation_service.memory is None:
            observation_service.memory = memory_service
        
        filters = {}
        if event_type:
            filters['event_type'] = event_type
        if significance:
            filters['significance'] = significance
        
        observations = await observation_service.get_recent_observations(
            child_id=child_id,
            limit=limit,
            filters=filters if filters else None
        )
        
        result = {
            "success": True,
            "count": len(observations),
            "observations": observations
        }
        
        print(f"[输出] count: {result['count']}")
        print("="*80 + "\n")
        
        return result
        
    except Exception as e:
        print(f"[错误] {str(e)}")
        print("="*80 + "\n")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/{child_id}")
async def get_observation_stats(child_id: str, days: int = 7):
    """
    获取观察统计
    
    参数：
    - child_id: 孩子ID
    - days: 统计天数（默认7天）
    """
    try:
        # 获取 Memory 服务
        memory_service = await get_memory()
        
        observation_service = container.get('observation')
        if observation_service.memory is None:
            observation_service.memory = memory_service
            
        stats = await observation_service.get_observation_stats(
            child_id=child_id,
            days=days
        )
        
        return {
            "success": True,
            "stats": stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============ 游戏实施阶段的行为事件记录 ============

@router.post("/record")
async def record_behavior_event(request: BehaviorRecordRequest):
    """
    记录一条行为事件（增强版）

    适用于游戏实施阶段的实时记录，支持:
    - source: 事件来源（parent_click/timed_snapshot/ai_probe_response/ai_inferred）
    - confidence: 置信度
    - game_phase: 游戏阶段

    去重逻辑：同一 session + 同一 event_type 在 5 秒内重复请求 返回 409。
    """
    now = datetime.now()
    dedup_key = (request.session_id, request.event_type)
    last_ts = _LAST_EVENT_TS.get(dedup_key)
    if last_ts is not None and (now - last_ts).total_seconds() < DEDUP_WINDOW_SECONDS:
        # 5 秒内重复请求 - 幂等冲突
        raise HTTPException(
            status_code=409,
            detail=(
                f"重复请求：session={request.session_id}, "
                f"event_type={request.event_type}, 距上次仅 "
                f"{(now - last_ts).total_seconds():.2f}s"
            ),
        )
    _LAST_EVENT_TS[dedup_key] = now

    record = BehaviorRecord(
        id=f"evt_{uuid4().hex[:12]}",
        timestamp=now,
        session_id=request.session_id,
        game_type=request.game_type,
        event_type=request.event_type,
        detail=request.detail,
        valence=request.valence,
        source=request.source,
        confidence=request.confidence,
        game_phase=request.game_phase,
        related_interest=request.related_interest,
    )
    BEHAVIOR_STORE.setdefault(request.session_id, []).append(record)

    # 同步会话统计（避免循环导入，运行时导入）
    try:
        from src.api.game_session import SESSION_STORE
        session = SESSION_STORE.get(request.session_id)
        if session is not None:
            session.total_events += 1
            if request.source == EventSource.AI_INFERRED:
                session.ai_inferences_count += 1
    except Exception:
        # 会话不存在不阻断事件记录本身
        pass

    return {
        "success": True,
        "data": record.model_dump(mode="json"),
        "message": "行为事件已记录",
    }
