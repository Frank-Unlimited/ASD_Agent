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
        
        约束会自动创建索引，所以先创建约束
        """
        # 唯一约束（自动创建索引）
        constraints = [
            # Person 节点唯一约束
            "CREATE CONSTRAINT person_id_unique IF NOT EXISTS FOR (p:Person) REQUIRE p.person_id IS UNIQUE",
            
            # Behavior 节点唯一约束
            "CREATE CONSTRAINT behavior_id_unique IF NOT EXISTS FOR (b:Behavior) REQUIRE b.behavior_id IS UNIQUE",
            
            # Object 节点唯一约束
            "CREATE CONSTRAINT object_id_unique IF NOT EXISTS FOR (o:Object) REQUIRE o.object_id IS UNIQUE",
            
            # InterestDimension 节点唯一约束
            "CREATE CONSTRAINT interest_id_unique IF NOT EXISTS FOR (i:InterestDimension) REQUIRE i.interest_id IS UNIQUE",
            
            # FunctionDimension 节点唯一约束
            "CREATE CONSTRAINT function_id_unique IF NOT EXISTS FOR (f:FunctionDimension) REQUIRE f.function_id IS UNIQUE",
            
            # FloorTimeGame 节点唯一约束
            "CREATE CONSTRAINT game_id_unique IF NOT EXISTS FOR (g:FloorTimeGame) REQUIRE g.game_id IS UNIQUE",
            
            # ChildAssessment 节点唯一约束
            "CREATE CONSTRAINT assessment_id_unique IF NOT EXISTS FOR (a:ChildAssessment) REQUIRE a.assessment_id IS UNIQUE",
        ]
        
        # 额外的索引（用于查询优化）
        indexes = [
            # Person 节点索引
            "CREATE INDEX person_type_index IF NOT EXISTS FOR (p:Person) ON (p.person_type)",
            
            # Behavior 节点索引
            "CREATE INDEX behavior_child_index IF NOT EXISTS FOR (b:Behavior) ON (b.child_id)",
            "CREATE INDEX behavior_timestamp_index IF NOT EXISTS FOR (b:Behavior) ON (b.timestamp)",
            "CREATE INDEX behavior_significance_index IF NOT EXISTS FOR (b:Behavior) ON (b.significance)",
            "CREATE INDEX behavior_child_time_index IF NOT EXISTS FOR (b:Behavior) ON (b.child_id, b.timestamp)",
            
            # Object 节点索引
            "CREATE INDEX object_name_index IF NOT EXISTS FOR (o:Object) ON (o.name)",
            
            # InterestDimension 节点索引
            "CREATE INDEX interest_name_index IF NOT EXISTS FOR (i:InterestDimension) ON (i.name)",
            
            # FunctionDimension 节点索引
            "CREATE INDEX function_name_index IF NOT EXISTS FOR (f:FunctionDimension) ON (f.name)",
            "CREATE INDEX function_category_index IF NOT EXISTS FOR (f:FunctionDimension) ON (f.category)",
            
            # FloorTimeGame 节点索引
            "CREATE INDEX game_child_index IF NOT EXISTS FOR (g:FloorTimeGame) ON (g.child_id)",
            "CREATE INDEX game_status_index IF NOT EXISTS FOR (g:FloorTimeGame) ON (g.status)",
            
            # ChildAssessment 节点索引
            "CREATE INDEX assessment_child_index IF NOT EXISTS FOR (a:ChildAssessment) ON (a.child_id)",
            "CREATE INDEX assessment_timestamp_index IF NOT EXISTS FOR (a:ChildAssessment) ON (a.timestamp)",
        ]
        
        async with self.driver.session() as session:
            # 创建唯一约束
            print("[IndexManager] 创建唯一约束...")
            for constraint_query in constraints:
                try:
                    await session.run(constraint_query)
                    constraint_name = constraint_query.split("FOR")[1].split("REQUIRE")[0].strip()
                    print(f"  ✓ {constraint_name}")
                except Exception as e:
                    print(f"  ✗ 约束创建失败: {str(e)[:100]}")
            
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

