"""
测试游戏总结功能
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.models.game import GamePlan, GameGoal, GameStep, TargetDimension
from services.SQLite.service import SQLiteService
import json


def test_create_mock_session():
    """创建一个模拟的游戏会话用于测试"""
    print("\n" + "=" * 60)
    print("创建模拟游戏会话")
    print("=" * 60)
    
    sqlite_service = SQLiteService()
    
    # 1. 创建游戏方案
    game_plan = GamePlan(
        game_id="game-test-001",
        child_id="test_child_001",
        title="彩虹积木游戏",
        description="通过彩色积木互动，提升眼神接触和社交互动",
        target_dimension=TargetDimension.EYE_CONTACT,
        estimated_duration=15,
        goals=GameGoal(
            primary_goal="提升眼神接触频率和持续时间",
            secondary_goals=["增强社交互动意愿", "提高注意力集中"],
            success_criteria=["主动眼神接触3次以上", "眼神接触持续2秒以上"]
        ),
        steps=[
            GameStep(
                step_number=1,
                title="准备阶段",
                description="准备彩色积木，坐在孩子对面",
                parent_actions=["拿出积木", "坐下来"],
                expected_child_response="观察积木",
                tips=["保持轻松氛围"]
            ),
            GameStep(
                step_number=2,
                title="互动阶段",
                description="递给孩子积木，等待眼神接触",
                parent_actions=["递积木", "等待"],
                expected_child_response="看向家长",
                tips=["不要强迫"]
            )
        ],
        materials_needed=["彩色积木10块"],
        environment_setup="安静的房间，地板上铺垫子",
        design_rationale="基于孩子对彩色积木的高兴趣设计"
    )
    
    # 保存游戏方案到 SQLite
    game_id = sqlite_service.save_game_plan(game_plan.dict())
    print(f"\n✅ 游戏方案已保存到 SQLite: {game_id}")
    
    # 2. 创建游戏会话
    session_id = sqlite_service.create_game_session(
        child_id="test_child_001",
        game_id=game_id
    )
    
    print(f"✅ 会话创建成功: {session_id}")
    
    # 3. 更新会话状态为已完成
    sqlite_service.update_game_session(session_id, {
        "status": "completed",
        "end_time": datetime.now().isoformat(),
        "actual_duration": 15,
        "parent_observations": [
            {
                "timestamp": datetime.now().isoformat(),
                "content": "孩子主动看了我一眼",
                "child_behavior": "眼神接触",
                "parent_feeling": "很开心"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "content": "孩子把积木递给我",
                "child_behavior": "社交互动",
                "parent_feeling": "感到惊喜"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "content": "孩子笑了",
                "child_behavior": "情绪表达",
                "parent_feeling": "很温暖"
            }
        ],
        "child_engagement_score": 8.5,
        "goal_achievement_score": 7.0,
        "parent_satisfaction_score": 9.0
    })
    
    print(f"✅ 会话状态已更新为 completed")
    
    # 4. 获取会话
    session = sqlite_service.get_game_session(session_id)
    print(f"\n会话信息:")
    print(f"  - ID: {session['session_id']}")
    print(f"  - 游戏ID: {session['game_id']}")
    print(f"  - 状态: {session['status']}")
    print(f"  - 时长: {session['actual_duration']} 分钟")
    print(f"  - 观察记录: {len(session.get('parent_observations', []))} 条")
    print(f"  - 参与度评分: {session.get('child_engagement_score', 'N/A')}")
    
    print("\n" + "=" * 60)
    print(f"模拟会话创建完成！session_id='{session_id}'")
    print("可以使用此 session_id 测试游戏总结功能")
    print("=" * 60)
    
    return session_id


if __name__ == "__main__":
    test_create_mock_session()
