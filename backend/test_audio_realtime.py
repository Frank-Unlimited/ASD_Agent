"""
测试 Qwen-Omni-Realtime 音频功能
完全复刻官方示例
"""

import os
import base64
import signal
import sys
import time
import pyaudio
import contextlib
import threading
import queue
from dashscope.audio.qwen_omni import *
import dashscope

# API Key
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-5cd70747046b4cf787793bb6ee28cb44')

voice = 'Cherry'
conversation = None
pya = None
mic_stream = None
b64_player = None

class B64PCMPlayer:
    def __init__(self, pya: pyaudio.PyAudio, sample_rate=24000, chunk_size_ms=100):
        self.pya = pya
        self.sample_rate = sample_rate
        self.chunk_size_bytes = chunk_size_ms * sample_rate * 2 // 1000
        self.player_stream = pya.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            output=True
        )
        self.raw_audio_buffer: queue.Queue = queue.Queue()
        self.b64_audio_buffer: queue.Queue = queue.Queue()
        self.status_lock = threading.Lock()
        self.status = 'playing'
        self.decoder_thread = threading.Thread(target=self.decoder_loop)
        self.player_thread = threading.Thread(target=self.player_loop)
        self.decoder_thread.start()
        self.player_thread.start()
        self.complete_event: threading.Event = None

    def decoder_loop(self):
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

    def player_loop(self):
        while self.status != 'stop':
            recv_audio_raw = None
            with contextlib.suppress(queue.Empty):
                recv_audio_raw = self.raw_audio_buffer.get(timeout=0.1)
            if recv_audio_raw is None:
                if self.complete_event:
                    self.complete_event.set()
                continue
            # 将块写入pyaudio音频播放器，等待播放完这个块
            self.player_stream.write(recv_audio_raw)

    def cancel_playing(self):
        self.b64_audio_buffer.queue.clear()
        self.raw_audio_buffer.queue.clear()

    def add_data(self, data):
        self.b64_audio_buffer.put(data)

    def wait_for_complete(self):
        self.complete_event = threading.Event()
        self.complete_event.wait()
        self.complete_event = None

    def shutdown(self):
        self.status = 'stop'
        self.decoder_thread.join()
        self.player_thread.join()
        self.player_stream.close()


class MyCallback(OmniRealtimeCallback):
    def on_open(self) -> None:
        global pya
        global mic_stream
        global b64_player
        print('✅ connection opened, init microphone')
        pya = pyaudio.PyAudio()
        mic_stream = pya.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True
        )
        b64_player = B64PCMPlayer(pya)

    def on_close(self, close_status_code, close_msg) -> None:
        print('❌ connection closed with code: {}, msg: {}, destroy microphone'.format(
            close_status_code, close_msg))
        sys.exit(0)

    def on_event(self, response: str) -> None:
        try:
            global conversation
            global b64_player
            type = response['type']
            
            if 'session.created' == type:
                print('📝 start session: {}'.format(response['session']['id']))
            
            if 'session.updated' == type:
                print('✅ session updated')
            
            if 'conversation.item.input_audio_transcription.completed' == type:
                print('🎤 question: {}'.format(response['transcript']))
            
            if 'response.audio_transcript.delta' == type:
                text = response['delta']
                print("💬 got llm response delta: {}".format(text))
            
            if 'response.audio.delta' == type:
                recv_audio_b64 = response['delta']
                b64_player.add_data(recv_audio_b64)
            
            if 'input_audio_buffer.speech_started' == type:
                print('🔊 ======VAD Speech Start======')
                b64_player.cancel_playing()
            
            if 'response.done' == type:
                print('✅ ======RESPONSE DONE======')
                print('[Metric] response: {}, first text delay: {}, first audio delay: {}'.format(
                    conversation.get_last_response_id(),
                    conversation.get_last_first_text_delay(),
                    conversation.get_last_first_audio_delay(),
                ))
        except Exception as e:
            print('[Error] {}'.format(e))
            return


if __name__ == '__main__':
    print('🚀 Initializing Qwen-Omni-Realtime...')
    print('API Key:', dashscope.api_key[:10] + '...')
    
    callback = MyCallback()
    conversation = OmniRealtimeConversation(
        model='qwen3-omni-flash-realtime',
        callback=callback,
        url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
    )
    
    print('🔌 Connecting...')
    conversation.connect()
    
    print('⚙️  Updating session...')
    conversation.update_session(
        output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
        voice=voice,
        input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
        output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
        enable_input_audio_transcription=True,
        input_audio_transcription_model='gummy-realtime-v1',
        enable_turn_detection=True,
        turn_detection_type='server_vad',
    )

    def signal_handler(sig, frame):
        print('\n⏹️  Ctrl+C pressed, stop recognition ...')
        conversation.close()
        if b64_player:
            b64_player.shutdown()
        print('✅ omni realtime stopped.')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    
    print("🎙️  Press 'Ctrl+C' to stop conversation...")
    print("📢 Start speaking now!")
    
    # 等待麦克风初始化
    time.sleep(1)
    
    packet_count = 0
    while True:
        if mic_stream:
            try:
                audio_data = mic_stream.read(3200, exception_on_overflow=False)
                audio_b64 = base64.b64encode(audio_data).decode('ascii')
                conversation.append_audio(audio_b64)
                
                # 打印前几个包的信息
                if packet_count < 3:
                    print(f'📤 Sent audio packet #{packet_count + 1}: {len(audio_data)} bytes, {len(audio_b64)} base64 chars')
                    packet_count += 1
                
            except Exception as e:
                print(f'❌ Error reading audio: {e}')
                break
        else:
            break
