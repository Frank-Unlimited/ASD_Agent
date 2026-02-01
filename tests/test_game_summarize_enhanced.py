"""
测试增强后的游戏总结功能（包含兴趣验证）
"""
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.models.game import GamePlan, GameGoal, GameStep, TargetDimension
from services.SQLite.service import SQLiteService
import json


def test_create_interest_trial_session():
    """创建一个兴趣试错的游戏会话"""
    print("\n" + "=" * 60)
    print("创建兴趣试错游戏会话")
    print("=" * 60)
    
    sqlite_service = SQLiteService()
    
    # 1. 创建一个游戏方案（测试"音乐玩具"这个兴趣点）
    game_plan = GamePlan(
        game_id="game-interest-trial-001",
        child_id="test_child_001",
        title="音乐探索游戏",
        description="通过音乐玩具验证孩子对听觉刺激的兴趣",
        target_dimension=TargetDimension.SENSORY,
        estimated_duration=15,
        goals=GameGoal(
            primary_goal="验证孩子对音乐玩具的兴趣",
            secondary_goals=["观察孩子对听觉刺激的反应", "探索新的兴趣点"],
            success_criteria=["孩子主动靠近音乐玩具", "孩子尝试操作音乐玩具"]
        ),
        steps=[
            GameStep(
                step_number=1,
                title="准备阶段",
                description="准备音乐玩具（音乐盒、小钢琴），放在孩子视线范围内",
                parent_actions=["摆放玩具", "观察孩子反应"],
                expected_child_response="注意到音乐玩具",
                tips=["不要主动引导，让孩子自然发现"]
            ),
            GameStep(
                step_number=2,
                title="音乐启动",
                description="轻轻按下音乐盒，播放柔和的音乐",
                parent_actions=["播放音乐", "观察孩子反应"],
                expected_child_response="转头寻找声源或靠近音乐盒",
                tips=["音量适中，避免惊吓孩子"]
            ),
            GameStep(
                step_number=3,
                title="互动尝试",
                description="如果孩子感兴趣，引导孩子尝试按按钮",
                parent_actions=["示范按按钮", "鼓励孩子尝试"],
                expected_child_response="尝试按按钮或触摸音乐玩具",
                tips=["给孩子足够的探索时间"]
            )
        ],
        materials_needed=["音乐盒", "小钢琴玩具"],
        environment_setup="安静的房间，减少其他干扰",
        design_rationale="档案中标记孩子可能对音乐有兴趣，但未经验证，本次游戏用于试错"
    )
    
    # 保存游戏方案
    game_id = sqlite_service.save_game_plan(game_plan.dict())
    print(f"\n✅ 游戏方案已保存: {game_id}")
    
    # 2. 创建游戏会话
    session_id = sqlite_service.create_game_session(
        child_id="test_child_001",
        game_id=game_id
    )
    print(f"✅ 会话创建成功: {session_id}")
    
    # 3. 模拟游戏过程（包含意外发现）
    sqlite_service.update_game_session(session_id, {
        "status": "completed",
        "end_time": datetime.now().isoformat(),
        "actual_duration": 12,  # 12分钟
        "parent_observations": [
            {
                "timestamp": datetime.now().isoformat(),
                "content": "播放音乐后，孩子立即转头寻找声源",
                "child_behavior": "主动寻找",
                "parent_feeling": "很惊喜"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "content": "孩子主动靠近音乐盒，伸手触摸",
                "child_behavior": "主动探索",
                "parent_feeling": "很开心"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "content": "孩子尝试按按钮，成功播放音乐后露出笑容",
                "child_behavior": "成功操作并表现出愉悦",
                "parent_feeling": "非常满意"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "content": "意外发现：孩子对音乐盒的旋转机械装置也很感兴趣，反复观察",
                "child_behavior": "专注观察机械运动",
                "parent_feeling": "意外的发现"
            },
            {
                "timestamp": datetime.now().isoformat(),
                "content": "游戏中途，孩子对旁边的彩色积木看了一眼，但很快又回到音乐玩具",
                "child_behavior": "短暂分心但能回到主要活动",
                "parent_feeling": "注意力还不错"
            }
        ],
        "child_engagement_score": 9.0,
        "goal_achievement_score": 9.5,
        "parent_satisfaction_score": 9.5,
        "notes": "本次游戏是为了验证孩子对音乐玩具的兴趣，结果非常成功！孩子表现出强烈的兴趣和主动性。"
    })
    
    print(f"✅ 会话状态已更新为 completed")
    
    # 4. 获取会话信息
    session = sqlite_service.get_game_session(session_id)
    print(f"\n会话信息:")
    print(f"  - ID: {session['session_id']}")
    print(f"  - 游戏ID: {session['game_id']}")
    print(f"  - 状态: {session['status']}")
    print(f"  - 时长: {session['actual_duration']} 分钟")
    print(f"  - 观察记录: {len(session.get('parent_observations', []))} 条")
    print(f"  - 参与度评分: {session.get('child_engagement_score', 'N/A')}")
    
    print("\n" + "=" * 60)
    print(f"兴趣试错游戏会话创建完成！")
    print(f"session_id='{session_id}'")
    print("\n这个会话包含：")
    print("  1. 明确的兴趣验证目标（音乐玩具）")
    print("  2. 孩子的积极反应（验证成功）")
    print("  3. 意外发现（对机械装置感兴趣）")
    print("  4. 对比兴趣（彩色积木 vs 音乐玩具）")
    print("\n可以使用此 session_id 测试增强后的游戏总结功能")
    print("=" * 60)
    
    return session_id


if __name__ == "__main__":
    session_id = test_create_interest_trial_session()
    print(f"\n\n下一步：运行游戏总结 API 测试")
    print(f"python tests/test_game_summarize_api.py")
    print(f"记得更新 SESSION_ID = '{session_id}'")
