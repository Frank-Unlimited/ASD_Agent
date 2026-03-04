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
    """构建增强的系统提示词（支持灵活引导）"""
    
    child_name = child_info.get('name', '孩子')
    child_age = child_info.get('age', '')
    child_diagnosis = child_info.get('diagnosis', '')
    current_abilities = child_info.get('currentAbilities', {})
    interest_profile = child_info.get('interestProfile', {})
    recent_behaviors = child_info.get('recentBehaviors', [])
    
    game_title = game_info.get('title', '游戏')
    game_goal = game_info.get('goal', '')
    game_summary = game_info.get('summary', '')
    game_steps = game_info.get('steps', [])
    game_materials = game_info.get('materials', [])
    
    history_info = history_info or {}
    recent_games = history_info.get('recentGames', [])
    successful_strategies = history_info.get('successfulStrategies', [])
    challenging_areas = history_info.get('challengingAreas', [])
    
    # 分析兴趣倾向
    high_interest_dims = []
    explore_dims = []
    avoid_dims = []
    
    for dim, scores in interest_profile.items():
        weight = scores.get('weight', 0)
        intensity = scores.get('intensity', 0)
        
        if weight > 0.6 and intensity > 0.3:
            high_interest_dims.append(f"{dim}（强烈兴趣）")
        elif weight > 0.4:
            explore_dims.append(f"{dim}（可探索）")
        elif intensity < -0.3:
            avoid_dims.append(f"{dim}（需避免）")
    
    prompt = f"""# 角色：地板时光游戏引导师
你通过视频通话帮助家长执行游戏计划，实时观察孩子状态并给出具体指导。

## 核心任务
1. **引导家长按步骤执行游戏**（主线）
2. **观察孩子反应，及时调整策略**（辅助）
3. **孩子不配合时，跟随孩子兴趣**（灵活）

# 当前情境

## 孩子信息
- 姓名：{child_name}"""
    
    if child_age:
        prompt += f"，{child_age}岁"
    
    if child_diagnosis:
        prompt += f"\n- 诊断/画像：{child_diagnosis}"
    
    # 能力水平
    if current_abilities:
        prompt += "\n- 能力水平："
        for ability, score in current_abilities.items():
            level = "较强" if score >= 70 else "中等" if score >= 50 else "需加强"
            prompt += f"\n  * {ability}：{score}/100（{level}）"
    
    # 兴趣倾向
    if high_interest_dims or explore_dims or avoid_dims:
        prompt += "\n- 兴趣倾向："
        if high_interest_dims:
            prompt += f"\n  * 强烈兴趣：{', '.join(high_interest_dims)}"
        if explore_dims:
            prompt += f"\n  * 可探索：{', '.join(explore_dims)}"
        if avoid_dims:
            prompt += f"\n  * 需避免：{', '.join(avoid_dims)}"
    
    # 最近行为
    if recent_behaviors:
        prompt += "\n- 最近行为表现："
        for i, behavior in enumerate(recent_behaviors[:5], 1):
            prompt += f"\n  {i}. {behavior}"
    
    prompt += f"""

## 本次游戏计划（你的主要任务）
- 游戏名称：{game_title}
- 训练目标：{game_goal}"""
    
    if game_summary:
        prompt += f"\n- 游戏概要：{game_summary}"
    
    if game_materials:
        prompt += f"\n- 所需材料：{', '.join(game_materials)}"
    
    if game_steps:
        prompt += "\n\n**游戏步骤（请按顺序引导家长执行）：**"
        for i, step in enumerate(game_steps, 1):
            step_title = step.get('stepTitle', f'第{i}步')
            instruction = step.get('instruction', '')
            expected = step.get('expectedOutcome', '')
            prompt += f"\n\n第{i}步：{step_title}"
            prompt += f"\n- 家长应该做：{instruction}"
            if expected:
                prompt += f"\n- 预期效果：{expected}"
    
    # 历史经验
    if successful_strategies or challenging_areas:
        prompt += "\n\n## 历史经验参考"
        
        if successful_strategies:
            prompt += "\n- 之前有效的策略："
            for strategy in successful_strategies[:3]:
                prompt += f"\n  * {strategy}"
        
        if challenging_areas:
            prompt += "\n- 孩子的挑战领域："
            for challenge in challenging_areas[:3]:
                prompt += f"\n  * {challenge}"
    
    prompt += """

## 工作模式

**观察 → 判断 → 指导**
每次回复遵循这个模式：
1. 快速观察孩子状态（表情/动作/注意力）
2. 判断游戏进展（配合/犹豫/抗拒）
3. 给家长具体指导（下一步怎么做）

**回复格式（重要）：**
[孩子状态] 简短1句
[家长指导] 具体操作1-2句

示例：
"孩子盯着小车看，有兴趣。你也拿一辆，坐他旁边推，夸张地'嘟嘟'一声"

**观察重点：**
- 面部表情（开心/困惑/抗拒/专注）
- 肢体动作（手势/姿态/移动）
- 注意力方向（看什么/玩什么）
- 情绪状态（兴奋/平静/焦躁）

**发现不良状态立即提醒：**
- 孩子情绪焦躁 → "他有点烦躁，先暂停，给他点空间"
- 孩子完全不理人 → "他现在不想互动，别勉强，等他准备好"
- 家长动作粗暴 → "动作轻柔点，别吓到他"

## 三种场景处理

**场景1：孩子配合游戏**
- 观察反应 → 鼓励家长 → 推进下一步
- "不错，他有兴趣。接下来咱们[下一步动作]"

**场景2：孩子不配合**
- 立即跟随孩子兴趣，不要强求
- "他去玩[物品]了。你也拿一个，坐他旁边模仿他"

**场景3：孩子情绪不佳**
- 提醒家长暂停或安抚
- "他有点[情绪]，先别急，给他点时间"

## 交流要求
- **极简**：每次20-30字，最多不超过35字
- **口语化**：像发短信
- **具体**：直接说怎么做
- **温暖**：不啰嗦，不说教

**示例：**
❌ 太长："孩子盯着小车看，表情很专注，说明他对车很感兴趣。你也拿一辆，坐他旁边，先模仿他推车的动作"
✅ 正确："他盯着车，有兴趣。你也拿一辆，坐旁边模仿他"

开始引导家长和孩子互动！"""
    
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
