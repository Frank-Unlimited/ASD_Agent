"""
其他基础设施层 Mock 服务（模块4-6）
"""
from typing import Any, Dict, List
from src.interfaces import (
    IVideoAnalysisService,
    ISpeechService,
    IDocumentParserService
)


# ============ 模块4: AI 视频解析 Mock ============

class MockVideoAnalysisService(IVideoAnalysisService):
    """视频解析 Mock 服务"""
    
    def get_service_name(self) -> str:
        return "MockVideoAnalysisService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def analyze_video(
        self, 
        video_path: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析视频"""
        print(f"[Mock Video] 分析视频: {video_path}")
        
        return {
            "duration": "15:23",
            "highlights": [
                {"time": "02:15", "event": "主动眼神接触", "duration": "3秒"},
                {"time": "08:42", "event": "微笑回应", "confidence": 0.92},
                {"time": "12:30", "event": "主动递积木", "significance": "breakthrough"}
            ],
            "metrics": {
                "eyeContactCount": 5,
                "smileCount": 8,
                "verbalAttempts": 2
            }
        }
    
    async def extract_highlights(
        self, 
        video_path: str, 
        analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """提取关键片段"""
        print(f"[Mock Video] 提取关键片段: {video_path}")
        
        return analysis_result.get("highlights", [])


# ============ 模块5: 语音处理 Mock ============

class MockSpeechService(ISpeechService):
    """语音处理 Mock 服务"""
    
    def get_service_name(self) -> str:
        return "MockSpeechService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def speech_to_text(self, audio_path: str) -> str:
        """语音转文字"""
        print(f"[Mock Speech] 语音转文字: {audio_path}")
        
        return "今天玩积木的时候，辰辰突然抬头看了我一眼，大概有2秒钟"
    
    async def text_to_speech(self, text: str) -> str:
        """文字转语音"""
        print(f"[Mock Speech] 文字转语音: {text[:50]}...")
        
        return "/mock/audio/guidance_001.mp3"


# ============ 模块6: 文档解析 Mock ============

class MockDocumentParserService(IDocumentParserService):
    """文档解析 Mock 服务"""
    
    def get_service_name(self) -> str:
        return "MockDocumentParserService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def parse_report(
        self, 
        file_path: str, 
        file_type: str
    ) -> Dict[str, Any]:
        """解析医院报告"""
        print(f"[Mock Parser] 解析报告: {file_path}, type={file_type}")
        
        return {
            "diagnosis": "孤独症谱系障碍（ASD）轻度",
            "age": 2.5,
            "assessmentDate": "2025-12-15",
            "keyFindings": {
                "socialInteraction": "眼神接触少，不主动发起互动",
                "communication": "语言发育迟缓，词汇量约20个",
                "behavior": "有刻板行为，喜欢旋转物体"
            },
            "recommendations": [
                "建议进行早期干预",
                "家庭训练为主",
                "定期复查"
            ]
        }
    
    async def parse_scale(
        self, 
        scale_data: Dict[str, Any], 
        scale_type: str
    ) -> Dict[str, Any]:
        """解析量表数据"""
        print(f"[Mock Parser] 解析量表: type={scale_type}")
        
        return {
            "scaleType": scale_type,
            "totalScore": 32,
            "severity": "轻度",
            "dimensionScores": {
                "socialInteraction": 8,
                "communication": 7,
                "behavior": 9,
                "sensory": 8
            }
        }
