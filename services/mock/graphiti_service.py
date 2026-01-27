"""
Graphiti 记忆网络 Mock 实现
"""
from typing import Any, Dict, List
from src.interfaces import IGraphitiService


class MockGraphitiService(IGraphitiService):
    """Graphiti Mock 服务"""
    
    def __init__(self):
        self.memories = {}
    
    def get_service_name(self) -> str:
        return "MockGraphitiService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def save_memories(self, child_id: str, memories: List[Dict[str, Any]]) -> None:
        """批量保存记忆"""
        print(f"[Mock Graphiti] 批量保存记忆: {child_id}, count={len(memories)}")
        
        if child_id not in self.memories:
            self.memories[child_id] = []
        
        self.memories[child_id].extend(memories)
    
    async def get_recent_memories(self, child_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近记忆"""
        print(f"[Mock Graphiti] 获取最近记忆: {child_id}, days={days}")
        
        return [
            {
                "memoryId": "mem-001",
                "timestamp": "2026-01-25T10:30:00",
                "content": "孩子主动递积木",
                "significance": "breakthrough"
            }
        ]
    
    async def analyze_trends(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """分析趋势"""
        print(f"[Mock Graphiti] 分析趋势: {child_id}, dimension={dimension}")
        
        return {
            "dimension": dimension,
            "trend": "improving",
            "rate": 0.22,
            "confidence": 0.85,
            "dataPoints": [
                {"date": "2026-01-15", "value": 2},
                {"date": "2026-01-20", "value": 5},
                {"date": "2026-01-25", "value": 8}
            ]
        }
    
    async def detect_milestones(self, child_id: str) -> List[Dict[str, Any]]:
        """检测里程碑"""
        print(f"[Mock Graphiti] 检测里程碑: {child_id}")
        
        return [
            {
                "milestoneId": "milestone-001",
                "date": "2026-01-23",
                "title": "首次主动眼神接触",
                "description": "孩子在积木游戏中主动看向家长",
                "significance": "breakthrough"
            }
        ]
    
    async def detect_plateau(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """检测平台期"""
        print(f"[Mock Graphiti] 检测平台期: {child_id}, dimension={dimension}")
        
        return {
            "hasPlateau": False,
            "dimension": dimension,
            "message": "该维度正在稳步提升"
        }
    
    async def build_context(self, child_id: str) -> Dict[str, Any]:
        """构建当前上下文"""
        print(f"[Mock Graphiti] 构建上下文: {child_id}")
        
        return {
            "recentTrends": {
                "eyeContact": {"trend": "improving", "rate": 0.22},
                "twoWayCommunication": {"trend": "stable", "rate": 0.05}
            },
            "attentionPoints": [
                "🌟 眼神接触快速提升（+22%/月）",
                "📌 双向沟通需要加强"
            ],
            "activeGoals": [
                {"dimension": "eyeContact", "target": "达到5次/游戏"},
                {"dimension": "twoWayCommunication", "target": "建立简单互动"}
            ],
            "lastUpdated": "2026-01-27T10:00:00"
        }
