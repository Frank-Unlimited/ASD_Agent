"""
集成测试：完整工作流测试
测试 Graphiti 服务在主流程中的集成
"""
import pytest
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.container import container, init_services
from src.models.state import DynamicInterventionState
from src.workflow.workflow import get_compiled_workflow


@pytest.fixture
def initial_state():
    """创建初始状态"""
    return DynamicInterventionState(
        childTimeline={
            "profile": {
                "childId": "test-integration-001",
                "name": "测试儿童",
                "age": 4,
                "diagnosis": "ASD"
            },
            "sessions": []
        },
        currentContext={},
        currentWeeklyPlan={},
        currentSession={},
        sessionHistory=[],
        workflow={
            "currentNode": "start",
            "nextNode": "assessment",
            "isHITLPaused": False
        },
        tempData={
            "reportPath": "/mock/report.pdf",
            "gameId": "game-integration-001"
        }
    )


@pytest.mark.asyncio
async def test_weekly_plan_with_graphiti(initial_state):
    """
    测试周计划生成节点（使用真实 Graphiti 服务）
    """
    print("\n" + "=" * 60)
    print("测试：周计划生成 + Graphiti 集成")
    print("=" * 60)
    
    # 1. 初始化服务
    init_services()
    
    # 2. 获取服务
    graphiti = container.get('graphiti')
    weekly_plan_service = container.get('weekly_plan')
    
    child_id = initial_state['childTimeline']['profile']['childId']
    
    # 3. 先保存一些历史记忆
    print("\n[Step 1] 保存历史记忆...")
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "孩子在积木游戏中主动与家长进行眼神接触",
            "metadata": {"dimension": "eye_contact", "session": "prev-001"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "milestone",
            "content": "首次完成3轮对话互动",
            "metadata": {"dimension": "two_way_communication", "significance": "high"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "能够识别并表达开心、难过两种情绪",
            "metadata": {"dimension": "emotional_expression"}
        }
    ]
    
    await graphiti.save_memories(child_id, memories)
    print(f"✓ 成功保存 {len(memories)} 条历史记忆")
    
    # 4. 构建上下文
    print("\n[Step 2] 从 Graphiti 构建上下文...")
    current_context = await graphiti.build_context(child_id)
    
    print(f"✓ 上下文构建完成")
    print(f"  - 趋势维度: {list(current_context.get('recentTrends', {}).keys())}")
    print(f"  - 关注点数: {len(current_context.get('attentionPoints', []))}")
    print(f"  - 活跃目标: {len(current_context.get('activeGoals', []))}")
    
    # 5. 生成周计划
    print("\n[Step 3] 生成周计划...")
    weekly_plan = await weekly_plan_service.generate_weekly_plan(
        child_id=child_id,
        child_profile=initial_state['childTimeline']['profile'],
        current_context=current_context
    )
    
    print(f"✓ 周计划生成完成")
    print(f"  - 计划ID: {weekly_plan.get('planId', 'N/A')}")
    print(f"  - 周目标: {weekly_plan.get('weeklyGoal', 'N/A')}")
    print(f"  - 关注维度: {weekly_plan.get('focusDimensions', [])}")
    
    # 6. 验证
    assert current_context is not None
    assert 'recentTrends' in current_context
    assert weekly_plan is not None
    assert 'weeklyGoal' in weekly_plan
    
    print("\n✓ 测试通过：周计划生成 + Graphiti 集成成功")


@pytest.mark.asyncio
async def test_memory_update_node(initial_state):
    """
    测试记忆更新节点（使用真实 Graphiti 服务）
    """
    print("\n" + "=" * 60)
    print("测试：记忆更新节点 + Graphiti 集成")
    print("=" * 60)
    
    # 1. 初始化服务
    init_services()
    
    # 2. 获取服务
    graphiti = container.get('graphiti')
    memory_update_service = container.get('memory_update')
    
    child_id = initial_state['childTimeline']['profile']['childId']
    
    # 3. 模拟会话数据
    session_data = {
        "sessionId": "session-test-001",
        "gameId": "game-001",
        "quickObservations": [
            {"content": "孩子主动发起互动", "dimension": "two_way_communication"}
        ],
        "finalSummary": {
            "highlights": ["眼神接触频率提升", "能够完成简单对话"],
            "concerns": ["情绪调节需要加强"]
        }
    }
    
    # 4. 更新记忆
    print("\n[Step 1] 更新记忆到 Graphiti...")
    await memory_update_service.update_memory(
        child_id=child_id,
        session_data=session_data
    )
    print("✓ 记忆更新完成")
    
    # 5. 刷新上下文
    print("\n[Step 2] 刷新上下文...")
    new_context = await memory_update_service.refresh_context(child_id)
    
    print(f"✓ 上下文刷新完成")
    print(f"  - 趋势维度: {list(new_context.get('recentTrends', {}).keys())}")
    print(f"  - 最近里程碑: {len(new_context.get('recentMilestones', []))}")
    
    # 6. 验证
    assert new_context is not None
    assert 'recentTrends' in new_context
    
    print("\n✓ 测试通过：记忆更新节点集成成功")


@pytest.mark.asyncio
async def test_full_workflow_integration():
    """
    测试完整工作流（简化版）
    重点测试 Graphiti 在流程中的作用
    """
    print("\n" + "=" * 60)
    print("测试：完整工作流集成（Graphiti）")
    print("=" * 60)
    
    # 1. 初始化服务
    init_services()
    
    # 2. 创建初始状态
    initial_state = DynamicInterventionState(
        childTimeline={
            "profile": {
                "childId": "test-workflow-001",
                "name": "工作流测试",
                "age": 5,
                "diagnosis": "ASD"
            },
            "sessions": []
        },
        currentContext={},
        currentWeeklyPlan={},
        currentSession={},
        sessionHistory=[],
        workflow={
            "currentNode": "start",
            "nextNode": "weekly_plan",
            "isHITLPaused": False
        },
        tempData={}
    )
    
    # 3. 获取服务
    graphiti = container.get('graphiti')
    child_id = initial_state['childTimeline']['profile']['childId']
    
    # 4. 模拟历史数据
    print("\n[Phase 1] 准备历史数据...")
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "孩子在游戏中表现出良好的眼神接触",
            "metadata": {"dimension": "eye_contact"}
        }
    ]
    await graphiti.save_memories(child_id, memories)
    print("✓ 历史数据准备完成")
    
    # 5. 执行周计划节点
    print("\n[Phase 2] 执行周计划节点...")
    from src.workflow.workflow import weekly_plan_node
    
    result = await weekly_plan_node(initial_state)
    
    print("✓ 周计划节点执行完成")
    print(f"  - 当前节点: {result['workflow']['currentNode']}")
    print(f"  - 下一节点: {result['workflow']['nextNode']}")
    print(f"  - 上下文已构建: {'currentContext' in result}")
    print(f"  - 周计划已生成: {'currentWeeklyPlan' in result}")
    
    # 6. 验证
    assert result['workflow']['currentNode'] == 'weekly_plan'
    assert result['workflow']['nextNode'] == 'game_start'
    assert 'currentContext' in result
    assert 'currentWeeklyPlan' in result
    
    print("\n✓ 测试通过：完整工作流集成成功")


if __name__ == "__main__":
    print("=" * 60)
    print("集成测试：Graphiti 服务在主流程中的集成")
    print("=" * 60)
    
    pytest.main([__file__, "-v", "-s"])
