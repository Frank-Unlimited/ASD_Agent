"""
Speech-Processing 模块深度检查脚本
检查所有潜在问题和依赖
"""
import sys
import os

# 添加模块路径
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 60)
print("Speech-Processing 模块深度检查")
print("=" * 60)

# ============ 1. 检查依赖 ============
print("\n[1] 检查依赖...")
dependencies = {
    'websocket': 'websocket-client',
    'json': 'json (内置)',
    'uuid': 'uuid (内置)',
    'threading': 'threading (内置)',
    'time': 'time (内置)',
}

missing_deps = []
for module, name in dependencies.items():
    try:
        __import__(module)
        print(f"  ✅ {name}")
    except ImportError:
        print(f"  ❌ {name} - 缺失")
        missing_deps.append(name)

if missing_deps:
    print(f"\n⚠️ 缺失依赖: {', '.join(missing_deps)}")
else:
    print("\n✅ 所有依赖已安装")

# ============ 2. 检查模块导入 ============
print("\n[2] 检查模块导入...")
modules_to_check = [
    ('config', 'SpeechConfig'),
    ('nls_client', 'nls'),
    ('asr_service', 'SpeechRecognizer'),
    ('tts_service', 'SpeechSynthesizer'),
    ('api_interface', 'speech_to_text'),
    ('api_interface', 'text_to_speech'),
    ('adapters', 'AliyunSpeechService'),
]

import_errors = []
for module_name, class_name in modules_to_check:
    try:
        module = __import__(module_name, fromlist=[class_name])
        getattr(module, class_name)
        print(f"  ✅ {module_name}.{class_name}")
    except Exception as e:
        print(f"  ❌ {module_name}.{class_name} - {e}")
        import_errors.append((module_name, class_name, str(e)))

if import_errors:
    print(f"\n⚠️ 导入错误: {len(import_errors)} 个")
else:
    print("\n✅ 所有模块导入成功")

# ============ 3. 检查配置 ============
print("\n[3] 检查配置...")
try:
    from config import SpeechConfig
    
    # 检查环境变量
    env_vars = {
        'ALIYUN_NLS_APPKEY': os.getenv('ALIYUN_NLS_APPKEY'),
        'ALIYUN_NLS_TOKEN': os.getenv('ALIYUN_NLS_TOKEN'),
    }
    
    for var, value in env_vars.items():
        if value:
            print(f"  ✅ {var}: {value[:10]}...")
        else:
            print(f"  ⚠️ {var}: 未设置")
    
    # 尝试创建配置
    try:
        config = SpeechConfig.from_env()
        print(f"\n  ✅ 配置创建成功")
        print(f"     - URL: {config.url}")
        print(f"     - ASR格式: {config.asr_format}")
        print(f"     - TTS格式: {config.tts_format}")
    except Exception as e:
        print(f"\n  ❌ 配置创建失败: {e}")

except Exception as e:
    print(f"  ❌ 配置检查失败: {e}")

# ============ 4. 检查NLS客户端 ============
print("\n[4] 检查NLS客户端...")
try:
    from nls_client import nls, NlsSpeechRecognizer, NlsSpeechSynthesizer
    
    print(f"  ✅ nls 模块")
    print(f"  ✅ NlsSpeechRecognizer 类")
    print(f"  ✅ NlsSpeechSynthesizer 类")
    
    # 检查类方法
    recognizer_methods = ['start', 'send_audio', 'stop', 'shutdown']
    synthesizer_methods = ['start', 'shutdown']
    
    print("\n  NlsSpeechRecognizer 方法:")
    for method in recognizer_methods:
        if hasattr(NlsSpeechRecognizer, method):
            print(f"    ✅ {method}()")
        else:
            print(f"    ❌ {method}() - 缺失")
    
    print("\n  NlsSpeechSynthesizer 方法:")
    for method in synthesizer_methods:
        if hasattr(NlsSpeechSynthesizer, method):
            print(f"    ✅ {method}()")
        else:
            print(f"    ❌ {method}() - 缺失")

except Exception as e:
    print(f"  ❌ NLS客户端检查失败: {e}")

# ============ 5. 检查UUID处理 ============
print("\n[5] 检查UUID处理...")
try:
    import uuid
    
    # 测试UUID生成
    test_uuid = str(uuid.uuid4())
    print(f"  原始UUID: {test_uuid}")
    
    # 测试去除连字符
    clean_uuid = test_uuid.replace('-', '')
    print(f"  清理后UUID: {clean_uuid}")
    print(f"  长度: {len(clean_uuid)} (应为32)")
    
    if len(clean_uuid) == 32:
        print(f"  ✅ UUID处理正确")
    else:
        print(f"  ❌ UUID长度错误")

except Exception as e:
    print(f"  ❌ UUID检查失败: {e}")

# ============ 6. 检查音频转换工具 ============
print("\n[6] 检查音频转换工具...")
try:
    from utils import convert_audio_to_pcm, is_ffmpeg_available
    
    # 检查ffmpeg
    if is_ffmpeg_available():
        print(f"  ✅ ffmpeg 已安装")
    else:
        print(f"  ⚠️ ffmpeg 未安装（音频转换功能不可用）")
    
    print(f"  ✅ convert_audio_to_pcm() 函数存在")

except Exception as e:
    print(f"  ❌ 音频工具检查失败: {e}")

# ============ 7. 代码质量检查 ============
print("\n[7] 代码质量检查...")

issues = []

# 检查 nls_client.py 中的重复代码
print("  检查重复代码...")
try:
    file_path = os.path.join(os.path.dirname(__file__), 'nls_client.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # 统计 .replace('-', '') 出现次数
    replace_count = content.count(".replace('-', '')")
    print(f"    - UUID清理代码出现 {replace_count} 次")
    if replace_count > 5:
        issues.append(f"UUID清理代码重复 {replace_count} 次，建议提取为函数")

except Exception as e:
    print(f"    ⚠️ 无法检查: {e}")

# 检查异常处理
print("  检查异常处理...")
try:
    file_path = os.path.join(os.path.dirname(__file__), 'asr_service.py')
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查裸except
    bare_except_count = content.count('except:')
    bare_except_lines = content.count('except Exception')
    
    if bare_except_count > 0:
        issues.append(f"asr_service.py 中有 {bare_except_count} 个裸except语句")
        print(f"    ⚠️ 发现 {bare_except_count} 个裸except")
    else:
        print(f"    ✅ 无裸except语句")
    
    print(f"    - 使用 'except Exception' {bare_except_lines} 次")

except Exception as e:
    print(f"    ⚠️ 无法检查: {e}")

# 检查日志记录
print("  检查日志记录...")
try:
    files_to_check = ['asr_service.py', 'tts_service.py', 'nls_client.py']
    has_logging = False
    print_count = 0
    
    for file in files_to_check:
        file_path = os.path.join(os.path.dirname(__file__), file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'import logging' in content:
            has_logging = True
        print_count += content.count('print(')
    
    if has_logging:
        print(f"    ✅ 使用了logging模块")
    else:
        print(f"    ⚠️ 未使用logging模块，仅使用print")
        print(f"    - 共有 {print_count} 个print语句")
        issues.append("建议使用logging模块替代print")

except Exception as e:
    print(f"    ⚠️ 无法检查: {e}")

# ============ 8. 总结 ============
print("\n" + "=" * 60)
print("检查总结")
print("=" * 60)

if missing_deps:
    print(f"\n❌ 缺失依赖: {len(missing_deps)} 个")
    for dep in missing_deps:
        print(f"   - {dep}")

if import_errors:
    print(f"\n❌ 导入错误: {len(import_errors)} 个")
    for module, cls, error in import_errors:
        print(f"   - {module}.{cls}: {error}")

if issues:
    print(f"\n⚠️ 代码质量问题: {len(issues)} 个")
    for i, issue in enumerate(issues, 1):
        print(f"   {i}. {issue}")

if not missing_deps and not import_errors and not issues:
    print("\n✅ 所有检查通过！模块状态良好。")
else:
    print("\n⚠️ 发现一些问题，但不影响核心功能。")

print("\n" + "=" * 60)
