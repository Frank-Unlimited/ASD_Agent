"""
系统适配器集合
包含文档解析和视频分析两个适配器
"""
import os
import json
from typing import Dict, Any, List
from src.interfaces.infrastructure import IDocumentParserService, IVideoAnalysisService

# 导入核心功能
try:
    from .api_interface import parse_image, parse_video, parse_text
    from .utils import encode_local_image, encode_local_video
except ImportError:
    from api_interface import parse_image, parse_video, parse_text
    from utils import encode_local_image, encode_local_video


# ============ 文档解析适配器 ============

class MultimodalDocumentParserService(IDocumentParserService):
    """文档解析服务 - 使用图片和文本解析"""
    
    async def parse_report(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """解析医院报告"""
        if file_type.lower() in ['jpg', 'jpeg', 'png', 'image']:
            # 准备图片
            if file_path.startswith(('http://', 'https://', 'data:')):
                image_url = file_path
            else:
                image_url = encode_local_image(file_path)
            
            # 解析提示词
            prompt = """
            请详细解析这份医院报告，提取：
            1. 诊断结果（主要诊断、诊断依据）
            2. 严重程度（轻度/中度/重度）
            3. 测试结果（各项测试名称和得分）
            4. 医生建议（治疗建议、干预方案）
            5. 患者信息（姓名、年龄、日期）
            """
            
            raw_text = parse_image(image_url, prompt)
            
            return {
                'raw_text': raw_text,
                'diagnosis': self._extract_field(raw_text, '诊断'),
                'severity': self._extract_field(raw_text, '严重程度'),
                'recommendations': [raw_text],  # 简化实现
                'file_path': file_path
            }
        else:
            raise ValueError(f"暂不支持 {file_type} 格式")
    
    async def parse_scale(self, scale_data: Dict[str, Any], scale_type: str) -> Dict[str, Any]:
        """解析量表数据"""
        prompt = f"请解析这份{scale_type}量表，提取总分、各维度得分、严重程度和建议。"
        
        if 'image_path' in scale_data:
            # 图片量表
            image_path = scale_data['image_path']
            if image_path.startswith(('http://', 'https://', 'data:')):
                image_url = image_path
            else:
                image_url = encode_local_image(image_path)
            
            raw_text = parse_image(image_url, prompt)
        elif 'text' in scale_data:
            # 文本量表
            raw_text = parse_text(f"{prompt}\n\n量表内容：\n{scale_data['text']}")
        else:
            raise ValueError("量表数据必须包含 image_path 或 text")
        
        return {
            'scale_type': scale_type,
            'total_score': 0,  # 需要从raw_text中提取
            'dimension_scores': {},
            'severity_level': 'unknown',
            'interpretation': raw_text,
            'recommendations': [],
            'raw_analysis': raw_text
        }
    
    def get_service_name(self) -> str:
        return "multimodal_document_parser"
    
    def get_service_version(self) -> str:
        return "1.0.0"
    
    def _extract_field(self, text: str, field: str) -> str:
        """从文本中提取指定字段"""
        # 尝试查找字段相关内容
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if field in line:
                # 返回该行及后续几行
                result_lines = lines[i:min(i+3, len(lines))]
                return '\n'.join(result_lines)
        # 如果没找到，返回前200字符
        return text[:200]


# ============ 视频分析适配器 ============

class MultimodalVideoAnalysisService(IVideoAnalysisService):
    """视频分析服务 - 使用视频解析"""
    
    async def analyze_video(self, video_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """分析视频"""
        # 构建提示词
        prompt = self._build_prompt(context)
        
        # 准备视频
        if video_path.startswith(('http://', 'https://', 'data:')):
            video_url = video_path
        else:
            video_url = encode_local_video(video_path)
        
        # 调用视频解析
        analysis_text = parse_video(video_url, prompt)
        
        return {
            'raw_analysis': analysis_text,
            'behaviors': [{'description': '眼神接触', 'significance': 3}],
            'interactions': [{'description': '互动行为', 'quality': 3}],
            'emotions': {'dominant_emotion': 'calm'},
            'attention': {'duration': 'moderate'},
            'summary': analysis_text[:500]
        }
    
    async def extract_highlights(self, video_path: str, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取关键片段"""
        highlights = []
        for behavior in analysis_result.get('behaviors', []):
            highlights.append({
                'timestamp': '00:00',
                'duration': 5,
                'type': 'behavior',
                'description': behavior.get('description', ''),
                'importance': behavior.get('significance', 3)
            })
        return highlights[:10]
    
    def get_service_name(self) -> str:
        return "multimodal_video_analysis"
    
    def get_service_version(self) -> str:
        return "1.0.0"
    
    def _build_prompt(self, context: Dict[str, Any]) -> str:
        """构建分析提示词"""
        child_profile = context.get('child_profile', {})
        child_name = child_profile.get('name', '孩子')
        
        return f"""
        请详细分析视频中{child_name}的表现，重点关注：
        1. 行为表现（眼神接触、肢体动作、重复行为）
        2. 互动情况（与家长互动、回应性、主动性）
        3. 情绪表现（情绪状态、变化、调节能力）
        4. 注意力情况（持续时间、转移能力、投入程度）
        
        请按时间顺序详细描述。
        """


__all__ = ['MultimodalDocumentParserService', 'MultimodalVideoAnalysisService']
