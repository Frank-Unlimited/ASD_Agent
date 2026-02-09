# 语音处理模块集成说明

## ✅ 已完成的集成

语音处理模块已成功集成到系统中！

### 集成内容

1. **核心服务实现**
   - `asr_service.py` - 语音识别服务
   - `tts_service.py` - 语音合成服务
   - `nls_client.py` - 自定义NLS客户端

2. **系统适配器** - `adapters.py`
   - `AliyunSpeechService` - 实现 `ISpeechService` 接口

3. **容器注册** - `src/container.py`
   - 已注册为 `speech` 服务

4. **配置添加** - `src/config.py` 和 `.env.example`
   - `ALIYUN_NLS_APPKEY` - Appkey配置
   - `ALIYUN_NLS_TOKEN` - Token配置

## 🎯 功能映射

```
你的模块功能          →  系统接口              →  应用场景
─────────────────────────────────────────────────────────────
speech_to_text()  ──→ ISpeechService        →  语音观察记录
                      - speech_to_text()       家长语音输入
                                               
text_to_speech()  ──→ ISpeechService        →  实时指引播报
                      - text_to_speech()       语音反馈
```

## 🚀 如何使用

### 1. 配置环境变量

在 `.env` 文件中设置：

```bash
# 启用真实语音服务
USE_REAL_SPEECH=true

# 阿里云智能语音配置
ALIYUN_NLS_APPKEY=your_appkey_here
ALIYUN_NLS_TOKEN=your_token_here
```

### 2. 在系统中使用

```python
from src.container import container

# 获取语音服务
speech_service = container.get('speech')

# 语音转文字
text = await speech_service.speech_to_text("audio.pcm")
print(f"识别结果: {text}")

# 文字转语音
audio_path = await speech_service.text_to_speech("你好，世界")
print(f"音频文件: {audio_path}")
```

### 3. 独立使用

```python
from api_interface import speech_to_text, text_to_speech

# 语音转文字
text = speech_to_text("audio.pcm")

# 文字转语音
audio_path = text_to_speech("你好", "output.wav")
```

## 📋 接口说明

### ISpeechService 接口

#### 1. speech_to_text()

```python
async def speech_to_text(audio_path: str) -> str:
    """
    语音转文字
    
    Args:
        audio_path: 音频文件路径（PCM格式，16000Hz）
        
    Returns:
        str: 识别结果文本
    """
```

#### 2. text_to_speech()

```python
async def text_to_speech(text: str) -> str:
    """
    文字转语音
    
    Args:
        text: 要合成的文本
        
    Returns:
        str: 音频文件路径（WAV格式）
    """
```

## 🔄 Mock vs Real

### Mock模式（默认）

```bash
USE_REAL_SPEECH=false
```

- 返回假数据
- 快速响应
- 用于开发和测试

### Real模式

```bash
USE_REAL_SPEECH=true
ALIYUN_NLS_APPKEY=your_appkey
ALIYUN_NLS_TOKEN=your_token
```

- 调用真实的阿里云API
- 返回真实识别/合成结果
- 用于生产环境

## 📁 文件结构

```
services/Speech-Processing/
├── __init__.py              # 模块入口
├── api_interface.py         # 核心接口
├── config.py                # 配置管理
├── asr_service.py           # 语音识别服务
├── tts_service.py           # 语音合成服务
├── nls_client.py            # 自定义NLS客户端 ⭐
├── adapters.py              # 系统适配器 ⭐
├── test_simple.py           # 功能测试
├── README.md                # 使用文档
├── SETUP.md                 # 安装说明
└── INTEGRATION.md           # 集成文档（本文件）
```

## 💡 使用场景

### 场景1: 观察捕获 - 语音记录

```python
# 家长在干预会话中语音记录观察
speech_service = container.get('speech')

# 录制音频后，转换为文字
observation_text = await speech_service.speech_to_text(
    audio_path="observation.pcm"
)

# 保存观察记录
save_observation(session_id, observation_text)
```

### 场景2: 实时指引 - 语音播报

```python
# 生成实时指引文本
guidance_text = "现在可以尝试和孩子进行眼神接触"

# 转换为语音播报
speech_service = container.get('speech')
audio_path = await speech_service.text_to_speech(guidance_text)

# 播放音频
play_audio(audio_path)
```

### 场景3: 对话助手 - 语音交互

```python
# 家长语音提问
question_audio = "孩子今天的表现怎么样？"
question_text = await speech_service.speech_to_text(question_audio)

# AI回答
answer_text = await chat_assistant.chat(child_id, question_text)

# 语音播报回答
answer_audio = await speech_service.text_to_speech(answer_text)
play_audio(answer_audio)
```

## 🎯 核心优势

1. **自定义客户端** - 不依赖官方SDK，更轻量
2. **完全适配** - 实现系统 `ISpeechService` 接口
3. **配置切换** - Mock/Real 灵活切换
4. **独立开发** - 模块内部完全独立

## 🔧 技术细节

### 自定义NLS客户端

我们实现了自己的NLS客户端（`nls_client.py`），原因：
1. 官方SDK不在PyPI上，安装复杂
2. 需要从GitHub下载，可能网络不稳定
3. 自定义实现更轻量，易于维护

**实现方式：**
- 使用 `websocket-client` 库
- 直接实现阿里云NLS WebSocket协议
- 完全兼容官方SDK的接口

### WebSocket通信流程

```
1. 建立连接
   wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1?token=xxx

2. 发送开始消息
   {"header": {...}, "payload": {...}}

3. 发送/接收数据
   - ASR: 发送音频数据，接收识别结果
   - TTS: 接收音频数据

4. 发送停止消息
   {"header": {"name": "Stop..."}}

5. 关闭连接
```

## ⚠️ 注意事项

1. **Token管理**
   - Token有效期24小时
   - 需要定期刷新
   - 建议实现自动刷新机制

2. **音频格式**
   - ASR输入: PCM格式，16000Hz，单声道
   - TTS输出: WAV格式（默认）

3. **并发限制**
   - 单个Appkey有并发限制
   - 建议使用连接池

4. **网络要求**
   - 需要稳定的网络连接
   - 阿里云ECS可使用内网URL

## 🐛 故障排查

### 问题1: 导入错误

```
ImportError: No module named 'nls'
```

**解决**：已自动使用 `nls_client.py`，无需安装官方SDK

### 问题2: Token无效

```
错误: Invalid token
```

**解决**：
1. 检查Token是否正确
2. 确认Token是否过期（24小时）
3. 重新获取Token

### 问题3: 音频格式错误

```
错误: Unsupported audio format
```

**解决**：
- 确保音频是PCM格式
- 采样率为16000Hz
- 单声道

## 📚 参考文档

- [阿里云智能语音交互](https://help.aliyun.com/product/30413.html)
- [语音识别API](https://help.aliyun.com/document_detail/92131.html)
- [语音合成API](https://help.aliyun.com/document_detail/84435.html)
- [获取Token](https://help.aliyun.com/document_detail/450255.html)

---

**✅ 集成完成！语音处理模块已是系统的一部分。** 🎉
