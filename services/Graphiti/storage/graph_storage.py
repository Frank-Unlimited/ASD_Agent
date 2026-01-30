"""
图存储操作
直接操作 Neo4j 数据库
"""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from neo4j import AsyncGraphDatabase, AsyncDriver
import uuid

from ..models.nodes import Child, Dimension, Observation, Milestone
from ..models.edges import EdgeType
from ..models.dimensions import get_dimension_config, get_display_name


class GraphStorage:
    """图存储管理器"""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        初始化图存储
        
        Args:
            uri: Neo4j URI
            user: 用户名
            password: 密码
        """
        self.driver: AsyncDriver = AsyncGraphDatabase.driver(uri, auth=(user, password))
        print(f"[GraphStorage] 已连接到 Neo4j: {uri}")
    
    async def close(self):
        """关闭连接"""
        await self.driver.close()
        print("[GraphStorage] 连接已关闭")
    
    # ============ Child 节点操作 ============
    
    async def ensure_child_node(self, child_id: str, name: str = "") -> None:
        """
        确保 Child 节点存在
        
        Args:
            child_id: 孩子ID
            name: 孩子姓名
        """
        query = """
        MERGE (c:Child {child_id: $child_id})
        ON CREATE SET c.name = $name,
                      c.created_at = datetime()
        ON MATCH SET c.name = CASE WHEN $name <> '' THEN $name ELSE c.name END
        RETURN c
        """
        
        async with self.driver.session() as session:
            await session.run(query, child_id=child_id, name=name)
    
    # ============ Dimension 节点操作 ============
    
    async def ensure_dimension_node(self, child_id: str, dimension: str) -> None:
        """
        确保 Dimension 节点存在，并建立 HAS_DIMENSION 边
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
        """
        config = get_dimension_config(dimension)
        if not config:
            print(f"[GraphStorage] 警告：未知维度 {dimension}")
            config = {
                "display_name": dimension,
                "category": "behavior",
                "description": ""
            }
        
        dimension_id = f"{child_id}_{dimension}"
        
        query = """
        MATCH (c:Child {child_id: $child_id})
        MERGE (d:Dimension {dimension_id: $dimension_id})
        ON CREATE SET d.child_id = $child_id,
                      d.name = $dimension,
                      d.display_name = $display_name,
                      d.category = $category,
                      d.description = $description
        MERGE (c)-[r:HAS_DIMENSION]->(d)
        ON CREATE SET r.created_at = datetime()
        RETURN d
        """
        
        async with self.driver.session() as session:
            await session.run(query, 
                child_id=child_id,
                dimension_id=dimension_id,
                dimension=dimension,
                display_name=config.get("display_name", dimension),
                category=config.get("category", "behavior"),
                description=config.get("description", "")
            )
    
    async def set_baseline(self, child_id: str, dimension: str, value: float, date: str) -> None:
        """
        设置维度的基线值
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            value: 基线值
            date: 基线日期
        """
        dimension_id = f"{child_id}_{dimension}"
        
        query = """
        MATCH (d:Dimension {dimension_id: $dimension_id})
        SET d.baseline_value = $value,
            d.baseline_date = $date
        RETURN d
        """
        
        async with self.driver.session() as session:
            await session.run(query, dimension_id=dimension_id, value=value, date=date)
    
    # ============ Observation 节点操作 ============
    
    async def create_observation_node(
        self,
        child_id: str,
        dimension: str,
        value: float,
        value_type: str,
        timestamp: str,
        source: str,
        context: Optional[str] = None,
        confidence: float = 0.8,
        session_id: Optional[str] = None
    ) -> str:
        """
        创建 Observation 节点并建立 HAS_OBSERVATION 边
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            value: 观察值
            value_type: 值类型
            timestamp: 时间戳
            source: 数据来源
            context: 上下文描述
            confidence: 置信度
            session_id: 会话ID
            
        Returns:
            observation_id: 观察记录ID
        """
        observation_id = f"obs-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        dimension_id = f"{child_id}_{dimension}"
        
        query = """
        MATCH (d:Dimension {dimension_id: $dimension_id})
        CREATE (o:Observation {
            observation_id: $observation_id,
            child_id: $child_id,
            dimension: $dimension,
            value: $value,
            value_type: $value_type,
            timestamp: $timestamp,
            source: $source,
            context: $context,
            confidence: $confidence,
            session_id: $session_id
        })
        CREATE (d)-[r:HAS_OBSERVATION]->(o)
        RETURN o.observation_id as observation_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                observation_id=observation_id,
                dimension_id=dimension_id,
                child_id=child_id,
                dimension=dimension,
                value=value,
                value_type=value_type,
                timestamp=timestamp,
                source=source,
                context=context,
                confidence=confidence,
                session_id=session_id
            )
            record = await result.single()
            return record["observation_id"] if record else observation_id
    
    async def get_observations(
        self,
        child_id: str,
        dimension: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取观察记录
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称（可选）
            start_time: 开始时间（可选）
            end_time: 结束时间（可选）
            limit: 限制数量（可选）
            
        Returns:
            观察记录列表
        """
        # 构建查询条件
        where_clauses = ["o.child_id = $child_id"]
        params = {"child_id": child_id}
        
        if dimension:
            where_clauses.append("o.dimension = $dimension")
            params["dimension"] = dimension
        
        if start_time:
            where_clauses.append("o.timestamp >= $start_time")
            params["start_time"] = start_time
        
        if end_time:
            where_clauses.append("o.timestamp <= $end_time")
            params["end_time"] = end_time
        
        where_clause = " AND ".join(where_clauses)
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        MATCH (o:Observation)
        WHERE {where_clause}
        RETURN o
        ORDER BY o.timestamp DESC
        {limit_clause}
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            records = await result.data()
            return [record["o"] for record in records]
    
    # ============ Milestone 节点操作 ============
    
    async def create_milestone_node(
        self,
        child_id: str,
        dimension: str,
        milestone_type: str,
        description: str,
        timestamp: str,
        significance: str = "high",
        observation_id: Optional[str] = None
    ) -> str:
        """
        创建 Milestone 节点
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称
            milestone_type: 里程碑类型
            description: 描述
            timestamp: 时间戳
            significance: 重要性
            observation_id: 触发的观察ID（可选）
            
        Returns:
            milestone_id: 里程碑ID
        """
        milestone_id = f"mile-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:6]}"
        
        # 创建里程碑节点
        query = """
        CREATE (m:Milestone {
            milestone_id: $milestone_id,
            child_id: $child_id,
            dimension: $dimension,
            type: $type,
            description: $description,
            timestamp: $timestamp,
            significance: $significance
        })
        RETURN m.milestone_id as milestone_id
        """
        
        async with self.driver.session() as session:
            result = await session.run(query,
                milestone_id=milestone_id,
                child_id=child_id,
                dimension=dimension,
                type=milestone_type,
                description=description,
                timestamp=timestamp,
                significance=significance
            )
            record = await result.single()
            created_id = record["milestone_id"] if record else milestone_id
        
        # 如果有关联的观察，建立 TRIGGERS 边
        if observation_id:
            await self.create_triggers_edge(observation_id, created_id)
        
        return created_id
    
    async def get_milestones(
        self,
        child_id: str,
        dimension: Optional[str] = None,
        start_time: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取里程碑
        
        Args:
            child_id: 孩子ID
            dimension: 维度名称（可选）
            start_time: 开始时间（可选）
            limit: 限制数量（可选）
            
        Returns:
            里程碑列表
        """
        where_clauses = ["m.child_id = $child_id"]
        params = {"child_id": child_id}
        
        if dimension:
            where_clauses.append("m.dimension = $dimension")
            params["dimension"] = dimension
        
        if start_time:
            where_clauses.append("m.timestamp >= $start_time")
            params["start_time"] = start_time
        
        where_clause = " AND ".join(where_clauses)
        limit_clause = f"LIMIT {limit}" if limit else ""
        
        query = f"""
        MATCH (m:Milestone)
        WHERE {where_clause}
        RETURN m
        ORDER BY m.timestamp DESC
        {limit_clause}
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, **params)
            records = await result.data()
            return [record["m"] for record in records]
    
    # ============ 边操作 ============
    
    async def create_triggers_edge(self, observation_id: str, milestone_id: str) -> None:
        """
        创建 TRIGGERS 边（Observation -> Milestone）
        
        Args:
            observation_id: 观察ID
            milestone_id: 里程碑ID
        """
        query = """
        MATCH (o:Observation {observation_id: $observation_id})
        MATCH (m:Milestone {milestone_id: $milestone_id})
        MERGE (o)-[r:TRIGGERS]->(m)
        RETURN r
        """
        
        async with self.driver.session() as session:
            await session.run(query, observation_id=observation_id, milestone_id=milestone_id)
    
    async def create_correlation_edge(
        self,
        child_id: str,
        dimension_a: str,
        dimension_b: str,
        correlation: float,
        lag_days: int,
        relationship: str,
        confidence: float,
        p_value: float
    ) -> None:
        """
        创建或更新 CORRELATES_WITH 边
        
        Args:
            child_id: 孩子ID
            dimension_a: 维度A
            dimension_b: 维度B
            correlation: 相关系数
            lag_days: 时滞天数
            relationship: 关系描述
            confidence: 置信度
            p_value: p值
        """
        dim_a_id = f"{child_id}_{dimension_a}"
        dim_b_id = f"{child_id}_{dimension_b}"
        
        query = """
        MATCH (d1:Dimension {dimension_id: $dim_a_id})
        MATCH (d2:Dimension {dimension_id: $dim_b_id})
        MERGE (d1)-[r:CORRELATES_WITH]->(d2)
        SET r.correlation = $correlation,
            r.lag_days = $lag_days,
            r.relationship = $relationship,
            r.confidence = $confidence,
            r.p_value = $p_value,
            r.updated_at = datetime()
        RETURN r
        """
        
        async with self.driver.session() as session:
            await session.run(query,
                dim_a_id=dim_a_id,
                dim_b_id=dim_b_id,
                correlation=correlation,
                lag_days=lag_days,
                relationship=relationship,
                confidence=confidence,
                p_value=p_value
            )
    
    async def get_correlations(
        self,
        child_id: str,
        min_correlation: float = 0.3
    ) -> List[Dict[str, Any]]:
        """
        获取维度关联
        
        Args:
            child_id: 孩子ID
            min_correlation: 最小相关系数
            
        Returns:
            关联列表
        """
        query = """
        MATCH (d1:Dimension {child_id: $child_id})-[r:CORRELATES_WITH]->(d2:Dimension {child_id: $child_id})
        WHERE abs(r.correlation) >= $min_correlation
        RETURN d1.name as dimension_a,
               d2.name as dimension_b,
               r.correlation as correlation,
               r.lag_days as lag_days,
               r.relationship as relationship,
               r.confidence as confidence,
               r.p_value as p_value
        ORDER BY abs(r.correlation) DESC
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, child_id=child_id, min_correlation=min_correlation)
            records = await result.data()
            return records
    
    # ============ 辅助方法 ============
    
    async def get_child_dimensions(self, child_id: str) -> List[str]:
        """
        获取孩子的所有维度
        
        Args:
            child_id: 孩子ID
            
        Returns:
            维度名称列表
        """
        query = """
        MATCH (d:Dimension {child_id: $child_id})
        RETURN d.name as dimension
        ORDER BY d.name
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, child_id=child_id)
            records = await result.data()
            return [record["dimension"] for record in records]
    
    async def clear_child_data(self, child_id: str) -> None:
        """
        清空孩子的所有数据
        
        Args:
            child_id: 孩子ID
        """
        query = """
        MATCH (n)
        WHERE n.child_id = $child_id
        DETACH DELETE n
        """
        
        async with self.driver.session() as session:
            await session.run(query, child_id=child_id)
            print(f"[GraphStorage] 已清空孩子 {child_id} 的所有数据")
