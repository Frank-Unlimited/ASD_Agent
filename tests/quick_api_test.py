"""快速 API 测试"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

print("测试 API 连接...")

# 1. 健康检查
try:
    r = requests.get(f"{API_BASE_URL}/health", timeout=5)
    print(f"✅ 健康检查: {r.json()}")
except Exception as e:
    print(f"❌ 无法连接服务器: {e}")
    print("请先启动服务器: python -m uvicorn src.main:app --host 0.0.0.0 --port 8000")
    exit(1)

# 2. 文字观察
print("\n测试文字观察...")
payload = {
    "child_id": "test_child_001",
    "text": "小明今天主动把积木递给我",
    "context": None
}

try:
    r = requests.post(
        f"{API_BASE_URL}/api/observation/text",
        json=payload,
        timeout=30
    )
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ 成功: {data.get('description', '')}")
    else:
        print(f"❌ 失败: {r.text}")
except Exception as e:
    print(f"❌ 错误: {e}")

# 3. 快速按钮
print("\n测试快速按钮...")
payload = {
    "child_id": "test_child_001",
    "button_type": "eye_contact",
    "context": None
}

try:
    r = requests.post(
        f"{API_BASE_URL}/api/observation/quick",
        json=payload,
        timeout=30
    )
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ 成功: {data.get('description', '')}")
    else:
        print(f"❌ 失败: {r.text}")
except Exception as e:
    print(f"❌ 错误: {e}")

# 4. 获取最近观察
print("\n测试获取最近观察...")
try:
    r = requests.get(
        f"{API_BASE_URL}/api/observation/recent/test_child_001?limit=5",
        timeout=10
    )
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"✅ 成功: 找到 {data.get('count', 0)} 条记录")
    else:
        print(f"❌ 失败: {r.text}")
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n测试完成！")
