"""
聊天服务 - 集成 LLM 和 Tools 的智能助手
"""
from typing import Dict, Any, List, Optional, AsyncGenerator
import json

from .chat_tools import ChatTools, TOOL_DEFINITIONS
from services.LLM_Service.service import get_llm_service


class ChatService:
    """聊天服务"""
    
    def __init__(self, chat_tools: ChatTools):
        self.chat_tools = chat_tools
        self.llm_service = get_llm_service()
        
        # Tool 名称到方法的映射
        self.tool_methods = {
            "record_behavior": self.chat_tools.record_behavior,
            "recommend_game": self.chat_tools.recommend_game,
            "get_child_profile": self.chat_tools.get_child_profile,
            "query_behaviors": self.chat_tools.query_behaviors,
            "query_interests": self.chat_tools.query_interests,
            "query_dimension_progress": self.chat_tools.query_dimension_progress,
            "get_latest_assessment": self.chat_tools.get_latest_assessment,
            "get_recent_games": self.chat_tools.get_recent_games,
            "generate_assessment": self.chat_tools.generate_assessment
        }
    
    async def chat(
        self,
        message: str,
        child_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        处理聊天消息
        
        Args:
            message: 用户消息
            child_id: 当前孩子ID
            conversation_history: 对话历史 [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            {
                "response": "助手回复",
                "tool_calls": [...],  # 调用的工具列表
                "conversation_history": [...]  # 更新后的对话历史
            }
        """
        print(f"[ChatService] 收到消息: {message[:50]}...")
        
        # 初始化对话历史
        if conversation_history is None:
            conversation_history = []
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(child_id)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        # 第一次调用 LLM（可能返回 tool calls）
        response = await self.llm_service.call_with_tools(
            messages=messages,
            tools=TOOL_DEFINITIONS,
            temperature=0.7,
            max_tokens=2000
        )
        
        assistant_message = response.get("message", {})
        tool_calls = response.get("tool_calls", [])
        
        # 如果有 tool calls，执行它们
        tool_results = []
        if tool_calls:
            print(f"[ChatService] 执行 {len(tool_calls)} 个工具调用")
            
            for tool_call in tool_calls:
                tool_name = tool_call.get("name")
                tool_args = tool_call.get("arguments", {})
                
                print(f"[ChatService] 调用工具: {tool_name}")
                print(f"[ChatService] 参数: {tool_args}")
                
                # 执行工具
                result = await self._execute_tool(tool_name, tool_args, child_id)
                tool_results.append({
                    "tool_name": tool_name,
                    "result": result
                })
            
            # 将工具结果添加到消息中，再次调用 LLM 生成最终回复
            # 注意：tool_calls 需要转换为 OpenAI 格式
            openai_tool_calls = []
            for tc in tool_calls:
                openai_tool_calls.append({
                    "id": tc.get("id"),
                    "type": "function",
                    "function": {
                        "name": tc.get("name"),
                        "arguments": json.dumps(tc.get("arguments", {}), ensure_ascii=False)
                    }
                })
            
            messages.append({
                "role": "assistant",
                "content": assistant_message.get("content", ""),
                "tool_calls": openai_tool_calls
            })
            
            # 添加工具结果
            for i, tool_call in enumerate(tool_calls):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.get("id", f"call_{i}"),
                    "name": tool_call.get("name"),
                    "content": json.dumps(tool_results[i]["result"], ensure_ascii=False)
                })
            
            # 第二次调用 LLM，生成基于工具结果的回复
            final_response = await self.llm_service.call_with_tools(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.7,
                max_tokens=2000
            )
            
            final_message = final_response.get("message", {})
            response_text = final_message.get("content", "")
        else:
            # 没有工具调用，直接返回回复
            response_text = assistant_message.get("content", "")
        
        # 更新对话历史
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # 限制对话历史长度（保留最近10轮）
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        return {
            "response": response_text,
            "tool_calls": tool_results,
            "conversation_history": conversation_history
        }
    
    def _build_system_prompt(self, child_id: str) -> str:
        """构建系统提示词"""
        return f"""你是一个专业的 ASD 儿童家庭干预助手，帮助家长记录孩子的行为、推荐游戏、查询评估结果。

**当前孩子ID**: {child_id}

**核心规则 - 必须遵守**：

1. 【自动记录】当家长描述孩子的任何行为、兴趣、表现时，你必须立即调用 record_behavior 工具
   - 触发词：喜欢、讨厌、做了、表现、感兴趣、玩了、说了、看了、听了等
   - 示例："孩子喜欢XX" → 立即调用 record_behavior
   - 不要询问"要不要记录"，直接记录

2. 【数据查询】当家长询问孩子的情况时，主动调用相应的查询工具：
   - "孩子之前做了什么" → query_behaviors
   - "孩子喜欢什么" → query_interests
   - "孩子进步如何" → query_dimension_progress
   - "最近玩了什么游戏" → get_recent_games
   - "上次评估结果" → get_latest_assessment

3. 【游戏推荐】当家长询问"玩什么"、"推荐游戏"时，调用 recommend_game

4. 【评估生成】当家长要求"评估孩子"、"做个评估"时，调用 generate_assessment（不是 get_latest_assessment）

**工具调用后的回复**：
- 记录行为后：简短确认，如"已记录✓"
- 查询数据后：用自然语言总结关键信息，不要直接复述 JSON
- 推荐游戏后：简要介绍游戏亮点
- 评估完成后：总结关键发现，给予鼓励

**交流风格**：
- 温暖、友好、专业
- 简洁明了，不啰嗦
- 关注进步，给予鼓励
- 主动使用工具获取数据，而不是说"我不知道"

**重要**：
- 识别到行为描述时，必须立即调用 record_behavior
- 遇到问题时，主动调用查询工具获取数据
- 基于数据回答问题，而不是猜测
"""
    
    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        child_id: str
    ) -> Dict[str, Any]:
        """执行工具调用"""
        try:
            # 确保 child_id 存在
            if "child_id" not in tool_args:
                tool_args["child_id"] = child_id
            
            # 直接调用工具方法
            tool_method = self.tool_methods.get(tool_name)
            
            if not tool_method:
                return {
                    "success": False,
                    "error": f"未知的工具: {tool_name}"
                }
            
            # 导入参数类
            from .chat_tools import (
                RecordBehaviorParams,
                RecommendGameParams,
                GetChildProfileParams,
                QueryBehaviorsParams,
                QueryInterestsParams,
                QueryDimensionProgressParams,
                GetLatestAssessmentParams,
                GetRecentGamesParams,
                GenerateAssessmentParams
            )
            
            # 参数类映射
            param_classes = {
                "record_behavior": RecordBehaviorParams,
                "recommend_game": RecommendGameParams,
                "get_child_profile": GetChildProfileParams,
                "query_behaviors": QueryBehaviorsParams,
                "query_interests": QueryInterestsParams,
                "query_dimension_progress": QueryDimensionProgressParams,
                "get_latest_assessment": GetLatestAssessmentParams,
                "get_recent_games": GetRecentGamesParams,
                "generate_assessment": GenerateAssessmentParams
            }
            
            param_class = param_classes.get(tool_name)
            if not param_class:
                return {
                    "success": False,
                    "error": f"未知的工具: {tool_name}"
                }
            
            # 验证参数
            params = param_class(**tool_args)
            
            # 执行工具
            result = await tool_method(params)
            
            return result
        
        except Exception as e:
            print(f"[ChatService] 工具执行失败: {tool_name}, 错误: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "error": str(e)
            }
    
    async def chat_stream(
        self,
        message: str,
        child_id: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        流式处理聊天消息
        
        生成事件：
        - {"type": "tool_call", "data": {"tool_name": "...", "arguments": {...}}}
        - {"type": "tool_result", "data": {"tool_name": "...", "result": {...}}}
        - {"type": "content", "data": {"text": "..."}}
        - {"type": "done", "data": {"conversation_history": [...]}}
        
        Args:
            message: 用户消息
            child_id: 当前孩子ID
            conversation_history: 对话历史
        
        Yields:
            事件字典
        """
        print(f"[ChatService Stream] 收到消息: {message[:50]}...")
        
        # 初始化对话历史
        if conversation_history is None:
            conversation_history = []
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(child_id)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": message})
        
        # 第一次调用 LLM（流式，检测是否有 tool calls）
        tool_calls_data = []
        content_chunks = []
        has_tool_calls = False
        
        async for chunk in self.llm_service.call_with_tools_stream(
            messages=messages,
            tools=TOOL_DEFINITIONS,
            temperature=0.7,
            max_tokens=2000
        ):
            delta = chunk.choices[0].delta if chunk.choices else None
            if not delta:
                continue
            
            # 收集内容
            if delta.content:
                content_chunks.append(delta.content)
            
            # 收集工具调用
            if delta.tool_calls:
                has_tool_calls = True
                for tc in delta.tool_calls:
                    # 确保有足够的空间
                    while len(tool_calls_data) <= tc.index:
                        tool_calls_data.append({
                            "id": None,
                            "name": None,
                            "arguments": ""
                        })
                    
                    if tc.id:
                        tool_calls_data[tc.index]["id"] = tc.id
                    if tc.function and tc.function.name:
                        tool_calls_data[tc.index]["name"] = tc.function.name
                    if tc.function and tc.function.arguments:
                        tool_calls_data[tc.index]["arguments"] += tc.function.arguments
        
        # 打印第一次 LLM 调用的结果
        print(f"\n[ChatService] 📋 第一次 LLM 调用结果:")
        print(f"  has_tool_calls: {has_tool_calls}")
        print(f"  tool_calls_data: {json.dumps(tool_calls_data, ensure_ascii=False, indent=2)}")
        print(f"  content_chunks: {content_chunks[:3] if len(content_chunks) > 3 else content_chunks}...")  # 只显示前3个
        
        # 处理工具调用
        tool_results = []
        if has_tool_calls and tool_calls_data:
            print(f"\n[ChatService] 🔧 执行 {len(tool_calls_data)} 个工具")
            
            for tool_call in tool_calls_data:
                tool_name = tool_call["name"]
                try:
                    tool_args = json.loads(tool_call["arguments"])
                except json.JSONDecodeError:
                    tool_args = {}
                
                # 发送工具调用事件
                yield {
                    "type": "tool_call",
                    "data": {
                        "tool_name": tool_name,
                        "tool_display_name": self._get_tool_display_name(tool_name),
                        "arguments": tool_args
                    }
                }
                
                # 执行工具
                result = await self._execute_tool(tool_name, tool_args, child_id)
                tool_results.append({
                    "tool_name": tool_name,
                    "result": result
                })
                
                # 打印完整的工具调用结果
                print(f"\n[ChatService] 📋 工具调用结果:")
                print(f"  工具: {tool_name}")
                print(f"  参数: {json.dumps(tool_args, ensure_ascii=False, indent=2)}")
                print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 发送工具结果事件
                yield {
                    "type": "tool_result",
                    "data": {
                        "tool_name": tool_name,
                        "tool_display_name": self._get_tool_display_name(tool_name),
                        "success": result.get("success", False),
                        "message": result.get("message", "") if result.get("success") else result.get("error", "")
                    }
                }
            
            # 将工具结果添加到消息中，再次调用 LLM 生成最终回复
            openai_tool_calls = []
            for i, tc in enumerate(tool_calls_data):
                openai_tool_calls.append({
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": tc["arguments"]
                    }
                })
            
            messages.append({
                "role": "assistant",
                "content": "".join(content_chunks) if content_chunks else "",
                "tool_calls": openai_tool_calls
            })
            
            # 添加工具结果
            for i, tool_call in enumerate(tool_calls_data):
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_call["name"],
                    "content": json.dumps(tool_results[i]["result"], ensure_ascii=False)
                })
            
            # 第二次流式调用 LLM，生成基于工具结果的回复
            response_text = ""
            async for chunk in self.llm_service.call_with_tools_stream(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.7,
                max_tokens=2000
            ):
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    response_text += delta.content
                    # 实时发送内容
                    yield {
                        "type": "content",
                        "data": {"text": delta.content}
                    }
        else:
            # 没有工具调用，需要重新流式调用以实时返回内容
            # 因为第一次调用只是收集了 chunks，没有实时发送
            print(f"\n[ChatService] ℹ️  没有工具调用，重新流式调用 LLM")
            response_text = ""
            async for chunk in self.llm_service.call_with_tools_stream(
                messages=messages,
                tools=TOOL_DEFINITIONS,
                temperature=0.7,
                max_tokens=2000
            ):
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    response_text += delta.content
                    # 实时发送内容
                    yield {
                        "type": "content",
                        "data": {"text": delta.content}
                    }
        
        # 更新对话历史
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # 限制对话历史长度（保留最近10轮）
        if len(conversation_history) > 20:
            conversation_history = conversation_history[-20:]
        
        # 发送完成事件
        yield {
            "type": "done",
            "data": {
                "conversation_history": conversation_history,
                "tool_calls": tool_results
            }
        }
    
    def _get_tool_display_name(self, tool_name: str) -> str:
        """获取工具显示名称"""
        names = {
            'record_behavior': '记录行为',
            'recommend_game': '推荐游戏',
            'get_child_profile': '查询档案',
            'query_behaviors': '查询行为记录',
            'query_interests': '查询兴趣点',
            'query_dimension_progress': '查询维度进展',
            'get_latest_assessment': '查询评估',
            'get_recent_games': '查询游戏历史',
            'generate_assessment': '生成评估报告'
        }
        return names.get(tool_name, tool_name)
