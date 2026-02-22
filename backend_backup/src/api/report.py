"""
报告生成 API
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse, PlainTextResponse
from typing import Optional
from datetime import datetime, timedelta

from src.models.report import (
    ReportGenerateRequest,
    ReportResponse,
    ReportType,
    ReportFormat
)
from src.container import get_sqlite_service, get_memory_service
from services.Report import ReportService

router = APIRouter(prefix="/api/report", tags=["报告生成"])


async def get_report_service(
    sqlite_service = Depends(get_sqlite_service),
    memory_service = Depends(get_memory_service)
):
    """获取报告服务"""
    return ReportService(sqlite_service, memory_service)


@router.post("/generate")
async def generate_report(
    request: ReportGenerateRequest,
    report_service: ReportService = Depends(get_report_service)
):
    """
    生成报告
    
    请求参数：
    - child_id: 孩子ID
    - report_type: 报告类型（medical/parent）
    - start_date: 开始日期（YYYY-MM-DD）
    - end_date: 结束日期（YYYY-MM-DD）
    - format: 报告格式（json/markdown/pdf）
    - include_charts: 是否包含图表
    """
    try:
        print(f"[报告生成] 开始生成报告: {request.child_id}, {request.report_type}")
        
        # 目前只支持医生版报告
        if request.report_type != ReportType.MEDICAL:
            raise HTTPException(
                status_code=400,
                detail=f"暂不支持的报告类型: {request.report_type}"
            )
        
        # 生成医生版报告
        report = await report_service.generate_medical_report(
            child_id=request.child_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # 根据格式返回
        if request.format == ReportFormat.JSON:
            return JSONResponse(content=report.dict())
        
        elif request.format == ReportFormat.MARKDOWN:
            markdown_content = _generate_markdown_report(report)
            return PlainTextResponse(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{report.report_id}.md"
                }
            )
        
        else:
            # PDF 格式暂不支持
            raise HTTPException(
                status_code=400,
                detail=f"暂不支持的报告格式: {request.format}"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[报告生成] 失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


@router.get("/{child_id}/latest")
async def get_latest_report(
    child_id: str,
    format: str = "json",
    report_service: ReportService = Depends(get_report_service)
):
    """
    获取最新报告（最近30天）
    
    参数：
    - format: 报告格式（json/markdown）
    """
    try:
        # 计算最近30天
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        # 生成报告
        report = await report_service.generate_medical_report(
            child_id=child_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # 根据格式返回
        if format == "markdown":
            markdown_content = _generate_markdown_report(report)
            return PlainTextResponse(
                content=markdown_content,
                media_type="text/markdown"
            )
        else:
            return JSONResponse(content=report.dict())
    
    except Exception as e:
        print(f"[报告生成] 失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"报告生成失败: {str(e)}")


def _generate_markdown_report(report) -> str:
    """生成 Markdown 格式的报告"""
    md = f"""# 儿童发展评估报告

---

## 基本信息

**报告编号**: {report.report_id}  
**孩子姓名**: {report.child_name}  
**性别**: {report.gender}  
**出生日期**: {report.birth_date}  
**年龄**: {report.age}  
**诊断**: {report.diagnosis or '未填写'}  

**报告周期**: {report.report_period_start} 至 {report.report_period_end}  
**生成时间**: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}  

---

## 总体进展评估

{report.overall_progress}

---

## 发展维度评估

"""
    
    for dim in report.development_dimensions:
        trend_emoji = "📈" if dim.trend == "increasing" else "📉" if dim.trend == "declining" else "➡️"
        
        md += f"### {trend_emoji} {dim.dimension_name}\n\n"
        md += f"- **当前水平**: {dim.current_level}/10\n"
        
        if dim.initial_level:
            md += f"- **初始水平**: {dim.initial_level}/10\n"
            md += f"- **变化**: {'+' if dim.change >= 0 else ''}{dim.change}\n"
        
        md += f"- **趋势**: {dim.trend}\n\n"
        
        if dim.key_observations:
            md += "**关键观察**:\n"
            for obs in dim.key_observations:
                md += f"- {obs}\n"
            md += "\n"
        
        if dim.recommendations:
            md += "**建议**:\n"
            for rec in dim.recommendations:
                md += f"- {rec}\n"
            md += "\n"
    
    md += "---\n\n## 观察记录总结\n\n"
    obs = report.observation_summary
    md += f"- **总观察次数**: {obs.total_observations}\n"
    md += f"- **语音观察**: {obs.voice_observations} 次\n"
    md += f"- **文字观察**: {obs.text_observations} 次\n"
    md += f"- **视频观察**: {obs.video_observations} 次\n"
    md += f"- **突破性进展**: {obs.breakthrough_count} 次\n"
    md += f"- **需要关注**: {obs.concern_count} 次\n\n"
    
    if obs.key_findings:
        md += "**关键发现**:\n"
        for finding in obs.key_findings:
            md += f"- {finding}\n"
        md += "\n"
    
    md += "---\n\n## 干预总结\n\n"
    interv = report.intervention_summary
    md += f"- **总会话数**: {interv.total_sessions} 次\n"
    md += f"- **总时长**: {interv.total_duration_hours} 小时\n"
    
    if interv.most_effective_game:
        md += f"- **最有效游戏**: {interv.most_effective_game}\n"
    
    if interv.avg_engagement_score:
        md += f"- **平均参与度**: {interv.avg_engagement_score}/10\n"
    
    if interv.avg_goal_achievement:
        md += f"- **平均目标达成度**: {interv.avg_goal_achievement}/10\n"
    
    md += "\n"
    
    if interv.games_implemented:
        md += "**实施的游戏**:\n\n"
        md += "| 游戏名称 | 日期 | 参与度 | 目标达成度 |\n"
        md += "|---------|------|--------|----------|\n"
        for game in interv.games_implemented[:10]:  # 最多显示10个
            md += f"| {game['name']} | {game['date']} | {game.get('engagement_score', 0)}/10 | {game.get('goal_achievement_score', 0)}/10 |\n"
        md += "\n"
    
    md += "---\n\n## 优势与改善领域\n\n"
    
    if report.strengths:
        md += "### ✅ 优势领域\n\n"
        for strength in report.strengths:
            md += f"- {strength}\n"
        md += "\n"
    
    if report.areas_for_improvement:
        md += "### 🎯 需要改善的领域\n\n"
        for area in report.areas_for_improvement:
            md += f"- {area}\n"
        md += "\n"
    
    md += "---\n\n## 临床建议\n\n"
    
    for i, rec in enumerate(report.clinical_recommendations, 1):
        md += f"{i}. {rec}\n"
    
    md += f"\n**建议下次评估日期**: {report.next_assessment_date}\n\n"
    
    if report.notes:
        md += f"---\n\n## 备注\n\n{report.notes}\n\n"
    
    md += "---\n\n"
    md += f"*本报告由 ASD 儿童地板时光家庭干预辅助系统自动生成*  \n"
    md += f"*生成时间: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    return md
