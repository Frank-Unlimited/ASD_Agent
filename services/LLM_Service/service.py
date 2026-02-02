"""
LLM 服务 - 统一接口
支持 System Prompt、Tool Calling、Output Schema
"""
import json
from typing import Dict, Any, List, Optional, Union
from openai import AsyncOpenAI
from src.config import settings
from .tool import Tool, ToolRegistry


class LLMService:
    """LLM 统一服务"""
    
    def __init__(self):
        """从配置初始化 LLM 客户端"""
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url
        self.model = settings.llm_model
        
        if not self.api_key:
            raise ValueError("LLM_API_KEY 未配置")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        print(f"[LLM Service] 初始化成功")
        print(f"  - Model: {self.model}")
        print(f"  - Base URL: {self.base_url}")
    
    async def call(
        self,
        system_prompt: str,
        user_message: str,
        tools: Optional[Union[List[Tool], List[Dict[str, Any]]]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        统一的 LLM 调用接口
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            tools: 工具列表（Tool 对象或 OpenAI 格式字典）
            output_schema: 输出格式定义（JSON Schema）
            conversation_history: 对话历史
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数
            
        Returns:
            {
                "content": str,              # 文本回复
                "tool_calls": List[Dict],    # 工具调用（如果有）
                "finish_reason": str,        # 结束原因
                "usage": Dict                # token 使用情况
            }
        """
        # 构建消息
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加对话历史
        if conversation_history:
            messages.extend(conversation_history)
        
        # 添加用户消息
        messages.append({"role": "user", "content": user_message})
        
        # 构建请求参数
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # 添加工具定义
        if tools:
            # 转换 Tool 对象为 OpenAI 格式
            if tools and isinstance(tools[0], Tool):
                request_params["tools"] = [t.to_openai_format() for t in tools]
            else:
                request_params["tools"] = tools
            request_params["tool_choice"] = "auto"
        
        # 添加输出格式
        if output_schema:
            # DeepSeek 目前主要支持 json_object，未必支持 json_schema
            if "deepseek" in self.model.lower():
                request_params["response_format"] = {"type": "json_object"}
                # DeepSeek 要求 JSON 模式下 Prompt 必须包含 "json" 字样
                if "json" not in system_prompt.lower() and "json" not in user_message.lower():
                    messages[0]["content"] += "\nReturn your response in valid JSON format."
            else:
                request_params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": output_schema
                }
        
        try:
            # 调用 API
            response = await self.client.chat.completions.create(**request_params)
            
            # 解析响应
            message = response.choices[0].message
            
            result = {
                "content": message.content,
                "tool_calls": None,
                "finish_reason": response.choices[0].finish_reason,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # 处理工具调用
            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments)
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            # 处理结构化输出
            if output_schema and message.content:
                content = message.content.strip()
                # 尝试剥离 Markdown 代码块
                if content.startswith("```json"):
                    content = content.split("```json", 1)[1].split("```", 1)[0].strip()
                elif content.startswith("```"):
                    content = content.split("```", 1)[1].split("```", 1)[0].strip()
                
                try:
                    result["structured_output"] = json.loads(content)
                except json.JSONDecodeError as je:
                    print(f"[LLM Service] JSON 解析失败: {je}")
                    print(f"原始内容: {message.content[:500]}...")
                    result["structured_output"] = None
            
            return result
            
        except Exception as e:
            print(f"[LLM Service] 调用失败: {e}")
            raise
    
    async def call_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        简化的工具调用接口（直接传入消息列表）
        
        Args:
            messages: 消息列表 [{"role": "system/user/assistant", "content": "..."}]
            tools: 工具定义列表（OpenAI 格式）
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Returns:
            {
                "message": {
                    "role": "assistant",
                    "content": "...",
                    "tool_calls": [...]  # 如果有
                },
                "tool_calls": [...]  # 简化格式
            }
        """
        # 构建请求参数
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        # 添加工具定义
        if tools:
            # 转换为 OpenAI 格式
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                })
            request_params["tools"] = openai_tools
            request_params["tool_choice"] = "auto"
        
        try:
            # 调用 API
            response = await self.client.chat.completions.create(**request_params)
            
            # 解析响应
            message = response.choices[0].message
            
            result = {
                "message": {
                    "role": "assistant",
                    "content": message.content or ""
                },
                "tool_calls": []
            }
            
            # 处理工具调用
            if message.tool_calls:
                result["message"]["tool_calls"] = message.tool_calls
                
                # 简化格式
                for tc in message.tool_calls:
                    result["tool_calls"].append({
                        "id": tc.id,
                        "name": tc.function.name,
                        "arguments": json.loads(tc.function.arguments)
                    })
            
            return result
            
        except Exception as e:
            print(f"[LLM Service] 调用失败: {e}")
            raise
    
    async def call_with_tools_stream(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ):
        """
        流式工具调用接口
        
        Args:
            messages: 消息列表
            tools: 工具定义列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            
        Yields:
            流式响应 chunk
        """
        # 构建请求参数
        request_params = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,  # 启用流式
            **kwargs
        }
        
        # 添加工具定义
        if tools:
            openai_tools = []
            for tool in tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": tool["parameters"]
                    }
                })
            request_params["tools"] = openai_tools
            request_params["tool_choice"] = "auto"
        
        try:
            # 调用流式 API
            stream = await self.client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                yield chunk
                
        except Exception as e:
            print(f"[LLM Service] ❌ 流式调用失败: {e}")
            raise
    
    async def call_with_tool_execution(
        self,
        system_prompt: str,
        user_message: str,
        tools: Union[List[Tool], ToolRegistry],
        max_iterations: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        带自动工具执行的调用（多轮对话）
        
        Args:
            system_prompt: 系统提示词
            user_message: 用户消息
            tools: Tool 对象列表或 ToolRegistry
            max_iterations: 最大迭代次数
            **kwargs: 其他参数
            
        Returns:
            最终的响应结果
        """
        # 构建工具注册表
        if isinstance(tools, ToolRegistry):
            registry = tools
            tool_list = registry.get_all()
        else:
            registry = ToolRegistry()
            registry.register_batch(tools)
            tool_list = tools
        conversation_history = []
        
        for iteration in range(max_iterations):
            # 调用 LLM
            result = await self.call(
                system_prompt=system_prompt,
                user_message=user_message if iteration == 0 else "",
                tools=tool_list,
                conversation_history=conversation_history,
                **kwargs
            )
            
            # 如果没有工具调用，返回结果
            if not result["tool_calls"]:
                return result
            
            # 执行工具调用
            print(f"[LLM Service] Iteration {iteration + 1}: 执行 {len(result['tool_calls'])} 个工具")
            
            # 添加 assistant 消息到历史
            conversation_history.append({
                "role": "assistant",
                "content": result["content"] or "",
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": tc["type"],
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": json.dumps(tc["function"]["arguments"])
                        }
                    }
                    for tc in result["tool_calls"]
                ]
            })
            
            # 执行工具并添加结果到历史
            for tool_call in result["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = tool_call["function"]["arguments"]
                
                try:
                    # 执行工具
                    tool_result = await registry.execute(tool_name, tool_args)
                    
                    # 添加工具结果到历史
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps(tool_result, ensure_ascii=False)
                    })
                    
                except Exception as e:
                    # 工具执行失败
                    conversation_history.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": json.dumps({"error": str(e)}, ensure_ascii=False)
                    })
        
        # 达到最大迭代次数
        return {
            "content": "达到最大迭代次数",
            "tool_calls": None,
            "finish_reason": "max_iterations",
            "usage": {}
        }


# ============ 全局实例 ============

_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """获取全局 LLM 服务实例（单例）"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def reset_llm_service():
    """重置全局 LLM 服务实例"""
    global _llm_service
    _llm_service = None


__all__ = ['LLMService', 'get_llm_service', 'reset_llm_service']
