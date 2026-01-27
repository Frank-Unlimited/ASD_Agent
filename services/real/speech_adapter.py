"""
语音服务真实适配器
"""
import importlib

# 动态导入带连字符的模块
speech_module = importlib.import_module('services.Speech-Processing.adapters')
AliyunSpeechService = speech_module.AliyunSpeechService

__all__ = ['AliyunSpeechService']
