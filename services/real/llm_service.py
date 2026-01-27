"""
LLM 服务 - 支持多个供应商（DeepSeek, OpenAI, Gemini 等）
"""
import os
from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod


# ============ LLM 接口定义 ============

class ILLMService(Protocol):
    """LLM 服务接口"""
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """基础对话接口"""
        pass
    
    @abstractmethod
    async def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带系统提示词的对话"""
        pass
    
    @abstractmethod
    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """生成 JSON 格式回复"""
        pass


# ============ DeepSeek 实现 ============

class DeepSeekLLMService(ILLMService):
    """DeepSeek LLM 服务"""
    
    def __init__(self, api_key: str = None, base_url: str = None):
        """初始化 DeepSeek 客户端"""
        from openai import AsyncOpenAI
        
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = base_url or os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未配置")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.model = "deepseek-chat"
        self.provider = "deepseek"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """调用 DeepSeek Chat API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[DeepSeek] API 调用失败: {e}")
            raise
    
    async def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带系统提示词的对话"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return await self.chat(messages, temperature, max_tokens)
    
    async def chat_with_history(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带历史记录的对话"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat(messages, temperature, max_tokens)
    
    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """生成 JSON 格式的回复"""
        import json
        
        response = await self.chat_with_system(
            system_prompt=system_prompt + "\n\n请以 JSON 格式返回结果。",
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        import json
        
        try:
            # 如果回复包含 ```json 代码块
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"[{self.provider}] JSON 解析失败: {e}")
            print(f"原始回复: {response}")
            return {"raw_response": response, "parse_error": str(e)}


# ============ OpenAI 实现 ============

class OpenAILLMService(ILLMService):
    """OpenAI LLM 服务"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """初始化 OpenAI 客户端"""
        from openai import AsyncOpenAI
        
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY 未配置")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model or os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.provider = "openai"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """调用 OpenAI Chat API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[OpenAI] API 调用失败: {e}")
            raise
    
    async def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带系统提示词的对话"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return await self.chat(messages, temperature, max_tokens)
    
    async def chat_with_history(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带历史记录的对话"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat(messages, temperature, max_tokens)
    
    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """生成 JSON 格式的回复"""
        import json
        
        response = await self.chat_with_system(
            system_prompt=system_prompt + "\n\nPlease return the result in JSON format.",
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        import json
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"[{self.provider}] JSON 解析失败: {e}")
            print(f"原始回复: {response}")
            return {"raw_response": response, "parse_error": str(e)}


# ============ Qwen 实现 ============

class QwenLLMService(ILLMService):
    """通义千问 LLM 服务"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """初始化 Qwen 客户端"""
        from openai import AsyncOpenAI
        
        self.api_key = api_key or os.getenv('QWEN_API_KEY') or os.getenv('DASHSCOPE_API_KEY')
        self.base_url = base_url or os.getenv('QWEN_BASE_URL', 'https://dashscope.aliyuncs.com') + '/compatible-mode/v1'
        self.model = model or os.getenv('QWEN_MODEL', 'qwen-plus')
        
        if not self.api_key:
            raise ValueError("QWEN_API_KEY 或 DASHSCOPE_API_KEY 未配置")
        
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        self.provider = "qwen"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """调用 Qwen Chat API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"[Qwen] API 调用失败: {e}")
            raise
    
    async def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带系统提示词的对话"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return await self.chat(messages, temperature, max_tokens)
    
    async def chat_with_history(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带历史记录的对话"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat(messages, temperature, max_tokens)
    
    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """生成 JSON 格式的回复"""
        import json
        
        response = await self.chat_with_system(
            system_prompt=system_prompt + "\n\n请以 JSON 格式返回结果。",
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        import json
        
        try:
            # 如果回复包含 ```json 代码块
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"[{self.provider}] JSON 解析失败: {e}")
            print(f"原始回复: {response}")
            return {"raw_response": response, "parse_error": str(e)}


# ============ Gemini 实现 ============

class GeminiLLMService(ILLMService):
    """Google Gemini LLM 服务"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """初始化 Gemini 客户端"""
        import google.generativeai as genai
        
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY 未配置")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model or os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        self.model = genai.GenerativeModel(self.model_name)
        self.provider = "gemini"
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """调用 Gemini Chat API"""
        try:
            # 转换消息格式
            gemini_messages = self._convert_messages(messages)
            
            # 配置生成参数
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            # 调用 API
            response = await self.model.generate_content_async(
                gemini_messages,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            print(f"[Gemini] API 调用失败: {e}")
            raise
    
    def _convert_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """转换消息格式为 Gemini 格式"""
        gemini_messages = []
        system_prompt = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                system_prompt = content
            elif role == "user":
                if system_prompt:
                    # 将系统提示词合并到第一条用户消息
                    content = f"{system_prompt}\n\n{content}"
                    system_prompt = None
                gemini_messages.append({"role": "user", "parts": [content]})
            elif role == "assistant":
                gemini_messages.append({"role": "model", "parts": [content]})
        
        return gemini_messages
    
    async def chat_with_system(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带系统提示词的对话"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return await self.chat(messages, temperature, max_tokens)
    
    async def chat_with_history(
        self,
        system_prompt: str,
        conversation_history: List[Dict[str, str]],
        user_message: str,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """带历史记录的对话"""
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        return await self.chat(messages, temperature, max_tokens)
    
    async def generate_json(
        self,
        system_prompt: str,
        user_message: str,
        temperature: float = 0.3,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """生成 JSON 格式的回复"""
        import json
        
        response = await self.chat_with_system(
            system_prompt=system_prompt + "\n\nPlease return the result in JSON format.",
            user_message=user_message,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return self._parse_json_response(response)
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        import json
        
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()
            
            return json.loads(json_str)
        except Exception as e:
            print(f"[{self.provider}] JSON 解析失败: {e}")
            print(f"原始回复: {response}")
            return {"raw_response": response, "parse_error": str(e)}


# ============ LLM 工厂 ============

class LLMFactory:
    """LLM 服务工厂"""
    
    _providers = {
        "deepseek": DeepSeekLLMService,
        "openai": OpenAILLMService,
        "gemini": GeminiLLMService,
        "qwen": QwenLLMService,
    }
    
    @classmethod
    def create(cls, provider: str = None, **kwargs) -> ILLMService:
        """
        创建 LLM 服务实例
        
        Args:
            provider: 供应商名称 (deepseek, openai, gemini)
            **kwargs: 传递给具体实现的参数
            
        Returns:
            ILLMService: LLM 服务实例
        """
        provider = provider or os.getenv('AI_PROVIDER', 'deepseek').lower()
        
        if provider not in cls._providers:
            raise ValueError(f"不支持的 LLM 供应商: {provider}. 支持的供应商: {list(cls._providers.keys())}")
        
        service_class = cls._providers[provider]
        
        try:
            service = service_class(**kwargs)
            print(f"[LLM Factory] 成功创建 {provider} 服务")
            return service
        except Exception as e:
            print(f"[LLM Factory] 创建 {provider} 服务失败: {e}")
            raise
    
    @classmethod
    def register_provider(cls, name: str, service_class: type):
        """注册新的 LLM 供应商"""
        cls._providers[name] = service_class
        print(f"[LLM Factory] 注册新供应商: {name}")


# ============ 全局实例管理 ============

_llm_service: Optional[ILLMService] = None


def get_llm_service(provider: str = None, **kwargs) -> ILLMService:
    """
    获取全局 LLM 服务实例（单例模式）
    
    Args:
        provider: 供应商名称，如果为 None 则使用环境变量 AI_PROVIDER
        **kwargs: 传递给具体实现的参数
        
    Returns:
        ILLMService: LLM 服务实例
    """
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMFactory.create(provider, **kwargs)
    return _llm_service


def reset_llm_service():
    """重置全局 LLM 服务实例（用于切换供应商）"""
    global _llm_service
    _llm_service = None


__all__ = [
    'ILLMService',
    'DeepSeekLLMService',
    'OpenAILLMService', 
    'GeminiLLMService',
    'QwenLLMService',
    'LLMFactory',
    'get_llm_service',
    'reset_llm_service'
]
