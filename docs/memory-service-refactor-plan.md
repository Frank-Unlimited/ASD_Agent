# Memory Service 重构方案

## 目标

使用 Graphiti-core 的原生 LLM 提取能力替换手动实现，同时保持对外接口不变。

## 重构原则

1. **接口不变**：所有公开方法的签名和返回值格式保持不变
2. **向后兼容**：现有调用方无需修改代码
3. **性能提升**：利用 Graphiti-core 的优化（分块、并发、缓存）
4. **代码简化**：删除重复的 LLM 调用和节点创建逻辑

## 重构内容

### 1. 初始化部分

**当前实现：**
```python
def __init__(self, config: Optional[MemoryConfig] = None):
    self.storage = GraphStorage(...)
    self._llm_service = None
```

**重构后：**
```python
def __init__(self, config: Optional[MemoryConfig] = None):
    self.config = config or MemoryConfig()
    
    # 使用 Graphiti-core 替代 GraphStorage
    self.graphiti = Graphiti(
        uri=self.config.neo4j_uri,
        user=self.config.neo4j_user,
        password=self.config.neo4j_password,
        llm_client=OpenAIClient(...),  # 使用配置的 LLM
        embedder=OpenAIEmbedder(...),
        store_raw_episode_content=True
    )
    
    # 保留 storage 用于直接查询（向后兼容）
    self.storage = GraphStorage(...)
```

### 2. record_behavior() 方法

**当前实现：**
- 手动调用 LLM 解析
- 手动创建 Behavior 节点
- 手动创建关系

**重构后：**
```python
async def record_behavior(
    self,
    child_id: str,
    raw_input: str,
    input_type: str = "text",
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """保持接口不变"""
    
    # 使用 Graphiti-core 自动提取
    result = await self.graphiti.add_episode(
        name=f"行为观察_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        episode_body=raw_input,
        source_description="家长观察记录",
        reference_time=datetime.now(),
        source=EpisodeType.observation,
        group_id=child_id,
        entity_types={
            "Behavior": BehaviorEntityModel,
            "Object": ObjectEntityModel,
            "Interest": InterestEntityModel,
            "Function": FunctionEntityModel
        },
        edge_types={
            "展现": ExhibitEdgeModel,
            "涉及对象": InvolveObjectEdgeModel,
            "体现兴趣": ShowInterestEdgeModel,
            "体现功能": ShowFunctionEdgeModel
        },
        custom_extraction_instructions=BEHAVIOR_EXTRACTION_INSTRUCTIONS
    )
    
    # 转换为原有返回格式（保持兼容）
    return {
        "behavior_id": result.episode.uuid,
        "child_id": child_id,
        "timestamp": result.episode.valid_at.isoformat(),
        "event_type": _extract_event_type(result.nodes),
        "description": _extract_description(result.nodes),
        "raw_input": raw_input,
        "input_type": input_type,
        "significance": _extract_significance(result.nodes),
        "ai_analysis": _build_ai_analysis(result.nodes, result.edges),
        "context": context or {},
        "objects_involved": _extract_objects(result.nodes),
        "related_interests": _extract_interests(result.edges),
        "related_functions": _extract_functions(result.edges)
    }
```

### 3. summarize_game() 方法

**当前实现：**
- 手动调用 LLM 生成总结
- 手动更新游戏节点

**重构后：**
```python
async def summarize_game(
    self,
    game_id: str,
    video_analysis: Optional[Dict[str, Any]] = None,
    parent_feedback: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """保持接口不变"""
    
    # 1. 获取游戏信息
    game = await self.storage.get_game(game_id)
    
    # 2. 构建 episode 内容
    episode_content = _build_game_summary_content(
        game, video_analysis, parent_feedback
    )
    
    # 3. 使用 Graphiti-core 自动提取总结
    result = await self.graphiti.add_episode(
        name=f"游戏总结_{game_id}",
        episode_body=episode_content,
        source_description="游戏实施总结",
        reference_time=datetime.now(),
        source=EpisodeType.game_summary,
        group_id=game["child_id"],
        entity_types={
            "GameSummary": GameSummaryEntityModel,
            "KeyBehavior": KeyBehaviorEntityModel
        },
        custom_extraction_instructions=GAME_SUMMARY_INSTRUCTIONS
    )
    
    # 4. 更新游戏节点（保持原有逻辑）
    summary_data = _extract_summary_data(result.nodes)
    await self.storage.update_game(game_id, {
        "status": "completed",
        "implementation": {
            **game.get("implementation", {}),
            **summary_data
        }
    })
    
    # 5. 返回原有格式
    return await self.storage.get_game(game_id)
```

### 4. generate_assessment() 方法

**当前实现：**
- 手动调用 LLM 生成评估
- 手动创建评估节点

**重构后：**
```python
async def generate_assessment(
    self,
    child_id: str,
    assessment_type: str,
    time_range: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """保持接口不变"""
    
    # 1. 获取历史数据（使用 Graphiti search）
    historical_data = await self._get_historical_data_for_assessment(
        child_id, assessment_type, time_range
    )
    
    # 2. 构建 episode 内容
    episode_content = _build_assessment_content(
        child_id, assessment_type, historical_data
    )
    
    # 3. 使用 Graphiti-core 生成评估
    result = await self.graphiti.add_episode(
        name=f"{assessment_type}_{datetime.now().strftime('%Y%m%d')}",
        episode_body=episode_content,
        source_description=f"{assessment_type} 评估",
        reference_time=datetime.now(),
        source=EpisodeType.assessment,
        group_id=child_id,
        entity_types={
            "Assessment": AssessmentEntityModel
        },
        custom_extraction_instructions=_get_assessment_instructions(assessment_type)
    )
    
    # 4. 保存评估节点（保持原有逻辑）
    assessment_data = _extract_assessment_data(result.nodes)
    assessment_id = await self.storage.create_assessment(assessment_data)
    
    # 5. 返回原有格式
    return await self.storage.get_assessment(assessment_id)
```

### 5. 查询方法（保持不变）

以下方法保持不变，继续使用 `self.storage`：

- `get_child()`
- `save_child()`
- `get_behaviors()`
- `get_objects()`
- `save_interest()`
- `get_latest_interest()`
- `get_interest_history()`
- `save_function()`
- `get_latest_function()`
- `get_function_history()`
- `save_game()`
- `get_game()`
- `get_recent_games()`
- `save_assessment()`
- `get_latest_assessment()`
- `get_assessment_history()`

## 需要新增的辅助函数

### 1. 实体类型定义

```python
# services/Memory/entity_models.py

from pydantic import BaseModel, Field

class BehaviorEntityModel(BaseModel):
    """行为实体模型"""
    event_type: str = Field(..., description="事件类型")
    description: str = Field(..., description="行为描述")
    significance: str = Field(..., description="重要性")
    emotional_state: str = Field(None, description="情绪状态")

class ObjectEntityModel(BaseModel):
    """对象实体模型"""
    name: str = Field(..., description="对象名称")
    category: str = Field(None, description="对象类别")

# ... 其他实体模型
```

### 2. 提取指令

```python
# services/Memory/extraction_instructions.py

BEHAVIOR_EXTRACTION_INSTRUCTIONS = """
重点提取：
1. 孩子的具体行为（Behavior 实体）
2. 涉及的对象（Object 实体）
3. 体现的兴趣点（Interest 实体）
4. 相关的功能维度（Function 实体）

关系类型：
- 孩子 -> 展现 -> 行为
- 行为 -> 涉及对象 -> 对象
- 行为 -> 体现兴趣 -> 兴趣
- 行为 -> 体现功能 -> 功能
"""

GAME_SUMMARY_INSTRUCTIONS = """
从游戏实施数据中提取：
1. 游戏总结（GameSummary 实体）
2. 关键行为（KeyBehavior 实体）
3. 亮点时刻
4. 需要改进的地方
"""

# ... 其他提取指令
```

### 3. 数据转换函数

```python
# services/Memory/converters.py

def _extract_event_type(nodes: List[EntityNode]) -> str:
    """从节点中提取事件类型"""
    for node in nodes:
        if node.entity_type == "Behavior":
            return node.attributes.get("event_type", "other")
    return "other"

def _extract_description(nodes: List[EntityNode]) -> str:
    """从节点中提取描述"""
    for node in nodes:
        if node.entity_type == "Behavior":
            return node.attributes.get("description", "")
    return ""

# ... 其他转换函数
```

## 迁移步骤

1. **第一阶段：准备工作**
   - 创建实体模型定义
   - 创建提取指令
   - 创建数据转换函数

2. **第二阶段：重构核心方法**
   - 重构 `record_behavior()`
   - 重构 `summarize_game()`
   - 重构 `generate_assessment()`

3. **第三阶段：测试验证**
   - 运行现有测试，确保兼容性
   - 对比新旧实现的输出
   - 性能测试

4. **第四阶段：清理**
   - 删除旧的 Prompt 文件
   - 删除旧的 Schema 文件
   - 更新文档

## 兼容性保证

1. **接口签名不变**：所有方法参数和返回值类型保持不变
2. **返回格式不变**：返回的字典结构保持不变
3. **错误处理不变**：异常类型和错误消息保持不变
4. **配置兼容**：`MemoryConfig` 保持不变

## 优势

1. **代码量减少**：删除约 500+ 行重复代码
2. **性能提升**：利用 Graphiti-core 的优化
3. **维护简化**：只需维护实体模型和提取指令
4. **功能增强**：自动获得 Graphiti-core 的新功能（社区检测、时序分析等）

## 风险和缓解

1. **风险**：Graphiti-core 提取结果可能与手动实现不完全一致
   - **缓解**：通过 `custom_extraction_instructions` 精确控制提取逻辑

2. **风险**：性能可能不如预期
   - **缓解**：使用 Graphiti-core 的批量接口 `add_episode_bulk()`

3. **风险**：现有测试可能失败
   - **缓解**：逐步迁移，保留旧实现作为备份

## 时间估算

- 准备工作：2-3 小时
- 核心重构：4-5 小时
- 测试验证：2-3 小时
- 清理文档：1 小时

**总计：9-12 小时**

---

## 实施进度

### ✅ 已完成 (2025-01-30)

1. **目录合并**
   - ✅ 复制 `services/Graphiti/models/` 到 `services/Memory/models/`
   - ✅ 复制 `services/Graphiti/storage/` 到 `services/Memory/storage/`
   - ✅ 复制 `services/Graphiti/utils/` 到 `services/Memory/utils/`
   - ✅ 更新 `services/Memory/service.py` 的导入路径
   - ✅ 更新所有测试文件的导入路径（8个文件）
   - ✅ 更新文档中的导入示例（README.md, SUMMARY.md）
   - ✅ 删除 `services/Graphiti/` 目录
   - ✅ 验证导入正常工作

2. **准备工作**
   - ✅ 创建实体模型定义 `services/Memory/entity_models.py`
     * BehaviorEntityModel, ObjectEntityModel, InterestEntityModel
     * FunctionEntityModel, PersonEntityModel
     * GameSummaryEntityModel, KeyBehaviorEntityModel, AssessmentEntityModel
     * 边模型：ExhibitEdgeModel, InvolveObjectEdgeModel, ShowInterestEdgeModel 等
   
   - ✅ 创建提取指令 `services/Memory/extraction_instructions.py`
     * BEHAVIOR_EXTRACTION_INSTRUCTIONS（行为记录提取）
     * GAME_SUMMARY_EXTRACTION_INSTRUCTIONS（游戏总结提取）
     * ASSESSMENT_EXTRACTION_INSTRUCTIONS（评估生成提取）
     * NEGATIVE_EVENT_EXTRACTION_INSTRUCTIONS（负面事件提取）
   
   - ✅ 创建数据转换函数 `services/Memory/converters.py`
     * extract_event_type(), extract_description(), extract_significance()
     * extract_objects(), extract_interests(), extract_functions()
     * build_ai_analysis(), build_game_summary_content()
     * extract_summary_data(), extract_assessment_data()
     * 节点转换函数：convert_behavior_to_dict() 等

### 🚧 待完成
   - ⏳ 重构 `record_behavior()` 使用 Graphiti-core
   - ⏳ 重构 `summarize_game()` 使用 Graphiti-core
   - ⏳ 重构 `generate_assessment()` 使用 Graphiti-core

3. **测试验证**
   - ⏳ 运行现有测试确保兼容性
   - ⏳ 对比新旧实现输出
   - ⏳ 性能测试

4. **清理**
   - ⏳ 删除旧的 Prompt 文件
   - ⏳ 删除旧的 Schema 文件
   - ⏳ 更新文档
