"""
Memory 服务智能写入功能演示
展示如何使用 4 个智能写入方法
"""
import asyncio
from services.Memory.service import get_memory_service
from services.Memory.config import MemoryConfig


async def demo_record_behavior():
    """演示：记录日常行为"""
    print("\n" + "="*60)
    print("演示 1: 记录日常行为 (record_behavior)")
    print("="*60)
    
    memory = await get_memory_service()
    
    # 场景：家长观察到孩子的行为
    raw_input = """
    今天下午，小明在玩积木的时候，突然主动把一块红色的积木递给我，
    还看着我的眼睛笑了。这是他第一次主动分享玩具！我好开心！
    """
    
    print(f"\n📝 家长输入: {raw_input.strip()}")
    
    # 调用 Memory 服务记录行为
    result = await memory.record_behavior(
        child_id="child_xiaoming",
        raw_input=raw_input,
        input_type="text"
    )
    
    print(f"\n✅ 记录成功!")
    print(f"  🆔 行为ID: {result['behavior_id']}")
    print(f"  📊 事件类型: {result['event_type']}")
    print(f"  ⭐ 重要性: {result['significance']}")
    print(f"  📝 描述: {result['description']}")
    print(f"  🎯 涉及对象: {result['objects_involved']}")
    print(f"  💡 相关兴趣: {result['related_interests']}")
    print(f"  🎓 相关功能: {result['related_functions']}")
    
    await memory.close()


async def demo_summarize_game():
    """演示：总结地板游戏"""
    print("\n" + "="*60)
    print("演示 2: 总结地板游戏 (summarize_game)")
    print("="*60)
    
    memory = await get_memory_service()
    
    # 场景：游戏结束后，需要生成总结
    game_id = "game_20260130_001"
    
    video_analysis = {
        "duration": "15分钟",
        "key_moments": [
            {"time": "02:15", "description": "主动递积木"},
            {"time": "08:30", "description": "眼神接触5次"},
            {"time": "12:00", "description": "专注搭建高塔"}
        ]
    }
    
    parent_feedback = {
        "notes": "孩子今天状态很好，比上次更主动了",
        "concerns": "中途有一次情绪波动，但很快恢复了"
    }
    
    print(f"\n🎮 游戏ID: {game_id}")
    print(f"📹 视频分析: {len(video_analysis['key_moments'])} 个关键时刻")
    print(f"💬 家长反馈: {parent_feedback['notes']}")
    
    # 调用 Memory 服务生成总结
    result = await memory.summarize_game(
        game_id=game_id,
        video_analysis=video_analysis,
        parent_feedback=parent_feedback
    )
    
    print(f"\n✅ 总结生成成功!")
    print(f"  📊 参与度得分: {result['implementation']['engagement_score']}")
    print(f"  🎯 目标达成得分: {result['implementation']['goal_achievement_score']}")
    print(f"  🌟 亮点:")
    for highlight in result['implementation']['highlights']:
        print(f"    - {highlight}")
    
    await memory.close()


async def demo_generate_assessment():
    """演示：生成评估报告"""
    print("\n" + "="*60)
    print("演示 3: 生成评估报告 (generate_assessment)")
    print("="*60)
    
    memory = await get_memory_service()
    
    # 场景：需要生成兴趣挖掘评估
    child_id = "child_xiaoming"
    
    print(f"\n👦 孩子ID: {child_id}")
    print(f"📋 评估类型: 兴趣挖掘 (interest_mining)")
    
    # 调用 Memory 服务生成评估
    result = await memory.generate_assessment(
        child_id=child_id,
        assessment_type="interest_mining"
    )
    
    print(f"\n✅ 评估生成成功!")
    print(f"  🆔 评估ID: {result['assessment_id']}")
    print(f"  📊 兴趣分析:")
    
    interests = result['analysis'].get('interests', {})
    for interest_name, interest_data in interests.items():
        if interest_data.get('level') in ['high', 'medium']:
            print(f"    - {interest_name}: {interest_data['level']}")
            if interest_data.get('items'):
                print(f"      喜欢的物品: {', '.join(interest_data['items'])}")
    
    await memory.close()


async def demo_import_profile():
    """演示：导入档案"""
    print("\n" + "="*60)
    print("演示 4: 导入档案 (import_profile)")
    print("="*60)
    
    memory = await get_memory_service()
    
    # 场景：新孩子入档，需要导入档案
    profile_data = {
        "name": "小红",
        "age": 4,
        "diagnosis": "自闭症谱系障碍（ASD）",
        "medical_reports": """
        诊断时间：2025年6月
        主要症状：社交互动困难、语言发展迟缓
        CARS评分：32分（轻度自闭症）
        """,
        "assessment_scales": """
        ABC量表：总分58分
        - 感觉：10分
        - 交往：15分
        - 躯体运动：8分
        - 语言：13分
        - 生活自理：12分
        """
    }
    
    print(f"\n👧 姓名: {profile_data['name']}")
    print(f"🎂 年龄: {profile_data['age']}岁")
    print(f"🏥 诊断: {profile_data['diagnosis']}")
    
    # 调用 Memory 服务导入档案
    result = await memory.import_profile(profile_data)
    
    print(f"\n✅ 档案导入成功!")
    print(f"  🆔 孩子ID: {result['child_id']}")
    print(f"  📋 初始评估ID: {result['assessment_id']}")
    print(f"  💬 消息: {result['message']}")
    
    # 查看初始评估
    assessment = await memory.get_latest_assessment(result['child_id'])
    print(f"\n📊 初始评估:")
    print(f"  整体评估: {assessment['analysis'].get('overall_assessment', '')[:100]}...")
    print(f"  优势领域: {assessment['analysis'].get('strengths', [])}")
    print(f"  挑战领域: {assessment['analysis'].get('challenges', [])}")
    
    await memory.close()


async def main():
    """运行所有演示"""
    print("\n" + "🌟"*30)
    print("Memory 服务智能写入功能演示")
    print("🌟"*30)
    
    try:
        await demo_record_behavior()
        await demo_summarize_game()
        await demo_generate_assessment()
        await demo_import_profile()
        
        print("\n" + "="*60)
        print("✅ 所有演示完成!")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
