"""
API 端点自动化测试
使用 requests 测试实际的 HTTP 请求
"""
import requests
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


API_BASE_URL = "http://localhost:8000"
TEST_CHILD_ID = "test_api_child_001"


def test_health_check():
    """测试健康检查"""
    print("\n[1/6] 测试健康检查...")
    response = requests.get(f"{API_BASE_URL}/health", timeout=5)
    print(f"  状态码: {response.status_code}")
    
    if response.status_code != 200:
        raise AssertionError(f"健康检查失败: {response.status_code}")
    
    data = response.json()
    if data.get("status") != "healthy":
        raise AssertionError(f"健康状态异常: {data}")
    
    print("✅ 健康检查通过")


def test_text_observation():
    """测试文字观察记录"""
    print("\n[2/6] 测试文字观察记录...")
    payload = {
        "child_id": TEST_CHILD_ID,
        "text": "小明今天主动把积木递给我，还看着我的眼睛笑了",
        "context": {
            "location": "家里客厅",
            "activity": "积木游戏"
        }
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/observation/text",
        json=payload,
        timeout=30
    )
    
    print(f"  状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  错误: {response.text}")
        raise AssertionError(f"文字观察记录失败: {response.status_code}")
    
    data = response.json()
    if not data.get("success"):
        raise AssertionError(f"返回 success=False: {data}")
    if "behavior_id" not in data:
        raise AssertionError(f"缺少 behavior_id: {data}")
    if "description" not in data:
        raise AssertionError(f"缺少 description: {data}")
    
    print(f"✅ 文字观察记录成功")
    print(f"  - behavior_id: {data['behavior_id']}")
    print(f"  - 描述: {data['description']}")
    print(f"  - 事件类型: {data['event_type']}")
    print(f"  - 重要性: {data['significance']}")
    
    return data["behavior_id"]


def test_quick_button():
    """测试快速按钮"""
    print("\n[3/6] 测试快速按钮...")
    payload = {
        "child_id": TEST_CHILD_ID,
        "button_type": "eye_contact",
        "context": None
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/observation/quick",
        json=payload,
        timeout=30
    )
    
    print(f"  状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  错误: {response.text}")
        raise AssertionError(f"快速按钮记录失败: {response.status_code}")
    
    data = response.json()
    if not data.get("success"):
        raise AssertionError(f"返回 success=False: {data}")
    if "behavior_id" not in data:
        raise AssertionError(f"缺少 behavior_id: {data}")
    
    print(f"✅ 快速按钮记录成功")
    print(f"  - behavior_id: {data['behavior_id']}")
    print(f"  - 按钮类型: {data['button_type']}")
    print(f"  - 描述: {data['description']}")


def test_get_recent_observations():
    """测试获取最近观察"""
    print("\n[4/6] 测试获取最近观察...")
    response = requests.get(
        f"{API_BASE_URL}/api/observation/recent/{TEST_CHILD_ID}?limit=10",
        timeout=10
    )
    
    print(f"  状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  错误: {response.text}")
        raise AssertionError(f"获取最近观察失败: {response.status_code}")
    
    data = response.json()
    if not data.get("success"):
        raise AssertionError(f"返回 success=False: {data}")
    if "observations" not in data:
        raise AssertionError(f"缺少 observations: {data}")
    
    print(f"✅ 获取最近观察成功")
    print(f"  - 记录数: {data['count']}")
    
    if data["count"] > 0:
        print(f"  - 最新记录: {data['observations'][0].get('description', '')[:50]}...")


def test_get_stats():
    """测试获取统计"""
    print("\n[5/6] 测试获取统计...")
    response = requests.get(
        f"{API_BASE_URL}/api/observation/stats/{TEST_CHILD_ID}?days=7",
        timeout=10
    )
    
    print(f"  状态码: {response.status_code}")
    
    if response.status_code != 200:
        print(f"  错误: {response.text}")
        raise AssertionError(f"获取统计失败: {response.status_code}")
    
    data = response.json()
    if not data.get("success"):
        raise AssertionError(f"返回 success=False: {data}")
    if "stats" not in data:
        raise AssertionError(f"缺少 stats: {data}")
    
    stats = data["stats"]
    print(f"✅ 获取统计成功")
    print(f"  - 总记录数: {stats['total_count']}")
    print(f"  - 突破性进步: {stats['breakthrough_count']}")
    print(f"  - 事件类型: {stats['event_types']}")


def test_multiple_observations():
    """测试批量记录"""
    print("\n[6/6] 测试批量记录...")
    
    test_cases = [
        "孩子听到音乐就开心地跳舞",
        "小红拉着妈妈的手去拿玩具",
        "孩子第一次主动叫了妈妈",
    ]
    
    for i, text in enumerate(test_cases, 1):
        payload = {
            "child_id": TEST_CHILD_ID,
            "text": text,
            "context": None
        }
        
        response = requests.post(
            f"{API_BASE_URL}/api/observation/text",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"  ❌ 记录 {i} 失败: {response.text}")
            continue
        
        data = response.json()
        print(f"  ✓ 记录 {i}: {data['description'][:30]}... ({data['significance']})")
    
    print(f"✅ 批量记录完成")


def cleanup():
    """清理测试数据"""
    print("\n[清理] 清理测试数据...")
    try:
        import asyncio
        from services.Memory.service import get_memory_service
        
        async def do_cleanup():
            memory = await get_memory_service()
            await memory.storage.clear_child_data(TEST_CHILD_ID)
            await memory.close()
        
        asyncio.run(do_cleanup())
        print("✅ 清理完成")
    except Exception as e:
        print(f"⚠️ 清理失败: {e}")


def main():
    """主测试流程"""
    print("="*60)
    print("API 端点自动化测试")
    print("="*60)
    print(f"API 地址: {API_BASE_URL}")
    print(f"测试孩子ID: {TEST_CHILD_ID}")
    
    try:
        # 测试健康检查
        test_health_check()
        
        # 测试文字观察
        test_text_observation()
        
        # 测试快速按钮
        test_quick_button()
        
        # 测试获取最近观察
        test_get_recent_observations()
        
        # 测试获取统计
        test_get_stats()
        
        # 测试批量记录
        test_multiple_observations()
        
        print("\n" + "="*60)
        print("🎉 所有测试通过！")
        print("="*60)
        
    except AssertionError as e:
        print("\n" + "="*60)
        print(f"❌ 测试失败: {e}")
        print("="*60)
        return False
    except requests.exceptions.ConnectionError:
        print("\n" + "="*60)
        print("❌ 无法连接到服务器")
        print("请确保服务器已启动: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000")
        print("="*60)
        return False
    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ 未知错误: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return False
    finally:
        # 清理测试数据
        cleanup()
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
