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
        if self.config.use_mock:
            return self._generate_mock_response(request)
            
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
        
        try:
            completion = self.client.chat.completions.create(**kwargs)
            
            if self.config.stream:
                return self._process_stream_response(completion, request.enable_thinking)
            else:
                return self._process_response(completion)
        except Exception as e:
            if "401" in str(e) or "invalid_api_key" in str(e).lower():
                logger.warning(f"Aliyun API Key invalid, falling back to Mock: {e}")
                return self._generate_mock_response(request)
            raise e

    def _generate_mock_response(self, request: ParseRequest) -> ParseResponse:
        """生成模拟解析结果"""
        # 预设一个典型的医学报告 Mock 结果
        mock_answer = """
【提取的文字】
姓名：王小明 性别：男 年龄：3岁6个月
检查日期：2026-01-15
临床表现：言语发育迟缓，社交意向弱，存在刻板行为（转圈、对齐玩具）。
评估工具：CARS评分为34分，ABC量表总分72分。
诊断建议：疑似孤独症谱系障碍（ASD），建议进行针对性康复训练。

【孩子画像】
小明是一个3岁半的小男孩，目前处于ASD疑似诊断状态。他表现出明显的社交沟通障碍和兴趣狭隘。他喜欢把玩具车排成整齐的一排，对叫他名字反应较慢。目前言语表达以单音节为主。建议重点关注共同注意（Shared Attention）的培养，并在日常游戏中加入更多的轮流互动，以帮助他建立更稳定的社交联结。
"""
        return ParseResponse(
            answer=mock_answer,
            reasoning="[Mock Reasoning] 由于 API Key 失效或未配置，系统自动生成了演示数据。在真实环境中，解析器将通过视觉模型提取报告内容。",
            usage=None
        )
    
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
