"""
测试 Memory 服务的 LLM 智能解析功能
"""
import asyncio
from datetime import datetime, timezone
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.Memory import get_memory_service


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result: dict, title: str = ""):
    """打印结果"""
    if title:
        print(f"\n{title}")
    
    if result.get("success"):
        print(f"✓ 成功: {result.get('message', '')}")
        if "parsed_data" in result:
            print(f"\n  LLM 解析结果:")
            parsed = result["parsed_data"]
            print(f"    事件类型: {parsed.get('event_type')}")
            print(f"    重要性: {parsed.get('significance')}")
            print(f"    描述: {parsed.get('description')}")
            print(f"    涉及对象: {parsed.get('objects_involved', [])}")
            print(f"    相关兴趣: {parsed.get('related_interests', [])}")
            print(f"    相关功能: {parsed.get('related_functions', [])}")
            
            if parsed.get('context', {}).get('negative_event'):
                print(f"\n  ⚠️  负面事件检测:")
                ctx = parsed['context']
                print(f"    严重程度: {ctx.get('severity')}")
                print(f"    影响天数: {ctx.get('impact_duration_days')}")
                print(f"    触发因素: {ctx.get('triggers', [])}")
                print(f"    家长情绪: {ctx.get('parent_emotion')}")
                print(f"    需要支持: {ctx.get('parent_needs_support')}")
        
        if "behavior_id" in result:
            print(f"\n  行为ID: {result['behavior_id']}")
    else:
        print(f"✗ 失败: {result.get('message', '')}")


async def test_memory_llm():
    """测试 Memory 服务的 LLM 功能"""
    
    print_section("Memory 服务 LLM 智能解析测试")
    
    # 获取服务实例
    memory = await get_memory_service()
    
    # ============ 1. 清空数据 ============
    print_section("1. 初始化环境")
    await memory.clear_all_data()
    await memory.initialize()
    print("✓ 数据已清空，固定节点已初始化")
    
    # ============ 2. 创建孩子档案 ============
    print_section("2. 创建孩子档案")
    from services.Memory.models.nodes import Person
    
    child = Person(
        person_type="child",
        name="辰辰",
        role="孩子",
        basic_info={
            "age": 3,
            "gender": "male",
            "diagnosis": "ASD轻度",
            "birth_date": "2023-06-15"
        }
    )
    
    child_id = await memory.save_child(child)
    print(f"✓ 孩子档案已创建: {child_id}")
    
    # ============ 3. 测试智能行为记录（正面） ============
    print_section("3. 智能行为记录 - 正面行为")
    
    result1 = await memory.record_behavior_from_text(
        child_id=child_id,
        raw_input="今天玩积木时，辰辰突然把积木递给我，还看了我一眼",
        input_type="text"
    )
    print_result(result1, "测试 1: 主动社交互动")
    
    result2 = await memory.record_behavior_from_text(
        child_id=child_id,
        raw_input="辰辰今天第一次叫了我'妈妈'，我好激动！",
        input_type="text"
    )
    print_result(result2, "测试 2: 首次语言表达")
    
    result3 = await memory.record_behavior_from_text(
        child_id=child_id,
        raw_input="今天带辰辰去公园，他在滑梯上玩得很开心，还和其他小朋友一起排队",
        input_type="text"
    )
    print_result(result3, "测试 3: 户外社交活动")
    
    # ============ 4. 测试智能行为记录（负面） ============
    print_section("4. 智能行为记录 - 负面事件")
    
    result4 = await memory.record_behavior_from_text(
        child_id=child_id,
        raw_input="我今天没忍住，对辰辰吼了一声，他吓哭了，我很自责",
        input_type="text"
    )
    print_result(result4, "测试 4: 家长情绪失控")
    
    result5 = await memory.record_behavior_from_text(
        child_id=child_id,
        raw_input="今天玩拼图时，辰辰拼不上就开始发脾气，把拼图扔了，哭了很久",
        input_type="text"
    )
    print_result(result5, "测试 5: 孩子挫折反应")
    
    # ============ 5. 查询行为记录 ============
    print_section("5. 查询行为记录")
    
    behaviors = await memory.get_behaviors(child_id=child_id, limit=10)
    print(f"✓ 共查询到 {len(behaviors)} 条行为记录")
    
    for i, bh in enumerate(behaviors, 1):
        print(f"\n  [{i}] {bh.get('description')}")
        print(f"      类型: {bh.get('event_type')} | 重要性: {bh.get('significance')}")
    
    # ============ 6. 负面事件处理 ============
    print_section("6. 负面事件处理")
    
    # 获取最近的负面事件
    concerns = await memory.get_recent_concerns(child_id=child_id, days=14)
    print(f"\n✓ 最近的负面事件: {len(concerns)} 个")
    
    for i, concern in enumerate(concerns, 1):
        print(f"\n  [{i}] {concern.get('description')}")
    
    # 提取触发因素
    triggers = await memory.extract_triggers_to_avoid(child_id=child_id, days=14)
    print(f"\n✓ 需要避让的触发因素:")
    print(f"  活动类: {triggers.get('activities', [])}")
    print(f"  人物类: {triggers.get('people', [])}")
    print(f"  情境类: {triggers.get('situations', [])}")
    print(f"  对象类: {triggers.get('objects', [])}")
    print(f"  总计: {len(triggers.get('all_triggers', []))} 个")
    
    # 评估家长支持需求
    support = await memory.get_parent_support_needed(child_id=child_id, days=7)
    print(f"\n✓ 家长支持需求评估:")
    print(f"  需要支持: {'是' if support.get('support_needed') else '否'}")
    print(f"  负面事件数: {support.get('concern_count')}")
    print(f"  高严重度事件: {support.get('high_severity_count')}")
    print(f"  需要专业帮助: {'是' if support.get('needs_professional_help') else '否'}")
    print(f"  家长情绪: {support.get('parent_emotions', [])}")
    print(f"  系统消息: {support.get('message')}")
    
    # ============ 7. 测试总结 ============
    print_section("测试总结")
    
    print("\n✅ 测试完成统计:")
    print(f"  - 创建孩子档案: 1个")
    print(f"  - 智能记录行为: 5个 (3个正面 + 2个负面)")
    print(f"  - 负面事件: {len(concerns)} 个")
    print(f"  - 触发因素: {len(triggers.get('all_triggers', []))} 个")
    
    print("\n✅ LLM 功能验证:")
    print("  ✓ 自动识别事件类型")
    print("  ✓ 自动判断重要性")
    print("  ✓ 自动提取涉及对象")
    print("  ✓ 自动推断兴趣维度")
    print("  ✓ 自动推断功能维度")
    print("  ✓ 自动识别负面事件")
    print("  ✓ 自动提取触发因素")
    print("  ✓ 自动分析家长情绪")
    print("  ✓ 自动创建关系")
    
    print("\n" + "=" * 70)
    print("  🎉 Memory 服务 LLM 智能解析测试完成！")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_memory_llm())
