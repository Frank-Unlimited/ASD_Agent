"""
快速运行集成测试
"""
import asyncio
import sys
sys.path.insert(0, '.')

from tests.test_game_memory_integration import (
    test_memory_service_initialization,
    test_create_child_profile,
    test_record_behavior,
    test_save_game_plan,
    test_summarize_game,
    test_generate_interest_assessment,
    test_get_recent_games,
    test_get_latest_assessment,
    test_cleanup,
    test_complete_game_cycle
)


async def run_all_tests():
    """运行所有测试"""
    print("="*60)
    print("游戏模块 Memory 集成测试")
    print("="*60)
    
    tests = [
        ("Memory 服务初始化", test_memory_service_initialization),
        ("创建孩子档案", test_create_child_profile),
        ("记录行为", test_record_behavior),
        ("保存游戏方案", test_save_game_plan),
        ("游戏总结", test_summarize_game),
        ("生成兴趣评估", test_generate_interest_assessment),
        ("获取最近游戏", test_get_recent_games),
        ("获取最新评估", test_get_latest_assessment),
        ("清理测试数据", test_cleanup),
        ("完整的游戏闭环", test_complete_game_cycle),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ 测试失败: {name}")
            print(f"   错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
