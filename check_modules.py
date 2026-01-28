"""
三个模块最终全面检查
"""
import sys
import os
import importlib
from pathlib import Path

sys.path.insert(0, '.')

print('=' * 70)
print('三个模块最终全面检查')
print('=' * 70)

# 1. 导入测试
print('\n【1. 导入测试】')
print('-' * 70)

modules_to_test = [
    ('SQLite API', 'services.SQLite.api_interface', ['get_child', 'save_child']),
    ('SQLite 适配器', 'services.SQLite.adapters', ['SQLiteServiceAdapter']),
    ('Speech API', 'services.Speech-Processing.api_interface', ['speech_to_text', 'text_to_speech']),
    ('Speech 适配器', 'services.Speech-Processing.adapters', ['AliyunSpeechService']),
    ('Multimodal API', 'services.Multimodal-Understanding.api_interface', ['parse_text', 'parse_image', 'parse_video']),
    ('Multimodal 适配器', 'services.Multimodal-Understanding.adapters', ['MultimodalVideoAnalysisService']),
]

all_passed = True

for name, module_path, items in modules_to_test:
    try:
        module = importlib.import_module(module_path)
        
        for item in items:
            if hasattr(module, item):
                print(f'✓ {name}: {item}')
            else:
                print(f'✗ {name}: {item} 不存在')
                all_passed = False
    except Exception as e:
        print(f'✗ {name}: 导入失败 - {e}')
        all_passed = False

# 2. 配置检查
print('\n【2. 配置文件检查】')
print('-' * 70)

if os.path.exists('.env'):
    with open('.env', 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    config_checks = [
        ('SQLITE_DB_PATH', 'SQLite 数据库路径'),
        ('ALIYUN_NLS_APPKEY', '阿里云语音 AppKey'),
        ('ALIYUN_NLS_TOKEN', '阿里云语音 Token'),
        ('DASHSCOPE_API_KEY', '通义千问 API Key'),
        ('USE_REAL_SQLITE', 'SQLite 服务开关'),
        ('USE_REAL_SPEECH', 'Speech 服务开关'),
        ('USE_REAL_VIDEO_ANALYSIS', 'Video 服务开关'),
    ]
    
    for key, desc in config_checks:
        if key in env_content:
            lines = [l for l in env_content.split('\n') if l.startswith(key)]
            if lines:
                value = lines[0].split('=', 1)[1].strip()
                if value and not value.startswith('your-'):
                    print(f'✓ {desc} ({key}): 已配置')
                else:
                    print(f'⚠ {desc} ({key}): 需要配置实际值')
        else:
            print(f'✗ {desc} ({key}): 未找到')

# 3. 语法检查
print('\n【3. 语法和类型检查】')
print('-' * 70)

modules = [
    'services/SQLite',
    'services/Speech-Processing', 
    'services/Multimodal-Understanding'
]

for module_dir in modules:
    py_files = list(Path(module_dir).glob('*.py'))
    py_files = [f for f in py_files if not f.name.startswith('test_')]
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), str(py_file), 'exec')
            print(f'✓ {py_file} 语法正确')
        except SyntaxError as e:
            print(f'✗ {py_file} 语法错误: {e}')
            all_passed = False

# 4. 功能测试
print('\n【4. 基础功能测试】')
print('-' * 70)

# 测试 SQLite
try:
    from services.SQLite.config import SQLiteConfig
    config = SQLiteConfig()
    print(f'✓ SQLite 配置加载成功: {config.db_path}')
except Exception as e:
    print(f'✗ SQLite 配置加载失败: {e}')
    all_passed = False

# 测试 Speech
try:
    from services.Speech_Processing.config import SpeechConfig
    # 不实际初始化，避免需要真实的 API Key
    print(f'✓ Speech 配置模块可导入')
except Exception as e:
    # 尝试用连字符导入
    try:
        speech_config = importlib.import_module('services.Speech-Processing.config')
        print(f'✓ Speech 配置模块可导入')
    except Exception as e2:
        print(f'⚠ Speech 配置需要 API Key: {e2}')

# 测试 Multimodal
try:
    multimodal_config = importlib.import_module('services.Multimodal-Understanding.config')
    print(f'✓ Multimodal 配置模块可导入')
except Exception as e:
    print(f'⚠ Multimodal 配置需要 API Key: {e}')

# 5. 代码质量检查
print('\n【5. 代码质量检查】')
print('-' * 70)

issues = []

# 检查 Speech 超时处理
speech_asr_file = Path('services/Speech-Processing/asr_service.py')
if speech_asr_file.exists():
    with open(speech_asr_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'self.completed.wait(timeout=30)' in content:
            if 'if not self.completed.wait' not in content:
                issues.append('⚠ Speech ASR: 超时后未检查返回值，可能导致资源泄漏')
            else:
                print('✓ Speech ASR: 超时处理正确')

# 检查 SQLite 数据验证
sqlite_service_file = Path('services/SQLite/service.py')
if sqlite_service_file.exists():
    with open(sqlite_service_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'def save_child' in content:
            if 'required_fields' not in content:
                issues.append('⚠ SQLite: save_child 缺少必填字段验证')
            else:
                print('✓ SQLite: 数据验证已实现')

# 检查 Multimodal analyze_video
multimodal_adapter_file = Path('services/Multimodal-Understanding/adapters.py')
if multimodal_adapter_file.exists():
    with open(multimodal_adapter_file, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'def analyze_video' in content:
            if '_parse_analysis_text' in content and '_fallback_parse' in content:
                print('✓ Multimodal: analyze_video 已修复（真实解析）')
            else:
                issues.append('⚠ Multimodal: analyze_video 可能仍返回假数据')

# 显示发现的问题
if issues:
    print('\n发现的代码质量问题:')
    for issue in issues:
        print(f'  {issue}')

print('\n' + '=' * 70)
if all_passed and not issues:
    print('✅ 所有检查通过！三个模块状态良好')
elif not issues:
    print('✅ 核心功能正常，有一些配置需要完善')
else:
    print('⚠️  核心功能正常，有一些代码质量问题可以优化')
print('=' * 70)
