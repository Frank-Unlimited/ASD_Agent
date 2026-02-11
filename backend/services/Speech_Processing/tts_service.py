"""
语音合成服务（TTS - Text To Speech）
"""
import threading
from typing import Optional

try:
    import nls
except ImportError:
    try:
        from .nls_client import nls
    except ImportError:
        from nls_client import nls

try:
    from .config import SpeechConfig
except ImportError:
    from .config import SpeechConfig


class SpeechSynthesizer:
    """语音合成器"""
    
    def __init__(self, config: Optional[SpeechConfig] = None):
        """初始化合成器"""
        self.config = config or SpeechConfig.from_env()
        self.audio_data = bytearray()
        self.error = None
        self.completed = threading.Event()
    
    def synthesize_to_file(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None
    ) -> str:
        """
        合成语音并保存到文件
        
        Args:
            text: 要合成的文本
            output_path: 输出文件路径
            voice: 发音人（可选）
            
        Returns:
            str: 输出文件路径
        """
        audio_data = self.synthesize(text, voice)
        
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        
        return output_path
    
    def synthesize(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        合成语音
        
        Args:
            text: 要合成的文本
            voice: 发音人（可选）
            
        Returns:
            bytes: 音频二进制数据
        """
        self.audio_data = bytearray()
        self.error = None
        self.completed.clear()
        
        # 创建合成器
        synthesizer = nls.NlsSpeechSynthesizer(
            url=self.config.url,
            token=self.config.token,
            appkey=self.config.appkey,
            on_metainfo=self._on_metainfo,
            on_data=self._on_data,
            on_completed=self._on_completed,
            on_error=self._on_error,
            on_close=self._on_close,
            callback_args=[]
        )
        
        # 开始合成
        synthesizer.start(
            text=text,
            aformat=self.config.tts_format,
            voice=voice or self.config.tts_voice,
            sample_rate=self.config.tts_sample_rate,
            volume=self.config.tts_volume,
            speech_rate=self.config.tts_speech_rate,
            pitch_rate=self.config.tts_pitch_rate,
            wait_complete=True
        )
        
        # 等待完成
        self.completed.wait(timeout=60)
        
        if self.error:
            raise Exception(f"合成失败: {self.error}")
        
        return bytes(self.audio_data)
    
    def _on_metainfo(self, message, *args):
        """元信息回调"""
        print(f"[TTS] 元信息: {message}")
    
    def _on_data(self, data, *args):
        """音频数据回调"""
        self.audio_data.extend(data)
    
    def _on_completed(self, message, *args):
        """合成完成回调"""
        print(f"[TTS] 合成完成: {message}")
        self.completed.set()
    
    def _on_error(self, message, *args):
        """错误回调"""
        print(f"[TTS] 错误: {message}")
        self.error = message
        self.completed.set()
    
    def _on_close(self, *args):
        """连接关闭回调"""
        print(f"[TTS] 连接关闭")
