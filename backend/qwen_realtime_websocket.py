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
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# API Key（从环境变量读取）
dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')

if not dashscope.api_key:
    raise ValueError('DASHSCOPE_API_KEY environment variable is not set')

PORT = 8766


def build_system_prompt(child_info: dict, game_info: dict, history_info: dict = None) -> str:
    """构建简化的系统提示词（专注处理孩子分心）"""
    
    child_name = child_info.get('name', '孩子')
    game_title = game_info.get('title', '游戏')
    game_goal = game_info.get('goal', '')
    game_steps = game_info.get('steps', [])
    game_materials = game_info.get('materials', [])
    
    prompt = f"""# 角色：地板时光引导师

你通过视频通话观察孩子，当孩子注意力分散时，引导家长用地板时光的方式处理。

## 当前情况
- 孩子：{child_name}
- 游戏：{game_title}
- 目标：{game_goal}"""
    
    if game_materials:
        prompt += f"\n- 材料：{', '.join(game_materials)}"
    
    if game_steps:
        prompt += "\n\n**游戏步骤（了解这些，才能在孩子分心时找到回归的桥梁）：**"
        for i, step in enumerate(game_steps, 1):
            step_title = step.get('stepTitle', f'第{i}步')
            instruction = step.get('instruction', '')
            prompt += f"\n{i}. {step_title}：{instruction}"
    
    prompt += """

## 你的任务

**只在孩子注意力分散时说话**

当你看到孩子：
- 不看游戏材料，看别的东西
- 拿起其他物品
- 走开或转身
- 对游戏失去兴趣

**立即引导家长：**

### 四步法（Follow the Child's Lead）

**1. 观察**
看清孩子在做什么、看什么

**2. 跟随**
"你也[拿/看/做]一个，坐他旁边"

**3. 互动**
"[轻轻碰/慢慢靠近]，等他看你"

**4. 桥梁（关键！）**
结合游戏步骤和孩子当前兴趣，找到连接点：
- 如果孩子在玩车，游戏是积木 → "把积木当车库/停车场"
- 如果孩子在看窗外，游戏是认颜色 → "指外面的[颜色]，再指[游戏材料]"
- 如果孩子在排列物品，游戏是分类 → "你也排一个，按[游戏目标]排"

**核心思路：在孩子的兴趣中实现游戏目标**

### 回复格式

[孩子在做什么] 1句
[家长怎么做] 1-2句
[如何连接游戏] 1句（如果可能）

**示例：**

场景：游戏是"积木搭高塔"，孩子拿起小车
"他拿车了。你也拿一辆，推到他面前。等他看你，把积木当车库，'车开进去'"

场景：游戏是"认识颜色"，孩子看窗外的树
"他在看树。你也看，'绿色的树'。指指绿色的[游戏材料]，'这个也是绿色'"

场景：游戏是"物品分类"，孩子在排列玩具
"他在排玩具。你也排一个，慢慢按[大小/颜色]排，看他会不会跟着分"

场景：游戏是"角色扮演"，孩子趴在地上看蚂蚁
"他在看蚂蚁。蹲下来一起看。'小蚂蚁在搬家'，拿[游戏材料]，'我们也搬家'"

## 核心原则

✅ 跟随孩子的兴趣
✅ 在他的世界里建立连接
✅ 用他感兴趣的方式实现游戏目标
✅ 慢慢搭桥回到游戏步骤

❌ 不要强拉回游戏
❌ 不要说"回来""别走神"
❌ 不要打断孩子
❌ 不要放弃游戏目标（要巧妙融入）

## 何时说话

**说话：**
- 孩子明显分心超过5秒
- 家长不知道怎么办
- 家长试图强拉孩子

**不说话：**
- 孩子在玩游戏
- 家长正在互动
- 家长在哄孩子

## 语言要求

- 20-35字
- 口语化
- 具体动作
- 温和语气

开始观察！"""
    
    return prompt


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
    session_initialized = False  # 标记会话是否已初始化
    is_speaking = False  # 是否正在说话
    silence_start_time = None  # 静音开始时间
    
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
        
        print('[Server] Connection established, waiting for init message...')
        
        # 处理客户端消息
        async for message in websocket:
            try:
                data = json.loads(message)
                msg_type = data.get('type')
                
                # 初始化会话（接收游戏和孩子信息）
                if msg_type == 'init' and not session_initialized:
                    child_info = data.get('childInfo', {})
                    game_info = data.get('gameInfo', {})
                    history_info = data.get('historyInfo', {})
                    
                    print(f'[Server] 收到初始化信息:')
                    print(f'  - 孩子: {child_info.get("name", "未知")}')
                    print(f'  - 游戏: {game_info.get("title", "未知")}')
                    print(f'  - 历史记录: {len(history_info.get("recentGames", []))} 个游戏')
                    
                    # 构建增强的系统提示词
                    system_prompt = build_system_prompt(child_info, game_info, history_info)
                    
                    # 更新会话配置（使用非 server_vad 模式，更稳定）
                    print('[Server] Updating session with enhanced system prompt...')
                    conversation.update_session(
                        output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
                        voice='Cherry',
                        input_audio_format=AudioFormat.PCM_16000HZ_MONO_16BIT,
                        output_audio_format=AudioFormat.PCM_24000HZ_MONO_16BIT,
                        enable_input_audio_transcription=True,
                        input_audio_transcription_model='gummy-realtime-v1',
                        enable_turn_detection=False,  # 关闭 server_vad，使用手动控制
                        instructions=system_prompt
                    )
                    
                    session_initialized = True
                    print('[Server] Session initialized, ready for audio/video...')
                    
                    # 通知前端初始化完成
                    await websocket.send(json.dumps({
                        'type': 'session.initialized'
                    }))
                    continue
                
                # 如果会话未初始化，忽略其他消息
                if not session_initialized:
                    print(f'[Server] ⚠️  Session not initialized, ignoring {msg_type} message')
                    continue
                
                if msg_type == 'audio':
                    # 接收音频数据（已经是 base64 编码）
                    audio_b64 = data.get('audio')
                    if audio_b64:
                        conversation.append_audio(audio_b64)
                        
                        # 在发送音频后，如果有待发送的视频帧，每 500ms 发送一次
                        if pending_video_frame:
                            try:
                                current_time = time.time()
                                if current_time - last_video_time >= 0.5:  # 改为 500ms
                                    conversation.append_video(pending_video_frame)
                                    last_video_time = current_time
                                    pending_video_frame = None
                            except Exception as e:
                                print(f'[Server] ⚠️  发送视频帧失败: {type(e).__name__}: {e}')
                
                elif msg_type == 'speech_start':
                    # 前端检测到语音开始
                    print('[Server] 🎤 用户开始说话')
                    is_speaking = True
                    silence_start_time = None
                
                elif msg_type == 'speech_end':
                    # 前端检测到语音结束
                    print('[Server] 🔇 用户停止说话')
                    is_speaking = False
                    silence_start_time = time.time()
                
                elif msg_type == 'commit':
                    # 前端主动请求提交（例如用户点击了"发送"按钮）
                    print('[Server] 📤 收到提交请求，创建响应')
                    conversation.commit()
                    conversation.create_response()
                    is_speaking = False
                    silence_start_time = None
                
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
