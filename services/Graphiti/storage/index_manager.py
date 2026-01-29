"""
索引管理器
"""
from neo4j import AsyncDriver


class IndexManager:
    """Neo4j 索引管理"""
    
    def __init__(self, driver: AsyncDriver):
        """
        初始化索引管理器
        
        Args:
            driver: Neo4j driver
        """
        self.driver = driver
    
    async def create_indexes(self) -> None:
        """创建所有必要的索引"""
        indexes = [
            # Child 节点索引
            "CREATE INDEX child_id_index IF NOT EXISTS FOR (c:Child) ON (c.child_id)",
            
            # Dimension 节点索引
            "CREATE INDEX dimension_id_index IF NOT EXISTS FOR (d:Dimension) ON (d.dimension_id)",
            "CREATE INDEX dimension_child_index IF NOT EXISTS FOR (d:Dimension) ON (d.child_id, d.name)",
            
            # Observation 节点索引
            "CREATE INDEX observation_id_index IF NOT EXISTS FOR (o:Observation) ON (o.observation_id)",
            "CREATE INDEX observation_child_dim_index IF NOT EXISTS FOR (o:Observation) ON (o.child_id, o.dimension)",
            "CREATE INDEX observation_timestamp_index IF NOT EXISTS FOR (o:Observation) ON (o.timestamp)",
            
            # Milestone 节点索引
            "CREATE INDEX milestone_id_index IF NOT EXISTS FOR (m:Milestone) ON (m.milestone_id)",
            "CREATE INDEX milestone_child_index IF NOT EXISTS FOR (m:Milestone) ON (m.child_id)",
            "CREATE INDEX milestone_timestamp_index IF NOT EXISTS FOR (m:Milestone) ON (m.timestamp)",
        ]
        
        async with self.driver.session() as session:
            for index_query in indexes:
                try:
                    await session.run(index_query)
                    print(f"[IndexManager] 索引创建成功: {index_query[:50]}...")
                except Exception as e:
                    print(f"[IndexManager] 索引创建失败: {e}")
        
        print("[IndexManager] 所有索引创建完成")
    
    async def drop_all_indexes(self) -> None:
        """删除所有索引（谨慎使用）"""
        query = "SHOW INDEXES"
        
        async with self.driver.session() as session:
            result = await session.run(query)
            indexes = await result.data()
            
            for index in indexes:
                index_name = index.get("name")
                if index_name:
                    drop_query = f"DROP INDEX {index_name} IF EXISTS"
                    try:
                        await session.run(drop_query)
                        print(f"[IndexManager] 删除索引: {index_name}")
                    except Exception as e:
                        print(f"[IndexManager] 删除索引失败: {e}")
