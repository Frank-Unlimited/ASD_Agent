# 模块开发与集成指南

## 📋 目录
1. [项目架构概览](#项目架构概览)
2. [开发新模块的步骤](#开发新模块的步骤)
3. [集成模块到系统](#集成模块到系统)
4. [实战示例：多模态解析模块](#实战示例多模态解析模块)
5. [最佳实践](#最佳实践)

---

## 项目架构概览

### 核心设计理念
- **接口先行**：所有模块先定义接口，再实现
- **依赖注入**：通过容器管理服务实例
- **Mock驱动**：先用Mock验证架构，再逐步替换真实实现
- **配置切换**：通过环境变量控制Mock/Real

### 目录结构
```
project/
├── src/                          # 核心代码
│   ├── interfaces/               # 接口定义（契约层）
│   │   ├── base.py              # 基础接口
│   │   ├── infrastructure.py    # 基础设施层接口（模块1-6）
│   │   └── business.py          # 业务逻辑层接口（模块7-16）
│   ├── container.py             # 依赖注入容器
│   ├── config.py                # 配置管理
│   └── main.py                  # FastAPI入口
├── services/                     # 服务实现
│   ├── mock/                    # Mock实现（快速验证）
│   ├── real/                    # 真实实现（逐步替换）
│   └── YourModule/              # 你的新模块
└── docs/                        # 文档
```

### 三层架构

```
┌─────────────────────────────────────┐
│   LangGraph 工作流层（编排层）        │
│   - 调用接口，不关心实现              │
└─────────────────────────────────────┘
              ↓ 调用
┌─────────────────────────────────────┐
│   接口层（契约层）                    │
│   - 定义所有模块的接口                │
│   - src/interfaces/                 │
└─────────────────────────────────────┘
              ↓ 实现
┌─────────────────────────────────────┐
│   服务实现层                          │
│   - Mock实现（services/mock/）       │
│   - Real实现（services/real/）       │
│   - 自定义模块（services/YourModule/）│
└─────────────────────────────────────┘
```

---

## 开发新模块的步骤

### 步骤1：确定模块类型

**基础设施层模块**（模块1-6）：
- 提供底层能力（数据库、AI服务、文件处理等）
- 被业务层调用
- 示例：视频解析、语音识别、数据存储

**业务逻辑层模块**（模块7-16）：
- 实现业务逻辑
- 调用基础设施层
- 示例：评估、计划推荐、总结生成

### 步骤2：定义接口

在 `src/interfaces/` 中定义接口：

**基础设施层接口** → `src/interfaces/infrastructure.py`
**业务逻辑层接口** → `src/interfaces/business.py`

```python
# 示例：定义多模态解析接口
from abc import ABC, abstractmethod
from typing import Dict, Any
from src.interfaces.base import BaseService

class IMultimodalService(BaseService):
    """多模态解析接口"""
    
    @abstractmethod
    async def parse_text(self, text: str, prompt: str = None) -> str:
        """解析文本"""
        pass
    
    @abstractmethod
    async def parse_image(self, image_url: str, prompt: str = None) -> str:
        """解析图片"""
        pass
    
    @abstractmethod
    async def parse_video(self, video_url: str, prompt: str = None) -> str:
        """解析视频"""
        pass
    
    def get_service_name(self) -> str:
        return "multimodal"
    
    def get_service_version(self) -> str:
        return "1.0.0"
```

### 步骤3：创建Mock实现

在 `services/mock/` 中创建Mock实现：

```python
# services/mock/multimodal_service.py
from src.interfaces.infrastructure import IMultimodalService

class MockMultimodalService(IMultimodalService):
    """多模态解析Mock实现"""
    
    async def parse_text(self, text: str, prompt: str = None) -> str:
        return f"[Mock] 文本解析结果: {text[:50]}..."
    
    async def parse_image(self, image_url: str, prompt: str = None) -> str:
        return f"[Mock] 图片解析结果: {image_url}"
    
    async def parse_video(self, video_url: str, prompt: str = None) -> str:
        return f"[Mock] 视频解析结果: {video_url}"
    
    def get_service_name(self) -> str:
        return "multimodal"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
```

### 步骤4：实现真实服务

在 `services/` 中创建你的模块文件夹：

```
services/
└── Multimodal-Understanding/
    ├── __init__.py
    ├── api_interface.py      # 对外接口
    ├── config.py             # 配置
    ├── models.py             # 数据模型
    ├── multimodal_parser.py  # 核心逻辑
    └── utils.py              # 工具函数
```

创建适配器类：

```python
# services/Multimodal-Understanding/service_adapter.py
from src.interfaces.infrastructure import IMultimodalService
from .api_interface import parse_text, parse_image, parse_video

class MultimodalService(IMultimodalService):
    """多模态解析真实实现（适配器）"""
    
    async def parse_text(self, text: str, prompt: str = None) -> str:
        # 调用你的实际实现
        return parse_text(text, prompt)
    
    async def parse_image(self, image_url: str, prompt: str = None) -> str:
        return parse_image(image_url, prompt)
    
    async def parse_video(self, video_url: str, prompt: str = None) -> str:
        return parse_video(video_url, prompt)
    
    def get_service_name(self) -> str:
        return "multimodal"
    
    def get_service_version(self) -> str:
        return "1.0.0"
```

### 步骤5：注册到容器

修改 `src/container.py`：

```python
def init_services():
    """初始化所有服务"""
    
    # ... 其他服务注册 ...
    
    # 注册多模态服务
    if settings.use_real_multimodal:
        from services.Multimodal_Understanding.service_adapter import MultimodalService
        container.register('multimodal', MultimodalService())
    else:
        from services.mock.multimodal_service import MockMultimodalService
        container.register('multimodal', MockMultimodalService())
```

### 步骤6：添加配置项

修改 `src/config.py`：

```python
class Settings(BaseSettings):
    # ... 其他配置 ...
    
    # 多模态服务配置
    use_real_multimodal: bool = False
    dashscope_api_key: str = ""
```

修改 `.env.example`：

```bash
# 多模态服务配置
USE_REAL_MULTIMODAL=false
DASHSCOPE_API_KEY=your_api_key_here
```

### 步骤7：在工作流中使用

在 LangGraph 节点中调用：

```python
from src.container import container

async def video_analysis_node(state: DynamicInterventionState):
    """视频分析节点"""
    
    # 获取服务（自动根据配置返回Mock或Real）
    multimodal_service = container.get('multimodal')
    
    # 调用服务
    video_url = state['tempData']['videoPath']
    result = await multimodal_service.parse_video(
        video_url, 
        "请分析视频中儿童的行为表现"
    )
    
    # 更新状态
    state['currentSession']['videoAnalysis'] = result
    return state
```

---

## 集成模块到系统

### 集成检查清单

- [ ] 接口已定义在 `src/interfaces/`
- [ ] Mock实现已创建在 `services/mock/`
- [ ] 真实实现已创建在 `services/YourModule/`
- [ ] 适配器类已创建
- [ ] 服务已注册到容器
- [ ] 配置项已添加
- [ ] 环境变量已配置
- [ ] 单元测试已编写
- [ ] 文档已更新

### 测试流程

#### 1. 测试Mock实现

```python
# tests/test_multimodal_mock.py
import pytest
from services.mock.multimodal_service import MockMultimodalService

@pytest.mark.asyncio
async def test_mock_parse_image():
    service = MockMultimodalService()
    result = await service.parse_image("https://example.com/image.jpg", "描述图片")
    assert "[Mock]" in result
    assert "image.jpg" in result
```

#### 2. 测试真实实现

```python
# tests/test_multimodal_real.py
import pytest
from services.Multimodal_Understanding.service_adapter import MultimodalService

@pytest.mark.asyncio
async def test_real_parse_image():
    service = MultimodalService()
    result = await service.parse_image(
        "https://img.alicdn.com/imgextra/i1/O1CN01gDEY8M1W114Hi3XcN_!!6000000002727-0-tps-1024-406.jpg",
        "这道题怎么解答？"
    )
    assert len(result) > 0
    assert "[Mock]" not in result
```

#### 3. 测试容器集成

```python
# tests/test_container.py
from src.container import container, init_services
from src.config import settings

def test_container_multimodal_mock():
    settings.use_real_multimodal = False
    init_services()
    service = container.get('multimodal')
    assert service.get_service_version().endswith('-mock')

def test_container_multimodal_real():
    settings.use_real_multimodal = True
    init_services()
    service = container.get('multimodal')
    assert not service.get_service_version().endswith('-mock')
```

---

## 实战示例：多模态解析模块

### 当前状态

你已经创建了 `services/Multimodal-Understanding/` 模块，包含：
- ✅ 核心功能实现（parse_text, parse_image, parse_video）
- ✅ 配置管理（config.py）
- ✅ 数据模型（models.py）
- ✅ 工具函数（utils.py）
- ✅ 测试文件（test_simple.py）

### 需要完成的集成步骤

#### 1. 定义接口

```python
# 在 src/interfaces/infrastructure.py 中添加

class IMultimodalService(BaseService):
    """多模态解析接口"""
    
    @abstractmethod
    async def parse_text(self, text: str, prompt: Optional[str] = None) -> str:
        """解析文本"""
        pass
    
    @abstractmethod
    async def parse_image(self, image_url: str, prompt: Optional[str] = None) -> str:
        """解析图片（支持URL或base64）"""
        pass
    
    @abstractmethod
    async def parse_video(self, video_url: str, prompt: Optional[str] = None) -> str:
        """解析视频（支持URL或base64）"""
        pass
```

#### 2. 创建Mock实现

```python
# services/mock/multimodal_service.py
from src.interfaces.infrastructure import IMultimodalService

class MockMultimodalService(IMultimodalService):
    """多模态解析Mock实现"""
    
    async def parse_text(self, text: str, prompt: str = None) -> str:
        return f"[Mock] 文本解析: {text[:100]}"
    
    async def parse_image(self, image_url: str, prompt: str = None) -> str:
        return f"[Mock] 图片解析: 这是一张包含{prompt or '内容'}的图片"
    
    async def parse_video(self, video_url: str, prompt: str = None) -> str:
        return f"[Mock] 视频解析: 视频展示了{prompt or '场景'}"
    
    def get_service_name(self) -> str:
        return "multimodal"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
```

#### 3. 创建适配器

```python
# services/Multimodal-Understanding/service_adapter.py
from src.interfaces.infrastructure import IMultimodalService
from .api_interface import parse_text, parse_image, parse_video

class MultimodalService(IMultimodalService):
    """多模态解析真实实现"""
    
    async def parse_text(self, text: str, prompt: str = None) -> str:
        # 你的实现是同步的，这里包装成异步
        return parse_text(text, prompt)
    
    async def parse_image(self, image_url: str, prompt: str = None) -> str:
        return parse_image(image_url, prompt)
    
    async def parse_video(self, video_url: str, prompt: str = None) -> str:
        return parse_video(video_url, prompt)
    
    def get_service_name(self) -> str:
        return "multimodal"
    
    def get_service_version(self) -> str:
        return "1.0.0"
```

#### 4. 更新Mock导出

```python
# services/mock/__init__.py 中添加
from services.mock.multimodal_service import MockMultimodalService

__all__ = [
    # ... 其他服务 ...
    'MockMultimodalService',
]
```

#### 5. 注册到容器

```python
# src/container.py 中添加
def init_services():
    # ... 其他服务 ...
    
    # 多模态服务
    if settings.use_real_multimodal:
        from services.Multimodal_Understanding.service_adapter import MultimodalService
        container.register('multimodal', MultimodalService())
    else:
        container.register('multimodal', MockMultimodalService())
```

#### 6. 添加配置

```python
# src/config.py 中添加
class Settings(BaseSettings):
    # ... 其他配置 ...
    
    # 多模态服务
    use_real_multimodal: bool = False
    dashscope_api_key: str = ""
```

#### 7. 使用示例

```python
# 在任何需要的地方使用
from src.container import container

async def analyze_child_video(video_path: str):
    # 获取服务（自动根据配置选择Mock或Real）
    multimodal = container.get('multimodal')
    
    # 调用服务
    result = await multimodal.parse_video(
        video_path,
        "请分析视频中儿童的眼神接触、肢体动作和互动行为"
    )
    
    return result
```

---

## 最佳实践

### 1. 接口设计原则

- **单一职责**：每个接口只负责一类功能
- **最小化**：只暴露必要的方法
- **异步优先**：使用 async/await
- **类型提示**：使用完整的类型注解

### 2. Mock实现原则

- **快速返回**：不要有真实的网络请求或计算
- **有意义的假数据**：返回符合接口契约的数据
- **标记Mock**：在返回值中包含 `[Mock]` 标记

### 3. 真实实现原则

- **错误处理**：捕获并处理所有可能的异常
- **日志记录**：记录关键操作和错误
- **配置驱动**：通过配置控制行为
- **可测试**：编写单元测试和集成测试

### 4. 集成原则

- **渐进式**：先Mock，后Real
- **可切换**：通过配置切换实现
- **向后兼容**：接口变更要考虑兼容性
- **文档完善**：更新相关文档

### 5. 命名规范

```python
# 接口命名：I + 功能名 + Service
class IMultimodalService(BaseService): pass

# Mock实现：Mock + 功能名 + Service
class MockMultimodalService(IMultimodalService): pass

# 真实实现：功能名 + Service
class MultimodalService(IMultimodalService): pass

# 容器注册名：小写，下划线分隔
container.register('multimodal', service)
```

---

## 常见问题

### Q1: 我的模块是同步的，如何适配异步接口？

```python
import asyncio

class MyService(IMyService):
    async def my_method(self, param: str) -> str:
        # 方式1：在线程池中运行同步代码
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, sync_function, param)
        return result
        
        # 方式2：直接调用（如果很快）
        return sync_function(param)
```

### Q2: 如何在模块间共享数据？

通过 State 传递：

```python
async def node_a(state: DynamicInterventionState):
    service = container.get('service_a')
    result = await service.process()
    state['tempData']['result_a'] = result
    return state

async def node_b(state: DynamicInterventionState):
    # 使用 node_a 的结果
    result_a = state['tempData']['result_a']
    service = container.get('service_b')
    result = await service.process(result_a)
    return state
```

### Q3: 如何处理大文件上传？

```python
class IMultimodalService(BaseService):
    @abstractmethod
    async def parse_video_file(
        self, 
        file_path: str,  # 使用文件路径而不是内容
        prompt: str = None
    ) -> str:
        pass
```

### Q4: 如何添加缓存？

```python
from functools import lru_cache

class MultimodalService(IMultimodalService):
    @lru_cache(maxsize=100)
    async def parse_image(self, image_url: str, prompt: str = None) -> str:
        # 实现
        pass
```

---

## 总结

开发和集成新模块的核心流程：

1. **定义接口** → `src/interfaces/`
2. **创建Mock** → `services/mock/`
3. **实现真实服务** → `services/YourModule/`
4. **创建适配器** → 连接接口和实现
5. **注册到容器** → `src/container.py`
6. **添加配置** → `src/config.py` + `.env`
7. **编写测试** → `tests/`
8. **在工作流中使用** → 通过容器获取服务

这种架构的优势：
- ✅ 接口稳定，实现灵活
- ✅ Mock驱动，快速验证
- ✅ 渐进式开发，降低风险
- ✅ 配置切换，方便测试
- ✅ 依赖注入，松耦合

现在你可以按照这个指南，将你的多模态解析模块完整集成到系统中了！
