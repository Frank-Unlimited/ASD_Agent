#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Microsoft GraphRAG 数据完整导入 Neo4j 图数据库
从 Jupyter Notebook 提取的所有未注释代码

功能:
1. 连接 Neo4j 数据库
2. 清空数据库（可选）
3. 并行批量导入数据
4. 导入 documents, text_units, entities, relationships, communities, community_reports
5. 创建节点和关系
6. 验证导入结果
"""

import time
import pandas as pd
import concurrent.futures
from neo4j import GraphDatabase, exceptions
from tabulate import tabulate
import os
import json


# ========== Neo4j 连接配置 ==========
NEO4J_URI = "bolt://localhost:7687"  # 注意：Bolt端口是7687，不是7474
NEO4J_USERNAME = "neo4j"
NEO4J_PASSWORD = "Han9510!"  # 替换为你的密码
NEO4J_DATABASE = "neo4j"
RETRY_TIMES = 3
RETRY_DELAY = 5

# 全局驱动实例
driver = None


# ========== 连接函数 ==========
def connect_neo4j():
    """创建Neo4j驱动并验证连接（带重试）"""
    global driver
    for i in range(RETRY_TIMES):
        try:
            if NEO4J_PASSWORD.strip() == "":
                driver = GraphDatabase.driver(NEO4J_URI, connection_timeout=30)
            else:
                driver = GraphDatabase.driver(
                    NEO4J_URI,
                    auth=(NEO4J_USERNAME, NEO4J_PASSWORD),
                    connection_timeout=30
                )
            driver.verify_connectivity()
            print(f"✅ 第{i+1}次尝试：Neo4j连接成功！")
            return driver
        except exceptions.AuthError:
            print(f"❌ 第{i+1}次尝试：用户名/密码错误！")
            break
        except exceptions.ServiceUnavailable as e:
            print(f"❌ 第{i+1}次尝试：Neo4j服务未启动或端口错误！错误信息：{str(e)}")
            if i < RETRY_TIMES - 1:
                time.sleep(RETRY_DELAY)
            else:
                break
        except Exception as e:
            print(f"❌ 第{i+1}次尝试：连接失败：{str(e)}")
            time.sleep(RETRY_DELAY)
    return None


# ========== 清空数据库函数 ==========
def clear_neo4j_database():
    """清空Neo4j数据库的所有数据"""
    global driver
    driver = connect_neo4j()
    if not driver:
        print("❌ Neo4j连接失败，终止清空操作！")
        return

    try:
        with driver.session() as session:
            # 步骤1：删除所有约束
            constraints = session.run("""
                SHOW CONSTRAINTS YIELD name, type, entityType, labelsOrTypes, properties
                WHERE name IS NOT NULL
            """).data()
            
            if constraints:
                print(f"📌 发现{len(constraints)}个约束，开始删除...")
                cons_count = 0
                for cons in constraints:
                    cons_name = cons['name']
                    try:
                        session.run(f"DROP CONSTRAINT {cons_name}")
                        print(f"✅ 已删除约束：{cons_name}")
                        cons_count += 1
                    except Exception as e:
                        print(f"⚠️ 删除约束{cons_name}失败：{str(e)}")
                print(f"📌 约束删除完成：成功{cons_count}个")
            else:
                print("📌 未发现任何约束")

            # 步骤2：删除所有独立索引
            indexes = session.run("""
                SHOW INDEXES YIELD name, type
                WHERE name IS NOT NULL AND type <> 'CONSTRAINT'
            """).data()
            
            if indexes:
                print(f"\n📌 发现{len(indexes)}个索引，开始删除...")
                idx_count = 0
                for idx in indexes:
                    idx_name = idx['name']
                    try:
                        session.run(f"DROP INDEX {idx_name}")
                        print(f"✅ 已删除索引：{idx_name}")
                        idx_count += 1
                    except Exception as e:
                        print(f"⚠️ 删除索引{idx_name}失败：{str(e)}")
                print(f"📌 索引删除完成：成功{idx_count}个")
            else:
                print("📌 未发现任何独立索引")

            # 步骤3：删除所有节点和关系
            result = session.run("MATCH (n) DETACH DELETE n")
            counters = result.consume().counters
            print(f"\n📌 数据删除结果：")
            print(f"   - 已删除节点：{counters.nodes_deleted}")
            print(f"   - 已删除关系：{counters.relationships_deleted}")

        print("\n🎉 Neo4j数据库已完全清空！")

    except Exception as e:
        print(f"\n❌ 清空数据库失败：{str(e)}")
    finally:
        if driver:
            driver.close()


# ========== 读取 Parquet 文件函数 ==========
def find_and_read_parquet(filename):
    """自动查找并读取 parquet 文件"""
    possible_paths = [
        f'../data/output/{filename}',
        f'data/output/{filename}',
        f'../../data/output/{filename}',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✅ 找到文件: {path}")
            return pd.read_parquet(path)
    
    raise FileNotFoundError(f"找不到 {filename}")


# ========== 并行批量导入函数 ==========
def parallel_batched_import(statement, df, batch_size=100, max_workers=8):
    """使用并行处理进行批量导入数据到Neo4j"""
    global driver
    
    total = len(df)
    batches = (total + batch_size - 1) // batch_size
    start_time = time.time()
    results = []
    
    print(f"开始并行导入 {total} 行数据，分为 {batches} 个批次，每批 {batch_size} 条")
    
    def process_batch(batch_idx):
        start = batch_idx * batch_size
        end = min(start + batch_size, total)
        batch = df.iloc[start:end]
        batch_start_time = time.time()
        
        try:
            with driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(
                    "UNWIND $rows AS value " + statement,   
                    rows=batch.to_dict("records")
                )
                summary = result.consume()
                batch_duration = time.time() - batch_start_time
                
                return {
                    "batch": batch_idx,
                    "rows": end - start,
                    "success": True,
                    "duration": batch_duration,
                    "counters": summary.counters
                }
        except Exception as e:
            batch_duration = time.time() - batch_start_time
            print(f"批次 {batch_idx} (行 {start}-{end-1}) 处理失败: {str(e)}")
            
            return {
                "batch": batch_idx,
                "rows": end - start,
                "success": False,
                "duration": batch_duration,
                "error": str(e)
            }
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_batch, i) for i in range(batches)]
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            result = future.result()
            results.append(result)
            
            if result["success"]:
                print(f"批次 {result['batch']} 完成: {result['rows']} 行, 耗时 {result['duration']:.2f}秒")
            
            print(f"进度: {i+1}/{batches} 批次完成 ({((i+1)/batches*100):.1f}%)")
    
    successful_rows = sum(r["rows"] for r in results if r["success"])
    failed_rows = sum(r["rows"] for r in results if not r["success"])
    
    duration = time.time() - start_time
    rows_per_second = successful_rows / duration if duration > 0 else 0
    
    print(f"导入完成: 总计 {total} 行, 成功 {successful_rows} 行, 失败 {failed_rows} 行")
    print(f"总耗时: {duration:.2f}秒, 平均速度: {rows_per_second:.2f} 行/秒")
    
    return {
        "total_rows": total,
        "successful_rows": successful_rows,
        "failed_rows": failed_rows,
        "duration_seconds": duration,
        "rows_per_second": rows_per_second,
        "batch_results": results
    }


# ========== 导入文档 ==========
def create_document_nodes(df_documents):
    """创建Document节点"""
    global driver
    with driver.session(database=NEO4J_DATABASE) as session:
        try:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:__Document__) REQUIRE d.id IS UNIQUE")
        except Exception as e:
            print(f"创建约束时出错 (可能已存在): {e}")
    
    cypher_statement = """
    MERGE (d:__Document__ {id: value.id})
    ON CREATE SET 
        d.human_readable_id = value.human_readable_id,
        d.title = value.title,
        d.text = value.text,
        d.creation_date = value.creation_date,
        d.import_timestamp = timestamp()
    """
    
    return parallel_batched_import(cypher_statement, df_documents)


# ========== 导入文本单元 ==========
def setup_chunk_constraints():
    """创建Chunk标签的约束"""
    global driver
    with driver.session(database=NEO4J_DATABASE) as session:
        try:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:__Chunk__) REQUIRE c.id IS UNIQUE")
            print("已创建Chunk.id唯一性约束")
        except Exception as e:
            print(f"创建__Chunk__约束时出错 (可能已存在): {e}")


def import_chunks(df_chunks, batch_size=100, max_workers=8):
    """导入文档块(Chunk)到Neo4j"""
    global driver
    
    setup_chunk_constraints()
    
    print("开始导入Chunk节点...")
    chunk_statement = """
    MERGE (c:__Chunk__ {id: value.id})
    SET c.text = value.text,
        c.n_tokens = value.n_tokens,
        c.human_readable_id = value.human_readable_id,
        c.name = value.human_readable_id
    """
    
    chunk_result = parallel_batched_import(chunk_statement, df_chunks, batch_size, max_workers)
    
    print("准备Chunk-Document关系数据...")
    relations_data = []
    
    for idx, row in df_chunks.iterrows():
        chunk_id = row['id']
        doc_ids_container = row['document_ids']
        
        flat_doc_ids = []
        if isinstance(doc_ids_container, list):
            for item in doc_ids_container:
                if hasattr(item, 'dtype') and hasattr(item, 'tolist'):
                    flat_doc_ids.extend(item.tolist())
                elif isinstance(item, list):
                    flat_doc_ids.extend(item)
                else:
                    flat_doc_ids.append(item)
        elif doc_ids_container is not None:
            flat_doc_ids.append(doc_ids_container)
        
        for doc_id in flat_doc_ids:
            if doc_id is not None and str(doc_id).strip() != '':
                doc_id_str = str(doc_id).strip()
                if not (doc_id_str.startswith('<elementId>') or doc_id_str.startswith('<id>')):
                    relations_data.append({
                        'chunk_id': chunk_id,
                        'document_id': doc_id_str
                    })
    
    if relations_data:
        print(f"开始创建 {len(relations_data)} 个Chunk-Document关系...")
        df_relations = pd.DataFrame(relations_data)
        
        relation_statement = """
        MATCH (c:__Chunk__ {id: value.chunk_id})
        MATCH (d:__Document__ {id: value.document_id})
        MERGE (c)-[:PART_OF]->(d)
        """
        
        relation_result = parallel_batched_import(relation_statement, df_relations, batch_size, max_workers)
        print(f"已创建 {relation_result['successful_rows']} 个Chunk-Document关系")
    
    return chunk_result


# ========== 导入实体 ==========
def setup_entity_constraints():
    """创建Entity标签的约束"""
    global driver
    with driver.session(database=NEO4J_DATABASE) as session:
        try:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:__Entity__) REQUIRE e.id IS UNIQUE")
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:__Entity__) REQUIRE e.name IS UNIQUE")
            print("已创建__Entity__.id唯一性约束")
        except Exception as e:
            print(f"创建__Entity__约束时出错 (可能已存在): {e}")


def import_entities(df_entities, batch_size=100, max_workers=8):
    """导入实体(Entity)到Neo4j"""
    global driver
    
    setup_entity_constraints()
    
    print("预处理text_unit_ids...")
    df_entities = df_entities.copy()
    
    for idx, row in df_entities.iterrows():
        text_unit_ids = row.get('text_unit_ids')
        
        if not isinstance(text_unit_ids, list):
            if isinstance(text_unit_ids, str):
                try:
                    text_unit_ids = json.loads(text_unit_ids)
                except:
                    text_unit_ids = [text_unit_ids]
            elif hasattr(text_unit_ids, 'dtype') and hasattr(text_unit_ids, 'tolist'):
                text_unit_ids = text_unit_ids.tolist()
            else:
                text_unit_ids = [text_unit_ids] if text_unit_ids is not None else []
        
        flat_text_unit_ids = []
        for item in text_unit_ids:
            if isinstance(item, list) or (hasattr(item, 'dtype') and hasattr(item, 'tolist')):
                if hasattr(item, 'tolist'):
                    flat_text_unit_ids.extend(item.tolist())
                else:
                    flat_text_unit_ids.extend(item)
            else:
                flat_text_unit_ids.append(item)
        
        flat_text_unit_ids = [str(id) for id in flat_text_unit_ids if id is not None and str(id).strip() != '']
        df_entities.at[idx, 'text_unit_ids'] = flat_text_unit_ids
    
    print("检查Neo4j功能支持...")
    has_apoc = False
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            try:
                result = session.run("RETURN apoc.version() AS version")
                version = result.single()["version"]
                has_apoc = True
                print(f"APOC插件已安装，版本: {version}")
            except Exception as e:
                print(f"检查APOC插件时出错 (可能未安装): {e}")
    except Exception as e:
        print(f"检查Neo4j功能支持时出错: {e}")
    
    print("开始导入__Entity__节点并创建关系...")
    
    if has_apoc:
        entity_statement = """
        MERGE (e:__Entity__ {id:value.id})
        SET e += value {.human_readable_id, .description, .frequency, .degree, .x, .y}
        SET e.name = replace(coalesce(value.title, value.human_readable_id, ''), '"', '')
        
        WITH e, value
        CALL apoc.create.addLabels(e, 
            CASE WHEN coalesce(value.type,"") = "" 
            THEN [] 
            ELSE [apoc.text.upperCamelCase(replace(value.type,'"',''))] 
            END
        ) YIELD node
        
        WITH node as e, value
        UNWIND value.text_unit_ids AS text_unit
        MATCH (c:__Chunk__ {id:text_unit})
        MERGE (c)-[:HAS_ENTITY]->(e)
        """
    else:
        entity_statement = """
        MERGE (e:__Entity__ {id:value.id})
        SET e += value {.human_readable_id, .description, .frequency, .degree, .x, .y}
        SET e.name = replace(coalesce(value.title, value.human_readable_id, ''), '"', '')
        
        WITH e, value
        UNWIND value.text_unit_ids AS text_unit
        MATCH (c:__Chunk__ {id:text_unit})
        MERGE (c)-[:HAS_ENTITY]->(e)
        """
    
    entity_result = parallel_batched_import(entity_statement, df_entities, batch_size, max_workers)
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run("MATCH (e:__Entity__) RETURN count(e) as count")
        entity_count = result.single()["count"]
        
        result = session.run("MATCH (c:__Chunk__)-[r:HAS_ENTITY]->(e:__Entity__) RETURN count(r) as count")
        relation_count = result.single()["count"]
        
        print(f"验证结果: {entity_count} 个__Entity__节点, {relation_count} 个HAS_ENTITY关系")
    
    return entity_result


# ========== 导入关系 ==========
def setup_relationship_constraints():
    """创建Relationship标签的约束"""
    global driver
    with driver.session(database=NEO4J_DATABASE) as session:
        try:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:__Relationship__) REQUIRE r.id IS UNIQUE")
            print("已创建__Relationship__.id唯一性约束")
        except Exception as e:
            print(f"创建__Relationship__约束时出错 (可能已存在): {e}")


def import_relationships(df_relationships, batch_size=100, max_workers=8):
    """导入关系数据到Neo4j"""
    global driver
    
    setup_relationship_constraints()
    
    print("预处理text_unit_ids...")
    df_relationships = df_relationships.copy()
    
    for idx, row in df_relationships.iterrows():
        text_unit_ids = row.get('text_unit_ids')
        
        if not isinstance(text_unit_ids, list):
            if isinstance(text_unit_ids, str):
                try:
                    text_unit_ids = json.loads(text_unit_ids)
                except:
                    text_unit_ids = [text_unit_ids]
            elif hasattr(text_unit_ids, 'dtype') and hasattr(text_unit_ids, 'tolist'):
                text_unit_ids = text_unit_ids.tolist()
            else:
                text_unit_ids = [text_unit_ids] if text_unit_ids is not None else []
        
        flat_text_unit_ids = []
        for item in text_unit_ids:
            if isinstance(item, list) or (hasattr(item, 'dtype') and hasattr(item, 'tolist')):
                if hasattr(item, 'tolist'):
                    flat_text_unit_ids.extend(item.tolist())
                else:
                    flat_text_unit_ids.extend(item)
            else:
                flat_text_unit_ids.append(item)
        
        flat_text_unit_ids = [str(id) for id in flat_text_unit_ids if id is not None and str(id).strip() != '']
        df_relationships.at[idx, 'text_unit_ids'] = flat_text_unit_ids
    
    print("开始导入关系数据...")
    
    relationship_statement = """
    MERGE (r:__Relationship__ {id: value.id})
    SET r.human_readable_id = value.human_readable_id,
        r.description = value.description,
        r.weight = value.weight,
        r.combined_degree = value.combined_degree,
        r.name = value.human_readable_id
    
    WITH r, value
    MERGE (source:__Entity__ {id: value.source})
    MERGE (target:__Entity__ {id: value.target})
    
    MERGE (source)-[rel:RELATED]->(target)
    SET rel.relationship_id = value.id,
        rel.description = value.description,
        rel.weight = value.weight
    
    RETURN r.id as relationship_id
    """
    
    relationship_result = parallel_batched_import(relationship_statement, df_relationships, batch_size, max_workers)
    print(f"已创建 {relationship_result['successful_rows']} 个__Relationship__节点和RELATED关系")
    
    chunk_relations = []
    for _, row in df_relationships.iterrows():
        rel_id = row['id']
        for chunk_id in row['text_unit_ids']:
            chunk_relations.append({
                'relationship_id': rel_id,
                'chunk_id': chunk_id
            })
    
    if chunk_relations:
        df_chunk_relations = pd.DataFrame(chunk_relations)
        
        chunk_rel_statement = """
        MATCH (r:__Relationship__ {id: value.relationship_id})
        MATCH (c:__Chunk__ {id: value.chunk_id})
        MERGE (c)-[:HAS_RELATIONSHIP]->(r)
        """
        
        chunk_rel_result = parallel_batched_import(chunk_rel_statement, df_chunk_relations, batch_size, max_workers)
        print(f"已创建 {chunk_rel_result['successful_rows']} 个Chunk-Relationship关系")
    
    return relationship_result


# ========== 导入社区 ==========
def setup_community_constraints():
    """创建Community标签的约束"""
    global driver
    with driver.session(database=NEO4J_DATABASE) as session:
        try:
            session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:__Community__) REQUIRE c.id IS UNIQUE")
            print("已创建__Community__.id唯一性约束")
        except Exception as e:
            print(f"创建__Community__约束时出错 (可能已存在): {e}")


def import_communities(df_communities, batch_size=100, max_workers=8):
    """导入社区(Community)数据到Neo4j"""
    global driver
    
    setup_community_constraints()
    
    print("预处理列表字段...")
    df_communities = df_communities.copy()
    
    list_fields = ['children', 'entity_ids', 'relationship_ids', 'text_unit_ids']
    
    for field in list_fields:
        if field in df_communities.columns:
            for idx, row in df_communities.iterrows():
                field_value = row.get(field)
                
                if not isinstance(field_value, list):
                    if isinstance(field_value, str):
                        try:
                            field_value = json.loads(field_value)
                        except:
                            field_value = [field_value]
                    elif hasattr(field_value, 'dtype') and hasattr(field_value, 'tolist'):
                        field_value = field_value.tolist()
                    else:
                        field_value = [field_value] if field_value is not None else []
                
                flat_field_value = []
                for item in field_value:
                    if isinstance(item, list) or (hasattr(item, 'dtype') and hasattr(item, 'tolist')):
                        if hasattr(item, 'tolist'):
                            flat_field_value.extend(item.tolist())
                        else:
                            flat_field_value.extend(item)
                    else:
                        flat_field_value.append(item)
                
                if field in ['entity_ids', 'relationship_ids', 'text_unit_ids']:
                    flat_field_value = [str(id) for id in flat_field_value if id is not None and str(id).strip() != '']
                
                df_communities.at[idx, field] = flat_field_value
    
    print("开始导入社区节点...")
    
    community_statement = """
    MERGE (c:__Community__ {id: value.id})
    SET c.human_readable_id = value.human_readable_id,
        c.community = value.community,
        c.level = value.level,
        c.parent = value.parent,
        c.children = value.children,
        c.title = value.title,
        c.period = value.period,
        c.size = value.size,
        c.name = coalesce(value.title, value.human_readable_id, 'Community_' + value.id)
    
    RETURN c.id as community_id
    """
    
    community_result = parallel_batched_import(community_statement, df_communities, batch_size, max_workers)
    print(f"已创建 {community_result['successful_rows']} 个__Community__节点")
    
    print("开始创建社区与实体的关系...")
    entity_relations = []
    for _, row in df_communities.iterrows():
        community_id = row['id']
        entity_ids = row.get('entity_ids', [])
        
        for entity_id in entity_ids:
            entity_relations.append({
                'community_id': community_id,
                'entity_id': entity_id
            })
    
    if entity_relations:
        df_entity_relations = pd.DataFrame(entity_relations)
        
        entity_rel_statement = """
        MATCH (c:__Community__ {id: value.community_id})
        MATCH (e:__Entity__ {id: value.entity_id})
        MERGE (e)-[:IN_COMMUNITY]->(c)
        """
        
        entity_rel_result = parallel_batched_import(entity_rel_statement, df_entity_relations, batch_size, max_workers)
        print(f"已创建 {entity_rel_result['successful_rows']} 个Entity-Community关系")
    
    print("开始创建社区与关系的关系...")
    rel_relations = []
    for _, row in df_communities.iterrows():
        community_id = row['id']
        relationship_ids = row.get('relationship_ids', [])
        
        for rel_id in relationship_ids:
            rel_relations.append({
                'community_id': community_id,
                'relationship_id': rel_id
            })
    
    if rel_relations:
        df_rel_relations = pd.DataFrame(rel_relations)
        
        rel_rel_statement = """
        MATCH (c:__Community__ {id: value.community_id})
        MATCH (r:__Relationship__ {id: value.relationship_id})
        MERGE (r)-[:IN_COMMUNITY]->(c)
        """
        
        rel_rel_result = parallel_batched_import(rel_rel_statement, df_rel_relations, batch_size, max_workers)
        print(f"已创建 {rel_rel_result['successful_rows']} 个Relationship-Community关系")
    
    return community_result


# ========== 导入社区报告 ==========
def import_community_reports(df_reports, batch_size=20, max_workers=2):
    """导入社区报告数据到Neo4j"""
    global driver
    
    print("预处理社区报告数据...")
    df_reports = df_reports.copy()
    
    df_reports['community_str'] = None
    df_reports['processed_findings'] = None
    
    for idx, row in df_reports.iterrows():
        if 'community' in row:
            community_str = str(row['community'])
            df_reports.at[idx, 'community_str'] = community_str
        
        findings = row.get('findings')
        
        if hasattr(findings, 'dtype') and hasattr(findings, 'tolist'):
            try:
                findings = findings.tolist()
            except Exception as e:
                findings = []
        elif not isinstance(findings, list):
            if isinstance(findings, str):
                try:
                    findings = json.loads(findings)
                except Exception as e:
                    findings = []
            else:
                findings = []
        
        if not isinstance(findings, list):
            findings = []
        
        valid_findings = []
        for i, finding in enumerate(findings):
            if isinstance(finding, dict):
                if 'summary' not in finding:
                    finding['summary'] = f"Finding_{i}"
                if 'explanation' not in finding:
                    finding['explanation'] = ""
                valid_findings.append(finding)
        
        df_reports.at[idx, 'processed_findings'] = valid_findings
    
    print("准备Finding数据...")
    findings_data = []
    
    for idx, row in df_reports.iterrows():
        community_str = row['community_str']
        processed_findings = row['processed_findings']
        
        if not isinstance(processed_findings, list):
            continue
            
        for i, finding in enumerate(processed_findings):
            if isinstance(finding, dict):
                finding_id = f"{community_str}_{i}"
                findings_data.append({
                    'finding_id': finding_id,
                    'community_id': community_str,
                    'summary': finding.get('summary', f"Finding_{i}"),
                    'explanation': finding.get('explanation', "")
                })
    
    print(f"准备了 {len(findings_data)} 个Finding数据")
    
    print("步骤1: 导入社区节点...")
    
    community_statement = """
    MERGE (c:__Community__ {community: value.community_str})
    SET c.level = value.level,
        c.title = value.title,
        c.rank = value.rank,
        c.rating_explanation = value.rating_explanation,
        c.full_content = value.full_content,
        c.summary = value.summary,
        c.name = coalesce(value.title, 'Community_' + value.community_str)
    RETURN c.community as community_id
    """
    
    community_result = parallel_batched_import(community_statement, df_reports, batch_size, max_workers)
    print(f"已创建/更新 {community_result['successful_rows']} 个社区节点")
    
    if findings_data:
        print("步骤2: 导入Finding节点和关系...")
        df_findings = pd.DataFrame(findings_data)
        
        finding_statement = """
        MERGE (f:__Finding__ {id: value.finding_id})
        SET f.summary = value.summary,
            f.explanation = value.explanation,
            f.name = value.summary
        
        WITH f, value
        MATCH (c:__Community__ {community: value.community_id})
        MERGE (c)-[:HAS_FINDING]->(f)
        """
        
        finding_result = parallel_batched_import(finding_statement, df_findings, batch_size, max_workers)
        print(f"已创建 {finding_result['successful_rows']} 个Finding节点和HAS_FINDING关系")
    
    return community_result


# ========== 主函数 ==========
def main():
    """主函数：执行完整的导入流程"""
    global driver
    
    print("=" * 80)
    print("Microsoft GraphRAG 数据导入 Neo4j 图数据库")
    print("=" * 80)
    
    # 1. 连接数据库
    print("\n步骤1: 连接Neo4j数据库...")
    driver = connect_neo4j()
    if not driver:
        print("❌ 无法连接到Neo4j数据库，程序退出")
        return
    
    # 2. 读取数据文件
    print("\n步骤2: 读取Parquet数据文件...")
    try:
        df_documents = find_and_read_parquet('documents.parquet')
        df_text_units = find_and_read_parquet('text_units.parquet')
        df_entities = find_and_read_parquet('entities.parquet')
        df_relations = find_and_read_parquet('relationships.parquet')
        df_communities = find_and_read_parquet('communities.parquet')
        df_communities_reports = find_and_read_parquet('community_reports.parquet')
        
        print(f"✅ 成功读取所有数据文件")
        print(f"   - Documents: {len(df_documents)} 行")
        print(f"   - Text Units: {len(df_text_units)} 行")
        print(f"   - Entities: {len(df_entities)} 行")
        print(f"   - Relationships: {len(df_relations)} 行")
        print(f"   - Communities: {len(df_communities)} 行")
        print(f"   - Community Reports: {len(df_communities_reports)} 行")
    except Exception as e:
        print(f"❌ 读取数据文件失败: {e}")
        return
    
    # 3. 导入数据
    print("\n步骤3: 开始导入数据到Neo4j...")
    
    try:
        print("\n3.1 导入Documents...")
        create_document_nodes(df_documents)
        
        print("\n3.2 导入Text Units (Chunks)...")
        import_chunks(df_text_units)
        
        print("\n3.3 导入Entities...")
        import_entities(df_entities)
        
        print("\n3.4 导入Relationships...")
        import_relationships(df_relations)
        
        print("\n3.5 导入Communities...")
        import_communities(df_communities)
        
        print("\n3.6 导入Community Reports...")
        import_community_reports(df_communities_reports)
        
        print("\n" + "=" * 80)
        print("✅ 所有数据导入完成！")
        print("=" * 80)
        print("\n可以访问 http://localhost:7474 查看Neo4j浏览器")
        print("常用查询:")
        print("  - 查看实体关系: MATCH path = (:__Entity__)-[:RELATED]->(:__Entity__) RETURN path LIMIT 200")
        print("  - 查看文档结构: MATCH (d:__Document__)<-[:PART_OF]-(c:__Chunk__) RETURN * LIMIT 100")
        print("  - 查看社区: MATCH p=()-[r:IN_COMMUNITY]->() RETURN p LIMIT 25")
        
    except Exception as e:
        print(f"\n❌ 导入过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.close()
            print("\n数据库连接已关闭")


if __name__ == "__main__":
    # 可选：先清空数据库
    # clear_neo4j_database()
    
    # 执行导入
    main()
