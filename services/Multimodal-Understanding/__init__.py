"""
多模态解析模块 - 简洁版
只暴露三个核心接口：parse_text, parse_image, parse_video

快速使用:
    from Multimodal_Understanding import parse_text, parse_image, parse_video
    
    # 文本
    result = parse_text("什么是AI？")
    
    # 图片
    result = parse_image("https://example.com/image.jpg", "描述图片")
    result = parse_image("实际本地地址", "描述图片")
    
    # 视频
    result = parse_video("https://example.com/video.mp4", "总结视频")
    result = parse_video("实际本地地址", "总结视频")
"""

try:
    from .api_interface import parse_text, parse_image, parse_video
    from .utils import encode_local_image, encode_local_video
except ImportError:
    from api_interface import parse_text, parse_image, parse_video
    from utils import encode_local_image, encode_local_video

__all__ = [
    'parse_text',
    'parse_image',
    'parse_video',
    'encode_local_image',
    'encode_local_video',
]

__version__ = '1.0.0'
