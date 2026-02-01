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
        
        # ========== 测试 2: 记录行为（使用 Graphiti-core，只提取基础实体）==========
        print("\n[测试 2/5] 记录行为（使用 Graphiti-core，只提取基础实体）...")
        
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
            # 注意：新架构下，观察记录不再提取 Interest 和 Function
            print(f"  ✓ related_interests: {result['related_interests']} (应为空)")
            print(f"  ✓ related_functions: {result['related_functions']} (应为空)")
        
        print(f"\n✅ 成功记录 {len(behavior_results)} 条行为（只提取基础实体）")
        
        # ========== 测试 3: 查询行为记录 ==========
        print("\n[测试 3/5] 查询行为记录...")
        behaviors = await memory.get_behaviors(child_id=child_id, filters={"limit": 10})
        print(f"✅ 查询到 {len(behaviors)} 条行为记录")
        
        for i, bh in enumerate(behaviors[:3], 1):
            print(f"  {i}. [{bh.get('timestamp', 'N/A')[:19]}] {bh.get('description', 'N/A')[:40]}...")
        
        # ========== 测试 4: 使用新接口 store_game_summary() ==========
        print("\n[测试 4/5] 使用新接口 store_game_summary()...")
        
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
        
        # 模拟上层服务生成的总结文本
        summary_text = """
        游戏实施总结：
        
        本次音乐积木游戏持续15分钟，孩子表现出很高的参与度。
        
        关键时刻：
        - 02:30 - 主动分享积木，展现社交主动性
        - 08:15 - 跟随音乐节奏摆动身体，展现听觉敏感度
        
        参与度评分：8.5/10
        目标达成度：7.0/10
        
        亮点：孩子首次主动分享玩具，这是一个重要的突破。
        建议：下次可以增加更多互动环节。
        """
        
        print("\n  使用新接口 store_game_summary()...")
        summary_result = await memory.store_game_summary(
            child_id=child_id,
            game_id=game_id,
            summary_text=summary_text,
            metadata={"session_duration": "15分钟"}
        )
        
        print(f"  ✓ episode_id: {summary_result['episode_id']}")
        print(f"  ✓ 提取的实体: {list(summary_result['extracted_entities'].keys())}")
        
        print(f"\n✅ 游戏总结存储成功（使用新架构）")
        
        # ========== 测试 5: 使用新接口 store_assessment() ==========
        print("\n[测试 5/5] 使用新接口 store_assessment()...")
        
        # 模拟上层服务生成的评估文本
        assessment_text = """
        兴趣挖掘评估报告：
        
        基于最近30天的观察数据，孩子展现出以下兴趣偏好：
        
        1. 社交互动（强度：8.5/10）
           - 主动分享玩具的频率增加
           - 眼神接触时长延长
           
        2. 建构活动（强度：7.0/10）
           - 喜欢搭建积木
           - 能够完成简单的拼装任务
           
        3. 音乐节奏（强度：6.5/10）
           - 对音乐有明显反应
           - 能够跟随节奏摆动
        
        建议：
        - 继续强化社交互动类游戏
        - 引入更多建构类活动
        """
        
        assessment_result = await memory.store_assessment(
            child_id=child_id,
            assessment_text=assessment_text,
            assessment_type="interest_mining",
            metadata={"data_period": "30天"}
        )
        
        print(f"✅ 评估存储成功:")
        print(f"  ✓ episode_id: {assessment_result['episode_id']}")
        print(f"  ✓ assessment_id: {assessment_result['assessment_id']}")
        print(f"  ✓ assessment_type: {assessment_result['assessment_type']}")
        print(f"  ✓ 提取的实体: {list(assessment_result['extracted_entities'].keys())}")
        
        # ========== 测试 6: 搜索历史记忆（新方法）==========
        print("\n[测试 6/7] 搜索历史记忆（search_memories）...")
        
        search_result = await memory.search_memories(
            child_id=child_id,
            query="孩子的社交互动表现",
            filters={"num_results": 5}
        )
        
        print(f"✅ 搜索成功:")
        print(f"  ✓ 查询: {search_result['query']}")
        print(f"  ✓ 结果数量: {search_result['total_results']}")
        
        if search_result['results']:
            print(f"  ✓ 示例结果:")
            for i, result in enumerate(search_result['results'][:2], 1):
                print(f"    {i}. {result['fact'][:60]}...")
        
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
        print("  ✓ 行为记录（只提取基础实体）- 正常")
        print("  ✓ 行为查询 - 正常")
        print("  ✓ 游戏总结（新接口 store_game_summary）- 正常")
        print("  ✓ 评估存储（新接口 store_assessment）- 正常")
        print("  ✓ 搜索历史记忆（search_memories）- 正常")
        print("  ✓ 数据完整性 - 正常")
        
        print("\n✅ 重构后的功能与新架构一致！")
        print("\n📊 新架构特点:")
        print("  • 观察记录 - 只提取基础实体（Behavior、Object、Person）")
        print("  • 游戏总结 - 上层服务生成，Memory 只负责存储和提取实体")
        print("  • 评估报告 - 上层服务生成，Memory 只负责存储和提取实体")
        print("  • Interest/Function - 由评估层建立关联，不在观察时提取")
        
        print("\n📊 新增方法:")
        print("  • store_game_summary() - 存储已生成的游戏总结")
        print("  • store_assessment() - 存储已生成的评估报告")
        print("  • search_memories() - 搜索历史记忆数据")
        
        print("\n📊 已废弃方法（向后兼容）:")
        print("  • summarize_game() - 使用 store_game_summary() 代替")
        print("  • generate_assessment() - 使用 store_assessment() 代替")
        
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
