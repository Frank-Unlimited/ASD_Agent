"""
测试对象-兴趣关联查询功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.Memory.service import get_memory_service
from services.Memory.config import MemoryConfig


async def test_object_interest_associations():
    """测试对象-兴趣关联查询"""
    
    print("=" * 60)
    print("测试对象-兴趣关联查询")
    print("=" * 60)
    
    # 1. 初始化服务
    memory_service = await get_memory_service()
    
    # 使用测试数据中的 child_id（从调试输出中看到的）
    child_id = "test_refactor_child"  # 或 "test_advanced_child"
    
    try:
        # 2. 测试：查询所有对象的兴趣关联
        print("\n【测试1】查询所有对象的兴趣关联")
        print("-" * 60)
        
        result = await memory_service.get_object_interest_associations(
            child_id=child_id,
            min_frequency=1  # 最少出现1次
        )
        
        print(f"时间范围: {result['time_range']}")
        print(f"总结: {result['summary']}")
        print(f"\n发现 {result['total_objects']} 个对象:")
        
        for obj_name, obj_data in result['associations'].items():
            print(f"\n  【{obj_name}】")
            print(f"    - 涉及行为数: {obj_data['total_behaviors']}")
            print(f"    - 主要兴趣: {obj_data['primary_interest']}")
            print(f"    - 兴趣分布:")
            
            for int_name, int_data in obj_data['interests'].items():
                print(f"      * {int_name}: "
                      f"频率={int_data['frequency']}, "
                      f"强度={int_data['avg_intensity']}, "
                      f"占比={int_data['percentage']:.0%}")
        
        # 3. 测试：查询特定对象
        print("\n" + "=" * 60)
        print("【测试2】查询特定对象（积木）的兴趣关联")
        print("-" * 60)
        
        result2 = await memory_service.get_object_interest_associations(
            child_id=child_id,
            object_name="积木",
            min_frequency=1
        )
        
        if result2['associations']:
            for obj_name, obj_data in result2['associations'].items():
                print(f"\n【{obj_name}】的兴趣关联:")
                for int_name, int_data in obj_data['interests'].items():
                    print(f"  - {int_name}: "
                          f"频率={int_data['frequency']}, "
                          f"强度={int_data['avg_intensity']}, "
                          f"占比={int_data['percentage']:.0%}")
        else:
            print("未找到'积木'的关联数据")
        
        # 4. 测试：查询最近30天的关联
        print("\n" + "=" * 60)
        print("【测试3】查询最近30天的对象-兴趣关联")
        print("-" * 60)
        
        result3 = await memory_service.get_object_interest_associations(
            child_id=child_id,
            min_frequency=1,
            days=30
        )
        
        print(f"时间范围: {result3['time_range']}")
        print(f"总结: {result3['summary']}")
        
        # 5. 应用场景演示
        print("\n" + "=" * 60)
        print("【应用场景】根据兴趣推荐对象")
        print("-" * 60)
        
        # 假设孩子的主要兴趣是 "construction" 和 "visual"
        target_interests = ["construction", "visual"]
        
        print(f"目标兴趣: {', '.join(target_interests)}")
        print("\n推荐对象:")
        
        # 找出与目标兴趣相关的对象
        recommendations = []
        for obj_name, obj_data in result['associations'].items():
            for target_int in target_interests:
                if target_int in obj_data['interests']:
                    int_data = obj_data['interests'][target_int]
                    recommendations.append({
                        "object": obj_name,
                        "interest": target_int,
                        "score": int_data['avg_intensity'] * int_data['percentage']
                    })
        
        # 按评分排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"  {i}. {rec['object']} (关联兴趣: {rec['interest']}, 评分: {rec['score']:.2f})")
        
        print("\n✅ 测试完成！")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await memory_service.close()


if __name__ == "__main__":
    asyncio.run(test_object_interest_associations())
