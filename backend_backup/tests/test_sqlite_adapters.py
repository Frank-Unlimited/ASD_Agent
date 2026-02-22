"""
适配器测试 - 测试系统接口适配
"""
import os
import sys
import asyncio
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载环境变量: {env_path}")
except ImportError:
    print("⚠️  python-dotenv 未安装")

from adapters import SQLiteServiceAdapter

print("\n" + "=" * 70)
print("🔌 SQLite 适配器测试 - 验证系统接口实现")
print("=" * 70)

# 统计测试结果
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0
}

def run_test(test_name, test_func):
    """运行单个测试"""
    test_results['total'] += 1
    print(f"\n{'=' * 70}")
    print(f"🧪 {test_name}")
    print('=' * 70)
    
    try:
        asyncio.run(test_func())
        test_results['passed'] += 1
        print(f"\n✅ 测试通过")
        return True
    except Exception as e:
        test_results['failed'] += 1
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# 测试1: 适配器初始化
# ============================================================
async def test_adapter_initialization():
    """测试适配器的创建和初始化"""
    print("\n📝 创建适配器实例...")
    
    adapter = SQLiteServiceAdapter()
    print(f"✅ 适配器创建成功")
    
    # 验证适配器实现了所有必需的方法
    required_methods = [
        'get_child', 'save_child',
        'create_session', 'get_session', 'update_session',
        'save_weekly_plan', 'get_weekly_plan',
        'save_observation',
        'get_session_history'
    ]
    
    print(f"\n🔍 验证接口方法...")
    for method in required_methods:
        if hasattr(adapter, method):
            print(f"   ✅ {method}")
        else:
            raise Exception(f"缺少方法: {method}")
    
    print(f"\n✅ 所有接口方法都已实现")

# ============================================================
# 测试2: 孩子档案管理（通过适配器）
# ============================================================
async def test_child_profile_via_adapter():
    """测试通过适配器管理孩子档案"""
    print("\n📝 通过适配器保存孩子档案...")
    
    adapter = SQLiteServiceAdapter()
    
    # 保存档案
    child_data = {
        'child_id': 'adapter-test-child-001',
        'name': '测试小红',
        'age': 30,  # 2岁半
        'gender': '女',
        'diagnosis': 'ASD',
        'eye_contact': 4.0,
        'two_way_communication': 3.5,
        'emotional_expression': 5.0,
        'problem_solving': 4.5,
        'creative_thinking': 4.0,
        'logical_thinking': 4.5,
        'strengths': ['喜欢音乐', '模仿能力强'],
        'weaknesses': ['语言表达困难'],
        'interests': ['唱歌', '跳舞', '画画'],
        'focus_points': ['提升语言表达', '增加社交互动']
    }
    
    await adapter.save_child(child_data)
    print(f"✅ 档案已保存: {child_data['child_id']}")
    
    # 查询档案
    print(f"\n🔍 通过适配器查询档案...")
    profile = await adapter.get_child('adapter-test-child-001')
    
    if profile:
        print(f"✅ 查询成功:")
        print(f"   姓名: {profile['name']}")
        print(f"   年龄: {profile['age']} 月")
        print(f"   眼神接触: {profile['eye_contact']}")
        print(f"   优势: {profile['strengths']}")
    else:
        raise Exception("档案查询失败")

# ============================================================
# 测试3: 会话管理（通过适配器）
# ============================================================
async def test_session_management_via_adapter():
    """测试通过适配器管理会话"""
    print("\n📝 通过适配器创建会话...")
    
    adapter = SQLiteServiceAdapter()
    
    # 创建会话
    session_id = await adapter.create_session('adapter-test-child-001', 'game-001')
    print(f"✅ 会话已创建: {session_id}")
    
    # 查询会话
    print(f"\n🔍 通过适配器查询会话...")
    session = await adapter.get_session(session_id)
    
    if session:
        print(f"✅ 查询成功:")
        print(f"   会话ID: {session['session_id']}")
        print(f"   孩子ID: {session['child_id']}")
        print(f"   游戏ID: {session['game_id']}")
        print(f"   状态: {session['status']}")
    else:
        raise Exception("会话查询失败")
    
    # 更新会话
    print(f"\n📝 通过适配器更新会话...")
    await adapter.update_session(session_id, {
        'status': 'in_progress',
        'start_time': datetime.now().isoformat(),
        'game_name': '音乐互动游戏',
        'quick_observations': [
            {'type': 'smile', 'timestamp': datetime.now().isoformat()},
            {'type': 'eye_contact', 'timestamp': datetime.now().isoformat()}
        ]
    })
    
    # 验证更新
    updated_session = await adapter.get_session(session_id)
    if updated_session['status'] == 'in_progress':
        print(f"✅ 更新成功:")
        print(f"   状态: {updated_session['status']}")
        print(f"   游戏: {updated_session['game_name']}")
        print(f"   观察: {len(updated_session['quick_observations'])} 条")
    else:
        raise Exception("会话更新失败")

# ============================================================
# 测试4: 周计划管理（通过适配器）
# ============================================================
async def test_weekly_plan_via_adapter():
    """测试通过适配器管理周计划"""
    print("\n📝 通过适配器保存周计划...")
    
    adapter = SQLiteServiceAdapter()
    
    week_start = datetime.now()
    week_end = week_start + timedelta(days=7)
    
    plan_data = {
        'child_id': 'adapter-test-child-001',
        'week_start': week_start.isoformat(),
        'week_end': week_end.isoformat(),
        'weekly_goal': '提升语言表达和社交互动',
        'focus_dimensions': ['two_way_communication', 'emotional_expression'],
        'daily_plans': [
            {
                'day': 1,
                'game_id': 'game-music-001',
                'game_name': '音乐互动游戏',
                'goal': '跟唱3首儿歌',
                'difficulty': 'easy'
            },
            {
                'day': 2,
                'game_id': 'game-dance-001',
                'game_name': '舞蹈模仿游戏',
                'goal': '模仿5个动作',
                'difficulty': 'easy'
            }
        ],
        'status': 'active'
    }
    
    plan_id = await adapter.save_weekly_plan(plan_data)
    print(f"✅ 周计划已保存: {plan_id}")
    
    # 查询周计划
    print(f"\n🔍 通过适配器查询周计划...")
    plan = await adapter.get_weekly_plan(plan_id)
    
    if plan:
        print(f"✅ 查询成功:")
        print(f"   计划ID: {plan['plan_id']}")
        print(f"   周目标: {plan['weekly_goal']}")
        print(f"   每日计划: {len(plan['daily_plans'])} 天")
    else:
        raise Exception("周计划查询失败")

# ============================================================
# 测试5: 观察记录管理（通过适配器）
# ============================================================
async def test_observation_via_adapter():
    """测试通过适配器保存观察记录"""
    print("\n📝 通过适配器保存观察记录...")
    
    adapter = SQLiteServiceAdapter()
    
    # 创建一个会话用于测试
    session_id = await adapter.create_session('adapter-test-child-001', 'game-002')
    
    # 保存观察
    obs_id = await adapter.save_observation({
        'session_id': session_id,
        'child_id': 'adapter-test-child-001',
        'observation_type': 'quick',
        'timestamp': datetime.now().isoformat(),
        'content': '孩子跟着音乐拍手',
        'structured_data': {
            'type': 'imitation',
            'quality': 'good'
        }
    })
    
    print(f"✅ 观察记录已保存: {obs_id}")

# ============================================================
# 测试6: 会话历史查询（通过适配器）
# ============================================================
async def test_session_history_via_adapter():
    """测试通过适配器查询会话历史"""
    print("\n🔍 通过适配器查询会话历史...")
    
    adapter = SQLiteServiceAdapter()
    
    history = await adapter.get_session_history('adapter-test-child-001', limit=5)
    
    if history:
        print(f"✅ 查询成功: 找到 {len(history)} 条会话记录")
        for i, session in enumerate(history, 1):
            print(f"\n   会话 {i}:")
            print(f"      ID: {session['session_id']}")
            print(f"      游戏: {session.get('game_name', session['game_id'])}")
            print(f"      状态: {session['status']}")
    else:
        print("⚠️  未找到会话记录")

# ============================================================
# 测试7: 异步接口验证
# ============================================================
async def test_async_interface():
    """测试适配器的异步接口"""
    print("\n🔄 验证异步接口...")
    
    adapter = SQLiteServiceAdapter()
    
    # 并发执行多个操作
    print(f"\n📝 并发执行多个操作...")
    
    tasks = [
        adapter.get_child('adapter-test-child-001'),
        adapter.get_session_history('adapter-test-child-001', limit=3),
    ]
    
    results = await asyncio.gather(*tasks)
    
    print(f"✅ 并发操作完成:")
    print(f"   获取到孩子档案: {'是' if results[0] else '否'}")
    print(f"   获取到会话历史: {len(results[1])} 条")

# ============================================================
# 测试8: 接口兼容性验证
# ============================================================
async def test_interface_compatibility():
    """测试适配器与系统接口的兼容性"""
    print("\n🔍 验证接口兼容性...")
    
    adapter = SQLiteServiceAdapter()
    
    # 验证适配器是 ISQLiteService 的实例
    from src.interfaces.infrastructure import ISQLiteService
    
    if isinstance(adapter, ISQLiteService):
        print(f"✅ 适配器正确实现了 ISQLiteService 接口")
    else:
        raise Exception("适配器未正确实现 ISQLiteService 接口")
    
    # 验证所有方法都是异步的
    print(f"\n🔍 验证方法签名...")
    import inspect
    
    methods = [
        'get_child', 'save_child',
        'create_session', 'get_session', 'update_session',
        'save_weekly_plan', 'get_weekly_plan',
        'save_observation', 'get_session_history'
    ]
    
    for method_name in methods:
        method = getattr(adapter, method_name)
        if asyncio.iscoroutinefunction(method):
            print(f"   ✅ {method_name} 是异步方法")
        else:
            raise Exception(f"{method_name} 不是异步方法")
    
    print(f"\n✅ 所有方法都是异步的")

# ============================================================
# 运行所有测试
# ============================================================
print("\n" + "=" * 70)
print("🚀 开始测试")
print("=" * 70)

run_test("测试1: 适配器初始化", test_adapter_initialization)
run_test("测试2: 孩子档案管理（通过适配器）", test_child_profile_via_adapter)
run_test("测试3: 会话管理（通过适配器）", test_session_management_via_adapter)
run_test("测试4: 周计划管理（通过适配器）", test_weekly_plan_via_adapter)
run_test("测试5: 观察记录管理（通过适配器）", test_observation_via_adapter)
run_test("测试6: 会话历史查询（通过适配器）", test_session_history_via_adapter)
run_test("测试7: 异步接口验证", test_async_interface)
run_test("测试8: 接口兼容性验证", test_interface_compatibility)

# ============================================================
# 测试总结
# ============================================================
print("\n" + "=" * 70)
print("📊 测试总结")
print("=" * 70)
print(f"总计: {test_results['total']} 个测试")
print(f"✅ 通过: {test_results['passed']} 个")
print(f"❌ 失败: {test_results['failed']} 个")

if test_results['failed'] > 0:
    print(f"\n⚠️  有 {test_results['failed']} 个测试失败")
elif test_results['passed'] > 0:
    print(f"\n🎉 所有测试通过！")

print("\n" + "=" * 70)
print("💡 适配器说明")
print("=" * 70)
print("✅ 适配器已实现 ISQLiteService 接口")
print("✅ 所有方法都是异步的（async/await）")
print("✅ 同步实现自动转换为异步接口")
print("✅ 完全兼容系统接口规范")
print("\n" + "=" * 70)
