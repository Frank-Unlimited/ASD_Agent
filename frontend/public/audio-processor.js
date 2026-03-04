/**
 * AudioWorklet 处理器 - 用于音频采集
 * 替代已废弃的 ScriptProcessorNode
 */
class AudioCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.isMuted = false;
    this.isSpeaking = false;
    this.silenceFrames = 0;
    this.speechFrames = 0;
    this.packetCount = 0;
    
    // 智能 VAD 参数
    this.SPEECH_THRESHOLD = 0.05;  // 语音检测阈值
    this.SPEECH_FRAMES_THRESHOLD = 3;  // 3帧确认开始说话
    this.SHORT_SILENCE_THRESHOLD = 12;  // 短停顿：12帧（1.5秒）- 可能是思考
    this.LONG_SILENCE_THRESHOLD = 24;   // 长停顿：24帧（3秒）- 确认结束
    
    // 音量趋势分析
    this.recentAmplitudes = [];  // 记录最近的音量
    this.AMPLITUDE_HISTORY_SIZE = 10;  // 保留最近10帧的音量
    this.lastSpeechAmplitude = 0;  // 最后一次说话的音量
    this.energyDecayDetected = false;  // 是否检测到能量衰减
    
    // 监听主线程消息
    this.port.onmessage = (e) => {
      if (e.data.type === 'setMuted') {
        this.isMuted = e.data.value;
      }
    };
  }
  
  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || !input[0]) return true;
    
    const inputData = input[0]; // 第一个声道
    
    if (this.isMuted) {
      return true;
    }
    
    // 检查音频数据
    let hasAudio = false;
    let maxAmplitude = 0;
    for (let i = 0; i < inputData.length; i++) {
      const abs = Math.abs(inputData[i]);
      if (abs > maxAmplitude) maxAmplitude = abs;
      if (abs > 0.001) hasAudio = true;
    }
    
    // 智能 VAD 检测
    const isSpeechDetected = maxAmplitude > this.SPEECH_THRESHOLD;
    
    if (isSpeechDetected) {
      this.speechFrames++;
      this.silenceFrames = 0;
      this.energyDecayDetected = false;
      
      // 记录音量历史
      this.recentAmplitudes.push(maxAmplitude);
      if (this.recentAmplitudes.length > this.AMPLITUDE_HISTORY_SIZE) {
        this.recentAmplitudes.shift();
      }
      this.lastSpeechAmplitude = maxAmplitude;
      
      if (!this.isSpeaking && this.speechFrames >= this.SPEECH_FRAMES_THRESHOLD) {
        this.port.postMessage({ type: 'speech_start', amplitude: maxAmplitude });
        this.isSpeaking = true;
      }
    } else {
      this.speechFrames = 0;
      
      if (this.isSpeaking) {
        this.silenceFrames++;
        
        // 智能判断：区分停顿和结束
        let shouldEnd = false;
        
        // 1. 短停顿（1.5秒内）：检测能量衰减
        if (this.silenceFrames >= this.SHORT_SILENCE_THRESHOLD && this.silenceFrames < this.LONG_SILENCE_THRESHOLD) {
          // 计算最近音量的平均值和趋势
          if (this.recentAmplitudes.length >= 8) {  // 增加到8帧，更稳定
            const recent8 = this.recentAmplitudes.slice(-8);
            const avgRecent = recent8.reduce((a, b) => a + b, 0) / recent8.length;
            
            // 降低敏感度：从 0.6 改为 0.4，只有音量下降很多才判定为结束
            if (this.lastSpeechAmplitude < avgRecent * 0.4) {
              this.energyDecayDetected = true;
            }
          }
          
          // 如果检测到能量衰减，提前结束
          if (this.energyDecayDetected) {
            shouldEnd = true;
          }
        }
        
        // 2. 长停顿（3秒）：直接结束
        if (this.silenceFrames >= this.LONG_SILENCE_THRESHOLD) {
          shouldEnd = true;
        }
        
        if (shouldEnd) {
          this.port.postMessage({ type: 'speech_end' });
          this.isSpeaking = false;
          this.silenceFrames = 0;
          this.recentAmplitudes = [];
          this.energyDecayDetected = false;
        }
      }
    }
    
    // 跳过静音包
    if (!hasAudio && this.packetCount < 3) {
      this.packetCount++;
      return true;
    }
    
    // 转换为 PCM16
    const pcm16 = new Int16Array(inputData.length);
    for (let i = 0; i < inputData.length; i++) {
      const s = Math.max(-1, Math.min(1, inputData[i]));
      pcm16[i] = s < 0 ? Math.floor(s * 0x8000) : Math.floor(s * 0x7FFF);
    }
    
    // 检查前面是否全是 0
    const firstBytes = new Uint8Array(pcm16.buffer.slice(0, 20));
    const hasDataAtStart = Array.from(firstBytes).some(b => b !== 0);
    
    if (!hasDataAtStart && this.packetCount < 3) {
      this.packetCount++;
      return true;
    }
    
    // 发送音频数据到主线程
    this.port.postMessage({
      type: 'audio_data',
      data: pcm16.buffer,
      hasAudio,
      maxAmplitude
    }, [pcm16.buffer]); // 转移所有权，避免复制
    
    if (this.packetCount < 3) {
      this.packetCount++;
    }
    
    return true; // 保持处理器运行
  }
}

registerProcessor('audio-capture-processor', AudioCaptureProcessor);
