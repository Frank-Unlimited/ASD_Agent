"""
多模态理解服务真实适配器
"""
import importlib

# 动态导入多模态理解模块
multimodal_module = importlib.import_module('services.Multimodal_Understanding.adapters')
MultimodalVideoAnalysisService = multimodal_module.MultimodalVideoAnalysisService
MultimodalDocumentParserService = multimodal_module.MultimodalDocumentParserService

__all__ = ['MultimodalVideoAnalysisService', 'MultimodalDocumentParserService']
