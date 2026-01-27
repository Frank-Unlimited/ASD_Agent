"""
API接口模块 - 简洁的三个核心接口
"""
import os
from typing import Optional

try:
    from .multimodal_parser import MultimodalParser
    from .models import ParseRequest
    from .config import MultimodalConfig
except ImportError:
    from multimodal_parser import MultimodalParser
    from models import ParseRequest
    from config import MultimodalConfig


# 全局解析器实例
_parser: Optional[MultimodalParser] = None


def _get_parser() -> MultimodalParser:
    """获取解析器实例"""
    global _parser
    if _parser is None:
        _parser = MultimodalParser()
    return _parser


def parse_text(text: str, prompt: Optional[str] = None) -> str:
    """
    解析文本
    
    Args:
        text: 输入文本
        prompt: 可选的提示词
        
    Returns:
        str: 解析结果
        
    Example:
        result = parse_text("什么是人工智能？")
        print(result)
    """
    parser = _get_parser()
    request = ParseRequest.from_text(text, prompt)
    response = parser.parse(request)
    return response.answer


def parse_image(image_url: str, prompt: Optional[str] = None) -> str:
    """
    解析图片
    
    Args:
        image_url: 图片URL或base64编码
        prompt: 提示词/问题
        
    Returns:
        str: 解析结果
        
    Example:
        # 使用URL
        result = parse_image("https://example.com/image.jpg", "描述这张图片")
        
        # 使用base64
        from utils import encode_local_image
        image_base64 = encode_local_image("path/to/image.jpg")
        result = parse_image(image_base64, "描述这张图片")
    """
    parser = _get_parser()
    request = ParseRequest.from_image(image_url, prompt)
    response = parser.parse(request)
    return response.answer


def parse_video(video_url: str, prompt: Optional[str] = None) -> str:
    """
    解析视频
    
    Args:
        video_url: 视频URL或base64编码
        prompt: 提示词/问题
        
    Returns:
        str: 解析结果
        
    Example:
        # 使用URL
        result = parse_video("https://example.com/video.mp4", "总结视频内容")
        
        # 使用base64
        from utils import encode_local_video
        video_base64 = encode_local_video("path/to/video.mp4")
        result = parse_video(video_base64, "总结视频内容")
    """
    parser = _get_parser()
    request = ParseRequest.from_video(video_url, prompt)
    response = parser.parse(request)
    return response.answer
