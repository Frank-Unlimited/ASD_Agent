"""
测试真实业务服务（基于 LLM）
"""
import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 启用真实服务
os.environ['USE_REAL_ASSESSMENT'] = 'true'
os.environ['USE_REAL_CHAT'] = 'true'

from src.container import container, init_services


async def test_assessment_service():
    """测试评估服务"""
    print("\n" + "="*60)
    print("测试真实评估服务")
    print("="*60)
    
    assessment = container.get('assessment')
    print(f"服务名称: {assessment.get_service_name()}")
    print(f"服务版本: {assessment.get_service_version()}")
    
    # 测试构建画像
    print("\n1. 测试构建孩子画像:")
    parsed_data = {
        'name': '小明',
        'age': 5,
        'gender': 'male',
        'diagnosis': 'ASD',
        'severity': '中度',
        'report_summary': '孩子在社交互动方面存在明显困难，眼神接触少，语言发育迟缓。',
        'scale_results': 'CARS-2 总分: 35分（中度自闭症）',
        'interests': ['旋转物体', '积木', '水流']
    }
    
    portrait = await assessment.build_portrait(parsed_data)
    print(f"\n生成的画像:")
    import json
    print(json.dumps(portrait, ensure_ascii=False, indent=2))
    
    # 测试创建观察框架
    print("\n2. 测试创建观察框架:")
    framework = await assessment.create_observation_framework(portrait)
    print(f"\n观察框架:")
    print(json.dumps(framework, ensure_ascii=False, indent=2))
    
    print("\n✅ 评估服务测试完成")


async def test_chat_service():
    """测试对话助手服务"""
    print("\n" + "="*60)
    print("测试真实对话助手")
    print("="*60)
    
    chat = container.get('chat_assistant')
    print(f"服务名称: {chat.get_service_name()}")
    print(f"服务版本: {chat.get_service_version()}")
    
    # 测试路由
    print("\n1. 测试查询路由:")
    queries = [
        "你好，我想了解一下地板时光疗法",
        "有什么适合5岁孩子的游戏推荐吗？",
        "我的孩子今天不愿意和我互动，这是为什么？",
        "我想看看孩子最近的进展"
    ]
    
    for query in queries:
        route = await chat.route_query(query)
        print(f"   问题: {query}")
        print(f"   路由: {route}\n")
    
    # 测试对话
    print("\n2. 测试对话:")
    conversation_history = []
    
    # 第一轮
    user_msg1 = "我的孩子5岁，刚诊断为ASD中度，我应该怎么开始干预？"
    response1 = await chat.chat('child_001', user_msg1, conversation_history)
    print(f"\n用户: {user_msg1}")
    print(f"助手: {response1['response'][:200]}...")
    
    # 添加到历史
    conversation_history.append({'role': 'user', 'content': user_msg1})
    conversation_history.append({'role': 'assistant', 'content': response1['response']})
    
    # 第二轮
    user_msg2 = "具体应该怎么做呢？"
    response2 = await chat.chat('child_001', user_msg2, conversation_history)
    print(f"\n用户: {user_msg2}")
    print(f"助手: {response2['response'][:200]}...")
    
    print("\n✅ 对话助手测试完成")


async def test_integration():
    """测试服务集成"""
    print("\n" + "="*60)
    print("测试真实服务集成")
    print("="*60)
    
    # 模拟完整流程：评估 -> 对话咨询
    print("\n场景：家长完成初始评估后咨询干预建议\n")
    
    # 1. 评估
    assessment = container.get('assessment')
    parsed_data = {
        'name': '小红',
        'age': 4,
        'gender': 'female',
        'diagnosis': 'ASD',
        'severity': '轻度',
        'report_summary': '孩子在社交沟通方面有轻微困难，但对感兴趣的话题能够进行简单对话。',
        'scale_results': 'CARS-2 总分: 28分（轻度自闭症）',
        'interests': ['绘画', '音乐', '动物']
    }
    
    print("步骤1: 构建孩子画像...")
    portrait = await assessment.build_portrait(parsed_data)
    print(f"   优势: {portrait.get('strengths', [])[:2]}")
    print(f"   弱项: {portrait.get('weaknesses', [])[:2]}")
    
    # 2. 家长咨询
    chat = container.get('chat_assistant')
    
    print("\n步骤2: 家长咨询干预建议...")
    user_question = f"我的孩子{parsed_data['name']}，{parsed_data['age']}岁，{parsed_data['severity']}ASD。她喜欢{', '.join(parsed_data['interests'])}。我应该如何开始地板时光干预？"
    
    response = await chat.chat('child_002', user_question, [])
    print(f"\n   问题: {user_question}")
    print(f"\n   建议: {response['response'][:300]}...")
    
    print("\n✅ 集成测试完成")


async def main():
    """主测试函数"""
    print("="*60)
    print("真实业务服务测试（基于 LLM）")
    print("="*60)
    
    # 初始化服务
    print("\n初始化服务容器...")
    init_services()
    
    # 检查 LLM 是否可用
    if not container.has('llm'):
        print("\n❌ LLM 服务未配置，无法测试真实业务服务")
        print("请在 .env 文件中配置 DEEPSEEK_API_KEY 或其他 LLM API 密钥")
        return
    
    # 运行测试
    await test_assessment_service()
    await test_chat_service()
    await test_integration()
    
    print("\n" + "="*60)
    print("所有测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
