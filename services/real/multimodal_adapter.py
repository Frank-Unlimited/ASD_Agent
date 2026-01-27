"""
多模态理解服务真实适配器
"""
import sys
import os

# 添加 Multimodal-Understanding 模块路径
multimodal_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Multimodal-Understanding'))
if multimodal_path not in sys.path:
    sys.path.insert(0, multimodal_path)

try:
    from adapters import MultimodalVideoAnalysisService, MultimodalDocumentParserService
finally:
    # 清理路径
    if multimodal_path in sys.path:
        sys.path.remove(multimodal_path)

__all__ = ['MultimodalVideoAnalysisService', 'MultimodalDocumentParserService']
