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


@router.get("/{assessment_id}/export")
async def export_assessment(
    assessment_id: str,
    format: str = "json",
    assessment_service = Depends(get_assessment_service)
):
    """
    导出评估报告
    
    支持格式：
    - json: JSON 格式
    - markdown: Markdown 格式（适合打印）
    """
    try:
        assessment = assessment_service.sqlite.get_assessment(assessment_id)
        if not assessment:
            raise HTTPException(status_code=404, detail="评估不存在")
        
        if format == "json":
            from fastapi.responses import JSONResponse
            return JSONResponse(content=assessment)
        
        elif format == "markdown":
            from fastapi.responses import PlainTextResponse
            markdown_content = _generate_markdown_report(assessment)
            return PlainTextResponse(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f"attachment; filename=assessment_{assessment_id}.md"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _generate_markdown_report(assessment: dict) -> str:
    """生成 Markdown 格式的评估报告"""
    report = assessment.get('report', {})
    
    md = f"""# 评估报告

**评估ID**: {assessment['assessment_id']}  
**孩子ID**: {assessment['child_id']}  
**评估类型**: {assessment['assessment_type']}  
**评估时间**: {assessment['timestamp']}  

---

## 综合评分

**{report.get('overall_score', 0)}/10**

## 整体评价

{report.get('overall_assessment', '')}

---

## 兴趣热力图

"""
    
    # 兴趣热力图
    interest_heatmap = assessment.get('interest_heatmap', {})
    if interest_heatmap and interest_heatmap.get('dimensions'):
        md += f"**整体兴趣广度**: {interest_heatmap.get('overall_breadth', '')}\n\n"
        
        for name, dim in interest_heatmap['dimensions'].items():
            trend_emoji = {'increasing': '📈', 'stable': '➡️', 'decreasing': '📉'}.get(dim.get('trend', ''), '➡️')
            md += f"### {dim.get('dimension_name', name)}\n"
            md += f"- **强度**: {dim.get('strength', 0):.1f}/10\n"
            md += f"- **趋势**: {trend_emoji} {dim.get('trend', '')}\n"
            md += f"- **置信度**: {dim.get('confidence', '')}\n\n"
    
    md += "\n---\n\n## 功能维度趋势\n\n"
    
    # 功能维度趋势
    dimension_trends = assessment.get('dimension_trends', {})
    if dimension_trends and dimension_trends.get('active_dimensions'):
        for name, dim in dimension_trends['active_dimensions'].items():
            trend_emoji = {'improving': '📈', 'stable': '➡️', 'declining': '📉'}.get(dim.get('trend', ''), '➡️')
            md += f"### {dim.get('dimension_name', name)}\n"
            md += f"- **当前水平**: {dim.get('current_level', 0):.1f}/10\n"
            md += f"- **基线**: {dim.get('baseline', 0):.1f}/10\n"
            md += f"- **变化**: {dim.get('change', '')}\n"
            md += f"- **趋势**: {trend_emoji} {dim.get('trend', '')}\n\n"
    
    md += "\n---\n\n## 干预建议\n\n"
    
    # 干预建议
    recommendations = report.get('recommendations', [])
    for i, rec in enumerate(recommendations, 1):
        md += f"{i}. {rec}\n"
    
    md += "\n---\n\n*本报告由 AI 自动生成*\n"
    
    return md


__all__ = ['router']
