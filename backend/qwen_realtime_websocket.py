"""
Qwen-Omni-Realtime WebSocket 服务器
使用官方 Python SDK，通过 WebSocket 暴露给前端
"""

import asyncio
import websockets
import json
import base64
import os
import time
from dashscope.audio.qwen_omni import *
import dashscope

# API Key
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY', 'sk-5cd70747046b4cf787793bb6ee28cb44')

PORT = 8766


class RealtimeCallback(OmniRealtimeCallback):
    """回调处理器"""
    
    def __init__(self, websocket):
        self.websocket = websocket
        self.loop = asyncio.get_event_loop()
    
    def on_open(self):
        print('[Callback] Connection opened')
        # 通知前端连接已建立
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(json.dumps({
                'type': 'connection.opened'
            })),
            self.loop
        )
    
    def on_close(self, close_status_code, close_msg):
        print(f'[Callback] Connection closed: {close_status_code} - {close_msg}')
        # 通知前端连接已关闭
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(json.dumps({
                'type': 'connection.closed',
                'code': close_status_code,
                'message': close_msg
            })),
            self.loop
        )
    
    def on_event(self, response):
        """处理所有事件"""
        event_type = response.get('type')
        
        # 如果是错误事件，打印完整信息
        if event_type == 'error':
            print(f'[Callback] ⚠️  Error event: {response}')
        else:
            print(f'[Callback] Event: {event_type}')
        
        # 转发所有事件到前端
        asyncio.run_coroutine_threadsafe(
            self.websocket.send(json.dumps(response)),
            self.loop
        )


async def handle_client(websocket):
    """处理客户端连接"""
    print(f'[Server] Client connected from {websocket.remote_address}')
    
    conversation = None
    callback = RealtimeCallback(websocket)
    last_video_time = 0  # 记录上次发送视频帧的时间
    pending_video_frame = None  # 缓存待发送的视频帧
    
    try:
        # 创建会话（使用最新的 turbo 模型，支持视频）
        conversation = OmniRealtimeConversation(
            model='qwen-omni-turbo-realtime-latest',
            callback=callback,
            url="wss://dashscope.aliyuncs.com/api-ws/v1/realtime"
        )
        
        print('[Server] Connecting to Qwen Realtime API...')
        conversation.connect()
        
        # 等待一小段时间让连接建立
        await asyncio.sleep(0.5)
        
        # 更新会话配置
        print('[Server] Updating session...')
        conversation.update_session(
            output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
            voice='Cherry',
            input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
            output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
            enable_input_audio_transcription=True,
            input_audio_transcription_model='gummy-realtime-v1',
            enable_turn_detection=True,
            turn_detection_type='server_vad',
        )
        
        print('[Server] Session ready, waiting for audio...')
        
        # 处理客户端消息
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                if msg_type == 'audio':
                    # 接收音频数据（已经是 base64 编码）
                    audio_b64 = data.get('audio')
                    if audio_b64:
                        conversation.append_audio(audio_b64)
                        
                        # 在发送音频后，如果有待发送的视频帧，一起发送
                        if pending_video_frame:
                            try:
                                current_time = time.time()
                                if current_time - last_video_time >= 2.0:
                                    print(f'[Server] 发送视频帧（跟随音频），大小: {len(pending_video_frame)} 字符')
                                    conversation.append_video(pending_video_frame)
                                    print('[Server] 视频帧发送成功')
                                    last_video_time = current_time
                                    pending_video_frame = None
                            except Exception as e:
                                print(f'[Server] ⚠️  发送视频帧失败: {type(e).__name__}: {e}')
                                import traceback
                                traceback.print_exc()
                
                elif msg_type == 'image':
                    # 接收视频帧（base64 编码的 JPEG）
                    # 不立即发送，而是缓存起来，等待下次发送音频时一起发送
                    image_b64 = data.get('image')
                    if image_b64:
                        # 移除 data:image/jpeg;base64, 前缀（如果有）
                        if image_b64.startswith('data:'):
                            image_b64 = image_b64.split(',', 1)[1]
                        
                        # 缓存视频帧
                        pending_video_frame = image_b64
                        print(f'[Server] 缓存视频帧，大小: {len(image_b64)} 字符')
                        
                elif msg_type == 'ping':
                    # 心跳
                    await websocket.send(json.dumps({'type': 'pong'}))
                
                else:
                    print(f'[Server] Unknown message type: {msg_type}')
                    
            except json.JSONDecodeError:
                print('[Server] Invalid JSON message')
            except Exception as e:
                print(f'[Server] Error processing message: {e}')
    
    except Exception as e:
        print(f'[Server] Error: {e}')
        await websocket.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))
    
    finally:
        if conversation:
            print('[Server] Closing conversation...')
            conversation.close()
        print(f'[Server] Client disconnected')


async def main():
    """启动服务器"""
    print(f'🚀 Starting Qwen Realtime WebSocket Server on port {PORT}...')
    print(f'📡 Using API Key: {dashscope.api_key[:10]}...')
    
    async with websockets.serve(handle_client, 'localhost', PORT):
        print(f'✅ Server running on ws://localhost:{PORT}')
        print('Press Ctrl+C to stop')
        await asyncio.Future()  # run forever


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n⏹️  Server stopped')
