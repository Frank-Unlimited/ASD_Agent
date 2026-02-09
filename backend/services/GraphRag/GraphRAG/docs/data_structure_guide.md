# Data 目录结构详解

本文档详细说明 `data/` 目录下各个文件和文件夹的作用。

---

## 📁 目录结构总览

```
data/
├── .env                      # 环境变量配置（敏感信息）
├── settings.yaml             # 主配置文件
├── settings_csv.yaml         # CSV 数据源配置
├── settings_pdf.yaml         # PDF 数据源配置
├── input/                    # 输入数据目录
├── output/                   # 索引输出目录 ⭐
├── cache/                    # LLM 调用缓存
├── logs/                     # 日志文件
├── prompts/                  # Prompt 模板
├── prompt_turn_output/       # Prompt 调优输出
├── pdf_outputs/              # PDF 处理输出
├── pdf_csv_exports/          # PDF 导出 CSV
└── update_output/            # 增量更新输出
```

---

## 🔧 核心配置文件

### 1. `.env` - 环境变量配置

**作用**: 存储 API 密钥、模型名称等敏感配置信息

**内容示例**:
```env
# LLM API 配置
GRAPHRAG_API_BASE=https://api.deepseek.com
GRAPHRAG_API_KEY=sk-xxxxxxxxxxxxx
GRAPHRAG_MODEL_NAME=deepseek-chat

# Embedding API 配置
Embedding_API_BASE=https://ai.devtool.tech/proxy/v1
Embedding_API_KEY=sk-proj-xxxxxxxxxxxxx
Embedding_MODEL_NAME=text-embedding-3-small
```

**重要提示**:
- ⚠️ 不要提交到 Git 仓库
- 使用 `.gitignore` 排除此文件
- 生产环境使用不同的密钥

---

### 2. `settings.yaml` - 主配置文件

**作用**: GraphRAG 的核心配置文件，定义模型、输入输出、处理流程等

**主要配置项**:

#### 模型配置
```yaml
models:
  default_chat_model:
    type: openai_chat
    api_base: ${GRAPHRAG_API_BASE}
    api_key: ${GRAPHRAG_API_KEY}
    model: ${GRAPHRAG_MODEL_NAME}
    concurrent_requests: 25
    
  default_embedding_model:
    type: openai_embedding
    api_base: ${Embedding_API_BASE}
    api_key: ${Embedding_API_KEY}
    model: ${Embedding_MODEL_NAME}
```

#### 输入配置
```yaml
input:
  type: file                    # 数据源类型: file, blob
  file_type: text               # 文件类型: text, csv
  base_dir: "input"             # 输入目录
  file_encoding: utf-8          # 文件编码
  file_pattern: ".*\\.txt$"     # 文件匹配模式
```

#### 输出配置
```yaml
output:
  type: file                    # 输出类型: file, blob, cosmosdb
  base_dir: "output"            # 输出目录
```

#### 文本分块配置
```yaml
chunks:
  size: 500                     # 每块大小（字符数）
  overlap: 100                  # 重叠大小（字符数）
  group_by_columns: [id]        # 分组列
```

#### 图谱提取配置
```yaml
extract_graph:
  model_id: default_chat_model
  prompt: "prompt_turn_output/extract_graph_zh.txt"
  entity_types: [company, person, technology, ...]
  max_gleanings: 1              # 最大提取轮数
```

---

### 3. `settings_csv.yaml` / `settings_pdf.yaml`

**作用**: 针对特定数据源类型的配置文件

**使用场景**:
- 处理 CSV 数据时使用 `settings_csv.yaml`
- 处理 PDF 数据时使用 `settings_pdf.yaml`
- 可以为不同数据源定制不同的处理参数

---

## 📂 数据目录详解

### 1. `input/` - 输入数据目录

**作用**: 存放需要被 GraphRAG 索引的原始数据文件

**支持的文件类型**:
- `.txt` - 纯文本文件
- `.pdf` - PDF 文档
- `.csv` - CSV 数据表
- `.docx` - Word 文档（需要额外配置）

**示例结构**:
```
input/
├── technology_companies.txt    # 科技公司介绍
├── all_text.pdf               # PDF 文档
└── merged_review.csv          # CSV 数据
```

**使用建议**:
- 文件名使用英文，避免特殊字符
- 文本文件使用 UTF-8 编码
- 大文件建议分割成多个小文件

---

### 2. `output/` - 索引输出目录 ⭐

**作用**: 存储索引构建后的所有结构化数据，这是查询时的核心数据源

**核心文件说明**:

#### `entities.parquet`
- **内容**: 从文本中提取的所有实体
- **字段**: id, name, type, description, text_unit_ids, ...
- **示例**: 
  - 实体名: "OpenAI"
  - 类型: "company"
  - 描述: "人工智能研究公司"

#### `relationships.parquet`
- **内容**: 实体之间的关系
- **字段**: source, target, description, weight, text_unit_ids, ...
- **示例**:
  - 源实体: "OpenAI"
  - 目标实体: "GPT-4"
  - 关系: "开发了"

#### `communities.parquet`
- **内容**: 通过图算法聚类的社区信息
- **字段**: id, level, title, entities, relationships, ...
- **说明**: 使用 Leiden 算法对实体进行层次化聚类

#### `community_reports.parquet`
- **内容**: 每个社区的 AI 生成摘要
- **字段**: community, level, title, summary, findings, ...
- **说明**: 这是全局搜索的核心数据

#### `text_units.parquet`
- **内容**: 原始文本的分块
- **字段**: id, text, n_tokens, document_ids, entity_ids, ...
- **说明**: 用于检索和上下文提供

#### `documents.parquet`
- **内容**: 文档元数据
- **字段**: id, title, raw_content, text_unit_ids, ...

#### `lancedb/`
- **内容**: 向量数据库
- **说明**: 存储文本和实体的向量表示，用于语义检索

#### `stats.json`
- **内容**: 索引统计信息
- **示例**:
```json
{
  "total_entities": 1234,
  "total_relationships": 5678,
  "total_communities": 89,
  "total_text_units": 2345
}
```

#### `context.json`
- **内容**: 索引上下文信息
- **说明**: 记录索引构建的配置和参数

---

### 3. `cache/` - 缓存目录

**作用**: 缓存 LLM 调用结果，避免重复计算，节省 API 费用和时间

**子目录说明**:

#### `cache/extract_graph/`
- 缓存图谱提取的 LLM 响应
- 文件格式: JSON
- 按文本块的哈希值存储

#### `cache/summarize_descriptions/`
- 缓存实体描述摘要的 LLM 响应
- 避免重复摘要相同的实体

#### `cache/community_reporting/`
- 缓存社区报告生成的 LLM 响应
- 这是最耗费 token 的部分

#### `cache/text_embedding/`
- 缓存文本向量化结果
- 避免重复调用 Embedding API

**缓存策略**:
- 基于内容哈希的缓存键
- 增量索引时会复用缓存
- 可以手动清理缓存强制重新生成

---

### 4. `logs/` - 日志目录

**作用**: 记录所有操作日志，便于调试和监控

**日志文件**:

#### `graphrag_api.log`
- API 服务运行日志
- 记录请求、响应、错误等

#### `graphrag_query.log`
- 查询操作日志
- 记录查询参数、结果、耗时等

#### `dev_graphrag_indexing.log`
- 索引构建日志
- 记录索引进度、错误、统计等

#### `indexing-engine.log`
- 索引引擎底层日志
- 更详细的技术日志

**日志格式**:
```
2025-01-04 10:30:45 - graphrag-api - INFO - 开始执行查询: 什么是人工智能？
2025-01-04 10:30:46 - graphrag-api - INFO - 查询类型: local
2025-01-04 10:30:48 - graphrag-api - INFO - 查询成功完成
```

---

### 5. `prompts/` - Prompt 模板目录

**作用**: 存储各种 LLM 任务的 Prompt 模板

**主要 Prompt 文件**:

#### 图谱提取
- `extract_graph.txt` - 英文版
- `extract_graph_zh.txt` - 中文版
- 用于从文本中提取实体和关系

#### 描述摘要
- `summarize_descriptions.txt` - 英文版
- `summarize_descriptions_zh.txt` - 中文版
- 用于摘要实体描述

#### 社区报告
- `community_report_graph.txt` - 基于图结构
- `community_report_text.txt` - 基于文本
- `community_report_graph_zh.txt` - 中文版
- 用于生成社区摘要报告

#### 查询 Prompt
- `local_search_system_prompt.txt` - 本地搜索
- `global_search_map_system_prompt.txt` - 全局搜索（Map）
- `global_search_reduce_system_prompt.txt` - 全局搜索（Reduce）
- `drift_search_system_prompt.txt` - 漂移搜索
- `basic_search_system_prompt.txt` - 基础搜索

**自定义 Prompt**:
- 可以直接编辑这些文件来优化 Prompt
- 建议先备份原始文件
- 修改后需要重新构建索引

---

### 6. `prompt_turn_output/` - Prompt 调优输出

**作用**: 存储通过 `graphrag prompt-tune` 命令自动优化后的 Prompt

**生成方式**:
```bash
cd dev
python graphrag_prompt_tune.py
```

**文件说明**:
- `extract_graph_zh.txt` - 调优后的提取 Prompt
- `summarize_descriptions_zh.txt` - 调优后的摘要 Prompt
- `community_report_graph_zh.txt` - 调优后的报告 Prompt
- `metadata.json` - 调优元数据和统计

**使用方式**:
- 调优后的 Prompt 会自动在 `settings.yaml` 中引用
- 可以对比原始 Prompt 和调优后的差异

---

### 7. `pdf_outputs/` - PDF 处理输出

**作用**: 存储 PDF 文档处理的中间结果和输出

**目录结构**:
```
pdf_outputs/
└── [timestamp]_[uuid]/
    ├── cache/              # PDF 处理缓存
    ├── output/             # PDF 索引输出
    └── logs/               # PDF 处理日志
```

**使用场景**:
- 单独处理 PDF 文档
- 保留 PDF 处理的完整历史
- 便于调试 PDF 提取问题

---

### 8. `pdf_csv_exports/` - PDF 导出 CSV

**作用**: 将 PDF 处理结果导出为 CSV 格式

**文件格式**:
```
pdf_csv_exports/
├── [timestamp]_[uuid]_pdf_data.csv      # 提取的数据
└── [timestamp]_[uuid]_metadata.json     # 元数据
```

**CSV 内容**:
- 页码
- 提取的文本
- 实体信息
- 关系信息

---

### 9. `update_output/` - 增量更新输出

**作用**: 存储增量索引更新的结果，避免全量重建

**目录结构**:
```
update_output/
└── [timestamp]/
    ├── entities.parquet
    ├── relationships.parquet
    ├── communities.parquet
    └── ...
```

**使用场景**:
- 添加新文档时使用增量更新
- 比全量重建更快、更省钱
- 保留更新历史便于回滚

**增量更新命令**:
```bash
python -m graphrag update --root data
```

---

## 📊 数据大小参考

典型的索引数据大小（1000 个文档）:

| 文件 | 大小 | 说明 |
|------|------|------|
| entities.parquet | 5-10 MB | 取决于实体数量 |
| relationships.parquet | 10-20 MB | 取决于关系数量 |
| communities.parquet | 1-2 MB | 相对较小 |
| community_reports.parquet | 5-10 MB | 取决于报告详细程度 |
| text_units.parquet | 20-50 MB | 取决于文本总量 |
| lancedb/ | 50-100 MB | 向量数据库 |
| cache/ | 100-500 MB | LLM 调用缓存 |

---

## 🔄 数据流程

```
1. 原始数据 (input/)
   ↓
2. 文本分块
   ↓
3. 实体提取 → entities.parquet
   ↓
4. 关系提取 → relationships.parquet
   ↓
5. 社区检测 → communities.parquet
   ↓
6. 社区报告 → community_reports.parquet
   ↓
7. 向量化 → lancedb/
   ↓
8. 查询使用 (output/)
```

---

## 🧹 数据清理

### 清理缓存
```bash
rm -rf data/cache/*
```

### 清理日志
```bash
rm -rf data/logs/*.log
```

### 清理输出（重新索引前）
```bash
rm -rf data/output/*
```

### 清理增量更新历史
```bash
rm -rf data/update_output/*
```

---

## 💡 最佳实践

1. **定期备份 output/ 目录**
   - 索引构建耗时且费用高
   - 备份可以快速恢复

2. **保留 cache/ 目录**
   - 增量更新时会复用缓存
   - 节省 API 费用

3. **监控日志文件大小**
   - 设置日志轮转
   - 定期清理旧日志

4. **版本控制**
   - 不要提交 .env 文件
   - 不要提交 output/ 和 cache/
   - 可以提交 prompts/ 和配置文件

5. **数据安全**
   - 敏感数据不要放在 input/
   - 定期清理不需要的数据
   - 使用加密存储敏感信息

---

## 📞 相关文档

- [API 服务使用指南](./api_service_guide.md)
- [配置文件详解](./config/yaml.md)
- [索引构建指南](./index/overview.md)
- [查询方法指南](./query/overview.md)

---

**最后更新**: 2025-01-04
