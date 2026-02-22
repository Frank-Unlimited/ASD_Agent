"""
系统适配器
将 Speech-Processing 模块适配到系统的 ISpeechService 接口
"""
import os
from typing import Optional
from src.interfaces.infrastructure import ISpeechService

# 导入核心功能
try:
    from .api_interface import speech_to_text, text_to_speech
except ImportError:
    from api_interface import speech_to_text, text_to_speech


class AliyunSpeechService(ISpeechService):
    """阿里云语音服务适配器"""
    
    async def speech_to_text(self, audio_path: str) -> str:
        """
        语音转文字
        
        Args:
            audio_path: 音频文件路径
            
        Returns:
            str: 识别结果文本
        """
        # 调用实际实现（同步转异步）
        return speech_to_text(audio_path)
    
    async def text_to_speech(self, text: str) -> str:
        """
        文字转语音
        
        Args:
            text: 要合成的文本
            
        Returns:
            str: 音频文件路径
        """
        # 生成临时文件路径
        import tempfile
        import uuid
        
        temp_dir = tempfile.gettempdir()
        filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
        output_path = os.path.join(temp_dir, filename)
        
        # 调用实际实现（同步转异步）
        return text_to_speech(text, output_path)
    
    def get_service_name(self) -> str:
        """获取服务名称"""
        return "aliyun_speech"
    
    def get_service_version(self) -> str:
        """获取服务版本"""
        return "1.0.0"


__all__ = ['AliyunSpeechService']
