"""
测试 Tools 与 LLM 的集成
交互式测试脚本
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from openai import AsyncOpenAI
from src.container import init_services
from src.config import settings
from tools import get_tools_for_llm, execute_tool_calls_from_message


async def chat_with_tools():
    """与 LLM 进行带工具的对话"""
    
    # 初始化服务
    print("🔧 初始化服务...")
    init_services()
    
    # 初始化 OpenAI 客户端（使用 Qwen API）
    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url
    )
    
    # 获取工具列表
    tools = get_tools_for_llm()
    print(f"✅ 已加载 {len(tools)} 个工具\n")
    
    # 系统提示
    system_prompt = """你是一个 ASD 儿童干预助手，可以使用工具来：
1. 查询和管理孩子的档案信息（SQLite）
2. 保存和查询干预记忆（Memory）
3. 分析干预视频（Video Analysis）
4. 检索方法论、游戏、量表等知识（RAG）

请根据用户的需求，选择合适的工具来完成任务。"""
    
    # 对话历史
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    
    print("=" * 60)
    print("🤖 ASD 干预助手（带工具调用）")
    print("=" * 60)
    print("提示：输入 'quit' 或 'exit' 退出")
    print("提示：输入 'clear' 清空对话历史")
    print("提示：输入 'tools' 查看可用工具")
    print("=" * 60)
    print()
    
    while True:
        # 获取用户输入
        try:
            user_input = input("👤 你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n👋 再见！")
            break
        
        if not user_input:
            continue
        
        # 处理特殊命令
        if user_input.lower() in ['quit', 'exit']:
            print("\n👋 再见！")
            break
        
        if user_input.lower() == 'clear':
            messages = [{"role": "system", "content": system_prompt}]
            print("✅ 对话历史已清空\n")
            continue
        
        if user_input.lower() == 'tools':
            print("\n📦 可用工具列表:")
            print("  SQLite: get_child_profile, save_child_profile, create_session, update_session, get_session_history, delete_child")
            print("  Memory: save_memories, get_recent_memories, build_context, analyze_trends, detect_milestones, clear_memories")
            print("  Video: analyze_video")
            print("  RAG: search_methodology, search_games, search_games_by_dimension, search_games_by_interest, get_game_details, search_scale, search_cases")
            print()
            continue
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_input})
        
        try:
            # 第一次调用 LLM
            print("🤔 思考中...")
            response = await client.chat.completions.create(
                model=settings.llm_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7
            )
            
            message = response.choices[0].message
            
            # 检查是否需要调用工具
            if message.tool_calls:
                print(f"🔧 需要调用 {len(message.tool_calls)} 个工具:")
                for tc in message.tool_calls:
                    print(f"  - {tc.function.name}")
                
                # 将 LLM 的响应添加到消息历史
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                })
                
                # 执行工具调用
                print("⚙️  执行工具...")
                tool_results = await execute_tool_calls_from_message(message)
                
                # 显示工具结果（简化）
                for result in tool_results:
                    content = result['content']
                    if len(content) > 100:
                        content = content[:100] + "..."
                    print(f"  ✅ {result['name']}: {content}")
                
                # 将工具结果添加到消息历史
                messages.extend(tool_results)
                
                # 第二次调用 LLM（获取最终答案）
                print("💭 整理答案...")
                final_response = await client.chat.completions.create(
                    model=settings.llm_model,
                    messages=messages,
                    temperature=0.7
                )
                
                final_message = final_response.choices[0].message
                assistant_reply = final_message.content
                
                # 添加到历史
                messages.append({"role": "assistant", "content": assistant_reply})
            else:
                # 没有工具调用，直接回复
                assistant_reply = message.content
                messages.append({"role": "assistant", "content": assistant_reply})
            
            # 显示助手回复
            print(f"\n🤖 助手: {assistant_reply}\n")
            
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}\n")
            # 移除最后添加的用户消息
            if messages[-1]["role"] == "user":
                messages.pop()


async def main():
    """主函数"""
    await chat_with_tools()


if __name__ == "__main__":
    asyncio.run(main())
