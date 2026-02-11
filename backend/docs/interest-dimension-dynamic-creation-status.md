# 兴趣维度动态创建 - 实现状态

## 日期
2026-02-04

## 目标
让 LLM 动态创建 InterestDimension 节点，而不是预先创建固定的 8 个节点。

## 当前状态：✅ 基本完成（边类型问题待优化）

### 已完成 ✅

1. **移除固定节点初始化**
   - 文件：`services/Memory/storage/graph_storage.py`
   - 修改：`initialize_fixed_nodes()` 现在只创建约束和索引，不创建固定的 InterestDimension 节点

2. **更新实体模型**
   - 文件：`services/Memory/entity_models.py`
   - 新增：`InterestDimensionEntityModel`
   - 字段：`dimension_id`, `display_name`, `description`
   - 注意：使用 `dimension_id` 而不是 `name`（避免与 Graphiti 的保护字段冲突）

3. **更新提取指令**
   - 文件：`services/Memory/extraction_instructions.py`
   - 新增：InterestDimension 实体提取说明
   - 新增：shows_interest 边的推理规则
   - 示例：如何从行为推理出兴趣维度

4. **更新 Cypher 查询**
   - 文件：`services/Memory/service.py`
   - 修改：所有查询使用 `dimension_id` 而不是 `name`

5. **修复编码问题**
   - 移除特殊字符（✓, ✗, ❌）避免 Windows GBK 编码错误

6. **边类型名称改为英文**
   - `'体现兴趣'` → `'shows_interest'`
   - `'展现'` → `'exhibits'`
   - `'涉及对象'` → `'involves_object'`
   - `'涉及人物'` → `'involves_person'`

7. **测试验证通过** ✅
   - 文件：`tests/test_llm_interest_inference.py`
   - 测试输入：`"小明今天玩彩色积木，搭了一个高塔，很开心"`
   - 测试结果：
     - ✅ LLM 成功创建了 3 个 InterestDimension 实体：`construction`、`order`、`visual`
     - ✅ LLM 正确推理了行为与兴趣维度的关联
     - ✅ 边的 `fact` 属性包含了关系信息：
       - `'搭高塔体现order兴趣'`
       - `'玩彩色积木体现construction兴趣'`
       - `'玩彩色积木体现visual兴趣'`

### 已知问题 ⚠️

1. **Graphiti 边类型问题**
   - 现象：Graphiti 创建的是 `RELATES_TO` 边，而不是 `SHOWS_INTEREST` 边
   - 原因：`edge_types` 和 `edge_type_map` 参数只是提示 LLM，但实际创建边时使用默认逻辑
   - 影响：边没有 `weight`, `reasoning`, `manifestation` 属性，只有 `fact` 属性
   - 观察：边的 `name` 属性是 `'SHOWS_INTEREST'`，但 `type(r)` 是 `RELATES_TO`
   - 临时方案：从 `fact` 属性中提取关系信息（已在测试中实现）

### 优化方向 📋

1. **深入研究 Graphiti 边类型机制**（可选）
   - 查看 Graphiti 源码中 `edge_types` 的实际用法
   - 查看 `external/graphiti/graphiti_core/utils/maintenance/edge_operations.py`
   - 可能需要修改 Graphiti 源码或使用不同的 API

2. **应用层解析方案**（推荐）
   - 接受 `RELATES_TO` 边
   - 从 `fact` 属性中提取权重和推理信息
   - 在查询时解析边的语义

## 测试文件

- `tests/test_llm_interest_inference.py`：测试 LLM 推理兴趣维度功能
  - 状态：✅ 通过
  - 功能：验证 LLM 能否从行为描述中推理出兴趣维度

## 相关文件

- `services/Memory/storage/graph_storage.py` - 存储层
- `services/Memory/entity_models.py` - 实体模型
- `services/Memory/service.py` - 服务层
- `services/Memory/extraction_instructions.py` - 提取指令
- `services/Memory/storage/index_manager.py` - 索引管理
- `tests/test_llm_interest_inference.py` - 测试文件

## 结论

✅ **核心功能已实现**：LLM 能够动态创建 InterestDimension 节点，并正确推理行为与兴趣维度的关联。

⚠️ **边类型问题**：Graphiti 使用默认的 `RELATES_TO` 边，而不是自定义的 `SHOWS_INTEREST` 边。这不影响核心功能，但需要在应用层解析 `fact` 属性。

📋 **建议**：先使用当前方案（从 `fact` 解析），后续如有需要再深入研究 Graphiti 的边类型机制。
