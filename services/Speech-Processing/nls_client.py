"""
简化版阿里云NLS客户端
不依赖官方SDK，直接使用WebSocket通信
"""
import json
import uuid
import time
import threading
from typing import Optional, Callable
import websocket


class NlsSpeechRecognizer:
    """语音识别客户端"""
    
    def __init__(
        self,
        url: str,
        token: str,
        appkey: str,
        on_start: Optional[Callable] = None,
        on_result_changed: Optional[Callable] = None,
        on_completed: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        callback_args: list = None
    ):
        self.url = url
        self.token = token
        self.appkey = appkey
        self.on_start = on_start
        self.on_result_changed = on_result_changed
        self.on_completed = on_completed
        self.on_error = on_error
        self.on_close = on_close
        self.callback_args = callback_args or []
        
        self.ws = None
        self.task_id = str(uuid.uuid4()).replace('-', '')  # 移除连字符
        self.started = False
    
    def start(
        self,
        aformat="pcm",
        sample_rate=16000,
        ch=1,
        enable_intermediate_result=False,
        enable_punctuation_prediction=True,
        enable_inverse_text_normalization=True,
        timeout=10,
        **kwargs
    ):
        """开始识别"""
        # 构建请求头（message_id 必须是32位十六进制，不带连字符）
        header = {
            "message_id": str(uuid.uuid4()).replace('-', ''),  # 移除连字符
            "task_id": self.task_id,
            "namespace": "SpeechRecognizer",
            "name": "StartRecognition",
            "appkey": self.appkey
        }
        
        # 构建请求体
        payload = {
            "format": aformat,
            "sample_rate": sample_rate,
            "enable_intermediate_result": enable_intermediate_result,
            "enable_punctuation_prediction": enable_punctuation_prediction,
            "enable_inverse_text_normalization": enable_inverse_text_normalization
        }
        
        # 创建WebSocket连接
        ws_url = f"{self.url}?token={self.token}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=self._on_open
        )
        
        # 保存启动参数
        self.start_message = {
            "header": header,
            "payload": payload
        }
        
        # 在后台线程中运行
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        # 等待连接建立
        time.sleep(1)
        return True
    
    def send_audio(self, audio_data: bytes):
        """发送音频数据"""
        if self.ws and self.started:
            self.ws.send(audio_data, opcode=websocket.ABNF.OPCODE_BINARY)
            return True
        return False
    
    def stop(self, timeout=10):
        """停止识别"""
        if self.ws:
            # 发送停止消息（message_id 必须是32位十六进制，不带连字符）
            header = {
                "message_id": str(uuid.uuid4()).replace('-', ''),  # 移除连字符
                "task_id": self.task_id,
                "namespace": "SpeechRecognizer",
                "name": "StopRecognition",
                "appkey": self.appkey
            }
            
            message = {"header": header}
            self.ws.send(json.dumps(message))
            time.sleep(0.5)
            return True
        return False
    
    def shutdown(self):
        """关闭连接"""
        if self.ws:
            try:
                self.ws.close()
                # ✅ 等待线程结束，避免资源泄漏
                if hasattr(self, 'ws_thread') and self.ws_thread.is_alive():
                    self.ws_thread.join(timeout=2)
            except Exception as e:
                print(f"[NLS-ASR] 关闭 WebSocket 时出错: {e}")
            finally:
                self.ws = None
    
    def _on_open(self, ws):
        """连接建立"""
        # 发送开始识别消息
        ws.send(json.dumps(self.start_message))
    
    def _on_message(self, ws, message):
        """接收消息"""
        try:
            msg = json.loads(message)
            name = msg.get("header", {}).get("name", "")
            
            if name == "RecognitionStarted":
                self.started = True
                if self.on_start:
                    self.on_start(message, *self.callback_args)
            
            elif name == "RecognitionResultChanged":
                if self.on_result_changed:
                    self.on_result_changed(message, *self.callback_args)
            
            elif name == "RecognitionCompleted":
                if self.on_completed:
                    self.on_completed(message, *self.callback_args)
            
            elif name == "TaskFailed":
                if self.on_error:
                    self.on_error(message, *self.callback_args)
        
        except Exception as e:
            if self.on_error:
                self.on_error(str(e), *self.callback_args)
    
    def _on_error(self, ws, error):
        """错误处理"""
        if self.on_error:
            self.on_error(str(error), *self.callback_args)
    
    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        if self.on_close:
            self.on_close(*self.callback_args)


class NlsSpeechSynthesizer:
    """语音合成客户端"""
    
    def __init__(
        self,
        url: str,
        token: str,
        appkey: str,
        long_tts: bool = False,
        on_metainfo: Optional[Callable] = None,
        on_data: Optional[Callable] = None,
        on_completed: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_close: Optional[Callable] = None,
        callback_args: list = None
    ):
        self.url = url
        self.token = token
        self.appkey = appkey
        self.long_tts = long_tts
        self.on_metainfo = on_metainfo
        self.on_data = on_data
        self.on_completed = on_completed
        self.on_error = on_error
        self.on_close = on_close
        self.callback_args = callback_args or []
        
        self.ws = None
        self.task_id = str(uuid.uuid4()).replace('-', '')  # 移除连字符
        self.completed_event = threading.Event()
    
    def start(
        self,
        text: str,
        aformat="wav",
        voice="xiaoyun",
        sample_rate=16000,
        volume=50,
        speech_rate=0,
        pitch_rate=0,
        wait_complete=True,
        **kwargs
    ):
        """开始合成"""
        # 构建请求（message_id 必须是32位十六进制，不带连字符）
        header = {
            "message_id": str(uuid.uuid4()).replace('-', ''),  # 移除连字符
            "task_id": self.task_id,
            "namespace": "SpeechSynthesizer",
            "name": "StartSynthesis",
            "appkey": self.appkey
        }
        
        payload = {
            "text": text,
            "format": aformat,
            "voice": voice,
            "sample_rate": sample_rate,
            "volume": volume,
            "speech_rate": speech_rate,
            "pitch_rate": pitch_rate
        }
        
        # 创建WebSocket连接
        ws_url = f"{self.url}?token={self.token}"
        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
            on_open=lambda ws: ws.send(json.dumps({"header": header, "payload": payload}))
        )
        
        # 在后台线程中运行
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()
        
        # 等待完成
        if wait_complete:
            self.completed_event.wait(timeout=60)
        
        return True
    
    def shutdown(self):
        """关闭连接"""
        if self.ws:
            try:
                self.ws.close()
                # ✅ 等待线程结束，避免资源泄漏
                if hasattr(self, 'ws_thread') and self.ws_thread.is_alive():
                    self.ws_thread.join(timeout=2)
            except Exception as e:
                print(f"[NLS-TTS] 关闭 WebSocket 时出错: {e}")
            finally:
                self.ws = None
    
    def _on_message(self, ws, message):
        """接收消息"""
        # 检查是否是二进制数据（音频）
        if isinstance(message, bytes):
            if self.on_data:
                self.on_data(message, *self.callback_args)
        else:
            try:
                msg = json.loads(message)
                name = msg.get("header", {}).get("name", "")
                
                if name == "MetaInfo":
                    if self.on_metainfo:
                        self.on_metainfo(message, *self.callback_args)
                
                elif name == "SynthesisCompleted":
                    if self.on_completed:
                        self.on_completed(message, *self.callback_args)
                    self.completed_event.set()
                
                elif name == "TaskFailed":
                    if self.on_error:
                        self.on_error(message, *self.callback_args)
                    self.completed_event.set()
            
            except Exception as e:
                if self.on_error:
                    self.on_error(str(e), *self.callback_args)
    
    def _on_error(self, ws, error):
        """错误处理"""
        if self.on_error:
            self.on_error(str(error), *self.callback_args)
        self.completed_event.set()
    
    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭"""
        if self.on_close:
            self.on_close(*self.callback_args)
        self.completed_event.set()


# 模拟nls模块
class NlsModule:
    """模拟nls模块"""
    NlsSpeechRecognizer = NlsSpeechRecognizer
    NlsSpeechSynthesizer = NlsSpeechSynthesizer
    
    @staticmethod
    def enableTrace(enable: bool):
        """启用/禁用跟踪"""
        pass


# 创建模块实例
nls = NlsModule()
