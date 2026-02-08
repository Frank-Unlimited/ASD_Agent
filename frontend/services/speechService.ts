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
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];
  private audioContext: AudioContext | null = null;

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
   * 开始录音
   */
  async startRecording(): Promise<void> {
    try {
      // 请求麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          channelCount: 1, // 单声道
          sampleRate: 16000, // 16kHz
          echoCancellation: true, // 回声消除
          noiseSuppression: true, // 噪音抑制
        } 
      });

      // 创建 MediaRecorder
      this.mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });

      this.audioChunks = [];

      // 收集音频数据
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      // 开始录音
      this.mediaRecorder.start();
      console.log('[Speech] 开始录音');
    } catch (error) {
      console.error('[Speech] 录音失败:', error);
      throw new Error('无法访问麦克风，请检查权限设置');
    }
  }

  /**
   * 停止录音并返回音频 Blob
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('录音器未初始化'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        // 合并音频片段
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        
        // 停止所有音轨
        if (this.mediaRecorder?.stream) {
          this.mediaRecorder.stream.getTracks().forEach(track => track.stop());
        }

        console.log('[Speech] 录音完成，大小:', audioBlob.size, 'bytes');
        resolve(audioBlob);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * 将音频 Blob 转换为 PCM 格式
   */
  async convertToPCM(audioBlob: Blob): Promise<ArrayBuffer> {
    try {
      // 创建 AudioContext
      if (!this.audioContext) {
        this.audioContext = new AudioContext({ sampleRate: 16000 });
      }

      // 读取音频数据
      const arrayBuffer = await audioBlob.arrayBuffer();
      
      // 解码音频
      const audioBuffer = await this.audioContext.decodeAudioData(arrayBuffer);

      // 获取单声道数据
      const channelData = audioBuffer.getChannelData(0);

      // 转换为 16 位 PCM
      const pcmData = new Int16Array(channelData.length);
      for (let i = 0; i < channelData.length; i++) {
        // 将 [-1, 1] 范围转换为 [-32768, 32767]
        const s = Math.max(-1, Math.min(1, channelData[i]));
        pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
      }

      console.log('[Speech] PCM 转换完成，长度:', pcmData.length);
      return pcmData.buffer;
    } catch (error) {
      console.error('[Speech] PCM 转换失败:', error);
      throw new Error('音频格式转换失败');
    }
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
   * 完整流程：录音 → 转换 → 识别
   */
  async recordAndRecognize(): Promise<ASRResult> {
    try {
      // 停止录音
      const audioBlob = await this.stopRecording();

      // 转换为 PCM
      const pcmData = await this.convertToPCM(audioBlob);

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
