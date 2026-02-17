"""
索引管理器 - 重构版
管理唯一约束和索引
"""
from neo4j import AsyncDriver


class IndexManager:
    """Neo4j 索引和约束管理"""
    
    def __init__(self, driver: AsyncDriver):
        """
        初始化索引管理器
        
        Args:
            driver: Neo4j driver
        """
        self.driver = driver
    
    async def create_constraints_and_indexes(self) -> None:
        """
        创建所有必要的唯一约束和索引
        
        注意：在Memory架构中，大部分节点由Memory服务管理
        这里只创建固定节点（InterestDimension）的约束
        """
        # 唯一约束（自动创建索引）
        constraints = [
            # InterestDimension 节点唯一约束（8个固定维度）
            "CREATE CONSTRAINT interest_dimension_unique IF NOT EXISTS FOR (i:InterestDimension) REQUIRE i.dimension IS UNIQUE",
        ]
        
        # 额外的索引（用于查询优化）
        indexes = [
            # Entity 节点索引（供参考）
            # - Entity.uuid
            # - Entity.name
            # - Entity.group_id
            # - Episodic.uuid
            # - Episodic.group_id
            
            # 注意：Neo4j 不支持在索引创建时使用 WHERE 子句
            # 如果需要特定类型的索引，应该使用标签（如 :Behavior）
        ]
        
        async with self.driver.session() as session:
            # 创建唯一约束
            print("[IndexManager] 创建唯一约束...")
            for constraint_query in constraints:
                try:
                    await session.run(constraint_query)
                    constraint_name = constraint_query.split("FOR")[1].split("REQUIRE")[0].strip()
                    print(f"  OK {constraint_name}")
                except Exception as e:
                    print(f"  FAIL constraint: {str(e)[:100]}")
            
            # 创建索引
            print("\n[IndexManager] 创建索引...")
            for index_query in indexes:
                try:
                    await session.run(index_query)
                    index_name = index_query.split("FOR")[1].split("ON")[0].strip()
                    print(f"  ✓ {index_name}")
                except Exception as e:
                    print(f"  ✗ 索引创建失败: {str(e)[:100]}")
        
        print("\n[IndexManager] 所有约束和索引创建完成")
    
    async def drop_all_constraints_and_indexes(self) -> None:
        """删除所有约束和索引（谨慎使用）"""
        async with self.driver.session() as session:
            # 删除所有约束
            print("[IndexManager] 删除所有约束...")
            result = await session.run("SHOW CONSTRAINTS")
            constraints = await result.data()
            
            for constraint in constraints:
                constraint_name = constraint.get("name")
                if constraint_name:
                    drop_query = f"DROP CONSTRAINT {constraint_name} IF EXISTS"
                    try:
                        await session.run(drop_query)
                        print(f"  ✓ 删除约束: {constraint_name}")
                    except Exception as e:
                        print(f"  ✗ 删除约束失败: {e}")
            
            # 删除所有索引
            print("\n[IndexManager] 删除所有索引...")
            result = await session.run("SHOW INDEXES")
            indexes = await result.data()
            
            for index in indexes:
                index_name = index.get("name")
                # 跳过由约束自动创建的索引（已经被删除）
                if index_name and not index_name.endswith("_unique"):
                    drop_query = f"DROP INDEX {index_name} IF EXISTS"
                    try:
                        await session.run(drop_query)
                        print(f"  ✓ 删除索引: {index_name}")
                    except Exception as e:
                        print(f"  ✗ 删除索引失败: {e}")
        
        print("\n[IndexManager] 所有约束和索引已删除")
    
    async def show_constraints_and_indexes(self) -> None:
        """显示当前所有约束和索引"""
        async with self.driver.session() as session:
            # 显示约束
            print("[IndexManager] 当前约束:")
            result = await session.run("SHOW CONSTRAINTS")
            constraints = await result.data()
            
            if constraints:
                for constraint in constraints:
                    print(f"  - {constraint.get('name')}: {constraint.get('type')}")
            else:
                print("  (无)")
            
            # 显示索引
            print("\n[IndexManager] 当前索引:")
            result = await session.run("SHOW INDEXES")
            indexes = await result.data()
            
            if indexes:
                for index in indexes:
                    print(f"  - {index.get('name')}: {index.get('type')}")
            else:
                print("  (无)")

