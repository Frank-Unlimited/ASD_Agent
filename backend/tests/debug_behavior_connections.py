"""
调试：查看 Behavior 是否同时连接 Object 和 Interest
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.Memory.service import get_memory_service


async def debug_behavior_connections():
    """查看 Behavior 的连接情况"""
    
    print("=" * 60)
    print("调试：Behavior 连接情况")
    print("=" * 60)
    
    memory_service = await get_memory_service()
    
    try:
        child_id = "test_refactor_child"
        
        # 1. 查看有 Object 连接的 Behavior
        print("\n【1】有 Object 连接的 Behavior:")
        query1 = """
        MATCH (b:Entity)-[r:RELATES_TO]->(obj:Entity)
        WHERE 'Behavior' IN labels(b) AND 'Object' IN labels(obj)
        RETURN b.name AS behavior, obj.name AS object, b.uuid AS behavior_uuid
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query1)
        for record in records:
            print(f"  - {record['behavior']} --> {record['object']} (uuid: {record['behavior_uuid']})")
        
        # 2. 查看有 Interest 连接的 Behavior
        print("\n【2】有 Interest 连接的 Behavior:")
        query2 = """
        MATCH (b:Entity)-[r:RELATES_TO]->(int:Entity)
        WHERE 'Behavior' IN labels(b) AND 'Interest' IN labels(int)
        RETURN b.name AS behavior, int.name AS interest, b.uuid AS behavior_uuid, r.intensity AS intensity
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query2)
        for record in records:
            print(f"  - {record['behavior']} --> {record['interest']} (强度: {record['intensity']}, uuid: {record['behavior_uuid']})")
        
        # 3. 查看同时有 Object 和 Interest 连接的 Behavior
        print("\n【3】同时有 Object 和 Interest 连接的 Behavior:")
        query3 = """
        MATCH (b:Entity)-[r_obj:RELATES_TO]->(obj:Entity)
        WHERE 'Behavior' IN labels(b) AND 'Object' IN labels(obj)
        
        MATCH (b)-[r_int:RELATES_TO]->(int:Entity)
        WHERE 'Interest' IN labels(int)
        
        RETURN b.name AS behavior,
               obj.name AS object,
               int.name AS interest,
               r_int.intensity AS intensity
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query3)
        
        if records:
            for record in records:
                print(f"  - {record['behavior']}")
                print(f"    Object: {record['object']}")
                print(f"    Interest: {record['interest']} (强度: {record['intensity']})")
        else:
            print("  (未找到同时连接 Object 和 Interest 的 Behavior)")
        
        # 4. 统计
        print("\n【4】统计:")
        query4 = """
        MATCH (b:Entity)
        WHERE 'Behavior' IN labels(b)
        OPTIONAL MATCH (b)-[:RELATES_TO]->(obj:Entity)
        WHERE 'Object' IN labels(obj)
        OPTIONAL MATCH (b)-[:RELATES_TO]->(int:Entity)
        WHERE 'Interest' IN labels(int)
        
        WITH b,
             COUNT(DISTINCT obj) AS obj_count,
             COUNT(DISTINCT int) AS int_count
        
        RETURN 
            SUM(CASE WHEN obj_count > 0 THEN 1 ELSE 0 END) AS behaviors_with_objects,
            SUM(CASE WHEN int_count > 0 THEN 1 ELSE 0 END) AS behaviors_with_interests,
            SUM(CASE WHEN obj_count > 0 AND int_count > 0 THEN 1 ELSE 0 END) AS behaviors_with_both
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query4)
        if records:
            record = records[0]
            print(f"  - 有 Object 连接的 Behavior: {record['behaviors_with_objects']}")
            print(f"  - 有 Interest 连接的 Behavior: {record['behaviors_with_interests']}")
            print(f"  - 同时有两者的 Behavior: {record['behaviors_with_both']}")
        
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await memory_service.close()


if __name__ == "__main__":
    asyncio.run(debug_behavior_connections())
