# 多模态解析模块集成说明

## ✅ 已完成的集成

你的多模态解析模块已经成功集成到系统中，适配了**两个接口**！

### 集成内容

1. **文档解析适配器** - `adapters.py::MultimodalDocumentParserService`
   - 实现了 `IDocumentParserService` 接口
   - 使用**图片解析**和**文本解析**能力
   - 用于解析医院报告和量表

2. **视频分析适配器** - `adapters.py::MultimodalVideoAnalysisService`
   - 实现了 `IVideoAnalysisService` 接口
   - 使用**视频解析**能力
   - 用于分析儿童行为视频

3. **容器注册** - `src/container.py`
   - `document_parser` - 文档解析服务
   - `video_analysis` - 视频分析服务

4. **配置添加** - `src/config.py` 和 `.env.example`
   - `DASHSCOPE_API_KEY` - 通义千问API密钥
   - `USE_REAL_DOCUMENT_PARSER` - 启用文档解析
   - `USE_REAL_VIDEO_ANALYSIS` - 启用视频分析

## 🎯 功能映射

### 你的模块功能 → 系统接口

```
parse_text()  ──┐
                ├──> IDocumentParserService (文档解析)
parse_image() ──┘    - parse_report()  解析医院报告
                     - parse_scale()   解析量表

parse_video() ────> IVideoAnalysisService (视频分析)
                     - analyze_video()      分析视频
                     - extract_highlights() 提取关键片段
```

## 🚀 如何使用

### 1. 配置环境变量

在 `.env` 文件中设置：

```bash
# 启用真实服务
USE_REAL_DOCUMENT_PARSER=true
USE_REAL_VIDEO_ANALYSIS=true

# 通义千问API密钥
DASHSCOPE_API_KEY=your_api_key_here
```

### 2. 使用文档解析服务

```python
from src.container import container

# 获取文档解析服务
doc_service = container.get('document_parser')

# 解析医院报告（图片）
result = await doc_service.parse_report(
    file_path="path/to/report.jpg",  # 或 URL
    file_type="image"
)

print(result['diagnosis'])      # 诊断结果
print(result['severity'])       # 严重程度
print(result['recommendations']) # 建议

# 解析量表（图片）
result = await doc_service.parse_scale(
    scale_data={'image_path': 'path/to/scale.jpg'},
    scale_type='CARS'
)

print(result['total_score'])      # 总分
print(result['severity_level'])   # 严重程度
print(result['interpretation'])   # 解释

# 解析量表（文本）
result = await doc_service.parse_scale(
    scale_data={'text': '题目1: 3分\n题目2: 4分'},
    scale_type='ABC'
)
```

### 3. 使用视频分析服务

```python
from src.container import container

# 获取视频分析服务
video_service = container.get('video_analysis')

# 分析视频
result = await video_service.analyze_video(
    video_path="path/to/video.mp4",  # 或 URL
    context={
        'child_profile': {
            'name': '辰辰',
            'age': 2.5,
            'interests': ['旋转物体']
        },
        'observation_framework': {
            'dimensions': ['眼神接触', '互动质量']
        },
        'game_info': {
            'name': '泡泡游戏',
            'goal': '提升互动'
        }
    }
)

print(result['summary'])       # 总结
print(result['behaviors'])     # 行为列表
print(result['interactions'])  # 互动列表
print(result['emotions'])      # 情绪信息
print(result['attention'])     # 注意力信息

# 提取关键片段
highlights = await video_service.extract_highlights(
    video_path="path/to/video.mp4",
    analysis_result=result
)

for highlight in highlights:
    print(f"{highlight['timestamp']}: {highlight['description']}")
```

## 🧪 测试

### 测试适配器

```bash
cd services/Multimodal-Understanding
python test_adapters.py
```

### 测试原始功能

```bash
cd services/Multimodal-Understanding
python test_simple.py
```

## � 接口详细说明

### IDocumentParserService 接口

#### 1. parse_report()

```python
async def parse_report(
    file_path: str,      # 文件路径或URL
    file_type: str       # 文件类型（image/pdf/doc）
) -> Dict[str, Any]:
    """
    解析医院报告
    
    返回:
    {
        'raw_text': str,           # 原始文本
        'diagnosis': str,          # 诊断结果
        'severity': str,           # 严重程度
        'test_results': List,      # 测试结果
        'recommendations': List,   # 建议
        'file_path': str          # 文件路径
    }
    """
```

#### 2. parse_scale()

```python
async def parse_scale(
    scale_data: Dict[str, Any],  # 量表数据
    scale_type: str              # 量表类型（CARS/ABC/ADOS）
) -> Dict[str, Any]:
    """
    解析量表数据
    
    scale_data 可以是:
    - {'image_path': 'path/to/scale.jpg'}  # 图片量表
    - {'text': '题目1: 3分\n题目2: 4分'}    # 文本量表
    
    返回:
    {
        'scale_type': str,         # 量表类型
        'total_score': float,      # 总分
        'dimension_scores': Dict,  # 各维度得分
        'severity_level': str,     # 严重程度
        'interpretation': str,     # 解释
        'recommendations': List,   # 建议
        'raw_analysis': str       # 原始分析
    }
    """
```

### IVideoAnalysisService 接口

#### 1. analyze_video()

```python
async def analyze_video(
    video_path: str,         # 视频路径或URL
    context: Dict[str, Any]  # 上下文信息
) -> Dict[str, Any]:
    """
    分析视频
    
    返回:
    {
        'raw_analysis': str,       # 原始分析文本
        'behaviors': List[Dict],   # 行为列表
        'interactions': List[Dict],# 互动列表
        'emotions': Dict,          # 情绪信息
        'attention': Dict,         # 注意力信息
        'summary': str            # 总结
    }
    """
```

#### 2. extract_highlights()

```python
async def extract_highlights(
    video_path: str,
    analysis_result: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    提取关键片段
    
    返回:
    [
        {
            'timestamp': str,      # 时间戳
            'duration': int,       # 持续时间（秒）
            'type': str,          # 类型
            'description': str,    # 描述
            'importance': int      # 重要性（1-5）
        }
    ]
    """
```

## 🔄 Mock vs Real

### Mock模式（默认）

```bash
USE_REAL_DOCUMENT_PARSER=false
USE_REAL_VIDEO_ANALYSIS=false
```

- 返回假数据
- 快速响应
- 用于开发和测试

### Real模式

```bash
USE_REAL_DOCUMENT_PARSER=true
USE_REAL_VIDEO_ANALYSIS=true
DASHSCOPE_API_KEY=your_key
```

- 调用真实的通义千问API
- 返回真实分析结果
- 用于生产环境

## 📁 文件结构

```
services/Multimodal-Understanding/
├── __init__.py              # 模块入口
├── api_interface.py         # 核心接口（parse_text/image/video）
├── config.py                # 配置管理
├── models.py                # 数据模型
├── multimodal_parser.py     # 解析器实现
├── utils.py                 # 工具函数
├── adapters.py              # 系统适配器 ⭐⭐
│   ├── MultimodalDocumentParserService  # 文档解析适配器
│   └── MultimodalVideoAnalysisService   # 视频分析适配器
├── test_simple.py           # 功能测试
├── test_adapters.py         # 适配器测试 ⭐
├── USAGE.md                 # 使用文档
├── INTEGRATION.md           # 集成文档（本文件）
└── README.md                # 模块说明
```

## 🎯 核心优势

1. **一个模块，两个接口** - 充分利用多模态能力
2. **不修改接口** - 完全适配现有系统接口
3. **灵活切换** - 通过配置轻松切换 Mock/Real
4. **独立开发** - 模块内部实现完全独立
5. **统一调用** - 通过容器统一获取和使用

## 💡 使用场景

### 场景1: 初始评估 - 解析医院报告

```python
# 家长上传医院诊断报告（图片）
doc_service = container.get('document_parser')
result = await doc_service.parse_report(
    file_path=uploaded_image_path,
    file_type='image'
)

# 提取诊断信息用于建立孩子档案
child_profile = {
    'diagnosis': result['diagnosis'],
    'severity': result['severity'],
    'initial_assessment': result['recommendations']
}
```

### 场景2: 初始评估 - 解析量表

```python
# 家长填写CARS量表（拍照上传）
doc_service = container.get('document_parser')
result = await doc_service.parse_scale(
    scale_data={'image_path': scale_image_path},
    scale_type='CARS'
)

# 用于评估和建立观察框架
assessment = {
    'total_score': result['total_score'],
    'severity_level': result['severity_level'],
    'key_dimensions': result['dimension_scores']
}
```

### 场景3: 干预会话 - 分析视频

```python
# 干预会话结束后，分析录制的视频
video_service = container.get('video_analysis')
result = await video_service.analyze_video(
    video_path=session_video_path,
    context={
        'child_profile': child_profile,
        'game_info': game_info
    }
)

# 用于生成会话总结
session_summary = {
    'behaviors': result['behaviors'],
    'interactions': result['interactions'],
    'progress': result['summary']
}
```

## 🐛 故障排查

### 问题1: 导入错误

```
ImportError: cannot import name 'MultimodalDocumentParserService'
```

**解决**：确保从 `adapters.py` 导入，而不是其他文件。

### 问题2: API密钥错误

```
ValueError: API key not found
```

**解决**：检查 `.env` 文件中的 `DASHSCOPE_API_KEY`。

### 问题3: 文件格式不支持

```
ValueError: 暂不支持 pdf 格式
```

**解决**：当前只支持图片格式（JPG/PNG），PDF需要先转换为图片。

## 📞 支持

如有问题，请查看：
- `USAGE.md` - 基础使用文档
- `test_simple.py` - 功能测试示例
- `test_adapters.py` - 适配器测试示例

---

**集成完成！你的模块现在适配了两个系统接口。** 🎉

**功能分配：**
- 📄 **文档解析** = 图片解析 + 文本解析
- 🎬 **视频分析** = 视频解析
