"""
聊天 API
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional, AsyncGenerator
from pydantic import BaseModel, Field
import json

from src.container import (
    get_memory_service,
    get_sqlite_service,
    get_observation_service,
    get_game_recommender,
    get_game_summarizer,
    get_assessment_service
)
from services.Chat import ChatService, ChatTools
from services.Report import ReportService

router = APIRouter(prefix="/api/chat", tags=["聊天"])


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str = Field(..., description="角色（user/assistant）")
    content: str = Field(..., description="消息内容")


class ChatRequest(BaseModel):
    """聊天请求"""
    message: str = Field(..., description="用户消息")
    child_id: str = Field(..., description="当前孩子ID")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="对话历史"
    )


class ChatResponse(BaseModel):
    """聊天响应"""
    response: str = Field(..., description="助手回复")
    tool_calls: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="调用的工具列表"
    )
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="更新后的对话历史"
    )


async def get_chat_service(
    memory_service = Depends(get_memory_service),
    sqlite_service = Depends(get_sqlite_service),
    observation_service = Depends(get_observation_service),
    game_recommender = Depends(get_game_recommender),
    game_summarizer = Depends(get_game_summarizer),
    assessment_service = Depends(get_assessment_service)
):
    """获取聊天服务"""
    # 创建报告服务
    report_service = ReportService(sqlite_service, memory_service)
    
    # 创建工具集
    chat_tools = ChatTools(
        memory_service=memory_service,
        sqlite_service=sqlite_service,
        observation_service=observation_service,
        game_recommender=game_recommender,
        game_summarizer=game_summarizer,
        assessment_service=assessment_service,
        report_service=report_service
    )
    
    # 创建聊天服务
    return ChatService(chat_tools)


@router.post("/message", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    发送聊天消息（非流式）
    
    支持的功能：
    - 记录行为观察
    - 推荐游戏
    - 查询档案和评估
    - 查询游戏历史
    - 生成评估和报告
    """
    try:
        # print(f"[Chat API] 收到消息: {request.message[:50]}...")
        
        # 转换对话历史格式
        conversation_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.conversation_history
        ]
        
        # 调用聊天服务
        result = await chat_service.chat(
            message=request.message,
            child_id=request.child_id,
            conversation_history=conversation_history
        )
        
        # 转换回响应格式
        response_history = [
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in result["conversation_history"]
        ]
        
        return ChatResponse(
            response=result["response"],
            tool_calls=result["tool_calls"],
            conversation_history=response_history
        )
    
    except Exception as e:
        print(f"[Chat API] 失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@router.post("/stream")
async def stream_message(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    发送聊天消息（流式返回）
    
    返回 SSE 流，事件类型：
    - tool_call: 工具调用开始
    - tool_result: 工具执行结果
    - content: 文本内容（逐字返回）
    - done: 完成
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # print(f"[Chat API Stream] 收到消息: {request.message[:50]}...")
            
            # 转换对话历史格式
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
            
            # 调用流式聊天服务
            async for event in chat_service.chat_stream(
                message=request.message,
                child_id=request.child_id,
                conversation_history=conversation_history
            ):
                # 发送 SSE 事件
                event_type = event.get("type")
                data = event.get("data")
                
                # 立即发送，不缓冲
                event_str = f"event: {event_type}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
                yield event_str
                
                # 添加调试日志
                # print(f"[Chat API Stream] 发送事件: {event_type}")
            
        except Exception as e:
            print(f"[Chat API Stream] 失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 发送错误事件
            yield f"event: error\ndata: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用 nginx 缓冲
            "Content-Type": "text/event-stream; charset=utf-8"
        }
    )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "chat"}
