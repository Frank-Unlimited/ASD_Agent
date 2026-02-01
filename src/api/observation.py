"""
行为观察 API
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, Any
from src.container import container


router = APIRouter(prefix="/api/observation", tags=["observation"])


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
