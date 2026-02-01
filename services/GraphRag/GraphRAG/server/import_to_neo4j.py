#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将 GraphRAG 生成的 parquet 文件导入到 Neo4j 数据库
适用于 macOS 系统
"""

import pandas as pd
from neo4j import GraphDatabase
from pathlib import Path
import logging
from tqdm import tqdm
from typing import List, Dict, Any
import warnings

warnings.filterwarnings("ignore")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========================================
# Neo4j 连接配置 - 在这里修改你的 Neo4j 连接信息
# ========================================
NEO4J_URI = "bolt://localhost:7687"  # Neo4j 连接地址，默认端口 7687
NEO4J_USERNAME = "neo4j"              # Neo4j 用户名，默认为 neo4j
NEO4J_PASSWORD = "Han9510!"      # ⚠️ 修改为你设置的密码
NEO4J_DATABASE = "neo4j"              # 数据库名称，社区版只能使用 neo4j

# ========================================
# Parquet 文件路径配置 - 修改为你的 output 目录路径
# ========================================
# 获取脚本所在目录的父目录（项目根目录）
SCRIPT_DIR = Path(__file__).parent.parent
OUTPUT_DIR = SCRIPT_DIR / "data" / "output"  # GraphRAG 生成的 parquet 文件所在目录

# Parquet 文件路径
DOCUMENTS_PATH = OUTPUT_DIR / "documents.parquet"
TEXT_UNITS_PATH = OUTPUT_DIR / "text_units.parquet"
ENTITIES_PATH = OUTPUT_DIR / "entities.parquet"
RELATIONSHIPS_PATH = OUTPUT_DIR / "relationships.parquet"
COMMUNITIES_PATH = OUTPUT_DIR / "communities.parquet"
COMMUNITY_REPORTS_PATH = OUTPUT_DIR / "community_reports.parquet"


class Neo4jImporter:
    """Neo4j 数据导入器 - 使用并行批量导入提高性能"""
    
    def __init__(self, uri: str, username: str, password: str, database: str = "neo4j"):
        """
        初始化 Neo4j 连接
        
        参数:
            uri: Neo4j 连接地址
            username: 用户名
            password: 密码
            database: 数据库名称
        """
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        logger.info(f"✅ 已连接到 Neo4j: {uri}")
    
    def close(self):
        """关闭 Neo4j 连接"""
        self.driver.close()
        logger.info("Neo4j 连接已关闭")
    
    def clear_database(self):
        """
        清空数据库中的所有节点和关系
        ⚠️ 警告：此操作不可逆，会删除所有数据
        """
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("✅ 数据库已清空")
    
    def create_constraints(self):
        """
        创建约束和索引以提高查询性能
        - 为实体 ID 创建唯一性约束
        - 为实体名称创建索引
        - 为社区、文档、文本单元创建约束
        """
        with self.driver.session(database=self.database) as session:
            constraints = [
                ("graphrag_entity_id", "FOR (e:__Entity__) REQUIRE e.id IS UNIQUE", "__Entity__ ID"),
                ("graphrag_relationship_id", "FOR (r:__Relationship__) REQUIRE r.id IS UNIQUE", "__Relationship__ ID"),
                ("graphrag_community_id", "FOR (c:__Community__) REQUIRE c.id IS UNIQUE", "__Community__ ID"),
                ("graphrag_document_id", "FOR (d:__Document__) REQUIRE d.id IS UNIQUE", "__Document__ ID"),
                ("graphrag_text_unit_id", "FOR (t:__Chunk__) REQUIRE t.id IS UNIQUE", "__Chunk__ ID"),
            ]
            
            for constraint_name, constraint_def, description in constraints:
                try:
                    session.run(f"CREATE CONSTRAINT {constraint_name} IF NOT EXISTS {constraint_def}")
                    logger.info(f"✅ 已创建 {description} 唯一性约束")
                except Exception as e:
                    logger.warning(f"⚠️ 创建 {description} 约束失败（可能已存在）: {e}")
            
            # 创建索引
            indexes = [
                ("graphrag_entity_name", "FOR (e:__Entity__) ON (e.name)", "__Entity__ name"),
                ("graphrag_entity_human_readable_id", "FOR (e:__Entity__) ON (e.human_readable_id)", "__Entity__ human_readable_id"),
                ("graphrag_relationship_human_readable_id", "FOR (r:__Relationship__) ON (r.human_readable_id)", "__Relationship__ human_readable_id"),
                ("graphrag_community_title", "FOR (c:__Community__) ON (c.title)", "__Community__ title"),
            ]
            
            for index_name, index_def, description in indexes:
                try:
                    session.run(f"CREATE INDEX {index_name} IF NOT EXISTS {index_def}")
                    logger.info(f"✅ 已创建 {description} 索引")
                except Exception as e:
                    logger.warning(f"⚠️ 创建 {description} 索引失败（可能已存在）: {e}")
    
    def parallel_batched_import(self, statement: str, df: pd.DataFrame, 
                               batch_size: int = 100, max_workers: int = 1):
        """
        使用并行处理进行批量导入数据到 Neo4j（参考 Notebook 中的实现）
        
        参数:
            statement: Cypher 查询语句，使用 value 作为每行数据的引用
            df: 要导入的 DataFrame
            batch_size: 每批处理的行数，默认 100
            max_workers: 并行线程数，默认 8
        
        返回:
            导入统计信息的字典
        """
        import time
        import concurrent.futures
        
        # 1. 初始化，计算总行数、批次数，并记录开始时间
        total = len(df)
        batches = (total + batch_size - 1) // batch_size  # 向上取整
        start_time = time.time()
        results = []
        
        logger.info(f"开始并行导入 {total} 行数据，分为 {batches} 个批次，每批 {batch_size} 条")
        
        # 2. 定义批处理函数
        def process_batch(batch_idx):
            """
            批处理函数，用于处理每个批次的数据
            
            参数:
                batch_idx: 批次索引
            
            返回:
                批次处理结果字典
            """
            # 计算批次的起始和结束索引
            start = batch_idx * batch_size
            end = min(start + batch_size, total)
            batch = df.iloc[start:end]
            
            batch_start_time = time.time()
            
            try:
                with self.driver.session(database=self.database) as session:
                    # UNWIND 是 Cypher 中的关键字，用于将列表展开为多行
                    # $rows 是参数，表示将要传入的行数据
                    # 完整意思：将 $rows 参数（一个列表）中的每个元素展开，
                    # 每个元素被赋值给变量 value，对每个 value 执行后续的 Cypher 语句
                    result = session.run(
                        "UNWIND $rows AS value " + statement,
                        rows=batch.to_dict("records")  # 将 DataFrame 转换为字典列表
                    )
                    summary = result.consume()  # 获取查询的摘要信息（执行统计）
                    batch_duration = time.time() - batch_start_time
                    
                    return {
                        "batch": batch_idx,
                        "rows": end - start,
                        "success": True,
                        "duration": batch_duration,
                        "counters": summary.counters  # 统计信息（创建/更新的节点数等）
                    }
            except Exception as e:
                batch_duration = time.time() - batch_start_time
                logger.error(f"❌ 批次 {batch_idx} (行 {start}-{end-1}) 处理失败: {str(e)}")
                
                return {
                    "batch": batch_idx,
                    "rows": end - start,
                    "success": False,
                    "duration": batch_duration,
                    "error": str(e)
                }
        
        # 3. 使用线程池并行处理批次
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有批次任务
            futures = [executor.submit(process_batch, i) for i in range(batches)]
            
            # 处理完成的批次
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                
                if result["success"]:
                    logger.info(f"✅ 批次 {result['batch']} 完成: {result['rows']} 行, "
                              f"耗时 {result['duration']:.2f}秒")
                else:
                    logger.error(f"❌ 批次 {result['batch']} 失败: {result['rows']} 行, "
                               f"耗时 {result['duration']:.2f}秒")
                
                # 显示进度
                progress = (i + 1) / batches * 100
                logger.info(f"📊 进度: {i+1}/{batches} 批次完成 ({progress:.1f}%)")
        
        # 4. 统计结果
        successful_rows = sum(r["rows"] for r in results if r["success"])
        failed_rows = sum(r["rows"] for r in results if not r["success"])
        
        duration = time.time() - start_time
        rows_per_second = successful_rows / duration if duration > 0 else 0
        
        logger.info(f"✅ 导入完成: 总计 {total} 行, 成功 {successful_rows} 行, 失败 {failed_rows} 行")
        logger.info(f"⏱️  总耗时: {duration:.2f}秒, 平均速度: {rows_per_second:.2f} 行/秒")
        
        return {
            "total_rows": total,
            "successful_rows": successful_rows,
            "failed_rows": failed_rows,
            "duration_seconds": duration,
            "rows_per_second": rows_per_second,
            "batch_results": results
        }

    def import_entities(self, entities_df: pd.DataFrame, batch_size: int = 100):
        """
        导入实体节点到 Neo4j
        
        参数:
            entities_df: 实体 DataFrame（从 entities.parquet 读取）
            batch_size: 每批处理的行数
        """
        logger.info(f"📦 开始导入 {len(entities_df)} 个实体...")
        
        # 检查实际的列名，GraphRAG 可能使用 'title' 而不是 'name'
        id_column = 'title' if 'title' in entities_df.columns else 'name' if 'name' in entities_df.columns else 'id'
        logger.info(f"使用 '{id_column}' 列作为实体 ID")
        
        # 检查 human_readable_id
        if 'human_readable_id' in entities_df.columns:
            logger.info(f"✅ human_readable_id 范围: {entities_df['human_readable_id'].min()} - {entities_df['human_readable_id'].max()}")
        else:
            logger.warning("⚠️  未找到 human_readable_id 列")
        
        # 为 ID 为 null 的实体生成唯一 ID
        null_count = entities_df[id_column].isna().sum()
        if null_count > 0:
            logger.warning(f"⚠️  发现 {null_count} 个 {id_column} 为 null 的实体，将生成唯一 ID")
            entities_df[id_column] = entities_df.apply(
                lambda row: f"__NULL_ENTITY_{row['human_readable_id']}" if pd.isna(row[id_column]) else row[id_column],
                axis=1
            )
        
        # Cypher 语句：直接使用 human_readable_id，不创建 graphrag_id
        statement = f"""
        MERGE (e:__Entity__ {{id: value.{id_column}}})
        SET e.name = value.{id_column},
            e.type = value.type,
            e.description = value.description,
            e.human_readable_id = value.human_readable_id,
            e.text_unit_ids = value.text_unit_ids
        """
        
        # 使用并行批量导入
        result = self.parallel_batched_import(statement, entities_df, batch_size=batch_size)
        logger.info(f"✅ 实体导入完成: {result['successful_rows']}/{result['total_rows']} 成功")
        return result
    
    def import_relationships(self, relationships_df: pd.DataFrame, batch_size: int = 100):
        """
        导入关系到 Neo4j：创建 __Relationship__ 节点和 RELATED_TO 边
        
        参数:
            relationships_df: 关系 DataFrame（从 relationships.parquet 读取）
            batch_size: 每批处理的行数
        """
        logger.info(f"🔗 开始导入 {len(relationships_df)} 个关系...")
        
        # 检查 human_readable_id
        if 'human_readable_id' in relationships_df.columns:
            logger.info(f"✅ 关系 human_readable_id 范围: {relationships_df['human_readable_id'].min()} - {relationships_df['human_readable_id'].max()}")
        
        # 步骤 1: 创建 __Relationship__ 元数据节点
        relationship_node_statement = """
        MERGE (r:__Relationship__ {id: value.id})
        SET r.human_readable_id = value.human_readable_id,
            r.source = value.source,
            r.target = value.target,
            r.description = value.description,
            r.weight = value.weight,
            r.text_unit_ids = value.text_unit_ids
        """
        
        logger.info("📦 创建 __Relationship__ 元数据节点...")
        result_nodes = self.parallel_batched_import(relationship_node_statement, relationships_df, batch_size=batch_size)
        logger.info(f"✅ __Relationship__ 节点创建完成: {result_nodes['successful_rows']}/{result_nodes['total_rows']} 成功")
        
        # 步骤 2: 创建实体之间的 RELATED_TO 边
        relationship_edge_statement = """
        MATCH (source:__Entity__ {id: value.source})
        MATCH (target:__Entity__ {id: value.target})
        MERGE (source)-[r:RELATED_TO]->(target)
        SET r.description = value.description,
            r.weight = value.weight,
            r.relationship_id = value.id
        """
        
        logger.info("🔗 创建实体之间的 RELATED_TO 边...")
        result_edges = self.parallel_batched_import(relationship_edge_statement, relationships_df, batch_size=batch_size)
        logger.info(f"✅ RELATED_TO 边创建完成: {result_edges['successful_rows']}/{result_edges['total_rows']} 成功")
        
        return {
            'nodes': result_nodes,
            'edges': result_edges,
            'total_rows': len(relationships_df),
            'successful_rows': min(result_nodes['successful_rows'], result_edges['successful_rows'])
        }
    
    def import_documents(self, documents_df: pd.DataFrame, batch_size: int = 100):
        """
        导入文档节点到 Neo4j
        
        参数:
            documents_df: 文档 DataFrame（从 documents.parquet 读取）
            batch_size: 每批处理的行数
        """
        logger.info(f"📄 开始导入 {len(documents_df)} 个文档...")
        
        statement = """
        MERGE (d:__Document__ {id: value.id})
        SET d.title = value.title,
            d.raw_content = value.raw_content,
            d.text_unit_ids = value.text_unit_ids
        """
        
        result = self.parallel_batched_import(statement, documents_df, batch_size=batch_size)
        logger.info(f"✅ 文档导入完成: {result['successful_rows']}/{result['total_rows']} 成功")
        return result
    
    def import_text_units(self, text_units_df: pd.DataFrame, batch_size: int = 100):
        """
        导入文本单元节点到 Neo4j，并关联到文档、实体和关系
        
        参数:
            text_units_df: 文本单元 DataFrame（从 text_units.parquet 读取）
            batch_size: 每批处理的行数
        """
        logger.info(f"📝 开始导入 {len(text_units_df)} 个文本单元...")
        
        # 步骤 1: 创建文本块节点并连接到文档
        chunk_statement = """
        MERGE (t:__Chunk__ {id: value.id})
        SET t.text = value.text,
            t.n_tokens = value.n_tokens,
            t.document_ids = value.document_ids,
            t.entity_ids = value.entity_ids,
            t.relationship_ids = value.relationship_ids
        WITH t, value
        UNWIND value.document_ids AS doc_id
        MATCH (d:__Document__ {id: doc_id})
        MERGE (t)-[:PART_OF]->(d)
        """
        
        result_chunks = self.parallel_batched_import(chunk_statement, text_units_df, batch_size=batch_size)
        logger.info(f"✅ 文本单元节点创建完成: {result_chunks['successful_rows']}/{result_chunks['total_rows']} 成功")
        
        # 步骤 2: 连接文本块到实体
        logger.info("🔗 连接文本块到实体...")
        entity_link_statement = """
        MATCH (t:__Chunk__ {id: value.id})
        WITH t, value.entity_ids AS entity_ids
        WHERE entity_ids IS NOT NULL AND size(entity_ids) > 0
        UNWIND entity_ids AS entity_id
        MATCH (e:__Entity__ {id: entity_id})
        MERGE (t)-[:MENTIONS]->(e)
        """
        
        result_entities = self.parallel_batched_import(entity_link_statement, text_units_df, batch_size=batch_size)
        logger.info(f"✅ 文本块-实体连接完成: {result_entities['successful_rows']}/{result_entities['total_rows']} 成功")
        
        # 步骤 3: 连接文本块到关系节点
        logger.info("🔗 连接文本块到关系...")
        relationship_link_statement = """
        MATCH (t:__Chunk__ {id: value.id})
        WITH t, value.relationship_ids AS relationship_ids
        WHERE relationship_ids IS NOT NULL AND size(relationship_ids) > 0
        UNWIND relationship_ids AS rel_id
        MATCH (r:__Relationship__ {id: rel_id})
        MERGE (t)-[:HAS_RELATIONSHIP]->(r)
        """
        
        result_relationships = self.parallel_batched_import(relationship_link_statement, text_units_df, batch_size=batch_size)
        logger.info(f"✅ 文本块-关系连接完成: {result_relationships['successful_rows']}/{result_relationships['total_rows']} 成功")
        
        return {
            'chunks': result_chunks,
            'entity_links': result_entities,
            'relationship_links': result_relationships,
            'total_rows': len(text_units_df),
            'successful_rows': result_chunks['successful_rows'],
            'duration_seconds': result_chunks['duration_seconds'] + result_entities['duration_seconds'] + result_relationships['duration_seconds']
        }
    
    def import_communities(self, communities_df: pd.DataFrame, batch_size: int = 100):
        """
        导入社区节点到 Neo4j，并关联实体
        
        参数:
            communities_df: 社区 DataFrame（从 communities.parquet 读取）
            batch_size: 每批处理的行数
        """
        logger.info(f"🏘️ 开始导入 {len(communities_df)} 个社区...")
        
        statement = """
        MERGE (c:__Community__ {id: value.id})
        SET c.title = value.title,
            c.level = value.level,
            c.entity_ids = value.entity_ids,
            c.relationship_ids = value.relationship_ids,
            c.text_unit_ids = value.text_unit_ids
        WITH c, value
        UNWIND value.entity_ids AS entity_id
        MATCH (e:__Entity__ {id: entity_id})
        MERGE (e)-[:BELONGS_TO]->(c)
        """
        
        result = self.parallel_batched_import(statement, communities_df, batch_size=batch_size)
        logger.info(f"✅ 社区导入完成: {result['successful_rows']}/{result['total_rows']} 成功")
        return result
    
    def import_community_reports(self, reports_df: pd.DataFrame, batch_size: int = 100):
        """
        导入社区报告，并关联到社区
        
        参数:
            reports_df: 社区报告 DataFrame（从 community_reports.parquet 读取）
            batch_size: 每批处理的行数
        """
        logger.info(f"📊 开始导入 {len(reports_df)} 个社区报告...")
        
        statement = """
        MATCH (c:__Community__ {id: value.community})
        SET c.summary = value.summary,
            c.full_content = value.full_content,
            c.rank = value.rank,
            c.rank_explanation = value.rank_explanation,
            c.findings = value.findings
        """
        
        result = self.parallel_batched_import(statement, reports_df, batch_size=batch_size)
        logger.info(f"✅ 社区报告导入完成: {result['successful_rows']}/{result['total_rows']} 成功")
        return result


def main():
    """
    主函数：执行完整的 GraphRAG 数据导入流程
    
    流程：
    1. 检查 parquet 文件是否存在
    2. 读取所有数据
    3. 连接 Neo4j 数据库
    4. 创建约束和索引
    5. 并行批量导入所有数据
    6. 显示导入结果
    """
    logger.info("=" * 70)
    logger.info("🚀 开始导入 GraphRAG 数据到 Neo4j")
    logger.info("=" * 70)
    
    # 1. 检查必需文件是否存在
    required_files = {
        "实体": ENTITIES_PATH,
        "关系": RELATIONSHIPS_PATH,
    }
    
    for name, path in required_files.items():
        if not path.exists():
            logger.error(f"❌ {name}文件不存在: {path}")
            logger.error("请先运行 GraphRAG 索引构建生成 parquet 文件")
            return
    
    # 2. 读取 parquet 文件
    logger.info("📖 读取 parquet 文件...")
    data_files = {}
    
    try:
        # 必需文件
        data_files['entities'] = pd.read_parquet(ENTITIES_PATH)
        data_files['relationships'] = pd.read_parquet(RELATIONSHIPS_PATH)
        
        logger.info(f"📊 实体数量: {len(data_files['entities'])}")
        logger.info(f"📊 关系数量: {len(data_files['relationships'])}")
        
        # 可选文件
        optional_files = {
            'documents': DOCUMENTS_PATH,
            'text_units': TEXT_UNITS_PATH,
            'communities': COMMUNITIES_PATH,
            'community_reports': COMMUNITY_REPORTS_PATH,
        }
        
        for key, path in optional_files.items():
            if path.exists():
                data_files[key] = pd.read_parquet(path)
                logger.info(f"📊 {key} 数量: {len(data_files[key])}")
            else:
                logger.warning(f"⚠️  {key} 文件不存在，跳过: {path}")
        
        # 显示实体类型分布
        if 'type' in data_files['entities'].columns:
            type_counts = data_files['entities']['type'].value_counts()
            logger.info(f"📊 实体类型分布: {dict(type_counts.head(5))}")
        
    except Exception as e:
        logger.error(f"❌ 读取 parquet 文件失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return
    
    # 3. 连接 Neo4j 并导入
    logger.info(f"🔌 连接 Neo4j: {NEO4J_URI}")
    importer = Neo4jImporter(NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    results = {}
    total_duration = 0
    
    try:
        # 清空数据库
        logger.info("⚠️  清空数据库...")
        importer.clear_database()
        
        # 4. 创建约束和索引
        logger.info("🔧 创建约束和索引...")
        importer.create_constraints()
        
        # 5. 导入数据（按依赖顺序）
        step = 1
        
        # 步骤 1: 导入文档（如果存在）
        if 'documents' in data_files:
            logger.info("\n" + "=" * 70)
            logger.info(f"第 {step} 步：导入文档")
            logger.info("=" * 70)
            results['documents'] = importer.import_documents(data_files['documents'], batch_size=100)
            total_duration += results['documents']['duration_seconds']
            step += 1
        
        # 步骤 2: 导入实体
        logger.info("\n" + "=" * 70)
        logger.info(f"第 {step} 步：导入实体节点")
        logger.info("=" * 70)
        results['entities'] = importer.import_entities(data_files['entities'], batch_size=100)
        total_duration += results['entities']['duration_seconds']
        step += 1
        
        # 步骤 3: 导入关系
        logger.info("\n" + "=" * 70)
        logger.info(f"第 {step} 步：导入关系")
        logger.info("=" * 70)
        results['relationships'] = importer.import_relationships(data_files['relationships'], batch_size=100)
        # 关系导入返回的是包含 nodes 和 edges 的字典
        if 'nodes' in results['relationships']:
            total_duration += results['relationships']['nodes']['duration_seconds']
            total_duration += results['relationships']['edges']['duration_seconds']
        step += 1
        
        # 步骤 4: 导入文本单元（如果存在）
        if 'text_units' in data_files:
            logger.info("\n" + "=" * 70)
            logger.info(f"第 {step} 步：导入文本单元")
            logger.info("=" * 70)
            results['text_units'] = importer.import_text_units(data_files['text_units'], batch_size=100)
            if 'duration_seconds' in results['text_units']:
                total_duration += results['text_units']['duration_seconds']
            step += 1
        
        # 步骤 5: 导入社区（如果存在）
        if 'communities' in data_files:
            logger.info("\n" + "=" * 70)
            logger.info(f"第 {step} 步：导入社区")
            logger.info("=" * 70)
            results['communities'] = importer.import_communities(data_files['communities'], batch_size=100)
            total_duration += results['communities']['duration_seconds']
            step += 1
        
        # 步骤 6: 导入社区报告（如果存在）
        if 'community_reports' in data_files:
            logger.info("\n" + "=" * 70)
            logger.info(f"第 {step} 步：导入社区报告")
            logger.info("=" * 70)
            results['community_reports'] = importer.import_community_reports(data_files['community_reports'], batch_size=100)
            total_duration += results['community_reports']['duration_seconds']
            step += 1
        
        # 6. 显示最终结果
        logger.info("\n" + "=" * 70)
        logger.info("✅ 数据导入完成！")
        logger.info("=" * 70)
        
        for key, result in results.items():
            logger.info(f"📊 {key}: {result['successful_rows']}/{result['total_rows']} 成功")
        
        logger.info(f"⏱️  总耗时: {total_duration:.2f} 秒")
        logger.info("\n🌐 请访问 http://localhost:7474 查看知识图谱")
        logger.info("   默认用户名: neo4j")
        logger.info("   密码: 你设置的密码")
        logger.info("\n💡 在 Neo4j 浏览器中运行以下查询查看图谱:")
        logger.info("   # 查看实体")
        logger.info("   MATCH (n:__Entity__) RETURN n LIMIT 25")
        logger.info("\n   # 查看社区")
        logger.info("   MATCH (c:__Community__) RETURN c LIMIT 10")
        logger.info("\n   # 查看实体和它们所属的社区")
        logger.info("   MATCH (e:__Entity__)-[:BELONGS_TO]->(c:__Community__) RETURN e, c LIMIT 25")
        logger.info("\n   # 通过 human_readable_id 查询实体（例如查询实体 20397）")
        logger.info("   MATCH (e:__Entity__ {human_readable_id: 20397}) RETURN e")
        logger.info("\n   # 通过实体名称查询")
        logger.info("   MATCH (e:__Entity__ {id: '层析液'}) RETURN e")
        logger.info("=" * 70)
        
    except Exception as e:
        logger.error(f"❌ 导入过程中发生错误: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        importer.close()


if __name__ == "__main__":
    main()
