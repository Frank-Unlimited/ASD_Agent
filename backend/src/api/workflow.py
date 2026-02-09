"""
工作流 API 路由
支持分步执行的工作流控制
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from src.models.state import DynamicInterventionState
from src.workflow.workflow import (
    assessment_node,
    weekly_plan_node,
    game_start_node,
    game_end_node,
    preliminary_summary_node,
    feedback_form_node,
    final_summary_node,
    memory_update_node,
    reassessment_node,
    should_adjust_plan
)

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

# 内存存储工作流状态
workflow_store: Dict[str, Dict[str, Any]] = {}


# ============ 请求/响应模型 ============

class InitWorkflowRequest(BaseModel):
    childId: str = "child-001"
    childName: str = "辰辰"
    reportPath: str = "/mock/report.pdf"
    gameId: str = "game-001"


class SubmitFeedbackRequest(BaseModel):
    feedback: Dict[str, Any]


class WorkflowResponse(BaseModel):
    success: bool
    workflowId: Optional[str] = None
    state: Optional[Dict[str, Any]] = None
    currentNode: Optional[str] = None
    nextNode: Optional[str] = None
    message: Optional[str] = None
    executionTime: Optional[float] = None


# ============ 节点映射 ============

NODE_FUNCTIONS = {
    "assessment": assessment_node,
    "weekly_plan": weekly_plan_node,
    "game_start": game_start_node,
    "game_end": game_end_node,
    "preliminary_summary": preliminary_summary_node,
    "feedback_form": feedback_form_node,
    "final_summary": final_summary_node,
    "memory_update": memory_update_node,
    "reassessment": reassessment_node,
}

NODE_SEQUENCE = [
    "assessment",
    "weekly_plan",
    "game_start",
    "game_end",
    "preliminary_summary",
    "feedback_form",
    "final_summary",
    "memory_update",
    "reassessment",
]


# ============ API 端点 ============

@router.post("/init", response_model=WorkflowResponse)
async def init_workflow(request: InitWorkflowRequest):
    """
    初始化工作流
    创建初始 State 并返回 workflowId
    """
    workflow_id = f"wf-{uuid.uuid4().hex[:8]}"
    
    # 创建初始 State
    initial_state: DynamicInterventionState = {
        "childTimeline": {
            "profile": {
                "childId": request.childId,
                "name": request.childName,
                "age": 2.5,
                "birthDate": "2023-07-01",
                "diagnosis": "ASD轻度",
                "interests": ["旋转物体", "水流"],
                "customDimensions": {}
            },
            "metrics": {},
            "microObservations": []
        },
        "currentContext": {
            "recentTrends": {},
            "attentionPoints": [],
            "activeGoals": [],
            "lastUpdated": None
        },
        "currentSession": {},
        "currentWeeklyPlan": None,
        "sessionHistory": None,
        "conversationHistory": None,
        "workflow": {
            "currentNode": "start",
            "nextNode": "assessment",
            "isHITLPaused": False,
            "checkpointId": None,
            "needsAdjustment": None
        },
        "tempData": {
            "reportPath": request.reportPath,
            "gameId": request.gameId
        }
    }
    
    # 存储到内存
    workflow_store[workflow_id] = {
        "state": initial_state,
        "currentNode": "start",
        "history": [],
        "createdAt": datetime.now().isoformat()
    }
    
    return WorkflowResponse(
        success=True,
        workflowId=workflow_id,
        state=initial_state,
        currentNode="start",
        nextNode="assessment",
        message="工作流初始化成功"
    )


@router.post("/{workflow_id}/execute/{node_name}", response_model=WorkflowResponse)
async def execute_node(workflow_id: str, node_name: str):
    """
    执行单个节点
    """
    # 检查工作流是否存在
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 检查节点是否有效
    if node_name not in NODE_FUNCTIONS:
        raise HTTPException(status_code=400, detail=f"无效的节点名称: {node_name}")
    
    workflow_data = workflow_store[workflow_id]
    current_state = workflow_data["state"]
    
    # 执行节点
    start_time = datetime.now()
    try:
        node_function = NODE_FUNCTIONS[node_name]
        result = await node_function(current_state)
        
        # 更新 State
        updated_state = {**current_state, **result}
        
        # 确定下一个节点
        next_node = updated_state["workflow"].get("nextNode")
        
        # 特殊处理：feedback_form 节点后需要等待用户提交反馈
        if node_name == "feedback_form":
            next_node = "hitl_pause"  # 标记为暂停状态
        
        # 特殊处理：reassessment 节点后需要判断是否调整
        if node_name == "reassessment":
            decision = should_adjust_plan(updated_state)
            if decision == "weekly_plan":
                next_node = "weekly_plan"
            else:
                next_node = "end"
        
        # 更新存储
        workflow_data["state"] = updated_state
        workflow_data["currentNode"] = node_name
        workflow_data["history"].append({
            "node": node_name,
            "timestamp": datetime.now().isoformat(),
            "duration": (datetime.now() - start_time).total_seconds()
        })
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return WorkflowResponse(
            success=True,
            workflowId=workflow_id,
            state=updated_state,
            currentNode=node_name,
            nextNode=next_node,
            message=f"节点 {node_name} 执行成功",
            executionTime=execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"节点执行失败: {str(e)}")


@router.post("/{workflow_id}/submit-feedback", response_model=WorkflowResponse)
async def submit_feedback(workflow_id: str, request: SubmitFeedbackRequest):
    """
    提交 HITL 反馈
    从 feedback_form 节点恢复执行
    """
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    workflow_data = workflow_store[workflow_id]
    current_state = workflow_data["state"]
    
    # 将反馈添加到 State
    current_state["currentSession"]["parentFeedback"] = request.feedback
    
    # 更新工作流状态
    current_state["workflow"]["isHITLPaused"] = False
    current_state["workflow"]["nextNode"] = "final_summary"
    
    workflow_data["state"] = current_state
    
    return WorkflowResponse(
        success=True,
        workflowId=workflow_id,
        state=current_state,
        currentNode="feedback_form",
        nextNode="final_summary",
        message="反馈提交成功，工作流继续执行"
    )


@router.get("/{workflow_id}/status", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: str):
    """
    获取工作流当前状态
    """
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    workflow_data = workflow_store[workflow_id]
    
    return WorkflowResponse(
        success=True,
        workflowId=workflow_id,
        state=workflow_data["state"],
        currentNode=workflow_data["currentNode"],
        message="获取状态成功"
    )


@router.post("/{workflow_id}/reset", response_model=WorkflowResponse)
async def reset_workflow(workflow_id: str):
    """
    重置工作流
    """
    if workflow_id not in workflow_store:
        raise HTTPException(status_code=404, detail="工作流不存在")
    
    # 删除工作流
    del workflow_store[workflow_id]
    
    return WorkflowResponse(
        success=True,
        message="工作流已重置"
    )


@router.get("/list")
async def list_workflows():
    """
    列出所有工作流（调试用）
    """
    return {
        "total": len(workflow_store),
        "workflows": [
            {
                "workflowId": wf_id,
                "currentNode": data["currentNode"],
                "createdAt": data["createdAt"]
            }
            for wf_id, data in workflow_store.items()
        ]
    }
