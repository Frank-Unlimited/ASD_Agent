"""
配置管理模块
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SpeechConfig:
    """语音处理配置类"""
    
    # 阿里云配置
    appkey: Optional[str] = None
    token: Optional[str] = None
    url: str = "wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1"
    
    # 语音识别配置
    asr_format: str = "pcm"  # 音频格式：pcm, opus, opu
    asr_sample_rate: int = 16000  # 采样率
    asr_enable_punctuation: bool = True  # 标点预测
    asr_enable_itn: bool = True  # 中文数字转阿拉伯数字
    
    # 语音合成配置
    tts_format: str = "wav"  # 输出格式：pcm, wav, mp3
    tts_voice: str = "xiaoyun"  # 发音人
    tts_sample_rate: int = 16000  # 采样率
    tts_volume: int = 50  # 音量 0-100
    tts_speech_rate: int = 0  # 语速 -500~500
    tts_pitch_rate: int = 0  # 语调 -500~500
    
    def __post_init__(self):
        """初始化后处理"""
        if self.appkey is None:
            self.appkey = os.getenv("ALIYUN_NLS_APPKEY")
            if not self.appkey:
                raise ValueError("Appkey not found. Set ALIYUN_NLS_APPKEY environment variable.")
        
        if self.token is None:
            self.token = os.getenv("ALIYUN_NLS_TOKEN")
            if not self.token:
                raise ValueError("Token not found. Set ALIYUN_NLS_TOKEN environment variable.")
    
    @classmethod
    def from_env(cls) -> 'SpeechConfig':
        """从环境变量创建配置"""
        return cls(
            appkey=os.getenv("ALIYUN_NLS_APPKEY"),
            token=os.getenv("ALIYUN_NLS_TOKEN"),
            url=os.getenv("ALIYUN_NLS_URL", cls.url)
        )
