"""
测试 Graphiti 服务
"""
import pytest
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from services.real.graphiti_service import GraphitiService
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()


# 注意：这些测试需要 Neo4j 数据库运行
# 如果没有 Neo4j，测试会失败
# 可以使用 Docker 快速启动: docker run -p 7688:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest

@pytest.fixture
def graphiti_service():
    """创建 Graphiti 服务实例"""
    service = GraphitiService(
        neo4j_uri="bolt://localhost:7688",
        neo4j_user="neo4j",
        neo4j_password="password"
    )
    yield service
    # 清理
    asyncio.run(service.close())


@pytest.mark.asyncio
async def test_save_memories(graphiti_service):
    """测试保存记忆"""
    child_id = "test-child-001"
    
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "孩子主动与妈妈进行眼神接触，持续3秒",
            "metadata": {
                "dimension": "eye_contact",
                "session_id": "session-001"
            }
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "milestone",
            "content": "首次主动发起对话",
            "metadata": {
                "dimension": "two_way_communication",
                "significance": "high"
            }
        }
    ]
    
    # 保存记忆
    await graphiti_service.save_memories(child_id, memories)
    
    # 验证：获取最近记忆
    recent_memories = await graphiti_service.get_recent_memories(child_id, days=1)
    
    assert len(recent_memories) > 0
    print(f"✓ 成功保存并检索到 {len(recent_memories)} 条记忆")


@pytest.mark.asyncio
async def test_analyze_trends(graphiti_service):
    """测试趋势分析"""
    child_id = "test-child-001"
    dimension = "eye_contact"
    
    # 先保存一些数据
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": f"眼神接触观察 {i}",
            "metadata": {"dimension": dimension}
        }
        for i in range(5)
    ]
    
    await graphiti_service.save_memories(child_id, memories)
    
    # 分析趋势
    trend_result = await graphiti_service.analyze_trends(child_id, dimension)
    
    assert "dimension" in trend_result
    assert "trend" in trend_result
    assert trend_result["dimension"] == dimension
    
    print(f"✓ 趋势分析结果: {trend_result}")


@pytest.mark.asyncio
async def test_detect_milestones(graphiti_service):
    """测试里程碑检测"""
    child_id = "test-child-001"
    
    # 保存一些里程碑数据
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "milestone",
            "content": "首次主动微笑",
            "metadata": {"significance": "high"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "milestone",
            "content": "突破性进步：能够完成3轮对话",
            "metadata": {"significance": "high"}
        }
    ]
    
    await graphiti_service.save_memories(child_id, memories)
    
    # 检测里程碑
    milestones = await graphiti_service.detect_milestones(child_id)
    
    assert isinstance(milestones, list)
    print(f"✓ 检测到 {len(milestones)} 个里程碑")


@pytest.mark.asyncio
async def test_build_context(graphiti_service):
    """测试构建上下文"""
    child_id = "test-child-001"
    
    # 保存一些数据
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "眼神接触频率提升",
            "metadata": {"dimension": "eye_contact"}
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "能够进行双向沟通",
            "metadata": {"dimension": "two_way_communication"}
        }
    ]
    
    await graphiti_service.save_memories(child_id, memories)
    
    # 构建上下文
    context = await graphiti_service.build_context(child_id)
    
    assert "recentTrends" in context
    assert "attentionPoints" in context
    assert "activeGoals" in context
    assert "lastUpdated" in context
    
    print(f"✓ 上下文构建成功")
    print(f"  - 趋势数量: {len(context['recentTrends'])}")
    print(f"  - 关注点: {context['attentionPoints']}")


@pytest.mark.asyncio
async def test_detect_plateau(graphiti_service):
    """测试平台期检测"""
    child_id = "test-child-001"
    dimension = "emotional_regulation"
    
    # 检测平台期
    plateau_result = await graphiti_service.detect_plateau(child_id, dimension)
    
    assert "dimension" in plateau_result
    assert "isPlateau" in plateau_result
    assert "suggestion" in plateau_result
    
    print(f"✓ 平台期检测结果: {plateau_result}")


if __name__ == "__main__":
    # 运行测试
    print("=" * 60)
    print("Graphiti 服务测试")
    print("=" * 60)
    print("\n注意：需要 Neo4j 数据库运行在 localhost:7687")
    print("快速启动命令: docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:latest\n")
    
    pytest.main([__file__, "-v", "-s"])
