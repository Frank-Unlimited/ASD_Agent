"""
Graphiti 服务使用示例
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.container import container, init_services


async def main():
    """主函数"""
    print("=" * 60)
    print("Graphiti 服务使用示例")
    print("=" * 60)
    
    # 1. 初始化服务容器
    print("\n[1] 初始化服务...")
    init_services()
    
    # 2. 获取 Graphiti 服务
    graphiti = container.get('graphiti')
    print(f"✓ 服务类型: {type(graphiti).__name__}")
    print(f"✓ 服务名称: {graphiti.get_service_name()}")
    print(f"✓ 服务版本: {graphiti.get_service_version()}")
    
    # 3. 保存记忆
    print("\n[2] 保存记忆...")
    child_id = "demo-child-001"
    
    memories = [
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "孩子主动与妈妈进行眼神接触，持续3秒",
            "metadata": {
                "dimension": "eye_contact",
                "session_id": "session-demo-001"
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
        },
        {
            "timestamp": datetime.now().isoformat(),
            "type": "observation",
            "content": "能够识别并表达开心的情绪",
            "metadata": {
                "dimension": "emotional_expression"
            }
        }
    ]
    
    await graphiti.save_memories(child_id, memories)
    print(f"✓ 成功保存 {len(memories)} 条记忆")
    
    # 4. 获取最近记忆
    print("\n[3] 获取最近记忆...")
    recent_memories = await graphiti.get_recent_memories(child_id, days=7)
    print(f"✓ 找到 {len(recent_memories)} 条最近记忆")
    
    if recent_memories:
        print("\n最近的记忆:")
        for i, mem in enumerate(recent_memories[:3], 1):
            print(f"  {i}. {mem.get('content', 'N/A')}")
    
    # 5. 分析趋势
    print("\n[4] 分析趋势...")
    dimensions = ["eye_contact", "two_way_communication", "emotional_expression"]
    
    for dim in dimensions:
        trend = await graphiti.analyze_trends(child_id, dim)
        print(f"  - {dim}: {trend.get('trend', 'unknown')} (数据点: {trend.get('dataPoints', 0)})")
    
    # 6. 检测里程碑
    print("\n[5] 检测里程碑...")
    milestones = await graphiti.detect_milestones(child_id)
    print(f"✓ 检测到 {len(milestones)} 个里程碑")
    
    if milestones:
        print("\n里程碑事件:")
        for i, milestone in enumerate(milestones[:3], 1):
            print(f"  {i}. {milestone.get('description', 'N/A')}")
    
    # 7. 构建上下文
    print("\n[6] 构建上下文...")
    context = await graphiti.build_context(child_id)
    
    print(f"✓ 上下文构建完成")
    print(f"  - 趋势维度数: {len(context.get('recentTrends', {}))}")
    print(f"  - 关注点数: {len(context.get('attentionPoints', []))}")
    print(f"  - 活跃目标数: {len(context.get('activeGoals', []))}")
    
    if context.get('attentionPoints'):
        print("\n关注点:")
        for point in context['attentionPoints']:
            print(f"  • {point}")
    
    # 8. 检测平台期
    print("\n[7] 检测平台期...")
    plateau = await graphiti.detect_plateau(child_id, "eye_contact")
    print(f"  - 是否平台期: {plateau.get('isPlateau', False)}")
    print(f"  - 建议: {plateau.get('suggestion', 'N/A')}")
    
    print("\n" + "=" * 60)
    print("✓ 所有功能测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
