"""
测试 Game Service
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.game import GameRecommendRequest, TargetDimension
from src.models.profile import ChildProfile, Gender, DiagnosisLevel, DevelopmentDimension, InterestPoint
from services.game import GameRecommender
from services.mock.sqlite_service import MockSQLiteService
from services.mock.rag_service import MockRAGService


class MockProfileService:
    """Mock Profile Service"""
    
    async def get_profile(self, child_id: str) -> ChildProfile:
        """返回测试档案"""
        return ChildProfile(
            child_id=child_id,
            name="小明",
            gender=Gender.MALE,
            birth_date="2020-03-15",
            diagnosis="自闭症谱系障碍",
            diagnosis_level=DiagnosisLevel.MODERATE,
            diagnosis_date="2023-06-20",
            development_dimensions=[
                DevelopmentDimension(
                    dimension_id="eye_contact",
                    dimension_name="眼神接触",
                    current_level=4.5
                ),
                DevelopmentDimension(
                    dimension_id="joint_attention",
                    dimension_name="共同注意",
                    current_level=3.8
                ),
                DevelopmentDimension(
                    dimension_id="language",
                    dimension_name="语言能力",
                    current_level=5.2
                )
            ],
            interests=[
                InterestPoint(
                    interest_id="int-1",
                    name="水流",
                    intensity=8.5
                ),
                InterestPoint(
                    interest_id="int-2",
                    name="旋转物体",
                    intensity=7.0
                ),
                InterestPoint(
                    interest_id="int-3",
                    name="音乐",
                    intensity=6.5
                )
            ]
        )


async def test_game_recommendation():
    """测试游戏推荐"""
    print("\n" + "="*60)
    print("测试 Game Service - 游戏推荐")
    print("="*60)
    
    # 初始化服务
    profile_service = MockProfileService()
    sqlite_service = MockSQLiteService()
    
    game_recommender = GameRecommender(
        profile_service=profile_service,
        sqlite_service=sqlite_service
    )
    
    # 测试 1: 基本推荐（无特殊要求）
    print("\n[测试 1] 基本推荐（无特殊要求）")
    print("-" * 60)
    
    request = GameRecommendRequest(
        child_id="test-child-001"
    )
    
    try:
        response = await game_recommender.recommend_game(request)
        
        print(f"✓ 推荐成功")
        print(f"  游戏标题: {response.game_plan.title}")
        print(f"  游戏ID: {response.game_plan.game_id}")
        print(f"  目标维度: {response.game_plan.target_dimension.value}")
        print(f"  预计时长: {response.game_plan.estimated_duration} 分钟")
        print(f"  步骤数量: {len(response.game_plan.steps)}")
        print(f"  设计依据: {response.game_plan.design_rationale[:100]}...")
        print(f"  推荐理由: {response.recommendation_reason[:100]}...")
        
        # 显示游戏步骤
        print(f"\n  游戏步骤:")
        for step in response.game_plan.steps[:3]:  # 只显示前3步
            print(f"    {step.step_number}. {step.title}")
            print(f"       {step.description[:80]}...")
        
        # 显示材料
        if response.game_plan.materials_needed:
            print(f"\n  所需材料: {', '.join(response.game_plan.materials_needed[:5])}")
        
        # 显示注意事项
        if response.game_plan.precautions:
            print(f"\n  注意事项:")
            for precaution in response.game_plan.precautions[:2]:
                print(f"    - [{precaution.category}] {precaution.content[:60]}...")
        
    except Exception as e:
        print(f"✗ 推荐失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 测试 2: 指定关注维度
    print("\n[测试 2] 指定关注维度（眼神接触）")
    print("-" * 60)
    
    request = GameRecommendRequest(
        child_id="test-child-001",
        focus_dimension=TargetDimension.EYE_CONTACT
    )
    
    try:
        response = await game_recommender.recommend_game(request)
        
        print(f"✓ 推荐成功")
        print(f"  游戏标题: {response.game_plan.title}")
        print(f"  目标维度: {response.game_plan.target_dimension.value}")
        print(f"  是否匹配要求: {'✓' if response.game_plan.target_dimension == TargetDimension.EYE_CONTACT else '✗'}")
        
    except Exception as e:
        print(f"✗ 推荐失败: {e}")
    
    # 测试 3: 指定时长偏好
    print("\n[测试 3] 指定时长偏好（15分钟）")
    print("-" * 60)
    
    request = GameRecommendRequest(
        child_id="test-child-001",
        duration_preference=15
    )
    
    try:
        response = await game_recommender.recommend_game(request)
        
        print(f"✓ 推荐成功")
        print(f"  游戏标题: {response.game_plan.title}")
        print(f"  预计时长: {response.game_plan.estimated_duration} 分钟")
        print(f"  时长是否接近要求: {'✓' if abs(response.game_plan.estimated_duration - 15) <= 5 else '✗'}")
        
    except Exception as e:
        print(f"✗ 推荐失败: {e}")
    
    # 测试 4: 同时指定维度和时长
    print("\n[测试 4] 同时指定维度和时长")
    print("-" * 60)
    
    request = GameRecommendRequest(
        child_id="test-child-001",
        focus_dimension=TargetDimension.JOINT_ATTENTION,
        duration_preference=20
    )
    
    try:
        response = await game_recommender.recommend_game(request)
        
        print(f"✓ 推荐成功")
        print(f"  游戏标题: {response.game_plan.title}")
        print(f"  目标维度: {response.game_plan.target_dimension.value}")
        print(f"  预计时长: {response.game_plan.estimated_duration} 分钟")
        
    except Exception as e:
        print(f"✗ 推荐失败: {e}")
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)


async def test_schema_builder():
    """测试 Schema 构建器"""
    print("\n" + "="*60)
    print("测试 Schema Builder")
    print("="*60)
    
    from services.game.schema_builder import pydantic_to_json_schema
    from src.models.game import GamePlan
    
    schema = pydantic_to_json_schema(
        model=GamePlan,
        schema_name="GamePlan",
        description="完整的地板时光游戏方案"
    )
    
    print(f"\n✓ Schema 构建成功")
    print(f"  Schema 名称: {schema['name']}")
    print(f"  Schema 描述: {schema['description']}")
    print(f"  属性数量: {len(schema['schema']['properties'])}")
    print(f"  必需字段数量: {len(schema['schema']['required'])}")
    
    # 显示部分属性
    print(f"\n  部分属性:")
    for key in list(schema['schema']['properties'].keys())[:5]:
        prop = schema['schema']['properties'][key]
        prop_type = prop.get('type', prop.get('anyOf', 'unknown'))
        print(f"    - {key}: {prop_type}")
    
    print("\n" + "="*60)


async def test_prompt_builder():
    """测试 Prompt 构建器"""
    print("\n" + "="*60)
    print("测试 Prompt Builder")
    print("="*60)
    
    from services.game.prompts import build_game_recommendation_prompt
    
    # 创建测试档案
    profile = ChildProfile(
        child_id="test-001",
        name="小明",
        gender=Gender.MALE,
        birth_date="2020-03-15",
        diagnosis="自闭症谱系障碍",
        diagnosis_level=DiagnosisLevel.MODERATE,
        development_dimensions=[
            DevelopmentDimension(
                dimension_id="eye_contact",
                dimension_name="眼神接触",
                current_level=4.5
            )
        ],
        interests=[
            InterestPoint(
                interest_id="int-1",
                name="水流",
                intensity=8.5
            )
        ]
    )
    
    prompt = build_game_recommendation_prompt(
        child_profile=profile,
        recent_assessments=None,
        recent_games=None,
        focus_dimension="eye_contact",
        duration_preference=15
    )
    
    print(f"\n✓ Prompt 构建成功")
    print(f"  Prompt 长度: {len(prompt)} 字符")
    print(f"\n  Prompt 预览:")
    print("-" * 60)
    print(prompt[:500] + "...")
    print("-" * 60)
    
    # 检查关键内容
    checks = [
        ("包含孩子姓名", "小明" in prompt),
        ("包含年龄信息", "岁" in prompt or "个月" in prompt),
        ("包含诊断信息", "自闭症" in prompt),
        ("包含发展维度", "眼神接触" in prompt),
        ("包含兴趣点", "水流" in prompt),
        ("包含关注维度", "eye_contact" in prompt),
        ("包含时长要求", "15" in prompt),
    ]
    
    print(f"\n  内容检查:")
    for check_name, result in checks:
        print(f"    {'✓' if result else '✗'} {check_name}")
    
    print("\n" + "="*60)


async def main():
    """运行所有测试"""
    print("\n开始测试 Game Service")
    
    # 测试 Schema Builder
    await test_schema_builder()
    
    # 测试 Prompt Builder
    await test_prompt_builder()
    
    # 测试游戏推荐（需要 LLM API）
    print("\n是否测试游戏推荐功能？（需要 LLM API）")
    print("按 Enter 继续，Ctrl+C 跳过")
    try:
        input()
        await test_game_recommendation()
    except KeyboardInterrupt:
        print("\n跳过游戏推荐测试")


if __name__ == "__main__":
    asyncio.run(main())
