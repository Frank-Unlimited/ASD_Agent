# GraphRAG 二次开发说明文档

## 📋 概述

本项目基于 [Microsoft GraphRAG](https://github.com/microsoft/graphrag) 进行了深度二次开发，扩展了原生 GraphRAG 的功能，使其更适合生产环境和实际应用场景。

### 核心改进

1. **PDF 文档支持** - 基于 MinerU 的智能 PDF 解析
2. **Neo4j 图谱可视化** - 完整的图谱导入和可视化方案
3. **RESTful API 服务** - 生产级 API 服务和 Nginx 反向代理
4. **其他增强功能** - 多种实用的扩展功能

---

## 🎯 主要功能对比

| 功能 | 原生 GraphRAG | 本项目 |
|------|--------------|--------|
| 文本文件支持 | ✅ | ✅ |
| PDF 文件支持 | ❌ | ✅ 智能解析 |
| CSV 文件支持 | ✅ | ✅ |
| 图谱可视化 | ❌ | ✅ Neo4j |
| NL2Cypher | ❌ | ✅ |
| API 服务 | ❌ | ✅ RESTful |
| Nginx 代理 | ❌ | ✅ |
| Docker 部署 | ⚠️ 基础 | ✅ 完整 |
| 访问控制 | ❌ | ✅ Access Key |

---

## 1️⃣ PDF 文档支持

### 1.1 技术架构

基于 **MinerU** 实现的智能 PDF 解析流程：

```
PDF 文件
    ↓
MinerU 解析服务
    ↓
Markdown 格式
    ↓
表格/图片 LLM 处理
    ↓
结构感知分块
    ↓
GraphRAG 索引构建
```

### 1.2 核心实现

#### MinerU 集成

**文件位置**：`graphrag/index/input/pdf.py`

```python
async def load_pdf(
    config: InputConfig,
    progress: ProgressLogger | None,
    storage: PipelineStorage,
) -> pd.DataFrame:
    """Load PDF inputs from a directory using remote parsing service."""
    
    # 1. 调用 MinerU 远程服务解析 PDF
    result = do_parse(file_path, url=config.mineru_api_url)
    
    # 2. 下载解析结果
    download_success = await download_output_files(
        config.mineru_api_url, 
        config.mineru_output_dir, 
        config.local_output_dir, 
        doc_id
    )
```

#### 表格和图片的 LLM 处理

**表格描述生成**：
```python
# 使用 LLM 为表格生成自然语言描述
table_description = await generate_table_description(
    table_data,
    api_key=config.table_description_api_key,
    model=config.table_description_model
)
```

**图片描述生成**：
```python
# 使用视觉模型为图片生成描述
image_description = await generate_image_description(
    image_path,
    api_key=config.image_description_api_key,
    model=config.image_description_model  # doubao-1-5-vision-pro
)
```

#### 结构感知分块

**Markdown 分块策略**：
```python
chunks:
  strategy: markdown  # 自定义参数
  size: 500
  overlap: 100
  group_by_columns: [id]
```

### 1.3 配置说明

**环境变量配置**（`.env`）：
```bash
# MinerU PDF 解析服务
MINERU_API_URL=http://host.docker.internal:6688/
MINERU_OUTPUT_DIR=/app/data/mineru_output

# PDF 输出目录
PDF_LOCAL_OUTPUT_DIR=/app/data/pdf_outputs

# 图片描述生成（视觉模型）
IMAGE_DESCRIPTION_API_KEY=your-api-key
IMAGE_DESCRIPTION_MODEL=doubao-1-5-vision-pro-32k-250115
IMAGE_DESCRIPTION_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# 表格描述生成
TABLE_DESCRIPTION_API_KEY=your-api-key
TABLE_DESCRIPTION_MODEL=doubao-1-5-lite-32k-250115
TABLE_DESCRIPTION_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
```

**GraphRAG 配置**（`data/settings_pdf.yaml`）：
```yaml
input:
  type: file
  file_type: pdf
  base_dir: "input"
  file_pattern: ".*\\.pdf$"
  local_output_dir: ${PDF_LOCAL_OUTPUT_DIR}
  mineru_api_url: ${MINERU_API_URL}
  mineru_output_dir: ${MINERU_OUTPUT_DIR}
  table_description_api_key: ${TABLE_DESCRIPTION_API_KEY}
  table_description_model: ${TABLE_DESCRIPTION_MODEL}
  image_description_api_key: ${IMAGE_DESCRIPTION_API_KEY}
  image_description_model: ${IMAGE_DESCRIPTION_MODEL}

chunks:
  strategy: markdown  # 结构感知分块
  size: 500
  overlap: 100
```

### 1.4 使用示例

```bash
# 1. 上传 PDF 文件
curl -X POST "http://localhost:8080/api/upload" \
  -F "file=@document.pdf" \
  -F "access_key=duping"

# 2. 构建索引（自动使用 settings_pdf.yaml）
curl -X POST "http://localhost:8080/api/index" \
  -H "Content-Type: application/json" \
  -d '{"access_key": "duping"}'
```

### 1.5 处理流程详解

```
1. PDF 上传
   ↓
2. MinerU 解析
   - 提取文本
   - 识别表格
   - 提取图片
   ↓
3. 内容增强
   - 表格 → LLM 生成描述
   - 图片 → Vision 模型生成描述
   ↓
4. Markdown 输出
   - 保留文档结构
   - 嵌入表格/图片描述
   ↓
5. 结构感知分块
   - 按 Markdown 结构分块
   - 保持语义完整性
   ↓
6. GraphRAG 索引
   - 实体提取
   - 关系构建
   - 社区检测
```

---

## 2️⃣ Neo4j 图谱可视化

### 2.1 功能概述

将 GraphRAG 生成的知识图谱导入 Neo4j，实现：
- 📊 **图谱可视化**：直观查看实体和关系
- 🔍 **NL2Cypher**：自然语言转 Cypher 查询
- 💬 **图谱中查看 GraphRAG 回答**：结合图谱和 RAG 结果

### 2.2 数据导入

**文件位置**：`server/import_to_neo4j.py`

#### 导入流程

```python
class Neo4jImporter:
    """Neo4j 数据导入器 - 使用并行批量导入"""
    
    def import_all(self):
        # 1. 导入文档
        self.import_documents(documents_df)
        
        # 2. 导入实体
        self.import_entities(entities_df)
        
        # 3. 导入关系
        self.import_relationships(relationships_df)
        
        # 4. 导入文本单元
        self.import_text_units(text_units_df)
        
        # 5. 导入社区
        self.import_communities(communities_df)
        
        # 6. 导入社区报告
        self.import_community_reports(reports_df)
```

#### 图谱结构

```
Neo4j 节点类型：
├── __Entity__          # 实体节点
├── __Relationship__    # 关系元数据节点
├── __Community__       # 社区节点
├── __Document__        # 文档节点
└── __Chunk__           # 文本块节点

关系类型：
├── RELATED_TO          # 实体之间的关系
├── BELONGS_TO          # 实体属于社区
├── PART_OF             # 文本块属于文档
├── MENTIONS            # 文本块提及实体
└── HAS_RELATIONSHIP    # 文本块包含关系
```

#### 并行批量导入

```python
def parallel_batched_import(self, statement: str, df: pd.DataFrame, 
                           batch_size: int = 100, max_workers: int = 8):
    """
    使用并行处理进行批量导入
    - 提高导入速度
    - 支持大规模数据
    - 错误处理和重试
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_batch, i) for i in range(batches)]
        # 处理结果...
```

### 2.3 图谱可视化

#### 启动 Neo4j

```bash
# 使用 Docker 启动 Neo4j
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest
```

#### 导入数据

```bash
# 运行导入脚本
python server/import_to_neo4j.py
```

#### 可视化查询

```cypher
# 查看实体和关系
MATCH (e:__Entity__)-[r:RELATED_TO]->(e2:__Entity__)
RETURN e, r, e2 LIMIT 50

# 查看社区结构
MATCH (e:__Entity__)-[:BELONGS_TO]->(c:__Community__)
RETURN e, c LIMIT 25

# 查看特定实体的邻居
MATCH (e:__Entity__ {name: "某个实体"})-[r]-(n)
RETURN e, r, n
```

### 2.4 NL2Cypher 功能

**自然语言转 Cypher 查询**

#### API 端点

```bash
POST /api/nl-to-cypher
```

#### 实现原理

```python
async def nl_to_cypher(question: str, neo4j_url: str, 
                       neo4j_user: str, neo4j_password: str):
    # 1. 获取 Neo4j schema
    schema = get_neo4j_schema(neo4j_url, neo4j_user, neo4j_password)
    
    # 2. 构建 prompt
    prompt = f"""
    根据以下 Neo4j 图谱 schema，将自然语言问题转换为 Cypher 查询：
    
    Schema:
    - 节点标签: {schema['node_labels']}
    - 关系类型: {schema['relationship_types']}
    - 节点属性: {schema['node_properties']}
    
    问题: {question}
    
    请生成 Cypher 查询语句。
    """
    
    # 3. 调用 LLM 生成 Cypher
    cypher = await generate_cypher(prompt)
    
    # 4. 执行查询
    results = execute_cypher(neo4j_url, cypher, neo4j_user, neo4j_password)
    
    return {
        "question": question,
        "cypher": cypher,
        "results": results
    }
```

#### 使用示例

```bash
curl -X POST "http://localhost:8080/api/nl-to-cypher" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "找出所有与人工智能相关的实体",
    "neo4j_url": "http://localhost/neo4j-db/neo4j",
    "neo4j_user": "neo4j",
    "neo4j_password": "your-password",
    "access_key": "hanhaochen"
  }'
```

**响应示例**：
```json
{
  "question": "找出所有与人工智能相关的实体",
  "cypher": "MATCH (e:__Entity__) WHERE e.name CONTAINS '人工智能' OR e.description CONTAINS '人工智能' RETURN e LIMIT 10",
  "results": [
    {"e": {"name": "人工智能", "type": "technology", "description": "..."}},
    {"e": {"name": "机器学习", "type": "technology", "description": "..."}}
  ],
  "explanation": "查询所有名称或描述中包含'人工智能'的实体"
}
```

### 2.5 图谱中查看 GraphRAG 回答

**集成 GraphRAG 查询和 Neo4j 可视化**

#### 工作流程

```
1. 用户提问
   ↓
2. GraphRAG 查询
   - 检索相关实体
   - 生成回答
   ↓
3. 提取相关实体
   ↓
4. Neo4j 可视化
   - 显示实体关系图
   - 高亮相关节点
   ↓
5. 返回结果
   - 文本回答
   - 图谱可视化
```

#### API 实现

```python
@app.post("/api/query-with-graph")
async def query_with_graph(request: QueryWithGraphRequest):
    # 1. GraphRAG 查询
    graphrag_response = await query_graphrag(request.query)
    
    # 2. 提取相关实体
    entities = extract_entities_from_response(graphrag_response)
    
    # 3. 生成 Cypher 查询
    cypher = f"""
    MATCH (e:__Entity__)
    WHERE e.name IN {entities}
    MATCH (e)-[r]-(n)
    RETURN e, r, n
    """
    
    # 4. 执行 Neo4j 查询
    graph_data = execute_cypher(cypher)
    
    return {
        "answer": graphrag_response,
        "entities": entities,
        "graph": graph_data
    }
```

### 2.6 Neo4j 应用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **图谱探索** | 可视化浏览知识图谱 | 查看实体关系网络 |
| **路径查询** | 查找实体间的关系路径 | A 和 B 之间的最短路径 |
| **社区分析** | 分析社区结构和层次 | 查看社区内的实体分布 |
| **实体搜索** | 基于属性搜索实体 | 查找特定类型的实体 |
| **关系分析** | 分析实体间的关系强度 | 查看高权重关系 |
| **NL2Cypher** | 自然语言查询图谱 | "找出所有公司实体" |

---

## 3️⃣ RESTful API 服务

### 3.1 服务架构

```
用户请求
    ↓
Nginx (80端口)
    ├── /api/*          → GraphRAG API (8000端口)
    ├── /neo4j/*        → Neo4j Browser (7474端口)
    ├── /neo4j-db/*     → Neo4j HTTP API (7474端口)
    └── /               → 静态页面
```

### 3.2 核心 API 端点

**文件位置**：`server/graphrag_service.py`

#### 查询 API

```python
@app.post("/api/query/local")
async def query_local(request: QueryRequest):
    """本地搜索 - 基于实体和关系的精确查询"""
    
@app.post("/api/query/global")
async def query_global(request: QueryRequest):
    """全局搜索 - 基于社区报告的宏观查询"""
    
@app.post("/api/query/drift")
async def query_drift(request: QueryRequest):
    """漂移搜索 - 探索性查询"""
```

#### 索引管理 API

```python
@app.post("/api/upload")
async def upload_file(file: UploadFile, access_key: str):
    """上传文件（支持 .txt 和 .pdf）"""
    
@app.post("/api/index")
async def build_index(access_key: str):
    """构建 GraphRAG 索引"""
    
@app.get("/api/index/status/{task_id}")
async def get_index_status(task_id: str):
    """查询索引构建状态"""
```

#### Neo4j 集成 API

```python
@app.post("/api/nl-to-cypher")
async def nl_to_cypher(request: NLToCypherRequest):
    """自然语言转 Cypher 查询"""
    
@app.post("/api/query-with-graph")
async def query_with_graph(request: QueryWithGraphRequest):
    """GraphRAG 查询 + Neo4j 图谱可视化"""
```

### 3.3 Nginx 反向代理

**文件位置**：`nginx_neo4j_http.conf`

#### 配置说明

```nginx
server {
    listen 80;
    server_name localhost;
    
    # GraphRAG API 服务
    location /api/ {
        proxy_pass http://localhost:8000/api/;
    }
    
    # Neo4j Browser
    location /neo4j/ {
        proxy_pass http://localhost:7474/;
    }
    
    # Neo4j HTTP API
    location /neo4j-db/ {
        proxy_pass http://localhost:7474/db/;
    }
    
    # 静态文件
    location / {
        proxy_pass http://localhost:8000/;
    }
}
```

#### 优势

1. **统一入口**：所有服务通过 80 端口访问
2. **简化部署**：无需暴露多个端口
3. **负载均衡**：支持多实例部署
4. **SSL 终止**：统一处理 HTTPS
5. **访问控制**：统一的安全策略

### 3.4 访问控制

#### Access Key 机制

```python
# 查询权限
QUERY_ACCESS_KEY = "hanhaochen"

# 更新权限
UPDATE_ACCESS_KEY = "duping"

def verify_query_access(access_key: str) -> bool:
    """验证查询权限"""
    return access_key == QUERY_ACCESS_KEY

def verify_update_access(access_key: str) -> bool:
    """验证更新权限"""
    return access_key == UPDATE_ACCESS_KEY
```

#### 使用示例

```bash
# 查询（需要 QUERY_ACCESS_KEY）
curl -X POST "http://localhost:8080/api/query/local" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "什么是人工智能？",
    "access_key": "hanhaochen"
  }'

# 上传文件（需要 UPDATE_ACCESS_KEY）
curl -X POST "http://localhost:8080/api/upload" \
  -F "file=@document.pdf" \
  -F "access_key=duping"
```

### 3.5 作为智能体工具

**封装为可调用的工具**

#### OpenAI Function Calling 格式

```json
{
  "name": "graphrag_query",
  "description": "查询知识图谱，获取相关信息",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "要查询的问题"
      },
      "query_type": {
        "type": "string",
        "enum": ["local", "global", "drift"],
        "description": "查询类型：local（精确）、global（宏观）、drift（探索）"
      }
    },
    "required": ["query"]
  }
}
```

#### LangChain Tool 集成

```python
from langchain.tools import Tool

graphrag_tool = Tool(
    name="GraphRAG",
    description="查询知识图谱，获取相关信息。适用于需要从文档中检索信息的场景。",
    func=lambda query: requests.post(
        "http://localhost:8080/api/query/local",
        json={
            "query": query,
            "access_key": "hanhaochen"
        }
    ).json()["response"]
)
```

#### 使用场景

1. **智能客服**：作为知识库查询工具
2. **研究助手**：文献检索和分析
3. **企业知识管理**：内部文档查询
4. **多智能体系统**：作为专业知识工具

---

## 4️⃣ 其他二次开发功能

### 4.1 多文件类型支持

#### 支持的文件类型

| 文件类型 | 配置文件 | 说明 |
|---------|---------|------|
| `.txt` | `settings.yaml` | 纯文本文件 |
| `.pdf` | `settings_pdf.yaml` | PDF 文档（MinerU 解析） |
| `.csv` | `settings_csv.yaml` | CSV 数据文件 |

#### 自动配置选择

```python
def get_config_file(file_type: str) -> str:
    """根据文件类型自动选择配置文件"""
    if file_type == "pdf":
        return "settings_pdf.yaml"
    elif file_type == "csv":
        return "settings_csv.yaml"
    else:
        return "settings.yaml"
```

### 4.2 异步索引构建

#### 后台任务处理

```python
@app.post("/api/index")
async def build_index(background_tasks: BackgroundTasks, access_key: str):
    """异步构建索引"""
    task_id = str(uuid.uuid4())
    
    # 添加后台任务
    background_tasks.add_task(
        run_index_build,
        task_id=task_id,
        config_file=config_file
    )
    
    return {
        "status": "started",
        "task_id": task_id,
        "message": "索引构建已开始"
    }
```

#### 任务状态查询

```python
@app.get("/api/index/status/{task_id}")
async def get_index_status(task_id: str):
    """查询索引构建状态"""
    if task_id not in index_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return index_tasks[task_id]
```

### 4.3 日志系统

#### 结构化日志

```python
def log_to_file(message: str, level: str = "INFO"):
    """记录日志到文件"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "level": level,
        "message": message
    }
    
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
```

#### 日志查询 API

```python
@app.get("/api/logs")
async def get_logs(limit: int = 100):
    """获取最近的日志"""
    logs = []
    with open(log_file, "r") as f:
        for line in f:
            logs.append(json.loads(line))
    
    return logs[-limit:]
```

### 4.4 健康检查

```python
@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "graphrag": "running",
            "neo4j": check_neo4j_connection(),
            "mineru": check_mineru_connection()
        }
    }
```

### 4.5 数据导出

#### CSV 导出

```python
@app.get("/api/export/entities")
async def export_entities(format: str = "csv"):
    """导出实体数据"""
    entities_df = pd.read_parquet("data/output/entities.parquet")
    
    if format == "csv":
        csv_path = "data/exports/entities.csv"
        entities_df.to_csv(csv_path, index=False)
        return FileResponse(csv_path)
```

### 4.6 Prompt 管理

#### 自定义 Prompt

```yaml
# data/prompts/extract_graph_zh.txt
根据以下文本，提取实体和关系：

文本：{text}

请提取：
1. 实体（人物、组织、地点、概念等）
2. 实体之间的关系
3. 关系的描述

输出格式：JSON
```

#### Prompt 调优

```python
@app.post("/api/prompt/tune")
async def tune_prompt(prompt_name: str, new_content: str):
    """更新 prompt 模板"""
    prompt_path = f"data/prompts/{prompt_name}.txt"
    
    with open(prompt_path, "w") as f:
        f.write(new_content)
    
    return {"status": "success", "message": "Prompt 已更新"}
```

### 4.7 缓存管理

#### 查询缓存

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(query: str, query_type: str):
    """缓存查询结果"""
    return execute_query(query, query_type)
```

#### 缓存清理

```python
@app.post("/api/cache/clear")
async def clear_cache(access_key: str):
    """清理缓存"""
    if not verify_update_access(access_key):
        raise HTTPException(status_code=403, detail="无权限")
    
    cached_query.cache_clear()
    return {"status": "success", "message": "缓存已清理"}
```

### 4.8 批量处理

#### 批量上传

```python
@app.post("/api/upload/batch")
async def upload_batch(files: List[UploadFile], access_key: str):
    """批量上传文件"""
    results = []
    
    for file in files:
        result = await process_file(file)
        results.append(result)
    
    return {
        "total": len(files),
        "success": len([r for r in results if r["status"] == "success"]),
        "results": results
    }
```

---

## 📊 性能优化

### 5.1 并行处理

```python
# Neo4j 导入使用并行批处理
max_workers = 8  # 并行线程数
batch_size = 100  # 每批处理数量

with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = [executor.submit(process_batch, batch) for batch in batches]
```

### 5.2 向量数据库优化

```yaml
vector_store:
  default_vector_store:
    type: lancedb
    db_uri: output/lancedb
    overwrite: True  # 开发时使用，生产环境设为 False
```

### 5.3 LLM 并发控制

```yaml
models:
  default_chat_model:
    concurrent_requests: 25  # 并发请求数
    tokens_per_minute: 0     # 0 表示不限制
    requests_per_minute: 0   # 0 表示不限制
    max_retries: -1          # -1 表示动态重试
```

---

## 🔧 开发指南

### 6.1 添加新的文件类型支持

1. 在 `graphrag/index/input/` 创建新的加载器
2. 在 `graphrag/config/enums.py` 添加文件类型枚举
3. 在 `graphrag/index/input/factory.py` 注册加载器
4. 创建对应的 `settings_*.yaml` 配置文件

### 6.2 添加新的 API 端点

```python
@app.post("/api/your-endpoint")
async def your_endpoint(request: YourRequest):
    """你的端点描述"""
    # 1. 验证权限
    if not verify_access(request.access_key):
        raise HTTPException(status_code=403)
    
    # 2. 处理逻辑
    result = process_your_logic(request)
    
    # 3. 返回结果
    return {"status": "success", "data": result}
```

### 6.3 自定义 Prompt

1. 在 `data/prompts/` 创建新的 prompt 文件
2. 在 `settings.yaml` 中引用
3. 使用 Prompt 调优功能优化

---

## 📚 参考资料

### 官方文档
- [Microsoft GraphRAG](https://github.com/microsoft/graphrag)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### 项目文档
- [README.md](README.md) - 项目介绍和快速开始
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - 部署指南
- [RUN_DOCKER.md](RUN_DOCKER.md) - Docker 运行指南

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

### 贡献领域
- 新的文件类型支持
- 性能优化
- 新的 API 功能
- 文档改进
- Bug 修复

---

**更新日期**：2024-12-27  
**版本**：v2.0  
**作者**：GraphRAG Team
