"""
测试 Memory 服务的智能写入功能
"""
import asyncio
import pytest
from services.Memory.service import get_memory_service
from services.Memory.config import MemoryConfig


@pytest.mark.asyncio
async def test_record_behavior():
    """测试行为记录功能"""
    print("\n========== 测试 record_behavior ==========")
    
    # 初始化服务
    config = MemoryConfig()
    memory = await get_memory_service(config)
    
    # 创建测试孩子
    from services.Graphiti.models.nodes import Person
    child = Person(
        person_id="test_child_001",
        person_type="child",
        name="小明",
        role="patient",
        basic_info={"age": 5, "diagnosis": "ASD"},
        created_at="2024-01-01T00:00:00Z"
    )
    await memory.storage.create_person(child)
    
    # 测试行为记录
    raw_input = "今天小明主动把积木递给我，还看着我的眼睛笑了，这是第一次！"
    
    result = await memory.record_behavior(
        child_id="test_child_001",
        raw_input=raw_input,
        input_type="text"
    )
    
    print(f"\n✅ 行为记录成功:")
    print(f"  - behavior_id: {result['behavior_id']}")
    print(f"  - 事件类型: {result['event_type']}")
    print(f"  - 重要性: {result['significance']}")
    print(f"  - 描述: {result['description']}")
    print(f"  - 涉及对象: {result['objects_involved']}")
    print(f"  - 相关兴趣: {result['related_interests']}")
    print(f"  - 相关功能: {result['related_functions']}")
    print(f"  - AI 分析: {result['ai_analysis']}")
    
    # 清理
    await memory.storage.clear_child_data("test_child_001")
    await memory.close()


@pytest.mark.asyncio
async def test_generate_assessment():
    """测试评估生成功能"""
    print("\n========== 测试 generate_assessment ==========")
    
    # 初始化服务
    config = MemoryConfig()
    memory = await get_memory_service(config)
    
    # 创建测试孩子
    from services.Graphiti.models.nodes import Person, Behavior
    child = Person(
        person_id="test_child_002",
        person_type="child",
        name="小红",
        role="patient",
        basic_info={"age": 4, "diagnosis": "ASD"},
        created_at="2024-01-01T00:00:00Z"
    )
    await memory.storage.create_person(child)
    
    # 创建一些测试行为记录
    behaviors = [
        "小红今天玩积木时很专注，搭了一个高塔",
        "小红听到音乐就开心地跳舞",
        "小红主动拉着妈妈的手去拿玩具"
    ]
    
    for desc in behaviors:
        behavior = Behavior(
            behavior_id=f"behavior_{desc[:5]}",
            child_id="test_child_002",
            timestamp="2024-01-15T10:00:00Z",
            event_type="social",
            description=desc,
            raw_input=desc,
            input_type="text",
            significance="improvement",
            ai_analysis={},
            context={},
            evidence={}
        )
        await memory.storage.create_behavior(behavior)
    
    # 测试兴趣挖掘评估
    result = await memory.generate_assessment(
        child_id="test_child_002",
        assessment_type="interest_mining"
    )
    
    print(f"\n✅ 兴趣挖掘评估成功:")
    print(f"  - assessment_id: {result['assessment_id']}")
    print(f"  - 评估类型: {result['assessment_type']}")
    print(f"  - 分析结果: {result['analysis']}")
    
    # 清理
    await memory.storage.clear_child_data("test_child_002")
    await memory.close()


@pytest.mark.asyncio
async def test_import_profile():
    """测试档案导入功能"""
    print("\n========== 测试 import_profile ==========")
    
    # 初始化服务
    config = MemoryConfig()
    memory = await get_memory_service(config)
    
    # 测试档案数据
    profile_data = {
        "name": "小刚",
        "age": 6,
        "diagnosis": "自闭症谱系障碍（ASD）",
        "medical_reports": """
        诊断时间：2023年3月
        主要症状：社交互动困难、语言发展迟缓、重复刻板行为
        CARS评分：35分（中度自闭症）
        """,
        "assessment_scales": """
        ABC量表：总分68分
        - 感觉：12分
        - 交往：18分
        - 躯体运动：10分
        - 语言：15分
        - 生活自理：13分
        """
    }
    
    result = await memory.import_profile(profile_data)
    
    print(f"\n✅ 档案导入成功:")
    print(f"  - child_id: {result['child_id']}")
    print(f"  - assessment_id: {result['assessment_id']}")
    print(f"  - 消息: {result['message']}")
    
    # 验证孩子档案
    child = await memory.get_child(result['child_id'])
    print(f"\n  孩子档案:")
    print(f"    - 姓名: {child['name']}")
    print(f"    - 基本信息: {child['basic_info']}")
    
    # 验证初始评估
    assessment = await memory.get_latest_assessment(result['child_id'])
    print(f"\n  初始评估:")
    print(f"    - 评估类型: {assessment['assessment_type']}")
    print(f"    - 分析结果: {assessment['analysis']}")
    
    # 清理
    await memory.storage.clear_child_data(result['child_id'])
    await memory.close()


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_record_behavior())
    asyncio.run(test_generate_assessment())
    asyncio.run(test_import_profile())
