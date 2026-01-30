"""
测试 Graphiti 高级功能
验证社区检测、时序分析、智能搜索等功能
"""
import asyncio
import sys
from datetime import datetime

sys.path.insert(0, '.')

from services.Memory import get_memory_service
from services.Memory.models.nodes import Person


async def test_graphiti_advanced_features():
    """测试 Graphiti 高级功能"""
    
    print("\n" + "="*70)
    print("Graphiti 高级功能测试")
    print("="*70)
    
    memory = await get_memory_service()
    
    try:
        # ========== 准备测试数据 ==========
        print("\n[准备] 创建测试数据...")
        child = Person(
            person_id="test_advanced_child",
            person_type="child",
            name="高级功能测试小明",
            role="patient",
            basic_info={"age": 5, "diagnosis": "ASD"},
            created_at=datetime.now().isoformat()
        )
        child_id = await memory.save_child(child)
        print(f"✅ 孩子档案创建: {child_id}")
        
        # 记录多条行为，构建图谱
        test_behaviors = [
            "小明今天玩积木时很专注，搭了一个高塔",
            "小明听到音乐就开心地跳舞，还拉着妈妈一起跳",
            "小明看到小汽车就很兴奋，推着车跑来跑去",
            "小明今天主动和小朋友分享玩具",
            "小明在画画时很安静，画了很多圆圈",
            "小明听到门铃声会主动去开门",
            "小明喜欢看旋转的风扇，能看很久",
            "小明今天学会了自己穿鞋子"
        ]
        
        print(f"\n记录 {len(test_behaviors)} 条行为...")
        for behavior_text in test_behaviors:
            await memory.record_behavior(
                child_id=child_id,
                raw_input=behavior_text,
                input_type="text"
            )
        print(f"✅ 行为记录完成")
        
        # ========== 测试 1: 社区检测 ==========
        print("\n" + "="*70)
        print("[测试 1/3] 社区检测 - 发现兴趣聚类")
        print("="*70)
        
        communities_result = await memory.discover_interest_communities(child_id)
        
        print(f"\n发现 {communities_result['total_communities']} 个社区")
        
        for i, comm in enumerate(communities_result['communities'][:3], 1):
            print(f"\n社区 {i}: {comm['name']}")
            print(f"  成员数量: {comm['size']}")
            print(f"  总结: {comm['summary'][:100]}...")
            if comm['members']:
                print(f"  成员示例: {comm['members'][0].get('name', 'N/A')}")
        
        print(f"\n洞察:")
        print(communities_result['insights'])
        
        # ========== 测试 2: 时序趋势分析 ==========
        print("\n" + "="*70)
        print("[测试 2/3] 时序趋势分析 - 分析发展趋势")
        print("="*70)
        
        # 分析兴趣趋势
        interest_trends = await memory.analyze_temporal_trends(
            child_id=child_id,
            dimension="interest",
            days=30
        )
        
        print(f"\n维度: {interest_trends['dimension']}")
        print(f"分析周期: {interest_trends['period_days']} 天")
        print(f"数据点数量: {interest_trends['total_data_points']}")
        
        if interest_trends['trends']:
            print(f"\n趋势:")
            for trend in interest_trends['trends']:
                print(f"  - {trend['name']}: {trend['trend']} (变化率: {trend['change_rate']:.1%})")
                print(f"    数据点: {len(trend['data_points'])} 个")
        
        print(f"\n总结: {interest_trends['summary']}")
        
        # 分析功能趋势
        function_trends = await memory.analyze_temporal_trends(
            child_id=child_id,
            dimension="function",
            days=30
        )
        
        print(f"\n功能维度趋势:")
        print(f"  总结: {function_trends['summary']}")
        
        # ========== 测试 3: 智能搜索 ==========
        print("\n" + "="*70)
        print("[测试 3/3] 智能搜索 - 语义检索")
        print("="*70)
        
        # 测试不同的搜索查询
        search_queries = [
            "小明喜欢什么玩具",
            "小明的社交互动情况",
            "小明的专注力表现"
        ]
        
        for query in search_queries:
            print(f"\n查询: {query}")
            search_result = await memory.intelligent_search(
                child_id=child_id,
                query=query,
                search_type="hybrid",
                num_results=3
            )
            
            print(f"  找到 {search_result['total_results']} 条结果")
            
            for i, result in enumerate(search_result['results'][:2], 1):
                print(f"  {i}. {result['fact'][:60]}...")
                if result.get('relevance_score'):
                    print(f"     相关度: {result['relevance_score']:.2f}")
        
        # ========== 总结 ==========
        print("\n" + "="*70)
        print("🎉 Graphiti 高级功能测试完成！")
        print("="*70)
        
        print("\n✅ 测试结果:")
        print(f"  ✓ 社区检测 - 发现 {communities_result['total_communities']} 个兴趣社区")
        print(f"  ✓ 时序分析 - 分析了 {interest_trends['total_data_points']} 个数据点")
        print(f"  ✓ 智能搜索 - 执行了 {len(search_queries)} 次语义搜索")
        
        print("\n📊 Graphiti 高级功能:")
        print("  • 社区检测 - 自动发现兴趣聚类和关联模式")
        print("  • 时序分析 - 追踪发展趋势和变化")
        print("  • 智能搜索 - 语义理解的精准检索")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # 清理测试数据
        print("\n清理测试数据...")
        await memory.storage.clear_child_data("test_advanced_child")
        await memory.close()
        print("✅ 清理完成")


if __name__ == "__main__":
    success = asyncio.run(test_graphiti_advanced_features())
    sys.exit(0 if success else 1)
