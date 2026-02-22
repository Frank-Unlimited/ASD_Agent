# 语音处理模块 - 安装说明

## ✅ 已完成的安装

### 1. 已安装的依赖

- ✅ `aliyun-python-sdk-core` - 阿里云核心SDK
- ✅ `websocket-client` - WebSocket客户端
- ✅ `cryptography` - 加密库
- ✅ `jmespath` - JSON查询

### 2. 自定义NLS客户端

由于官方NLS SDK不在PyPI上，我们创建了自己的客户端：
- ✅ `nls_client.py` - 简化版NLS客户端
  - 实现了 `NlsSpeechRecognizer` - 语音识别
  - 实现了 `NlsSpeechSynthesizer` - 语音合成
  - 直接使用WebSocket与阿里云通信

## 🚀 使用方式

### 1. 配置环境变量

在项目根目录的 `.env` 文件中添加：

```bash
# 阿里云智能语音配置
ALIYUN_NLS_APPKEY=your_appkey_here
ALIYUN_NLS_TOKEN=your_token_here
```

### 2. 获取Appkey和Token

#### 获取Appkey
1. 登录[阿里云智能语音控制台](https://nls-portal.console.aliyun.com/applist)
2. 创建项目或选择现有项目
3. 复制Appkey

#### 获取Token
参考文档：https://help.aliyun.com/document_detail/450255.html

方式1：使用AccessKey获取（推荐）
```python
import requests

url = "https://nls-meta.cn-shanghai.aliyuncs.com/pop/2018-05-18/tokens"
params = {
    "AccessKeyId": "your_access_key_id",
    "Action": "CreateToken"
}

response = requests.get(url, params=params)
token = response.json()["Token"]["Id"]
print(f"Token: {token}")
```

方式2：在控制台手动获取
- Token有效期24小时，需要定期更新

### 3. 测试

```bash
cd services/Speech-Processing
python test_simple.py
```

## 📁 文件说明

| 文件 | 说明 |
|------|------|
| `nls_client.py` | 自定义NLS客户端（核心） |
| `asr_service.py` | 语音识别服务 |
| `tts_service.py` | 语音合成服务 |
| `api_interface.py` | 简洁接口 |
| `adapters.py` | 系统适配器 |
| `config.py` | 配置管理 |

## 🔧 技术实现

### 自定义客户端 vs 官方SDK

**为什么使用自定义客户端？**
1. 官方SDK不在PyPI上，安装复杂
2. 需要从GitHub下载，网络可能不稳定
3. 自定义客户端更轻量，易于维护

**实现方式：**
- 使用 `websocket-client` 库
- 直接实现阿里云NLS协议
- 完全兼容官方SDK的接口

### WebSocket协议

```
连接: wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1?token=xxx

消息格式:
{
    "header": {
        "message_id": "uuid",
        "task_id": "uuid",
        "namespace": "SpeechRecognizer/SpeechSynthesizer",
        "name": "StartRecognition/StartSynthesis",
        "appkey": "your_appkey"
    },
    "payload": {
        // 参数
    }
}
```

## ⚠️ 注意事项

1. **Token有效期**
   - Token有效期为24小时
   - 建议实现自动刷新机制

2. **音频格式要求**
   - ASR: PCM格式，16000Hz，单声道
   - TTS: 输出支持PCM、WAV、MP3

3. **并发限制**
   - 单个Appkey有并发限制
   - 建议使用连接池管理

4. **网络要求**
   - 需要稳定的网络连接
   - 建议使用阿里云ECS内网访问

## 🐛 故障排查

### 问题1: 连接失败

```
错误: Connection refused
```

**解决**：
- 检查网络连接
- 确认Token是否有效
- 尝试使用内网URL（如果在阿里云ECS上）

### 问题2: Token过期

```
错误: Token expired
```

**解决**：
- 重新获取Token
- 实现Token自动刷新

### 问题3: Appkey无效

```
错误: Invalid appkey
```

**解决**：
- 检查Appkey是否正确
- 确认项目是否已开通相应服务

## 📚 参考文档

- [阿里云智能语音交互](https://help.aliyun.com/product/30413.html)
- [语音识别接口说明](https://help.aliyun.com/document_detail/92131.html)
- [语音合成接口说明](https://help.aliyun.com/document_detail/84435.html)
- [获取Token](https://help.aliyun.com/document_detail/450255.html)

---

**✅ 环境已准备就绪！可以开始使用了。**
