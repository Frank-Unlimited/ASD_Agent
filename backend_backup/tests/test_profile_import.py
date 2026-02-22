"""
测试档案导入功能
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.container import get_memory_service, get_sqlite_service, init_services


async def test_text_import():
    """测试文字导入档案"""
    print("\n" + "="*60)
    print("测试文字导入档案")
    print("="*60)
    
    # 1. 初始化容器和服务
    print("\n[1] 初始化服务...")
    init_services()
    memory_service = await get_memory_service()
    sqlite_service = get_sqlite_service()
    print("✅ 服务初始化成功")
    
    # 2. 准备档案数据
    profile_data = {
        "name": "小明",
        "age": 5,
        "diagnosis": "自闭症谱系障碍（ASD）",
        "medical_reports": """
【诊断报告】
患儿：小明，男，5岁
诊断：自闭症谱系障碍（ASD）- 中度
诊断日期：2025年1月

【主要表现】
1. 社交互动：眼神接触较少，不主动与人互动
2. 语言沟通：语言发育迟缓，词汇量约50个，多为名词
3. 重复行为：喜欢旋转物体，对水流特别感兴趣
4. 感觉敏感：对声音敏感，不喜欢嘈杂环境

【优势领域】
- 视觉记忆力强
- 对数字和形状有兴趣
- 精细动作发展良好
        """,
        "assessment_scales": """
【CARS评分】总分：35分（中度自闭症）
【ABC评分】总分：58分
        """
    }
    
    # 3. 调用导入（模拟 API 层的完整流程）
    print("\n[2] 导入档案...")
    
    # 3.1 调用 Memory 服务解析医学报告
    memory_result = await memory_service.import_profile(profile_data)
    
    # 3.2 创建系统档案（保存到 SQLite）
    from datetime import datetime
    from src.models.profile import ChildProfile, Gender, DiagnosisLevel
    
    profile = ChildProfile(
        child_id=memory_result["child_id"],
        name=profile_data.get("name", "待完善"),
        gender=Gender.OTHER,
        birth_date=datetime.now().strftime("%Y-%m-%d"),
        diagnosis=profile_data.get("diagnosis", ""),
        diagnosis_level=DiagnosisLevel.NOT_DIAGNOSED,
        notes=f"从文字导入\n\n医学报告：\n{profile_data.get('medical_reports', '')[:500]}..."
    )
    
    sqlite_service.save_child(profile)
    
    result = {
        "child_id": memory_result["child_id"],
        "assessment_id": memory_result["assessment_id"],
        "message": f"档案创建成功，已为 {profile.name} 生成初始评估"
    }
    
    print(f"\n✅ 档案导入成功")
    print(f"   - 孩子ID: {result['child_id']}")
    print(f"   - 评估ID: {result['assessment_id']}")
    print(f"   - 消息: {result['message']}")
    
    # 4. 验证档案（SQLite）
    print("\n[3] 验证系统档案（SQLite）...")
    child_profile = sqlite_service.get_child(result['child_id'])
    if child_profile:
        print(f"✅ 系统档案已保存到 SQLite")
        print(f"   - 姓名: {child_profile.name}")
        print(f"   - 诊断: {child_profile.diagnosis}")
        print(f"   - 档案ID: {child_profile.child_id}")
    
    # 5. 验证档案（Memory）
    print("\n[4] 验证图数据（Memory）...")
    child_graph = await memory_service.get_child(result['child_id'])
    if child_graph:
        print(f"✅ 图数据已保存到 Memory")
        print(f"   - 姓名: {child_graph.get('name')}")
        
        # basic_info 可能是 JSON 字符串，需要解析
        import json
        basic_info = child_graph.get('basic_info', {})
        if isinstance(basic_info, str):
            basic_info = json.loads(basic_info)
        
        print(f"   - 年龄: {basic_info.get('age')}")
        print(f"   - 诊断: {basic_info.get('diagnosis')}")
    
    # 6. 验证评估
    print("\n[5] 验证初始评估...")
    assessment = await memory_service.get_latest_assessment(
        result['child_id'],
        "comprehensive"
    )
    if assessment:
        print(f"✅ 初始评估已生成")
        print(f"   - 评估ID: {assessment['assessment_id']}")
        print(f"   - 评估类型: {assessment['assessment_type']}")
        print(f"   - 分析结果: {str(assessment.get('analysis', {}))[:200]}...")
    
    # 7. 关闭服务
    print("\n[6] 关闭服务...")
    await memory_service.close()
    print("✅ 服务已关闭")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_text_import())
