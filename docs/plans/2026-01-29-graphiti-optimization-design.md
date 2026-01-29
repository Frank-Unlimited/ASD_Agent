# Graphiti 模块优化设计文档

**文档日期**：2026-01-29
**文档版本**：v1.0
**模块定位**：存储观察记忆、提取趋势数据、支持多维度分析

---

## 目录

1. [需求概述](#1-需求概述)
2. [数据模型设计](#2-数据模型设计)
3. [输入数据结构](#3-输入数据结构)
4. [存储结构优化](#4-存储结构优化)
5. [趋势提取算法](#5-趋势提取算法)
6. [跨维度关联分析](#6-跨维度关联分析)
7. [输出接口设计](#7-输出接口设计)
8. [实现计划](#8-实现计划)

---

## 1. 需求概述

### 1.1 模块职责

**Graphiti 模块负责**：
- 存储来自各 Agent 的观察记忆
- 提取多维度趋势数据
- 分析跨维度关联关系
- 输出完整趋势数据供上层模块使用

**不负责**：
- 实时决策（由其他 Agent 负责）
- 报告生成（由报告生成模块负责，但依赖本模块的趋势数据）

### 1.2 依赖关系

```
报告生成 → 趋势分析 → Graphiti 模块
游戏推荐 → 趋势分析 → Graphiti 模块
```

### 1.3 支持的维度

**六大情绪发展里程碑（格林斯潘）**：

| 维度ID | 中文名称 | 描述 |
|--------|---------|------|
| self_regulation | 自我调节 | 情绪和行为的自我控制能力 |
| intimacy | 亲密关系 | 与照护者建立情感联结的能力 |
| two_way_communication | 双向沟通 | 基本的一来一回互动能力 |
| complex_communication | 复杂沟通 | 多轮、复杂的沟通交流 |
| emotional_ideas | 情绪想法 | 表达和理解情绪的能力 |
| logical_thinking | 逻辑思维 | 因果推理和逻辑表达能力 |

**行为观察维度**：

| 维度ID | 中文名称 | 描述 |
|--------|---------|------|
| eye_contact | 眼神接触 | 与他人眼神交流的频率和时长 |
| spontaneous_smile | 主动微笑 | 自发的社交性微笑 |
| verbal_attempt | 语言尝试 | 主动发声或说话的尝试 |
| repetitive_behavior | 刻板行为 | 重复性动作或行为模式 |
| sensory_response | 感官反应 | 对感官刺激的反应模式 |
| social_initiation | 社交发起 | 主动发起社交互动 |

### 1.4 分析能力要求

- **趋势分析**：上升/下降/稳定、变化率、多时间窗口
- **平台期检测**：识别进展停滞的维度
- **异常波动检测**：识别突破或数据问题
- **跨维度关联**：分析维度间的相关性和因果关系

---

## 2. 数据模型设计

### 2.1 节点类型

```
┌─────────────────────────────────────────────────────────────┐
│                      图数据模型                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│    ┌─────────┐                                              │
│    │  Child  │  孩子节点（锚点）                              │
│    └────┬────┘                                              │
│         │ HAS_DIMENSION                                     │
│         ▼                                                   │
│    ┌───────────┐      CORRELATES_WITH      ┌───────────┐   │
│    │ Dimension │◄─────────────────────────►│ Dimension │   │
│    └─────┬─────┘                           └───────────┘   │
│          │ HAS_OBSERVATION                                  │
│          ▼                                                  │
│    ┌─────────────┐       TRIGGERS       ┌───────────┐      │
│    │ Observation │─────────────────────►│ Milestone │      │
│    └─────────────┘                      └───────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Child 节点**：
```python
{
    "node_type": "Child",
    "child_id": "child-001",
    "name": "辰辰",
    "created_at": "2026-01-01T00:00:00Z"
}
```

**Dimension 节点**：
```python
{
    "node_type": "Dimension",
    "dimension_id": "child-001_eye_contact",
    "child_id": "child-001",
    "name": "eye_contact",
    "display_name": "眼神接触",
    "category": "behavior",  # milestone | behavior
    "baseline_value": 2.0,
    "baseline_date": "2026-01-01"
}
```

**Observation 节点**：
```python
{
    "node_type": "Observation",
    "observation_id": "obs-20260129-001",
    "child_id": "child-001",
    "dimension": "eye_contact",
    "value": 8.0,
    "value_type": "score",  # score | count | duration | boolean
    "timestamp": "2026-01-29T14:30:00Z",
    "source": "observation_agent",
    "context": "积木游戏中主动看向家长",
    "confidence": 0.85,
    "session_id": "session-20260129-001"
}
```

**Milestone 节点**：
```python
{
    "node_type": "Milestone",
    "milestone_id": "mile-20260129-001",
    "child_id": "child-001",
    "dimension": "eye_contact",
    "type": "first_time",  # first_time | breakthrough | significant_improvement
    "description": "首次主动发起眼神接触",
    "timestamp": "2026-01-29T14:30:00Z",
    "significance": "high"  # high | medium | low
}
```

### 2.2 边类型

| 边类型 | 起点 | 终点 | 属性 |
|--------|------|------|------|
| HAS_DIMENSION | Child | Dimension | created_at |
| HAS_OBSERVATION | Dimension | Observation | - |
| TRIGGERS | Observation | Milestone | - |
| CORRELATES_WITH | Dimension | Dimension | correlation, lag_days, relationship, updated_at |

---

## 3. 输入数据结构

### 3.1 标准输入 JSON 格式

各 Agent 输入给 Graphiti 模块的数据格式：

```json
{
  "child_id": "child-001",
  "timestamp": "2026-01-29T14:30:00Z",
  "source": "observation_agent",
  "session_id": "session-20260129-001",

  "observations": [
    {
      "dimension": "eye_contact",
      "value": 8,
      "value_type": "score",
      "context": "积木游戏中主动看向家长",
      "duration_seconds": 3,
      "confidence": 0.85
    },
    {
      "dimension": "spontaneous_smile",
      "value": 3,
      "value_type": "count",
      "context": "游戏过程中的微笑次数",
      "confidence": 0.90
    }
  ],

  "milestone": {
    "detected": true,
    "type": "first_time",
    "description": "首次主动发起眼神接触",
    "dimension": "eye_contact"
  },

  "metadata": {
    "game_type": "积木传递",
    "game_duration_minutes": 15,
    "parent_mood": "positive",
    "environment": "home"
  }
}
```

### 3.2 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| child_id | string | 是 | 孩子唯一标识 |
| timestamp | ISO8601 | 是 | 观察时间 |
| source | string | 是 | 数据来源 Agent |
| session_id | string | 否 | 关联的会话ID |
| observations | array | 是 | 观察记录列表 |
| observations[].dimension | string | 是 | 维度标识 |
| observations[].value | number | 是 | 观察值 |
| observations[].value_type | enum | 是 | score/count/duration/boolean |
| observations[].context | string | 否 | 观察上下文描述 |
| observations[].confidence | float | 否 | 置信度 0-1，默认 0.8 |
| milestone | object | 否 | 里程碑信息（如有） |
| metadata | object | 否 | 额外元数据 |

### 3.3 数据来源枚举

```python
class DataSource(Enum):
    OBSERVATION_AGENT = "observation_agent"      # 观察捕获 Agent
    VIDEO_AGENT = "video_agent"                  # 视频分析 Agent
    FEEDBACK_AGENT = "feedback_agent"            # 反馈表 Agent
    ASSESSMENT_AGENT = "assessment_agent"        # 评估 Agent
    PARENT_DIRECT = "parent_direct"              # 家长直接记录
```

---

## 4. 存储结构优化

### 4.1 Episode 内容格式

将结构化 JSON 转换为 Graphiti 可理解的文本，同时保留元数据：

```python
def format_episode_content(observation: dict) -> str:
    """格式化 Episode 内容"""
    return f"""
[观察记录] 孩子 {observation['child_id']} 在 {observation['timestamp']}
维度: {observation['dimension']} ({get_display_name(observation['dimension'])})
数值: {observation['value']} ({observation['value_type']})
场景: {observation.get('context', '无')}
置信度: {observation.get('confidence', 0.8) * 100}%
来源: {observation['source']}
会话: {observation.get('session_id', '无')}
"""

def format_episode_metadata(observation: dict) -> dict:
    """提取 Episode 元数据（用于索引）"""
    return {
        "child_id": observation['child_id'],
        "dimension": observation['dimension'],
        "value": observation['value'],
        "value_type": observation['value_type'],
        "timestamp": observation['timestamp'],
        "source": observation['source'],
        "session_id": observation.get('session_id'),
        "confidence": observation.get('confidence', 0.8),
        "is_milestone": observation.get('milestone', {}).get('detected', False)
    }
```

### 4.2 图结构存储流程

```python
async def store_observation(input_data: dict):
    """存储观察数据到图结构"""
    child_id = input_data['child_id']

    # 1. 确保 Child 节点存在
    await ensure_child_node(child_id)

    for obs in input_data['observations']:
        dimension = obs['dimension']

        # 2. 确保 Dimension 节点存在，并建立 HAS_DIMENSION 边
        await ensure_dimension_node(child_id, dimension)

        # 3. 创建 Observation 节点
        obs_node = await create_observation_node(child_id, obs, input_data)

        # 4. 建立 HAS_OBSERVATION 边
        await create_has_observation_edge(child_id, dimension, obs_node)

    # 5. 处理里程碑
    if input_data.get('milestone', {}).get('detected'):
        milestone_node = await create_milestone_node(child_id, input_data['milestone'])
        # 找到触发里程碑的观察，建立 TRIGGERS 边
        await create_triggers_edge(obs_node, milestone_node)

    # 6. 添加 Episode 到 Graphiti（保持语义搜索能力）
    await add_episode_to_graphiti(child_id, input_data)
```

### 4.3 索引策略

**Neo4j 索引**：

```cypher
// Child 节点索引
CREATE INDEX child_id_index FOR (c:Child) ON (c.child_id);

// Dimension 节点复合索引
CREATE INDEX dimension_index FOR (d:Dimension) ON (d.child_id, d.name);

// Observation 节点索引（按时间查询）
CREATE INDEX observation_time_index FOR (o:Observation) ON (o.child_id, o.dimension, o.timestamp);

// Milestone 节点索引
CREATE INDEX milestone_index FOR (m:Milestone) ON (m.child_id, m.timestamp);

// 里程碑快速查询索引
CREATE INDEX milestone_type_index FOR (m:Milestone) ON (m.child_id, m.type);
```

---

## 5. 趋势提取算法

### 5.1 基础趋势计算

```python
from dataclasses import dataclass
from typing import List, Literal
from scipy import stats
import numpy as np

@dataclass
class TrendInfo:
    direction: Literal["improving", "stable", "declining"]
    rate: float           # 变化率
    confidence: float     # 置信度 0-1
    p_value: float        # 统计显著性

def calculate_trend(data_points: List[dict], min_points: int = 5) -> TrendInfo:
    """
    计算趋势

    Args:
        data_points: 按时间排序的数据点列表，每个包含 timestamp 和 value
        min_points: 最少数据点数量

    Returns:
        TrendInfo: 趋势信息
    """
    if len(data_points) < min_points:
        return TrendInfo(
            direction="stable",
            rate=0.0,
            confidence=0.0,
            p_value=1.0
        )

    # 提取数值序列
    values = [p['value'] for p in data_points]
    x = np.arange(len(values))

    # 线性回归
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, values)

    # 计算变化率
    early_avg = np.mean(values[:len(values)//3])
    recent_avg = np.mean(values[-len(values)//3:])

    if early_avg > 0:
        rate = (recent_avg - early_avg) / early_avg
    else:
        rate = 0.0 if recent_avg == 0 else 1.0

    # 判定趋势方向
    # 使用斜率和统计显著性共同判断
    if p_value < 0.05:  # 统计显著
        if slope > 0.05:
            direction = "improving"
        elif slope < -0.05:
            direction = "declining"
        else:
            direction = "stable"
    else:
        direction = "stable"

    # 置信度 = R² 值
    confidence = r_value ** 2

    return TrendInfo(
        direction=direction,
        rate=rate,
        confidence=confidence,
        p_value=p_value
    )
```

### 5.2 多时间窗口分析

```python
@dataclass
class MultiWindowTrend:
    trend_7d: TrendInfo    # 短期趋势（7天）
    trend_30d: TrendInfo   # 中期趋势（30天）
    trend_90d: TrendInfo   # 长期趋势（90天）

async def analyze_multi_window_trend(
    child_id: str,
    dimension: str
) -> MultiWindowTrend:
    """
    多时间窗口趋势分析

    用途：
    - 7天趋势：实时决策、游戏推荐
    - 30天趋势：策略调整、平台期识别
    - 90天趋势：报告生成、整体评估
    """
    now = datetime.now(timezone.utc)

    # 获取各时间窗口的数据
    data_7d = await get_observations(child_id, dimension, now - timedelta(days=7), now)
    data_30d = await get_observations(child_id, dimension, now - timedelta(days=30), now)
    data_90d = await get_observations(child_id, dimension, now - timedelta(days=90), now)

    return MultiWindowTrend(
        trend_7d=calculate_trend(data_7d, min_points=3),
        trend_30d=calculate_trend(data_30d, min_points=7),
        trend_90d=calculate_trend(data_90d, min_points=15)
    )
```

### 5.3 平台期检测

```python
@dataclass
class PlateauInfo:
    is_plateau: bool
    duration_days: int
    suggestion: str

def detect_plateau(
    data_points: List[dict],
    window_days: int = 14,
    variance_threshold: float = 0.05
) -> PlateauInfo:
    """
    检测平台期

    定义：连续 N 天内数值变化率 < 阈值

    Args:
        data_points: 数据点列表
        window_days: 检测窗口（天）
        variance_threshold: 变化率阈值

    Returns:
        PlateauInfo: 平台期信息
    """
    if len(data_points) < window_days:
        return PlateauInfo(is_plateau=False, duration_days=0, suggestion="数据不足")

    # 取最近 window_days 的数据
    recent_data = data_points[-window_days:]
    values = [p['value'] for p in recent_data]

    # 计算变异系数 (CV = std / mean)
    mean_val = np.mean(values)
    if mean_val == 0:
        cv = 0
    else:
        cv = np.std(values) / mean_val

    is_plateau = cv < variance_threshold

    # 如果是平台期，回溯计算持续天数
    duration_days = 0
    if is_plateau:
        for i in range(len(data_points) - window_days, -1, -1):
            window = data_points[i:i + window_days]
            if len(window) < window_days:
                break
            window_values = [p['value'] for p in window]
            window_cv = np.std(window_values) / np.mean(window_values) if np.mean(window_values) > 0 else 0
            if window_cv < variance_threshold:
                duration_days += 1
            else:
                break
        duration_days += window_days

    suggestion = "考虑调整干预策略，尝试新的游戏类型" if is_plateau else "继续当前计划"

    return PlateauInfo(
        is_plateau=is_plateau,
        duration_days=duration_days,
        suggestion=suggestion
    )
```

### 5.4 异常波动检测

```python
@dataclass
class AnomalyInfo:
    has_anomaly: bool
    anomaly_type: Literal["spike", "drop", "none"]
    anomaly_value: float
    anomaly_date: str
    interpretation: str

def detect_anomaly(
    data_points: List[dict],
    std_threshold: float = 2.0
) -> AnomalyInfo:
    """
    检测异常波动

    定义：数值偏离均值超过 N 个标准差

    Args:
        data_points: 数据点列表
        std_threshold: 标准差阈值

    Returns:
        AnomalyInfo: 异常信息
    """
    if len(data_points) < 5:
        return AnomalyInfo(
            has_anomaly=False,
            anomaly_type="none",
            anomaly_value=0,
            anomaly_date="",
            interpretation="数据不足"
        )

    values = [p['value'] for p in data_points]
    mean_val = np.mean(values)
    std_val = np.std(values)

    if std_val == 0:
        return AnomalyInfo(
            has_anomaly=False,
            anomaly_type="none",
            anomaly_value=0,
            anomaly_date="",
            interpretation="数据无波动"
        )

    # 检查最近的数据点
    recent_point = data_points[-1]
    z_score = (recent_point['value'] - mean_val) / std_val

    if abs(z_score) > std_threshold:
        anomaly_type = "spike" if z_score > 0 else "drop"
        interpretation = "可能是突破性进步，建议关注" if anomaly_type == "spike" else "可能是状态波动或数据问题，建议核实"

        return AnomalyInfo(
            has_anomaly=True,
            anomaly_type=anomaly_type,
            anomaly_value=recent_point['value'],
            anomaly_date=recent_point['timestamp'],
            interpretation=interpretation
        )

    return AnomalyInfo(
        has_anomaly=False,
        anomaly_type="none",
        anomaly_value=0,
        anomaly_date="",
        interpretation="无异常"
    )
```

---

## 6. 跨维度关联分析

### 6.1 相关性计算

```python
from itertools import combinations
from scipy.stats import pearsonr
from scipy.signal import correlate

@dataclass
class Correlation:
    dimension_a: str
    dimension_b: str
    correlation: float      # 相关系数 -1 到 1
    lag_days: int           # 时滞天数（正数表示 A 领先 B）
    relationship: str       # 关系描述
    confidence: float       # 置信度
    p_value: float          # 统计显著性

def calculate_correlation(
    series_a: List[float],
    series_b: List[float],
    timestamps: List[str]
) -> tuple[float, float]:
    """
    计算皮尔逊相关系数

    Returns:
        (correlation, p_value)
    """
    if len(series_a) != len(series_b) or len(series_a) < 5:
        return 0.0, 1.0

    correlation, p_value = pearsonr(series_a, series_b)
    return correlation, p_value

def calculate_lag(
    series_a: List[float],
    series_b: List[float],
    max_lag: int = 14
) -> int:
    """
    计算时滞（A 领先 B 多少天）

    使用互相关分析

    Args:
        series_a: 维度 A 的时间序列
        series_b: 维度 B 的时间序列
        max_lag: 最大时滞天数

    Returns:
        lag_days: 正数表示 A 领先，负数表示 B 领先
    """
    if len(series_a) < max_lag * 2:
        return 0

    # 标准化
    a_norm = (np.array(series_a) - np.mean(series_a)) / (np.std(series_a) + 1e-10)
    b_norm = (np.array(series_b) - np.mean(series_b)) / (np.std(series_b) + 1e-10)

    # 互相关
    cross_corr = correlate(a_norm, b_norm, mode='full')
    lags = np.arange(-len(series_a) + 1, len(series_a))

    # 只看 ±max_lag 范围
    valid_idx = np.where(np.abs(lags) <= max_lag)[0]
    valid_lags = lags[valid_idx]
    valid_corr = cross_corr[valid_idx]

    # 找最大相关对应的 lag
    best_idx = np.argmax(np.abs(valid_corr))
    best_lag = valid_lags[best_idx]

    return int(best_lag)

def infer_relationship(correlation: float, lag_days: int) -> str:
    """
    推断关系类型
    """
    if abs(correlation) < 0.3:
        return "无明显关联"

    direction = "正相关" if correlation > 0 else "负相关"

    if abs(lag_days) <= 2:
        return f"同步{direction}"
    elif lag_days > 2:
        return f"A 可能促进 B（{direction}，领先 {lag_days} 天）"
    else:
        return f"B 可能促进 A（{direction}，领先 {-lag_days} 天）"
```

### 6.2 全维度关联分析

```python
async def analyze_all_correlations(
    child_id: str,
    min_data_points: int = 10,
    significance_threshold: float = 0.3
) -> List[Correlation]:
    """
    分析所有维度之间的关联

    Args:
        child_id: 孩子ID
        min_data_points: 最少数据点
        significance_threshold: 相关性阈值

    Returns:
        显著关联列表
    """
    # 获取所有维度
    dimensions = await get_child_dimensions(child_id)

    # 获取各维度的时间序列数据
    series_data = {}
    for dim in dimensions:
        data = await get_observations(child_id, dim, days=90)
        if len(data) >= min_data_points:
            # 按日聚合（取每日最后一条记录）
            daily_data = aggregate_daily(data)
            series_data[dim] = daily_data

    # 计算两两关联
    correlations = []
    for dim_a, dim_b in combinations(series_data.keys(), 2):
        # 对齐时间序列
        aligned_a, aligned_b, timestamps = align_series(
            series_data[dim_a],
            series_data[dim_b]
        )

        if len(aligned_a) < min_data_points:
            continue

        # 计算相关性
        corr, p_value = calculate_correlation(aligned_a, aligned_b, timestamps)

        # 只保留显著相关
        if abs(corr) >= significance_threshold and p_value < 0.05:
            lag = calculate_lag(aligned_a, aligned_b)
            relationship = infer_relationship(corr, lag)

            correlations.append(Correlation(
                dimension_a=dim_a,
                dimension_b=dim_b,
                correlation=round(corr, 3),
                lag_days=lag,
                relationship=relationship,
                confidence=1 - p_value,
                p_value=round(p_value, 4)
            ))

    # 按相关性强度排序
    correlations.sort(key=lambda x: abs(x.correlation), reverse=True)

    return correlations
```

### 6.3 存储关联结果

```python
async def store_correlations(child_id: str, correlations: List[Correlation]):
    """
    将关联结果存储到图数据库
    """
    for corr in correlations:
        query = """
        MATCH (d1:Dimension {child_id: $child_id, name: $dim_a})
        MATCH (d2:Dimension {child_id: $child_id, name: $dim_b})
        MERGE (d1)-[r:CORRELATES_WITH]->(d2)
        SET r.correlation = $correlation,
            r.lag_days = $lag_days,
            r.relationship = $relationship,
            r.confidence = $confidence,
            r.p_value = $p_value,
            r.updated_at = datetime()
        """

        await execute_query(query, {
            "child_id": child_id,
            "dim_a": corr.dimension_a,
            "dim_b": corr.dimension_b,
            "correlation": corr.correlation,
            "lag_days": corr.lag_days,
            "relationship": corr.relationship,
            "confidence": corr.confidence,
            "p_value": corr.p_value
        })
```

---

## 7. 输出接口设计

### 7.1 数据结构定义

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Literal
from datetime import datetime

@dataclass
class DataPoint:
    """单个数据点"""
    timestamp: str
    value: float
    source: str
    confidence: float
    context: Optional[str] = None

@dataclass
class TrendInfo:
    """趋势信息"""
    direction: Literal["improving", "stable", "declining"]
    rate: float                 # 变化率
    confidence: float           # 置信度 0-1
    p_value: float              # 统计显著性

@dataclass
class PlateauInfo:
    """平台期信息"""
    is_plateau: bool
    duration_days: int
    suggestion: str

@dataclass
class AnomalyInfo:
    """异常信息"""
    has_anomaly: bool
    anomaly_type: Literal["spike", "drop", "none"]
    anomaly_value: float
    anomaly_date: str
    interpretation: str

@dataclass
class DimensionTrend:
    """单维度完整趋势数据"""
    dimension: str                      # 维度ID
    display_name: str                   # 显示名称（中文）
    category: str                       # milestone | behavior

    # 数值信息
    current_value: float                # 当前值（最近7天均值）
    baseline_value: float               # 基线值（首次评估）
    total_improvement: float            # 总体提升百分比

    # 多时间窗口趋势
    trend_7d: TrendInfo                 # 短期趋势
    trend_30d: TrendInfo                # 中期趋势
    trend_90d: TrendInfo                # 长期趋势

    # 状态标记
    plateau: PlateauInfo                # 平台期信息
    anomaly: AnomalyInfo                # 异常信息

    # 数据序列（供可视化）
    data_points: List[DataPoint]        # 时间序列数据
    data_point_count: int               # 数据点总数

@dataclass
class Milestone:
    """里程碑"""
    milestone_id: str
    dimension: str
    type: str                           # first_time | breakthrough | significant_improvement
    description: str
    timestamp: str
    significance: str                   # high | medium | low

@dataclass
class Correlation:
    """维度关联"""
    dimension_a: str
    dimension_b: str
    correlation: float                  # -1 到 1
    lag_days: int                       # 时滞天数
    relationship: str                   # 关系描述
    confidence: float

@dataclass
class TrendAnalysisResult:
    """完整趋势分析输出"""
    child_id: str
    child_name: str
    analysis_time: str

    # 各维度趋势
    dimensions: Dict[str, DimensionTrend]

    # 里程碑
    recent_milestones: List[Milestone]
    total_milestones: int

    # 跨维度关联
    correlations: List[Correlation]

    # 综合指标（供上层决策）
    summary: TrendSummary

@dataclass
class TrendSummary:
    """趋势摘要"""
    attention_dimensions: List[str]     # 需要关注的维度（下降或平台期）
    improving_dimensions: List[str]     # 进展良好的维度
    stable_dimensions: List[str]        # 稳定的维度
    overall_status: str                 # excellent | good | attention_needed
    recommendation: str                 # 综合建议
```

### 7.2 主要接口

```python
class GraphitiModule:
    """Graphiti 模块主接口"""

    async def save_observations(self, input_data: dict) -> None:
        """
        保存观察数据

        Args:
            input_data: 标准输入 JSON（见第3节）
        """
        pass

    async def get_full_trend(self, child_id: str) -> TrendAnalysisResult:
        """
        获取完整趋势分析

        Args:
            child_id: 孩子ID

        Returns:
            TrendAnalysisResult: 包含所有维度趋势、里程碑、关联的完整结果

        用途：报告生成、全面评估
        """
        pass

    async def get_dimension_trend(
        self,
        child_id: str,
        dimension: str,
        include_data_points: bool = True
    ) -> DimensionTrend:
        """
        获取单维度趋势

        Args:
            child_id: 孩子ID
            dimension: 维度名称
            include_data_points: 是否包含原始数据点

        Returns:
            DimensionTrend: 该维度的完整趋势数据

        用途：单维度深入分析、可视化
        """
        pass

    async def get_correlations(
        self,
        child_id: str,
        min_correlation: float = 0.3
    ) -> List[Correlation]:
        """
        获取维度关联

        Args:
            child_id: 孩子ID
            min_correlation: 最小相关系数阈值

        Returns:
            List[Correlation]: 关联列表，按相关性强度排序

        用途：发现维度间规律、因果推断
        """
        pass

    async def get_milestones(
        self,
        child_id: str,
        days: Optional[int] = None,
        dimension: Optional[str] = None
    ) -> List[Milestone]:
        """
        获取里程碑

        Args:
            child_id: 孩子ID
            days: 最近多少天（None 表示全部）
            dimension: 指定维度（None 表示全部）

        Returns:
            List[Milestone]: 里程碑列表，按时间倒序

        用途：成长历程展示、报告生成
        """
        pass

    async def get_quick_summary(self, child_id: str) -> TrendSummary:
        """
        获取快速摘要

        Args:
            child_id: 孩子ID

        Returns:
            TrendSummary: 简要摘要，包含需关注维度和综合建议

        用途：游戏推荐、快速决策
        """
        pass

    async def refresh_correlations(self, child_id: str) -> None:
        """
        刷新关联分析

        定期调用，更新维度间的关联关系

        Args:
            child_id: 孩子ID
        """
        pass
```

### 7.3 输出示例

```json
{
  "child_id": "child-001",
  "child_name": "辰辰",
  "analysis_time": "2026-01-29T15:00:00Z",

  "dimensions": {
    "eye_contact": {
      "dimension": "eye_contact",
      "display_name": "眼神接触",
      "category": "behavior",
      "current_value": 7.5,
      "baseline_value": 2.0,
      "total_improvement": 2.75,

      "trend_7d": {
        "direction": "improving",
        "rate": 0.15,
        "confidence": 0.82,
        "p_value": 0.03
      },
      "trend_30d": {
        "direction": "improving",
        "rate": 0.45,
        "confidence": 0.88,
        "p_value": 0.01
      },
      "trend_90d": {
        "direction": "improving",
        "rate": 1.25,
        "confidence": 0.91,
        "p_value": 0.005
      },

      "plateau": {
        "is_plateau": false,
        "duration_days": 0,
        "suggestion": "继续当前计划"
      },
      "anomaly": {
        "has_anomaly": false,
        "anomaly_type": "none",
        "anomaly_value": 0,
        "anomaly_date": "",
        "interpretation": "无异常"
      },

      "data_points": [
        {"timestamp": "2026-01-22", "value": 6.0, "source": "observation_agent", "confidence": 0.85},
        {"timestamp": "2026-01-25", "value": 7.0, "source": "video_agent", "confidence": 0.78},
        {"timestamp": "2026-01-29", "value": 8.0, "source": "observation_agent", "confidence": 0.90}
      ],
      "data_point_count": 45
    }
  },

  "recent_milestones": [
    {
      "milestone_id": "mile-20260129-001",
      "dimension": "eye_contact",
      "type": "first_time",
      "description": "首次主动发起眼神接触",
      "timestamp": "2026-01-29T14:30:00Z",
      "significance": "high"
    }
  ],
  "total_milestones": 8,

  "correlations": [
    {
      "dimension_a": "eye_contact",
      "dimension_b": "two_way_communication",
      "correlation": 0.72,
      "lag_days": 5,
      "relationship": "eye_contact 可能促进 two_way_communication（正相关，领先 5 天）",
      "confidence": 0.95
    }
  ],

  "summary": {
    "attention_dimensions": ["repetitive_behavior"],
    "improving_dimensions": ["eye_contact", "spontaneous_smile", "two_way_communication"],
    "stable_dimensions": ["self_regulation"],
    "overall_status": "good",
    "recommendation": "眼神接触和双向沟通进展良好，建议继续当前游戏类型；刻板行为需要关注，可尝试引入感官调节活动"
  }
}
```

---

## 8. 实现计划

### 8.1 模块结构

```
services/Graphiti/
├── __init__.py
├── config.py                 # 配置
├── service.py                # 核心服务（现有，需重构）
├── adapters.py               # 适配器（现有，需更新）
├── api_interface.py          # API 接口（现有，需重构）
│
├── models/                   # 新增：数据模型
│   ├── __init__.py
│   ├── nodes.py              # 节点模型
│   ├── edges.py              # 边模型
│   └── output.py             # 输出模型
│
├── storage/                  # 新增：存储层
│   ├── __init__.py
│   ├── graph_storage.py      # 图存储操作
│   └── index_manager.py      # 索引管理
│
├── analysis/                 # 新增：分析层
│   ├── __init__.py
│   ├── trend_analyzer.py     # 趋势分析
│   ├── plateau_detector.py   # 平台期检测
│   ├── anomaly_detector.py   # 异常检测
│   └── correlation_analyzer.py  # 关联分析
│
└── utils/                    # 新增：工具函数
    ├── __init__.py
    ├── time_series.py        # 时间序列处理
    └── statistics.py         # 统计函数
```

### 8.2 实现优先级

| 优先级 | 模块 | 内容 | 依赖 |
|--------|------|------|------|
| P0 | models/ | 数据模型定义 | 无 |
| P0 | storage/ | 图存储和索引 | models |
| P1 | analysis/trend_analyzer.py | 基础趋势分析 | storage |
| P1 | analysis/plateau_detector.py | 平台期检测 | trend_analyzer |
| P1 | analysis/anomaly_detector.py | 异常检测 | trend_analyzer |
| P2 | analysis/correlation_analyzer.py | 关联分析 | storage |
| P2 | api_interface.py 重构 | 新接口实现 | 全部 analysis |
| P3 | adapters.py 更新 | 适配新接口 | api_interface |

### 8.3 测试计划

| 测试类型 | 覆盖范围 |
|---------|---------|
| 单元测试 | 趋势计算、平台期检测、关联计算等核心算法 |
| 集成测试 | 存储 → 分析 → 输出的完整流程 |
| 性能测试 | 大数据量下的查询和分析性能 |
| 回归测试 | 确保现有接口兼容 |

---

## 附录

### A. 维度映射表

```python
DIMENSION_CONFIG = {
    # 六大情绪里程碑
    "self_regulation": {
        "display_name": "自我调节",
        "category": "milestone",
        "description": "情绪和行为的自我控制能力",
        "value_type": "score",
        "max_value": 10
    },
    "intimacy": {
        "display_name": "亲密关系",
        "category": "milestone",
        "description": "与照护者建立情感联结的能力",
        "value_type": "score",
        "max_value": 10
    },
    "two_way_communication": {
        "display_name": "双向沟通",
        "category": "milestone",
        "description": "基本的一来一回互动能力",
        "value_type": "score",
        "max_value": 10
    },
    "complex_communication": {
        "display_name": "复杂沟通",
        "category": "milestone",
        "description": "多轮、复杂的沟通交流",
        "value_type": "score",
        "max_value": 10
    },
    "emotional_ideas": {
        "display_name": "情绪想法",
        "category": "milestone",
        "description": "表达和理解情绪的能力",
        "value_type": "score",
        "max_value": 10
    },
    "logical_thinking": {
        "display_name": "逻辑思维",
        "category": "milestone",
        "description": "因果推理和逻辑表达能力",
        "value_type": "score",
        "max_value": 10
    },

    # 行为观察维度
    "eye_contact": {
        "display_name": "眼神接触",
        "category": "behavior",
        "description": "与他人眼神交流的频率和时长",
        "value_type": "score",
        "max_value": 10
    },
    "spontaneous_smile": {
        "display_name": "主动微笑",
        "category": "behavior",
        "description": "自发的社交性微笑",
        "value_type": "count",
        "max_value": None
    },
    "verbal_attempt": {
        "display_name": "语言尝试",
        "category": "behavior",
        "description": "主动发声或说话的尝试",
        "value_type": "count",
        "max_value": None
    },
    "repetitive_behavior": {
        "display_name": "刻板行为",
        "category": "behavior",
        "description": "重复性动作或行为模式",
        "value_type": "score",
        "max_value": 10,
        "inverse": True  # 数值越低越好
    },
    "sensory_response": {
        "display_name": "感官反应",
        "category": "behavior",
        "description": "对感官刺激的反应模式",
        "value_type": "score",
        "max_value": 10
    },
    "social_initiation": {
        "display_name": "社交发起",
        "category": "behavior",
        "description": "主动发起社交互动",
        "value_type": "count",
        "max_value": None
    }
}
```

### B. 里程碑类型

```python
MILESTONE_TYPES = {
    "first_time": {
        "display_name": "首次出现",
        "description": "该行为/能力首次被观察到",
        "significance": "high"
    },
    "breakthrough": {
        "display_name": "突破性进步",
        "description": "显著超越以往水平的表现",
        "significance": "high"
    },
    "significant_improvement": {
        "display_name": "显著改善",
        "description": "持续稳定的明显进步",
        "significance": "medium"
    },
    "consistency": {
        "display_name": "稳定表现",
        "description": "某项能力达到稳定可重复的水平",
        "significance": "medium"
    }
}
```

---

**文档结束**
