"""
基础设施层接口定义（模块1-6）
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.interfaces.base import BaseService


# ============ 模块1: SQLite 数据管理模块 ============

class ISQLiteService(BaseService):
    """SQLite 数据管理接口"""
    
    @abstractmethod
    async def get_child(self, child_id: str) -> Dict[str, Any]:
        """获取孩子档案"""
        pass
    
    @abstractmethod
    async def save_child(self, profile: Dict[str, Any]) -> None:
        """保存孩子档案"""
        pass
    
    @abstractmethod
    async def create_session(self, child_id: str, game_id: str) -> str:
        """创建干预会话"""
        pass
    
    @abstractmethod
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """获取会话信息"""
        pass
    
    @abstractmethod
    async def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """更新会话信息"""
        pass
    
    @abstractmethod
    async def save_weekly_plan(self, plan: Dict[str, Any]) -> str:
        """保存周计划"""
        pass
    
    @abstractmethod
    async def get_weekly_plan(self, plan_id: str) -> Dict[str, Any]:
        """获取周计划"""
        pass
    
    @abstractmethod
    async def save_observation(self, observation: Dict[str, Any]) -> str:
        """保存观察记录"""
        pass
    
    @abstractmethod
    async def get_session_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会话历史"""
        pass
    
    @abstractmethod
    async def delete_child(self, child_id: str) -> None:
        """删除孩子档案"""
        pass


# ============ 模块2: Graphiti 记忆网络模块 ============

class IGraphitiService(BaseService):
    """Graphiti 记忆网络接口"""
    
    @abstractmethod
    async def save_memories(self, child_id: str, memories: List[Dict[str, Any]]) -> None:
        """批量保存记忆（优化：一次性写入）"""
        pass
    
    @abstractmethod
    async def get_recent_memories(self, child_id: str, days: int = 7) -> List[Dict[str, Any]]:
        """获取最近记忆"""
        pass
    
    @abstractmethod
    async def analyze_trends(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """分析趋势"""
        pass
    
    @abstractmethod
    async def detect_milestones(self, child_id: str) -> List[Dict[str, Any]]:
        """检测里程碑"""
        pass
    
    @abstractmethod
    async def detect_plateau(self, child_id: str, dimension: str) -> Dict[str, Any]:
        """检测平台期"""
        pass
    
    @abstractmethod
    async def build_context(self, child_id: str) -> Dict[str, Any]:
        """构建当前上下文（趋势、关注点等）"""
        pass
    
    @abstractmethod
    async def clear_memories(self, child_id: str) -> None:
        """清空指定孩子的所有记忆"""
        pass


# ============ 模块3: 知识库与 RAG 模块 ============

class IKnowledgeRAGService(BaseService):
    """知识库与 RAG 接口"""
    
    @abstractmethod
    async def search_methodology(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索方法论知识库"""
        pass
    
    @abstractmethod
    async def search_games(
        self, 
        query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """检索游戏知识库"""
        pass
    
    @abstractmethod
    async def search_games_by_dimension(
        self, 
        dimension: str, 
        difficulty: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """按维度检索游戏"""
        pass
    
    @abstractmethod
    async def search_games_by_interest(
        self, 
        interest: str, 
        top_k: int = 10
    ) -> List[Dict[str, Any]]:
        """按兴趣检索游戏"""
        pass
    
    @abstractmethod
    async def search_scale(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索量表知识库"""
        pass
    
    @abstractmethod
    async def search_cases(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """检索案例知识库"""
        pass
    
    @abstractmethod
    async def get_game(self, game_id: str) -> Dict[str, Any]:
        """获取游戏详情"""
        pass


# ============ 模块4: AI 视频解析模块 ============

class IVideoAnalysisService(BaseService):
    """AI 视频解析接口"""
    
    @abstractmethod
    async def analyze_video(
        self, 
        video_path: str, 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """分析视频"""
        pass
    
    @abstractmethod
    async def extract_highlights(
        self, 
        video_path: str, 
        analysis_result: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """提取关键片段"""
        pass


# ============ 模块5: 语音处理模块 ============

class ISpeechService(BaseService):
    """语音处理接口"""
    
    @abstractmethod
    async def speech_to_text(self, audio_path: str) -> str:
        """语音转文字"""
        pass
    
    @abstractmethod
    async def text_to_speech(self, text: str) -> str:
        """文字转语音（返回音频文件路径）"""
        pass


# ============ 模块6: 文档解析模块 ============

class IDocumentParserService(BaseService):
    """文档解析接口"""
    
    @abstractmethod
    async def parse_report(
        self, 
        file_path: str, 
        file_type: str
    ) -> Dict[str, Any]:
        """解析医院报告"""
        pass
    
    @abstractmethod
    async def parse_scale(
        self, 
        scale_data: Dict[str, Any], 
        scale_type: str
    ) -> Dict[str, Any]:
        """解析量表数据"""
        pass
