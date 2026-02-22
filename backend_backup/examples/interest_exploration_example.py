"""
兴趣维度探索度计算 - 使用示例

演示如何使用新的兴趣维度探索度计算功能
"""
import asyncio
from services.Memory.service import MemoryService
from services.Memory.config import MemoryConfig


async def main():
    """主函数"""
    
    # 1. 创建 Memory 服务
    config = MemoryConfig(enable_llm=True)
    memory_service = MemoryService(config)
    await memory_service.initialize()
    
    try:
        child_id = "example_child_001"
        
        print("=" * 60)
        print("兴趣维度探索度计算 - 使用示例")
        print("=" * 60)
        
        # 2. 记录一些行为
        print("\n步骤 1: 记录行为观察")
        print("-" * 60)
        
        behaviors = [
            "小明今天玩彩色积木，搭了一个高塔，很开心，玩了10分钟",
            "小明看到旋转的齿轮就盯着看，很专注，看了5分钟",
            "小明听到音乐就开始摇摆，很兴奋",
            "小明玩水，看水流，玩了15分钟",
            "小明把玩具排成一排，很认真",
        ]
        
        for i, behavior_text in enumerate(behaviors, 1):
            print(f"\n记录 {i}: {behavior_text}")
            result = await memory_service.record_behavior(
                child_id=child_id,
                raw_input=behavior_text
            )
            print(f"  ✓ 已记录，行为ID: {result['behavior_id'][:8]}...")
        
        # 3. 计算所有兴趣维度的探索度
        print("\n\n步骤 2: 计算所有兴趣维度的探索度")
        print("-" * 60)
        
        all_scores = await memory_service.calculate_all_exploration_scores(child_id)
        
        print(f"\n发现 {len(all_scores)} 个活跃的兴趣维度：\n")
        for score_data in all_scores:
            print(f"📊 {score_data['dimension'].upper()}")
            print(f"   探索度: {score_data['exploration_score']:.1f}/100")
            print(f"   行为数量: {score_data['behavior_count']}")
            print(f"   权重总和: {score_data['total_weight']:.2f}")
            print(f"   事件类型: {', '.join(score_data['event_types'])}")
            print(f"   时间跨度: {score_data['time_span_days']} 天")
            print()
        
        # 4. 查看某个维度的详细行为
        if all_scores:
            top_dimension = all_scores[0]['dimension']
            
            print(f"\n步骤 3: 查看 {top_dimension.upper()} 维度的关联行为")
            print("-" * 60)
            
            behaviors_data = await memory_service.get_behaviors_for_interest_dimension(
                child_id=child_id,
                dimension=top_dimension,
                limit=10
            )
            
            print(f"\n找到 {len(behaviors_data)} 个关联行为：\n")
            for i, behavior in enumerate(behaviors_data, 1):
                print(f"{i}. {behavior['behavior']}")
                print(f"   权重: {behavior['weight']:.2f}")
                print(f"   推理: {behavior['reasoning']}")
                if behavior['manifestation']:
                    print(f"   表现: {behavior['manifestation']}")
                print()
        
        # 5. 查找多维度兴趣行为
        print("\n步骤 4: 查找涉及多个兴趣维度的行为")
        print("-" * 60)
        
        multi_interest = await memory_service.get_multi_interest_behaviors(
            child_id=child_id,
            min_dimensions=2
        )
        
        if multi_interest:
            print(f"\n找到 {len(multi_interest)} 个多维度兴趣行为：\n")
            for i, behavior in enumerate(multi_interest, 1):
                print(f"{i}. {behavior['behavior']}")
                print(f"   涉及 {behavior['dimension_count']} 个维度:")
                for interest in behavior['interests']:
                    print(f"     • {interest['dimension']} (权重: {interest['weight']:.2f})")
                    if interest['reasoning']:
                        print(f"       理由: {interest['reasoning']}")
                print()
        else:
            print("\n暂无涉及多个维度的行为")
        
        # 6. 总结
        print("\n" + "=" * 60)
        print("总结")
        print("=" * 60)
        print(f"\n✓ 共记录 {len(behaviors)} 个行为")
        print(f"✓ 发现 {len(all_scores)} 个活跃的兴趣维度")
        if all_scores:
            print(f"✓ 最强兴趣维度: {all_scores[0]['dimension']} "
                  f"(探索度: {all_scores[0]['exploration_score']:.1f})")
        print(f"✓ 多维度兴趣行为: {len(multi_interest)} 个")
        
        print("\n💡 提示:")
        print("  - 探索度反映了孩子在该维度的行为数量和多样性")
        print("  - 权重反映了行为对该维度的贡献程度")
        print("  - 多维度兴趣行为可能特别有价值，因为它们同时满足多个兴趣点")
        
    finally:
        # 关闭服务
        await memory_service.close()


if __name__ == "__main__":
    asyncio.run(main())
