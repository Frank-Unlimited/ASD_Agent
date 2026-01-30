"""
测试游戏总结 API
"""
import requests
import json

API_URL = "http://localhost:7860"
SESSION_ID = "session-949551f6eff9"  # 从 test_game_summarize_enhanced.py 获取


def test_game_summarize():
    """测试游戏总结"""
    print("\n" + "=" * 80)
    print("测试游戏总结 API")
    print("=" * 80)
    
    # 1. 测试健康检查
    print("\n[1/2] 测试健康检查...")
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
    
    # 2. 测试游戏总结
    print("\n[2/2] 测试游戏总结...")
    print("=" * 80)
    
    request_data = {
        "session_id": SESSION_ID
    }
    
    print(f"\n请求数据:")
    print(json.dumps(request_data, ensure_ascii=False, indent=2))
    
    try:
        print(f"\n发送请求到: {API_URL}/api/game/summarize")
        print("⏳ 等待 LLM 生成游戏总结（可能需要 10-30 秒）...")
        
        response = requests.post(
            f"{API_URL}/api/game/summarize",
            json=request_data,
            timeout=60
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print("\n✅ 游戏总结成功！")
            print("=" * 80)
            
            summary = data.get('summary', {})
            
            print(f"\n【整体评价】")
            print(summary.get('overall_assessment', 'N/A')[:300] + "...")
            
            print(f"\n【成功程度】{summary.get('success_level', 'N/A')}")
            
            # 目标达成
            goal_achievement = summary.get('goal_achievement', {})
            if goal_achievement:
                print(f"\n【目标达成】")
                print(f"  主要目标达成: {goal_achievement.get('primary_goal_achieved', 'N/A')}")
            
            # 维度进展
            dimension_progress = summary.get('dimension_progress', [])
            if dimension_progress:
                print(f"\n【维度进展】（共 {len(dimension_progress)} 个维度）")
                for dim in dimension_progress[:3]:
                    print(f"  - {dim.get('dimension_name', 'N/A')}: {dim.get('performance_score', 'N/A')}/10")
                    print(f"    {dim.get('progress_description', 'N/A')[:100]}...")
            
            # 亮点
            highlights = summary.get('highlights', [])
            if highlights:
                print(f"\n【亮点时刻】")
                for i, highlight in enumerate(highlights[:3], 1):
                    print(f"  {i}. {highlight}")
            
            # 改进建议
            improvements = summary.get('areas_for_improvement', [])
            if improvements:
                print(f"\n【改进建议】")
                for i, improvement in enumerate(improvements[:3], 1):
                    print(f"  {i}. {improvement}")
            
            # 下次建议
            recommendations = summary.get('recommendations_for_next', [])
            if recommendations:
                print(f"\n【下次建议】")
                for i, rec in enumerate(recommendations[:3], 1):
                    print(f"  {i}. {rec}")
            
            print("\n" + "=" * 80)
            print("完整响应已保存到 game_summarize_response.json")
            
            with open('game_summarize_response.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
        else:
            print(f"\n❌ 游戏总结失败")
            print(f"错误信息: {response.text}")
            
    except requests.Timeout:
        print("\n❌ 请求超时（超过60秒）")
    except Exception as e:
        print(f"\n❌ 游戏总结测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("测试完成")
    print("=" * 80)


if __name__ == "__main__":
    test_game_summarize()
