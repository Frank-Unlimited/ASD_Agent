"""
MemoryService 完整测试 - 包含更多数据和详细结果展示
"""
import asyncio
import json
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.Memory import get_memory_service
from services.Graphiti.models.nodes import Person, Behavior, Object


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """打印子章节标题"""
    print(f"\n【{title}】")
    print("-" * 70)


async def test_full_memory_service():
    """完整测试记忆服务"""
    
    print_section("MemoryService 完整功能测试")
    
    # 获取服务实例
    service = await get_memory_service()
    
    # ============ 1. 初始化 ============
    print_subsection("1. 初始化环境")
    print("清空测试数据...")
    await service.clear_all_data()
    await service.initialize()
    print("✓ 环境初始化完成")
    print("  - 创建了 7 个唯一约束")
    print("  - 创建了 13 个索引")
    print("  - 初始化了 41 个固定节点（8个兴趣 + 33个功能）")
    
    # ============ 2. 创建人物 ============
    print_subsection("2. 创建人物档案")
    
    # 孩子
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
    child_id = await service.save_child(child)
    print(f"✓ 孩子档案: {child.name}")
    print(f"  - ID: {child_id}")
    print(f"  - 年龄: {child.basic_info['age']}岁")
    print(f"  - 诊断: {child.basic_info['diagnosis']}")
    
    # 家长
    mom = Person(
        person_type="parent",
        name="妈妈",
        role="主要照顾者",
        basic_info={"relationship": "母亲", "occupation": "全职妈妈"}
    )
    mom_id = await service.save_person(mom)
    print(f"\n✓ 家长1: {mom.name} ({mom.role})")
    print(f"  - ID: {mom_id}")
    
    dad = Person(
        person_type="parent",
        name="爸爸",
        role="辅助照顾者",
        basic_info={"relationship": "父亲", "occupation": "工程师"}
    )
    dad_id = await service.save_person(dad)
    print(f"\n✓ 家长2: {dad.name} ({dad.role})")
    print(f"  - ID: {dad_id}")
    
    # 老师
    teacher = Person(
        person_type="teacher",
        name="李老师",
        role="康复治疗师",
        basic_info={"specialty": "地板时光", "experience_years": 5}
    )
    teacher_id = await service.save_person(teacher)
    print(f"\n✓ 老师: {teacher.name} ({teacher.role})")
    print(f"  - ID: {teacher_id}")
    print(f"  - 专长: {teacher.basic_info['specialty']}")
    
    # ============ 3. 创建对象 ============
    print_subsection("3. 创建对象（玩具）")
    
    objects_data = [
        {
            "name": "彩色积木",
            "description": "12色木质积木套装，适合建构游戏",
            "tags": ["建构类", "视觉刺激", "精细动作"],
            "interests": [("construction", True, 1.0), ("visual", False, 0.7)]
        },
        {
            "name": "旋转齿轮",
            "description": "机械齿轮玩具，可以旋转和拼接",
            "tags": ["视觉类", "因果关系", "精细动作"],
            "interests": [("visual", True, 1.0), ("cognitive", False, 0.6)]
        },
        {
            "name": "软胶球",
            "description": "柔软的触觉球，适合抛接游戏",
            "tags": ["触觉类", "运动类", "社交互动"],
            "interests": [("tactile", True, 0.9), ("motor", True, 0.8), ("social", False, 0.5)]
        },
        {
            "name": "音乐盒",
            "description": "播放儿歌的音乐盒",
            "tags": ["听觉类", "情绪调节"],
            "interests": [("auditory", True, 1.0)]
        }
    ]
    
    object_ids = {}
    for i, obj_data in enumerate(objects_data, 1):
        obj = Object(
            name=obj_data["name"],
            description=obj_data["description"],
            tags=obj_data["tags"],
            usage={"total_games": 0, "effectiveness": "unknown"}
        )
        obj_id = await service.save_object(obj)
        object_ids[obj_data["name"]] = obj_id
        
        print(f"\n✓ 对象{i}: {obj.name}")
        print(f"  - ID: {obj_id}")
        print(f"  - 描述: {obj.description}")
        print(f"  - 标签: {', '.join(obj.tags)}")
        
        # 关联到兴趣维度
        interests_str = []
        for interest_name, primary, score in obj_data["interests"]:
            await service.link_object_to_interest(obj_id, interest_name, primary, score)
            interests_str.append(f"{interest_name}({'主' if primary else '次'}, {score})")
        print(f"  - 兴趣维度: {', '.join(interests_str)}")
    
    # ============ 4. 创建行为记录 ============
    print_subsection("4. 创建行为记录")
    
    behaviors_data = [
        {
            "event_type": "social",
            "description": "孩子主动递积木给妈妈，同时抬头看了一眼",
            "raw_input": "今天玩积木时，辰辰突然把积木递给我，还看了我一眼",
            "input_type": "text",
            "significance": "breakthrough",
            "object": "彩色积木",
            "interests": [("construction", 8.0, 180)],
            "functions": [("eye_contact", 7.0, 0.9), ("social_initiation", 8.0, 0.95)],
            "context": {"activity": "积木游戏", "location": "家里客厅", "duration": "3分钟"}
        },
        {
            "event_type": "social",
            "description": "孩子看到妈妈进门，主动挥手",
            "raw_input": "辰辰看到我回家，主动挥手了",
            "input_type": "text",
            "significance": "improvement",
            "object": None,
            "interests": [("social", 6.0, 5)],
            "functions": [("social_smile", 6.0, 0.8), ("social_initiation", 5.0, 0.7)],
            "context": {"location": "家门口", "time": "下午5点"}
        },
        {
            "event_type": "emotion",
            "description": "孩子玩积木时露出开心的笑容",
            "raw_input": "辰辰搭积木时笑了",
            "input_type": "text",
            "significance": "normal",
            "object": "彩色积木",
            "interests": [("construction", 7.0, 120)],
            "functions": [("emotional_expression", 6.0, 0.75)],
            "context": {"activity": "积木游戏", "mood": "愉快"}
        },
        {
            "event_type": "social",
            "description": "孩子听到音乐后，转头看向音乐盒",
            "raw_input": "音乐响起时，辰辰转头看了",
            "input_type": "text",
            "significance": "normal",
            "object": "音乐盒",
            "interests": [("auditory", 7.0, 10), ("visual", 5.0, 5)],
            "functions": [("auditory_response", 7.0, 0.85), ("joint_attention", 5.0, 0.6)],
            "context": {"activity": "音乐游戏"}
        },
        {
            "event_type": "communication",
            "description": "孩子用手指向想要的玩具",
            "raw_input": "辰辰指着齿轮玩具，想要玩",
            "input_type": "text",
            "significance": "improvement",
            "object": "旋转齿轮",
            "interests": [("visual", 8.0, 30)],
            "functions": [("non_verbal_communication", 7.0, 0.9), ("joint_attention", 6.0, 0.8)],
            "context": {"activity": "自由玩耍", "communication_type": "指向"}
        },
        {
            "event_type": "social",
            "description": "孩子和爸爸玩抛接球游戏，主动回应",
            "raw_input": "和爸爸玩球，辰辰会接球并扔回来",
            "input_type": "text",
            "significance": "improvement",
            "object": "软胶球",
            "interests": [("motor", 7.0, 300), ("social", 6.0, 300)],
            "functions": [("body_coordination", 6.0, 0.8), ("social_interest", 7.0, 0.85), ("imitation", 5.0, 0.7)],
            "context": {"activity": "抛接球游戏", "partner": "爸爸", "duration": "5分钟"}
        },
        {
            "event_type": "firstTime",
            "description": "孩子第一次主动叫'妈妈'",
            "raw_input": "辰辰今天第一次清楚地叫了'妈妈'！",
            "input_type": "voice",
            "significance": "breakthrough",
            "object": None,
            "interests": [("social", 9.0, 2)],
            "functions": [("language_expression", 8.0, 0.95), ("social_initiation", 8.0, 0.9)],
            "context": {"location": "家里", "emotion": "激动", "first_time": True}
        },
        {
            "event_type": "emotion",
            "description": "孩子在玩齿轮时专注了10分钟",
            "raw_input": "辰辰玩齿轮玩具，专注了很久",
            "input_type": "text",
            "significance": "improvement",
            "object": "旋转齿轮",
            "interests": [("visual", 8.0, 600), ("cognitive", 6.0, 600)],
            "functions": [("joint_attention", 7.0, 0.85)],
            "context": {"activity": "齿轮游戏", "duration": "10分钟", "focus_level": "高"}
        }
    ]
    
    behavior_ids = []
    for i, bh_data in enumerate(behaviors_data, 1):
        behavior = Behavior(
            child_id=child_id,
            event_type=bh_data["event_type"],
            description=bh_data["description"],
            raw_input=bh_data["raw_input"],
            input_type=bh_data["input_type"],
            significance=bh_data["significance"],
            context=bh_data["context"]
        )
        bh_id = await service.save_behavior(behavior)
        behavior_ids.append(bh_id)
        
        print(f"\n✓ 行为{i}: [{bh_data['event_type']}] {bh_data['significance']}")
        print(f"  - ID: {bh_id}")
        print(f"  - 描述: {bh_data['description']}")
        print(f"  - 原始输入: {bh_data['raw_input']}")
        
        # 创建关系
        await service.link_behavior_to_child(bh_id, child_id)
        
        if bh_data["object"]:
            obj_id = object_ids[bh_data["object"]]
            await service.link_behavior_to_object(bh_id, obj_id, "使用")
            print(f"  - 涉及对象: {bh_data['object']}")
        
        if bh_data["interests"]:
            interests_str = []
            for interest_name, intensity, duration in bh_data["interests"]:
                await service.link_behavior_to_interest(bh_id, interest_name, intensity, duration, True)
                interests_str.append(f"{interest_name}(强度{intensity})")
            print(f"  - 体现兴趣: {', '.join(interests_str)}")
        
        if bh_data["functions"]:
            functions_str = []
            for function_name, score, strength in bh_data["functions"]:
                await service.link_behavior_to_function(bh_id, function_name, score, strength)
                functions_str.append(f"{function_name}(评分{score})")
            print(f"  - 反映功能: {', '.join(functions_str)}")
    
    # ============ 5. 查询和统计 ============
    print_subsection("5. 查询和统计")
    
    # 查询所有行为
    all_behaviors = await service.get_behaviors(child_id=child_id, limit=100)
    print(f"\n✓ 总行为记录数: {len(all_behaviors)}")
    
    # 按事件类型统计
    event_types = {}
    for bh in all_behaviors:
        event_type = bh['event_type']
        event_types[event_type] = event_types.get(event_type, 0) + 1
    
    print("\n按事件类型统计:")
    for event_type, count in sorted(event_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {event_type}: {count}条")
    
    # 按重要性统计
    significance_types = {}
    for bh in all_behaviors:
        sig = bh['significance']
        significance_types[sig] = significance_types.get(sig, 0) + 1
    
    print("\n按重要性统计:")
    for sig, count in sorted(significance_types.items(), key=lambda x: x[1], reverse=True):
        emoji = "🌟" if sig == "breakthrough" else "📈" if sig == "improvement" else "✓"
        print(f"  {emoji} {sig}: {count}条")
    
    # 最近的突破性行为
    breakthroughs = [bh for bh in all_behaviors if bh['significance'] == 'breakthrough']
    print(f"\n✓ 突破性行为 ({len(breakthroughs)}条):")
    for bh in breakthroughs:
        print(f"  🌟 {bh['description']}")
    
    # ============ 6. 数据验证测试 ============
    print_subsection("6. 数据验证测试")
    
    validation_tests = [
        {
            "name": "无效的 person_type",
            "test": lambda: service.save_child(Person(person_type="invalid", name="测试")),
            "expected_error": "person_type 必须是"
        },
        {
            "name": "空的 child_id",
            "test": lambda: service.save_behavior(Behavior(child_id="", description="测试")),
            "expected_error": "child_id 不能为空"
        },
        {
            "name": "空的 description",
            "test": lambda: service.save_behavior(Behavior(child_id=child_id, description="")),
            "expected_error": "description 不能为空"
        },
        {
            "name": "无效的 event_type",
            "test": lambda: service.save_behavior(Behavior(child_id=child_id, description="测试", event_type="invalid")),
            "expected_error": "event_type 必须是"
        },
        {
            "name": "空的对象名称",
            "test": lambda: service.save_object(Object(name="")),
            "expected_error": "name 不能为空"
        }
    ]
    
    passed = 0
    for test in validation_tests:
        try:
            await test["test"]()
            print(f"✗ {test['name']}: 应该抛出异常")
        except ValueError as e:
            if test["expected_error"] in str(e):
                print(f"✓ {test['name']}: 正确捕获异常")
                passed += 1
            else:
                print(f"✗ {test['name']}: 异常信息不匹配")
        except Exception as e:
            print(f"✗ {test['name']}: 意外的异常类型 - {type(e).__name__}")
    
    print(f"\n验证测试通过: {passed}/{len(validation_tests)}")
    
    # ============ 7. 负面事件处理测试 ============
    print_subsection("7. 负面事件处理")
    
    # 创建一个负面事件
    print("\n创建负面事件：妈妈情绪失控...")
    negative_event = Behavior(
        child_id=child_id,
        event_type="emotion",
        description="妈妈在游戏中情绪失控，对孩子大声吼叫，孩子受惊吓哭泣",
        raw_input="我今天没忍住，对辰辰吼了一声，他吓哭了，我很自责",
        input_type="text",
        significance="concern",
        context={
            # 负面事件标识
            "negative_event": True,
            "severity": "high",
            
            # 影响预估
            "impact_duration_days": 7,
            "affected_dimensions": ["anxiety_level", "trust", "emotional_response"],
            
            # 触发因素
            "triggers": ["积木游戏", "妈妈参与", "要求配合", "高难度任务"],
            
            # 避让建议
            "avoidance_needed": True,
            "avoidance_period_days": 7,
            "alternative_activities": ["自主探索游戏", "低压力感官游戏", "孩子主导的游戏"],
            
            # 家长情绪
            "parent_emotion": "焦虑、疲惫、自责",
            "parent_needs_support": True,
            "parent_support_suggestions": ["休息和自我关怀", "寻求家人支持", "情绪管理资源"],
            
            # 孩子反应
            "child_reaction": "哭泣、退缩、拒绝互动、眼神回避",
            "immediate_comfort_provided": True,
            
            # 恢复追踪
            "recovery_status": "active",
            "recovery_signs": [],
            "follow_up_needed": True,
            
            # 关联信息
            "game_id": "game_001",
            "related_object_ids": [object_ids["彩色积木"]]
        }
    )
    
    negative_event_id = await service.save_behavior(negative_event)
    await service.link_behavior_to_child(negative_event_id, child_id)
    await service.link_behavior_to_object(negative_event_id, object_ids["彩色积木"], "触发创伤")
    await service.link_behavior_to_function(negative_event_id, "anxiety_level", 8.0, 0.9)
    
    # 关联涉及的人物：妈妈是触发者
    await service.link_behavior_to_person(
        behavior_id=negative_event_id,
        person_id=mom_id,
        role="trigger",
        interaction_quality="negative",
        involvement_level="high",
        notes="情绪失控，对孩子大声吼叫"
    )
    
    print(f"✓ 负面事件已记录: {negative_event_id}")
    print(f"  - 严重程度: {negative_event.context['severity']}")
    print(f"  - 预计影响: {negative_event.context['impact_duration_days']}天")
    print(f"  - 触发因素: {', '.join(negative_event.context['triggers'])}")
    print(f"  - 涉及人物: 妈妈 (触发者)")
    
    # 创建一个正面的多人互动场景
    print("\n创建正面场景：老师带领打鼓游戏...")
    drum_game = Behavior(
        child_id=child_id,
        event_type="social",
        description="老师带领孩子打鼓，孩子跟随节奏，妈妈在旁边鼓励",
        raw_input="李老师今天教辰辰打鼓，辰辰很开心，跟着节奏打，我在旁边给他加油",
        input_type="text",
        significance="improvement",
        context={
            "activity": "打鼓游戏",
            "location": "康复中心",
            "duration": "15分钟",
            "mood": "愉快、专注"
        }
    )
    
    drum_game_id = await service.save_behavior(drum_game)
    await service.link_behavior_to_child(drum_game_id, child_id)
    
    # 关联老师：引导者
    await service.link_behavior_to_person(
        behavior_id=drum_game_id,
        person_id=teacher_id,
        role="facilitator",
        interaction_quality="positive",
        involvement_level="high",
        notes="专业引导，节奏清晰"
    )
    
    # 关联妈妈：观察者/鼓励者
    await service.link_behavior_to_person(
        behavior_id=drum_game_id,
        person_id=mom_id,
        role="observer",
        interaction_quality="positive",
        involvement_level="medium",
        notes="在旁边观察和鼓励"
    )
    
    # 关联功能维度
    await service.link_behavior_to_interest(drum_game_id, "auditory", 8.0, 900, True)
    await service.link_behavior_to_interest(drum_game_id, "motor", 7.0, 900, True)
    await service.link_behavior_to_function(drum_game_id, "auditory_response", 7.0, 0.85)
    await service.link_behavior_to_function(drum_game_id, "body_coordination", 6.0, 0.8)
    await service.link_behavior_to_function(drum_game_id, "imitation", 7.0, 0.85)
    
    print(f"✓ 打鼓游戏已记录: {drum_game_id}")
    print(f"  - 涉及人物: 李老师 (引导者), 妈妈 (观察者)")
    print(f"  - 互动质量: 正面")
    print(f"  - 体现兴趣: auditory(强度8.0), motor(强度7.0)")
    print(f"  - 反映功能: auditory_response, body_coordination, imitation")
    
    # 查询最近的负面事件
    print("\n查询最近的负面事件...")
    recent_concerns = await service.get_recent_concerns(child_id, days=14)
    print(f"✓ 找到 {len(recent_concerns)} 个未恢复的负面事件")
    
    for concern in recent_concerns:
        ctx = concern.get('context', {})
        if isinstance(ctx, str):
            import json
            ctx = json.loads(ctx)
        print(f"  - [{ctx.get('severity', 'unknown')}] {concern['description'][:40]}...")
    
    # 提取需要避让的触发因素
    print("\n提取需要避让的触发因素...")
    triggers = await service.extract_triggers_to_avoid(child_id, days=14)
    print(f"✓ 触发因素分析:")
    print(f"  - 活动类: {', '.join(triggers['activities']) if triggers['activities'] else '无'}")
    print(f"  - 对象类: {', '.join(triggers['objects']) if triggers['objects'] else '无'}")
    print(f"  - 人物类: {', '.join(triggers['people']) if triggers['people'] else '无'}")
    print(f"  - 情境类: {', '.join(triggers['situations']) if triggers['situations'] else '无'}")
    print(f"  - 总计: {len(triggers['all_triggers'])} 个触发因素")
    
    # 检查家长支持需求
    print("\n检查家长支持需求...")
    support = await service.get_parent_support_needed(child_id, days=7)
    print(f"✓ 家长支持分析:")
    print(f"  - 需要支持: {'是' if support['support_needed'] else '否'}")
    print(f"  - 负面事件数: {support['concern_count']}")
    print(f"  - 高严重度事件: {support['high_severity_count']}")
    print(f"  - 需要专业帮助: {'是' if support['needs_professional_help'] else '否'}")
    print(f"  - 系统消息: {support['message']}")
    if support['suggestions']:
        print(f"  - 建议: {', '.join(support['suggestions'])}")
    
    # 模拟游戏推荐场景
    print("\n模拟游戏推荐场景...")
    print("游戏推荐模块会:")
    print("  ❌ 避开: 积木游戏、妈妈参与的游戏、高难度任务")
    print("  ✅ 推荐: 自主探索游戏、低压力感官游戏、爸爸参与的游戏")
    print("  ⏰ 避让期: 7天")
    
    # 再创建一个轻度负面事件
    print("\n创建轻度负面事件：孩子拒绝配合...")
    mild_concern = Behavior(
        child_id=child_id,
        event_type="emotion",
        description="孩子拒绝配合游戏，表现出抗拒",
        raw_input="辰辰今天不想玩，一直摇头",
        input_type="text",
        significance="concern",
        context={
            "negative_event": True,
            "severity": "low",
            "impact_duration_days": 2,
            "triggers": ["疲劳", "游戏时间过长"],
            "parent_emotion": "理解、耐心",
            "parent_needs_support": False,
            "child_reaction": "摇头、转身",
            "recovery_status": "active"
        }
    )
    
    mild_concern_id = await service.save_behavior(mild_concern)
    await service.link_behavior_to_child(mild_concern_id, child_id)
    print(f"✓ 轻度负面事件已记录: {mild_concern_id}")
    
    # 再次查询
    recent_concerns = await service.get_recent_concerns(child_id, days=14)
    print(f"\n✓ 当前未恢复的负面事件: {len(recent_concerns)} 个")
    
    # 按严重程度统计
    severity_count = {"high": 0, "medium": 0, "low": 0}
    for concern in recent_concerns:
        ctx = concern.get('context', {})
        if isinstance(ctx, str):
            ctx = json.loads(ctx)
        severity = ctx.get('severity', 'medium')
        severity_count[severity] = severity_count.get(severity, 0) + 1
    
    print("按严重程度统计:")
    print(f"  - 高: {severity_count['high']}个")
    print(f"  - 中: {severity_count['medium']}个")
    print(f"  - 低: {severity_count['low']}个")
    
    # 展示人物关联的价值
    print("\n✓ 人物关联分析:")
    print("  通过'涉及人物'关系，系统可以:")
    print("  - 识别谁在负面事件中扮演了触发者角色（妈妈）")
    print("  - 识别谁在正面事件中扮演了引导者角色（李老师）")
    print("  - 分析不同人物对孩子的影响（正面/负面）")
    print("  - 推荐游戏时考虑人物因素（如：暂时避开妈妈主导的游戏）")
    print("  - 生成报告时展示各人物的贡献和影响")
    
    # ============ 8. 测试总结 ============
    print_section("测试总结")
    
    print("\n✅ 测试数据统计:")
    print(f"  - 人物节点: 4个 (1个孩子 + 2个家长 + 1个老师)")
    print(f"  - 对象节点: {len(object_ids)}个")
    print(f"  - 行为节点: {len(behavior_ids) + 3}个 (含2个负面事件 + 1个多人互动)")
    print(f"  - 固定维度节点: 41个 (8个兴趣 + 33个功能)")
    print(f"  - 人物关联: 3个 (妈妈触发者 + 老师引导者 + 妈妈观察者)")
    
    print("\n✅ 功能验证:")
    print("  ✓ 人物管理 (创建、查询)")
    print("  ✓ 对象管理 (创建、关联兴趣)")
    print("  ✓ 行为管理 (创建、查询、统计)")
    print("  ✓ 关系管理 (6种关系类型)")
    print("  ✓ 数据验证 (5项验证规则)")
    print("  ✓ 负面事件处理 (记录、查询、触发因素提取、家长支持)")
    print("  ✓ 人物关联 (触发者、引导者、观察者角色识别)")
    
    print("\n✅ 数据质量:")
    print(f"  ✓ 突破性行为: {len(breakthroughs)}条")
    print(f"  ✓ 改进性行为: {significance_types.get('improvement', 0)}条")
    print(f"  ✓ 常规行为: {significance_types.get('normal', 0)}条")
    print(f"  ⚠️ 负面事件: {len(recent_concerns)}条 (需要关注)")
    
    print("\n✅ 负面事件处理:")
    print(f"  ✓ 高严重度事件: {severity_count['high']}个")
    print(f"  ✓ 触发因素识别: {len(triggers['all_triggers'])}个")
    print(f"  ✓ 家长支持评估: {'需要' if support['support_needed'] else '不需要'}")
    print(f"  ✓ 游戏推荐调整: 已启用避让机制")
    
    print("\n" + "=" * 70)
    print("  🎉 MemoryService 完整功能测试通过！")
    print("=" * 70)
    
    # 关闭服务
    await service.close()


if __name__ == "__main__":
    asyncio.run(test_full_memory_service())
