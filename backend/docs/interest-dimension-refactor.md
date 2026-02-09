# 兴趣维度重构 - 实施文档

## 概述

本次重构简化了兴趣维度的设计，采用图数据库的优势，通过边来表达行为与兴趣维度的关联关系。

## 核心设计理念

### 1. **InterestDimension 是轻量级聚合节点**
- 只存储维度标识和计算结果
- 不维护行为列表（通过图查询获取）
- 不存储时序信息（时序在边上）

### 2. **通过 Graphiti 的边表达关联**
- `Behavior --[show_interest]--> InterestDimension`
- 边的属性：weight（权重）、reasoning（推理依据）、manifestation（具体表现）

### 3. **探索度动态计算**
- 基于边的数量和权重
- 考虑行为多样性（事件类型）
- 通过 Cypher 查询实时计算

## 已完成的实施步骤

### 步骤 1: 更新 entity_models.py

**文件**: `services/Memory/entity_models.py`

**修改内容**:
```python
class ShowInterestEdgeModel(BaseModel):
    """体现兴趣边模型 - 行为体现兴趣"""
    
    weight: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="关联权重：这个行为对该兴趣维度的贡献度（0-1）"
    )
    
    reasoning: Optional[str] = Field(
        None,
        description="推理依据：为什么这个行为体现了该兴趣维度"
    )
    
    manifestation: Optional[str] = Field(
        None,
        description="具体表现：行为如何体现兴趣"
    )
```

**变更说明**:
- 移除了 `intensity` 和 `duration_seconds` 字段
- 添加了 `weight`（关联权重）字段
- 添加了 `reasoning`（推理依据）字段
- 添加了 `manifestation`（具体表现）字段

### 步骤 2: 更新 extraction_instructions.py

**文件**: `services/Memory/extraction_instructions.py`

**修改内容**:
- 在 `BEHAVIOR_EXTRACTION_INSTRUCTIONS` 中添加了兴趣维度推理指令
- 明确了 8 个兴趣维度的定义和示例
- 提供了权重分配规则和推理示例

**关键指令**:
```
### 4. InterestDimension（兴趣维度）- 通过推理建立关联

对于每个行为，分析它体现了哪些兴趣维度，并为每个关联创建边：

- weight: 关联权重（0-1）
  - 1.0: 强关联，这是行为的主要吸引点
  - 0.7-0.9: 中等关联，明显涉及该维度
  - 0.4-0.6: 弱关联，部分涉及该维度
  - <0.4: 不建立边

推理规则：
1. 一个行为可以关联多个兴趣维度
2. 根据行为的核心吸引点判断主要维度（weight高）
3. 根据行为的附带特征判断次要维度（weight低）
4. 考虑涉及的对象、活动类型、孩子的反应
```

**示例**:
- "玩彩色积木" → visual(0.8) + construction(0.6) + order(0.4)
- "听音乐摇摆" → auditory(0.9) + motor(0.6)
- "玩水" → tactile(0.8) + visual(0.4)

### 步骤 3: 添加探索度计算函数

**文件**: `services/Memory/service.py`

**新增函数**:

#### 3.1 `calculate_exploration_score(child_id, dimension)`
计算单个兴趣维度的探索度

**计算公式**:
```python
base_score = min(100, total_weight * 10)
diversity_factor = 1 + (event_types_count - 1) * 0.1
exploration_score = min(100, base_score * diversity_factor)
```

**返回数据**:
```python
{
    "dimension": str,
    "exploration_score": float,  # 0-100
    "behavior_count": int,
    "total_weight": float,
    "event_types": List[str],
    "first_observed": str,
    "last_observed": str,
    "time_span_days": int
}
```

#### 3.2 `calculate_all_exploration_scores(child_id)`
计算所有兴趣维度的探索度，按分数降序排序

#### 3.3 `get_behaviors_for_interest_dimension(child_id, dimension, limit)`
获取某个兴趣维度的所有关联行为（用于评估Agent分析）

**返回数据**:
```python
[{
    "behavior": str,
    "event_type": str,
    "emotion": str,
    "duration": int,
    "significance": str,
    "weight": float,
    "reasoning": str,
    "manifestation": str,
    "observed_at": str
}]
```

#### 3.4 `get_multi_interest_behaviors(child_id, min_dimensions)`
查找涉及多个兴趣维度的行为（交叉兴趣）

## 图谱结构示例

```
Child(小明)
  |
  |--[exhibit]-->Behavior1("玩彩色积木")
  |                |
  |                |--[show_interest(weight=0.8, reasoning="彩色是主要吸引点")]-->InterestDimension(visual)
  |                |--[show_interest(weight=0.6, reasoning="涉及搭建")]-->InterestDimension(construction)
  |                |--[involve_object]-->Object("积木")
  |
  |--[exhibit]-->Behavior2("看旋转齿轮")
  |                |
  |                |--[show_interest(weight=0.9)]-->InterestDimension(visual)
  |
  |--[exhibit]-->Behavior3("玩水")
                   |
                   |--[show_interest(weight=0.8)]-->InterestDimension(tactile)
                   |--[show_interest(weight=0.4)]-->InterestDimension(visual)
```

## 工作流程

### 1. 行为记录阶段
```
家长输入："小明今天玩彩色积木，很开心，玩了10分钟"
    ↓
LLM 提取实体：
  - Behavior: "玩彩色积木"
  - Object: "积木"
    ↓
Graphiti 创建节点和边：
  - 创建 Behavior 节点
  - 创建 Child --[exhibit]--> Behavior 边
  - 创建 Behavior --[involve_object]--> Object 边
```

### 2. 兴趣推理阶段
```
LLM 分析："玩彩色积木" 关联哪些兴趣维度？
    ↓
推理结果：
  - visual (weight=0.8): 彩色刺激是主要吸引点
  - construction (weight=0.6): 涉及搭建行为
    ↓
Graphiti 创建边：
  - Behavior --[show_interest(weight=0.8)]--> InterestDimension(visual)
  - Behavior --[show_interest(weight=0.6)]--> InterestDimension(construction)
```

### 3. 探索度计算阶段
```
触发时机：
  - 新增行为记录后
  - 评估Agent运行前
  - 游戏推荐前
    ↓
Cypher 查询：
  MATCH (c:Child)-[:exhibit]->(b:Behavior)
        -[r:show_interest]->(i:InterestDimension {dimension: 'visual'})
  RETURN sum(r.weight), count(b), ...
    ↓
计算 exploration_score = 85.5
    ↓
更新 InterestDimension 节点的 exploration_score 属性
```

### 4. 强度评估阶段（评估Agent）
```
评估Agent 查询：
  - 获取所有关联的 Behavior 节点
  - 分析行为的质量（持续时间、主动性、情绪等）
  - 综合判断 intensity
    ↓
更新 InterestDimension：
  - intensity = 8.5
  - intensity_reasoning = "小明对视觉刺激反应积极..."
  - standard_interests = ["visual_colorful_blocks", ...]
```

## 测试

**测试文件**: `tests/test_interest_exploration.py`

**测试用例**:
1. `test_calculate_exploration_score`: 测试单个维度探索度计算
2. `test_calculate_all_exploration_scores`: 测试所有维度探索度计算
3. `test_get_behaviors_for_interest_dimension`: 测试获取维度关联行为
4. `test_get_multi_interest_behaviors`: 测试查找多维度兴趣行为

**运行测试**:
```bash
pytest tests/test_interest_exploration.py -v -s
```

## 优势总结

### ✅ 数据存储在图谱中
- InterestDimension 只是聚合节点，不维护行为列表
- 通过边来表达关联，利用图数据库的优势

### ✅ 探索度动态计算
- 基于边的权重和数量
- 考虑行为多样性
- 可以灵活调整计算公式

### ✅ 职责清晰
- 探索度：客观统计（图查询）
- 强度：主观评估（Agent判断）

### ✅ 时序信息在边上
- Graphiti 自动为边添加时间戳
- 不需要在 InterestDimension 中维护时序字段
- 通过查询边的时间戳即可获取时序信息

### ✅ 验证状态在评估中
- 不需要在 InterestDimension 中存储验证状态
- 评估Agent 通过分析行为质量来判断兴趣是否真实

## 后续步骤

### 步骤 4: 更新评估Agent
- 读取关联行为
- 计算强度（intensity）
- 生成推理依据（intensity_reasoning）
- 提取标准兴趣点（standard_interests）

### 步骤 5: 更新游戏推荐
- 基于 exploration_score 和 intensity 推荐
- 优先使用探索度高且强度高的兴趣维度
- 参考 standard_interests 选择游戏材料

### 步骤 6: 更新数据可视化
- 兴趣热力图：显示 intensity
- 探索度图表：显示 exploration_score
- 行为关联图：显示行为与兴趣维度的连接

## 注意事项

1. **向后兼容**: 保持现有 API 接口不变，内部实现改为图查询
2. **性能优化**: 探索度计算结果可以缓存，避免重复查询
3. **数据迁移**: 需要将现有的兴趣数据迁移到新的图结构
4. **LLM 推理质量**: 需要监控 LLM 推理的权重分配是否合理

## 相关文件

- `services/Memory/entity_models.py`: 实体和边模型定义
- `services/Memory/extraction_instructions.py`: LLM 提取指令
- `services/Memory/service.py`: Memory 服务实现
- `tests/test_interest_exploration.py`: 测试用例
- `docs/interest-dimension-refactor.md`: 本文档
