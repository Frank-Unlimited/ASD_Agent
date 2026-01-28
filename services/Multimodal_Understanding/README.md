# 多模态解析模块

基于通义千问3-VL-Plus的多模态内容解析服务，已集成到ASD干预系统。

## 🎯 功能

- ✅ 文本解析
- ✅ 图片解析（URL或base64）
- ✅ 视频解析（URL或base64）
- ✅ 本地文件支持
- ✅ 系统集成（适配 IVideoAnalysisService 接口）

## 📦 快速开始

### 1. 独立使用

```python
from api_interface import parse_text, parse_image, parse_video

# 文本
result = parse_text("什么是人工智能？")

# 图片
result = parse_image("https://example.com/image.jpg", "描述图片")

# 视频
result = parse_video("https://example.com/video.mp4", "总结视频")
```

### 2. 系统集成使用

```python
from src.container import container

# 获取服务
video_service = container.get('video_analysis')

# 分析视频
result = await video_service.analyze_video(
    video_path="path/to/video.mp4",
    context={'child_profile': {...}}
)
```

## 📚 文档

- [USAGE.md](./USAGE.md) - 详细使用文档
- [INTEGRATION.md](./INTEGRATION.md) - 系统集成说明

## 🧪 测试

```bash
# 测试核心功能
python test_simple.py

# 测试系统适配器
python test_adapter.py
```

## ⚙️ 配置

在 `.env` 文件中设置：

```bash
# 启用真实服务
USE_REAL_VIDEO_ANALYSIS=true

# API密钥
DASHSCOPE_API_KEY=your_api_key_here
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `api_interface.py` | 核心接口（parse_text/image/video） |
| `service_adapter.py` | 系统适配器（IVideoAnalysisService） |
| `config.py` | 配置管理 |
| `models.py` | 数据模型 |
| `multimodal_parser.py` | 解析器实现 |
| `utils.py` | 工具函数（base64编码等） |
| `test_simple.py` | 功能测试 |
| `test_adapter.py` | 适配器测试 |

## 🔄 两种使用方式

### 方式1: 直接调用（独立使用）

```python
from api_interface import parse_video
result = parse_video(video_url, prompt)
```

### 方式2: 通过容器（系统集成）

```python
from src.container import container
service = container.get('video_analysis')
result = await service.analyze_video(video_path, context)
```

## ✨ 特性

- 支持URL和本地文件
- 自动base64编码
- 流式输出支持
- Mock/Real模式切换
- 完整的类型提示

## 📝 License

MIT
