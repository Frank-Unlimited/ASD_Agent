"""
测试对象提取功能
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.Memory.service import get_memory_service


async def test_object_extraction():
    """测试对象提取"""
    print("="*60)
    print("测试对象提取功能")
    print("="*60)
    
    # 初始化服务
    memory = await get_memory_service()
    
    # 创建测试孩子
    from services.Graphiti.models.nodes import Person
    child = Person(
        person_id="test_obj_child",
        person_type="child",
        name="测试小明",
        role="patient",
        basic_info={"age": 3},
        created_at="2024-01-30T00:00:00Z"
    )
    await memory.save_child(child)
    print("✅ 测试孩子创建成功")
    
    # 测试用例
    test_cases = [
        "小明喜欢听绘本",
        "孩子在玩积木",
        "小红拿着玩具车在地上跑",
        "孩子对着镜子笑",
        "小明把球递给妈妈",
    ]
    
    print("\n开始测试...")
    for i, text in enumerate(test_cases, 1):
        print(f"\n[{i}] 输入: {text}")
        
        result = await memory.record_behavior(
            child_id="test_obj_child",
            raw_input=text,
            input_type="text"
        )
        
        print(f"  描述: {result['description']}")
        print(f"  对象: {result['objects_involved']}")
        print(f"  兴趣: {result['related_interests']}")
        print(f"  功能: {result['related_functions']}")
        
        if not result['objects_involved']:
            print(f"  ⚠️ 未提取到对象！")
        else:
            print(f"  ✅ 成功提取对象")
    
    # 查询所有对象节点
    print("\n查询 Neo4j 中的对象节点...")
    objects = await memory.get_objects("test_obj_child")
    print(f"找到 {len(objects)} 个对象节点:")
    for obj in objects:
        print(f"  - {obj.get('name', 'unknown')}")
    
    # 清理
    print("\n清理测试数据...")
    await memory.storage.clear_child_data("test_obj_child")
    await memory.close()
    print("✅ 清理完成")


if __name__ == "__main__":
    asyncio.run(test_object_extraction())
