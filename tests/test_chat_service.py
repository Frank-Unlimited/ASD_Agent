"""
测试聊天服务
"""
import asyncio
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.container import (
    get_memory_service,
    get_sqlite_service,
    get_observation_service,
    get_game_recommender,
    get_game_summarizer,
    get_assessment_service,
    init_services
)
from services.Chat import ChatService, ChatTools
from services.Report import ReportService


async def test_chat():
    """测试聊天功能"""
    print("\n" + "="*60)
    print("测试聊天服务")
    print("="*60)
    
    # 1. 初始化服务
    print("\n[1] 初始化服务...")
    init_services()
    
    memory_service = await get_memory_service()
    sqlite_service = get_sqlite_service()
    observation_service = await get_observation_service()
    game_recommender = await get_game_recommender()
    game_summarizer = await get_game_summarizer()
    assessment_service = await get_assessment_service()
    report_service = ReportService(sqlite_service, memory_service)
    
    print("✅ 服务初始化成功")
    
    # 2. 创建聊天服务
    print("\n[2] 创建聊天服务...")
    chat_tools = ChatTools(
        memory_service=memory_service,
        sqlite_service=sqlite_service,
        observation_service=observation_service,
        game_recommender=game_recommender,
        game_summarizer=game_summarizer,
        assessment_service=assessment_service,
        report_service=report_service
    )
    
    chat_service = ChatService(chat_tools)
    print("✅ 聊天服务创建成功")
    
    # 3. 测试场景
    test_child_id = "test_child_001"
    conversation_history = []
    
    test_messages = [
        "你好！",
        "辰辰今天主动和小朋友分享玩具了",
        "今天玩什么游戏好？",
        "孩子最近有进步吗？"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n[{i+2}] 测试消息: {message}")
        print("-" * 60)
        
        result = await chat_service.chat(
            message=message,
            child_id=test_child_id,
            conversation_history=conversation_history
        )
        
        print(f"\n助手回复:")
        print(result["response"])
        
        if result["tool_calls"]:
            print(f"\n工具调用 ({len(result['tool_calls'])} 个):")
            for tool_call in result["tool_calls"]:
                print(f"  - {tool_call['tool_name']}: {tool_call['result'].get('success', False)}")
        
        # 更新对话历史
        conversation_history = result["conversation_history"]
        
        print("-" * 60)
    
    # 4. 关闭服务
    print(f"\n[{len(test_messages)+3}] 关闭服务...")
    await memory_service.close()
    print("✅ 服务已关闭")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_chat())
