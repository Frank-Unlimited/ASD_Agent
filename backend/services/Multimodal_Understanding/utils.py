"""
工具函数模块
"""
import base64
import mimetypes
from pathlib import Path
from typing import Union
import logging

logger = logging.getLogger(__name__)


def encode_local_image(image_path: Union[str, Path]) -> str:
    """
    将本地图片编码为base64 data URL
    
    Args:
        image_path: 图片路径
        
    Returns:
        str: base64编码的data URL
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    # 获取MIME类型
    mime_type, _ = mimetypes.guess_type(str(image_path))
    if not mime_type or not mime_type.startswith('image/'):
        mime_type = 'image/jpeg'  # 默认类型
    
    # 读取并编码
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{image_data}"


def encode_local_video(video_path: Union[str, Path]) -> str:
    """
    将本地视频编码为base64 data URL
    
    Args:
        video_path: 视频路径
        
    Returns:
        str: base64编码的data URL
    """
    video_path = Path(video_path)
    
    if not video_path.exists():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    # 获取MIME类型
    mime_type, _ = mimetypes.guess_type(str(video_path))
    if not mime_type or not mime_type.startswith('video/'):
        mime_type = 'video/mp4'  # 默认类型
    
    # 读取并编码
    with open(video_path, 'rb') as f:
        video_data = base64.b64encode(f.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{video_data}"


def encode_video_bytes(video_bytes: bytes, mime_type: str = "video/mp4") -> str:
    """
    将视频字节数据编码为base64 data URL
    
    Args:
        video_bytes: 视频字节数据
        mime_type: MIME类型，默认为video/mp4
        
    Returns:
        str: base64编码的data URL
    """
    video_data = base64.b64encode(video_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{video_data}"


def encode_image_bytes(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    将图片字节数据编码为base64 data URL
    
    Args:
        image_bytes: 图片字节数据
        mime_type: MIME类型，默认为image/jpeg
        
    Returns:
        str: base64编码的data URL
    """
    image_data = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{image_data}"


def validate_url(url: str) -> bool:
    """
    验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        bool: 是否为有效URL
    """
    if url.startswith('data:'):
        return True
    
    if url.startswith(('http://', 'https://')):
        return True
    
    return False


def setup_logging(level: str = "INFO"):
    """
    配置日志
    
    Args:
        level: 日志级别
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
