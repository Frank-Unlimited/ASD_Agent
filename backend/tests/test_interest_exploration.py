"""
测试兴趣维度探索度计算功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
import pytest_asyncio
import asyncio
from services.Memory.service import MemoryService
from services.Memory.config import MemoryConfig


@pytest_asyncio.fixture
async def memory_service():
    """创建 Memory 服务实例"""
    service = MemoryService()
    await service.initialize()
    yield service
    await service.close()


@pytest.mark.asyncio
async def test_calculate_exploration_score(memory_service):
    """测试单个兴趣维度的探索度计算"""
    child_id = "test_child_001"
    
    # 直接在图中创建测试数据（模拟 Graphiti 创建的结构）
    # 注意：使用 group_id 而不是 Child 节点
    
    behaviors_data = [
        {
            "uuid": "behavior_uuid_1",
            "name": "Behavior_玩彩色积木",
            "description": "玩彩色积木",
            "event_type": "play",
            "dimension": "visual",
            "weight": 0.8
        },
        {
            "uuid": "behavior_uuid_2",
            "name": "Behavior_看旋转齿轮",
            "description": "看旋转齿轮",
            "event_type": "observation",
            "dimension": "visual",
            "weight": 0.9
        },
        {
            "uuid": "behavior_uuid_3",
            "name": "Behavior_看绘本彩色图片",
            "description": "看绘本彩色图片",
            "event_type": "reading",
            "dimension": "visual",
            "weight": 0.7
        }
    ]
    
    for data in behaviors_data:
        # 创建 Behavior Entity 节点（模拟 Graphiti 结构）
        query = """
        MERGE (i:InterestDimension {dimension: $dimension})
        CREATE (b:Entity:Behavior {
            uuid: $uuid,
            name: $name,
            group_id: $group_id,
            description: $description,
            event_type: $event_type,
            created_at: datetime()
        })
        CREATE (b)-[r:show_interest {
            weight: $weight,
            reasoning: '测试数据',
            manifestation: '测试表现',
            created_at: datetime()
        }]->(i)
        """
        await memory_service.storage.execute_query(query, {
            "uuid": data["uuid"],
            "name": data["name"],
            "group_id": child_id,
            "description": data["description"],
            "event_type": data["event_type"],
            "dimension": data["dimension"],
            "weight": data["weight"]
        })
    
    # 计算 visual 维度的探索度
    result = await memory_service.calculate_exploration_score(
        child_id=child_id,
        dimension="visual"
    )
    
    print("\n=== Visual 维度探索度 ===")
    print(f"探索度: {result['exploration_score']}")
    print(f"行为数量: {result['behavior_count']}")
    print(f"权重总和: {result['total_weight']}")
    print(f"事件类型: {result['event_types']}")
    print(f"时间跨度: {result['time_span_days']} 天")
    
    assert result['exploration_score'] > 0
    assert result['behavior_count'] >= 3
    assert result['total_weight'] > 2.0  # 0.8 + 0.9 + 0.7 = 2.4


@pytest.mark.asyncio
async def test_calculate_all_exploration_scores(memory_service):
    """测试计算所有兴趣维度的探索度"""
    child_id = "test_child_002"
    
    # 记录多样化的行为
    behaviors = [
        "小明玩彩色积木",  # visual + construction
        "小明听音乐就摇摆",  # auditory + motor
        "小明玩水很开心",  # tactile + visual
        "小明把玩具排成一排",  # order
    ]
    
    for behavior_text in behaviors:
        await memory_service.record_behavior(
            child_id=child_id,
            raw_input=behavior_text
        )
    
    # 计算所有维度的探索度
    results = await memory_service.calculate_all_exploration_scores(
        child_id=child_id
    )
    
    print("\n=== 所有兴趣维度探索度 ===")
    for result in results:
        print(f"{result['dimension']}: {result['exploration_score']} "
              f"(行为数: {result['behavior_count']}, 权重: {result['total_weight']})")
    
    assert len(results) > 0
    # 验证按探索度降序排序
    for i in range(len(results) - 1):
        assert results[i]['exploration_score'] >= results[i+1]['exploration_score']


@pytest.mark.asyncio
async def test_get_behaviors_for_interest_dimension(memory_service):
    """测试获取某个兴趣维度的关联行为"""
    child_id = "test_child_003"
    
    # 记录一些行为
    behaviors = [
        "小明玩彩色积木",
        "小明看旋转齿轮",
        "小明看绘本"
    ]
    
    for behavior_text in behaviors:
        await memory_service.record_behavior(
            child_id=child_id,
            raw_input=behavior_text
        )
    
    # 获取 visual 维度的所有行为
    behaviors_data = await memory_service.get_behaviors_for_interest_dimension(
        child_id=child_id,
        dimension="visual"
    )
    
    print("\n=== Visual 维度关联行为 ===")
    for behavior in behaviors_data:
        print(f"行为: {behavior['behavior']}")
        print(f"  权重: {behavior['weight']}")
        print(f"  推理: {behavior['reasoning']}")
        print(f"  表现: {behavior['manifestation']}")
        print()
    
    assert len(behaviors_data) > 0
    # 验证每个行为都有权重
    for behavior in behaviors_data:
        assert behavior['weight'] is not None
        assert 0 <= behavior['weight'] <= 1


@pytest.mark.asyncio
async def test_get_multi_interest_behaviors(memory_service):
    """测试查找涉及多个兴趣维度的行为"""
    child_id = "test_child_004"
    
    # 记录一些涉及多个维度的行为
    behaviors = [
        "小明玩彩色积木，搭了一个高塔",  # visual + construction + order
        "小明听音乐就摇摆",  # auditory + motor
        "小明玩水，看水流",  # tactile + visual
    ]
    
    for behavior_text in behaviors:
        await memory_service.record_behavior(
            child_id=child_id,
            raw_input=behavior_text
        )
    
    # 查找涉及至少2个维度的行为
    multi_interest_behaviors = await memory_service.get_multi_interest_behaviors(
        child_id=child_id,
        min_dimensions=2
    )
    
    print("\n=== 多维度兴趣行为 ===")
    for behavior in multi_interest_behaviors:
        print(f"行为: {behavior['behavior']}")
        print(f"  涉及维度数: {behavior['dimension_count']}")
        print(f"  兴趣维度:")
        for interest in behavior['interests']:
            print(f"    - {interest['dimension']} (权重: {interest['weight']})")
        print()
    
    assert len(multi_interest_behaviors) > 0
    # 验证每个行为至少涉及2个维度
    for behavior in multi_interest_behaviors:
        assert behavior['dimension_count'] >= 2


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
