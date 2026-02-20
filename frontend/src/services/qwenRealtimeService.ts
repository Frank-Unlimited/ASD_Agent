/**
 * Qwen-Omni-Realtime 服务（基于官方 Python SDK）
 * 通过 WebSocket 连接到 Python 后端
 */

export interface RealtimeCallbacks {
  onConnected?: () => void;
  onSessionCreated?: () => void;
  onSessionUpdated?: () => void;
  onDisconnected?: () => void;
  onError?: (error: Error) => void;
  onUserTranscript?: (transcript: string) => void;
  onAssistantTranscript?: (transcript: string) => void;
  onAssistantAudio?: (audioData: ArrayBuffer) => void;
  onSpeechStarted?: () => void;
  onSpeechStopped?: () => void;
  onResponseStarted?: () => void; // AI 开始新的回复
  onResponseCompleted?: (fullTranscript: string) => void; // AI 回复完成
}

export interface ChildInfo {
  name: string;
  age?: string;
  interests?: string[];
  abilities?: Record<string, string>;
}

export interface GameInfo {
  name: string;
  description?: string;
  goals?: string[];
  steps?: string[];
}

export interface RealtimeInitOptions {
  childInfo: {
    name: string;
    age: number;
    diagnosis: string;
    currentAbilities: Record<string, number>;
    interestProfile: Record<string, { weight: number; intensity: number }>;
    recentBehaviors: string[];
  };
  gameInfo: {
    title: string;
    goal: string;
    summary: string;
    steps: Array<{
      stepTitle: string;
      instruction: string;
      expectedOutcome: string;
    }>;
    materials: string[];
    currentStep: number;
  };
  historyInfo: {
    recentGames: Array<{
      title: string;
      result: string;
      evaluation: {
        score: number;
        summary: string;
      };
    }>;
    successfulStrategies: string[];
    challengingAreas: string[];
  };
}

class QwenRealtimeService {
  private ws: WebSocket | null = null;
  private callbacks: RealtimeCallbacks = {};
  private isConnected: boolean = false;
  private serverUrl: string;
  private currentAssistantTranscript: string = ''; // 跟踪当前 AI 回复的完整文本
  
  constructor() {
    // 连接到 Python WebSocket 服务器
    this.serverUrl = 'ws://localhost:8766';
  }
  
  /**
   * 建立连接
   */
  async connect(callbacks: RealtimeCallbacks, initOptions: RealtimeInitOptions): Promise<void> {
    if (this.isConnected) {
      console.warn('[Qwen Realtime] 已经连接');
      return;
    }
    
    this.callbacks = callbacks;
    
    return new Promise((resolve, reject) => {
      try {
        console.log('[Qwen Realtime] 连接到服务器:', this.serverUrl);
        this.ws = new WebSocket(this.serverUrl);
        
        this.ws.onopen = () => {
          console.log('[Qwen Realtime] WebSocket 连接已建立');
          this.isConnected = true;
          
          // 发送初始化信息
          console.log('[Qwen Realtime] 发送初始化信息:', initOptions);
          this.ws!.send(JSON.stringify({
            type: 'init',
            childInfo: initOptions.childInfo,
            gameInfo: initOptions.gameInfo,
            historyInfo: initOptions.historyInfo
          }));
          
          if (this.callbacks.onConnected) {
            this.callbacks.onConnected();
          }
          
          resolve();
        };
        
        this.ws.onmessage = async (event) => {
          let data = event.data;
          if (data instanceof Blob) {
            data = await data.text();
          }
          this.handleMessage(data);
        };
        
        this.ws.onerror = (error) => {
          console.error('[Qwen Realtime] WebSocket 错误:', error);
          const err = new Error('WebSocket 连接错误');
          if (this.callbacks.onError) {
            this.callbacks.onError(err);
          }
          reject(err);
        };
        
        this.ws.onclose = (event) => {
          console.log('[Qwen Realtime] WebSocket 连接已关闭 - Code:', event.code, 'Reason:', event.reason);
          this.isConnected = false;
          if (this.callbacks.onDisconnected) {
            this.callbacks.onDisconnected();
          }
        };
        
      } catch (error) {
        console.error('[Qwen Realtime] 连接失败:', error);
        reject(error);
      }
    });
  }
  
  /**
   * 处理服务器消息
   */
  private handleMessage(data: string): void {
    try {
      const message = JSON.parse(data);
      const eventType = message.type;
      
      console.log('[Qwen Realtime] 收到事件:', eventType);
      
      switch (eventType) {
        case 'connection.opened':
          // Python 后端连接已建立
          break;
        
        case 'session.initialized':
          console.log('[Qwen Realtime] 会话已初始化（包含游戏和孩子信息）');
          if (this.callbacks.onSessionCreated) {
            this.callbacks.onSessionCreated();
          }
          break;
          
        case 'session.created':
          console.log('[Qwen Realtime] 会话已创建:', message.session?.id);
          break;
          
        case 'session.updated':
          console.log('[Qwen Realtime] 会话配置已更新');
          if (this.callbacks.onSessionUpdated) {
            this.callbacks.onSessionUpdated();
          }
          break;
          
        case 'input_audio_buffer.speech_started':
          console.log('[Qwen Realtime] 检测到语音开始');
          if (this.callbacks.onSpeechStarted) {
            this.callbacks.onSpeechStarted();
          }
          break;
          
        case 'input_audio_buffer.speech_stopped':
          console.log('[Qwen Realtime] 检测到语音结束');
          if (this.callbacks.onSpeechStopped) {
            this.callbacks.onSpeechStopped();
          }
          break;
          
        case 'conversation.item.input_audio_transcription.completed':
          const userTranscript = message.transcript;
          console.log('[Qwen Realtime] 用户:', userTranscript);
          if (this.callbacks.onUserTranscript) {
            this.callbacks.onUserTranscript(userTranscript);
          }
          break;
        
        case 'response.created':
          // AI 开始新的回复
          console.log('[Qwen Realtime] AI 开始新的回复');
          this.currentAssistantTranscript = ''; // 重置累积的文本
          if (this.callbacks.onResponseStarted) {
            this.callbacks.onResponseStarted();
          }
          break;
          
        case 'response.audio_transcript.delta':
          const assistantDelta = message.delta;
          this.currentAssistantTranscript += assistantDelta; // 累积文本
          if (this.callbacks.onAssistantTranscript) {
            this.callbacks.onAssistantTranscript(assistantDelta);
          }
          break;
          
        case 'response.audio.delta':
          // 解码 base64 音频数据
          const audioBase64 = message.delta;
          const audioData = this.base64ToArrayBuffer(audioBase64);
          if (this.callbacks.onAssistantAudio) {
            this.callbacks.onAssistantAudio(audioData);
          }
          break;
          
        case 'response.audio_transcript.done':
          console.log('[Qwen Realtime] 助手:', message.transcript);
          break;
          
        case 'response.done':
          console.log('[Qwen Realtime] 响应完成');
          // AI 回复完成，传递完整文本
          if (this.callbacks.onResponseCompleted) {
            this.callbacks.onResponseCompleted(this.currentAssistantTranscript);
          }
          break;
          
        case 'error':
          const errorMsg = message.message || message.error?.message || JSON.stringify(message);
          console.error('[Qwen Realtime] 服务器错误:', errorMsg);
          if (this.callbacks.onError) {
            this.callbacks.onError(new Error(errorMsg));
          }
          break;
          
        case 'connection.closed':
          console.log('[Qwen Realtime] 后端连接已关闭:', message.code, message.message);
          break;
          
        default:
          // 忽略其他事件
          break;
      }
    } catch (error) {
      console.error('[Qwen Realtime] 解析消息失败:', error);
    }
  }
  
  /**
   * 发送音频数据（PCM16, 16kHz, 单声道）
   */
  sendAudio(audioData: ArrayBuffer): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[Qwen Realtime] WebSocket 未连接');
      return;
    }
    
    const base64Audio = this.arrayBufferToBase64(audioData);
    
    this.ws.send(JSON.stringify({
      type: 'audio',
      audio: base64Audio
    }));
  }
  
  /**
   * 发送通用消息
   */
  sendMessage(message: Record<string, any>): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[Qwen Realtime] WebSocket 未连接');
      return;
    }
    
    this.ws.send(JSON.stringify(message));
  }
  
  /**
   * 发送视频帧（JPEG 格式）
   */
  sendImage(imageDataUrl: string): void {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.error('[Qwen Realtime] WebSocket 未连接');
      return;
    }
    
    // 移除 data:image/jpeg;base64, 前缀
    const base64Image = imageDataUrl.replace(/^data:image\/\w+;base64,/, '');
    
    this.ws.send(JSON.stringify({
      type: 'image',
      image: base64Image
    }));
  }
  
  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }
  
  /**
   * ArrayBuffer 转 Base64
   */
  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  }
  
  /**
   * Base64 转 ArrayBuffer
   */
  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }
    return bytes.buffer;
  }
  
  /**
   * 检查是否已连接
   */
  isConnectionActive(): boolean {
    return this.isConnected && this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}

export const qwenRealtimeService = new QwenRealtimeService();
