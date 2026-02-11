"""
测试报告生成功能
"""
import asyncio
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.container import get_memory_service, get_sqlite_service, init_services
from services.Report import ReportService


async def test_report_generation():
    """测试报告生成"""
    print("\n" + "="*60)
    print("测试报告生成")
    print("="*60)
    
    # 1. 初始化服务
    print("\n[1] 初始化服务...")
    init_services()
    memory_service = await get_memory_service()
    sqlite_service = get_sqlite_service()
    report_service = ReportService(sqlite_service, memory_service)
    print("✅ 服务初始化成功")
    
    # 2. 查找测试孩子
    print("\n[2] 查找测试孩子...")
    test_child_id = "test_child_001"
    child = sqlite_service.get_child(test_child_id)
    
    if not child:
        print(f"❌ 测试孩子不存在: {test_child_id}")
        print("请先运行 scripts/create_test_profile.py 创建测试数据")
        return
    
    print(f"✅ 找到测试孩子: {child.name} (ID: {test_child_id})")
    
    # 3. 生成报告（最近30天）
    print("\n[3] 生成医生版报告...")
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    print(f"   报告周期: {start_date} 至 {end_date}")
    
    report = await report_service.generate_medical_report(
        child_id=test_child_id,
        start_date=start_date,
        end_date=end_date
    )
    
    print(f"\n✅ 报告生成成功")
    print(f"   - 报告ID: {report.report_id}")
    print(f"   - 孩子姓名: {report.child_name}")
    print(f"   - 年龄: {report.age}")
    print(f"   - 诊断: {report.diagnosis}")
    
    # 4. 查看发展维度
    print(f"\n[4] 发展维度评估 ({len(report.development_dimensions)} 个维度):")
    for dim in report.development_dimensions:
        trend_emoji = "📈" if dim.trend == "increasing" else "📉" if dim.trend == "declining" else "➡️"
        print(f"   {trend_emoji} {dim.dimension_name}: {dim.current_level}/10 (趋势: {dim.trend})")
        if dim.initial_level:
            change_str = f"+{dim.change}" if dim.change >= 0 else str(dim.change)
            print(f"      初始: {dim.initial_level}/10, 变化: {change_str}")
    
    # 5. 查看观察记录总结
    print(f"\n[5] 观察记录总结:")
    obs = report.observation_summary
    print(f"   - 总观察次数: {obs.total_observations}")
    print(f"   - 突破性进展: {obs.breakthrough_count} 次")
    print(f"   - 需要关注: {obs.concern_count} 次")
    
    if obs.key_findings:
        print(f"   - 关键发现 (前3条):")
        for finding in obs.key_findings[:3]:
            print(f"     • {finding}")
    
    # 6. 查看干预总结
    print(f"\n[6] 干预总结:")
    interv = report.intervention_summary
    print(f"   - 总会话数: {interv.total_sessions} 次")
    print(f"   - 总时长: {interv.total_duration_hours} 小时")
    if interv.most_effective_game:
        print(f"   - 最有效游戏: {interv.most_effective_game}")
    if interv.avg_engagement_score:
        print(f"   - 平均参与度: {interv.avg_engagement_score}/10")
    if interv.avg_goal_achievement:
        print(f"   - 平均目标达成度: {interv.avg_goal_achievement}/10")
    
    # 7. 查看整体评估
    print(f"\n[7] 总体进展评估:")
    print(f"   {report.overall_progress[:200]}...")
    
    # 8. 查看优势和改善领域
    print(f"\n[8] 优势与改善领域:")
    if report.strengths:
        print(f"   ✅ 优势 ({len(report.strengths)} 项):")
        for strength in report.strengths[:3]:
            print(f"      • {strength}")
    
    if report.areas_for_improvement:
        print(f"   🎯 需要改善 ({len(report.areas_for_improvement)} 项):")
        for area in report.areas_for_improvement[:3]:
            print(f"      • {area}")
    
    # 9. 查看临床建议
    print(f"\n[9] 临床建议 ({len(report.clinical_recommendations)} 条):")
    for i, rec in enumerate(report.clinical_recommendations[:5], 1):
        print(f"   {i}. {rec}")
    
    # 10. 查看图表
    print(f"\n[10] 图表数据 ({len(report.charts)} 个图表):")
    for chart in report.charts:
        print(f"   - {chart.title} ({chart.chart_type.value})")
        if chart.description:
            print(f"     {chart.description}")
    
    # 11. 导出为 Markdown
    print(f"\n[11] 导出为 Markdown...")
    from src.api.report import _generate_markdown_report
    markdown_content = _generate_markdown_report(report)
    
    # 保存到文件
    output_file = f"report_{report.report_id}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"✅ Markdown 报告已保存: {output_file}")
    print(f"   文件大小: {len(markdown_content)} 字符")
    
    # 12. 关闭服务
    print("\n[12] 关闭服务...")
    await memory_service.close()
    print("✅ 服务已关闭")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_report_generation())
