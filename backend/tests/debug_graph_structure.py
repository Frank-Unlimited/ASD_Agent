"""
调试：查看图数据库的实际结构
"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.Memory.service import get_memory_service


async def debug_graph_structure():
    """查看图数据库的实际结构"""
    
    print("=" * 60)
    print("调试：查看图数据库结构")
    print("=" * 60)
    
    memory_service = await get_memory_service()
    
    try:
        # 1. 查看所有节点标签
        print("\n【1】所有节点标签:")
        query1 = "CALL db.labels()"
        records, _, _ = await memory_service.graphiti.driver.execute_query(query1)
        for record in records:
            print(f"  - {record['label']}")
        
        # 2. 查看所有关系类型
        print("\n【2】所有关系类型:")
        query2 = "CALL db.relationshipTypes()"
        records, _, _ = await memory_service.graphiti.driver.execute_query(query2)
        for record in records:
            print(f"  - {record['relationshipType']}")
        
        # 3. 查看 Entity 节点的标签分布
        print("\n【3】Entity 节点的标签分布:")
        query3 = """
        MATCH (n:Entity)
        RETURN labels(n) AS labels, COUNT(*) AS count
        ORDER BY count DESC
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query3)
        for record in records:
            print(f"  - {record['labels']}: {record['count']}")
        
        # 4. 查看 Episodic 节点
        print("\n【4】Episodic 节点:")
        query4 = """
        MATCH (e:Episodic)
        RETURN e.uuid AS uuid, e.name AS name, e.group_id AS group_id, e.content AS content
        LIMIT 5
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query4)
        for record in records:
            print(f"  - {record['name']} (group_id: {record['group_id']})")
            print(f"    内容: {record['content'][:100]}...")
        
        # 5. 查看 Behavior 相关的关系
        print("\n【5】Behavior 相关的关系:")
        query5 = """
        MATCH (b:Entity)-[r]->(target:Entity)
        WHERE 'Behavior' IN labels(b)
        RETURN labels(b) AS behavior_labels,
               type(r) AS rel_type,
               labels(target) AS target_labels,
               b.name AS behavior_name,
               target.name AS target_name
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query5)
        for record in records:
            print(f"  - {record['behavior_name']} --[{record['rel_type']}]--> {record['target_name']}")
            print(f"    Behavior标签: {record['behavior_labels']}")
            print(f"    Target标签: {record['target_labels']}")
        
        # 6. 查看 Object 节点
        print("\n【6】Object 节点:")
        query6 = """
        MATCH (o:Entity)
        WHERE 'Object' IN labels(o)
        RETURN o.uuid AS uuid, o.name AS name, labels(o) AS labels
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query6)
        for record in records:
            print(f"  - {record['name']} (标签: {record['labels']})")
        
        # 7. 查看 Interest 节点
        print("\n【7】Interest 节点:")
        query7 = """
        MATCH (i:Entity)
        WHERE 'Interest' IN labels(i)
        RETURN i.uuid AS uuid, i.name AS name, labels(i) AS labels
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query7)
        for record in records:
            print(f"  - {record['name']} (标签: {record['labels']})")
        
        # 8. 查看完整的 Behavior -> Object -> Interest 路径
        print("\n【8】Behavior -> Object 关系:")
        query8 = """
        MATCH (b:Entity)-[r]->(o:Entity)
        WHERE 'Behavior' IN labels(b) AND 'Object' IN labels(o)
        RETURN b.name AS behavior, type(r) AS rel_type, o.name AS object, properties(r) AS rel_props
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query8)
        if records:
            for record in records:
                print(f"  - {record['behavior']} --[{record['rel_type']}]--> {record['object']}")
                print(f"    关系属性: {record['rel_props']}")
        else:
            print("  (未找到 Behavior -> Object 关系)")
        
        # 9. 查看 Behavior -> Interest 关系
        print("\n【9】Behavior -> Interest 关系:")
        query9 = """
        MATCH (b:Entity)-[r]->(i:Entity)
        WHERE 'Behavior' IN labels(b) AND 'Interest' IN labels(i)
        RETURN b.name AS behavior, type(r) AS rel_type, i.name AS interest, properties(r) AS rel_props
        LIMIT 10
        """
        records, _, _ = await memory_service.graphiti.driver.execute_query(query9)
        if records:
            for record in records:
                print(f"  - {record['behavior']} --[{record['rel_type']}]--> {record['interest']}")
                print(f"    关系属性: {record['rel_props']}")
        else:
            print("  (未找到 Behavior -> Interest 关系)")
        
    except Exception as e:
        print(f"\n❌ 调试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await memory_service.close()


if __name__ == "__main__":
    asyncio.run(debug_graph_structure())
