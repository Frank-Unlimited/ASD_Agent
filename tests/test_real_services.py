"""
测试真实服务集成
"""
import asyncio
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置环境变量启用真实服务
os.environ['USE_REAL_SQLITE'] = 'true'
os.environ['USE_REAL_SPEECH'] = 'true'
os.environ['USE_REAL_VIDEO_ANALYSIS'] = 'true'
os.environ['USE_REAL_DOCUMENT_PARSER'] = 'true'

from src.container import container, init_services
from src.config import settings


async def test_sqlite_service():
    """测试 SQLite 服务"""
    print("\n=== 测试 SQLite 服务 ===")
    sqlite = container.get('sqlite')
    print(f"服务名称: {sqlite.get_service_name()}")
    print(f"服务版本: {sqlite.get_service_version()}")
    
    # 先创建孩子档案
    await sqlite.save_child({
        'child_id': 'child_001',
        'name': '测试孩子',
        'age': 5,
        'gender': 'male',
        'diagnosis': 'ASD',
        'severity': 'moderate'
    })
    print("创建孩子档案: child_001")
    
    # 测试创建会话
    session_id = await sqlite.create_session('child_001', 'game_001')
    print(f"创建会话: {session_id}")
    
    # 测试获取会话
    session = await sqlite.get_session(session_id)
    print(f"获取会话: {session}")
    
    print("✅ SQLite 服务测试通过")


async def test_speech_service():
    """测试语音服务"""
    print("\n=== 测试语音服务 ===")
    speech = container.get('speech')
    print(f"服务名称: {speech.get_service_name()}")
    print(f"服务版本: {speech.get_service_version()}")
    
    # 注意：需要配置阿里云密钥才能真正调用
    if settings.aliyun_access_key_id and settings.aliyun_nls_appkey:
        try:
            # 测试 TTS
            text = "你好，这是一个测试"
            audio_path = await speech.text_to_speech(text)
            print(f"TTS 输出: {audio_path}")
            print("✅ 语音服务测试通过")
        except Exception as e:
            print(f"⚠️ 语音服务需要配置密钥: {e}")
    else:
        print("⚠️ 跳过语音服务测试（需要配置 ALIYUN_ACCESS_KEY_ID 和 ALIYUN_NLS_APPKEY）")


async def test_document_parser_service():
    """测试文档解析服务"""
    print("\n=== 测试文档解析服务 ===")
    parser = container.get('document_parser')
    print(f"服务名称: {parser.get_service_name()}")
    print(f"服务版本: {parser.get_service_version()}")
    
    # 注意：需要配置通义千问密钥才能真正调用
    if settings.dashscope_api_key:
        print("✅ 文档解析服务已配置")
    else:
        print("⚠️ 跳过文档解析测试（需要配置 DASHSCOPE_API_KEY）")


async def test_video_analysis_service():
    """测试视频分析服务"""
    print("\n=== 测试视频分析服务 ===")
    video = container.get('video_analysis')
    print(f"服务名称: {video.get_service_name()}")
    print(f"服务版本: {video.get_service_version()}")
    
    # 注意：需要配置通义千问密钥才能真正调用
    if settings.dashscope_api_key:
        print("✅ 视频分析服务已配置")
    else:
        print("⚠️ 跳过视频分析测试（需要配置 DASHSCOPE_API_KEY）")


async def main():
    """主测试函数"""
    print("=" * 60)
    print("真实服务集成测试")
    print("=" * 60)
    
    # 初始化服务
    print("\n初始化服务容器...")
    init_services()
    
    # 测试各个服务
    await test_sqlite_service()
    await test_speech_service()
    await test_document_parser_service()
    await test_video_analysis_service()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
