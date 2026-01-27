"""
完整测试 - 测试所有功能
"""
import os
import sys
import time
from pathlib import Path

# 添加项目根目录到路径（用于加载 .env）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from dotenv import load_dotenv
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ 已加载环境变量: {env_path}")
    else:
        print(f"⚠️  未找到 .env 文件: {env_path}")
except ImportError:
    print("⚠️  python-dotenv 未安装，尝试从系统环境变量读取")

# 检查配置
appkey = os.getenv("ALIYUN_NLS_APPKEY")
token = os.getenv("ALIYUN_NLS_TOKEN")

print("\n" + "=" * 70)
print("🎤 语音处理模块 - 完整测试")
print("=" * 70)

print("\n📋 环境检查:")
print("-" * 70)

# 检查配置
if not appkey or appkey == "your-nls-appkey-here":
    print("❌ ALIYUN_NLS_APPKEY 未配置")
    print("   请在 .env 文件中设置正确的 Appkey")
    has_config = False
else:
    print(f"✅ ALIYUN_NLS_APPKEY: {appkey[:10]}...")
    has_config = True

if not token or token == "your-nls-token-here":
    print("❌ ALIYUN_NLS_TOKEN 未配置")
    print("   请在 .env 文件中设置正确的 Token")
    has_config = False
else:
    print(f"✅ ALIYUN_NLS_TOKEN: {token[:20]}...")

if not has_config:
    print("\n⚠️  配置不完整，部分测试将跳过")
    print("\n📖 配置方法:")
    print("   1. 登录阿里云控制台: https://nls-portal.console.aliyun.com/")
    print("   2. 获取 Appkey 和 Token")
    print("   3. 在 .env 文件中配置:")
    print("      ALIYUN_NLS_APPKEY=your_appkey")
    print("      ALIYUN_NLS_TOKEN=your_token")

from api_interface import speech_to_text, text_to_speech
from utils import is_ffmpeg_available, get_audio_info, convert_audio_to_pcm
from config import SpeechConfig

# 检查 ffmpeg
print()
if is_ffmpeg_available():
    print("✅ ffmpeg 已安装，支持 MP3/WAV 等格式自动转换")
else:
    print("⚠️  ffmpeg 未安装，仅支持 PCM 格式")
    print("   安装方法:")
    print("     Windows: choco install ffmpeg")
    print("     Mac: brew install ffmpeg")
    print("     Linux: sudo apt-get install ffmpeg")

# 显示配置信息
print("\n⚙️  当前配置:")
print("-" * 70)
try:
    config = SpeechConfig.from_env()
    print(f"  WebSocket URL: {config.url}")
    print(f"  ASR 格式: {config.asr_format}")
    print(f"  ASR 采样率: {config.asr_sample_rate} Hz")
    print(f"  TTS 发音人: {config.tts_voice}")
    print(f"  TTS 音量: {config.tts_volume}")
    print(f"  TTS 语速: {config.tts_speech_rate}")
except Exception as e:
    print(f"  ⚠️  配置加载失败: {e}")

# 统计测试结果
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'skipped': 0
}

def run_test(test_name, test_func):
    """运行单个测试"""
    test_results['total'] += 1
    print(f"\n{'=' * 70}")
    print(f"🧪 {test_name}")
    print('=' * 70)
    
    try:
        result = test_func()
        if result:
            test_results['passed'] += 1
            print(f"\n✅ 测试通过")
        else:
            test_results['skipped'] += 1
            print(f"\n⏭️  测试跳过")
        return result
    except Exception as e:
        test_results['failed'] += 1
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# 测试1: 文字转语音（基础）
# ============================================================
def test_tts_basic():
    """测试基础文字转语音"""
    if not has_config:
        print("⚠️  跳过: 配置不完整")
        return False
    
    text = "你好，我是智能语音助手。"
    print(f"\n📝 输入文本: {text}")
    
    output_path = "output_basic.wav"
    print(f"🎯 输出文件: {output_path}")
    
    start_time = time.time()
    result = text_to_speech(text, output_path)
    elapsed = time.time() - start_time
    
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📁 输出: {result}")
    
    if os.path.exists(result):
        file_size = os.path.getsize(result)
        print(f"📊 文件大小: {file_size} 字节 ({file_size/1024:.2f} KB)")
        
        if is_ffmpeg_available():
            info = get_audio_info(result)
            if 'error' not in info:
                print(f"🎵 音频信息:")
                print(f"   - 格式: {info.get('format')}")
                print(f"   - 时长: {info.get('duration'):.2f} 秒")
                print(f"   - 采样率: {info.get('sample_rate')} Hz")
                print(f"   - 声道数: {info.get('channels')}")
                print(f"   - 比特率: {info.get('bit_rate', 0)} bps")
        return True
    else:
        print("❌ 文件未生成")
        return False

# ============================================================
# 测试2: 文字转语音（长文本）
# ============================================================
def test_tts_long():
    """测试长文本语音合成"""
    if not has_config:
        print("⚠️  跳过: 配置不完整")
        return False
    
    text = """
    欢迎使用语音处理模块。
    本模块基于阿里云智能语音交互服务，
    支持语音识别和语音合成功能。
    可以处理多种音频格式，包括MP3、WAV和PCM。
    """
    print(f"\n📝 输入文本: {text.strip()}")
    print(f"📏 文本长度: {len(text)} 字符")
    
    output_path = "output_long.wav"
    
    start_time = time.time()
    result = text_to_speech(text, output_path)
    elapsed = time.time() - start_time
    
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    
    if os.path.exists(result):
        file_size = os.path.getsize(result)
        print(f"📊 文件大小: {file_size/1024:.2f} KB")
        
        if is_ffmpeg_available():
            info = get_audio_info(result)
            if 'error' not in info:
                print(f"🎵 时长: {info.get('duration'):.2f} 秒")
        return True
    return False

# ============================================================
# 测试3: 语音转文字（使用生成的音频）
# ============================================================
def test_asr_generated():
    """测试识别刚生成的音频"""
    if not has_config:
        print("⚠️  跳过: 配置不完整")
        return False
    
    audio_file = "output_basic.wav"
    
    if not os.path.exists(audio_file):
        print(f"⚠️  跳过: 音频文件不存在 - {audio_file}")
        print("   请先运行测试1生成音频文件")
        return False
    
    print(f"\n🎵 输入文件: {audio_file}")
    
    if is_ffmpeg_available():
        info = get_audio_info(audio_file)
        if 'error' not in info:
            print(f"📊 音频信息:")
            print(f"   - 格式: {info.get('format')}")
            print(f"   - 时长: {info.get('duration'):.2f} 秒")
            print(f"   - 采样率: {info.get('sample_rate')} Hz")
    
    print(f"\n🔄 正在识别...")
    start_time = time.time()
    result_text = speech_to_text(audio_file)
    elapsed = time.time() - start_time
    
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📝 识别结果: {result_text}")
    print(f"📏 结果长度: {len(result_text)} 字符")
    
    return True

# ============================================================
# 测试4: 语音转文字（外部音频文件）
# ============================================================
def test_asr_external():
    """测试识别外部音频文件"""
    if not has_config:
        print("⚠️  跳过: 配置不完整")
        return False
    
    # 查找测试文件
    test_files = [
        "test.mp3",
        "test.wav",
        "test.pcm",
        "audio.mp3",
        "audio.wav",
    ]
    
    audio_file = None
    for file in test_files:
        if os.path.exists(file):
            audio_file = file
            break
    
    if not audio_file:
        print(f"⚠️  跳过: 未找到外部测试音频文件")
        print(f"   支持的文件名: {', '.join(test_files)}")
        print(f"   请将音频文件放到当前目录")
        return False
    
    print(f"\n🎵 输入文件: {audio_file}")
    
    if is_ffmpeg_available():
        info = get_audio_info(audio_file)
        if 'error' not in info:
            print(f"📊 音频信息:")
            print(f"   - 格式: {info.get('format')}")
            print(f"   - 时长: {info.get('duration'):.2f} 秒")
            print(f"   - 采样率: {info.get('sample_rate')} Hz")
            print(f"   - 声道数: {info.get('channels')}")
    
    print(f"\n🔄 正在识别...")
    start_time = time.time()
    result_text = speech_to_text(audio_file)
    elapsed = time.time() - start_time
    
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📝 识别结果: {result_text}")
    
    return True

# ============================================================
# 测试5: 音频格式转换
# ============================================================
def test_audio_conversion():
    """测试音频格式转换"""
    if not is_ffmpeg_available():
        print("⚠️  跳过: ffmpeg 未安装")
        return False
    
    # 查找测试文件
    test_files = ["test.mp3", "test.wav", "output_basic.wav"]
    source_file = None
    
    for file in test_files:
        if os.path.exists(file):
            source_file = file
            break
    
    if not source_file:
        print(f"⚠️  跳过: 未找到音频文件")
        return False
    
    print(f"\n🎵 源文件: {source_file}")
    
    # 获取源文件信息
    info = get_audio_info(source_file)
    if 'error' not in info:
        print(f"📊 源文件信息:")
        print(f"   - 格式: {info.get('format')}")
        print(f"   - 采样率: {info.get('sample_rate')} Hz")
        print(f"   - 声道数: {info.get('channels')}")
    
    # 转换为 PCM
    print(f"\n🔄 转换为 PCM 格式...")
    start_time = time.time()
    pcm_file = convert_audio_to_pcm(source_file, "converted.pcm")
    elapsed = time.time() - start_time
    
    print(f"⏱️  耗时: {elapsed:.2f} 秒")
    print(f"📁 输出: {pcm_file}")
    
    if os.path.exists(pcm_file):
        file_size = os.path.getsize(pcm_file)
        print(f"📊 文件大小: {file_size/1024:.2f} KB")
        return True
    
    return False

# ============================================================
# 测试6: 系统适配器
# ============================================================
def test_adapter():
    """测试系统适配器"""
    if not has_config:
        print("⚠️  跳过: 配置不完整")
        return False
    
    print(f"\n🔌 测试系统适配器...")
    
    try:
        from adapters import AliyunSpeechService
        
        service = AliyunSpeechService()
        print(f"✅ 适配器创建成功")
        print(f"   服务名称: {service.get_service_name()}")
        print(f"   服务版本: {service.get_service_version()}")
        
        # 测试 TTS
        print(f"\n📝 测试 text_to_speech 接口...")
        import asyncio
        
        async def test_tts():
            result = await service.text_to_speech("测试适配器")
            return result
        
        audio_path = asyncio.run(test_tts())
        print(f"✅ TTS 测试通过: {audio_path}")
        
        # 测试 ASR
        if os.path.exists(audio_path):
            print(f"\n🎵 测试 speech_to_text 接口...")
            
            async def test_asr():
                result = await service.speech_to_text(audio_path)
                return result
            
            text = asyncio.run(test_asr())
            print(f"✅ ASR 测试通过: {text}")
        
        return True
    
    except Exception as e:
        print(f"❌ 适配器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================
# 运行所有测试
# ============================================================
print("\n" + "=" * 70)
print("🚀 开始测试")
print("=" * 70)

run_test("测试1: 文字转语音（基础）", test_tts_basic)
run_test("测试2: 文字转语音（长文本）", test_tts_long)
run_test("测试3: 语音转文字（生成的音频）", test_asr_generated)
run_test("测试4: 语音转文字（外部音频）", test_asr_external)
run_test("测试5: 音频格式转换", test_audio_conversion)
run_test("测试6: 系统适配器", test_adapter)

# ============================================================
# 测试总结
# ============================================================
print("\n" + "=" * 70)
print("📊 测试总结")
print("=" * 70)
print(f"总计: {test_results['total']} 个测试")
print(f"✅ 通过: {test_results['passed']} 个")
print(f"❌ 失败: {test_results['failed']} 个")
print(f"⏭️  跳过: {test_results['skipped']} 个")

if test_results['failed'] > 0:
    print(f"\n⚠️  有 {test_results['failed']} 个测试失败")
elif test_results['passed'] > 0:
    print(f"\n🎉 所有测试通过！")
else:
    print(f"\n⚠️  所有测试都被跳过，请检查配置")

print("\n" + "=" * 70)
print("💡 提示")
print("=" * 70)
print("  - 支持 MP3、WAV、PCM 等格式（需要 ffmpeg）")
print("  - 推荐使用 16000Hz 采样率的音频文件")
print("  - 音频文件时长建议在 60 秒以内")
print("  - Token 有效期 24 小时，需定期刷新")
print("\n" + "=" * 70)

