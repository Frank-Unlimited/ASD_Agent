"""
语音服务真实适配器
"""
import importlib

# 动态导入（使用下划线版本）
speech_module = importlib.import_module('services.Speech_Processing.adapters')
AliyunSpeechService = speech_module.AliyunSpeechService

__all__ = ['AliyunSpeechService']
