"""
语音服务真实适配器
"""
import sys
import os

# 添加 Speech-Processing 模块路径
speech_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Speech-Processing'))
if speech_path not in sys.path:
    sys.path.insert(0, speech_path)

try:
    from adapters import AliyunSpeechService
finally:
    # 清理路径
    if speech_path in sys.path:
        sys.path.remove(speech_path)

__all__ = ['AliyunSpeechService']
