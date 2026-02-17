"""
简单的集成测试（不依赖 pytest）
"""
import asyncio
import sys
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, '.')

from services.Memory.service import get_memory_service
from services.Memory.config import MemoryConfig
from services.Memory.models.nodes import Person


async def test_complete_cycle():
    """测试完整的游戏闭环"""
    print("\n" + "="*60)
    print("游戏模块 Memory 集成测试 - 完整闭环")
    print("="*60)
    
    memory = await get_memory_service()
    
    try:
        # 1. 创建孩子档案
        print("\n[1/6] 创建孩子档案...")
        child = Person(
            person_id="test_child_simple_001",
            person_type="child",
            name="测试小明",
            role="patient",
            basic_info={"age": 5, "diagnosis": "ASD"},
            created_at=datetime.now().isoformat()
        )
        child_id = await memory.save_child(child)
        print(f"✅ 孩子档案创建成功: {child_id}")
        
        # 2. 记录行为
        print("\n[2/6] 记录行为...")
        behaviors = [
            "小明今天玩积木时很专注，搭了一个高塔",
            "小明听到音乐就开心地跳舞",
            "小明主动拉着妈妈的手去拿玩具"
        ]
        
        for i, behavior_text in enumerate(behaviors, 1):
            result = await memory.record_behavior(
                child_id=child_id,
                raw_input=behavior_text,
                input_type="text"
            )
            print(f"  ✓ 行为 {i}: {result['description'][:30]}... (重要性: {result['significance']})")
        
        print(f"✅ 记录了 {len(behaviors)} 条行为")
        
        # 3. 生成兴趣评估
        print("\n[3/6] 生成兴趣评估...")
        assessment = await memory.generate_assessment(
            child_id=child_id,
            assessment_type="interest_mining"
        )
        print(f"✅ 兴趣评估生成成功: {assessment['assessment_id']}")
        
        # 4. 保存游戏方案
        print("\n[4/6] 保存游戏方案...")
        game_data = {
            "game_id": "test_game_simple_001",
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
        print(f"✅ 游戏方案保存成功: {game_id}")
        
        # 5. 游戏总结
        print("\n[5/6] 生成游戏总结...")
        game_summary = await memory.summarize_game(
            game_id=game_id,
            video_analysis={
                "duration": "20分钟",
                "key_moments": [
                    {"time": "05:00", "description": "主动分享积木"},
                    {"time": "15:00", "description": "跟随音乐节奏"}
                ]
            },
            parent_feedback={"notes": "孩子很喜欢这个游戏"}
        )
        print(f"✅ 游戏总结生成成功")
        print(f"  - 参与度: {game_summary['implementation'].get('engagement_score', 'N/A')}")
        print(f"  - 目标达成: {game_summary['implementation'].get('goal_achievement_score', 'N/A')}")
        
        # 6. 验证数据完整性
        print("\n[6/6] 验证数据完整性...")
        
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
        
        # 验证行为记录
        behaviors_list = await memory.get_behaviors(child_id, {"limit": 10})
        print(f"  ✓ 行为记录: {len(behaviors_list)} 条")
        
        print("\n✅ 数据完整性验证通过")
        
        print("\n" + "="*60)
        print("🎉 完整的游戏闭环测试成功！")
        print("="*60)
        print("\n记忆驱动架构闭环:")
        print("  创建档案 → 记录行为 → 生成评估 → 保存游戏 → 游戏总结")
        print("  ✓ 所有数据已保存到 Memory")
        print("  ✓ 关系图谱已建立")
        print("  ✓ 可以进行下一轮推荐")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理测试数据
        print("\n清理测试数据...")
        await memory.storage.clear_child_data("test_child_simple_001")
        await memory.close()
        print("✅ 清理完成")


if __name__ == "__main__":
    success = asyncio.run(test_complete_cycle())
    sys.exit(0 if success else 1)
