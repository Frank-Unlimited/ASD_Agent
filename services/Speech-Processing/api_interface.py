"""
API接口模块 - 简洁的函数式接口
"""
import os
from typing import Optional

try:
    from .config import SpeechConfig
    from .asr_service import SpeechRecognizer
    from .tts_service import SpeechSynthesizer
except ImportError:
    from config import SpeechConfig
    from asr_service import SpeechRecognizer
    from tts_service import SpeechSynthesizer


# 全局实例
_recognizer: Optional[SpeechRecognizer] = None
_synthesizer: Optional[SpeechSynthesizer] = None


def _get_recognizer() -> SpeechRecognizer:
    """获取识别器实例"""
    global _recognizer
    if _recognizer is None:
        _recognizer = SpeechRecognizer()
    return _recognizer


def _get_synthesizer() -> SpeechSynthesizer:
    """获取合成器实例"""
    global _synthesizer
    if _synthesizer is None:
        _synthesizer = SpeechSynthesizer()
    return _synthesizer


def speech_to_text(audio_path: str) -> str:
    """
    语音转文字
    
    Args:
        audio_path: 音频文件路径（PCM格式，16000Hz采样率）
        
    Returns:
        str: 识别结果文本
        
    Example:
        text = speech_to_text("audio.pcm")
        print(text)
    """
    recognizer = _get_recognizer()
    return recognizer.recognize_file(audio_path)


def text_to_speech(text: str, output_path: Optional[str] = None) -> str:
    """
    文字转语音
    
    Args:
        text: 要合成的文本
        output_path: 输出文件路径（可选，默认为temp.wav）
        
    Returns:
        str: 输出文件路径
        
    Example:
        audio_path = text_to_speech("你好，世界")
        print(f"音频已保存到: {audio_path}")
    """
    if output_path is None:
        output_path = "temp.wav"
    
    synthesizer = _get_synthesizer()
    return synthesizer.synthesize_to_file(text, output_path)
