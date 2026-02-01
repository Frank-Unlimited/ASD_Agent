"""
行为观察服务测试
"""
import asyncio
import sys
sys.path.insert(0, '.')

from datetime import datetime
from services.Memory.service import get_memory_service
from services.Observation import ObservationService
from services.Memory.models.nodes import Person


async def test_observation_service():
    """测试行为观察服务"""
    print("\n" + "="*60)
    print("行为观察服务测试")
    print("="*60)
    
    # 初始化服务
    memory = await get_memory_service()
    observation = ObservationService(memory_service=memory)
    
    try:
        # 1. 创建测试孩子
        print("\n[1/5] 创建测试孩子...")
        child = Person(
            person_id="test_child_obs_001",
            person_type="child",
            name="观察测试小红",
            role="patient",
            basic_info={"age": 4, "diagnosis": "ASD"},
            created_at=datetime.now().isoformat()
        )
        await memory.save_child(child)
        print("✅ 孩子档案创建成功")
        
        # 2. 测试文字观察
        print("\n[2/5] 测试文字观察...")
        result1 = await observation.record_text_observation(
            child_id="test_child_obs_001",
            text="小红今天主动拉着我的手去拿她喜欢的玩具",
            context={"location": "家里", "activity": "自由玩耍"}
        )
        print(f"✅ 文字观察记录成功:")
        print(f"  - behavior_id: {result1['behavior_id']}")
        print(f"  - 描述: {result1['description']}")
        print(f"  - 重要性: {result1['significance']}")
        
        # 3. 测试快速按钮
        print("\n[3/5] 测试快速按钮...")
        result2 = await observation.record_quick_button(
            child_id="test_child_obs_001",
            button_type="eye_contact",
            context={"location": "幼儿园"}
        )
        print(f"✅ 快速按钮记录成功:")
        print(f"  - behavior_id: {result2['behavior_id']}")
        print(f"  - 按钮类型: {result2['button_type']}")
        print(f"  - 描述: {result2['description']}")
        
        # 4. 获取最近观察
        print("\n[4/5] 获取最近观察...")
        recent = await observation.get_recent_observations(
            child_id="test_child_obs_001",
            limit=10
        )
        print(f"✅ 获取成功: {len(recent)} 条记录")
        for i, obs in enumerate(recent, 1):
            print(f"  {i}. {obs.get('description', 'N/A')[:40]}... ({obs.get('significance', 'N/A')})")
        
        # 5. 获取统计
        print("\n[5/5] 获取观察统计...")
        stats = await observation.get_observation_stats(
            child_id="test_child_obs_001",
            days=7
        )
        print(f"✅ 统计完成:")
        print(f"  - 总记录数: {stats['total_count']}")
        print(f"  - 事件类型分布: {stats['event_types']}")
        print(f"  - 重要性分布: {stats['significance_counts']}")
        print(f"  - 突破性进步: {stats['breakthrough_count']} 次")
        
        print("\n" + "="*60)
        print("🎉 行为观察服务测试成功！")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理
        print("\n清理测试数据...")
        await memory.storage.clear_child_data("test_child_obs_001")
        await memory.close()
        print("✅ 清理完成")


if __name__ == "__main__":
    success = asyncio.run(test_observation_service())
    sys.exit(0 if success else 1)
