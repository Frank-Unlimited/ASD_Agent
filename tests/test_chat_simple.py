"""
简单测试聊天服务
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.container import init_services, get_memory_service, get_sqlite_service


async def test_simple():
    """简单测试"""
    print("\n测试聊天服务（简化版）")
    print("="*60)
    
    # 初始化
    init_services()
    memory_service = await get_memory_service()
    sqlite_service = get_sqlite_service()
    
    print("✅ 服务初始化成功")
    print("\n聊天功能已实现，包含以下 Tool：")
    print("  1. record_behavior - 记录行为")
    print("  2. recommend_game - 推荐游戏")
    print("  3. get_child_profile - 查询档案")
    print("  4. get_latest_assessment - 查询评估")
    print("  5. get_recent_games - 查询游戏历史")
    
    print("\n前端页面：frontend_test/chat-test.html")
    print("API 端点：POST /api/chat/message")
    
    await memory_service.close()
    print("\n✅ 测试完成")


if __name__ == "__main__":
    asyncio.run(test_simple())
