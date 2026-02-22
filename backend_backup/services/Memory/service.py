"""
Memory 服务 - 简化版（已移除 Graphiti 依赖）
提供基础的记忆存储接口
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import json

from .config import MemoryConfig
from .storage.graph_storage import GraphStorage
from .models.nodes import Person, Behavior, Object, FloorTimeGame, ChildAssessment
from .utils.validators import validate_person, validate_behavior, validate_object

# 导入 LLM 服务
from services.LLM_Service.service import get_llm_service


class MemoryService:
    """
    记忆服务 - 简化版
    
    职责：
    1. 提供基础的数据存储接口
    2. 数据验证和错误处理
    3. 封装图存储操作
    
    注意：已移除 Graphiti 相关功能
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        
        # GraphStorage（用于直接查询）
        self.storage = GraphStorage(
            uri=self.config.neo4j_uri,
            user=self.config.neo4j_user,
            password=self.config.neo4j_password
        )
        
        # LLM 服务（按需初始化）
        self._llm_service = None
    
    @property
    def llm_service(self):
        """延迟初始化 LLM 服务"""
        if self._llm_service is None and self.config.enable_llm:
            self._llm_service = get_llm_service()
        return self._llm_service
    
    async def initialize(self):
        """初始化服务（创建固定节点、约束、索引）"""
        await self.storage.initialize_fixed_nodes()
    
    async def close(self):
        """关闭服务"""
        await self.storage.close()
    
    # ========== 基础写入 ==========
    
    async def record_behavior(
        self,
        child_id: str,
        raw_input: str,
        input_type: str = "text",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        日常行为记录
        
        Args:
            child_id: 孩子ID
            raw_input: 原始输入（文字描述）
            input_type: 输入类型（text/quick_button）
            context: 可选上下文
        
        Returns:
            行为记录字典
        """
        behavior_id = f"behavior_{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        behavior = Behavior(
            behavior_id=behavior_id,
            child_id=child_id,
            timestamp=timestamp,
            event_type="observation",
            description=raw_input,
            raw_input=raw_input,
            input_type=input_type,
            significance="normal",
            ai_analysis={},
            context=context or {}
        )
        
        await self.storage.create_behavior(behavior)
        
        return {
            "behavior_id": behavior_id,
            "child_id": child_id,
            "timestamp": timestamp,
            "event_type": "observation",
            "description": raw_input,
            "raw_input": raw_input,
            "input_type": input_type,
            "significance": "normal",
            "ai_analysis": {},
            "context": context or {},
            "objects_involved": [],
            "related_interests": [],
            "related_functions": []
        }
    
    async def store_game_summary(
        self,
        child_id: str,
        game_id: str,
        summary_text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        存储游戏总结
        
        Args:
            child_id: 孩子ID
            game_id: 游戏ID
            summary_text: 游戏总结文本
            metadata: 可选元数据
        
        Returns:
            存储结果
        """
        episode_id = f"summary_{uuid.uuid4().hex[:12]}"
        
        # 更新游戏节点
        try:
            game = await self.storage.get_game(game_id)
            if game:
                updates = {
                    "status": "completed",
                    "implementation": {
                        **game.get("implementation", {}),
                        "summary": summary_text,
                        **(metadata or {})
                    }
                }
                await self.storage.update_game(game_id, updates)
        except Exception as e:
            print(f"[store_game_summary] 更新游戏节点失败: {e}")
        
        return {
            "episode_id": episode_id,
            "game_id": game_id,
            "child_id": child_id,
            "extracted_entities": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def store_assessment(
        self,
        child_id: str,
        assessment_text: str,
        assessment_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        存储评估报告
        
        Args:
            child_id: 孩子ID
            assessment_text: 评估报告文本
            assessment_type: 评估类型
            metadata: 可选元数据
        
        Returns:
            存储结果
        """
        assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        assessment = ChildAssessment(
            assessment_id=assessment_id,
            child_id=child_id,
            assessment_type=assessment_type,
            summary=assessment_text,
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata=metadata or {}
        )
        
        await self.storage.create_assessment(assessment)
        
        # 创建关系：孩子 -> 评估
        await self.storage.create_relationship(
            from_id=child_id,
            from_label="Person",
            to_id=assessment_id,
            to_label="ChildAssessment",
            rel_type="接受评估"
        )
        
        return {
            "episode_id": assessment_id,
            "assessment_id": assessment_id,
            "child_id": child_id,
            "assessment_type": assessment_type,
            "extracted_entities": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def import_profile(
        self,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        从结构化数据导入档案
        
        Args:
            profile_data: 档案数据
        
        Returns:
            导入结果
        """
        name = profile_data.get("name", "未命名")
        age = profile_data.get("age")
        diagnosis = profile_data.get("diagnosis", "")
        
        # 生成 child_id
        child_id = f"child_{uuid.uuid4().hex[:12]}"
        
        # 创建 Person 节点
        child = Person(
            person_id=child_id,
            person_type="child",
            name=name,
            role="patient",
            basic_info={
                "age": age,
                "diagnosis": diagnosis,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                "source": "profile_import"
            },
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        await self.storage.create_person(child)
        
        # 创建初始评估
        assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        assessment = ChildAssessment(
            assessment_id=assessment_id,
            child_id=child_id,
            assessment_type="initial",
            summary=f"档案导入 - {name}",
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"source": "profile_import"}
        )
        
        await self.storage.create_assessment(assessment)
        
        # 创建关系
        await self.storage.create_relationship(
            from_id=child_id,
            from_label="Person",
            to_id=assessment_id,
            to_label="ChildAssessment",
            rel_type="接受评估"
        )
        
        return {
            "child_id": child_id,
            "assessment_id": assessment_id,
            "message": f"档案导入成功，已为 {name} 创建初始评估"
        }
    
    # ========== 基础读取 ==========
    
    async def get_child(self, child_id: str) -> Optional[Dict[str, Any]]:
        """获取孩子档案"""
        return await self.storage.get_person(child_id)
    
    async def get_child_stats(self, child_id: str) -> Dict[str, Any]:
        """获取孩子的统计数据"""
        return {
            "observation_count": 0,
            "game_session_count": 0,
            "assessment_count": 0,
            "last_activity": None
        }
    
    async def save_child(self, child: Person) -> str:
        """保存孩子档案"""
        validate_person(child)
        
        if child.person_type != "child":
            raise ValueError(f"person_type 必须是 'child'，当前是 '{child.person_type}'")
        
        if not child.person_id:
            child.person_id = f"child_{uuid.uuid4().hex[:12]}"
        
        if not child.created_at:
            child.created_at = datetime.now(timezone.utc).isoformat()
        
        await self.storage.create_person(child)
        return child.person_id
    
    async def get_behaviors(
        self,
        child_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """查询行为记录"""
        return await self.storage.get_behaviors_by_child(child_id, filters)
    
    async def save_object(self, obj: Object) -> str:
        """保存对象（玩具/物品）"""
        validate_object(obj)
        
        if not obj.object_id:
            obj.object_id = f"obj_{uuid.uuid4().hex[:12]}"
        
        return await self.storage.create_object(obj)
    
    async def get_objects(self, child_id: str) -> List[Dict[str, Any]]:
        """获取孩子相关的对象列表"""
        return await self.storage.get_objects_by_child(child_id)
    
    async def save_game(self, game: Dict[str, Any]) -> str:
        """保存游戏节点"""
        game_id = game.get("game_id", f"game_{uuid.uuid4().hex[:12]}")
        
        game_node = FloorTimeGame(
            game_id=game_id,
            child_id=game.get("child_id", ""),
            name=game.get("name", ""),
            description=game.get("description", ""),
            created_at=game.get("created_at", datetime.now(timezone.utc).isoformat()),
            status=game.get("status", "recommended"),
            design=game.get("design", {}),
            implementation=game.get("implementation", {})
        )
        
        await self.storage.create_game(game_node)
        return game_id
    
    async def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """获取单个游戏"""
        return await self.storage.get_game(game_id)
    
    async def get_recent_games(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取最近游戏列表"""
        return await self.storage.get_games_by_child(child_id, limit)
    
    async def save_assessment(
        self,
        child_id: str,
        assessment_type: str,
        analysis: Dict[str, Any],
        recommendations: Optional[Dict[str, Any]] = None
    ) -> str:
        """保存评估结果"""
        assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        assessment = ChildAssessment(
            assessment_id=assessment_id,
            child_id=child_id,
            assessment_type=assessment_type,
            summary=json.dumps(analysis, ensure_ascii=False),
            created_at=datetime.now(timezone.utc).isoformat(),
            metadata={"recommendations": recommendations or {}}
        )
        
        await self.storage.create_assessment(assessment)
        
        await self.storage.create_relationship(
            from_id=child_id,
            from_label="Person",
            to_id=assessment_id,
            to_label="ChildAssessment",
            rel_type="接受评估"
        )
        
        return assessment_id
    
    async def get_latest_assessment(
        self,
        child_id: str,
        assessment_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """获取最新评估"""
        return await self.storage.get_latest_assessment(child_id, assessment_type)
    
    async def get_assessment_history(
        self,
        child_id: str,
        assessment_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取评估历史"""
        return await self.storage.get_assessment_history(child_id, assessment_type, limit)
    
    # 兴趣和功能维度的便捷方法
    
    async def save_interest(self, interest: Dict[str, Any]) -> str:
        """保存兴趣评估快照"""
        child_id = interest.get("child_id")
        if not child_id:
            raise ValueError("缺少 child_id")
        
        return await self.save_assessment(
            child_id=child_id,
            assessment_type="interest_mining",
            analysis=interest,
            recommendations=interest.get("recommendations", {})
        )
    
    async def get_latest_interest(self, child_id: str) -> Optional[Dict[str, Any]]:
        """获取最新兴趣评估"""
        return await self.get_latest_assessment(child_id, "interest_mining")
    
    async def get_interest_history(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取兴趣评估历史"""
        return await self.get_assessment_history(child_id, "interest_mining", limit)
    
    async def save_function(self, func: Dict[str, Any]) -> str:
        """保存功能评估快照"""
        child_id = func.get("child_id")
        if not child_id:
            raise ValueError("缺少 child_id")
        
        return await self.save_assessment(
            child_id=child_id,
            assessment_type="trend_analysis",
            analysis=func,
            recommendations=func.get("recommendations", {})
        )
    
    async def get_latest_function(self, child_id: str) -> Optional[Dict[str, Any]]:
        """获取最新功能评估"""
        return await self.get_latest_assessment(child_id, "trend_analysis")
    
    async def get_function_history(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取功能评估历史"""
        return await self.get_assessment_history(child_id, "trend_analysis", limit)


# 全局单例
_memory_service_instance = None


async def get_memory_service() -> MemoryService:
    """获取 Memory 服务单例"""
    global _memory_service_instance
    
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService()
        await _memory_service_instance.initialize()
    
    return _memory_service_instance
