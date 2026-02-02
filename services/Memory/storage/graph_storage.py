"""
图存储操作 - 重构版
基于记忆驱动架构的图数据库操作
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from neo4j import AsyncGraphDatabase, AsyncDriver
import uuid
import json

from ..models.nodes import Person, Behavior, Object, InterestDimension, FunctionDimension, FloorTimeGame, ChildAssessment
from ..models.edges import EdgeType
from ..models.dimensions import get_all_interest_names, get_all_function_names, INTEREST_DIMENSIONS, FUNCTION_DIMENSIONS
from ..utils.query_builder import QueryBuilder
from .index_manager import IndexManager


class GraphStorage:
    """图存储管理器 - 重构版"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        初始化图存储
        
        Args:
            uri: Neo4j URI
            user: 用户名
            password: 密码
        """
        self.driver: AsyncDriver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        self.query_builder = QueryBuilder()
        self.index_manager = IndexManager(self.driver)
        print(f"[GraphStorage] 已连接到 Neo4j: {uri}")
    
    async def close(self):
        """关闭连接"""
        await self.driver.close()
        print("[GraphStorage] 连接已关闭")
    
    # ============ 初始化固定节点 ============
    
    async def initialize_fixed_nodes(self):
        """
        初始化固定节点
        - 8个兴趣维度节点
        - 33个功能维度节点
        - 创建唯一约束和索引
        """
        # 先创建约束和索引
        await self.index_manager.create_constraints_and_indexes()
        
        async with self.driver.session() as session:
            # 创建8个兴趣维度节点
            for interest_name in get_all_interest_names():
                config = INTEREST_DIMENSIONS[interest_name]
                query = """
                MERGE (i:InterestDimension {interest_id: $interest_id})
                ON CREATE SET i.name = $name,
                              i.display_name = $display_name,
                              i.description = $description
                """
                await session.run(query,
                    interest_id=f"interest_{interest_name}",
                    name=interest_name,
                    display_name=config["display_name"],
                    description=config["description"]
                )
            
            # 创建33个功能维度节点
            for function_name in get_all_function_names():
                config = FUNCTION_DIMENSIONS[function_name]
                query = """
                MERGE (f:FunctionDimension {function_id: $function_id})
                ON CREATE SET f.name = $name,
                              f.display_name = $display_name,
                              f.category = $category,
                              f.description = $description
                """
                await session.run(query,
                    function_id=f"function_{function_name}",
                    name=function_name,
                    display_name=config["display_name"],
                    category=config["category"],
                    description=config["description"]
                )
            
            print("[GraphStorage] 固定节点初始化完成")
    
    # ============ Person 节点操作 ============
    
    async def create_person(self, person: Person) -> str:
        """
        创建人物节点（使用 MERGE 避免重复）
        
        如果 person_id 已存在，则更新属性；否则创建新节点
        """
        query = """
        MERGE (p:Person {person_id: $person_id})
        ON CREATE SET p.person_type = $person_type,
                      p.name = $name,
                      p.role = $role,
                      p.basic_info = $basic_info,
                      p.created_at = $created_at
        ON MATCH SET p.name = $name,
                     p.role = $role,
                     p.basic_info = $basic_info
        RETURN p.person_id as person_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                person_id=person.person_id,
                person_type=person.person_type,
                name=person.name,
                role=person.role,
                basic_info=json.dumps(person.basic_info),  # 序列化为 JSON 字符串
                created_at=person.created_at or datetime.now(timezone.utc).isoformat()
            )
            record = await result.single()
            return record["person_id"] if record else person.person_id
    
    async def get_person(self, person_id: str) -> Optional[Dict[str, Any]]:
        """获取人物节点"""
        query = "MATCH (p:Person {person_id: $person_id}) RETURN p"
        
        async with self.driver.session() as session:
            result = await session.run(query, person_id=person_id)
            record = await result.single()
            return dict(record["p"]) if record else None
    
    async def update_person(self, person_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新人物节点属性
        
        Args:
            person_id: 人物ID
            updates: 要更新的属性字典（如 {"name": "新名字", "basic_info": {...}}）
        
        Returns:
            是否更新成功
        """
        if not updates:
            return False
        
        # 构建SET子句
        set_clauses = []
        params = {"person_id": person_id}
        
        for key, value in updates.items():
            if key == "basic_info":
                # basic_info需要序列化为JSON
                set_clauses.append(f"p.{key} = $param_{key}")
                params[f"param_{key}"] = json.dumps(value)
            else:
                set_clauses.append(f"p.{key} = $param_{key}")
                params[f"param_{key}"] = value
        
        query = f"""
        MATCH (p:Person {{person_id: $person_id}})
        SET {', '.join(set_clauses)}
        RETURN p.person_id as person_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            return record is not None
    
    # ============ Behavior 节点操作 ============
    
    async def create_behavior(self, behavior: Behavior) -> str:
        """
        创建行为节点（使用 MERGE 避免重复）
        
        如果 behavior_id 已存在，则更新属性；否则创建新节点
        """
        query = """
        MERGE (b:Behavior {behavior_id: $behavior_id})
        ON CREATE SET b.child_id = $child_id,
                      b.timestamp = $timestamp,
                      b.event_type = $event_type,
                      b.description = $description,
                      b.raw_input = $raw_input,
                      b.input_type = $input_type,
                      b.significance = $significance,
                      b.ai_analysis = $ai_analysis,
                      b.context = $context,
                      b.evidence = $evidence
        ON MATCH SET b.description = $description,
                     b.significance = $significance,
                     b.ai_analysis = $ai_analysis,
                     b.context = $context,
                     b.evidence = $evidence
        RETURN b.behavior_id as behavior_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                behavior_id=behavior.behavior_id,
                child_id=behavior.child_id,
                timestamp=behavior.timestamp,
                event_type=behavior.event_type,
                description=behavior.description,
                raw_input=behavior.raw_input,
                input_type=behavior.input_type,
                significance=behavior.significance,
                ai_analysis=json.dumps(behavior.ai_analysis),  # 序列化为 JSON 字符串
                context=json.dumps(behavior.context),  # 序列化为 JSON 字符串
                evidence=json.dumps(behavior.evidence)  # 序列化为 JSON 字符串
            )
            record = await result.single()
            return record["behavior_id"] if record else behavior.behavior_id
    
    async def get_behavior(self, behavior_id: str) -> Optional[Dict[str, Any]]:
        """获取单个行为节点"""
        query = "MATCH (b:Behavior {behavior_id: $behavior_id}) RETURN b"
        
        async with self.driver.session() as session:
            result = await session.run(query, behavior_id=behavior_id)
            record = await result.single()
            return dict(record["b"]) if record else None
    
    async def get_behaviors(
        self,
        child_id: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """获取行为记录"""
        conditions = []
        params = {}
        
        if child_id:
            conditions.append("b.child_id = $child_id")
            params["child_id"] = child_id
        
        if start_time:
            conditions.append("b.timestamp >= $start_time")
            params["start_time"] = start_time
        
        if end_time:
            conditions.append("b.timestamp <= $end_time")
            params["end_time"] = end_time
        
        where_clause = " AND ".join(conditions) if conditions else "true"
        
        query = f"""
        MATCH (b:Behavior)
        WHERE {where_clause}
        RETURN b
        ORDER BY b.timestamp DESC
        LIMIT {limit}
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            records = await result.data()
            return [dict(record["b"]) for record in records]
    
    # ============ Object 节点操作 ============
    
    async def create_object(self, obj: Object) -> str:
        """
        创建对象节点（使用 MERGE 避免重复）
        
        如果 object_id 已存在，则更新属性；否则创建新节点
        """
        query = """
        MERGE (o:Object {object_id: $object_id})
        ON CREATE SET o.name = $name,
                      o.description = $description,
                      o.tags = $tags,
                      o.usage = $usage
        ON MATCH SET o.name = $name,
                     o.description = $description,
                     o.tags = $tags,
                     o.usage = $usage
        RETURN o.object_id as object_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                object_id=obj.object_id,
                name=obj.name,
                description=obj.description,
                tags=obj.tags,  # 列表可以直接存储
                usage=json.dumps(obj.usage)  # 序列化为 JSON 字符串
            )
            record = await result.single()
            return record["object_id"] if record else obj.object_id
    
    async def get_object(self, object_id: str) -> Optional[Dict[str, Any]]:
        """获取对象节点"""
        query = "MATCH (o:Object {object_id: $object_id}) RETURN o"
        
        async with self.driver.session() as session:
            result = await session.run(query, object_id=object_id)
            record = await result.single()
            return dict(record["o"]) if record else None
    
    async def get_objects_by_child(
        self,
        child_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取孩子相关的对象列表
        
        通过关系图谱查询：孩子 -> 行为 -> 对象
        """
        query = """
        MATCH (p:Person {person_id: $child_id})-[:展现]->(b:Behavior)-[:涉及对象]->(o:Object)
        RETURN DISTINCT o
        LIMIT $limit
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, child_id=child_id, limit=limit)
            records = await result.data()
            return [dict(record["o"]) for record in records]
    
    # ============ 关系操作 ============
    
    async def create_relationship(
        self,
        from_id: str,
        from_label: str,
        to_id: str,
        to_label: str,
        rel_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        创建关系
        
        Args:
            from_id: 起始节点ID
            from_label: 起始节点标签
            to_id: 目标节点ID
            to_label: 目标节点标签
            rel_type: 关系类型
            properties: 关系属性
            
        Returns:
            是否成功
        """
        # 根据节点标签确定 ID 字段名
        id_field_map = {
            "Person": "person_id",
            "Behavior": "behavior_id",
            "Object": "object_id",
            "InterestDimension": "interest_id",
            "FunctionDimension": "function_id",
            "FloorTimeGame": "game_id",
            "ChildAssessment": "assessment_id"
        }
        
        from_id_field = id_field_map.get(from_label, f"{from_label.lower()}_id")
        to_id_field = id_field_map.get(to_label, f"{to_label.lower()}_id")
        
        # 构建属性字符串
        props_str = ""
        if properties:
            props_list = [f"{k}: ${k}" for k in properties.keys()]
            props_str = "{" + ", ".join(props_list) + "}"
        
        query = f"""
        MATCH (from:{from_label})
        WHERE from.{from_id_field} = $from_id
        MATCH (to:{to_label})
        WHERE to.{to_id_field} = $to_id
        MERGE (from)-[r:`{rel_type}` {props_str}]->(to)
        RETURN r
        """
        
        params = {"from_id": from_id, "to_id": to_id}
        if properties:
            params.update(properties)
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            return record is not None
    
    # ============ 辅助方法 ============
    
    async def clear_all_data(self):
        """清空所有数据（谨慎使用）"""
        query = "MATCH (n) DETACH DELETE n"
        
        async with self.driver.session() as session:
            await session.run(query)
            print("[GraphStorage] 所有数据已清空")
    
    async def clear_child_data(self, child_id: str):
        """清空某个孩子的所有数据"""
        query = """
        MATCH (n)
        WHERE n.child_id = $child_id
        DETACH DELETE n
        """
        
        async with self.driver.session() as session:
            await session.run(query, child_id=child_id)
            print(f"[GraphStorage] 已清空孩子 {child_id} 的所有数据")
    
    # ============ ChildAssessment 节点操作 ============
    
    async def create_assessment(self, assessment: ChildAssessment) -> str:
        """
        创建评估节点（使用 MERGE 避免重复）
        
        Args:
            assessment: 评估节点对象
            
        Returns:
            assessment_id
        """
        query = """
        MERGE (a:ChildAssessment {assessment_id: $assessment_id})
        ON CREATE SET a.child_id = $child_id,
                      a.assessor_id = $assessor_id,
                      a.timestamp = $timestamp,
                      a.assessment_type = $assessment_type,
                      a.analysis = $analysis,
                      a.recommendations = $recommendations
        ON MATCH SET a.analysis = $analysis,
                     a.recommendations = $recommendations
        RETURN a.assessment_id as assessment_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                assessment_id=assessment.assessment_id,
                child_id=assessment.child_id,
                assessor_id=assessment.assessor_id,
                timestamp=assessment.timestamp,
                assessment_type=assessment.assessment_type,
                analysis=json.dumps(assessment.analysis, ensure_ascii=False),
                recommendations=json.dumps(assessment.recommendations, ensure_ascii=False)
            )
            record = await result.single()
            return record["assessment_id"]
    
    async def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """
        获取评估节点
        
        Args:
            assessment_id: 评估ID
            
        Returns:
            评估数据字典，如果不存在则返回 None
        """
        query = """
        MATCH (a:ChildAssessment {assessment_id: $assessment_id})
        RETURN a
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, assessment_id=assessment_id)
            record = await result.single()
            
            if record:
                node = record["a"]
                data = dict(node)
                
                # 解析 JSON 字段
                if "analysis" in data and isinstance(data["analysis"], str):
                    try:
                        data["analysis"] = json.loads(data["analysis"])
                    except:
                        pass
                
                if "recommendations" in data and isinstance(data["recommendations"], str):
                    try:
                        data["recommendations"] = json.loads(data["recommendations"])
                    except:
                        pass
                
                return data
            
            return None
    
    async def get_assessments_by_child(
        self,
        child_id: str,
        assessment_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取孩子的评估历史
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            limit: 返回数量限制
            
        Returns:
            评估列表（按时间倒序）
        """
        if assessment_type:
            query = """
            MATCH (a:ChildAssessment {child_id: $child_id, assessment_type: $assessment_type})
            RETURN a
            ORDER BY a.timestamp DESC
            LIMIT $limit
            """
            params = {
                "child_id": child_id,
                "assessment_type": assessment_type,
                "limit": limit
            }
        else:
            query = """
            MATCH (a:ChildAssessment {child_id: $child_id})
            RETURN a
            ORDER BY a.timestamp DESC
            LIMIT $limit
            """
            params = {
                "child_id": child_id,
                "limit": limit
            }
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            records = await result.data()
            
            assessments = []
            for record in records:
                node = record["a"]
                data = dict(node)
                
                # 解析 JSON 字段
                if "analysis" in data and isinstance(data["analysis"], str):
                    try:
                        data["analysis"] = json.loads(data["analysis"])
                    except:
                        pass
                
                if "recommendations" in data and isinstance(data["recommendations"], str):
                    try:
                        data["recommendations"] = json.loads(data["recommendations"])
                    except:
                        pass
                
                assessments.append(data)
            
            return assessments
    
    async def get_latest_assessment(
        self,
        child_id: str,
        assessment_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取最新的评估
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            
        Returns:
            最新评估数据，如果不存在则返回 None
        """
        assessments = await self.get_assessments_by_child(
            child_id=child_id,
            assessment_type=assessment_type,
            limit=1
        )
        
        return assessments[0] if assessments else None


    # ============ FloorTimeGame 节点操作 ============
    
    async def create_game(self, game: FloorTimeGame) -> str:
        """
        创建游戏节点（使用 MERGE 避免重复）
        
        Args:
            game: 游戏节点对象
            
        Returns:
            game_id
        """
        query = """
        MERGE (g:FloorTimeGame {game_id: $game_id})
        ON CREATE SET g.child_id = $child_id,
                      g.name = $name,
                      g.description = $description,
                      g.created_at = $created_at,
                      g.status = $status,
                      g.design = $design,
                      g.implementation = $implementation
        ON MATCH SET g.name = $name,
                     g.description = $description,
                     g.status = $status,
                     g.design = $design,
                     g.implementation = $implementation
        RETURN g.game_id as game_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                game_id=game.game_id,
                child_id=game.child_id,
                name=game.name,
                description=game.description,
                created_at=game.created_at,
                status=game.status,
                design=json.dumps(game.design, ensure_ascii=False),
                implementation=json.dumps(game.implementation, ensure_ascii=False)
            )
            record = await result.single()
            return record["game_id"]
    
    async def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取游戏节点
        
        Args:
            game_id: 游戏ID
            
        Returns:
            游戏数据字典，如果不存在则返回 None
        """
        query = """
        MATCH (g:FloorTimeGame {game_id: $game_id})
        RETURN g
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, game_id=game_id)
            record = await result.single()
            
            if record:
                node = record["g"]
                data = dict(node)
                
                # 解析 JSON 字段
                if "design" in data and isinstance(data["design"], str):
                    try:
                        data["design"] = json.loads(data["design"])
                    except:
                        pass
                
                if "implementation" in data and isinstance(data["implementation"], str):
                    try:
                        data["implementation"] = json.loads(data["implementation"])
                    except:
                        pass
                
                return data
            
            return None
    
    async def get_games_by_child(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取孩子的游戏列表
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
            
        Returns:
            游戏列表（按创建时间倒序）
        """
        query = """
        MATCH (g:FloorTimeGame {child_id: $child_id})
        RETURN g
        ORDER BY g.created_at DESC
        LIMIT $limit
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, child_id=child_id, limit=limit)
            records = await result.data()
            
            games = []
            for record in records:
                node = record["g"]
                data = dict(node)
                
                # 解析 JSON 字段
                if "design" in data and isinstance(data["design"], str):
                    try:
                        data["design"] = json.loads(data["design"])
                    except:
                        pass
                
                if "implementation" in data and isinstance(data["implementation"], str):
                    try:
                        data["implementation"] = json.loads(data["implementation"])
                    except:
                        pass
                
                games.append(data)
            
            return games
    
    async def update_game(
        self,
        game_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        更新游戏节点
        
        Args:
            game_id: 游戏ID
            updates: 要更新的字段（字典）
            
        Returns:
            是否成功
        """
        # 构建 SET 子句
        set_clauses = []
        params = {"game_id": game_id}
        
        for key, value in updates.items():
            if key in ["design", "implementation"]:
                # JSON 字段需要序列化
                params[key] = json.dumps(value, ensure_ascii=False)
            else:
                params[key] = value
            set_clauses.append(f"g.{key} = ${key}")
        
        if not set_clauses:
            return False
        
        query = f"""
        MATCH (g:FloorTimeGame {{game_id: $game_id}})
        SET {", ".join(set_clauses)}
        RETURN g
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            record = await result.single()
            return record is not None
