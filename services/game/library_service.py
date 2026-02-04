"""
游戏库服务
"""
from typing import List, Dict, Optional, Any
from .library_data import GAME_LIBRARY
from src.models.game import GamePlan, GameStatus
import uuid
from datetime import datetime

class GameLibraryService:
    """管理结构化游戏库的服务"""
    
    def __init__(self):
        # 将原始数据转换为字典，方便检索
        self._games_by_id = {game["id"]: game for game in GAME_LIBRARY}
    
    def list_games(self) -> List[Dict[str, Any]]:
        """列出所有预设游戏"""
        return GAME_LIBRARY
    
    def get_game_by_id(self, game_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取游戏"""
        return self._games_by_id.get(game_id)
    
    def search_games_by_dimension(self, dimension: str) -> List[Dict[str, Any]]:
        """按维度搜索游戏"""
        return [g for g in GAME_LIBRARY if g["target_dimension"].value == dimension]

    def select_game_for_child(self, game_id: str, child_id: str) -> Optional[GamePlan]:
        """
        从库中选择一个游戏，并实例化为针对特定孩子的 GamePlan
        """
        game_data = self.get_game_by_id(game_id)
        if not game_data:
            return None
            
        # 复制库中的数据，并补充孩子特定字段
        # 注意：这里我们保留原始 ID 或生成一个新的映射 ID？
        # 用户希望从“库”里选，所以核心内容应该保持一致。
        
        # 转换格式以匹配 GamePlan
        plan_data = game_data.copy()
        plan_data["game_id"] = game_id # 直接使用库 ID，方便前端匹配
        plan_data["child_id"] = child_id
        plan_data["status"] = GameStatus.RECOMMENDED
        plan_data["created_at"] = datetime.now()
        
        return GamePlan(**plan_data)

__all__ = ['GameLibraryService']
