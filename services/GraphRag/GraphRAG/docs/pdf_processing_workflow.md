# GraphRAG PDF 处理完整流程

本文档详细说明 GraphRAG 项目中如何处理 PDF 文件，包括读取、解析、处理和存储的完整流程。

---

## 📋 流程概览

```
1. PDF 文件读取 (data/input/)
   ↓
2. Base64 编码
   ↓
3. 调用 MinerU 服务解析
   ↓
4. 下载解析结果
   ↓
5. 提取结构化信息（表格、图片）
   ↓
6. 生成描述（AI）
   ↓
7. 增强 Markdown 文本
   ↓
8. 导出 CSV 和 JSON
   ↓
9. 存入 GraphRAG 索引
```

---

## 🔧 配置文件

### `data/settings_pdf.yaml`

```yaml
input:
  type: file
  file_type: pdf                                    # 指定处理 PDF 文件
  base_dir: "input"                                 # PDF 输入目录
  file_pattern: ".*\\.pdf$"                         # 匹配所有 .pdf 文件
  
  # MinerU 服务配置
  mineru_api_url: "http://192.168.110.131:8000/"   # MinerU 服务地址
  mineru_output_dir: "/home/07_minerU/tmp/"        # MinerU 服务器输出目录
  local_output_dir: "./data/pdf_outputs"           # 本地存储目录
  
  # 表格描述生成配置
  table_description_api_key: "sk-xxx"              # DeepSeek API Key
  table_description_model: "deepseek-chat"
  base_url: "https://api.deepseek.com"
  
  # 图片描述生成配置
  image_description_api_key: "sk-xxx"              # OpenAI API Key
  image_description_model: "gpt-4o"
  image_description_base_url: "https://ai.devtool.tech/proxy/v1"
```

---

## 📂 核心代码文件

### `graphrag/index/input/pdf.py`

这是 PDF 处理的核心文件，包含所有处理逻辑。

---

## 🔍 详细流程解析

### 1. PDF 文件读取

**位置**: `data/input/` 目录

**代码**: `graphrag/index/input/pdf.py` - `load_pdf()` 函数

```python
async def load_pdf(config, progress, storage):
    # 从 storage 读取 PDF 文件
    buffer = BytesIO(await storage.get(path, as_bytes=True))
```

**说明**:
- 从配置的 `base_dir` (默认 `data/input/`) 读取 PDF 文件
- 使用 `file_pattern` 匹配文件（默认 `.*\\.pdf$`）
- 以二进制方式读取文件内容


---

### 2. Base64 编码

**代码**: `graphrag/index/input/pdf.py` - `to_b64()` 函数

```python
def to_b64(file_path):
    """将文件转换为base64编码"""
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')
```

**流程**:
1. 将 PDF 二进制内容保存到临时文件
2. 读取临时文件并进行 Base64 编码
3. 编码后的字符串可以安全地通过 HTTP 传输

**为什么需要 Base64**:
- 二进制数据不能直接嵌入 JSON
- Base64 将二进制转换为 ASCII 字符串
- 便于通过 HTTP API 传输

---

### 3. 调用 MinerU 服务解析

**代码**: `graphrag/index/input/pdf.py` - `do_parse()` 函数

```python
def do_parse(file_path, url=None, **kwargs):
    """调用MinerU远程Server服务解析PDF文件"""
    # 拼接 /predict 到 url 路径
    if url:
        if not url.endswith('/'):
            url = url + '/'
        url = url + 'predict'
    
    # 发送 POST 请求
    response = requests.post(url, json={
        'file': to_b64(file_path),
        'kwargs': kwargs
    })
    
    if response.status_code == 200:
        output = response.json()
        return output
```

**请求格式**:
```json
POST http://192.168.110.131:8000/predict
{
  "file": "base64编码的PDF内容",
  "kwargs": {
    "debug_able": false,
    "parse_method": "auto"
  }
}
```

**响应格式**:
```json
{
  "output_dir": "/home/07_minerU/tmp/1704355200_uuid/auto"
}
```

**MinerU 服务做什么**:
1. 接收 Base64 编码的 PDF
2. 使用 AI 模型解析文档结构
3. 提取文本、表格、图片
4. 生成 Markdown 文件
5. 返回输出目录路径

---

### 4. 下载解析结果

**代码**: `graphrag/index/input/pdf.py` - `download_output_files()` 函数

```python
async def download_output_files(url, output_dir, local_dir, doc_id):
    """从远程服务器下载解析结果文件"""
    # 构建下载 URL
    url = url + 'download_output_files'
    full_path = f"{output_dir}/{doc_id}"
    
    # 发送 GET 请求
    response = requests.get(url, params={'output_dir': full_path})
    
    # 保存 ZIP 文件
    with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
        temp_file.write(response.content)
        zip_path = temp_file.name
    
    # 解压到本地目录
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_extract_dir)
```

**下载的文件结构**:
```
data/pdf_outputs/1704355200_uuid/
└── auto/
    ├── 1704355200_uuid.md              # Markdown 文本
    ├── 1704355200_uuid_model.json      # 文档结构模型
    ├── 1704355200_uuid_content_list.json  # 内容列表
    └── images/                          # 提取的图片
        ├── image_001.png
        ├── image_002.png
        └── ...
```

**关键文件说明**:
- **`.md`**: 解析后的 Markdown 文本，包含文档内容
- **`_model.json`**: 文档结构模型，包含表格、图片的位置和 HTML
- **`_content_list.json`**: 内容元素列表，包含图片路径和上下文
- **`images/`**: 从 PDF 中提取的所有图片

---

### 5. 提取结构化信息

#### 5.1 提取表格信息

**代码**: `extract_tables_from_model_json()` 函数

```python
async def extract_tables_from_model_json(doc_local_dir, doc_id):
    """从model.json中提取表格信息"""
    # 读取 model.json
    model_json_path = doc_local_dir / f"{doc_id}_model.json"
    with open(model_json_path, 'r') as f:
        model_json = json.load(f)
    
    # 遍历每一页
    for page in model_json:
        layout_dets = page.get('layout_dets', [])
        
        # 查找表格 (category_id = 5)
        for obj in layout_dets:
            if obj.get('category_id') == 5:
                table_data = {
                    "page": page_info.get('page_no'),
                    "table_idx": len(tables),
                    "bbox": [x1, y1, x2, y2],
                    "html": obj.get('html', ""),
                    "caption": ""  # 从 category_id=6 提取
                }
                tables.append(table_data)
```

**提取的表格信息**:
```json
{
  "tables": [
    {
      "page": 1,
      "table_idx": 0,
      "bbox": [100, 200, 500, 400],
      "html": "<table>...</table>",
      "caption": "表1: 销售数据统计",
      "description": ""  // 稍后由 AI 生成
    }
  ]
}
```

#### 5.2 提取图片信息

**代码**: `extract_images_from_content_list()` 函数

```python
def extract_images_from_content_list(doc_local_dir, doc_id):
    """从content_list.json中提取图片信息"""
    content_list_path = doc_local_dir / f"{doc_id}_content_list.json"
    with open(content_list_path, 'r') as f:
        content_list = json.load(f)
    
    # 遍历内容列表
    for idx, item in enumerate(content_list):
        if item.get('type') == 'image':
            image_data = {
                "page": item.get('page_idx'),
                "image_idx": len(images),
                "path": item.get('img_path'),
                "caption": item.get('img_caption'),
                "context_before": "",  # 前一项的文本
                "context_after": ""    # 后一项的文本
            }
            
            # 提取上下文
            if idx > 0 and content_list[idx-1].get('type') == 'text':
                image_data["context_before"] = content_list[idx-1].get('text')
            
            if idx < len(content_list)-1 and content_list[idx+1].get('type') == 'text':
                image_data["context_after"] = content_list[idx+1].get('text')
```

**提取的图片信息**:
```json
{
  "images": [
    {
      "page": 2,
      "image_idx": 0,
      "path": "images/image_001.png",
      "caption": "图1: 系统架构图",
      "context_before": "如下图所示，系统采用微服务架构...",
      "context_after": "从图中可以看出，各个服务之间...",
      "description": ""  // 稍后由 AI 生成
    }
  ]
}
```

---

### 6. 生成 AI 描述

#### 6.1 生成表格描述

**代码**: `generate_descriptions_for_tables()` 函数

```python
def generate_descriptions_for_tables(doc_local_dir, structured_info, config):
    """为表格生成描述"""
    # 使用 OpenAI API
    client = OpenAI(
        api_key=config.table_description_api_key,
        base_url=config.base_url  # DeepSeek API
    )
    
    for table_info in tables_data:
        # 构建提示词
        prompt = "你是一个助理，负责总结表格和文本。给出表格或文本的简明摘要。"
        user_message = f"请总结以下表格内容:\n\n{html_content}"
        
        # 调用 API
        response = client.chat.completions.create(
            model=config.table_description_model,  # deepseek-chat
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        description = response.choices[0].message.content
        table_data["description"] = description
```

**生成的描述示例**:
```
"该表格展示了2023年各季度的销售数据，包括销售额、增长率和市场份额。
第四季度销售额最高，达到500万元，同比增长25%。"
```

#### 6.2 生成图片描述

**代码**: `generate_descriptions_for_images()` 函数

```python
def generate_descriptions_for_images(doc_local_dir, image_info, config):
    """为图片生成描述"""
    from graphrag.index.input.util import generate_image_descriptions_sync
    
    # 调用图片描述生成函数
    descriptions = generate_image_descriptions_sync(
        config=config,
        image_dir=image_dir,
        output_file=output_file,
        max_retries=3,
        retry_delay=2,
        image_info=image_info  # 传递上下文信息
    )
    
    # 将描述添加到图片数据
    for image_data in image_info["images"]:
        img_path = str(doc_local_dir / image_data["path"])
        image_data["description"] = descriptions[img_path]
```

**使用的 API**:
- **模型**: GPT-4o (OpenAI)
- **输入**: 图片 + 上下文文本
- **输出**: 图片描述

**生成的描述示例**:
```
"这是一个系统架构图，展示了微服务架构的各个组件。
图中包含API网关、服务注册中心、多个微服务实例和数据库。
各组件之间通过REST API进行通信。"
```

---

### 7. 增强 Markdown 文本

**代码**: `enhance_markdown_with_metadata()` 函数

```python
def enhance_markdown_with_metadata(text, structured_info, image_info):
    """将元数据以注释形式插入到Markdown文本中"""
    # 在表格前插入元数据注释
    metadata = {
        "type": "table",
        "page": 1,
        "element_idx": 0,
        "description": "该表格展示了..."
    }
    metadata_str = json.dumps(metadata, ensure_ascii=False, indent=4)
    enhanced_text = f"<!-- METADATA\n{metadata_str}\n-->\n{table_html}"
    
    # 在图片前插入元数据注释
    metadata = {
        "type": "image",
        "page": 2,
        "element_idx": 0,
        "path": "images/image_001.png",
        "description": "这是一个系统架构图..."
    }
```

**增强后的 Markdown 示例**:
```markdown
# 文档标题

这是一段普通文本...

<!-- METADATA
{
    "type": "table",
    "page": 1,
    "element_idx": 0,
    "description": "该表格展示了2023年各季度的销售数据..."
}
-->
<table>
  <tr><th>季度</th><th>销售额</th></tr>
  <tr><td>Q1</td><td>300万</td></tr>
</table>

如下图所示...

<!-- METADATA
{
    "type": "image",
    "page": 2,
    "element_idx": 0,
    "path": "images/image_001.png",
    "description": "这是一个系统架构图，展示了微服务架构..."
}
-->
![系统架构图](images/image_001.png)
```

---

### 8. 导出 CSV 和 JSON

**代码**: `load_pdf()` 函数中的导出逻辑

```python
# 导出主数据到 CSV
csv_dir = Path('./data/pdf_csv_exports')
csv_path = csv_dir / f"{doc_id}_pdf_data.csv"
data.to_csv(csv_path, index=False, encoding='utf-8')

# 导出表格数据
tables_csv_path = csv_dir / f"{doc_id}_tables.csv"
tables_df.to_csv(tables_csv_path, index=False)

# 导出图片数据
images_csv_path = csv_dir / f"{doc_id}_images.csv"
images_df.to_csv(images_csv_path, index=False)

# 导出元数据到 JSON
metadata_path = csv_dir / f"{doc_id}_metadata.json"
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)
```

**导出的文件**:
```
data/pdf_csv_exports/
├── 1704355200_uuid_pdf_data.csv      # 主数据
├── 1704355200_uuid_tables.csv        # 表格数据
├── 1704355200_uuid_images.csv        # 图片数据
└── 1704355200_uuid_metadata.json     # 元数据
```

**CSV 文件内容示例**:

`_pdf_data.csv`:
```csv
text,title,id,creation_date
"# 文档标题\n\n这是内容...",document.pdf,1704355200_uuid,2025-01-04
```

`_tables.csv`:
```csv
table_idx,page,caption,description,html
0,1,"表1: 销售数据","该表格展示了...","<table>...</table>"
```

`_images.csv`:
```csv
image_idx,page,path,caption,description,context_before,context_after
0,2,"images/image_001.png","图1: 架构图","这是一个系统架构图...","如下图所示...","从图中可以看出..."
```

---

### 9. 存入 GraphRAG 索引

**最终数据结构**:

```python
data = pd.DataFrame([{
    "text": enhanced_markdown_text,  # 增强后的 Markdown
    "title": "document.pdf",
    "id": "1704355200_uuid",
    "metadata": {
        "file_path": "data/input/document.pdf",
        "output_dir": "/home/07_minerU/tmp/1704355200_uuid/auto",
        "local_output_dir": "./data/pdf_outputs/1704355200_uuid",
        "parse_time": "2025-01-04T10:30:00",
        "doc_id": "1704355200_uuid",
        "content_elements": [
            {
                "type": "table",
                "page": 1,
                "element_idx": 0,
                "html": "<table>...</table>",
                "description": "该表格展示了..."
            },
            {
                "type": "image",
                "page": 2,
                "element_idx": 0,
                "path": "images/image_001.png",
                "description": "这是一个系统架构图..."
            }
        ],
        "content_types": {
            "table": 2,
            "image": 3
        }
    },
    "creation_date": "2025-01-04"
}])
```

这个 DataFrame 会被传递给 GraphRAG 的索引构建流程，进行：
1. 文本分块 (chunking)
2. 实体提取 (entity extraction)
3. 关系提取 (relationship extraction)
4. 社区检测 (community detection)
5. 向量化 (embedding)

---

## 📊 完整数据流图

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PDF 文件 (data/input/document.pdf)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Base64 编码                                              │
│    "JVBERi0xLjQKJeLjz9MKMSAwIG9iago8PC9UeXBlL0NhdGFsb2c..." │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. POST http://192.168.110.131:8000/predict                │
│    {                                                         │
│      "file": "base64_content",                              │
│      "kwargs": {"parse_method": "auto"}                     │
│    }                                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. MinerU 服务解析                                          │
│    - AI 模型分析文档结构                                    │
│    - 提取文本、表格、图片                                   │
│    - 生成 Markdown                                          │
│    返回: {"output_dir": "/tmp/1704355200_uuid/auto"}       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. GET http://192.168.110.131:8000/download_output_files   │
│    params: {"output_dir": "/tmp/1704355200_uuid"}          │
│    返回: ZIP 文件                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. 解压到本地 (data/pdf_outputs/1704355200_uuid/)          │
│    ├── auto/                                                │
│    │   ├── 1704355200_uuid.md                              │
│    │   ├── 1704355200_uuid_model.json                      │
│    │   ├── 1704355200_uuid_content_list.json               │
│    │   └── images/                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. 提取结构化信息                                           │
│    - 从 model.json 提取表格 (HTML + 位置)                  │
│    - 从 content_list.json 提取图片 (路径 + 上下文)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. 生成 AI 描述                                             │
│    - DeepSeek API: 表格描述                                 │
│    - GPT-4o API: 图片描述                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. 增强 Markdown                                            │
│    - 在表格/图片前插入元数据注释                            │
│    - 包含描述、页码、位置等信息                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. 导出 CSV/JSON (data/pdf_csv_exports/)                  │
│     ├── 1704355200_uuid_pdf_data.csv                       │
│     ├── 1704355200_uuid_tables.csv                         │
│     ├── 1704355200_uuid_images.csv                         │
│     └── 1704355200_uuid_metadata.json                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. GraphRAG 索引构建                                       │
│     - 文本分块                                              │
│     - 实体提取                                              │
│     - 关系提取                                              │
│     - 社区检测                                              │
│     - 向量化                                                │
│     输出: data/output/*.parquet                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 关键要点总结

### MinerU 服务的输出文件

1. **`.md` 文件**: 解析后的 Markdown 文本
2. **`_model.json`**: 文档结构模型（表格 HTML、位置信息）
3. **`_content_list.json`**: 内容元素列表（图片路径、上下文）
4. **`images/` 目录**: 提取的所有图片

### GraphRAG 如何使用这些文件

1. **读取 `.md`**: 作为主要文本内容
2. **解析 `_model.json`**: 提取表格的 HTML 和位置
3. **解析 `_content_list.json`**: 提取图片路径和上下文
4. **调用 AI API**: 为表格和图片生成描述
5. **增强 Markdown**: 将元数据注释插入文本
6. **导出 CSV**: 便于查看和调试
7. **构建索引**: 将增强后的文本传入 GraphRAG

### 配置要点

1. **MinerU 服务地址**: `mineru_api_url`
2. **服务器输出目录**: `mineru_output_dir`
3. **本地存储目录**: `local_output_dir`
4. **表格描述 API**: DeepSeek
5. **图片描述 API**: GPT-4o

---

## 📞 相关文档

- [API 服务使用指南](./api_service_guide.md)
- [Data 目录结构说明](./data_structure_guide.md)
- [MinerU 服务部署](../course/server.py)

---

**最后更新**: 2025-01-04
