"""
游戏模块 Memory 集成测试
测试完整的记忆驱动闭环：推荐 → 实施 → 总结
"""
import pytest
import asyncio
from datetime import datetime

from services.Memory.service import get_memory_service
from services.Memory.config import MemoryConfig
from services.Graphiti.models.nodes import Person


@pytest.mark.asyncio
async def test_memory_service_initialization():
    """测试 Memory 服务初始化"""
    print("\n========== 测试 1: Memory 服务初始化 ==========")
    
    config = MemoryConfig()
    memory = await get_memory_service(config)
    
    assert memory is not None
    assert memory.storage is not None
    assert memory.llm_service is not None
    
    print("✅ Memory 服务初始化成功")
    
    await memory.close()


@pytest.mark.asyncio
async def test_create_child_profile():
    """测试创建孩子档案"""
    print("\n========== 测试 2: 创建孩子档案 ==========")
    
    memory = await get_memory_service()
    
    # 创建测试孩子
    child = Person(
        person_id="test_child_game_001",
        person_type="child",
        name="测试小明",
        role="patient",
        basic_info={
            "age": 5,
            "diagnosis": "ASD",
            "created_for": "game_integration_test"
        },
        created_at=datetime.now().isoformat()
    )
    
    child_id = await memory.save_child(child)
    
    assert child_id == "test_child_game_001"
    
    # 验证孩子档案
    saved_child = await memory.get_child(child_id)
    assert saved_child is not None
    assert saved_child['name'] == "测试小明"
    
    print(f"✅ 孩子档案创建成功: {child_id}")
    
    await memory.close()


@pytest.mark.asyncio
async def test_record_behavior():
    """测试记录行为"""
    print("\n========== 测试 3: 记录行为 ==========")
    
    memory = await get_memory_service()
    
    # 记录行为
    raw_input = "今天小明主动把积木递给我，还看着我的眼睛笑了，这是第一次！"
    
    result = await memory.record_behavior(
        child_id="test_child_game_001",
        raw_input=raw_input,
        input_type="text"
    )
    
    assert result is not None
    assert result['behavior_id'] is not None
    assert result['child_id'] == "test_child_game_001"
    assert result['event_type'] in ['social', 'emotion', 'communication', 'firstTime', 'other']
    assert result['significance'] in ['breakthrough', 'improvement', 'normal', 'concern']
    
    print(f"✅ 行为记录成功:")
    print(f"  - behavior_id: {result['behavior_id']}")
    print(f"  - 事件类型: {result['event_type']}")
    print(f"  - 重要性: {result['significance']}")
    print(f"  - 描述: {result['description']}")
    
    await memory.close()


@pytest.mark.asyncio
async def test_save_game_plan():
    """测试保存游戏方案"""
    print("\n========== 测试 4: 保存游戏方案 ==========")
    
    memory = await get_memory_service()
    
    # 创建游戏方案
    game_data = {
        "game_id": "test_game_001",
        "child_id": "test_child_game_001",
        "name": "彩色积木塔",
        "description": "通过积木传递建立双向沟通",
        "created_at": datetime.now().isoformat(),
        "status": "recommended",
        "design": {
            "target_dimension": "eye_contact",
            "goals": {"primary_goal": "建立眼神接触的主动性"},
            "steps": [
                {
                    "step_number": 1,
                    "title": "建立兴趣",
                    "description": "展示彩色积木"
                }
            ]
        },
        "implementation": {}
    }
    
    game_id = await memory.save_game(game_data)
    
    assert game_id == "test_game_001"
    
    # 验证游戏方案
    saved_game = await memory.get_game(game_id)
    assert saved_game is not None
    assert saved_game['name'] == "彩色积木塔"
    assert saved_game['child_id'] == "test_child_game_001"
    
    print(f"✅ 游戏方案保存成功: {game_id}")
    
    await memory.close()


@pytest.mark.asyncio
async def test_summarize_game():
    """测试游戏总结"""
    print("\n========== 测试 5: 游戏总结 ==========")
    
    memory = await get_memory_service()
    
    # 准备视频分析和家长反馈
    video_analysis = {
        "duration": "15分钟",
        "key_moments": [
            {"time": "02:15", "description": "主动递积木"},
            {"time": "08:30", "description": "眼神接触5次"}
        ]
    }
    
    parent_feedback = {
        "notes": "孩子今天状态很好，比上次更主动了"
    }
    
    # 调用游戏总结
    result = await memory.summarize_game(
        game_id="test_game_001",
        video_analysis=video_analysis,
        parent_feedback=parent_feedback
    )
    
    assert result is not None
    assert result['game_id'] == "test_game_001"
    assert result['status'] == "completed"
    assert 'implementation' in result
    assert 'summary' in result['implementation']
    
    print(f"✅ 游戏总结成功:")
    print(f"  - 参与度得分: {result['implementation'].get('engagement_score', 'N/A')}")
    print(f"  - 目标达成得分: {result['implementation'].get('goal_achievement_score', 'N/A')}")
    print(f"  - 总结: {result['implementation'].get('summary', 'N/A')[:100]}...")
    
    await memory.close()


@pytest.mark.asyncio
async def test_generate_interest_assessment():
    """测试生成兴趣评估"""
    print("\n========== 测试 6: 生成兴趣评估 ==========")
    
    memory = await get_memory_service()
    
    # 生成兴趣挖掘评估
    result = await memory.generate_assessment(
        child_id="test_child_game_001",
        assessment_type="interest_mining"
    )
    
    assert result is not None
    assert result['assessment_id'] is not None
    assert result['child_id'] == "test_child_game_001"
    assert result['assessment_type'] == "interest_mining"
    assert 'analysis' in result
    
    print(f"✅ 兴趣评估生成成功:")
    print(f"  - assessment_id: {result['assessment_id']}")
    print(f"  - 评估类型: {result['assessment_type']}")
    
    await memory.close()


@pytest.mark.asyncio
async def test_get_recent_games():
    """测试获取最近游戏"""
    print("\n========== 测试 7: 获取最近游戏 ==========")
    
    memory = await get_memory_service()
    
    # 获取最近游戏
    recent_games = await memory.get_recent_games(
        child_id="test_child_game_001",
        limit=5
    )
    
    assert recent_games is not None
    assert isinstance(recent_games, list)
    assert len(recent_games) > 0
    
    print(f"✅ 获取最近游戏成功: {len(recent_games)} 个游戏")
    
    for game in recent_games:
        print(f"  - {game.get('name', 'N/A')} (状态: {game.get('status', 'N/A')})")
    
    await memory.close()


@pytest.mark.asyncio
async def test_get_latest_assessment():
    """测试获取最新评估"""
    print("\n========== 测试 8: 获取最新评估 ==========")
    
    memory = await get_memory_service()
    
    # 获取最新评估
    latest_assessment = await memory.get_latest_assessment(
        child_id="test_child_game_001",
        assessment_type="interest_mining"
    )
    
    assert latest_assessment is not None
    assert latest_assessment['child_id'] == "test_child_game_001"
    assert latest_assessment['assessment_type'] == "interest_mining"
    
    print(f"✅ 获取最新评估成功:")
    print(f"  - assessment_id: {latest_assessment['assessment_id']}")
    print(f"  - 时间: {latest_assessment['timestamp']}")
    
    await memory.close()


@pytest.mark.asyncio
async def test_cleanup():
    """清理测试数据"""
    print("\n========== 测试 9: 清理测试数据 ==========")
    
    memory = await get_memory_service()
    
    # 清理测试孩子的所有数据
    await memory.storage.clear_child_data("test_child_game_001")
    
    print("✅ 测试数据清理完成")
    
    await memory.close()


@pytest.mark.asyncio
async def test_complete_game_cycle():
    """测试完整的游戏闭环"""
    print("\n========== 测试 10: 完整的游戏闭环 ==========")
    
    memory = await get_memory_service()
    
    try:
        # 1. 创建孩子档案
        child = Person(
            person_id="test_child_cycle_001",
            person_type="child",
            name="闭环测试小红",
            role="patient",
            basic_info={"age": 4, "diagnosis": "ASD"},
            created_at=datetime.now().isoformat()
        )
        await memory.save_child(child)
        print("  ✓ 步骤 1: 创建孩子档案")
        
        # 2. 记录一些行为
        behaviors = [
            "小红今天玩积木时很专注，搭了一个高塔",
            "小红听到音乐就开心地跳舞",
            "小红主动拉着妈妈的手去拿玩具"
        ]
        
        for behavior_text in behaviors:
            await memory.record_behavior(
                child_id="test_child_cycle_001",
                raw_input=behavior_text,
                input_type="text"
            )
        print("  ✓ 步骤 2: 记录行为")
        
        # 3. 生成兴趣评估
        assessment = await memory.generate_assessment(
            child_id="test_child_cycle_001",
            assessment_type="interest_mining"
        )
        print("  ✓ 步骤 3: 生成兴趣评估")
        
        # 4. 保存游戏方案（模拟推荐）
        game_data = {
            "game_id": "test_game_cycle_001",
            "child_id": "test_child_cycle_001",
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
        await memory.save_game(game_data)
        print("  ✓ 步骤 4: 保存游戏方案")
        
        # 5. 游戏总结（模拟实施后）
        await memory.summarize_game(
            game_id="test_game_cycle_001",
            video_analysis={"duration": "20分钟", "key_moments": []},
            parent_feedback={"notes": "孩子很喜欢"}
        )
        print("  ✓ 步骤 5: 游戏总结")
        
        # 6. 验证数据完整性
        saved_child = await memory.get_child("test_child_cycle_001")
        assert saved_child is not None
        
        saved_game = await memory.get_game("test_game_cycle_001")
        assert saved_game is not None
        assert saved_game['status'] == "completed"
        
        latest_assessment = await memory.get_latest_assessment("test_child_cycle_001")
        assert latest_assessment is not None
        
        print("  ✓ 步骤 6: 验证数据完整性")
        
        print("\n✅ 完整的游戏闭环测试成功！")
        print("   推荐 → 实施 → 总结 → 评估 → 推荐（循环）")
        
    finally:
        # 清理
        await memory.storage.clear_child_data("test_child_cycle_001")
        await memory.close()


if __name__ == "__main__":
    # 运行所有测试
    asyncio.run(test_memory_service_initialization())
    asyncio.run(test_create_child_profile())
    asyncio.run(test_record_behavior())
    asyncio.run(test_save_game_plan())
    asyncio.run(test_summarize_game())
    asyncio.run(test_generate_interest_assessment())
    asyncio.run(test_get_recent_games())
    asyncio.run(test_get_latest_assessment())
    asyncio.run(test_cleanup())
    asyncio.run(test_complete_game_cycle())
