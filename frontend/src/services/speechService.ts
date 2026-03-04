/**
 * 语音服务 - 录音 + 阿里云 ASR
 */

interface SpeechConfig {
  appkey: string;
  token: string;
  url: string;
}

interface ASRResult {
  success: boolean;
  text: string;
  error?: string;
}

class SpeechService {
  private config: SpeechConfig;
  private audioContext: AudioContext | null = null;
  private audioWorkletNode: AudioWorkletNode | null = null;
  private mediaStream: MediaStream | null = null;
  private audioChunks: Int16Array[] = [];
  private isRecording: boolean = false;
  private currentAmplitude: number = 0;

  constructor() {
    this.config = {
      appkey: import.meta.env.VITE_ALIYUN_NLS_APPKEY || '',
      token: import.meta.env.VITE_ALIYUN_NLS_TOKEN || '',
      url: 'wss://nls-gateway-cn-shanghai.aliyuncs.com/ws/v1'
    };

    if (!this.config.appkey || !this.config.token) {
      console.warn('阿里云语音服务未配置，请在 .env 中设置 VITE_ALIYUN_NLS_APPKEY 和 VITE_ALIYUN_NLS_TOKEN');
    }
  }

  /**
   * 开始录音（使用 AudioWorklet）
   */
  async startRecording(): Promise<void> {
    try {
      // 请求麦克风权限
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        } 
      });

      // 创建 AudioContext
      this.audioContext = new AudioContext({ sampleRate: 16000 });
      const source = this.audioContext.createMediaStreamSource(this.mediaStream);

      this.audioChunks = [];
      this.isRecording = true;

      // 尝试使用 AudioWorklet
      const supportsAudioWorklet = 'audioWorklet' in this.audioContext;

      if (supportsAudioWorklet) {
        try {
          console.log('[Speech] 使用 AudioWorklet 进行音频采集');
          
          await this.audioContext.audioWorklet.addModule('/audio-processor.js');
          
          this.audioWorkletNode = new AudioWorkletNode(
            this.audioContext,
            'audio-capture-processor'
          );

          this.audioWorkletNode.port.onmessage = (e) => {
            if (e.data.type === 'audio_data' && this.isRecording) {
              const pcm16 = new Int16Array(e.data.data);
              this.audioChunks.push(pcm16);
              this.currentAmplitude = e.data.maxAmplitude || 0;
            }
          };

          source.connect(this.audioWorkletNode);
          this.audioWorkletNode.connect(this.audioContext.destination);

          console.log('[Speech] AudioWorklet 录音已启动');
          return;

        } catch (workletError) {
          console.warn('[Speech] AudioWorklet 初始化失败，降级到 ScriptProcessor:', workletError);
        }
      } else {
        console.warn('[Speech] 浏览器不支持 AudioWorklet，使用 ScriptProcessor');
      }

      // 降级方案：ScriptProcessor
      const processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      processor.onaudioprocess = (e) => {
        if (!this.isRecording) return;

        const inputData = e.inputBuffer.getChannelData(0);
        
        // 计算音量
        let maxAmplitude = 0;
        for (let i = 0; i < inputData.length; i++) {
          const abs = Math.abs(inputData[i]);
          if (abs > maxAmplitude) maxAmplitude = abs;
        }
        this.currentAmplitude = maxAmplitude;

        // 转换为 PCM16
        const pcm16 = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          const s = Math.max(-1, Math.min(1, inputData[i]));
          pcm16[i] = s < 0 ? Math.floor(s * 0x8000) : Math.floor(s * 0x7FFF);
        }

        this.audioChunks.push(pcm16);
      };

      source.connect(processor);
      processor.connect(this.audioContext.destination);

      console.log('[Speech] ScriptProcessor 录音已启动');
    } catch (error) {
      console.error('[Speech] 录音失败:', error);
      throw new Error('无法访问麦克风，请检查权限设置');
    }
  }

  /**
   * 停止录音并返回 PCM 数据
   */
  async stopRecording(): Promise<ArrayBuffer> {
    this.isRecording = false;

    // 停止所有音轨
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
    }

    // 关闭 AudioContext
    if (this.audioWorkletNode) {
      this.audioWorkletNode.disconnect();
      this.audioWorkletNode = null;
    }

    if (this.audioContext) {
      await this.audioContext.close();
      this.audioContext = null;
    }

    // 合并所有 PCM 数据
    const totalLength = this.audioChunks.reduce((sum, chunk) => sum + chunk.length, 0);
    const mergedPCM = new Int16Array(totalLength);
    let offset = 0;
    for (const chunk of this.audioChunks) {
      mergedPCM.set(chunk, offset);
      offset += chunk.length;
    }

    console.log('[Speech] 录音完成，PCM 长度:', mergedPCM.length);
    return mergedPCM.buffer;
  }

  /**
   * 获取当前音量（用于实时显示）
   */
  getCurrentAmplitude(): number {
    return this.currentAmplitude;
  }

  /**
   * 调用阿里云 ASR 服务
   */
  async speechToText(pcmData: ArrayBuffer): Promise<ASRResult> {
    return new Promise((resolve) => {
      if (!this.config.appkey || !this.config.token) {
        resolve({
          success: false,
          text: '',
          error: '阿里云语音服务未配置'
        });
        return;
      }

      try {
        // 构建 WebSocket URL
        const url = `${this.config.url}?appkey=${this.config.appkey}&token=${this.config.token}`;
        const ws = new WebSocket(url);

        let result = '';
        let hasError = false;
        let recognitionStarted = false; // 标记识别是否已开始
        const taskId = this.generateTaskId(); // 使用同一个 task_id

        ws.onopen = () => {
          console.log('[Speech] WebSocket 连接成功');

          // 发送开始识别指令
          const startMessage = {
            header: {
              message_id: this.generateMessageId(),
              task_id: taskId,
              namespace: 'SpeechRecognizer',
              name: 'StartRecognition',
              appkey: this.config.appkey
            },
            payload: {
              format: 'pcm',
              sample_rate: 16000,
              enable_intermediate_result: false,
              enable_punctuation_prediction: true,
              enable_inverse_text_normalization: true
            }
          };

          ws.send(JSON.stringify(startMessage));
        };

        // 发送音频数据的函数
        const sendAudioData = () => {
          const chunkSize = 3200; // 每次发送 3200 字节
          let offset = 0;

          const sendChunk = () => {
            if (ws.readyState !== WebSocket.OPEN) {
              return;
            }

            if (offset < pcmData.byteLength) {
              const chunk = pcmData.slice(offset, offset + chunkSize);
              ws.send(chunk);
              offset += chunkSize;
              setTimeout(sendChunk, 10); // 每 10ms 发送一次
            } else {
              // 发送结束指令
              const stopMessage = {
                header: {
                  message_id: this.generateMessageId(),
                  task_id: taskId,
                  namespace: 'SpeechRecognizer',
                  name: 'StopRecognition',
                  appkey: this.config.appkey
                }
              };
              ws.send(JSON.stringify(stopMessage));
              console.log('[Speech] 音频数据发送完成');
            }
          };

          sendChunk();
        };

        ws.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            const messageName = message.header?.name;
            
            // 只在开发环境输出详细日志
            if (import.meta.env.DEV) {
              console.log('[Speech] 收到消息:', messageName);
            }

            // 识别开始 - 现在可以发送音频数据了
            if (messageName === 'RecognitionStarted') {
              recognitionStarted = true;
              console.log('[Speech] 识别已开始，开始发送音频数据');
              sendAudioData(); // 开始发送音频
            }

            // 识别完成
            if (messageName === 'RecognitionCompleted') {
              result = message.payload?.result || '';
              console.log('[Speech] 识别结果:', result);
              // 识别成功后立即关闭连接
              setTimeout(() => ws.close(), 100);
            }

            // 错误处理（但如果已经有结果了，就忽略超时错误）
            if (messageName === 'TaskFailed') {
              const errorMsg = message.header?.status_text || '未知错误';
              
              // 如果已经有识别结果，忽略 IDLE_TIMEOUT 错误
              if (result && errorMsg.includes('IDLE_TIMEOUT')) {
                console.log('[Speech] 识别已完成，忽略超时错误');
                return;
              }
              
              hasError = true;
              console.error('[Speech] 识别失败:', errorMsg);
              ws.close();
            }
          } catch (error) {
            console.error('[Speech] 解析消息失败:', error);
          }
        };

        ws.onerror = (error) => {
          console.error('[Speech] WebSocket 错误:', error);
          hasError = true;
        };

        ws.onclose = () => {
          console.log('[Speech] WebSocket 连接关闭');
          
          if (hasError) {
            resolve({
              success: false,
              text: '',
              error: '语音识别失败'
            });
          } else {
            resolve({
              success: true,
              text: result
            });
          }
        };

        // 超时处理
        setTimeout(() => {
          if (ws.readyState !== WebSocket.CLOSED) {
            ws.close();
            resolve({
              success: false,
              text: '',
              error: '识别超时'
            });
          }
        }, 30000); // 30 秒超时

      } catch (error) {
        console.error('[Speech] ASR 调用失败:', error);
        resolve({
          success: false,
          text: '',
          error: error instanceof Error ? error.message : '未知错误'
        });
      }
    });
  }

  /**
   * 完整流程：录音 → 识别
   */
  async recordAndRecognize(): Promise<ASRResult> {
    try {
      // 停止录音，直接获取 PCM 数据
      const pcmData = await this.stopRecording();

      // 调用 ASR
      const result = await this.speechToText(pcmData);

      return result;
    } catch (error) {
      console.error('[Speech] 录音识别失败:', error);
      return {
        success: false,
        text: '',
        error: error instanceof Error ? error.message : '未知错误'
      };
    }
  }

  /**
   * 生成消息 ID（32位十六进制字符串，不带连字符）
   */
  private generateMessageId(): string {
    // 生成 UUID 并移除所有连字符，得到32位十六进制字符串
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
    return uuid.replace(/-/g, ''); // 移除连字符
  }

  /**
   * 生成任务 ID（32位十六进制字符串，不带连字符）
   */
  private generateTaskId(): string {
    // 生成 UUID 并移除所有连字符，得到32位十六进制字符串
    const uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
    return uuid.replace(/-/g, ''); // 移除连字符
  }

  /**
   * 检查是否支持录音
   */
  static isSupported(): boolean {
    return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
  }
}

// 导出单例
export const speechService = new SpeechService();
export { SpeechService };
export type { ASRResult };
