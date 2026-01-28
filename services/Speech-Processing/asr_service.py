"""
语音识别服务（ASR - Automatic Speech Recognition）
"""
import os
import threading
import time
from typing import Optional, Callable

try:
    import nls
except ImportError:
    try:
        from .nls_client import nls
    except ImportError:
        from nls_client import nls

try:
    from .config import SpeechConfig
    from .utils import convert_audio_to_pcm
except ImportError:
    from .config import SpeechConfig
    try:
        from utils import convert_audio_to_pcm
    except ImportError:
        convert_audio_to_pcm = None


class SpeechRecognizer:
    """语音识别器"""
    
    def __init__(self, config: Optional[SpeechConfig] = None):
        """初始化识别器"""
        self.config = config or SpeechConfig.from_env()
        self.result = None
        self.error = None
        self.completed = threading.Event()
    
    def recognize_file(
        self, 
        audio_path: str,
        enable_intermediate_result: bool = False,
        auto_convert: bool = True
    ) -> str:
        """
        识别音频文件
        
        Args:
            audio_path: 音频文件路径（支持PCM、MP3、WAV等格式）
            enable_intermediate_result: 是否返回中间结果
            auto_convert: 是否自动转换格式（默认True）
            
        Returns:
            str: 识别结果文本
        """
        # 检查文件是否存在
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音频文件不存在: {audio_path}")
        
        # 如果不是PCM格式，尝试转换
        if not audio_path.lower().endswith('.pcm'):
            if auto_convert and convert_audio_to_pcm:
                print(f"[ASR] 检测到非PCM格式，正在转换...")
                try:
                    pcm_path = convert_audio_to_pcm(audio_path)
                    print(f"[ASR] 转换成功: {pcm_path}")
                    audio_path = pcm_path
                except Exception as e:
                    print(f"[ASR] 转换失败: {e}")
                    print(f"[ASR] 尝试直接使用原文件...")
            else:
                print(f"[ASR] 警告: 音频文件不是PCM格式，可能识别失败")
        
        # 读取音频文件
        with open(audio_path, 'rb') as f:
            audio_data = f.read()
        
        return self.recognize_audio(audio_data, enable_intermediate_result)
    
    def recognize_audio(
        self,
        audio_data: bytes,
        enable_intermediate_result: bool = False
    ) -> str:
        """
        识别音频数据
        
        Args:
            audio_data: 音频二进制数据
            enable_intermediate_result: 是否返回中间结果
            
        Returns:
            str: 识别结果文本
        """
        self.result = None
        self.error = None
        self.completed.clear()
        
        # 创建识别器
        recognizer = nls.NlsSpeechRecognizer(
            url=self.config.url,
            token=self.config.token,
            appkey=self.config.appkey,
            on_start=self._on_start,
            on_result_changed=self._on_result_changed,
            on_completed=self._on_completed,
            on_error=self._on_error,
            on_close=self._on_close,
            callback_args=[]
        )
        
        try:
            # 开始识别
            recognizer.start(
                aformat=self.config.asr_format,
                sample_rate=self.config.asr_sample_rate,
                enable_intermediate_result=enable_intermediate_result,
                enable_punctuation_prediction=self.config.asr_enable_punctuation,
                enable_inverse_text_normalization=self.config.asr_enable_itn
            )
            
            # 发送音频数据（分片发送，避免一次性创建所有切片）
            slice_size = 640  # 每次发送640字节
            for i in range(0, len(audio_data), slice_size):
                audio_slice = audio_data[i:i+slice_size]
                recognizer.send_audio(audio_slice)
                time.sleep(0.01)  # 模拟实时发送
            
            # 停止识别
            recognizer.stop()
            
            # 等待完成
            self.completed.wait(timeout=30)
            
            if self.error:
                raise Exception(f"识别失败: {self.error}")
            
            return self.result or ""
        
        finally:
            # ✅ 确保 WebSocket 连接被关闭，防止内存泄漏
            try:
                recognizer.shutdown()
            except Exception as e:
                print(f"[ASR] 关闭连接时出错: {e}")
    
    def _on_start(self, message, *args):
        """识别开始回调"""
        print(f"[ASR] 识别开始: {message}")
    
    def _on_result_changed(self, message, *args):
        """中间结果回调"""
        print(f"[ASR] 中间结果: {message}")
    
    def _on_completed(self, message, *args):
        """识别完成回调"""
        print(f"[ASR] 识别完成: {message}")
        try:
            import json
            result_dict = json.loads(message)
            # 从 payload.result 中提取识别结果
            payload = result_dict.get('payload', {})
            self.result = payload.get('result', '')
            if not self.result:
                # 兼容旧格式：直接从根级别获取
                self.result = result_dict.get('result', '')
        except Exception as e:
            print(f"[ASR] 解析结果失败: {e}")
            self.result = message
        finally:
            self.completed.set()
    
    def _on_error(self, message, *args):
        """错误回调"""
        print(f"[ASR] 错误: {message}")
        self.error = message
        self.completed.set()
    
    def _on_close(self, *args):
        """连接关闭回调"""
        print(f"[ASR] 连接关闭")
