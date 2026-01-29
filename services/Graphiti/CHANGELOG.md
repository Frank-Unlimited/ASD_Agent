# Graphiti 模块重构日志

## v2.0.0 - 2026-01-29

### 🎉 完全重构

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
- 统一的输入数据结构（见设计文档第3节）
- 支持 12 个标准维度（6个里程碑 + 6个行为）
- 支持多种值类型（score/count/duration/boolean）

### 📦 新增模块

```
services/Graphiti/
├── models/              # 数据模型
│   ├── nodes.py         # 节点模型
│   ├── edges.py         # 边类型
│   ├── output.py        # 输出数据结构
│   └── dimensions.py    # 维度配置
├── storage/             # 存储层
│   ├── graph_storage.py # 图存储操作
│   └── index_manager.py # 索引管理
├── analysis/            # 分析层
│   ├── trend_analyzer.py      # 趋势分析
│   ├── plateau_detector.py    # 平台期检测
│   ├── anomaly_detector.py    # 异常检测
│   └── correlation_analyzer.py # 关联分析
└── utils/               # 工具函数
    ├── time_series.py   # 时间序列处理
    └── statistics.py    # 统计函数
```

### 🔄 API 变更

#### 新增接口
- `POST /api/infrastructure/graphiti/save_observations` - 保存观察数据（新标准格式）
- `POST /api/infrastructure/graphiti/get_full_trend` - 获取完整趋势分析
- `POST /api/infrastructure/graphiti/get_dimension_trend` - 获取单维度趋势
- `POST /api/infrastructure/graphiti/get_quick_summary` - 获取快速摘要
- `POST /api/infrastructure/graphiti/get_milestones` - 获取里程碑
- `POST /api/infrastructure/graphiti/get_correlations` - 获取维度关联
- `POST /api/infrastructure/graphiti/refresh_correlations` - 刷新关联分析
- `POST /api/infrastructure/graphiti/clear_child_data` - 清空孩子数据

#### 移除接口
- `POST /api/infrastructure/graphiti/save_memories` - 已被 save_observations 替代
- `POST /api/infrastructure/graphiti/get_recent_memories` - 功能合并到新接口
- `POST /api/infrastructure/graphiti/analyze_trends` - 功能合并到 get_dimension_trend
- `POST /api/infrastructure/graphiti/detect_milestones` - 功能合并到 get_milestones
- `POST /api/infrastructure/graphiti/detect_plateau` - 功能合并到 get_dimension_trend
- `POST /api/infrastructure/graphiti/build_context` - 功能合并到 get_quick_summary
- `POST /api/infrastructure/graphiti/clear_memories` - 已被 clear_child_data 替代

### 📚 依赖更新

新增依赖：
- `scipy>=1.11.0` - 统计分析
- `numpy>=1.24.0` - 数值计算

### 🔧 配置更新

新增配置项（`services/Graphiti/config.py`）：
- `trend_min_points_7d` - 7天趋势最少数据点（默认3）
- `trend_min_points_30d` - 30天趋势最少数据点（默认7）
- `trend_min_points_90d` - 90天趋势最少数据点（默认15）
- `plateau_window_days` - 平台期检测窗口（默认14天）
- `plateau_variance_threshold` - 变化率阈值（默认0.05）
- `anomaly_std_threshold` - 异常检测标准差阈值（默认2.0）
- `correlation_min_points` - 关联分析最少数据点（默认10）
- `correlation_threshold` - 相关性阈值（默认0.3）
- `correlation_max_lag` - 最大时滞天数（默认14）

### 📖 文档更新

- 更新 `frontend_test/post_gets_use.md` - API 使用文档
- 更新 `services/Graphiti/README.md` - 模块说明
- 新增 `services/Graphiti/CHANGELOG.md` - 变更日志

### ⚠️ 破坏性变更

1. **数据格式变更**：输入数据格式完全改变，需要更新调用方代码
2. **API 接口变更**：旧接口已移除，需要迁移到新接口
3. **存储结构变更**：不再使用 Graphiti Episode，数据存储在自定义图结构中

### 🚀 迁移指南

#### 从旧接口迁移到新接口

**旧代码**：
```python
await service.save_memories(child_id, [
    {
        "timestamp": "2026-01-28T14:30:00",
        "type": "observation",
        "content": "孩子主动眼神接触3次"
    }
])
```

**新代码**：
```python
await service.save_observations({
    "child_id": "child-001",
    "timestamp": "2026-01-29T14:30:00Z",
    "source": "observation_agent",
    "observations": [
        {
            "dimension": "eye_contact",
            "value": 8,
            "value_type": "score",
            "context": "积木游戏中主动看向家长",
            "confidence": 0.85
        }
    ]
})
```

### 🐛 已知问题

无

### 📝 待办事项

- [ ] 添加单元测试
- [ ] 添加集成测试
- [ ] 性能优化（大数据量场景）
- [ ] 添加数据导出功能
- [ ] 支持自定义维度配置

---

## v1.0.0 - 2026-01-26

### 初始版本
- 基于 graphiti-core 的 Episode 模式
- 基础记忆存储和检索功能
