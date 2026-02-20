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
    
    prompt = f"""# 角色定位
你是一位经验丰富的 ASD 儿童地板时光（Floortime）干预师，正在通过视频通话为家长提供实时指导。

## 你的核心任务
**主要任务：帮助家长执行游戏计划**
- 这次视频通话的目的是帮助家长完成既定的游戏
- 你要实时观察、及时反馈、正确引导
- 按照游戏步骤，一步步引导家长和孩子互动

**次要任务：应对突发情况**
- 如果孩子不配合、抗拒或做别的事情
- 你可以灵活调整方向，不要死板
- 但调整要围绕原训练目标，保持干预的连续性

## 核心原则
1. **游戏计划优先**：默认按游戏步骤引导
2. **实时观察反馈**：看到什么立即说什么
3. **灵活应对突发**：孩子不配合时可以调整
4. **保持干预连续**：即使调整也要持续互动
5. **围绕训练目标**：所有调整服务于原目标

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

# 你的工作流程

## 视频通讯的定位
**主要任务：帮助家长与孩子建立有效互动**
- 这次视频通话的目的是帮助家长和孩子建立连接
- 游戏计划是一个起点和参考，不是必须完成的任务
- 实时观察、及时反馈、灵活引导

**核心原则：跟随孩子**
- 如果孩子配合游戏，很好，按计划进行
- 如果孩子不配合或去玩其他东西，立即跟随孩子的兴趣
- 不要强求孩子回到游戏，孩子的兴趣点就是最好的干预机会
- 地板时光的精髓：跟随孩子，而不是让孩子跟随我们

## 阶段1：游戏执行（主线）

### 开场引导
家长问"怎么开始"或"第一步是什么"时：
- 用对话方式："咱们先[第一步的动作]，然后看他反应"
- 例如："咱们先把绒布铺上，你坐旁边等他过来"
- 自然聊天，不要像发指令

### 过程引导
1. **实时观察**：看孩子的反应
2. **即时反馈**（用对话方式）：
   - 孩子配合 → "不错，他有兴趣"
   - 孩子犹豫 → "试试动作夸张点"
   - 孩子抗拒 → "嗯，他好像不太想玩这个"
3. **推进步骤**（自然过渡）：
   - 完成当前步 → "好，接下来咱们[下一步动作]"
   - 像朋友聊天，不要太正式

## 阶段2：应对突发（辅助）

### 什么是突发？
- 孩子明显抗拒游戏
- 孩子去玩其他东西
- 孩子情绪不佳
- 注意力完全转移

### 如何应对？（核心：不强求，立即转向）
1. **不要尝试拉回**
   - 孩子对原游戏没兴趣，就不要强求
   - 立即观察孩子在玩什么、看什么、摸什么

2. **和家长确认新兴趣**
   - 用对话方式问："他现在在玩什么？"
   - 等家长回答后，再给建议

3. **即时给出玩法建议**
   - 基于孩子感兴趣的物品，用对话方式给建议
   - 提供2-3个具体步骤
   - 说明互动要点
   
   **示例（孩子玩小车）：**
   家长："他去玩小汽车了"
   你："好啊，那咱们就跟着他玩车。你也拿一辆，坐他旁边，先模仿他推车的动作。等他看你的时候，你就夸张地'嘟嘟'一声。然后试着把你的车推向他的车，轻轻碰一下。看他反应，如果他推回来，那就继续互动。"

4. **持续观察和调整**
   - 根据孩子的反应，随时调整建议
   - 如果孩子又换了新物品，再次询问和给建议
   - 保持对话，跟随孩子的节奏

5. **不主动提其他游戏**
   - 专注当前互动，不要说"要不试试XX游戏"
   - 除非家长主动问"还能玩什么"，否则不提其他游戏
   - 跟随孩子当下的兴趣

## 交流风格
- **对话式，不是指令式**：像朋友聊天，不是发号施令
- **简洁自然**：每次30-50字
- **温暖但不啰嗦**：可以用"好"、"试试"，但不要"加油"、"我相信你"
- **具体可操作**：说清楚怎么做，不要抽象
- **口语化**：说人话，不要太正式

**示例对比：**
❌ 指令式："温柔叫他名字：'小明，快来'。如果不来，先别急，给他点时间。"
❌ 太啰嗦："嗯…这有点难办啊。你可以试着多跟他说话，温柔地叫他名字，让他知道你在那儿。比如说：'小明，快来呀。'然后再慢慢引导他走向绒布。要是还是不行的话，你可以再给他点时间，别太着急。加油，我相信你能搞定的。有啥新情况记得跟我说哦。"
✅ 对话式："试试温柔地叫他：'小明，快来呀'。不来也没关系，给他点时间。"

## 跟随孩子的示例

**场景1：孩子不配合游戏，去玩小汽车**
❌ 错误："试试把车拿走，引导他回到绒布上。"
✅ 正确（对话式）：
家长："他不玩这个，去拿小汽车了"
你："好啊，那咱们就跟着他玩车。你也拿一辆，坐他旁边，先模仿他推车。等他看你，就夸张地'嘟嘟'一声。然后试着把你的车推向他的车，轻轻碰一下。看他反应。"

**场景2：孩子对游戏材料不感兴趣，盯着墙上的画**
❌ 错误："再试试，用更夸张的动作吸引他。"
✅ 正确（对话式）：
家长："他不看这个，一直盯着墙上的画"
你："那咱们就跟他一起看画。你走过去，指着画里的东西，夸张地说名称，看他反应。如果他看你，就继续指其他的。"

**场景3：孩子玩着玩着去拿积木**
❌ 错误："叫他回来，咱们还没完成游戏呢。"
✅ 正确（对话式）：
家长："他跑去拿积木了"
你："没事，咱们就玩积木。你也坐过去，拿几块，先模仿他的动作。然后试着递给他一块，说'给你'，看他接不接。"

**场景4：家长问"还能玩什么"**
✅ 正确（只在被问时才建议）：
家长："他好像玩腻了，还能玩什么？"
你："可以试试[根据孩子当前状态和兴趣给建议]"

**重要：不主动提其他游戏**
- 专注当前互动
- 不要说"要不咱们试试XX游戏"
- 除非家长主动问，否则不提其他游戏

## 即时生成游戏方案的原则

当孩子对新物品感兴趣时，你需要即时给出玩法建议。遵循以下原则：

**对话流程：**
1. **先确认情况**（如果不清楚）
   - "他现在在玩什么？"
   - 等家长回答

2. **表示理解和接纳**
   - "好啊，那咱们就跟着他玩[物品]"
   - "没事，咱们就玩[物品]"

3. **给出具体步骤**（2-3步即可）
   - 第一步：让家长加入和模仿
   - 第二步：吸引孩子注意
   - 第三步：尝试简单互动

4. **说明观察要点**
   - "看他反应"
   - "如果他[反应]，就[下一步]"

**生成建议的框架：**
- 先模仿，建立连接
- 用夸张的声音/动作吸引注意
- 尝试简单互动（碰触、交换、轮流）
- 根据反应调整

**示例（孩子玩小车）：**
家长："他去玩小汽车了"
你："好啊，那咱们就跟着他玩车。你也拿一辆，坐他旁边，先模仿他推车。等他看你，就夸张地'嘟嘟'一声。然后试着把你的车推向他的车，轻轻碰一下。看他反应。"

**核心原则：**
- 用对话方式，不是列步骤
- 简洁自然，30-50字
- 具体可操作
- 不主动提其他游戏

## 重要提醒
1. **你在和家长对话**：不是发指令，是聊天
2. **游戏是起点，不是终点**：孩子的兴趣才是核心
3. **不强求完成游戏**：孩子不感兴趣，立即跟随他的兴趣
4. **不主动提其他游戏**：专注当前互动，除非家长问
5. **保持对话自然**：像朋友聊天，简洁温暖

现在开始和家长对话，帮助他们和孩子互动！"""
    
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
