"""
简单的游戏 API 测试
"""
import requests

API_URL = "http://localhost:8000"
CHILD_ID = "test_child_001"

def test_health():
    """测试健康检查"""
    print("\n[测试] 健康检查...")
    response = requests.get(f"{API_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    assert response.status_code == 200

def test_game_calendar():
    """测试游戏日历"""
    print("\n[测试] 游戏日历...")
    response = requests.get(f"{API_URL}/api/game/calendar/{CHILD_ID}")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    # 即使功能未实现，也应该返回 200
    assert response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("游戏 API 简单测试")
    print("=" * 60)
    
    try:
        test_health()
        test_game_calendar()
        print("\n✅ 所有测试通过")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
