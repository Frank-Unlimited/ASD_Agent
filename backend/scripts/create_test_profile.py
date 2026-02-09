"""
创建测试用的孩子档案
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


def create_test_profile():
    """创建测试档案"""
    print("\n" + "=" * 60)
    print("创建测试孩子档案")
    print("=" * 60)
    
    # 创建测试档案
    profile = ChildProfile(
        child_id="test_child_001",
        name="辰辰",
        gender=Gender.MALE,
        birth_date="2022-06-15",
        diagnosis="ASD轻度",
        diagnosis_level=DiagnosisLevel.MILD,
        diagnosis_date="2024-01-01",
        
        # 发展维度（33个维度的一部分）
        development_dimensions=[
            # 社交互动
            DevelopmentDimension(
                dimension_id="eye_contact",
                dimension_name="眼神接触",
                current_level=3.5,
                description="能够短暂建立眼神接触，但持续时间较短",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="social_smile",
                dimension_name="社交性微笑",
                current_level=4.0,
                description="能够回应性微笑，偶尔主动微笑",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="social_interest",
                dimension_name="社交兴趣",
                current_level=2.8,
                description="对他人兴趣较低，更喜欢独自玩耍",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="imitation",
                dimension_name="模仿能力",
                current_level=3.2,
                description="能够模仿简单动作，语言模仿较弱",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="joint_attention",
                dimension_name="共同注意力",
                current_level=2.5,
                description="较少主动分享注意力焦点",
                last_updated=datetime.now()
            ),
            
            # 语言沟通
            DevelopmentDimension(
                dimension_id="language_comprehension",
                dimension_name="语言理解",
                current_level=3.0,
                description="能理解简单指令",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="language_expression",
                dimension_name="语言表达",
                current_level=2.0,
                description="语言表达能力较弱，主要使用单词",
                last_updated=datetime.now()
            ),
            
            # 情绪适应
            DevelopmentDimension(
                dimension_id="emotional_expression",
                dimension_name="情绪表达",
                current_level=3.5,
                description="能够表达基本情绪",
                last_updated=datetime.now()
            ),
            DevelopmentDimension(
                dimension_id="emotional_response",
                dimension_name="情绪反应",
                current_level=3.0,
                description="情绪反应基本适当",
                last_updated=datetime.now()
            ),
        ],
        
        # 兴趣点
        interests=[
            InterestPoint(
                interest_id="int_001",
                name="彩色积木",
                category=InterestCategory.VISUAL,
                intensity=8.5,
                description="非常喜欢玩彩色积木，可以专注很长时间",
                tags=["视觉", "建构", "高强度"],
                discovered_date=datetime.now()
            ),
            InterestPoint(
                interest_id="int_002",
                name="旋转玩具",
                category=InterestCategory.MOTOR,
                intensity=7.0,
                description="喜欢看旋转的物体，如陀螺、风车",
                tags=["运动", "视觉", "中高强度"],
                discovered_date=datetime.now()
            ),
            InterestPoint(
                interest_id="int_003",
                name="儿歌音乐",
                category=InterestCategory.AUDITORY,
                intensity=6.5,
                description="喜欢听儿歌，会随着音乐摇摆",
                tags=["听觉", "中等强度"],
                discovered_date=datetime.now()
            ),
            InterestPoint(
                interest_id="int_004",
                name="动物模型",
                category=InterestCategory.COGNITIVE,
                intensity=5.5,
                description="对动物模型有一定兴趣",
                tags=["认知", "中等强度"],
                discovered_date=datetime.now()
            ),
        ],
        
        notes="辰辰是一个3岁半的男孩，诊断为ASD轻度。他对视觉类玩具特别感兴趣，尤其是彩色积木。社交互动能力有待提升，但情绪表达相对较好。",
        custom_fields={
            "parent_name": "妈妈",
            "primary_caregiver": "母亲",
            "intervention_start_date": "2024-01-10"
        }
    )
    
    # 初始化服务
    sqlite_service = SQLiteService()
    
    # 保存档案
    print("\n[创建] 保存档案...")
    try:
        sqlite_service.save_child(profile)
        print("✅ 档案创建成功")
        print(f"\n档案信息:")
        print(f"  - ID: {profile.child_id}")
        print(f"  - 姓名: {profile.name}")
        print(f"  - 年龄: 3岁6个月")
        print(f"  - 诊断: {profile.diagnosis} ({profile.diagnosis_level.value})")
        print(f"  - 发展维度数量: {len(profile.development_dimensions)}")
        print(f"  - 兴趣点数量: {len(profile.interests)}")
        
        print(f"\n主要兴趣点:")
        for interest in profile.interests[:3]:
            print(f"  - {interest.name} ({interest.category.value}): {interest.intensity}/10")
        
        print(f"\n关键发展维度:")
        for dim in profile.development_dimensions[:5]:
            print(f"  - {dim.dimension_name}: {dim.current_level}/10")
        
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 60)
    print("测试档案创建完成！")
    print("可以使用 child_id='test_child_001' 进行测试")
    print("=" * 60)


if __name__ == "__main__":
    create_test_profile()
