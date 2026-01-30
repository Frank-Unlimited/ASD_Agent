"""
测试 Game Summarizer
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.game import (
    GameSession,
    GamePlan,
    GameStatus,
    TargetDimension,
    GameGoal,
    GameStep,
    ParentObservation,
    VideoAnalysisSummary,
    GameSummaryRequest
)
from src.models.profile import ChildProfile, Gender, DiagnosisLevel, DevelopmentDimension, InterestPoint
from services.game import GameSummarizer
from services.mock.sqlite_service import MockSQLiteService


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
                )
            ]
        )


class MockSQLiteServiceExtended(MockSQLiteService):
    """扩展的 Mock SQLite Service"""
    
    def __init__(self):
        super().__init__()
        self.game_sessions = {}
        self.game_plans = {}
    
    async def get_game_session(self, session_id: str):
        """获取游戏会话"""
        return self.game_sessions.get(session_id)
    
    async def get_game_plan(self, game_id: str):
        """获取游戏方案"""
        return self.game_plans.get(game_id)
    
    async def save_game_session(self, data):
        """保存游戏会话"""
        self.game_sessions[data["session_id"]] = data["data"]
    
    async def save_game_plan(self, data):
        """保存游戏方案"""
        self.game_plans[data["game_id"]] = data


async def test_game_summarizer():
    """测试游戏总结"""
    print("\n" + "="*60)
    print("测试 Game Summarizer - 游戏总结")
    print("="*60)
    
    # 初始化服务
    profile_service = MockProfileService()
    sqlite_service = MockSQLiteServiceExtended()
    
    game_summarizer = GameSummarizer(
        profile_service=profile_service,
        sqlite_service=sqlite_service
    )
    
    # 准备测试数据
    game_id = "game-test-001"
    session_id = "session-test-001"
    child_id = "test-child-001"
    
    # 创建游戏方案
    game_plan = GamePlan(
        game_id=game_id,
        child_id=child_id,
        title="水流旋转游戏",
        description="利用孩子对水流和旋转物体的兴趣，训练眼神接触和共同注意",
        estimated_duration=15,
        target_dimension=TargetDimension.EYE_CONTACT,
        additional_dimensions=[TargetDimension.JOINT_ATTENTION],
        interest_points_used=["水流", "旋转物体"],
        design_rationale="基于孩子对水流（8.5/10）和旋转物体（7.0/10）的强烈兴趣设计",
        steps=[
            GameStep(
                step_number=1,
                title="准备阶段",
                description="家长和孩子面对面坐下，展示水杯和旋转玩具",
                duration_minutes=2,
                parent_actions=["坐在孩子对面", "展示材料"],
                expected_child_response="注意到材料，表现出兴趣"
            ),
            GameStep(
                step_number=2,
                title="水流互动",
                description="家长倒水，引导孩子观察并建立眼神接触",
                duration_minutes=5,
                parent_actions=["缓慢倒水", "等待孩子眼神", "给予回应"],
                expected_child_response="看向家长，尝试表达需求"
            ),
            GameStep(
                step_number=3,
                title="旋转共享",
                description="一起玩旋转玩具，建立共同注意",
                duration_minutes=5,
                parent_actions=["旋转玩具", "指向玩具", "看向孩子"],
                expected_child_response="跟随家长视线，共同关注玩具"
            ),
            GameStep(
                step_number=4,
                title="结束整理",
                description="一起收拾材料，巩固互动",
                duration_minutes=3,
                parent_actions=["邀请孩子一起收拾"],
                expected_child_response="参与收拾，保持互动"
            )
        ],
        goals=GameGoal(
            primary_goal="提升眼神接触频率和质量",
            secondary_goals=["增强共同注意能力", "提高主动沟通意愿"],
            success_criteria=["至少3次主动眼神接触", "能跟随家长视线", "有主动表达需求的行为"]
        ),
        materials_needed=["透明水杯", "水", "旋转玩具2-3个", "毛巾"],
        status=GameStatus.COMPLETED
    )
    
    # 保存游戏方案
    await sqlite_service.save_game_plan({
        "game_id": game_id,
        "child_id": child_id,
        "data": game_plan.dict()
    })
    
    # 创建游戏会话（已完成）
    start_time = datetime.now() - timedelta(hours=1)
    end_time = datetime.now() - timedelta(minutes=45)
    
    session = GameSession(
        session_id=session_id,
        game_id=game_id,
        child_id=child_id,
        start_time=start_time,
        end_time=end_time,
        actual_duration=18,  # 实际18分钟，超出预期3分钟
        status=GameStatus.COMPLETED,
        parent_observations=[
            ParentObservation(
                timestamp=start_time + timedelta(minutes=2),
                content="小明看到水杯后立刻兴奋起来",
                child_behavior="眼睛发亮，身体前倾",
                parent_feeling="很高兴看到他的兴趣"
            ),
            ParentObservation(
                timestamp=start_time + timedelta(minutes=5),
                content="倒水时，小明主动看向我的眼睛",
                child_behavior="主动眼神接触，持续约2秒",
                parent_feeling="非常惊喜，这是很大的进步"
            ),
            ParentObservation(
                timestamp=start_time + timedelta(minutes=10),
                content="玩旋转玩具时，小明会跟随我的手指方向看",
                child_behavior="能跟随视线，共同关注玩具",
                parent_feeling="感觉我们之间的连接更强了"
            ),
            ParentObservation(
                timestamp=start_time + timedelta(minutes=15),
                content="收拾时小明有点不情愿，但还是配合了",
                child_behavior="稍微抗拒，但最终参与收拾",
                parent_feeling="结束得还算顺利"
            )
        ],
        has_video=True,
        video_analysis=VideoAnalysisSummary(
            video_path="/videos/session-test-001.mp4",
            duration_seconds=1080,
            behavior_analysis="孩子在游戏过程中表现出较高的参与度，特别是在水流环节。观察到5次主动眼神接触，平均持续1.5-2秒。共同注意行为出现3次，能较好地跟随家长视线。",
            emotional_analysis="整体情绪积极，在水流和旋转环节表现出明显的愉悦。结束时有轻微的失望情绪，但能接受并配合。",
            ai_insights=[
                "眼神接触质量有明显提升，不仅是被动响应，还有主动发起",
                "对水流的兴趣可以有效作为社交互动的桥梁",
                "共同注意能力在结构化活动中表现良好",
                "建议在下次游戏中增加更多轮次的互动，延长游戏时间"
            ],
            key_moments=[
                {"timestamp": 120, "description": "首次主动眼神接触"},
                {"timestamp": 300, "description": "成功建立共同注意"},
                {"timestamp": 600, "description": "主动用手势表达需求"}
            ]
        ),
        child_engagement_score=8.5,
        goal_achievement_score=8.0,
        parent_satisfaction_score=9.0,
        notes="整体非常满意，小明的表现超出预期。希望能继续这类游戏。"
    )
    
    # 保存游戏会话
    await sqlite_service.save_game_session({
        "session_id": session_id,
        "data": session.dict()
    })
    
    print("\n[测试场景] 完整数据的游戏总结")
    print("-" * 60)
    print(f"游戏：{game_plan.title}")
    print(f"目标维度：{game_plan.target_dimension.value}")
    print(f"预计时长：{game_plan.estimated_duration} 分钟")
    print(f"实际时长：{session.actual_duration} 分钟")
    print(f"观察记录：{len(session.parent_observations)} 条")
    print(f"视频分析：{'有' if session.has_video else '无'}")
    print(f"家长评分：参与度 {session.child_engagement_score}/10, 达成度 {session.goal_achievement_score}/10")
    
    # 执行总结
    print("\n开始生成总结...")
    
    try:
        request = GameSummaryRequest(session_id=session_id)
        response = await game_summarizer.summarize_session(request)
        
        print(f"\n✓ 总结生成成功")
        print("="*60)
        
        summary = response.summary
        
        print(f"\n【整体评价】")
        print(f"成功程度: {summary.success_level}")
        print(f"{summary.overall_assessment}")
        
        print(f"\n【目标达成情况】")
        goal_ach = summary.goal_achievement
        print(f"主要目标达成: {'是' if goal_ach.get('primary_goal_achieved') else '否'}")
        if goal_ach.get('achievement_details'):
            print(f"详情: {goal_ach['achievement_details']}")
        
        print(f"\n【各维度表现】")
        for dim in summary.dimension_progress:
            print(f"\n{dim.dimension_name} ({dim.dimension.value})")
            print(f"  评分: {dim.performance_score}/10")
            print(f"  进展: {dim.progress_description}")
            if dim.highlights:
                print(f"  亮点: {', '.join(dim.highlights[:2])}")
        
        print(f"\n【孩子表现分析】")
        perf = summary.child_performance
        print(f"  参与度: {perf.get('engagement_level', '未知')}")
        print(f"  情绪状态: {perf.get('emotional_state', '未知')}")
        print(f"  注意力: {perf.get('attention_span', '未知')}")
        
        print(f"\n【亮点时刻】")
        for i, highlight in enumerate(summary.highlights, 1):
            print(f"  {i}. {highlight}")
        
        print(f"\n【需要改进】")
        for i, area in enumerate(summary.areas_for_improvement, 1):
            print(f"  {i}. {area}")
        
        if summary.parent_feedback:
            print(f"\n【家长反馈】")
            print(f"  {summary.parent_feedback}")
        
        print(f"\n【下次建议】")
        for i, rec in enumerate(summary.recommendations_for_next, 1):
            print(f"  {i}. {rec}")
        
        if summary.trend_observation:
            print(f"\n【趋势观察】")
            print(f"  {summary.trend_observation}")
        
        print(f"\n【数据来源】")
        for source in summary.data_sources_used:
            print(f"  - {source}")
        
        # 显示完整的 JSON（用于调试）
        print(f"\n\n{'='*60}")
        print("完整总结数据（JSON格式）")
        print('='*60)
        import json
        print(json.dumps(summary.dict(), ensure_ascii=False, indent=2))
        
        print("\n" + "="*60)
        print("测试完成")
        print("="*60)
        
    except Exception as e:
        print(f"\n✗ 总结生成失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """运行测试"""
    print("\n开始测试 Game Summarizer")
    await test_game_summarizer()


if __name__ == "__main__":
    asyncio.run(main())
