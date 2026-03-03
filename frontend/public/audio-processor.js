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
    
    // VAD 参数
    this.SPEECH_THRESHOLD = 0.05;
    this.SPEECH_FRAMES_THRESHOLD = 3;
    this.SILENCE_FRAMES_THRESHOLD = 4;
    
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
    
    // VAD 检测
    const isSpeechDetected = maxAmplitude > this.SPEECH_THRESHOLD;
    
    if (isSpeechDetected) {
      this.speechFrames++;
      this.silenceFrames = 0;
      
      if (!this.isSpeaking && this.speechFrames >= this.SPEECH_FRAMES_THRESHOLD) {
        this.port.postMessage({ type: 'speech_start', amplitude: maxAmplitude });
        this.isSpeaking = true;
      }
    } else {
      this.speechFrames = 0;
      
      if (this.isSpeaking) {
        this.silenceFrames++;
        if (this.silenceFrames >= this.SILENCE_FRAMES_THRESHOLD) {
          this.port.postMessage({ type: 'speech_end' });
          this.isSpeaking = false;
          this.silenceFrames = 0;
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
