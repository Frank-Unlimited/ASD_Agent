"""
评估 API 端点
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional

from src.models.assessment import (
    AssessmentRequest,
    AssessmentResponse,
    AssessmentHistoryRequest,
    AssessmentHistoryResponse
)
from src.container import get_assessment_service

router = APIRouter(prefix="/api/assessment", tags=["assessment"])


@router.post("/generate", response_model=AssessmentResponse)
async def generate_assessment(
    request: AssessmentRequest,
    assessment_service = Depends(get_assessment_service)
):
    """
    生成完整评估
    
    调用三个 Agent：
    1. 兴趣挖掘 Agent
    2. 功能分析 Agent
    3. 综合评估 Agent
    """
    try:
        response = await assessment_service.generate_comprehensive_assessment(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{assessment_id}")
async def get_assessment(
    assessment_id: str,
    assessment_service = Depends(get_assessment_service)
):
    """获取评估报告"""
    try:
        assessment = assessment_service.sqlite.get_assessment(assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="评估不存在")
        return assessment
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/history", response_model=AssessmentHistoryResponse)
async def get_assessment_history(
    request: AssessmentHistoryRequest,
    assessment_service = Depends(get_assessment_service)
):
    """获取评估历史"""
    try:
        history = assessment_service.sqlite.get_assessment_history(
            child_id=request.child_id,
            assessment_type=request.assessment_type,
            limit=request.limit
        )
        
        return AssessmentHistoryResponse(
            child_id=request.child_id,
            assessments=history,
            total=len(history),
            message="评估历史获取成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ['router']
