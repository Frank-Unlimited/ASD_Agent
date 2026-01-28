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
        # 构建结构化提示词
        prompt = self._build_structured_prompt(context)
        
        # 准备视频
        if video_path.startswith(('http://', 'https://', 'data:')):
            video_url = video_path
        else:
            video_url = encode_local_video(video_path)
        
        # 调用视频解析
        analysis_text = parse_video(video_url, prompt)
        
        # 尝试解析结构化结果
        try:
            parsed_result = self._parse_analysis_text(analysis_text)
            parsed_result['raw_analysis'] = analysis_text
            return parsed_result
        except Exception as e:
            print(f"[Multimodal] 结构化解析失败: {e}，使用降级方案")
            # 降级方案：从文本中提取关键信息
            return self._fallback_parse(analysis_text)
    
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
    
    def _build_structured_prompt(self, context: Dict[str, Any]) -> str:
        """构建结构化分析提示词"""
        child_profile = context.get('child_profile', {})
        child_name = child_profile.get('name', '孩子')
        child_age = child_profile.get('age', '未知')
        
        return f"""
请详细分析视频中{child_name}（{child_age}个月）的表现，并以JSON格式返回结果。

分析维度：
1. 行为表现（behaviors）：眼神接触、肢体动作、重复行为等
2. 互动情况（interactions）：与家长互动、回应性、主动性等
3. 情绪表现（emotions）：情绪状态、变化、调节能力等
4. 注意力情况（attention）：持续时间、转移能力、投入程度等

请按以下JSON格式返回：
{{
    "behaviors": [
        {{
            "description": "具体行为描述",
            "timestamp": "视频时间点（如00:15）",
            "significance": 1-5的重要性评分,
            "type": "eye_contact/body_movement/repetitive/other"
        }}
    ],
    "interactions": [
        {{
            "description": "互动描述",
            "timestamp": "视频时间点",
            "quality": 1-5的质量评分,
            "type": "response/initiative/joint_attention/other"
        }}
    ],
    "emotions": {{
        "dominant_emotion": "主要情绪（calm/happy/frustrated/anxious等）",
        "changes": [
            {{
                "timestamp": "时间点",
                "from": "之前情绪",
                "to": "之后情绪",
                "trigger": "触发原因"
            }}
        ],
        "regulation_ability": "情绪调节能力描述"
    }},
    "attention": {{
        "duration": "注意力持续时间（short/moderate/long）",
        "quality": "注意力质量（poor/fair/good）",
        "focus_shifts": [
            {{
                "timestamp": "时间点",
                "from": "之前关注对象",
                "to": "之后关注对象"
            }}
        ]
    }},
    "summary": "整体表现总结（200字以内）",
    "highlights": [
        {{
            "timestamp": "时间点",
            "description": "亮点描述",
            "importance": "high/medium/low"
        }}
    ]
}}

请确保返回有效的JSON格式。
"""
    
    def _parse_analysis_text(self, text: str) -> Dict[str, Any]:
        """解析AI返回的文本为结构化数据"""
        import json
        import re
        
        # 尝试提取JSON
        json_str = text.strip()
        
        # 如果包含代码块标记，提取其中的JSON
        if "```json" in text:
            json_str = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if json_str:
                json_str = json_str.group(1)
        elif "```" in text:
            json_str = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
            if json_str:
                json_str = json_str.group(1)
        
        # 尝试解析JSON
        try:
            result = json.loads(json_str)
            
            # 验证必需字段
            if not isinstance(result, dict):
                raise ValueError("返回结果不是字典格式")
            
            # 确保所有必需字段存在
            result.setdefault('behaviors', [])
            result.setdefault('interactions', [])
            result.setdefault('emotions', {'dominant_emotion': 'unknown'})
            result.setdefault('attention', {'duration': 'unknown', 'quality': 'unknown'})
            result.setdefault('summary', text[:500])
            result.setdefault('highlights', [])
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"[Multimodal] JSON解析失败: {e}")
            raise
    
    def _fallback_parse(self, text: str) -> Dict[str, Any]:
        """降级解析方案：从文本中提取关键信息"""
        import re
        
        # 初始化结果
        result = {
            'behaviors': [],
            'interactions': [],
            'emotions': {'dominant_emotion': 'unknown', 'changes': []},
            'attention': {'duration': 'unknown', 'quality': 'unknown'},
            'summary': text[:500] if len(text) > 500 else text,
            'highlights': [],
            'raw_analysis': text
        }
        
        # 提取行为相关信息
        behavior_keywords = ['眼神', '接触', '注视', '看', '动作', '手势', '重复', '摇晃', '拍手']
        for keyword in behavior_keywords:
            if keyword in text:
                # 查找包含关键词的句子
                sentences = re.split(r'[。！？\n]', text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence) > 5:
                        result['behaviors'].append({
                            'description': sentence.strip(),
                            'timestamp': '未知',
                            'significance': 3,
                            'type': 'extracted'
                        })
                        break
        
        # 提取互动相关信息
        interaction_keywords = ['互动', '回应', '交流', '沟通', '配合', '主动']
        for keyword in interaction_keywords:
            if keyword in text:
                sentences = re.split(r'[。！？\n]', text)
                for sentence in sentences:
                    if keyword in sentence and len(sentence) > 5:
                        result['interactions'].append({
                            'description': sentence.strip(),
                            'timestamp': '未知',
                            'quality': 3,
                            'type': 'extracted'
                        })
                        break
        
        # 提取情绪相关信息
        emotion_keywords = {
            'happy': ['开心', '高兴', '愉快', '笑', '微笑'],
            'calm': ['平静', '安静', '稳定'],
            'frustrated': ['沮丧', '失望', '不满'],
            'anxious': ['焦虑', '紧张', '不安'],
            'excited': ['兴奋', '激动']
        }
        
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    result['emotions']['dominant_emotion'] = emotion
                    break
            if result['emotions']['dominant_emotion'] != 'unknown':
                break
        
        # 提取注意力相关信息
        if any(word in text for word in ['专注', '集中', '持续', '长时间']):
            result['attention']['duration'] = 'long'
            result['attention']['quality'] = 'good'
        elif any(word in text for word in ['分散', '转移', '短暂']):
            result['attention']['duration'] = 'short'
            result['attention']['quality'] = 'poor'
        else:
            result['attention']['duration'] = 'moderate'
            result['attention']['quality'] = 'fair'
        
        # 如果没有提取到任何行为，至少添加一个总结性的
        if not result['behaviors']:
            result['behaviors'].append({
                'description': '视频分析结果见summary字段',
                'timestamp': '全程',
                'significance': 3,
                'type': 'general'
            })
        
        if not result['interactions']:
            result['interactions'].append({
                'description': '视频分析结果见summary字段',
                'timestamp': '全程',
                'quality': 3,
                'type': 'general'
            })
        
        return result


__all__ = ['MultimodalDocumentParserService', 'MultimodalVideoAnalysisService']
