"""
测试评估服务
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.assessment import AssessmentRequest, AssessmentType
from services.Assessment import AssessmentService
from services.SQLite.service import SQLiteService
from services.Memory.service import get_memory_service


async def test_assessment():
    """测试评估服务"""
    
    print("\n" + "="*60)
    print("测试评估服务")
    print("="*60)
    
    # 1. 初始化服务
    print("\n[1] 初始化服务...")
    sqlite_service = SQLiteService()
    memory_service = await get_memory_service()
    assessment_service = AssessmentService(
        sqlite_service=sqlite_service,
        memory_service=memory_service
    )
    print("✅ 服务初始化成功")
    
    # 2. 获取测试孩子ID
    print("\n[2] 获取测试孩子...")
    children = sqlite_service.get_all_children()
    if not children:
        print("❌ 没有找到孩子档案，请先创建测试档案")
        return
    
    child_id = children[0]['child_id']
    child_name = children[0]['name']
    print(f"✅ 找到测试孩子: {child_name} (ID: {child_id})")
    
    # 3. 生成完整评估
    print("\n[3] 生成完整评估...")
    request = AssessmentRequest(
        child_id=child_id,
        assessment_type=AssessmentType.COMPREHENSIVE,
        time_range_days=30
    )
    
    try:
        response = await assessment_service.generate_comprehensive_assessment(request)
        
        print(f"\n✅ 评估生成成功!")
        print(f"评估ID: {response.assessment_id}")
        print(f"孩子ID: {response.child_id}")
        print(f"\n--- 评估报告 ---")
        print(f"整体评价: {response.report.overall_assessment[:200]}...")
        print(f"综合评分: {response.report.overall_score}/10")
        
        if response.interest_heatmap:
            print(f"\n--- 兴趣热力图 ---")
            print(f"整体兴趣广度: {response.interest_heatmap.overall_breadth}")
            print(f"兴趣维度数量: {len(response.interest_heatmap.dimensions)}")
            print(f"新发现: {len(response.interest_heatmap.new_discoveries)} 个")
        
        if response.dimension_trends:
            print(f"\n--- 功能维度趋势 ---")
            print(f"活跃维度数量: {len(response.dimension_trends.active_dimensions)}")
            print(f"进步最快: {len(response.dimension_trends.top_improving)} 个维度")
            print(f"需要关注: {len(response.dimension_trends.needs_attention)} 个维度")
        
        print(f"\n--- 干预建议 ---")
        for i, rec in enumerate(response.report.recommendations[:3], 1):
            print(f"{i}. {rec}")
        
    except Exception as e:
        print(f"❌ 评估生成失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 4. 获取评估历史
    print("\n[4] 获取评估历史...")
    try:
        history = sqlite_service.get_assessment_history(child_id, limit=5)
        print(f"✅ 找到 {len(history)} 条评估记录")
        
        for i, assessment in enumerate(history, 1):
            print(f"\n{i}. 评估ID: {assessment['assessment_id']}")
            print(f"   类型: {assessment['assessment_type']}")
            print(f"   时间: {assessment['timestamp']}")
    except Exception as e:
        print(f"❌ 获取评估历史失败: {e}")
    
    # 5. 关闭服务
    print("\n[5] 关闭服务...")
    await memory_service.close()
    print("✅ 服务已关闭")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_assessment())
