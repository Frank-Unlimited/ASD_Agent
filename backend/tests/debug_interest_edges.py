"""
调试脚本：检查 InterestDimension 的边
"""
import asyncio
from services.Memory.service import MemoryService


async def main():
    service = MemoryService()
    await service.initialize()
    
    child_id = "test_child_llm_001"
    
    # 1. 查询所有边类型
    print("=" * 60)
    print("1. 查询 Behavior -> InterestDimension 的所有边类型")
    print("=" * 60)
    
    query1 = """
    MATCH (b:Entity:Behavior {group_id: $child_id})-[r]->(i:Entity:InterestDimension)
    RETURN type(r) as edge_type, count(*) as count
    """
    
    result1 = await service.storage.execute_query(query1, {"child_id": child_id})
    if result1:
        for row in result1:
            print(f"  - {row['edge_type']}: {row['count']} 条")
    else:
        print("  ❌ 没有找到任何边")
    
    # 2. 查询 Episodic -> InterestDimension 的边
    print("\n" + "=" * 60)
    print("2. 查询 Episodic -> InterestDimension 的边")
    print("=" * 60)
    
    query2 = """
    MATCH (e:Episodic {group_id: $child_id})-[r]->(i:Entity:InterestDimension)
    RETURN type(r) as edge_type, count(*) as count
    """
    
    result2 = await service.storage.execute_query(query2, {"child_id": child_id})
    if result2:
        for row in result2:
            print(f"  - {row['edge_type']}: {row['count']} 条")
    else:
        print("  ❌ 没有找到任何边")
    
    # 3. 查询所有与 InterestDimension 相关的边
    print("\n" + "=" * 60)
    print("3. 查询所有与 InterestDimension 相关的边")
    print("=" * 60)
    
    query3 = """
    MATCH (n {group_id: $child_id})-[r]->(i:Entity:InterestDimension)
    RETURN labels(n) as from_labels, type(r) as edge_type, 
           i.dimension_id as dimension, properties(r) as props
    """
    
    result3 = await service.storage.execute_query(query3, {"child_id": child_id})
    if result3:
        for row in result3:
            print(f"\n  {row['from_labels']} --[{row['edge_type']}]--> {row['dimension']}")
            print(f"    边属性: {row['props']}")
    else:
        print("  ❌ 没有找到任何边")
    
    # 4. 检查 edge_type_map 配置
    print("\n" + "=" * 60)
    print("4. 当前 edge_type_map 配置")
    print("=" * 60)
    print("  在 record_behavior() 中定义的边类型映射:")
    print("  - ('Behavior', 'InterestDimension'): ['体现兴趣']")
    
    await service.close()


if __name__ == "__main__":
    asyncio.run(main())
