# LLM Function Call 工具集

为 LLM 提供可调用的工具函数，支持 OpenAI Function Calling 标准。

## 快速开始

### 最简单的使用方式（推荐）

```python
from tools import get_tools_for_llm, execute_tool_calls_from_message
from openai import AsyncOpenAI

client = AsyncOpenAI()

# 1. 获取工具列表
tools = get_tools_for_llm()

# 2. 调用 LLM
response = await client.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "查询孩子 test-001 的档案"}],
    tools=tools
)

message = response.choices[0].message

# 3. 执行工具调用
if message.tool_calls:
    results = await execute_tool_calls_from_message(message)
    # results 可以直接添加到 messages 中返回给 LLM
```

## 对外接口 API

### 1. `get_tools_for_llm()` - 获取工具列表

```python
from tools import get_tools_for_llm

tools = get_tools_for_llm()
# 返回工具 schema 列表，可直接传给 LLM
```

### 2. `execute_tool_calls_from_message()` - 执行工具调用

```python
from tools import execute_tool_calls_from_message

# 从 LLM 消息对象中提取并执行工具
results = await execute_tool_calls_from_message(message)
```

### 3. `execute_tool_calls()` - 批量执行工具

```python
from tools import execute_tool_calls

# 手动传入 tool_calls 列表
results = await execute_tool_calls(tool_calls)
```

### 4. `execute_function_call()` - 执行单个工具

```python
from tools import execute_function_call

result = await execute_function_call(
    function_name="get_child_profile",
    function_arguments='{"child_id": "test-001"}'
)
```

### 5. `get_tools_interface()` - 获取接口实例

```python
from tools import get_tools_interface

interface = get_tools_interface()

# 查询工具信息
info = interface.get_tool_info()
print(f"共有 {info['total']} 个工具")

# 查询特定工具
tool_info = interface.get_tool_info("get_child_profile")
```

## 工具分类

### 1. SQLite 数据库工具 (`sqlite_tools.py`)
- `get_child_profile` - 获取孩子档案
- `save_child_profile` - 保存孩子档案
- `create_session` - 创建干预会话
- `update_session` - 更新会话信息
- `get_session_history` - 获取会话历史
- `delete_child` - 删除孩子档案

### 2. Graphiti 记忆网络工具 (`graphiti_tools.py`)
- `save_memories` - 保存观察记忆
- `get_recent_memories` - 获取最近记忆
- `build_context` - 构建当前上下文
- `analyze_trends` - 分析发展趋势
- `detect_milestones` - 检测里程碑
- `clear_memories` - 清空记忆

### 3. 视频分析工具 (`video_tools.py`)
- `analyze_video` - 分析干预视频

### 4. RAG 知识库工具 (`rag_tools.py`)
- `search_methodology` - 检索方法论
- `search_games` - 检索游戏
- `search_games_by_dimension` - 按维度检索游戏
- `search_games_by_interest` - 按兴趣检索游戏
- `get_game_details` - 获取游戏详情
- `search_scale` - 检索量表
- `search_cases` - 检索案例

## 使用方法

### 方式 1：直接使用工具执行器

```python
from tools import get_tool_executor

# 获取工具执行器
executor = get_tool_executor()

# 获取所有工具的 schema（用于 LLM）
schemas = executor.get_tool_schemas()

# 执行单个工具
result = await executor.execute_tool(
    tool_name="get_child_profile",
    arguments={"child_id": "test-001"}
)

# 批量执行工具调用（处理 LLM 返回的 tool_calls）
tool_calls = [
    {
        "id": "call_xxx",
        "type": "function",
        "function": {
            "name": "get_child_profile",
            "arguments": '{"child_id": "test-001"}'
        }
    }
]
results = await executor.execute_tool_calls(tool_calls)
```

### 方式 2：与 LLM 集成

```python
from openai import AsyncOpenAI
from tools import get_tool_executor

client = AsyncOpenAI()
executor = get_tool_executor()

# 1. 发送消息给 LLM，提供工具
response = await client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "获取孩子 test-001 的档案信息"}
    ],
    tools=executor.get_tool_schemas(),
    tool_choice="auto"
)

# 2. 检查是否需要调用工具
message = response.choices[0].message
if message.tool_calls:
    # 3. 执行工具调用
    tool_results = await executor.execute_tool_calls(message.tool_calls)
    
    # 4. 将工具结果返回给 LLM
    messages = [
        {"role": "user", "content": "获取孩子 test-001 的档案信息"},
        message,  # LLM 的响应（包含 tool_calls）
        *tool_results  # 工具执行结果
    ]
    
    final_response = await client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )
    
    print(final_response.choices[0].message.content)
```

### 方式 3：单独使用某个工具模块

```python
from tools.sqlite_tools import SQLITE_TOOLS, SQLITE_EXECUTORS

# 获取 SQLite 工具的 schema
schemas = list(SQLITE_TOOLS.values())

# 执行工具
result = await SQLITE_EXECUTORS['get_child_profile'](child_id="test-001")
```

## 工具 Schema 格式

所有工具遵循 OpenAI Function Calling 标准：

```python
{
    "type": "function",
    "function": {
        "name": "tool_name",
        "description": "工具描述",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "参数描述"
                }
            },
            "required": ["param1"]
        }
    }
}
```

## 添加新工具

1. 在对应的工具文件中添加工具定义（schema）
2. 实现工具执行器函数
3. 注册到 `EXECUTORS` 字典
4. 更新 `get_xxx_tools()` 函数

示例：

```python
# 1. 添加工具定义
NEW_TOOL = {
    "type": "function",
    "function": {
        "name": "my_new_tool",
        "description": "我的新工具",
        "parameters": {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        }
    }
}

# 2. 实现执行器
async def execute_my_new_tool(param1: str) -> Dict[str, Any]:
    service = container.get('some_service')
    return await service.some_method(param1)

# 3. 注册
EXECUTORS = {
    "my_new_tool": execute_my_new_tool,
}
```

## 注意事项

1. **所有工具执行器都是异步函数**（使用 `async def`）
2. **工具名称必须唯一**，不能重复
3. **参数类型必须与 schema 定义一致**
4. **工具执行器应该调用现有服务**，不要重复实现功能
5. **错误处理**：工具执行器应该抛出异常，由 `ToolExecutor` 统一处理

## 测试

```python
import asyncio
from tools import get_tool_executor

async def test_tools():
    executor = get_tool_executor()
    
    # 测试获取孩子档案
    result = await executor.execute_tool(
        "get_child_profile",
        {"child_id": "test-001"}
    )
    print(result)
    
    # 测试保存记忆
    result = await executor.execute_tool(
        "save_memories",
        {
            "child_id": "test-001",
            "memories": [{
                "timestamp": "2026-01-28T15:00:00",
                "type": "observation",
                "content": "孩子主动眼神接触5次"
            }]
        }
    )
    print(result)

if __name__ == "__main__":
    asyncio.run(test_tools())
```
