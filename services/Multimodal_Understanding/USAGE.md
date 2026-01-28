# 多模态解析模块使用指南

## 安装依赖

```bash
pip install openai python-dotenv
```

## 环境配置

```bash
export DASHSCOPE_API_KEY="your_api_key_here"
```

## 使用方式

### 方式1: 使用便捷接口（推荐）

```python
# 导入接口
from Multimodal_Understanding import parse_image, parse_text, parse_video

# 1. 解析图片
answer = parse_image(
    image_url="https://example.com/image.jpg",
    prompt="这道题怎么解答？"
)
print(answer)

# 2. 解析文本
answer = parse_text("什么是人工智能？")
print(answer)

# 3. 解析视频
answer = parse_video(
    video_url="https://example.com/video.mp4",
    prompt="总结视频内容"
)
print(answer)
```

### 方式2: 使用核心类

```python
from Multimodal_Understanding import MultimodalParser, ParseRequest

# 初始化解析器
parser = MultimodalParser()

# 创建请求
request = ParseRequest.from_image(
    image_url="https://example.com/image.jpg",
    prompt="描述这张图片"
)

# 获取结果
response = parser.parse(request)
print(response.answer)
```

### 方式3: 带推理过程

```python
from Multimodal_Understanding import parse_with_reasoning

result = parse_with_reasoning(
    image_url="https://example.com/math.jpg",
    prompt="这道题怎么解答？"
)

print("推理过程:", result["reasoning"])
print("答案:", result["answer"])
```

### 方式4: 流式输出

```python
from Multimodal_Understanding import parse_stream

for chunk in parse_stream(
    image_url="https://example.com/image.jpg",
    prompt="描述这张图片"
):
    print(chunk, end='', flush=True)
```

### 方式5: 混合内容

```python
from Multimodal_Understanding import parse_mixed

answer = parse_mixed(
    text="这是补充说明",
    image_urls=["https://example.com/img1.jpg", "https://example.com/img2.jpg"],
    prompt="综合分析这些内容"
)
print(answer)
```

### 方式6: 批量处理

```python
from Multimodal_Understanding import parse_image_batch

image_urls = [
    "https://example.com/img1.jpg",
    "https://example.com/img2.jpg",
    "https://example.com/img3.jpg"
]

prompts = ["描述图片1", "描述图片2", "描述图片3"]

results = parse_image_batch(image_urls, prompts)
for i, result in enumerate(results):
    print(f"图片{i+1}: {result}")
```

## 完整示例

```python
import os
os.environ["DASHSCOPE_API_KEY"] = "your_api_key"

from Multimodal_Understanding import (
    parse_image,
    parse_text,
    parse_with_reasoning,
    parse_stream
)

# 示例1: 简单图片解析
print("=" * 60)
print("示例1: 图片解析")
print("=" * 60)
answer = parse_image(
    "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
    "这道题怎么解答？"
)
print(answer)

# 示例2: 带推理过程
print("\n" + "=" * 60)
print("示例2: 带推理过程")
print("=" * 60)
result = parse_with_reasoning(
    "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
    "这道题怎么解答？"
)
print("推理:", result["reasoning"])
print("答案:", result["answer"])

# 示例3: 流式输出
print("\n" + "=" * 60)
print("示例3: 流式输出")
print("=" * 60)
print("答案: ", end='', flush=True)
for chunk in parse_stream(
    "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
    "这道题怎么解答？"
):
    print(chunk, end='', flush=True)
print()
```

## API参考

### 便捷函数

- `parse_text(text, prompt=None)` - 解析文本
- `parse_image(image_url, prompt=None)` - 解析图片
- `parse_video(video_url, prompt=None)` - 解析视频
- `parse_mixed(text, image_urls, video_urls, prompt)` - 解析混合内容
- `parse_with_reasoning(image_url, prompt)` - 带推理过程解析
- `parse_stream(image_url, prompt)` - 流式解析
- `parse_image_batch(image_urls, prompts)` - 批量解析

### 核心类

- `MultimodalParser` - 解析器类
- `ParseRequest` - 请求类
- `ParseResponse` - 响应类
- `MultimodalConfig` - 配置类

## 注意事项

1. 必须设置 `DASHSCOPE_API_KEY` 环境变量
2. 图片/视频URL需要可公开访问
3. 支持base64编码的图片/视频
4. 推理过程会消耗更多Token
