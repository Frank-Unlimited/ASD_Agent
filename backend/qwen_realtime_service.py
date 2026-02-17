"""
Qwen-Omni-Realtime 服务
完全基于官方 Python SDK 实现
"""

import os
import base64
import threading
import queue
import contextlib
from dashscope.audio.qwen_omni import *
import dashscope

# API Key
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-5cd70747046b4cf787793bb6ee28cb44')


class QwenRealtimeService:
    """Qwen Realtime 服务封装"""
    
    def __init__(self, voice='Cherry', model='qwen3-omni-flash-realtime'):
        self.voice = voice
        self.model = model
        self.conversation = None
        self.is_connected = False
        self.audio_queue = queue.Queue()
        
    def connect(self, callback):
        """建立连接"""
        print(f'[Qwen Realtime] Connecting with model: {self.model}')
        
        self.conversation = OmniRealtimeConversation(
            model=self.model,
            callback=callback,
            url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
        )
        
        self.conversation.connect()
        self.is_connected = True
        
    def update_session(self, instructions=None, enable_transcription=True):
        """更新会话配置"""
        if not self.conversation:
            raise Exception('Not connected')
        
        print('[Qwen Realtime] Updating session...')
        
        self.conversation.update_session(
            output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
            voice=self.voice,
            input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
            output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            enable_input_audio_transcription=enable_transcription,
            input_audio_transcription_model='gummy-realtime-v1' if enable_transcription else None,
            enable_turn_detection=True,
            turn_detection_type='server_vad',
        )
        
        if instructions:
            # 可以通过额外的 session.update 消息设置 instructions
            pass
    
    def send_audio(self, audio_bytes):
        """发送音频数据（PCM16, 16kHz, 单声道）"""
        if not self.conversation or not self.is_connected:
            return
        
        audio_b64 = base64.b64encode(audio_bytes).decode('ascii')
        self.conversation.append_audio(audio_b64)
    
    def close(self):
        """关闭连接"""
        if self.conversation:
            self.conversation.close()
            self.is_connected = False


class AudioPlayer:
    """音频播放器（用于播放 AI 响应的音频）"""
    
    def __init__(self, sample_rate=24000, chunk_size_ms=100):
        import pyaudio
        
        self.pya = pyaudio.PyAudio()
        self.sample_rate = sample_rate
        self.chunk_size_bytes = chunk_size_ms * sample_rate * 2 // 1000
        
        self.player_stream = self.pya.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True
        )
        
        self.raw_audio_buffer = queue.Queue()
        self.b64_audio_buffer = queue.Queue()
        self.status = 'playing'
        
        self.decoder_thread = threading.Thread(target=self._decoder_loop)
        self.player_thread = threading.Thread(target=self._player_loop)
        self.decoder_thread.start()
        self.player_thread.start()
    
    def _decoder_loop(self):
        """解码线程"""
        while self.status != 'stop':
            recv_audio_b64 = None
            with contextlib.suppress(queue.Empty):
                recv_audio_b64 = self.b64_audio_buffer.get(timeout=0.1)
            
            if recv_audio_b64 is None:
                continue
            
            recv_audio_raw = base64.b64decode(recv_audio_b64)
            
            # 将原始音频数据推入队列，按块处理
            for i in range(0, len(recv_audio_raw), self.chunk_size_bytes):
                chunk = recv_audio_raw[i:i + self.chunk_size_bytes]
                self.raw_audio_buffer.put(chunk)
    
    def _player_loop(self):
        """播放线程"""
        while self.status != 'stop':
            recv_audio_raw = None
            with contextlib.suppress(queue.Empty):
                recv_audio_raw = self.raw_audio_buffer.get(timeout=0.1)
            
            if recv_audio_raw is None:
                continue
            
            # 将块写入音频播放器
            self.player_stream.write(recv_audio_raw)
    
    def add_audio(self, audio_b64):
        """添加音频数据（base64 编码）"""
        self.b64_audio_buffer.put(audio_b64)
    
    def cancel_playing(self):
        """取消播放（清空缓冲区）"""
        self.b64_audio_buffer.queue.clear()
        self.raw_audio_buffer.queue.clear()
    
    def shutdown(self):
        """关闭播放器"""
        self.status = 'stop'
        self.decoder_thread.join()
        self.player_thread.join()
        self.player_stream.close()
        self.pya.terminate()


if __name__ == '__main__':
    # 测试代码
    print('Testing Qwen Realtime Service...')
    
    class TestCallback(OmniRealtimeCallback):
        def on_open(self):
            print('✅ Connected')
        
        def on_close(self, code, msg):
            print(f'❌ Closed: {code} - {msg}')
        
        def on_event(self, response):
            event_type = response.get('type')
            print(f'📨 Event: {event_type}')
    
    service = QwenRealtimeService()
    callback = TestCallback()
    
    service.connect(callback)
    service.update_session()
    
    print('Service ready!')
