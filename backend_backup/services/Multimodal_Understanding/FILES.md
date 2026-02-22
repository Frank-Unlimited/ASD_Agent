# 文件说明

## 📁 核心文件

### 功能实现层

| 文件 | 说明 | 用途 |
|------|------|------|
| `api_interface.py` | 核心接口 | 提供 `parse_text()`, `parse_image()`, `parse_video()` 三个函数 |
| `multimodal_parser.py` | 解析器实现 | 核心解析逻辑，调用通义千问API |
| `models.py` | 数据模型 | 定义请求和响应的数据结构 |
| `config.py` | 配置管理 | 管理API密钥和模型配置 |
| `utils.py` | 工具函数 | base64编码、文件处理等工具 |

### 系统集成层

| 文件 | 说明 | 用途 |
|------|------|------|
| **`adapters.py`** | **系统适配器** ⭐ | 适配两个系统接口 |
| ├─ `MultimodalDocumentParserService` | 文档解析适配器 | 实现 `IDocumentParserService` |
| └─ `MultimodalVideoAnalysisService` | 视频分析适配器 | 实现 `IVideoAnalysisService` |

### 测试文件

| 文件 | 说明 | 用途 |
|------|------|------|
| `test_simple.py` | 功能测试 | 测试核心功能（parse_text/image/video） |
| `test_adapters.py` | 适配器测试 | 测试系统集成（两个适配器） |

### 文档文件

| 文件 | 说明 | 内容 |
|------|------|------|
| `README.md` | 模块概览 | 快速开始和功能介绍 |
| `USAGE.md` | 使用文档 | 详细的使用方法和示例 |
| `INTEGRATION.md` | 集成文档 | 系统集成的详细说明 |
| `INTEGRATION_SUMMARY.md` | 集成总结 | 快速查看集成情况 |
| `FILES.md` | 文件说明 | 本文件，说明各文件用途 |

## 🎯 使用场景

### 场景1: 独立使用（不依赖系统）

```python
# 直接导入核心接口
from api_interface import parse_text, parse_image, parse_video

result = parse_image("image.jpg", "描述图片")
```

**使用文件**：
- `api_interface.py`
- `multimodal_parser.py`
- `models.py`
- `config.py`
- `utils.py`

### 场景2: 系统集成使用

```python
# 通过容器获取服务
from src.container import container

doc_service = container.get('document_parser')
video_service = container.get('video_analysis')

result = await doc_service.parse_report(...)
result = await video_service.analyze_video(...)
```

**使用文件**：
- `adapters.py` ⭐（适配器）
- 所有功能实现层文件

## 📊 文件依赖关系

```
adapters.py (系统适配器)
    ↓ 导入
api_interface.py (核心接口)
    ↓ 导入
multimodal_parser.py (解析器)
    ↓ 导入
models.py (数据模型)
config.py (配置)
utils.py (工具)
```

## 🔧 开发流程

1. **修改核心功能** → 编辑 `api_interface.py`, `multimodal_parser.py` 等
2. **测试核心功能** → 运行 `test_simple.py`
3. **测试系统集成** → 运行 `test_adapters.py`
4. **更新文档** → 修改相应的 `.md` 文件

## 🗑️ 已删除的文件

- ~~`document_adapter.py`~~ - 空文件，已删除
- ~~`service_adapter.py`~~ - 已合并到 `adapters.py`

## 📝 注意事项

1. **不要修改** `adapters.py` 中的接口签名（必须符合系统接口定义）
2. **可以修改** `api_interface.py` 中的实现细节
3. **测试时** 先测试 `test_simple.py`，再测试 `test_adapters.py`
4. **文档更新** 修改功能后记得更新相关文档

## 🎯 核心文件

如果只关注核心功能，重点看这几个文件：

1. **`api_interface.py`** - 对外接口
2. **`adapters.py`** - 系统集成
3. **`test_simple.py`** - 功能测试
4. **`INTEGRATION_SUMMARY.md`** - 集成总结

---

**文件结构清晰，职责明确！** ✨
