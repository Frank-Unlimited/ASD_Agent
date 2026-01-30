# 依赖注入更新 - Memory 服务集成

## 更新时间
2026-01-30

## 更新内容

### 1. Memory 服务的特殊处理

Memory 服务作为底层服务，**不通过容器注册**，而是通过 `get_memory_service()` 函数获取单例。

**原因**：
- Memory 服务需要异步初始化（`await get_memory_service()`）
- Memory 服务是单例，全局共享
- 避免在同步的容器初始化中处理异步逻辑

**使用方式**：
```python
from services.Memory.service import get_memory_service

# 在异步函数中
memory_service = await get_memory_service()
```

---

### 2. 游戏服务的依赖注入更新

#### 游戏推荐服务（GameRecommender）

**旧的注册方式**：
```python
from services.game import GameRecommenderService
game_recommender = GameRecommenderService(
    sqlite_service=container.get('sqlite'),
    llm_service=container.get('llm')
)
```

**新的注册方式**：
```python
from services.game import GameRecommender
from services.Memory.service import get_memory_service
import asyncio

# Memory 服务需要异步初始化
memory_service = asyncio.run(get_memory_service())

game_recommender = GameRecommender(
    profile_service=container.get('profile'),
    memory_service=memory_service,  # ✅ 添加 Memory 服务
    sqlite_service=container.get('sqlite')
)
```

**依赖关系**：
- `profile_service`: 档案服务
- `memory_service`: Memory 服务（新增）
- `sqlite_service`: SQLite 服务

---

#### 游戏总结服务（GameSummarizer）

**新增注册**：
```python
from services.game import GameSummarizer

# 复用已初始化的 Memory 服务
if 'game_recommender' in container._services:
    memory_service = container.get('game_recommender').memory_service
else:
    from services.Memory.service import get_memory_service
    import asyncio
    memory_service = asyncio.run(get_memory_service())

game_summarizer = GameSummarizer(
    profile_service=container.get('profile'),
    memory_service=memory_service,  # ✅ 添加 Memory 服务
    sqlite_service=container.get('sqlite')
)
```

**依赖关系**：
- `profile_service`: 档案服务
- `memory_service`: Memory 服务（新增）
- `sqlite_service`: SQLite 服务

**优化**：复用 GameRecommender 中已初始化的 Memory 服务，避免重复初始化。

---

### 3. 服务依赖图

```
┌─────────────────────────────────────────────────────────┐
│                    容器注册的服务                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  基础服务：                                              │
│  • sqlite_service                                       │
│  • llm_service                                          │
│  • file_upload_service                                  │
│  • speech_service                                       │
│  • video_analysis_service                               │
│  • document_parser_service                              │
│                                                         │
│  业务服务：                                              │
│  • profile_service                                      │
│    ├─ sqlite_service                                    │
│    └─ llm_service                                       │
│                                                         │
│  • observation_service                                  │
│    ├─ sqlite_service                                    │
│    └─ llm_service                                       │
│                                                         │
│  • game_recommender ✅ 新增 Memory 依赖                 │
│    ├─ profile_service                                   │
│    ├─ memory_service (通过 get_memory_service())       │
│    └─ sqlite_service                                    │
│                                                         │
│  • game_summarizer ✅ 新增                              │
│    ├─ profile_service                                   │
│    ├─ memory_service (复用 game_recommender 的)        │
│    └─ sqlite_service                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│              不通过容器注册的服务                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  • memory_service                                       │
│    通过 get_memory_service() 获取单例                   │
│    ├─ graphiti (GraphStorage)                          │
│    └─ llm_service (通过 get_llm_service())             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

### 4. 使用示例

#### 在 API 路由中使用游戏服务

```python
from src.container import container

# 获取游戏推荐服务
game_recommender = container.get('game_recommender')

# 推荐游戏
response = await game_recommender.recommend_game(request)
# ✅ 自动从 Memory 获取历史数据
# ✅ 自动保存到 Memory（Graphiti）
```

```python
# 获取游戏总结服务
game_summarizer = container.get('game_summarizer')

# 总结游戏
response = await game_summarizer.summarize_session(request)
# ✅ 自动从 Memory 获取历史数据
# ✅ 自动保存到 Memory（Graphiti）
# ✅ 自动创建关键行为节点
```

---

### 5. 注意事项

#### Memory 服务的初始化时机
- Memory 服务在容器初始化时通过 `asyncio.run()` 同步调用异步初始化
- 这是一个权衡：虽然在同步代码中调用异步函数不是最佳实践，但可以简化容器的使用
- 未来可以考虑将整个容器初始化改为异步

#### Memory 服务的单例模式
- `get_memory_service()` 返回全局单例
- 多次调用返回同一个实例
- 确保 Memory 服务在整个应用中只有一个实例

#### 服务复用
- GameSummarizer 复用 GameRecommender 的 Memory 服务实例
- 避免重复初始化，提高性能

---

### 6. 测试建议

#### 单元测试
```python
import pytest
from src.container import container, init_services

@pytest.fixture
def setup_container():
    init_services()
    yield container

def test_game_recommender_has_memory(setup_container):
    game_recommender = setup_container.get('game_recommender')
    assert hasattr(game_recommender, 'memory_service')
    assert game_recommender.memory_service is not None

def test_game_summarizer_has_memory(setup_container):
    game_summarizer = setup_container.get('game_summarizer')
    assert hasattr(game_summarizer, 'memory_service')
    assert game_summarizer.memory_service is not None

def test_memory_service_is_shared(setup_container):
    game_recommender = setup_container.get('game_recommender')
    game_summarizer = setup_container.get('game_summarizer')
    # 两个服务应该共享同一个 Memory 服务实例
    assert game_recommender.memory_service is game_summarizer.memory_service
```

#### 集成测试
```python
@pytest.mark.asyncio
async def test_game_recommendation_with_memory():
    """测试游戏推荐是否正确使用 Memory 服务"""
    game_recommender = container.get('game_recommender')
    
    request = GameRecommendRequest(
        child_id="test_child_001",
        focus_dimension=TargetDimension.EYE_CONTACT
    )
    
    response = await game_recommender.recommend_game(request)
    
    # 验证游戏已保存到 Memory
    game = await game_recommender.memory_service.get_game(response.game_plan.game_id)
    assert game is not None
    assert game['child_id'] == "test_child_001"
```

---

## 总结

依赖注入已更新完成，游戏服务现在正确集成了 Memory 服务。记忆驱动架构的完整闭环已经打通！

**下一步**：
1. 更新 API 路由，确保正确使用容器中的服务
2. 创建端到端测试
3. 实现其他业务模块（行为观察、评估）
