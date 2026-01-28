"""
语音处理模块
基于阿里云智能语音交互服务
支持语音识别（ASR）和语音合成（TTS）
"""

from .api_interface import speech_to_text, text_to_speech
from .config import SpeechConfig
from .utils import convert_audio_to_pcm, get_audio_info, is_ffmpeg_available

__all__ = [
    'speech_to_text',
    'text_to_speech',
    'SpeechConfig',
    'convert_audio_to_pcm',
    'get_audio_info',
    'is_ffmpeg_available',
]

__version__ = '1.0.0'
