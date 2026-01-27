"""数据模型定义"""
from dataclasses import dataclass
from typing import Optional, List
from enum import Enum


class ContentType(Enum):
    """内容类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"


@dataclass
class MediaContent:
    """媒体内容"""
    type: ContentType
    content: str
    
    def to_openai_format(self) -> dict:
        """转换为OpenAI格式"""
        if self.type == ContentType.TEXT:
            return {"type": "text", "text": self.content}
        elif self.type == ContentType.IMAGE:
            return {"type": "image_url", "image_url": {"url": self.content}}
        elif self.type == ContentType.VIDEO:
            return {"type": "video_url", "video_url": {"url": self.content}}


@dataclass
class ParseRequest:
    """解析请求"""
    contents: List[MediaContent]
    prompt: Optional[str] = None
    enable_thinking: bool = False
    
    @classmethod
    def from_text(cls, text: str, prompt: Optional[str] = None) -> 'ParseRequest':
        """从文本创建请求"""
        contents = [MediaContent(ContentType.TEXT, text)]
        return cls(contents=contents, prompt=prompt)
    
    @classmethod
    def from_image(cls, image_url: str, prompt: Optional[str] = None) -> 'ParseRequest':
        """从图片创建请求"""
        contents = []
        if prompt:
            contents.append(MediaContent(ContentType.TEXT, prompt))
        contents.append(MediaContent(ContentType.IMAGE, image_url))
        return cls(contents=contents, prompt=prompt)
    
    @classmethod
    def from_video(cls, video_url: str, prompt: Optional[str] = None) -> 'ParseRequest':
        """从视频创建请求"""
        contents = []
        if prompt:
            contents.append(MediaContent(ContentType.TEXT, prompt))
        contents.append(MediaContent(ContentType.VIDEO, video_url))
        return cls(contents=contents, prompt=prompt)
    
    @classmethod
    def from_mixed(cls, text: Optional[str] = None, 
                   image_urls: Optional[List[str]] = None,
                   video_urls: Optional[List[str]] = None,
                   prompt: Optional[str] = None) -> 'ParseRequest':
        """从混合内容创建请求"""
        contents = []
        if prompt:
            contents.append(MediaContent(ContentType.TEXT, prompt))
        if text:
            contents.append(MediaContent(ContentType.TEXT, text))
        if image_urls:
            for url in image_urls:
                contents.append(MediaContent(ContentType.IMAGE, url))
        if video_urls:
            for url in video_urls:
                contents.append(MediaContent(ContentType.VIDEO, url))
        return cls(contents=contents, prompt=prompt)


@dataclass
class ParseResponse:
    """解析响应"""
    answer: str
    reasoning: Optional[str] = None
    usage: Optional[dict] = None
    
    def __str__(self) -> str:
        result = f"Answer: {self.answer}"
        if self.reasoning:
            result = f"Reasoning: {self.reasoning}\n\n{result}"
        return result
