# GraphRAG 与 Neo4j 集成指南

本文档介绍如何将 GraphRAG 生成的知识图谱数据导入 Neo4j，以及如何实现自然语言到 Cypher 查询的转换。

## 目录

1. [数据导入流程](#数据导入流程)
2. [数据模型设计](#数据模型设计)
3. [NL2Cypher 实现](#nl2cypher-实现)
4. [前端可视化集成](#前端可视化集成)

---

## 数据导入流程

### 1. 导入脚本概述

导入脚本位于 `server/import_to_neo4j.py`，负责将 GraphRAG 生成的 parquet 文件导入到 Neo4j。

### 2. 核心功能

#### 2.1 实体导入

```python
def import_entities(self, entities_df: pd.DataFrame, batch_size: int = 100):
    """
    导入实体节点，使用 human_readable_id 作为 GraphRAG 查询 ID
    """
    # 使用 human_readable_id（GraphRAG 查询结果中的 ID）
    statement = f"""
    MERGE (e:__Entity__ {{id: value.{id_column}}})
    SET e.name = value.{id_column},
        e.type = value.type,
        e.description = value.description,
        e.human_readable_id = value.human_readable_id,
        e.text_unit_ids = value.text_unit_ids
    """
```

**关键点**：
- 使用 `human_readable_id` 字段作为 GraphRAG 查询结果中的实体 ID
- 为 null 值的实体生成唯一 ID：`__NULL_ENTITY_{human_readable_id}`

#### 2.2 关系导入

关系导入分为两步：

**步骤 1：创建 `__Relationship__` 元数据节点**

```python
relationship_node_statement = """
MERGE (r:__Relationship__ {id: value.id})
SET r.human_readable_id = value.human_readable_id,
    r.source = value.source,
    r.target = value.target,
    r.description = value.description,
    r.weight = value.weight
"""
```

**步骤 2：创建实体间的 `RELATED_TO` 边**

```python
relationship_edge_statement = """
MATCH (source:__Entity__ {id: value.source})
MATCH (target:__Entity__ {id: value.target})
MERGE (source)-[r:RELATED_TO]->(target)
SET r.description = value.description,
    r.weight = value.weight,
    r.relationship_id = value.id
"""
```

**关键点**：
- `__Relationship__` 是独立的元数据节点，不是图的边
- `RELATED_TO` 是实体之间的图边
- 两者都需要创建，用于不同的查询场景

#### 2.3 文本块导入

文本块导入分为三步：

**步骤 1：创建文本块节点**

```python
chunk_statement = """
MERGE (t:__Chunk__ {id: value.id})
SET t.text = value.text,
    t.n_tokens = value.n_tokens,
    t.entity_ids = value.entity_ids,
    t.relationship_ids = value.relationship_ids
"""
```

**步骤 2：连接文本块到实体**

```python
entity_link_statement = """
MATCH (t:__Chunk__ {id: value.id})
UNWIND value.entity_ids AS entity_id
MATCH (e:__Entity__ {id: entity_id})
MERGE (t)-[:MENTIONS]->(e)
"""
```

**步骤 3：连接文本块到关系节点**

```python
relationship_link_statement = """
MATCH (t:__Chunk__ {id: value.id})
UNWIND value.relationship_ids AS rel_id
MATCH (r:__Relationship__ {id: rel_id})
MERGE (t)-[:HAS_RELATIONSHIP]->(r)
"""
```

### 3. 性能优化

#### 3.1 并行批量导入

```python
def parallel_batched_import(self, statement: str, df: pd.DataFrame, 
                           batch_size: int = 100, max_workers: int = 1):
    """
    使用线程池并行处理批次
    max_workers=1 避免死锁
    """
```

**关键配置**：
- `batch_size=100`：每批处理 100 行
- `max_workers=1`：串行执行避免 Neo4j 死锁

#### 3.2 索引和约束

```python
# 唯一性约束
constraints = [
    ("graphrag_entity_id", "FOR (e:__Entity__) REQUIRE e.id IS UNIQUE"),
    ("graphrag_relationship_id", "FOR (r:__Relationship__) REQUIRE r.id IS UNIQUE"),
]

# 索引
indexes = [
    ("graphrag_entity_human_readable_id", "FOR (e:__Entity__) ON (e.human_readable_id)"),
    ("graphrag_relationship_human_readable_id", "FOR (r:__Relationship__) ON (r.human_readable_id)"),
]
```

### 4. 运行导入

```bash
conda activate hhc_base
python server/import_to_neo4j.py
```

---

## 数据模型设计

### 节点类型

| 节点类型 | 标签 | 主要属性 | 说明 |
|---------|------|---------|------|
| 实体 | `__Entity__` | `id`, `name`, `human_readable_id`, `type`, `description` | 知识图谱中的实体 |
| 关系元数据 | `__Relationship__` | `id`, `human_readable_id`, `source`, `target`, `description` | 关系的元数据节点 |
| 文本块 | `__Chunk__` | `id`, `text`, `n_tokens`, `entity_ids`, `relationship_ids` | 原始文本片段 |
| 文档 | `__Document__` | `id`, `title`, `raw_content` | 原始文档 |
| 社区 | `__Community__` | `id`, `title`, `level` | 实体聚类 |

### 关系类型

| 关系类型 | 起点 | 终点 | 说明 |
|---------|------|------|------|
| `RELATED_TO` | `__Entity__` | `__Entity__` | 实体间的关系边 |
| `MENTIONS` | `__Chunk__` | `__Entity__` | 文本块提到实体 |
| `HAS_RELATIONSHIP` | `__Chunk__` | `__Relationship__` | 文本块包含关系 |
| `PART_OF` | `__Chunk__` | `__Document__` | 文本块属于文档 |
| `BELONGS_TO` | `__Entity__` | `__Community__` | 实体属于社区 |

### 数据模型图

```
┌─────────────┐
│  __Entity__ │
│  - id       │
│  - name     │
│  - human_   │
│    readable │
│    _id      │
└──────┬──────┘
       │
       │ RELATED_TO (图边)
       │
       ▼
┌─────────────┐      MENTIONS      ┌──────────────┐
│  __Entity__ │◄───────────────────│  __Chunk__   │
└─────────────┘                    │  - text      │
                                   │  - n_tokens  │
                                   └──────┬───────┘
                                          │
                                          │ HAS_RELATIONSHIP
                                          │
                                          ▼
                                   ┌──────────────────┐
                                   │ __Relationship__ │
                                   │ - description    │
                                   │ - human_readable │
                                   │   _id            │
                                   └──────────────────┘
```

---

## NL2Cypher 实现

### 1. 架构概述

NL2Cypher 功能位于 `server/graphrag_service.py`，使用 LLM 将自然语言问题转换为 Cypher 查询。

### 2. 核心流程

```python
@app.post("/api/nl-to-cypher")
async def nl_to_cypher(request: NLToCypherRequest):
    # 1. 获取 Neo4j schema
    schema = get_neo4j_schema(neo4j_url, username, password)
    
    # 2. 构建 prompt
    prompt = build_cypher_prompt(question, schema)
    
    # 3. 调用 LLM 生成 Cypher
    cypher_query = await generate_cypher_with_llm(prompt)
    
    # 4. 执行 Cypher 查询
    results = execute_neo4j_cypher(cypher_query, neo4j_url, username, password)
    
    return results
```

### 3. Prompt 设计

#### 3.1 Prompt 结构

```python
def build_cypher_prompt(question: str, schema: dict) -> str:
    prompt = f"""你是一个 Neo4j Cypher 查询专家。根据用户的自然语言问题，生成对应的 Cypher 查询语句。

## 图谱 Schema 信息：
### 节点标签：
{node_labels_str}

### 关系类型：
{rel_types_str}

### 节点属性示例：
{node_props_str}

## GraphRAG 数据模型说明：
[详细的数据模型说明]

## 重要规则：
[查询生成规则]

## 常见查询模式示例：
[示例查询]

## 用户问题：
{question}

## Cypher 查询：
"""
```

#### 3.2 关键 Prompt 内容

**数据模型说明**：

```
- **__Entity__**: 实体节点，包含 name, description, type, human_readable_id 等属性
  - ID 属性：`id`（字符串类型）和 `human_readable_id`（数字类型）
  
- **__Chunk__**: 文本块节点
  - 通过 MENTIONS 关系连接到实体
  - 通过 HAS_RELATIONSHIP 关系连接到关系节点
  - 通过 PART_OF 关系连接到文档
  
- **__Relationship__**: 关系元数据节点（注意：这是节点不是边）
  - 包含 description, source, target, human_readable_id 等属性
  
- 图数据库中的边（关系）类型：
  - RELATED_TO: 实体之间的关系边
  - MENTIONS: 文本块提到实体
  - HAS_RELATIONSHIP: 文本块包含关系
  - PART_OF: 文本块属于文档
```

**重要规则**：

```
1. 只返回一个 Cypher 查询语句，不要返回多个查询
2. 不要有任何解释或额外文字
3. 使用 LIMIT 限制返回结果数量（默认 50，最多 100）
4. 数字类型的属性值不要加引号（例如：human_readable_id: 5573）
5. 字符串类型的属性值必须加引号（例如：name: '细胞'）

当用户要求"所有相关的X"或"与X相关的所有节点"时：
- 必须在多种节点类型中搜索关键词
- 使用 WHERE 子句同时匹配多种节点类型
- 例如：MATCH (n) WHERE (n:__Entity__ OR n:__Chunk__ OR n:__Relationship__) 
         AND (n.name CONTAINS '关键词' OR n.text CONTAINS '关键词')
```

**常见查询模式示例**：

```cypher
-- 在所有节点类型中搜索关键词
MATCH (n) 
WHERE (n:__Entity__ OR n:__Chunk__ OR n:__Relationship__) 
  AND (n.name CONTAINS '关键词' OR n.text CONTAINS '关键词' OR n.description CONTAINS '关键词') 
RETURN n LIMIT 50

-- 查找与关键词相关的所有节点及其关系
MATCH (n) 
WHERE (n:__Entity__ OR n:__Chunk__ OR n:__Relationship__) 
  AND (n.name CONTAINS '关键词' OR n.text CONTAINS '关键词' OR n.description CONTAINS '关键词') 
OPTIONAL MATCH (n)-[r]-(m) 
RETURN n, r, m LIMIT 100

-- 查找实体的所有相关内容（实体+关系节点+关系边+文本块）
MATCH (e:__Entity__) 
WHERE e.name CONTAINS '关键词' 
OPTIONAL MATCH (e)-[edge:RELATED_TO]-(m:__Entity__) 
OPTIONAL MATCH (chunk:__Chunk__)-[:MENTIONS]->(e) 
OPTIONAL MATCH (chunk)-[:HAS_RELATIONSHIP]->(rel:__Relationship__) 
RETURN e, edge, m, chunk, rel LIMIT 100
```

### 4. Cypher 语法修复

生成的 Cypher 会经过两层修复：

#### 4.1 修复标签语法错误

```python
def fix_cypher_syntax(cypher: str) -> str:
    """
    修复 MATCH (n:Label1 OR Label2) 这种错误语法
    正确语法：MATCH (n) WHERE (n:Label1 OR n:Label2)
    """
```

#### 4.2 修复数字类型引号

```python
def fix_numeric_values(cypher: str) -> str:
    """
    修复数字类型被错误加引号的问题
    例如：human_readable_id: '123' → human_readable_id: 123
    """
```

### 5. LLM 配置

```python
# 使用豆包 API（兼容 OpenAI 格式）
openai_client = AsyncOpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_API_BASE
)

# 生成 Cypher
response = await openai_client.chat.completions.create(
    model=LLM_MODEL_NAME,
    messages=[
        {"role": "system", "content": "你是一个 Neo4j Cypher 查询专家..."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,  # 低温度保证稳定性
    max_tokens=500
)
```

---

## 前端可视化集成

### 1. GraphRAG 查询结果可视化

位于 `server/static/index.html`，在 GraphRAG 查询结果中添加"🕸️ 在图谱中查看"按钮。

#### 1.1 提取实体和关系 ID

```javascript
async function visualizeQueryResults() {
    // 提取实体 ID：Entities (1699) 或 Entities (1699, 1727, 1723)
    const entityMatches = data.response.match(/Entities\s*\(([^)]+)\)/gi);
    
    // 提取关系 ID：Relationships (2634) 或 Relationships (2634, 2635)
    const relationshipMatches = data.response.match(/Relationships\s*\(([^)]+)\)/gi);
}
```

#### 1.2 生成 Cypher 查询

```javascript
if (entityIds.length > 0 && relationshipIds.length > 0) {
    // 同时查询实体、关系节点和相关文本块
    cypherQuery = `
        MATCH (e:__Entity__)
        WHERE e.human_readable_id IN [${entityIds.join(', ')}]
        OPTIONAL MATCH (e)-[edge:RELATED_TO]-(m:__Entity__)
        OPTIONAL MATCH (chunk:__Chunk__)-[:MENTIONS]->(e)
        WITH e, edge, m, collect(DISTINCT chunk) as chunks
        OPTIONAL MATCH (rel:__Relationship__)
        WHERE rel.human_readable_id IN [${relationshipIds.join(', ')}]
        OPTIONAL MATCH (relChunk:__Chunk__)-[:HAS_RELATIONSHIP]->(rel)
        RETURN e, edge, m, rel, chunks, collect(DISTINCT relChunk) as relChunks
        LIMIT 200
    `.trim();
}
```

#### 1.3 自动执行查询

```javascript
// 设置到查询框
document.getElementById('cypherQuery').value = cypherQuery;

// 切换到图谱面板
toggleGraphPanel();

// 自动执行查询
setTimeout(() => {
    executeNeo4jQuery();
}, 500);
```

### 2. 图谱可视化

使用 vis-network 库进行图谱可视化，支持：
- 节点点击查看详情
- 拖拽调整布局
- 缩放和平移
- 不同节点类型的颜色区分

---

## 最佳实践

### 1. 数据导入

- **定期重新导入**：GraphRAG 数据更新后需要重新导入
- **清空数据库**：导入前清空避免重复数据
- **监控性能**：关注批次失败率和死锁情况

### 2. 查询优化

- **使用索引字段**：优先使用 `human_readable_id`、`id`、`name` 等索引字段
- **限制结果数量**：使用 `LIMIT` 避免返回过多数据
- **避免全图扫描**：始终使用 `WHERE` 子句过滤

### 3. Prompt 优化

- **提供具体示例**：在 prompt 中包含常见查询模式
- **明确数据模型**：详细说明节点和关系类型
- **强调关键规则**：使用加粗和编号突出重要规则

---

## 故障排查

### 1. 导入失败

**问题**：实体导入失败，提示 `null property value for 'id'`

**解决**：
- 检查 `human_readable_id` 字段是否存在
- 为 null 值生成唯一 ID

### 2. 查询无结果

**问题**：通过 `human_readable_id` 查询无结果

**解决**：
- 检查数据是否已导入
- 验证 `human_readable_id` 是否正确设置
- 运行诊断查询：`MATCH (e:__Entity__) WHERE e.human_readable_id = 1699 RETURN e`

### 3. 死锁错误

**问题**：并行导入时出现 `DeadlockDetected` 错误

**解决**：
- 降低 `max_workers` 到 1
- 减小 `batch_size`

---

## 总结

本文档介绍了：

1. **数据导入**：如何将 GraphRAG 数据导入 Neo4j，包括实体、关系、文本块的导入
2. **数据模型**：Neo4j 中的节点和关系类型设计
3. **NL2Cypher**：如何使用 LLM 将自然语言转换为 Cypher 查询
4. **Prompt 设计**：详细的 prompt 结构和关键内容
5. **前端集成**：如何在前端实现 GraphRAG 结果的图谱可视化

通过这套方案，实现了 GraphRAG 与 Neo4j 的深度集成，提供了强大的知识图谱查询和可视化能力。
