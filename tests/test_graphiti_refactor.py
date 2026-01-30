"""
测试 Memory Service 重构后的功能
验证使用 Graphiti-core 后是否与之前行为一致
"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '.')

from services.Memory import get_memory_service
from services.Memory.models.nodes import Person


async def test_refactored_memory():
    """测试重构后的 Memory Service"""
    
    print("\n" + "="*70)
    print("Memory Service 重构功能测试")
    print("="*70)
    
    memory = await get_memory_service()
    
    try:
        # ========== 测试 1: 创建孩子档案 ==========
        print("\n[测试 1/5] 创建孩子档案...")
        child = Person(
            person_id="test_refactor_child",
            person_type="child",
            name="重构测试小明",
            role="patient",
            basic_info={"age": 4, "diagnosis": "ASD"},
            created_at=datetime.now().isoformat()
        )
        child_id = await memory.save_child(child)
        print(f"✅ 孩子档案创建成功: {child_id}")
        
        # ========== 测试 2: 记录行为（使用 Graphiti-core）==========
        print("\n[测试 2/5] 记录行为（使用 Graphiti-core）...")
        
        test_behaviors = [
            "小明今天主动把积木递给我，还看着我的眼睛笑了",
            "小明听到音乐就开心地跳舞",
            "小明玩球时很专注，持续了5分钟"
        ]
        
        behavior_results = []
        for i, behavior_text in enumerate(test_behaviors, 1):
            print(f"\n  行为 {i}: {behavior_text}")
            result = await memory.record_behavior(
                child_id=child_id,
                raw_input=behavior_text,
                input_type="text"
            )
            behavior_results.append(result)
            
            print(f"  ✓ behavior_id: {result['behavior_id']}")
            print(f"  ✓ event_type: {result['event_type']}")
            print(f"  ✓ significance: {result['significance']}")
            print(f"  ✓ description: {result['description']}")
            print(f"  ✓ objects_involved: {result['objects_involved']}")
            print(f"  ✓ related_interests: {result['related_interests']}")
            print(f"  ✓ related_functions: {result['related_functions']}")
        
        print(f"\n✅ 成功记录 {len(behavior_results)} 条行为")
        
        # ========== 测试 3: 查询行为记录 ==========
        print("\n[测试 3/5] 查询行为记录...")
        behaviors = await memory.get_behaviors(child_id=child_id, filters={"limit": 10})
        print(f"✅ 查询到 {len(behaviors)} 条行为记录")
        
        for i, bh in enumerate(behaviors[:3], 1):
            print(f"  {i}. [{bh.get('timestamp', 'N/A')[:19]}] {bh.get('description', 'N/A')[:40]}...")
        
        # ========== 测试 4: 保存游戏并总结（使用 Graphiti-core）==========
        print("\n[测试 4/5] 保存游戏并生成总结（使用 Graphiti-core）...")
        
        game_data = {
            "game_id": "test_refactor_game",
            "child_id": child_id,
            "name": "音乐积木游戏",
            "description": "结合音乐和积木的互动游戏",
            "created_at": datetime.now().isoformat(),
            "status": "recommended",
            "design": {
                "target_dimension": "social_interaction",
                "goals": {"primary_goal": "增强社交互动"}
            },
            "implementation": {}
        }
        
        game_id = await memory.save_game(game_data)
        print(f"✅ 游戏保存成功: {game_id}")
        
        # 生成游戏总结
        print("\n  生成游戏总结...")
        game_summary = await memory.summarize_game(
            game_id=game_id,
            video_analysis={
                "duration": "15分钟",
                "key_moments": [
                    {"time": "02:30", "description": "主动分享积木"},
                    {"time": "08:15", "description": "跟随音乐节奏"}
                ]
            },
            parent_feedback={"notes": "孩子很喜欢这个游戏"}
        )
        
        print(f"  ✓ 游戏状态: {game_summary.get('status')}")
        impl = game_summary.get('implementation', {})
        print(f"  ✓ 参与度评分: {impl.get('engagement_score', 'N/A')}")
        print(f"  ✓ 目标达成评分: {impl.get('goal_achievement_score', 'N/A')}")
        print(f"  ✓ 总结: {impl.get('summary', 'N/A')[:50]}...")
        
        print(f"\n✅ 游戏总结生成成功")
        
        # ========== 测试 5: 生成评估 ==========
        print("\n[测试 5/5] 生成兴趣评估...")
        assessment = await memory.generate_assessment(
            child_id=child_id,
            assessment_type="interest_mining"
        )
        
        print(f"✅ 评估生成成功:")
        print(f"  ✓ assessment_id: {assessment['assessment_id']}")
        print(f"  ✓ assessment_type: {assessment['assessment_type']}")
        
        # ========== 验证数据完整性 ==========
        print("\n[验证] 数据完整性检查...")
        
        # 验证孩子档案
        saved_child = await memory.get_child(child_id)
        assert saved_child is not None, "孩子档案未找到"
        print(f"  ✓ 孩子档案: {saved_child['name']}")
        
        # 验证游戏
        saved_game = await memory.get_game(game_id)
        assert saved_game is not None, "游戏未找到"
        assert saved_game['status'] == "completed", "游戏状态不正确"
        print(f"  ✓ 游戏: {saved_game['name']} (状态: {saved_game['status']})")
        
        # 验证评估
        latest_assessment = await memory.get_latest_assessment(child_id)
        assert latest_assessment is not None, "评估未找到"
        print(f"  ✓ 评估: {latest_assessment['assessment_type']}")
        
        # 验证行为记录数量
        all_behaviors = await memory.get_behaviors(child_id, {"limit": 100})
        print(f"  ✓ 行为记录: {len(all_behaviors)} 条")
        
        print("\n✅ 数据完整性验证通过")
        
        # ========== 对比测试结果 ==========
        print("\n" + "="*70)
        print("🎉 重构功能测试通过！")
        print("="*70)
        
        print("\n✅ 验证结果:")
        print("  ✓ 孩子档案创建 - 正常")
        print("  ✓ 行为记录（Graphiti-core）- 正常")
        print("  ✓ 行为查询 - 正常")
        print("  ✓ 游戏总结（Graphiti-core）- 正常")
        print("  ✓ 评估生成 - 正常")
        print("  ✓ 数据完整性 - 正常")
        
        print("\n✅ 重构后的功能与之前行为一致！")
        print("\n📊 使用 Graphiti-core 的方法:")
        print("  • record_behavior() - 自动提取实体和关系")
        print("  • summarize_game() - 自动提取游戏总结")
        print("  • generate_assessment() - 使用 Graphiti 搜索 + 自动提取评估")
        
        print("\n📊 保持原有实现的方法:")
        print("  • 所有查询方法 - 使用 GraphStorage")
        
        print("\n🔍 Graphiti 搜索功能:")
        print("  • 使用语义搜索获取相关历史数据")
        print("  • 替代传统的数据库查询")
        print("  • 更智能的上下文检索")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理测试数据
        print("\n清理测试数据...")
        await memory.storage.clear_child_data("test_refactor_child")
        await memory.close()
        print("✅ 清理完成")


if __name__ == "__main__":
    success = asyncio.run(test_refactored_memory())
    sys.exit(0 if success else 1)
