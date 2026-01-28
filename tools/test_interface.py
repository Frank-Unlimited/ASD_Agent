"""
测试 Tools 接口
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def test_get_tools():
    """测试获取工具列表"""
    print("=" * 60)
    print("测试 1: 获取工具列表")
    print("=" * 60)
    
    from tools import get_tools_for_llm
    
    tools = get_tools_for_llm()
    print(f"✅ 成功获取 {len(tools)} 个工具")
    
    # 显示前3个工具
    for i, tool in enumerate(tools[:3], 1):
        func = tool['function']
        print(f"\n工具 {i}: {func['name']}")
        print(f"  描述: {func['description']}")
        print(f"  参数: {list(func['parameters']['properties'].keys())}")


async def test_execute_single_tool():
    """测试执行单个工具"""
    print("\n" + "=" * 60)
    print("测试 2: 执行单个工具")
    print("=" * 60)
    
    from tools import execute_function_call
    
    # 测试获取孩子档案（Mock 数据）
    print("\n执行: get_child_profile")
    result = await execute_function_call(
        function_name="get_child_profile",
        function_arguments='{"child_id": "test-001"}'
    )
    
    if result['success']:
        print("✅ 执行成功")
        print(f"结果: {result['result']}")
    else:
        print(f"❌ 执行失败: {result['error']}")


async def test_execute_multiple_tools():
    """测试批量执行工具"""
    print("\n" + "=" * 60)
    print("测试 3: 批量执行工具")
    print("=" * 60)
    
    from tools import execute_tool_calls
    
    # 模拟 LLM 返回的工具调用
    tool_calls = [
        {
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "get_child_profile",
                "arguments": '{"child_id": "test-001"}'
            }
        },
        {
            "id": "call_2",
            "type": "function",
            "function": {
                "name": "search_games",
                "arguments": '{"query": "积木", "top_k": 3}'
            }
        }
    ]
    
    print(f"\n执行 {len(tool_calls)} 个工具调用...")
    results = await execute_tool_calls(tool_calls)
    
    print(f"✅ 成功执行 {len(results)} 个工具")
    for result in results:
        print(f"\n工具: {result['name']}")
        print(f"  ID: {result['tool_call_id']}")
        print(f"  结果: {result['content'][:100]}...")


async def test_tool_info():
    """测试查询工具信息"""
    print("\n" + "=" * 60)
    print("测试 4: 查询工具信息")
    print("=" * 60)
    
    from tools import get_tools_interface
    
    interface = get_tools_interface()
    
    # 查询所有工具
    info = interface.get_tool_info()
    print(f"\n✅ 共有 {info['total']} 个工具")
    
    # 按类别统计
    categories = {}
    for tool in info['tools']:
        name = tool['name']
        if 'child' in name or 'session' in name:
            category = "数据库"
        elif 'memor' in name or 'context' in name or 'trend' in name:
            category = "记忆"
        elif 'video' in name:
            category = "视频"
        elif 'search' in name or 'game' in name:
            category = "知识库"
        else:
            category = "其他"
        
        categories[category] = categories.get(category, 0) + 1
    
    print("\n工具分类统计:")
    for category, count in categories.items():
        print(f"  {category}: {count} 个")
    
    # 查询特定工具
    print("\n查询特定工具: get_child_profile")
    tool_info = interface.get_tool_info("get_child_profile")
    print(f"  名称: {tool_info['name']}")
    print(f"  描述: {tool_info['description']}")
    print(f"  参数: {list(tool_info['parameters']['properties'].keys())}")


async def test_error_handling():
    """测试错误处理"""
    print("\n" + "=" * 60)
    print("测试 5: 错误处理")
    print("=" * 60)
    
    from tools import execute_function_call
    
    # 测试不存在的工具
    print("\n测试: 调用不存在的工具")
    result = await execute_function_call(
        function_name="non_existent_tool",
        function_arguments='{"param": "value"}'
    )
    
    if not result['success']:
        print(f"✅ 正确捕获错误: {result['error']}")
    else:
        print("❌ 应该返回错误")
    
    # 测试错误的 JSON
    print("\n测试: 错误的 JSON 格式")
    result = await execute_function_call(
        function_name="get_child_profile",
        function_arguments='invalid json'
    )
    
    if not result['success']:
        print(f"✅ 正确捕获错误: {result['error']}")
    else:
        print("❌ 应该返回错误")


async def main():
    """运行所有测试"""
    print("\n🧪 Tools 接口测试\n")
    
    # 初始化服务容器
    from src.container import init_services
    init_services()
    
    # 运行测试
    await test_get_tools()
    await test_execute_single_tool()
    await test_execute_multiple_tools()
    await test_tool_info()
    await test_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
