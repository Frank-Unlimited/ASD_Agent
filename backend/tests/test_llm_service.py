"""
测试 LLM 服务 - 支持多个供应商
"""
import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from services.real.llm_service import LLMFactory, get_llm_service


async def test_basic_chat(provider: str):
    """测试基础对话"""
    print(f"\n{'='*60}")
    print(f"测试 {provider.upper()} - 基础对话")
    print(f"{'='*60}")
    
    try:
        llm = LLMFactory.create(provider)
        
        response = await llm.chat_with_system(
            system_prompt="你是一个专业的 ASD 儿童干预助手。",
            user_message="请简单介绍一下地板时光疗法。",
            max_tokens=200
        )
        
        print(f"\n问题: 请简单介绍一下地板时光疗法。")
        print(f"\n回答:\n{response}")
        print(f"\n✅ {provider} 基础对话测试通过")
        
    except Exception as e:
        print(f"\n❌ {provider} 基础对话测试失败: {e}")


async def test_json_generation(provider: str):
    """测试 JSON 生成"""
    print(f"\n{'='*60}")
    print(f"测试 {provider.upper()} - JSON 生成")
    print(f"{'='*60}")
    
    try:
        llm = LLMFactory.create(provider)
        
        system_prompt = """
        你是一个 ASD 儿童评估专家。
        请根据用户提供的信息，生成孩子的画像。
        """
        
        user_message = """
        孩子信息：
        - 姓名：小明
        - 年龄：5岁
        - 诊断：ASD 中度
        - 主要问题：眼神接触少、语言发育迟缓
        - 兴趣：喜欢旋转物体、积木
        
        请生成包含以下字段的 JSON：
        {
            "name": "姓名",
            "age": 年龄,
            "strengths": ["优势1", "优势2"],
            "weaknesses": ["弱项1", "弱项2"],
            "interests": ["兴趣1", "兴趣2"]
        }
        """
        
        result = await llm.generate_json(
            system_prompt=system_prompt,
            user_message=user_message,
            max_tokens=500
        )
        
        print(f"\n生成的 JSON:")
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        if "parse_error" in result:
            print(f"\n⚠️ {provider} JSON 解析有问题，但返回了原始响应")
        else:
            print(f"\n✅ {provider} JSON 生成测试通过")
        
    except Exception as e:
        print(f"\n❌ {provider} JSON 生成测试失败: {e}")


async def test_conversation_history(provider: str):
    """测试带历史记录的对话"""
    print(f"\n{'='*60}")
    print(f"测试 {provider.upper()} - 历史对话")
    print(f"{'='*60}")
    
    try:
        llm = LLMFactory.create(provider)
        
        system_prompt = "你是一个友好的 ASD 干预助手。"
        
        # 第一轮对话
        history = []
        user_msg1 = "我的孩子5岁，刚诊断为ASD。"
        response1 = await llm.chat_with_history(
            system_prompt=system_prompt,
            conversation_history=history,
            user_message=user_msg1,
            max_tokens=150
        )
        
        print(f"\n用户: {user_msg1}")
        print(f"助手: {response1}")
        
        # 添加到历史
        history.append({"role": "user", "content": user_msg1})
        history.append({"role": "assistant", "content": response1})
        
        # 第二轮对话
        user_msg2 = "我应该从哪里开始干预？"
        response2 = await llm.chat_with_history(
            system_prompt=system_prompt,
            conversation_history=history,
            user_message=user_msg2,
            max_tokens=150
        )
        
        print(f"\n用户: {user_msg2}")
        print(f"助手: {response2}")
        
        print(f"\n✅ {provider} 历史对话测试通过")
        
    except Exception as e:
        print(f"\n❌ {provider} 历史对话测试失败: {e}")


async def test_all_providers():
    """测试所有配置的供应商"""
    print("\n" + "="*60)
    print("LLM 服务多供应商测试")
    print("="*60)
    
    # 从环境变量获取当前配置的供应商
    provider = os.getenv('AI_PROVIDER', 'deepseek').lower()
    print(f"\n当前配置的供应商: {provider}")
    
    # 测试当前供应商
    await test_basic_chat(provider)
    await test_json_generation(provider)
    await test_conversation_history(provider)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)
    print("\n提示: 要测试其他供应商，请修改 .env 文件中的 AI_PROVIDER")
    print("支持的供应商: deepseek, openai, gemini")


async def test_factory():
    """测试工厂模式"""
    print("\n" + "="*60)
    print("测试 LLM 工厂")
    print("="*60)
    
    # 测试工厂创建
    print("\n1. 测试工厂创建不同供应商:")
    
    providers_to_test = []
    
    # 检查哪些供应商已配置
    if os.getenv('DEEPSEEK_API_KEY'):
        providers_to_test.append('deepseek')
    if os.getenv('OPENAI_API_KEY'):
        providers_to_test.append('openai')
    if os.getenv('GEMINI_API_KEY'):
        providers_to_test.append('gemini')
    
    for provider in providers_to_test:
        try:
            llm = LLMFactory.create(provider)
            print(f"   ✅ {provider}: 创建成功")
        except Exception as e:
            print(f"   ❌ {provider}: 创建失败 - {e}")
    
    # 测试全局单例
    print("\n2. 测试全局单例:")
    llm1 = get_llm_service()
    llm2 = get_llm_service()
    print(f"   两次获取是同一个实例: {llm1 is llm2}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='测试 LLM 服务')
    parser.add_argument('--provider', type=str, help='指定测试的供应商 (deepseek, openai, gemini)')
    parser.add_argument('--test', type=str, choices=['basic', 'json', 'history', 'factory', 'all'], 
                       default='all', help='指定测试类型')
    
    args = parser.parse_args()
    
    # 如果指定了供应商，覆盖环境变量
    if args.provider:
        os.environ['AI_PROVIDER'] = args.provider
    
    # 运行测试
    if args.test == 'factory':
        asyncio.run(test_factory())
    elif args.test == 'all':
        asyncio.run(test_all_providers())
    else:
        provider = os.getenv('AI_PROVIDER', 'deepseek').lower()
        if args.test == 'basic':
            asyncio.run(test_basic_chat(provider))
        elif args.test == 'json':
            asyncio.run(test_json_generation(provider))
        elif args.test == 'history':
            asyncio.run(test_conversation_history(provider))
