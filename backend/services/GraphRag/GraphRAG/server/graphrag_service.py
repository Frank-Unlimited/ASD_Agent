#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GraphRAG Query Service
FastAPI service wrapping GraphRAG query functionality
"""

import asyncio
import logging
import os
from pathlib import Path
from typing import Optional, Any, List
import threading

from fastapi import FastAPI, HTTPException, Query, UploadFile, File, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pandas as pd
import shutil
import subprocess
import uuid
from datetime import datetime
import yaml

# Load environment variables from data/.env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../data/.env"))

# Import OpenAI for LLM calls
from openai import AsyncOpenAI
import base64
import requests

# Import GraphRAG modules
import graphrag.api as api
from graphrag.config.load_config import load_config
from graphrag.callbacks.noop_query_callbacks import NoopQueryCallbacks
from graphrag.utils.storage import load_table_from_storage
from graphrag.storage.file_pipeline_storage import FilePipelineStorage
from graphrag.config.enums import IndexingMethod
from graphrag.logger.base import ProgressLogger

# ========================================
# Configuration
# ========================================

PROJECT_DIR = os.getenv("GRAPHRAG_PROJECT_DIR", "/Users/fengguihuan/Desktop/HHC/graphrag")
DATA_DIR_NAME = os.getenv("GRAPHRAG_DATA_DIR", "data")

# Access Key 配置
QUERY_ACCESS_KEY = "hanhaochen"  # 查询权限
UPDATE_ACCESS_KEY = "duping"     # 更新权限

# LLM 配置（从 .env 加载）
LLM_API_BASE = os.getenv("GRAPHRAG_API_BASE", "https://ark.cn-beijing.volces.com/api/v3")
LLM_API_KEY = os.getenv("GRAPHRAG_API_KEY", "")
LLM_MODEL_NAME = os.getenv("GRAPHRAG_MODEL_NAME", "doubao-1-5-lite-32k-250115")

# 初始化 OpenAI 客户端（兼容豆包 API）
openai_client = AsyncOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_API_BASE
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 调试日志 - 在初始化客户端之前
logger.info(f"LLM Configuration:")
logger.info(f"  API Base: {LLM_API_BASE}")
logger.info(f"  API Key: {'*' * 20 if LLM_API_KEY else 'NOT SET'}")
logger.info(f"  Model: {LLM_MODEL_NAME}")

# Data cache
data_cache = {}

# ========================================
# Access Key 鉴权函数
# ========================================

def verify_query_access(access_key: Optional[str] = None) -> bool:
    """验证查询权限"""
    if not access_key:
        return False
    return access_key == QUERY_ACCESS_KEY

def verify_update_access(access_key: Optional[str] = None) -> bool:
    """验证更新权限"""
    if not access_key:
        return False
    return access_key == UPDATE_ACCESS_KEY

# ========================================
# FastAPI Application
# ========================================

app = FastAPI(
    title="GraphRAG Query Service",
    description="FastAPI service for GraphRAG queries",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ========================================
# Request/Response Models
# ========================================

class QueryRequest(BaseModel):
    query: str = Field(..., description="Query text")
    query_type: str = Field(default="local", description="Query type: local, global, drift, basic")
    response_type: str = Field(default="text", description="Response type: text, json")
    community_level: int = Field(default=1, description="Community level")
    dynamic_community_selection: bool = Field(default=False, description="Enable dynamic community selection")
    access_key: Optional[str] = Field(None, description="Access key for authentication")

class QueryResponse(BaseModel):
    query: str
    response: str
    query_type: str
    context: str = ""

class IndexUpdateResponse(BaseModel):
    status: str
    message: str
    task_id: str = ""
    file_name: str = ""
    file_type: str = ""

class NLToCypherRequest(BaseModel):
    question: str = Field(..., description="Natural language question")
    neo4j_url: str = Field(..., description="Neo4j HTTP API URL")
    neo4j_user: str = Field(default="neo4j", description="Neo4j username")
    neo4j_password: str = Field(..., description="Neo4j password")
    access_key: Optional[str] = Field(None, description="Access key for authentication")

class NLToCypherResponse(BaseModel):
    question: str
    cypher: str
    results: Any
    explanation: str = ""

# 索引任务状态跟踪
index_tasks = {}

# ========================================
# NL to Cypher Functions
# ========================================

def get_neo4j_schema(neo4j_url: str, username: str, password: str) -> dict:
    """获取 Neo4j 图谱的 schema 信息"""
    try:
        # 确保 URL 有协议
        if not neo4j_url.startswith('http://') and not neo4j_url.startswith('https://'):
            neo4j_url = 'http://' + neo4j_url
        
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth}',
            'Accept': 'application/json'
        }
        
        schema_info = {
            'node_labels': [],
            'relationship_types': [],
            'node_properties': {},
            'relationship_properties': {}
        }
        
        # 获取节点标签
        response = requests.post(
            f"{neo4j_url}/tx/commit",
            headers=headers,
            json={
                "statements": [{
                    "statement": "CALL db.labels()",
                    "resultDataContents": ["row"]
                }]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and data['results'][0].get('data'):
                schema_info['node_labels'] = [row['row'][0] for row in data['results'][0]['data']]
        
        # 获取关系类型
        response = requests.post(
            f"{neo4j_url}/tx/commit",
            headers=headers,
            json={
                "statements": [{
                    "statement": "CALL db.relationshipTypes()",
                    "resultDataContents": ["row"]
                }]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and data['results'][0].get('data'):
                schema_info['relationship_types'] = [row['row'][0] for row in data['results'][0]['data']]
        
        # 获取节点属性示例
        response = requests.post(
            f"{neo4j_url}/tx/commit",
            headers=headers,
            json={
                "statements": [{
                    "statement": """
                        MATCH (n)
                        WITH labels(n) AS labels, keys(n) AS props
                        UNWIND labels AS label
                        RETURN DISTINCT label, props
                        LIMIT 20
                    """,
                    "resultDataContents": ["row"]
                }]
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and data['results'][0].get('data'):
                for row in data['results'][0]['data']:
                    label = row['row'][0]
                    props = row['row'][1]
                    if label not in schema_info['node_properties']:
                        schema_info['node_properties'][label] = set()
                    schema_info['node_properties'][label].update(props)
        
        # 转换 set 为 list
        for label in schema_info['node_properties']:
            schema_info['node_properties'][label] = list(schema_info['node_properties'][label])
        
        return schema_info
        
    except Exception as e:
        logger.error(f"Error getting Neo4j schema: {str(e)}")
        return {
            'node_labels': ['__Entity__', '__Chunk__', '__Relationship__'],
            'relationship_types': ['RELATED_TO', 'HAS_CHUNK'],
            'node_properties': {
                '__Entity__': ['name', 'description', 'type', 'rank', 'degree'],
                '__Chunk__': ['text', 'n_tokens', 'id'],
                '__Relationship__': ['description', 'source_id', 'target_id']
            },
            'relationship_properties': {}
        }

def build_cypher_prompt(question: str, schema: dict) -> str:
    """构建 Cypher 生成的 prompt"""
    
    node_labels_str = ", ".join(schema['node_labels'][:10])  # 限制数量
    rel_types_str = ", ".join(schema['relationship_types'][:10])
    
    # 构建节点属性说明
    node_props_str = ""
    for label, props in list(schema['node_properties'].items())[:5]:
        node_props_str += f"  - {label}: {', '.join(props[:10])}\n"
    
    prompt = f"""你是一个 Neo4j Cypher 查询专家。根据用户的自然语言问题，生成对应的 Cypher 查询语句。

## 图谱 Schema 信息：

### 节点标签：
{node_labels_str}

### 关系类型：
{rel_types_str}

### 节点属性示例：
{node_props_str}

## GraphRAG 数据模型说明：
- **__Entity__**: 实体节点，包含 name, description, type, human_readable_id 等属性
  - ID 属性：`id`（字符串类型）和 `human_readable_id`（数字类型）
  - 查询时建议同时尝试两种：WHERE n.id = '细胞' OR n.human_readable_id = 1699
- **__Chunk__**: 文本块节点，包含 text, n_tokens, entity_ids, relationship_ids 等属性
  - 通过 MENTIONS 关系连接到实体
  - 通过 HAS_RELATIONSHIP 关系连接到关系节点
  - 通过 PART_OF 关系连接到文档
- **__Relationship__**: 关系元数据节点（注意：这是节点不是边），包含 description, source, target, human_readable_id 等属性
- **__Document__**: 文档节点，表示原始文档
- **__Community__**: 社区节点，表示实体的聚类
- 图数据库中的边（关系）类型：
  - RELATED_TO: 实体之间的关系边
  - MENTIONS: 文本块提到实体
  - HAS_RELATIONSHIP: 文本块包含关系
  - PART_OF: 文本块属于文档
  - BELONGS_TO: 实体属于社区

## 重要规则：
1. **只返回一个 Cypher 查询语句，不要返回多个查询**
2. **不要有任何解释或额外文字**
3. 使用 LIMIT 限制返回结果数量（默认 100，最多 200）
4. 确保查询语法正确，使用标准 Cypher 语法
5. 优先使用索引字段（如 name, id, title）
6. 对于模糊匹配使用 CONTAINS 而不是 =
7. 返回图数据时使用 RETURN n, r, m 格式（节点和关系）
8. **数字类型的属性值不要加引号**（例如：human_readable_id: 5573）
9. **字符串类型的属性值必须加引号**（例如：name: '细胞'）

## 节点类型识别规则（非常重要！）：
10. **如果用户只问"实体"**，仅查询 __Entity__ 标签
11. **如果用户只问"文本"或"内容"或"文本块"**，仅查询 __Chunk__ 标签
12. **如果用户只问"关系"**，查询 __Relationship__ 节点
13. **如果用户只问"文档"**，查询 __Document__ 标签
14. **如果用户只问"社区"**，查询 __Community__ 标签

## 多节点类型查询规则（最重要！）：
15. **当用户使用以下关键词时，必须同时搜索 __Entity__、__Chunk__ 和 __Relationship__ 三种节点：**
    - "所有节点"
    - "所有相关节点"
    - "相关的所有节点"
    - "与X相关的节点"
    - "找出所有与X相关的"
    - "查找所有包含X的"
    
16. **多节点类型查询的标准模式（必须遵守）：**
    ```
    MATCH (n)
    WHERE (n:__Entity__ OR n:__Chunk__ OR n:__Relationship__)
      AND (
        n.name CONTAINS '关键词' OR 
        n.text CONTAINS '关键词' OR 
        n.description CONTAINS '关键词'
      )
    OPTIONAL MATCH (n)-[r]-(m)
    RETURN n, r, m
    LIMIT 100
    ```
    
17. **注意事项：**
    - 不要只查询 __Entity__，必须包含所有三种节点类型
    - 使用 OR 连接不同节点的属性字段（name, text, description）
    - 使用 OPTIONAL MATCH 获取节点之间的关系
    - 确保 RETURN 语句包含 n, r, m 以返回完整的图结构

## 常见查询模式示例：

### 单一节点类型查询：
- 仅查找实体: MATCH (n:__Entity__) WHERE n.name CONTAINS '关键词' RETURN n LIMIT 50
- 根据 human_readable_id 查找实体: MATCH (n:__Entity__) WHERE n.human_readable_id = 1699 RETURN n
- 仅查找文本块: MATCH (n:__Chunk__) WHERE n.text CONTAINS '关键词' RETURN n LIMIT 50
- 仅查找关系节点: MATCH (r:__Relationship__) WHERE r.description CONTAINS '关键词' RETURN r LIMIT 50

### 多节点类型查询（重点！）：
- **找出所有与"滤纸条"相关的节点（正确示例）**:
  ```
  MATCH (n)
  WHERE (n:__Entity__ OR n:__Chunk__ OR n:__Relationship__)
    AND (n.name CONTAINS '滤纸条' OR n.text CONTAINS '滤纸条' OR n.description CONTAINS '滤纸条')
  OPTIONAL MATCH (n)-[r]-(m)
  RETURN n, r, m
  LIMIT 100
  ```

- **查找所有包含"细胞"的节点及其关系（正确示例）**:
  ```
  MATCH (n)
  WHERE (n:__Entity__ OR n:__Chunk__ OR n:__Relationship__)
    AND (n.name CONTAINS '细胞' OR n.text CONTAINS '细胞' OR n.description CONTAINS '细胞')
  OPTIONAL MATCH (n)-[r]-(m)
  RETURN n, r, m
  LIMIT 100
  ```

### 特定关系查询：
- 查找实体及其图边关系: MATCH (n:__Entity__)-[r:RELATED_TO]-(m:__Entity__) WHERE n.name CONTAINS '关键词' RETURN n, r, m LIMIT 50
- 查找实体及其相关文本块: MATCH (e:__Entity__)<-[:MENTIONS]-(c:__Chunk__) WHERE e.human_readable_id = 1699 RETURN e, c LIMIT 50

## 用户问题：
{question}

## Cypher 查询：
"""
    return prompt

def fix_cypher_syntax(cypher: str) -> str:
    """修复常见的 Cypher 语法错误"""
    # 修复 MATCH (n:Label1 OR Label2) 这种错误语法
    # 正确语法应该是 MATCH (n) WHERE (n:Label1 OR n:Label2)
    import re
    
    # 查找 MATCH (变量:标签1 OR 标签2 ...) 模式
    pattern = r'MATCH\s+\((\w+):([^)]+)\)'
    
    def replace_match(match):
        var = match.group(1)
        labels_part = match.group(2)
        
        # 如果包含 OR，需要重写
        if ' OR ' in labels_part.upper():
            # 提取所有标签
            labels = re.split(r'\s+OR\s+', labels_part, flags=re.IGNORECASE)
            labels = [l.strip().split(':')[-1].strip() for l in labels]
            
            # 构建新的 WHERE 子句
            conditions = [f"{var}:{label}" for label in labels if label]
            where_clause = ' OR '.join(conditions)
            
            return f'MATCH ({var}) WHERE ({where_clause})'
        
        return match.group(0)
    
    cypher = re.sub(pattern, replace_match, cypher)
    
    return cypher

def fix_numeric_values(cypher: str) -> str:
    """修复数字类型被错误加引号的问题"""
    import re
    
    # 常见的数字类型属性名
    numeric_properties = [
        'id', 'human_readable_id', 'rank', 'degree', 'n_tokens', 
        'level', 'size', 'count', 'weight', 'score'
    ]
    
    # 为每个数字属性修复引号问题
    for prop in numeric_properties:
        # 匹配模式: property: '数字' 或 property: "数字"
        # 替换为: property: 数字
        pattern = rf'({prop}\s*:\s*)["\'](\d+)["\']'
        cypher = re.sub(pattern, r'\1\2', cypher)
    
    return cypher

async def generate_cypher_with_llm(prompt: str) -> str:
    """调用 LLM 生成 Cypher 查询"""
    try:
        response = await openai_client.chat.completions.create(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": "你是一个 Neo4j Cypher 查询专家。只返回一个 Cypher 查询语句，不要有任何解释。注意：数字类型的属性值不要加引号（如 id: 123），字符串类型的属性值必须加引号（如 name: '张三'）。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # 低温度保证稳定性
            max_tokens=500
        )
        
        cypher = response.choices[0].message.content.strip()
        
        # 清理可能的 markdown 代码块标记
        cypher = cypher.replace("```cypher", "").replace("```sql", "").replace("```", "").strip()
        
        # 如果有多个 MATCH 语句，只保留第一个完整的查询
        # 查找第一个 MATCH 到第一个 LIMIT 或 RETURN 的完整语句
        if cypher.upper().count('MATCH') > 1:
            # 找到第一个 MATCH 的位置
            first_match = cypher.upper().find('MATCH')
            # 找到第一个 LIMIT 后面的位置
            first_limit = cypher.upper().find('LIMIT', first_match)
            if first_limit != -1:
                # 找到 LIMIT 后面的数字
                limit_end = first_limit + 5  # "LIMIT" 长度
                while limit_end < len(cypher) and (cypher[limit_end].isdigit() or cypher[limit_end].isspace()):
                    limit_end += 1
                cypher = cypher[first_match:limit_end].strip()
            else:
                # 如果没有 LIMIT，找第一个 RETURN 后的换行或第二个 MATCH
                second_match = cypher.upper().find('MATCH', first_match + 5)
                if second_match != -1:
                    cypher = cypher[first_match:second_match].strip()
        
        # 移除可能的解释文字（只保留 MATCH/CREATE/MERGE 等开头的语句）
        lines = cypher.split('\n')
        cypher_lines = []
        for line in lines:
            line = line.strip()
            if line and (
                line.upper().startswith('MATCH') or 
                line.upper().startswith('RETURN') or
                line.upper().startswith('WHERE') or
                line.upper().startswith('WITH') or
                line.upper().startswith('LIMIT') or
                line.upper().startswith('ORDER') or
                line.upper().startswith('CREATE') or
                line.upper().startswith('MERGE') or
                line.upper().startswith('OPTIONAL') or
                line.upper().startswith('UNWIND') or
                line.upper().startswith('CALL')
            ):
                cypher_lines.append(line)
        
        if cypher_lines:
            cypher = ' '.join(cypher_lines)
        
        # 修复常见的语法错误
        cypher = fix_cypher_syntax(cypher)
        
        # 修复数字类型被错误加引号的问题
        cypher = fix_numeric_values(cypher)
        
        logger.info(f"Generated Cypher: {cypher}")
        return cypher
        
    except Exception as e:
        logger.error(f"Error generating Cypher with LLM: {str(e)}")
        raise HTTPException(status_code=500, detail=f"LLM 调用失败: {str(e)}")

def execute_neo4j_cypher(cypher: str, neo4j_url: str, username: str, password: str) -> dict:
    """执行 Cypher 查询"""
    try:
        # 确保 URL 有协议
        if not neo4j_url.startswith('http://') and not neo4j_url.startswith('https://'):
            neo4j_url = 'http://' + neo4j_url
        
        auth = base64.b64encode(f"{username}:{password}".encode()).decode()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {auth}',
            'Accept': 'application/json'
        }
        
        response = requests.post(
            f"{neo4j_url}/tx/commit",
            headers=headers,
            json={
                "statements": [{
                    "statement": cypher,
                    "resultDataContents": ["row", "graph"]
                }]
            },
            timeout=30
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Neo4j 查询失败: {response.text}")
        
        data = response.json()
        
        # 检查错误
        if data.get('errors') and len(data['errors']) > 0:
            error_msg = data['errors'][0].get('message', 'Unknown error')
            raise HTTPException(status_code=400, detail=f"Cypher 查询错误: {error_msg}")
        
        return data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing Cypher: {str(e)}")
        raise HTTPException(status_code=500, detail=f"执行查询失败: {str(e)}")

# ========================================
# Data Loading
# ========================================

async def load_data():
    """Load GraphRAG data into cache"""
    global data_cache
    
    if data_cache:
        return data_cache
    
    try:
        project_path = os.path.join(PROJECT_DIR, DATA_DIR_NAME)
        logger.info(f"Loading configuration from: {project_path}")
        
        # Load config
        graphrag_config = load_config(Path(project_path))
        
        # Get output directory
        output_dir = Path(graphrag_config.output.base_dir)
        if not output_dir.is_absolute():
            output_dir = Path(project_path) / output_dir
        
        logger.info(f"Using output directory: {output_dir}")
        
        # Create storage
        storage = FilePipelineStorage(root_dir=str(output_dir))
        
        # Load data tables
        logger.info("Loading data tables...")
        entities = await load_table_from_storage("entities", storage)
        logger.info(f"Loaded {len(entities)} entities")
        
        text_units = await load_table_from_storage("text_units", storage)
        logger.info(f"Loaded {len(text_units)} text units")
        
        communities = await load_table_from_storage("communities", storage)
        logger.info(f"Loaded {len(communities)} communities")
        
        community_reports = await load_table_from_storage("community_reports", storage)
        logger.info(f"Loaded {len(community_reports)} community reports")
        
        relationships = await load_table_from_storage("relationships", storage)
        logger.info(f"Loaded {len(relationships)} relationships")
        
        # Load covariates (optional)
        try:
            covariates = await load_table_from_storage("covariates", storage)
            logger.info(f"Loaded {len(covariates)} covariates")
        except Exception:
            covariates = None
            logger.info("No covariates found")
        
        # Cache data
        data_cache = {
            "config": graphrag_config,
            "entities": entities,
            "text_units": text_units,
            "communities": communities,
            "community_reports": community_reports,
            "relationships": relationships,
            "covariates": covariates
        }
        
        logger.info("Data loading complete")
        return data_cache
        
    except Exception as e:
        logger.error(f"Error loading data: {str(e)}", exc_info=True)
        raise

# ========================================
# Query Execution
# ========================================

async def execute_query(
    query: str,
    query_type: str = "local",
    response_type: str = "text",
    community_level: int = 1,
    dynamic_community_selection: bool = False
) -> dict:
    """Execute GraphRAG query"""
    try:
        data = await load_data()
        
        # Setup callbacks
        context_data = {}
        
        def on_context(context):
            nonlocal context_data
            context_data = context
        
        callbacks = NoopQueryCallbacks()
        callbacks.on_context = on_context
        
        logger.info(f"Executing {query_type} query: {query}")
        
        # Execute query based on type
        if query_type.lower() == "local":
            response, context = await api.local_search(
                config=data["config"],
                entities=data["entities"],
                communities=data["communities"],
                community_reports=data["community_reports"],
                text_units=data["text_units"],
                relationships=data["relationships"],
                covariates=data["covariates"],
                community_level=community_level,
                response_type=response_type,
                query=query,
                callbacks=[callbacks]
            )
        
        elif query_type.lower() == "global":
            response, context = await api.global_search(
                config=data["config"],
                entities=data["entities"],
                communities=data["communities"],
                community_reports=data["community_reports"],
                community_level=community_level,
                dynamic_community_selection=dynamic_community_selection,
                response_type=response_type,
                query=query,
                callbacks=[callbacks]
            )
        
        elif query_type.lower() == "drift":
            response, context = await api.drift_search(
                config=data["config"],
                entities=data["entities"],
                communities=data["communities"],
                community_reports=data["community_reports"],
                text_units=data["text_units"],
                relationships=data["relationships"],
                community_level=community_level,
                response_type=response_type,
                query=query,
                callbacks=[callbacks]
            )
        
        elif query_type.lower() == "basic":
            response, context = await api.basic_search(
                config=data["config"],
                text_units=data["text_units"],
                query=query,
                callbacks=[callbacks]
            )
        
        else:
            raise ValueError(f"Unsupported query type: {query_type}")
        
        logger.info("Query completed successfully")
        
        # 🔍 DEBUG: 打印上下文数据用于调试
        logger.info(f"Context data type: {type(context_data)}")
        logger.info(f"Context data keys: {context_data.keys() if isinstance(context_data, dict) else 'Not a dict'}")
        if isinstance(context_data, dict):
            for key, value in context_data.items():
                logger.info(f"Context[{key}]: {type(value)} - {str(value)[:200]}")
        
        return {
            "query": query,
            "response": response,
            "query_type": query_type,
            "context": str(context_data)
        }
    
    except Exception as e:
        logger.error(f"Query execution error: {str(e)}", exc_info=True)
        raise

# ========================================
# API Endpoints
# ========================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint - redirect to test page"""
    static_index = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_index):
        with open(static_index, 'r', encoding='utf-8') as f:
            return f.read()
    return """
    <html>
        <body>
            <h1>GraphRAG Query Service</h1>
            <p>Service is running. Visit <a href="/docs">/docs</a> for API documentation.</p>
        </body>
    </html>
    """

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/api/nl-to-cypher", response_model=NLToCypherResponse)
async def nl_to_cypher(request: NLToCypherRequest):
    """
    自然语言转 Cypher 查询
    
    使用 LLM 将自然语言问题转换为 Cypher 查询语句，并执行查询返回结果。
    
    Parameters:
    - question: 自然语言问题
    - neo4j_url: Neo4j HTTP API URL
    - neo4j_user: Neo4j 用户名
    - neo4j_password: Neo4j 密码
    - access_key: 访问密钥（需要查询权限）
    
    Returns:
    - NLToCypherResponse 包含生成的 Cypher、查询结果和解释
    """
    # 验证访问权限
    if not verify_query_access(request.access_key):
        logger.warning(f"Unauthorized NL to Cypher attempt with access_key: {request.access_key}")
        raise HTTPException(
            status_code=403, 
            detail="访问被拒绝：无效的访问密钥。需要有效的 access_key"
        )
    
    try:
        logger.info(f"NL to Cypher request: {request.question}")
        
        # 1. 获取 Neo4j schema
        logger.info("Getting Neo4j schema...")
        schema = get_neo4j_schema(
            request.neo4j_url,
            request.neo4j_user,
            request.neo4j_password
        )
        
        # 2. 构建 prompt
        logger.info("Building prompt...")
        prompt = build_cypher_prompt(request.question, schema)
        
        # 3. 调用 LLM 生成 Cypher
        logger.info("Generating Cypher with LLM...")
        cypher_query = await generate_cypher_with_llm(prompt)
        
        # 4. 执行 Cypher 查询
        logger.info(f"Executing Cypher: {cypher_query}")
        results = execute_neo4j_cypher(
            cypher_query,
            request.neo4j_url,
            request.neo4j_user,
            request.neo4j_password
        )
        
        # 5. 返回结果
        return NLToCypherResponse(
            question=request.question,
            cypher=cypher_query,
            results=results,
            explanation=f"已将自然语言问题转换为 Cypher 查询并执行"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"NL to Cypher error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")

@app.get("/api/query", response_model=QueryResponse)
async def query_get(
    query: str = Query(..., description="Query text"),
    query_type: str = Query("local", description="Query type: local, global, drift, basic"),
    response_type: str = Query("text", description="Response type: text, json"),
    community_level: int = Query(1, description="Community level (1-3)"),
    dynamic_community_selection: bool = Query(False, description="Enable dynamic community selection"),
    access_key: Optional[str] = Query(None, description="Access key for authentication")
):
    """
    Execute GraphRAG query (GET method)
    
    Parameters:
    - query: The search query text
    - query_type: Type of search (local, global, drift, basic)
    - response_type: Format of response (text, json)
    - community_level: Community hierarchy level to search
    - dynamic_community_selection: Use dynamic community selection for global search
    - access_key: Access key for authentication (required: 'hanhaochen')
    
    Returns:
    - QueryResponse with query results and context
    """
    # 验证访问权限
    if not verify_query_access(access_key):
        logger.warning(f"Unauthorized query attempt with access_key: {access_key}")
        raise HTTPException(
            status_code=403, 
            detail="访问被拒绝：无效的访问密钥。查询需要有效的 access_key"
        )
    
    try:
        result = await execute_query(
            query=query,
            query_type=query_type,
            response_type=response_type,
            community_level=community_level,
            dynamic_community_selection=dynamic_community_selection
        )
        return JSONResponse(content=result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_post(request: QueryRequest):
    """
    Execute GraphRAG query (POST method)
    
    Request body should contain QueryRequest model with query parameters.
    Requires access_key='hanhaochen' for authentication.
    """
    # 验证访问权限
    if not verify_query_access(request.access_key):
        logger.warning(f"Unauthorized query attempt with access_key: {request.access_key}")
        raise HTTPException(
            status_code=403, 
            detail="访问被拒绝：无效的访问密钥。查询需要有效的 access_key"
        )
    
    try:
        result = await execute_query(
            query=request.query,
            query_type=request.query_type,
            response_type=request.response_type,
            community_level=request.community_level,
            dynamic_community_selection=request.dynamic_community_selection
        )
        return JSONResponse(content=result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"API error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

# ========================================
# Startup
# ========================================

@app.on_event("startup")
async def startup_event():
    """Preload data on startup"""
    logger.info("Starting GraphRAG Query Service...")
    try:
        await load_data()
        logger.info("Service ready")
    except Exception as e:  
        logger.error(f"Startup failed: {str(e)}", exc_info=True)

# ========================================
# Index Update Functions
# ========================================

def run_index_update(file_path: str, file_type: str, task_id: str):
    """Run GraphRAG index update in background using Python API"""
    task_log_file = None
    task_logger = None
    
    try:
        # 创建任务专属日志文件
        data_dir = os.path.join(PROJECT_DIR, DATA_DIR_NAME)
        logs_dir = os.path.join(data_dir, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        
        task_log_file = os.path.join(logs_dir, f"task_{task_id}.log")
        
        # 创建任务专属的 logger
        task_logger = logging.getLogger(f"task_{task_id}")
        task_logger.setLevel(logging.INFO)
        task_logger.handlers = []  # 清除已有的 handlers
        
        # 添加文件 handler
        file_handler = logging.FileHandler(task_log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        task_logger.addHandler(file_handler)
        
        def log_to_file(message, level='info'):
            """写入任务日志"""
            if level == 'error':
                task_logger.error(message)
            elif level == 'warning':
                task_logger.warning(message)
            else:
                task_logger.info(message)
            logger.info(f"Task {task_id}: {message}")
        
        index_tasks[task_id]["status"] = "running"
        index_tasks[task_id]["message"] = "正在更新索引..."
        index_tasks[task_id]["log_file"] = task_log_file
        
        log_to_file("=" * 80)
        log_to_file(f"开始索引更新任务")
        log_to_file(f"任务ID: {task_id}")
        log_to_file(f"文件路径: {file_path}")
        log_to_file(f"文件类型: {file_type}")
        log_to_file("=" * 80)
        
        # 确定使用哪个配置文件（直接使用静态配置）
        if file_type == "pdf":
            config_file = "settings_pdf.yaml"
            log_to_file(f"使用 PDF 配置文件: {config_file}")
        else:
            config_file = "settings.yaml"
            log_to_file(f"使用文本配置文件: {config_file}")
        
        config_path = os.path.join(data_dir, config_file)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        log_to_file(f"使用配置文件: {config_path}")
        log_to_file("开始执行 GraphRAG 索引更新（使用 Python API）...")
        log_to_file("-" * 80)
        
        # 使用 Python API 而不是命令行
        from graphrag.config.enums import IndexingMethod
        from graphrag.logger.base import ProgressLogger
        from graphrag.logger.progress import Progress
        
        # 创建自定义进度记录器，将输出写入日志文件
        class TaskProgressLogger(ProgressLogger):
            def __init__(self, log_func):
                self.log_func = log_func
                self._disposed = False
                
            def __call__(self, update: Progress):
                """处理进度更新"""
                if update.description:
                    message = update.description
                elif update.percent is not None:
                    message = f"进度: {update.percent * 100:.1f}%"
                elif update.completed_items is not None and update.total_items is not None:
                    message = f"进度: {update.completed_items}/{update.total_items}"
                else:
                    message = str(update)
                self.log_func(f"PROGRESS: {message}")
                
            def child(self, prefix: str, transient: bool = True) -> "TaskProgressLogger":
                """创建子记录器"""
                # 创建一个新的子记录器，带有前缀
                child_logger = TaskProgressLogger(self.log_func)
                child_logger.log_func(f"开始子任务: {prefix}")
                return child_logger
                
            def dispose(self):
                """清理资源"""
                self._disposed = True
                
            def force_refresh(self) -> None:
                """强制刷新"""
                pass
                
            def stop(self) -> None:
                """停止记录"""
                self._disposed = True
                
            def info(self, message: str) -> None:
                self.log_func(f"INFO: {message}")
                
            def error(self, message: str) -> None:
                self.log_func(f"ERROR: {message}", 'error')
                
            def warning(self, message: str) -> None:
                self.log_func(f"WARNING: {message}", 'warning')
                
            def success(self, message: str) -> None:
                self.log_func(f"SUCCESS: {message}")
        
        progress_logger = TaskProgressLogger(log_to_file)
        
        # 加载配置（直接使用静态配置文件）
        from graphrag.config.load_config import load_config
        log_to_file(f"加载配置文件: {config_path}")
        graphrag_config = load_config(Path(data_dir), Path(config_path))
        
        log_to_file("配置加载成功")
        
        # 检查是否存在现有的索引文件
        # 使用配置中的输出目录
        output_base_dir = graphrag_config.output.base_dir
        if not os.path.isabs(output_base_dir):
            output_dir = os.path.join(data_dir, output_base_dir)
        else:
            output_dir = output_base_dir
            
        entities_file = os.path.join(output_dir, "entities.parquet")
        has_existing_index = os.path.exists(entities_file)
        
        log_to_file(f"检查输出目录: {output_dir}")
        log_to_file(f"检查索引文件: {entities_file}")
        
        if has_existing_index:
            log_to_file(f"✓ 检测到现有索引文件")
            log_to_file("将执行增量更新（仅处理新文档）")
        else:
            log_to_file("✗ 未检测到现有索引")
            log_to_file("将执行完整索引构建")
            log_to_file("警告：首次构建可能需要较长时间！")
        
        log_to_file("开始构建索引...")
        
        # 运行索引构建（使用 asyncio）
        import asyncio
        
        async def build_index_async():
            log_to_file("调用 api.build_index...")
            result = await api.build_index(
                config=graphrag_config,
                method=IndexingMethod.Standard,
                is_update_run=has_existing_index,  # 只有存在索引时才增量更新
                memory_profile=False,
                progress_logger=progress_logger
            )
            return result
        
        # 在新的事件循环中运行
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            index_result = loop.run_until_complete(build_index_async())
            loop.close()
        except Exception as e:
            log_to_file(f"索引构建异常: {str(e)}", 'error')
            raise
        
        log_to_file("-" * 80)
        log_to_file("索引构建完成，处理结果:")
        
        # 处理结果
        has_error = False
        for workflow_result in index_result:
            if workflow_result.errors:
                has_error = True
                log_to_file(f"工作流 [{workflow_result.workflow}] 失败:", 'error')
                for error in workflow_result.errors:
                    log_to_file(f"  错误: {error}", 'error')
            else:
                log_to_file(f"工作流 [{workflow_result.workflow}] 成功")
        
        return_code = 1 if has_error else 0
        log_to_file(f"索引构建完成，返回码: {return_code}")
        
        if return_code == 0:
            log_to_file("✅ 索引更新成功！")
            index_tasks[task_id]["status"] = "completed"
            index_tasks[task_id]["message"] = "索引更新成功！"
            
            # 读取完整日志作为输出
            with open(task_log_file, 'r', encoding='utf-8') as f:
                index_tasks[task_id]["output"] = f.read()
            
            logger.info(f"Index update completed for task {task_id}")
            
            # 清除数据缓存，强制重新加载
            global data_cache
            data_cache = {}
            log_to_file("数据缓存已清除，下次查询将重新加载")
        else:
            log_to_file(f"❌ 索引更新失败，返回码: {return_code}")
            index_tasks[task_id]["status"] = "failed"
            index_tasks[task_id]["message"] = f"索引更新失败，返回码: {return_code}"
            
            # 读取完整日志作为输出
            with open(task_log_file, 'r', encoding='utf-8') as f:
                index_tasks[task_id]["output"] = f.read()
            
            logger.error(f"Index update failed for task {task_id}, return code: {return_code}")
            
    except subprocess.TimeoutExpired:
        if task_log_file:
            log_to_file("❌ 索引更新超时（超过1小时）")
        index_tasks[task_id]["status"] = "failed"
        index_tasks[task_id]["message"] = "索引更新超时（超过1小时）"
        logger.error(f"Index update timeout for task {task_id}")
        
        if task_log_file and os.path.exists(task_log_file):
            with open(task_log_file, 'r', encoding='utf-8') as f:
                index_tasks[task_id]["output"] = f.read()
                
    except Exception as e:
        if task_log_file:
            log_to_file(f"❌ 索引更新出错: {str(e)}")
            log_to_file(f"错误详情: {repr(e)}")
        index_tasks[task_id]["status"] = "failed"
        index_tasks[task_id]["message"] = f"索引更新出错: {str(e)}"
        logger.error(f"Index update error for task {task_id}: {str(e)}", exc_info=True)
        
        if task_log_file and os.path.exists(task_log_file):
            with open(task_log_file, 'r', encoding='utf-8') as f:
                index_tasks[task_id]["output"] = f.read()
                
    finally:
        if task_log_file and task_logger:
            log_to_file("=" * 80)
            log_to_file(f"任务结束，最终状态: {index_tasks[task_id]['status']}")
            log_to_file("=" * 80)
            
            # 关闭 logger handlers
            for handler in task_logger.handlers[:]:
                handler.close()
                task_logger.removeHandler(handler)

# ========================================
# Index Update Endpoints
# ========================================

@app.post("/api/upload", response_model=IndexUpdateResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    access_key: Optional[str] = Form(None)
):
    """
    上传文件并更新索引
    支持 .txt 和 .pdf 文件
    使用静态配置文件中的参数（settings.yaml 或 settings_pdf.yaml）
    
    Parameters:
    - file: 上传的文件
    - access_key: 访问密钥（需要 'duping' 才能更新索引）
    """
    # 验证更新权限
    if not verify_update_access(access_key):
        logger.warning(f"Unauthorized upload attempt with access_key: {access_key}")
        raise HTTPException(
            status_code=403,
            detail="访问被拒绝：无效的访问密钥。索引更新需要有效的 access_key (duping)"
        )
    
    try:
        # 验证文件类型
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in [".txt", ".pdf"]:
            raise HTTPException(
                status_code=400,
                detail="只支持 .txt 和 .pdf 文件"
            )
        
        file_type = file_ext[1:]  # 去掉点号
        
        # 确定输入目录
        input_dir = os.path.join(PROJECT_DIR, DATA_DIR_NAME, "input")
        os.makedirs(input_dir, exist_ok=True)
        
        # 生成唯一文件名（保留原始扩展名）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join(input_dir, safe_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded: {file_path}")
        
        # 创建任务ID
        task_id = str(uuid.uuid4())
        index_tasks[task_id] = {
            "status": "pending",
            "message": "文件已上传，等待处理...",
            "file_name": file.filename,
            "file_type": file_type,
            "file_path": file_path,
            "created_at": datetime.now().isoformat()
        }
        
        # 在后台运行索引更新
        background_tasks.add_task(
            run_index_update, 
            file_path, 
            file_type, 
            task_id
        )
        
        return IndexUpdateResponse(
            status="accepted",
            message="文件已上传，索引更新已开始",
            task_id=task_id,
            file_name=file.filename,
            file_type=file_type
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

@app.get("/api/index/status/{task_id}")
async def get_index_status(task_id: str):
    """
    查询索引更新任务状态
    """
    if task_id not in index_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return index_tasks[task_id]

@app.get("/api/index/tasks")
async def list_index_tasks():
    """
    列出所有索引更新任务
    """
    return {
        "tasks": [
            {
                "task_id": task_id,
                **task_info
            }
            for task_id, task_info in index_tasks.items()
        ]
    }

@app.get("/api/index/logs/{task_id}")
async def get_index_logs(task_id: str, lines: int = 50):
    """
    获取索引任务的实时日志
    
    Parameters:
    - task_id: 任务ID
    - lines: 返回最后N行日志（默认50行）
    """
    if task_id not in index_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    try:
        # 优先使用任务专属日志文件
        task_log_file = index_tasks[task_id].get("log_file")
        log_dir = os.path.join(PROJECT_DIR, DATA_DIR_NAME, "logs")
        
        # 如果没有专属日志文件，尝试查找
        if not task_log_file or not os.path.exists(task_log_file):
            task_log_file = os.path.join(log_dir, f"task_{task_id}.log")
        
        # 如果专属日志文件不存在，查找最新的通用日志
        if not os.path.exists(task_log_file):
            log_files = []
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith('.log') and not file.startswith('task_'):
                        file_path = os.path.join(log_dir, file)
                        log_files.append((file_path, os.path.getmtime(file_path)))
            
            if not log_files:
                return {
                    "task_id": task_id,
                    "logs": ["等待任务开始..."],
                    "current_workflow": "等待中",
                    "progress": 0,
                    "log_file": "无"
                }
            
            # 获取最新的日志文件
            task_log_file = sorted(log_files, key=lambda x: x[1], reverse=True)[0][0]
        
        latest_log = task_log_file
        
        # 读取最后N行
        with open(latest_log, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        # 解析当前工作流和进度
        current_workflow = "初始化"
        progress = 0
        
        # GraphRAG 工作流关键词
        workflows = [
            ("create_base_text_units", "创建文本单元", 10),
            ("create_base_extracted_entities", "提取实体", 20),
            ("create_summarized_entities", "总结实体", 30),
            ("create_base_entity_graph", "构建实体图", 40),
            ("create_final_entities", "生成最终实体", 50),
            ("create_final_relationships", "生成关系", 60),
            ("create_final_communities", "创建社区", 70),
            ("create_final_community_reports", "生成社区报告", 80),
            ("create_final_text_units", "生成最终文本单元", 90),
            ("create_final_documents", "生成文档", 95),
        ]
        
        # 从日志中查找当前工作流
        for line in reversed(recent_lines):
            for workflow_key, workflow_name, workflow_progress in workflows:
                if workflow_key in line:
                    current_workflow = workflow_name
                    progress = workflow_progress
                    break
            if progress > 0:
                break
        
        # 检查是否完成
        if any("completed" in line.lower() or "success" in line.lower() for line in recent_lines[-5:]):
            current_workflow = "索引构建完成"
            progress = 100
        
        return {
            "task_id": task_id,
            "logs": [line.strip() for line in recent_lines],
            "current_workflow": current_workflow,
            "progress": progress,
            "log_file": os.path.basename(latest_log)
        }
        
    except Exception as e:
        logger.error(f"Failed to read logs for task {task_id}: {str(e)}")
        return {
            "task_id": task_id,
            "logs": [],
            "current_workflow": f"读取日志失败: {str(e)}",
            "progress": 0
        }

# ========================================
# Main
# ========================================

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    logger.info(f"Starting server at http://{host}:{port}")
    logger.info("Note: Access via Nginx at http://localhost (port 80)")
    uvicorn.run("graphrag_service:app", host=host, port=port, reload=True)
