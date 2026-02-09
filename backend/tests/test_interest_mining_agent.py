"""
测试兴趣挖掘 Agent (Agent 1)
专注于测试输入数据 → 兴趣热力图的转换过程
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.Assessment.service import AssessmentService
from services.SQLite.service import SQLiteService
from services.Memory import get_memory_service
from services.Memory.models.nodes import Person


async def test_interest_mining_agent():
    """测试兴趣挖掘 Agent"""
    
    print("\n" + "="*80)
    print("兴趣挖掘 Agent 测试")
    print("="*80)
    
    # 初始化服务
    print("\n[步骤 1] 初始化服务...")
    sqlite_service = SQLiteService()
    memory_service = await get_memory_service()
    assessment_service = AssessmentService(
        sqlite_service=sqlite_service,
        memory_service=memory_service
    )
    print("✅ 服务初始化完成")
    
    # 准备测试数据
    print("\n[步骤 2] 准备测试数据...")
    
    child_id = "test_interest_mining_child"
    
    # 创建孩子档案
    child = Person(
        person_id=child_id,
        person_type="child",
        name="兴趣测试小明",
        role="patient",
        basic_info={"age": 4, "diagnosis": "ASD"},
        created_at=datetime.now().isoformat()
    )
    await memory_service.save_child(child)
    print(f"✅ 创建孩子档案: {child.name}")
    
    # 准备行为记录（模拟真实场景）
    test_behaviors = [
        # 持续兴趣：积木（多次出现）
        "小明今天主动把积木递给我，还看着我的眼睛笑了",
        "小明又在玩积木，这次搭了一个很高的塔，持续了10分钟",
        "小明看到积木就很兴奋，主动要求玩",
        
        # 持续兴趣：音乐（多次出现）
        "小明听到音乐就开心地跳舞",
        "小明对音乐盒特别感兴趣，反复按开关听音乐",
        
        # 短暂兴趣：球（只出现一次）
        "小明玩球时很专注，持续了5分钟",
        
        # 意外发现
        "小明对玩具的包装纸更感兴趣，一直在撕纸玩",
        
        # 社交互动
        "小明主动拉着妈妈的手，想要一起玩",
        "小明今天第一次主动叫了'妈妈'",
        
        # 负面行为
        "小明拒绝玩拼图，情绪有些焦虑",
    ]
    
    print(f"\n📝 准备记录 {len(test_behaviors)} 条行为...")
    for i, behavior_text in enumerate(test_behaviors, 1):
        result = await memory_service.record_behavior(
            child_id=child_id,
            raw_input=behavior_text,
            input_type="text"
        )
        print(f"  {i}. {behavior_text[:40]}... → {result['event_type']}")
    
    print(f"✅ 成功记录 {len(test_behaviors)} 条行为")
    
    # 准备游戏总结
    game_summaries = [
        {
            "game_id": "test_game_1",
            "summary": """
音乐积木游戏总结：

本次游戏持续15分钟，小明表现出很高的参与度。

关键时刻：
- 02:30 - 主动分享积木，展现社交主动性
- 08:15 - 跟随音乐节奏摆动身体
- 12:00 - 对音乐盒的旋转机制特别感兴趣

参与度评分：8.5/10
目标达成度：7.0/10

亮点：孩子对积木和音乐都表现出真实的兴趣。
            """
        },
        {
            "game_id": "test_game_2",
            "summary": """
拼图游戏总结：

本次游戏持续5分钟，小明参与度较低。

关键时刻：
- 01:00 - 拒绝参与，情绪焦虑
- 03:00 - 对拼图盒子的图案更感兴趣

参与度评分：3.0/10

发现：档案中标记的"拼图兴趣"可能是假设兴趣。
            """
        }
    ]
    
    print(f"\n📝 准备保存 {len(game_summaries)} 个游戏总结...")
    for i, game_data in enumerate(game_summaries, 1):
        game_node = {
            "game_id": game_data["game_id"],
            "child_id": child_id,
            "name": f"测试游戏 {i}",
            "description": "测试游戏",
            "created_at": datetime.now().isoformat(),
            "status": "completed",
            "design": {},
            "implementation": {}
        }
        await memory_service.save_game(game_node)
        
        await memory_service.store_game_summary(
            child_id=child_id,
            game_id=game_data["game_id"],
            summary_text=game_data["summary"]
        )
        print(f"  {i}. {game_data['game_id']} → 已保存")
    
    print(f"✅ 成功保存 {len(game_summaries)} 个游戏总结")
    
    # 调用兴趣挖掘 Agent
    print("\n[步骤 3] 调用兴趣挖掘 Agent...")
    print("⏳ 正在分析数据，生成兴趣热力图...")
    
    try:
        interest_heatmap = await assessment_service.analyze_interests(
            child_id=child_id,
            time_range_days=30
        )
        
        print("✅ 兴趣热力图生成成功！")
        
        # 展示输出结果
        print("\n" + "="*80)
        print("📊 兴趣热力图分析结果")
        print("="*80)
        
        # 整体兴趣广度
        print(f"\n【整体兴趣广度】")
        print(f"评估结果: {interest_heatmap.overall_breadth}")
        
        # 兴趣维度详情
        print(f"\n【兴趣维度分析】")
        print(f"发现 {len(interest_heatmap.dimensions)} 个兴趣维度：\n")
        
        sorted_dimensions = sorted(
            interest_heatmap.dimensions.items(),
            key=lambda x: x[1].strength,
            reverse=True
        )
        
        for i, (dim_name, dim_data) in enumerate(sorted_dimensions[:5], 1):
            print(f"{i}. 【{dim_name}】")
            print(f"   强度: {dim_data.strength:.1f}/10")
            print(f"   趋势: {dim_data.trend}")
            print(f"   置信度: {dim_data.confidence}")
            
            if dim_data.key_objects:
                print(f"   关键对象:")
                for obj in dim_data.key_objects[:3]:
                    verified_mark = "✓" if obj.verified else "?"
                    print(f"     {verified_mark} {obj.name} (参与度: {obj.engagement:.1f}/10)")
            print()
        
        # 新发现
        if interest_heatmap.new_discoveries:
            print(f"【意外发现】")
            for i, discovery in enumerate(interest_heatmap.new_discoveries, 1):
                print(f"{i}. {discovery}")
            print()
        
        # 兴趣验证
        if interest_heatmap.interest_verification:
            print(f"【兴趣验证】")
            for i, verification in enumerate(interest_heatmap.interest_verification, 1):
                print(f"{i}. {verification}")
            print()
        
        # 分析总结
        print(f"【分析总结】")
        print(interest_heatmap.analysis_summary)
        
        # 验证输出质量
        print("\n" + "="*80)
        print("✅ 输出质量验证")
        print("="*80)
        
        print("\n[验证 1] 数据结构完整性")
        assert hasattr(interest_heatmap, 'dimensions')
        assert hasattr(interest_heatmap, 'overall_breadth')
        print("✅ 数据结构完整")
        
        print("\n[验证 2] 兴趣广度评估")
        assert interest_heatmap.overall_breadth in ["narrow", "moderate", "diverse"]
        print(f"✅ 兴趣广度: {interest_heatmap.overall_breadth}")
        
        print("\n" + "="*80)
        print("🎉 兴趣挖掘 Agent 测试完成！")
        print("="*80)
        
        print("\n📋 测试总结")
        print(f"输入: {len(test_behaviors)} 条行为 + {len(game_summaries)} 个游戏")
        print(f"输出: {len(interest_heatmap.dimensions)} 个兴趣维度")
        print(f"广度: {interest_heatmap.overall_breadth}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\n[清理] 删除测试数据...")
        await memory_service.storage.clear_child_data(child_id)
        await memory_service.close()
        print("✅ 清理完成")


if __name__ == "__main__":
    success = asyncio.run(test_interest_mining_agent())
    sys.exit(0 if success else 1)
