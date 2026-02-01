# Memory 服务模块

**记忆驱动架构的核心模块**

## 概述

Memory 服务提供语义化的记忆读写接口，集成 LLM 智能解析，让业务模块能够用"人话"记录和查询记忆。

## 核心功能

### 1. 智能行为记录

**输入**：家长的自然语言描述
```python
"今天玩积木时，辰辰突然把积木递给我，还看了我一眼"
```

**自动完成**：
- LLM 解析事件类型（social/emotion/communication）
- 判断重要性（breakthrough/improvement/normal/concern）
- 提取涉及的对象（积木）
- 推断相关的兴趣维度（construction, social）
- 推断相关的功能维度（eye_contact, social_initiation）
- 自动创建行为节点 + 关系

### 2. 负面事件智能识别

**输入**：
```python
"我今天没忍住，对辰辰吼了一声，他吓哭了，我很自责"
```

**自动完成**：
- 识别负面关键词（吼、哭、自责）
- 判断严重程度（low/medium/high）
- 预估影响持续天数（3-14天）
- 提取触发因素（积木游戏、妈妈参与、要求配合）
- 分析家长情绪（焦虑、疲惫、自责）
- 判断是否需要支持

### 3. 负面事件处理

- 获取最近的负面事件
- 提取需要避让的触发因素
- 评估家长支持需求
- 更新恢复状态

## 使用示例

### 智能记录行为

```python
from services.Memory import get_memory_service

# 获取服务实例
memory = await get_memory_service()

# 智能记录行为（LLM 自动解析）
result = await memory.record_behavior_from_text(
    child_id="child_001",
    raw_input="今天玩积木时，辰辰突然把积木递给我，还看了我一眼",
    input_type="text"
)

print(result)
# {
#     "success": True,
#     "behavior_id": "bh_xxx",
#     "parsed_data": {
#         "event_type": "social",
#         "significance": "breakthrough",
#         "description": "孩子主动递积木给妈妈，同时抬头看了一眼",
#         "objects_involved": ["积木"],
#         "related_interests": ["construction", "social"],
#         "related_functions": ["eye_contact", "social_initiation"]
#     },
#     "message": "行为记录已保存（LLM 智能解析）"
# }
```

### 查询负面事件

```python
# 获取最近的负面事件
concerns = await memory.get_recent_concerns(
    child_id="child_001",
    days=14
)

# 提取触发因素
triggers = await memory.extract_triggers_to_avoid(
    child_id="child_001",
    days=14
)

print(triggers)
# {
#     "activities": ["积木游戏", "高难度任务"],
#     "people": ["妈妈参与"],
#     "situations": ["要求配合"],
#     "all_triggers": ["积木游戏", "妈妈参与", "要求配合", "高难度任务"],
#     "concern_count": 1
# }

# 评估家长支持需求
support = await memory.get_parent_support_needed(
    child_id="child_001",
    days=7
)

print(support)
# {
#     "support_needed": True,
#     "concern_count": 1,
#     "high_severity_count": 1,
#     "needs_professional_help": False,
#     "parent_emotions": ["焦虑、疲惫、自责"],
#     "message": "注意到最近有一些挑战时刻..."
# }
```

### 手动记录行为（不使用 LLM）

```python
from services.Memory.models.nodes import Behavior

# 创建行为节点
behavior = Behavior(
    child_id="child_001",
    event_type="social",
    description="孩子主动递积木给妈妈",
    raw_input="...",
    input_type="text",
    significance="breakthrough"
)

# 保存
behavior_id = await memory.save_behavior(behavior)

# 手动创建关系
await memory.link_behavior_to_child(behavior_id, "child_001")
await memory.link_behavior_to_object(behavior_id, "obj_001")
await memory.link_behavior_to_interest(behavior_id, "construction")
await memory.link_behavior_to_function(behavior_id, "eye_contact")
```

## 配置

在 `.env` 文件中配置：

```bash
# Neo4j 配置
NEO4J_URI=bolt://localhost:7688
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# LLM 配置
MEMORY_ENABLE_LLM=true
MEMORY_LLM_TEMPERATURE=0.3
MEMORY_LLM_MAX_TOKENS=2000

# LLM 服务配置（使用全局 LLM 服务）
LLM_API_KEY=your_api_key
LLM_BASE_URL=https://api.deepseek.com
LLM_MODEL=deepseek-chat
```

## 架构

```
Memory 服务
    ├── service.py          # MemoryService 核心类
    ├── prompts.py          # LLM Prompts 模板
    ├── config.py           # 配置
    └── __init__.py
    
    依赖：
    ├── services/Graphiti   # 图存储层
    └── services/llm_service.py  # LLM 服务
```

## API 文档

### MemoryService

#### 智能解析方法

- `record_behavior_from_text(child_id, raw_input, input_type, context)` - 智能记录行为
- `_parse_behavior_with_llm(raw_input)` - LLM 解析行为
- `_detect_negative_event(raw_input)` - 检测负面事件
- `_auto_link_behavior(behavior_id, child_id, parsed)` - 自动创建关系
- `_find_or_create_object(object_name)` - 查找或创建对象

#### 人物管理

- `save_child(child)` - 保存孩子档案
- `save_person(person)` - 保存人物
- `get_child(child_id)` - 获取孩子档案
- `get_person(person_id)` - 获取人物信息

#### 行为管理

- `save_behavior(behavior)` - 保存行为记录
- `get_behaviors(child_id, start_time, end_time, limit)` - 查询行为记录

#### 负面事件处理

- `get_recent_concerns(child_id, days, only_active)` - 获取最近的负面事件
- `extract_triggers_to_avoid(child_id, days)` - 提取触发因素
- `get_parent_support_needed(child_id, days)` - 评估家长支持需求
- `update_recovery_status(behavior_id, recovery_status, recovery_signs)` - 更新恢复状态

#### 对象管理

- `save_object(obj)` - 保存对象
- `get_object(object_id)` - 获取对象信息

#### 关系管理

- `link_behavior_to_child(behavior_id, child_id)` - 创建"展现"关系
- `link_behavior_to_object(behavior_id, object_id, interaction_type)` - 创建"涉及对象"关系
- `link_behavior_to_interest(behavior_id, interest_name, ...)` - 创建"体现兴趣"关系
- `link_behavior_to_function(behavior_id, function_name, ...)` - 创建"反映功能"关系
- `link_behavior_to_person(behavior_id, person_id, role, ...)` - 创建"涉及人物"关系
- `link_object_to_interest(object_id, interest_name, ...)` - 创建"属于兴趣类别"关系

#### 辅助方法

- `initialize()` - 初始化服务
- `close()` - 关闭服务
- `clear_all_data()` - 清空所有数据
- `clear_child_data(child_id)` - 清空某个孩子的数据

## 优势

1. **降低使用门槛**：家长只需说"人话"，不需要填表单
2. **智能识别**：自动识别负面事件，不需要手动标记
3. **自动关联**：自动推断涉及的对象、兴趣、功能维度
4. **减少业务模块工作**：业务模块只需传原始文本

## 下一步

- [ ] 游戏总结（LLM 整合多源数据）
- [ ] 评估生成（LLM 分析行为记录）
- [ ] 趋势分析（LLM 分析功能维度变化）
