"""
测试 SQLite 服务的 ChildProfile 功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.models.profile import (
    ChildProfile,
    Gender,
    DiagnosisLevel,
    DevelopmentDimension,
    InterestPoint,
    InterestCategory
)
from services.SQLite.service import SQLiteService


def test_save_and_get_child():
    """测试保存和获取孩子档案"""
    print("\n" + "=" * 60)
    print("测试 SQLite ChildProfile 功能")
    print("=" * 60)
    
    # 创建测试档案
    profile = ChildProfile(
        child_id="test_child_001",
        name="测试宝宝",
        gender=Gender.MALE,
        birth_date="2022-06-15",
        diagnosis="ASD轻度",
        diagnosis_level=DiagnosisLevel.MILD,
        diagnosis_date="2024-01-01",
        development_dimensions=[
            DevelopmentDimension(
                dimension_id="eye_contact",
                dimension_name="眼神接触",
                current_level=3.5,
                description="能够短暂建立眼神接触",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="social_interaction",
                dimension_name="社交互动",
                current_level=2.8,
                description="对社交互动兴趣较低",
                last_updated=datetime.now()
            )
        ],
        interests=[
            InterestPoint(
                interest_id="int_001",
                name="彩色积木",
                category=InterestCategory.VISUAL,
                intensity=8.5,
                description="非常喜欢玩彩色积木",
                tags=["视觉", "建构"]
            ),
            InterestPoint(
                interest_id="int_002",
                name="旋转玩具",
                category=InterestCategory.MOTOR,
                intensity=7.0,
                description="喜欢看旋转的物体",
                tags=["运动", "视觉"]
            )
        ],
        notes="这是一个测试档案",
        custom_fields={"test_field": "test_value"}
    )
    
    # 初始化服务
    sqlite_service = SQLiteService()
    
    # 保存档案
    print("\n[测试] 保存档案...")
    try:
        sqlite_service.save_child(profile)
        print("✅ 保存成功")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return
    
    # 获取档案
    print("\n[测试] 获取档案...")
    try:
        retrieved_profile = sqlite_service.get_child("test_child_001")
        if retrieved_profile:
            print("✅ 获取成功")
            print(f"\n档案信息:")
            print(f"  - 姓名: {retrieved_profile.name}")
            print(f"  - 性别: {retrieved_profile.gender.value}")
            print(f"  - 出生日期: {retrieved_profile.birth_date}")
            print(f"  - 诊断: {retrieved_profile.diagnosis}")
            print(f"  - 诊断级别: {retrieved_profile.diagnosis_level.value if retrieved_profile.diagnosis_level else 'None'}")
            print(f"  - 发展维度数量: {len(retrieved_profile.development_dimensions)}")
            print(f"  - 兴趣点数量: {len(retrieved_profile.interests)}")
            
            if retrieved_profile.development_dimensions:
                print(f"\n发展维度:")
                for dim in retrieved_profile.development_dimensions:
                    print(f"  - {dim.dimension_name}: {dim.current_level}/10")
            
            if retrieved_profile.interests:
                print(f"\n兴趣点:")
                for interest in retrieved_profile.interests:
                    print(f"  - {interest.name} ({interest.category.value if interest.category else 'unknown'}): {interest.intensity}/10")
        else:
            print("❌ 获取失败: 档案不存在")
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 清理
    print("\n[测试] 清理测试数据...")
    try:
        sqlite_service.delete_child("test_child_001")
        print("✅ 清理成功")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    test_save_and_get_child()
