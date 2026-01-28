"""多模态解析器核心模块"""
from openai import OpenAI
from typing import Optional, Generator
import logging

try:
    from .config import MultimodalConfig
    from .models import ParseRequest, ParseResponse
except ImportError:
    from config import MultimodalConfig
    from models import ParseRequest, ParseResponse

logger = logging.getLogger(__name__)


class MultimodalParser:
    """多模态解析器"""
    
    def __init__(self, config: Optional[MultimodalConfig] = None):
        """初始化解析器"""
        self.config = config or MultimodalConfig.from_env()
        self.client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    def parse(self, request: ParseRequest) -> ParseResponse:
        """解析多模态内容"""
        message_content = [content.to_openai_format() for content in request.contents]
        
        kwargs = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": message_content}],
            "stream": self.config.stream,
        }
        
        if request.enable_thinking or self.config.enable_thinking:
            kwargs["extra_body"] = {
                'enable_thinking': True,
                "thinking_budget": self.config.thinking_budget
            }
        
        completion = self.client.chat.completions.create(**kwargs)
        
        if self.config.stream:
            return self._process_stream_response(completion, request.enable_thinking)
        else:
            return self._process_response(completion)
    
    def parse_stream(self, request: ParseRequest) -> Generator[tuple[Optional[str], Optional[str]], None, None]:
        """流式解析多模态内容"""
        message_content = [content.to_openai_format() for content in request.contents]
        
        kwargs = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": message_content}],
            "stream": True,
        }
        
        if request.enable_thinking or self.config.enable_thinking:
            kwargs["extra_body"] = {
                'enable_thinking': True,
                "thinking_budget": self.config.thinking_budget
            }
        
        completion = self.client.chat.completions.create(**kwargs)
        
        for chunk in completion:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            reasoning_chunk = None
            answer_chunk = None
            
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                reasoning_chunk = delta.reasoning_content
            
            if delta.content:
                answer_chunk = delta.content
            
            yield reasoning_chunk, answer_chunk
    
    def _process_stream_response(self, completion, enable_thinking: bool) -> ParseResponse:
        """处理流式响应"""
        reasoning_content = ""
        answer_content = ""
        usage = None
        
        for chunk in completion:
            if not chunk.choices:
                if hasattr(chunk, 'usage'):
                    usage = chunk.usage
                continue
            
            delta = chunk.choices[0].delta
            
            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                reasoning_content += delta.reasoning_content
            
            if delta.content:
                answer_content += delta.content
        
        return ParseResponse(
            answer=answer_content,
            reasoning=reasoning_content if enable_thinking else None,
            usage=usage
        )
    
    def _process_response(self, completion) -> ParseResponse:
        """处理非流式响应"""
        choice = completion.choices[0]
        message = choice.message
        
        reasoning = None
        if hasattr(message, 'reasoning_content'):
            reasoning = message.reasoning_content
        
        return ParseResponse(
            answer=message.content,
            reasoning=reasoning,
            usage=completion.usage if hasattr(completion, 'usage') else None
        )
