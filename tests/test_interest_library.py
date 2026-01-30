"""
测试兴趣点库
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models import (
    InterestCategory,
    StandardInterest,
    STANDARD_INTERESTS,
    get_interest_by_key,
    get_interests_by_category,
    search_interests,
    get_all_categories
)


def test_standard_interests():
    """测试标准兴趣点库"""
    print("\n" + "="*60)
    print("测试标准兴趣点库")
    print("="*60)
    
    # 1. 统计各类别的兴趣点数量
    print("\n[统计] 各类别兴趣点数量")
    print("-" * 60)
    
    category_counts = {}
    for interest in STANDARD_INTERESTS.values():
        category = interest.category.value
        category_counts[category] = category_counts.get(category, 0) + 1
    
    total = len(STANDARD_INTERESTS)
    print(f"总计: {total} 个标准兴趣点\n")
    
    for category in InterestCategory:
        count = category_counts.get(category.value, 0)
        print(f"  {category.value:15s} ({category.name:15s}): {count:2d} 个")
    
    # 2. 按类别查询
    print("\n[查询] 视觉类兴趣点")
    print("-" * 60)
    
    visual_interests = get_interests_by_category(InterestCategory.VISUAL)
    for interest in visual_interests:
        print(f"  - {interest.name:15s} ({interest.interest_key})")
        print(f"    描述: {interest.description}")
        print(f"    材料: {', '.join(interest.related_materials[:3])}")
        print()
    
    # 3. 关键词搜索
    print("\n[搜索] 关键词: '水'")
    print("-" * 60)
    
    water_interests = search_interests("水")
    for interest in water_interests:
        print(f"  - {interest.name} ({interest.category.value})")
        print(f"    关键词: {', '.join(interest.keywords)}")
    
    print("\n[搜索] 关键词: '积木'")
    print("-" * 60)
    
    block_interests = search_interests("积木")
    for interest in block_interests:
        print(f"  - {interest.name} ({interest.category.value})")
    
    # 4. 按键获取
    print("\n[获取] 特定兴趣点")
    print("-" * 60)
    
    interest = get_interest_by_key("tactile_water")
    if interest:
        print(f"  键: {interest.interest_key}")
        print(f"  名称: {interest.name}")
        print(f"  类别: {interest.category.value}")
        print(f"  描述: {interest.description}")
        print(f"  材料: {', '.join(interest.related_materials)}")
        print(f"  关键词: {', '.join(interest.keywords)}")
    
    # 5. 展示所有类别
    print("\n[类别] 所有兴趣类别")
    print("-" * 60)
    
    categories = get_all_categories()
    for cat in categories:
        print(f"  - {cat.value:15s} ({cat.name})")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


def test_interest_point_with_category():
    """测试带类别的兴趣点"""
    print("\n" + "="*60)
    print("测试 InterestPoint 扩展")
    print("="*60)
    
    from src.models import InterestPoint
    from datetime import datetime
    
    # 创建带类别的兴趣点
    interest = InterestPoint(
        interest_id="int-001",
        name="水流",
        category=InterestCategory.TACTILE,
        intensity=8.5,
        discovered_date=datetime.now(),
        description="喜欢玩水、观察水流",
        tags=["触觉", "视觉"],
        standard_interest_key="tactile_water"
    )
    
    print(f"\n创建兴趣点:")
    print(f"  ID: {interest.interest_id}")
    print(f"  名称: {interest.name}")
    print(f"  类别: {interest.category.value if interest.category else '未分类'}")
    print(f"  强度: {interest.intensity}/10")
    print(f"  标准库键: {interest.standard_interest_key}")
    
    # 关联到标准库
    if interest.standard_interest_key:
        standard = get_interest_by_key(interest.standard_interest_key)
        if standard:
            print(f"\n关联的标准兴趣点:")
            print(f"  名称: {standard.name}")
            print(f"  类别: {standard.category.value}")
            print(f"  推荐材料: {', '.join(standard.related_materials)}")
    
    print("\n" + "="*60)


def test_heatmap_data_with_category():
    """测试带类别的热力图数据"""
    print("\n" + "="*60)
    print("测试 InterestHeatmapData 扩展")
    print("="*60)
    
    from src.models import InterestHeatmapData, TrendDirection
    
    # 创建热力图数据
    heatmap = InterestHeatmapData(
        interest_name="水流",
        category="tactile",
        intensity_over_time=[
            {"date": "2024-01-01", "intensity": 7.0},
            {"date": "2024-01-08", "intensity": 7.5},
            {"date": "2024-01-15", "intensity": 8.0},
            {"date": "2024-01-22", "intensity": 8.5},
        ],
        current_intensity=8.5,
        trend=TrendDirection.IMPROVING,
        mention_count=12,
        first_mentioned="2024-01-01",
        last_mentioned="2024-01-22"
    )
    
    print(f"\n热力图数据:")
    print(f"  兴趣点: {heatmap.interest_name}")
    print(f"  类别: {heatmap.category}")
    print(f"  当前强度: {heatmap.current_intensity}/10")
    print(f"  趋势: {heatmap.trend.value}")
    print(f"  提及次数: {heatmap.mention_count}")
    print(f"  时间跨度: {heatmap.first_mentioned} ~ {heatmap.last_mentioned}")
    print(f"\n  强度变化:")
    for point in heatmap.intensity_over_time:
        print(f"    {point['date']}: {point['intensity']}/10")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    # 测试标准兴趣点库
    test_standard_interests()
    
    # 测试扩展的 InterestPoint
    test_interest_point_with_category()
    
    # 测试扩展的 InterestHeatmapData
    test_heatmap_data_with_category()
