# 语音处理模块

基于阿里云智能语音交互服务的语音处理模块，支持语音识别（ASR）和语音合成（TTS）。

## 🎯 功能

- ✅ 语音识别（ASR - Automatic Speech Recognition）
  - 支持PCM、OPUS、OPU格式
  - 支持标点预测
  - 支持中文数字转阿拉伯数字
  
- ✅ 语音合成（TTS - Text To Speech）
  - 支持多种发音人
  - 支持PCM、WAV、MP3格式输出
  - 支持语速、音量、语调调节

## 📦 安装

### 1. 安装阿里云NLS SDK

```bash
# 从GitHub下载SDK
git clone https://github.com/aliyun/alibabacloud-nls-python-sdk.git

# 进入SDK目录
cd alibabacloud-nls-python-sdk

# 安装依赖
python -m pip install -r requirements.txt

# 安装SDK
python -m pip install .
```

### 2. 配置环境变量

在项目根目录的 `.env` 文件中添加：

```bash
# 阿里云智能语音配置
ALIYUN_NLS_APPKEY=your_appkey_here
ALIYUN_NLS_TOKEN=your_token_here
```

## 🚀 快速开始

### 独立使用

```python
from api_interface import speech_to_text, text_to_speech

# 文字转语音
audio_path = text_to_speech("你好，世界", "output.wav")
print(f"音频已保存到: {audio_path}")

# 语音转文字
text = speech_to_text("audio.pcm")
print(f"识别结果: {text}")
```

### 系统集成使用

```python
from src.container import container

# 获取语音服务
speech_service = container.get('speech')

# 语音转文字
text = await speech_service.speech_to_text("audio.pcm")

# 文字转语音
audio_path = await speech_service.text_to_speech("你好")
```

## 📁 文件结构

```
services/Speech-Processing/
├── __init__.py              # 模块入口
├── api_interface.py         # 核心接口（speech_to_text/text_to_speech）
├── config.py                # 配置管理
├── asr_service.py           # 语音识别服务
├── tts_service.py           # 语音合成服务
├── adapters.py              # 系统适配器
├── test_simple.py           # 功能测试
└── README.md                # 说明文档
```

## 🧪 测试

```bash
cd services/Speech-Processing
python test_simple.py
```

## ⚙️ 配置说明

### 语音识别配置

- `asr_format`: 音频格式（pcm/opus/opu）
- `asr_sample_rate`: 采样率（默认16000Hz）
- `asr_enable_punctuation`: 是否启用标点预测
- `asr_enable_itn`: 是否启用中文数字转换

### 语音合成配置

- `tts_format`: 输出格式（pcm/wav/mp3）
- `tts_voice`: 发音人（xiaoyun/xiaogang等）
- `tts_sample_rate`: 采样率（默认16000Hz）
- `tts_volume`: 音量（0-100）
- `tts_speech_rate`: 语速（-500~500）
- `tts_pitch_rate`: 语调（-500~500）

## 📝 注意事项

1. 音频文件格式要求：
   - ASR: PCM格式，16000Hz采样率，单声道
   - TTS: 输出支持PCM、WAV、MP3格式

2. Token获取：
   - 参考阿里云文档获取Token
   - Token有效期为24小时，需要定期更新

3. 并发限制：
   - 不建议使用超过200个线程
   - 推荐使用multiprocessing进行多进程处理

## 🔗 参考文档

- [阿里云智能语音交互](https://help.aliyun.com/product/30413.html)
- [Python SDK文档](https://help.aliyun.com/document_detail/120693.html)
- [获取Token](https://help.aliyun.com/document_detail/450255.html)

## 📄 License

MIT
