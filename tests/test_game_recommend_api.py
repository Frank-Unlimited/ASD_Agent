"""
测试游戏推荐 API
"""
import requests
import json

API_URL = "http://localhost:8000"
CHILD_ID = "test_child_001"


def test_game_recommend():
    """测试游戏推荐"""
    print("\n" + "=" * 80)
    print("测试游戏推荐 API")
    print("=" * 80)
    
    # 1. 测试健康检查
    print("\n[1/3] 测试健康检查...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"状态码: {response.status_code}")
        if response.ok:
            print("✅ API 在线")
        else:
            print("❌ API 异常")
            return
    except Exception as e:
        print(f"❌ 无法连接到 API: {e}")
        return
    
    # 2. 测试游戏日历（应该为空）
    print("\n[2/3] 测试游戏日历...")
    try:
        response = requests.get(f"{API_URL}/api/game/calendar/{CHILD_ID}")
        print(f"状态码: {response.status_code}")
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)}")
        if response.ok:
            print("✅ 游戏日历 API 正常")
        else:
            print(f"⚠️ 游戏日历 API 返回错误")
    except Exception as e:
        print(f"❌ 游戏日历测试失败: {e}")
    
    # 3. 测试游戏推荐
    print("\n[3/3] 测试游戏推荐...")
    print("=" * 80)
    
    request_data = {
        "child_id": CHILD_ID,
        "focus_dimension": "eye_contact",
        "duration_preference": 15
    }
    
    print(f"\n请求数据:")
    print(json.dumps(request_data, ensure_ascii=False, indent=2))
    
    try:
        print(f"\n发送请求到: {API_URL}/api/game/recommend")
        print("⏳ 等待 LLM 生成游戏方案（可能需要 10-30 秒）...")
        
        response = requests.post(
            f"{API_URL}/api/game/recommend",
            json=request_data,
            timeout=60  # 60秒超时
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print("\n✅ 游戏推荐成功！")
            print("=" * 80)
            
            # 解析游戏方案
            game_plan = data.get('game_plan', {})
            
            print(f"\n【游戏标题】{game_plan.get('title', 'N/A')}")
            print(f"\n【游戏描述】")
            print(game_plan.get('description', 'N/A'))
            
            print(f"\n【目标维度】{game_plan.get('target_dimension', 'N/A')}")
            print(f"【预计时长】{game_plan.get('estimated_duration', 'N/A')} 分钟")
            
            # 游戏目标
            goals = game_plan.get('goals', {})
            if goals:
                print(f"\n【主要目标】{goals.get('primary_goal', 'N/A')}")
                secondary_goals = goals.get('secondary_goals', [])
                if secondary_goals:
                    print(f"【次要目标】")
                    for i, goal in enumerate(secondary_goals, 1):
                        print(f"  {i}. {goal}")
            
            # 游戏步骤
            steps = game_plan.get('steps', [])
            if steps:
                print(f"\n【游戏步骤】（共 {len(steps)} 步）")
                for step in steps[:3]:  # 只显示前3步
                    print(f"\n  步骤 {step.get('step_number', '?')}: {step.get('title', 'N/A')}")
                    print(f"  {step.get('description', 'N/A')[:100]}...")
                if len(steps) > 3:
                    print(f"\n  ... 还有 {len(steps) - 3} 个步骤")
            
            # 所需材料
            materials = game_plan.get('materials_needed', [])
            if materials:
                print(f"\n【所需材料】")
                for material in materials:
                    print(f"  - {material}")
            
            # 设计依据
            rationale = game_plan.get('design_rationale', '')
            if rationale:
                print(f"\n【设计依据】")
                print(rationale[:200] + "..." if len(rationale) > 200 else rationale)
            
            # 推荐理由
            reason = data.get('recommendation_reason', '')
            if reason:
                print(f"\n【推荐理由】")
                print(reason[:200] + "..." if len(reason) > 200 else reason)
            
            print("\n" + "=" * 80)
            print("完整响应已保存到 game_recommend_response.json")
            
            # 保存完整响应
            with open('game_recommend_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        else:
            print(f"\n❌ 游戏推荐失败")
            print(f"错误信息: {response.text}")
            
    except requests.Timeout:
        print("\n❌ 请求超时（超过60秒）")
        print("提示：LLM 生成可能需要较长时间，请检查服务器日志")
    except Exception as e:
        print(f"\n❌ 游戏推荐测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_game_recommend()
