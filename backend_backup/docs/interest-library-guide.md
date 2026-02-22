# 兴趣点库使用指南

## 概述

兴趣点库是 ASD 儿童地板时光干预系统的核心组件之一，提供了标准化的兴趣点分类和管理功能。

## 数据结构

### 1. 兴趣类别 (InterestCategory)

```python
class InterestCategory(str, Enum):
    VISUAL = "visual"          # 视觉类
    AUDITORY = "auditory"      # 听觉类
    TACTILE = "tactile"        # 触觉类
    MOTOR = "motor"            # 运动类
    CONSTRUCTION = "construction"  # 建构类
    ORDER = "order"            # 秩序类
    COGNITIVE = "cognitive"    # 认知类
    SOCIAL = "social"          # 社交类
    OTHER = "other"            # 其他
```

### 2. 标准兴趣点 (StandardInterest)

```python
class StandardInterest(BaseModel):
    interest_key: str          # 唯一标识
    name: str                  # 显示名称
    category: InterestCategory # 类别
    description: str           # 描述
    related_materials: List[str]  # 相关材料
    keywords: List[str]        # 关键词（用于匹配）
```

### 3. 兴趣点 (InterestPoint)

扩展后的 InterestPoint 包含：

```python
class InterestPoint(BaseModel):
    interest_id: str
    name: str
    category: Optional[InterestCategory]  # 新增：类别
    intensity: float  # 0-10
    discovered_date: Optional[datetime]
    description: Optional[str]
    tags: List[str]
    standard_interest_key: Optional[str]  # 新增：关联标准库
```

### 4. 热力图数据 (InterestHeatmapData)

扩展后的热力图数据包含：

```python
class InterestHeatmapData(BaseModel):
    interest_name: str
    category: Optional[str]  # 新增：类别
    intensity_over_time: List[Dict[str, Any]]
    current_intensity: float
    trend: TrendDirection
    mention_count: int
    first_mentioned: str
    last_mentioned: str
```

## 标准兴趣点库统计

总计：**49 个标准兴趣点**

| 类别 | 数量 | 示例 |
|------|------|------|
| 视觉类 (visual) | 7 | 彩色积木、旋转物体、光影玩具、绘本 |
| 听觉类 (auditory) | 7 | 儿歌、乐器声、自然音、机械声 |
| 触觉类 (tactile) | 7 | 黏土、沙子、水、软胶玩具 |
| 运动类 (motor) | 7 | 滑梯、秋千、蹦床、骑车 |
| 建构类 (construction) | 7 | 乐高、磁力片、积木、拆装玩具 |
| 秩序类 (order) | 5 | 排序玩具、分类盒、叠叠乐 |
| 认知类 (cognitive) | 6 | 数字卡片、字母书、地图、车标图 |
| 社交类 (social) | 3 | 回合制游戏、角色扮演、互动绘本 |

## 使用方法

### 1. 导入

```python
from src.models import (
    InterestCategory,
    StandardInterest,
    STANDARD_INTERESTS,
    get_interest_by_key,
    get_interests_by_category,
    search_interests,
    get_all_categories
)
```

### 2. 按类别查询

```python
# 获取所有视觉类兴趣点
visual_interests = get_interests_by_category(InterestCategory.VISUAL)

for interest in visual_interests:
    print(f"{interest.name}: {interest.description}")
```

### 3. 关键词搜索

```python
# 搜索包含"水"的兴趣点
water_interests = search_interests("水")

for interest in water_interests:
    print(f"{interest.name} ({interest.category.value})")
```

### 4. 按键获取

```python
# 获取特定兴趣点
interest = get_interest_by_key("tactile_water")
if interest:
    print(f"名称: {interest.name}")
    print(f"材料: {', '.join(interest.related_materials)}")
```

### 5. 创建带类别的兴趣点

```python
from src.models import InterestPoint, InterestCategory

interest = InterestPoint(
    interest_id="int-001",
    name="水流",
    category=InterestCategory.TACTILE,
    intensity=8.5,
    standard_interest_key="tactile_water"  # 关联到标准库
)
```

### 6. 创建热力图数据

```python
from src.models import InterestHeatmapData, TrendDirection

heatmap = InterestHeatmapData(
    interest_name="水流",
    category="tactile",  # 支持按类别分组
    intensity_over_time=[
        {"date": "2024-01-01", "intensity": 7.0},
        {"date": "2024-01-08", "intensity": 8.5},
    ],
    current_intensity=8.5,
    trend=TrendDirection.IMPROVING,
    mention_count=12,
    first_mentioned="2024-01-01",
    last_mentioned="2024-01-08"
)
```

## 应用场景

### 1. 档案创建时的兴趣点识别

当从医院报告中解析兴趣点时，可以使用关键词搜索匹配到标准库：

```python
# 从报告中提取的兴趣点文本
raw_interests = ["喜欢玩水", "对旋转的东西感兴趣", "喜欢积木"]

matched_interests = []
for raw in raw_interests:
    # 搜索匹配
    results = search_interests(raw)
    if results:
        matched_interests.append(results[0])
```

### 2. 游戏推荐时的材料建议

根据孩子的兴趣点，推荐相关材料：

```python
child_interests = profile.interests  # List[InterestPoint]

for interest in child_interests:
    if interest.standard_interest_key:
        standard = get_interest_by_key(interest.standard_interest_key)
        if standard:
            print(f"推荐材料: {', '.join(standard.related_materials)}")
```

### 3. 热力图按类别分组显示

前端可以按类别分组展示兴趣点热力图：

```python
# 获取所有热力图数据
heatmaps = get_interest_heatmaps(child_id)

# 按类别分组
grouped = {}
for heatmap in heatmaps:
    category = heatmap.category or "other"
    if category not in grouped:
        grouped[category] = []
    grouped[category].append(heatmap)

# 渲染
for category, items in grouped.items():
    print(f"\n{category} 类:")
    for item in items:
        print(f"  - {item.interest_name}: {item.current_intensity}/10")
```

### 4. 趋势分析

分析不同类别兴趣点的变化趋势：

```python
# 统计各类别的平均强度
category_stats = {}
for heatmap in heatmaps:
    cat = heatmap.category
    if cat not in category_stats:
        category_stats[cat] = []
    category_stats[cat].append(heatmap.current_intensity)

for cat, intensities in category_stats.items():
    avg = sum(intensities) / len(intensities)
    print(f"{cat}: 平均强度 {avg:.1f}/10")
```

## 扩展标准库

如需添加新的标准兴趣点，在 `src/models/interest_library.py` 中的 `STANDARD_INTERESTS` 字典中添加：

```python
STANDARD_INTERESTS = {
    # ... 现有兴趣点
    
    "new_interest_key": StandardInterest(
        interest_key="new_interest_key",
        name="新兴趣点名称",
        category=InterestCategory.VISUAL,
        description="描述",
        related_materials=["材料1", "材料2"],
        keywords=["关键词1", "关键词2"]
    ),
}
```

## 注意事项

1. **类别是可选的**：`InterestPoint.category` 和 `InterestHeatmapData.category` 都是可选字段，兼容旧数据
2. **标准库关联是可选的**：不是所有兴趣点都需要关联到标准库，自定义兴趣点也完全支持
3. **关键词匹配不区分大小写**：搜索时会自动转换为小写进行匹配
4. **类别枚举可扩展**：如需新增类别，在 `InterestCategory` 枚举中添加即可

## 测试

运行测试：

```bash
conda activate asd_agent
python tests/test_interest_library.py
```

测试覆盖：
- ✅ 标准兴趣点库统计
- ✅ 按类别查询
- ✅ 关键词搜索
- ✅ 按键获取
- ✅ InterestPoint 扩展
- ✅ InterestHeatmapData 扩展
