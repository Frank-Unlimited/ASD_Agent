"""
简单的 API 测试脚本
测试行为观察 API
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.container import init_services, container
from services.Memory.service import get_memory_service


async def test_observation_api():
    """测试行为观察 API 的底层逻辑"""
    
    print("\n" + "="*60)
    print("测试行为观察 API 底层逻辑")
    print("="*60)
    
    # 初始化服务
    print("\n[1/4] 初始化服务...")
    init_services()
    
    # 获取服务
    observation_service = container.get('observation')
    memory_service = observation_service.memory
    
    print("✅ 服务初始化成功")
    
    # 创建测试孩子
    print("\n[2/4] 创建测试孩子...")
    from services.Graphiti.models.nodes import Person
    
    child = Person(
        person_id="test_api_child_001",
        person_type="child",
        name="测试小红",
        role="patient",
        basic_info={"age": 3},
        created_at="2024-01-30T00:00:00Z"
    )
    
    await memory_service.save_child(child)
    print("✅ 测试孩子创建成功")
    
    # 测试文字观察
    print("\n[3/4] 测试文字观察...")
    result = await observation_service.record_text_observation(
        child_id="test_api_child_001",
        text="小红今天主动拉着妈妈的手去拿玩具，还回头看了妈妈一眼",
        context={"location": "家里客厅"}
    )
    
    print(f"✅ 文字观察记录成功:")
    print(f"  - behavior_id: {result['behavior_id']}")
    print(f"  - 描述: {result['description']}")
    print(f"  - 事件类型: {result['event_type']}")
    print(f"  - 重要性: {result['significance']}")
    
    # 测试快速按钮
    print("\n[4/4] 测试快速按钮...")
    result = await observation_service.record_quick_button(
        child_id="test_api_child_001",
        button_type="eye_contact",
        context={}
    )
    
    print(f"✅ 快速按钮记录成功:")
    print(f"  - behavior_id: {result['behavior_id']}")
    print(f"  - 按钮类型: {result['button_type']}")
    print(f"  - 描述: {result['description']}")
    
    # 获取最近观察
    print("\n[5/5] 获取最近观察...")
    observations = await observation_service.get_recent_observations(
        child_id="test_api_child_001",
        limit=10
    )
    
    print(f"✅ 获取成功: {len(observations)} 条记录")
    for i, obs in enumerate(observations, 1):
        print(f"  {i}. {obs.get('description', '')[:30]}... ({obs.get('significance', '')})")
    
    # 清理
    print("\n清理测试数据...")
    await memory_service.storage.clear_child_data("test_api_child_001")
    await memory_service.close()
    print("✅ 清理完成")
    
    print("\n" + "="*60)
    print("🎉 API 底层逻辑测试成功！")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_observation_api())
