# Graphiti 模块变更日志

## v3.1.0 - 2026-01-30 - Memory 服务独立 + LLM 智能解析

### 🎉 架构调整 + LLM 集成

将 MemoryService 独立为 `services/Memory/` 模块，并集成 LLM 智能解析功能。

### ✨ 新增功能

#### Memory 服务独立
- MemoryService 从 Graphiti 模块移到 `services/Memory/`
- Graphiti 模块只负责图存储操作
- Memory 服务提供语义化的记忆读写接口

#### LLM 智能解析
- **智能行为记录**：家长用自然语言描述，LLM 自动提取结构化数据
- **负面事件智能识别**：自动识别家长情绪失控、孩子受惊吓等负面事件
- **自动关联**：自动推断涉及的对象、兴趣维度、功能维度
- **家长支持评估**：自动分析家长情绪，判断是否需要支持

#### 新增文件
```
services/Memory/
├── __init__.py
├── service.py          # MemoryService（从 Graphiti 移过来 + LLM 扩展）
├── prompts.py          # LLM Prompts 模板
├── config.py           # 配置
└── README.md           # 完整文档
```

#### 测试验证
- `tests/test_memory_llm.py` - LLM 智能解析功能测试 ✅
  - 测试 5 个场景（3 个正面 + 2 个负面）
  - 验证 LLM 自动识别事件类型、重要性、对象、兴趣、功能
  - 验证负面事件智能识别和触发因素提取
  - 验证家长支持需求评估

### 📦 架构变化

**之前**：
```
services/Graphiti/
├── service.py          # MemoryService（混在 Graphiti 里）
├── api_interface.py
└── adapters.py
```

**现在**：
```
services/Memory/        # ✨ 新建：记忆服务（独立模块）
├── service.py          # MemoryService + LLM 智能解析
├── prompts.py
└── config.py

services/Graphiti/      # Graphiti 模块（只负责图存储）
├── storage/            # 图存储操作
├── models/             # 数据模型
├── api_interface.py    # 调用 Memory 服务
└── adapters.py         # 调用 api_interface
```

### 🔧 API 变化

#### 新增接口（Memory 服务）

**智能行为记录**：
```python
from services.Memory import get_memory_service

memory = await get_memory_service()

# 家长只需要说人话
result = await memory.record_behavior_from_text(
    child_id="child_001",
    raw_input="今天玩积木时，辰辰突然把积木递给我，还看了我一眼"
)

# LLM 自动解析：
# - 事件类型：social
# - 重要性：breakthrough
# - 涉及对象：积木
# - 相关兴趣：construction
# - 相关功能：eye_contact, social_initiation
```

#### 原有接口保持兼容

Graphiti 的 `api_interface.py` 和 `adapters.py` 保持不变，内部调用 Memory 服务。

---

## v3.0.0 - 2026-01-30 - 记忆驱动架构重构

### 🎉 完全重构（第二次）

基于设计文档 `docs/plans/2026-01-30-memory-driven-architecture-design.md` 完全重构 Graphiti 模块。

### ✨ 核心理念

**记忆驱动架构**：所有模块不直接通信，而是通过读写"记忆"来交换数据。

### 📦 新图结构

#### 7种节点类型
1. **Person** - 人物（孩子/家长/老师/朋友/兄弟姐妹）
2. **Behavior** - 行为事件
3. **Object** - 对象（玩具/物品）
4. **InterestDimension** - 兴趣维度（8个固定节点）
5. **FunctionDimension** - 功能维度（33个固定节点）
6. **FloorTimeGame** - 地板游戏
7. **ChildAssessment** - 儿童评估

#### 固定维度节点
- **8类兴趣**：visual, auditory, tactile, motor, construction, order, cognitive, social
- **33个功能维度**：分为6大类（sensory, social, language, motor, emotional, self_care）

#### 关系类型
- 人物相关：RELATED_TO, 展现, 观察, 实施, 参与, 评估, 接受
- 行为相关：涉及对象, 涉及人物, 体现兴趣, 反映功能
- 对象相关：属于兴趣类别
- 核心边（数据在边上）：具有兴趣, 具有功能, 评估兴趣, 评估功能
- 游戏相关：使用对象, 训练功能, 激发兴趣, 产生行为

### 🔧 去重机制

- 所有节点创建使用 **MERGE** 替代 CREATE
- **7个唯一约束**（自动创建索引）
- **13个额外索引**（查询优化）
- ON CREATE SET / ON MATCH SET 更新策略

### 📦 新增模块

```
services/Graphiti/
├── models/              # 数据模型
│   ├── nodes.py         # 7种节点定义
│   ├── edges.py         # 边类型和属性定义
│   ├── dimensions.py    # 8类兴趣+33个功能维度
│   └── filters.py       # 查询过滤器
├── storage/             # 存储层
│   ├── graph_storage.py # 核心存储操作（使用 MERGE 去重）
│   └── index_manager.py # 唯一约束和索引管理
├── utils/               # 工具函数
│   ├── query_builder.py # Cypher查询构建器
│   ├── validators.py    # 数据验证工具
│   ├── time_series.py   # 时间序列处理
│   └── statistics.py    # 统计函数
├── service.py           # MemoryService - 记忆服务层
└── config.py            # 配置
```

### � MemoryService - 记忆服务层

#### 核心职责
1. **语义化接口** - 业务模块用人话说"我要记录一个行为"
2. **智能解析** - 把自然语言转成结构化数据（LLM，待实现）
3. **数据验证** - 确保写入的数据符合规范

#### 已实现功能

**人物相关**
- `save_child(child: Person) -> str` - 保存孩子档案
- `save_person(person: Person) -> str` - 保存人物（家长/老师等）
- `get_child(child_id: str) -> Dict` - 获取孩子档案
- `get_person(person_id: str) -> Dict` - 获取人物信息

**行为相关**
- `save_behavior(behavior: Behavior) -> str` - 保存行为记录
- `get_behaviors(child_id, start_time, end_time, limit) -> List[Dict]` - 查询行为记录

**对象相关**
- `save_object(obj: Object) -> str` - 保存对象（玩具/物品）
- `get_object(object_id: str) -> Dict` - 获取对象信息

**关系相关**
- `link_behavior_to_child(behavior_id, child_id) -> bool` - 创建"展现"关系
- `link_behavior_to_object(behavior_id, object_id, interaction_type) -> bool` - 创建"涉及对象"关系
- `link_behavior_to_interest(behavior_id, interest_name, intensity, duration, positive_response) -> bool` - 创建"体现兴趣"关系
- `link_behavior_to_function(behavior_id, function_name, score, evidence_strength) -> bool` - 创建"反映功能"关系
- `link_object_to_interest(object_id, interest_name, primary, relevance_score) -> bool` - 创建"属于兴趣类别"关系
- `link_behavior_to_person(behavior_id, person_id, role, interaction_quality, involvement_level, notes) -> bool` - 创建"涉及人物"关系（支持4种角色：facilitator/participant/observer/trigger）

**负面事件处理**
- `get_recent_concerns(child_id, days, only_active) -> List[Dict]` - 获取最近的负面事件
- `extract_triggers_to_avoid(child_id, days) -> Dict` - 提取需要避让的触发因素
- `get_parent_support_needed(child_id, days) -> Dict` - 检查家长是否需要支持
- `update_recovery_status(behavior_id, recovery_status, recovery_signs) -> bool` - 更新恢复状态

**辅助方法**
- `clear_all_data()` - 清空所有数据（MATCH (n) DETACH DELETE n）
- `clear_child_data(child_id)` - 清空某个孩子的所有数据

### 📚 测试

- `tests/test_graphiti_demo.py` - 完整功能演示 ✅
- `tests/test_dedup.py` - 去重功能验证 ✅
- `tests/test_memory_service.py` - 基础服务层测试 ✅
- `tests/test_memory_service_full.py` - 完整功能测试 ✅
  - 11个行为记录（8个正常 + 2个负面事件 + 1个多人互动）
  - 4个对象节点
  - 4个人物节点
  - 负面事件处理验证
  - 人物关联验证（3个关联：妈妈触发者 + 老师引导者 + 妈妈观察者）
- `tests/test_memory_service.py` - 基础服务层测试 ✅（需要 Neo4j 环境）

### 📝 待完成

#### Phase 5: LLM 集成
- [ ] 创建 `llm_integration.py`
- [ ] 设计 LLM Prompts
- [ ] 实现智能解析方法：
  - [ ] `record_behavior()` - 解析自然语言为结构化行为
  - [ ] `generate_assessment()` - 生成评估结果
  - [ ] `summarize_game()` - 游戏总结
  - [ ] **负面事件智能识别** - 自动识别家长描述中的负面事件，提取触发因素

#### Phase 6: 接口层 ✅
- `api_interface.py` - 重写完成，提供RESTful风格的API接口
  - 人物管理：`save_child_profile()`, `save_person_profile()`, `get_child_profile()`
  - 行为记录：`record_behavior()`, `get_behaviors()`
  - 对象管理：`save_object()`
  - 负面事件：`get_recent_concerns()`, `get_triggers_to_avoid()`, `get_parent_support()`
  - 工具：`clear_all_data()`, `clear_child_data()`
- `adapters.py` - 重写完成，适配系统接口
  - 实现 IGraphitiService 接口
  - 提供旧版接口兼容（v2.0 接口返回待实现提示）
- `tests/test_graphiti_api.py` - API接口测试通过 ✅
  - 测试人物管理（3个人物）
  - 测试对象管理（2个对象）
  - 测试行为记录（3个行为：突破/负面/多人互动）
  - 测试负面事件处理（1个负面事件，4个触发因素）
  - 测试适配器（2个接口调用）

#### Phase 7: 负面事件处理增强
- [ ] 游戏推荐模块：增加触发因素避让逻辑
- [ ] 评估模块：分析负面事件对功能维度的影响
- [ ] 家长支持：自动提供情绪管理资源和建议

### 📋 设计增强

#### 负面事件处理规范 (2026-01-30)

增加了完整的负面事件记录和处理规范，用于处理可能对孩子造成心理影响的事件（如家长情绪失控）。

**核心特性**：
- 标准化的负面事件记录格式（`significance="concern"` + `negative_event=True`）
- 触发因素提取和避让机制
- 影响持续时间预估
- 恢复状态追踪
- 家长支持和资源推荐
- 游戏推荐自动调整（避开触发因素，推荐低压力游戏）

**使用场景**：
- 家长情绪失控（吼叫、发脾气）
- 孩子受惊吓或创伤
- 游戏中的负面体验
- 同伴冲突
- 感官过载

详见设计文档 3.2.1 节。

---

## v2.0.0 - 2026-01-29

### 🎉 完全重构（第一次）

基于设计文档 `docs/plans/2026-01-29-graphiti-optimization-design.md` 完全重构 Graphiti 模块。

### ✨ 新特性

#### 1. 自定义图结构
- 不再使用 Graphiti Episode 模式
- 直接操作 Neo4j，创建自定义节点和边
- 节点类型：Child, Dimension, Observation, Milestone
- 边类型：HAS_DIMENSION, HAS_OBSERVATION, TRIGGERS, CORRELATES_WITH

#### 2. 多维度趋势分析
- 支持 7天/30天/90天 多时间窗口趋势分析
- 线性回归计算趋势方向（improving/stable/declining）
- 统计显著性检验（p-value）
- 置信度评估（R²值）

#### 3. 平台期检测
- 基于变异系数（CV）检测进展停滞
- 自动回溯计算平台期持续天数
- 提供干预策略建议

#### 4. 异常波动检测
- 基于标准差检测异常数值
- 区分突破性进步（spike）和状态波动（drop）
- 提供解释和建议

#### 5. 跨维度关联分析
- 皮尔逊相关系数计算
- 互相关分析计算时滞（lag）
- 自动推断因果关系
- 存储关联结果到图数据库

#### 6. 标准化数据格式
- 统一的输入数据结构
- 支持 12 个标准维度（6个里程碑 + 6个行为）
- 支持多种值类型（score/count/duration/boolean）

---

## v1.0.0 - 2026-01-26

### 初始版本
- 基于 graphiti-core 的 Episode 模式
- 基础记忆存储和检索功能
