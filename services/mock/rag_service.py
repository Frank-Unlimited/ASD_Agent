"""
知识库与 RAG Mock 实现
"""
from typing import Any, Dict, List, Optional
from src.interfaces import IKnowledgeRAGService


class MockRAGService(IKnowledgeRAGService):
    """RAG Mock 服务"""
    
    def get_service_name(self) -> str:
        return "MockRAGService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def search_methodology(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索方法论知识库"""
        print(f"[Mock RAG] 检索方法论: {query}")
        
        return [
            {
                "id": "method-001",
                "title": "地板时光核心原则",
                "content": "跟随孩子的兴趣，建立情感联结...",
                "relevance": 0.95
            }
        ]
    
    async def search_games(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """检索游戏知识库"""
        print(f"[Mock RAG] 检索游戏: {query}, filters={filters}")
        
        return [
            {
                "id": "game-001",
                "name": "积木传递游戏",
                "description": "通过传递积木建立眼神接触",
                "targetDimensions": ["eyeContact", "twoWayCommunication"],
                "difficulty": "easy",
                "ageRange": "2-3岁",
                "relevance": 0.92
            },
            {
                "id": "game-002",
                "name": "球类互动游戏",
                "description": "通过滚球建立互动",
                "targetDimensions": ["twoWayCommunication", "intimacy"],
                "difficulty": "easy",
                "ageRange": "2-3岁",
                "relevance": 0.88
            }
        ][:top_k]
    
    async def search_games_by_dimension(
        self, 
        dimension: str, 
        difficulty: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """按维度检索游戏"""
        print(f"[Mock RAG] 按维度检索: dimension={dimension}, difficulty={difficulty}")
        
        return await self.search_games(f"{dimension} {difficulty}", top_k=top_k)
    
    async def search_games_by_interest(
        self, 
        interest: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """按兴趣检索游戏"""
        print(f"[Mock RAG] 按兴趣检索: {interest}")
        
        return await self.search_games(interest, top_k=top_k)
    
    async def search_scale(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索量表知识库"""
        print(f"[Mock RAG] 检索量表: {query}")
        
        return [
            {
                "id": "scale-001",
                "scaleType": "CARS-2",
                "itemNumber": 1,
                "question": "与人的关系",
                "relevance": 0.90
            }
        ]
    
    async def search_cases(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索案例知识库"""
        print(f"[Mock RAG] 检索案例: {query}")
        
        return []
    
    async def get_game(self, game_id: str) -> Dict[str, Any]:
        """获取游戏详情"""
        print(f"[Mock RAG] 获取游戏详情: {game_id}")
        
        return {
            "id": game_id,
            "name": "积木传递游戏",
            "description": "通过传递积木建立眼神接触和双向沟通",
            "targetDimensions": ["eyeContact", "twoWayCommunication"],
            "difficulty": "easy",
            "ageRange": "2-3岁",
            "requiredProps": ["积木5-10块"],
            "steps": [
                {"step": 1, "instruction": "坐在孩子对面，拿起一块积木"},
                {"step": 2, "instruction": "等待孩子看向你，然后递给他"},
                {"step": 3, "instruction": "鼓励孩子递回来"}
            ],
            "tips": [
                "不要强迫孩子看你",
                "用夸张的表情吸引注意",
                "及时给予正向反馈"
            ]
        }
