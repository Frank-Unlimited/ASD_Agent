/**
 * AI 视频通话组件
 * 使用 Qwen-Omni-Realtime 实现实时视频通话和行为观察
 */

import React, { useState, useRef, useEffect } from 'react';
import { Camera, Mic, MicOff, Video, VideoOff, X, Activity, Lightbulb, AlertCircle } from 'lucide-react';
import { qwenRealtimeService } from '../services/qwenRealtimeService';
import { ChildProfile } from '../types';

interface AIVideoCallProps {
  childProfile: ChildProfile | null;
  gameContext?: string;
  onClose: () => void;
}

/**
 * 计算年龄
 */
const calculateAge = (birthDate: string): number => {
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  return age;
};

const AIVideoCall: React.FC<AIVideoCallProps> = ({ childProfile, gameContext, onClose }) => {
  const [isActive, setIsActive] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [userTranscript, setUserTranscript] = useState('');
  const [assistantTranscript, setAssistantTranscript] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioWorkletNodeRef = useRef<AudioWorkletNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const frameIntervalRef = useRef<number | null>(null);
  const audioPlayerRef = useRef<AudioContext | null>(null);
  const audioQueueRef = useRef<ArrayBuffer[]>([]);
  const isPlayingRef = useRef(false);
  
  /**
   * 启动视频通话
   */
  const startCall = async () => {
    try {
      setIsConnecting(true);
      
      // 1. 获取摄像头和麦克风权限
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 720, height: 480, frameRate: 30 },
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      });
      
      mediaStreamRef.current = stream;
      
      // 2. 显示视频预览
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }
      
      // 3. 准备初始化信息
      const childInfo = {
        name: childProfile?.name || '孩子',
        age: childProfile?.birthDate ? calculateAge(childProfile.birthDate) + '岁' : undefined,
        diagnosis: childProfile?.diagnosis
      };
      
      const gameInfo = {
        name: gameContext || '自由游戏',
        description: '通过视频观察孩子的行为和互动',
        goals: [
          '观察孩子的兴趣点',
          '识别孩子的情绪状态',
          '提供实时干预建议'
        ]
      };
      
      // 4. 连接到 Qwen-Omni-Realtime（使用官方 Python SDK）
      await qwenRealtimeService.connect({
        onConnected: () => {
          console.log('[AI Video Call] 已连接到服务器，等待会话初始化...');
        },
        onSessionCreated: () => {
          console.log('[AI Video Call] 会话已初始化，开始音视频采集');
          setIsActive(true);
          setIsConnecting(false);
          
          // 开始音频采集
          startAudioCapture(stream);
          
          // 启动视频帧采集（每1秒一帧）
          startFrameCapture();
        },
        onSessionUpdated: () => {
          console.log('[AI Video Call] 会话配置已更新');
        },
        onDisconnected: () => {
          console.log('[AI Video Call] 连接已断开');
          stopCall();
        },
        onError: (error) => {
          console.error('[AI Video Call] 错误:', error);
          alert('连接失败：' + error.message);
          stopCall();
        },
        onUserTranscript: (transcript) => {
          setUserTranscript(transcript);
        },
        onAssistantTranscript: (delta) => {
          setAssistantTranscript(prev => prev + delta);
          
          // 检查是否包含建议
          if (delta.includes('建议') || delta.includes('可以') || delta.includes('试试')) {
            // 提取建议（简单实现）
            const sentences = (assistantTranscript + delta).split(/[。！？]/);
            const newSuggestions = sentences.filter(s => 
              s.includes('建议') || s.includes('可以') || s.includes('试试')
            ).slice(-3);
            setSuggestions(newSuggestions);
          }
        },
        onAssistantAudio: (audioData) => {
          // 播放音频
          playAudio(audioData);
        },
        onSpeechStarted: () => {
          setIsSpeaking(true);
        },
        onSpeechStopped: () => {
          setIsSpeaking(false);
        }
      }, {
        childInfo,
        gameInfo
      });
      
    } catch (error) {
      console.error('[AI Video Call] 启动失败:', error);
      alert('无法访问摄像头或麦克风，请检查权限设置');
      setIsConnecting(false);
    }
  };
  /**
   * 启动音频采集（完全复制官方 SDK 行为）
   */
  const startAudioCapture = async (stream: MediaStream) => {
    try {
      // 使用 16kHz 采样率（与官方 SDK 一致）
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      const source = audioContextRef.current.createMediaStreamSource(stream);
      
      // 创建 ScriptProcessorNode
      // 官方 SDK 使用 3200 个样本（6400 字节），但 ScriptProcessorNode 只支持 2 的幂次
      // 尝试使用 4096 样本（8192 字节，更接近官方的 6400 字节）
      const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);
      
      console.log('[AI Video Call] 音频采集已启动 - 采样率:', audioContextRef.current.sampleRate, 'Hz, 缓冲区:', 4096, '样本 (256ms)');
      
      let packetCount = 0;
      
      processor.onaudioprocess = (e) => {
        if (!isMuted && qwenRealtimeService.isConnectionActive()) {
          const inputData = e.inputBuffer.getChannelData(0);
          
          // 检查是否有真实音频数据（不是全 0）
          let hasAudio = false;
          let maxAmplitude = 0;
          for (let i = 0; i < inputData.length; i++) {
            const abs = Math.abs(inputData[i]);
            if (abs > maxAmplitude) maxAmplitude = abs;
            if (abs > 0.001) {
              hasAudio = true;
            }
          }
          
          // 跳过静音包（前几个包可能全是静音）
          if (!hasAudio) {
            if (packetCount < 3) {
              console.log(`[AI Video Call] 跳过静音包 #${packetCount + 1}`);
              packetCount++;
            }
            return;
          }
          
          // 只在前 3 个包打印详细日志
          if (packetCount < 3) {
            console.log(`[AI Video Call] 原始音频数据 #${packetCount + 1}:`, {
              hasAudio,
              maxAmplitude: maxAmplitude.toFixed(6),
              length: inputData.length,
              first10: Array.from(inputData.slice(0, 10)),
              // 找到第一个非零值的位置
              firstNonZeroIndex: Array.from(inputData).findIndex(v => Math.abs(v) > 0.001),
              // 显示最大振幅附近的值
              maxIndex: Array.from(inputData).findIndex(v => Math.abs(v) === maxAmplitude)
            });
          }
          
          // 转换为 Int16Array (PCM16)
          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            // 限制在 [-1, 1] 范围内
            const s = Math.max(-1, Math.min(1, inputData[i]));
            // 转换为 16-bit 整数
            pcm16[i] = s < 0 ? Math.floor(s * 0x8000) : Math.floor(s * 0x7FFF);
          }
          
          // 检查前面的字节是否全是 0（阿里云可能不接受前面全是 0 的包）
          const firstBytes = new Uint8Array(pcm16.buffer.slice(0, 20));
          const hasDataAtStart = Array.from(firstBytes).some(b => b !== 0);
          
          if (!hasDataAtStart) {
            if (packetCount < 3) {
              console.log(`[AI Video Call] 跳过前面全是 0 的音频包 #${packetCount + 1}`);
              packetCount++;
            }
            return;
          }
          
          // 只在前 3 个包打印日志
          if (packetCount < 3) {
            // 找到最大振幅的位置
            const maxIndex = Array.from(inputData).findIndex(v => Math.abs(v) === maxAmplitude);
            
            console.log(`[AI Video Call] 转换后的 PCM16 数据 #${packetCount + 1}:`, {
              samples: pcm16.length,
              bytes: pcm16.buffer.byteLength,
              first10: Array.from(pcm16.slice(0, 10)),
              // 显示最大振幅附近的转换结果
              aroundMaxIndex: maxIndex >= 0 ? {
                index: maxIndex,
                originalValue: inputData[maxIndex],
                convertedValue: pcm16[maxIndex],
                nearby: Array.from(pcm16.slice(Math.max(0, maxIndex - 5), maxIndex + 5))
              } : null,
              bufferFirst20Bytes: Array.from(new Uint8Array(pcm16.buffer.slice(0, 20))),
              // 显示最大振幅位置的字节
              bufferAroundMax: maxIndex >= 0 ? Array.from(new Uint8Array(pcm16.buffer.slice(maxIndex * 2, maxIndex * 2 + 10))) : null
            });
            packetCount++;
          }
          
          // 发送到服务器
          qwenRealtimeService.sendAudio(pcm16.buffer);
        }
      };
      
      // 重要：必须连接到 destination，否则不会触发 onaudioprocess
      source.connect(processor);
      processor.connect(audioContextRef.current.destination);
      
    } catch (error) {
      console.error('[AI Video Call] 音频采集失败:', error);
    }
  };
  
  /**
   * 启动视频帧采集
   */
  const startFrameCapture = () => {
    frameIntervalRef.current = window.setInterval(() => {
      if (!isVideoEnabled || !videoRef.current || !canvasRef.current) return;
      
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      
      if (!context || video.readyState !== video.HAVE_ENOUGH_DATA) return;
      
      // 设置 canvas 尺寸
      canvas.width = 720;
      canvas.height = 480;
      
      // 绘制当前帧
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // 转换为 JPEG base64
      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = reader.result as string;
            // 发送视频帧到服务器
            qwenRealtimeService.sendImage(base64);
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.8);
      
    }, 1000); // 每秒一帧
  };
  
  /**
   * 播放音频
   */
  const playAudio = async (audioData: ArrayBuffer) => {
    audioQueueRef.current.push(audioData);
    
    if (!isPlayingRef.current) {
      isPlayingRef.current = true;
      await processAudioQueue();
    }
  };
  
  /**
   * 处理音频队列
   */
  const processAudioQueue = async () => {
    // 确保 AudioContext 存在
    if (!audioPlayerRef.current || audioPlayerRef.current.state === 'closed') {
      try {
        audioPlayerRef.current = new AudioContext({ sampleRate: 24000 });
      } catch (error) {
        console.error('[AI Video Call] 无法创建 AudioContext:', error);
        return;
      }
    }
    
    while (audioQueueRef.current.length > 0) {
      const audioData = audioQueueRef.current.shift();
      if (!audioData) continue;
      
      try {
        // 阿里云返回的是 PCM16 格式（16-bit, 24kHz, 单声道）
        const audioBuffer = audioPlayerRef.current.createBuffer(
          1, // 单声道
          audioData.byteLength / 2, // PCM16 每个样本2字节
          24000 // 采样率
        );
        
        const channelData = audioBuffer.getChannelData(0);
        const view = new DataView(audioData);
        
        for (let i = 0; i < channelData.length; i++) {
          // 读取2字节的PCM16数据（小端序）
          const sample = view.getInt16(i * 2, true);
          
          // 归一化到 [-1, 1]
          channelData[i] = sample / 32768.0;
        }
        
        // 播放
        const source = audioPlayerRef.current.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioPlayerRef.current.destination);
        source.start();
        
        // 等待播放完成
        await new Promise(resolve => {
          source.onended = resolve;
        });
        
      } catch (error) {
        console.error('[AI Video Call] 音频播放失败:', error);
      }
    }
    
    isPlayingRef.current = false;
  };
  
  /**
   * 关闭组件（清理资源并通知父组件）
   */
  const handleClose = () => {
    // 先停止通话，清理所有资源
    if (isActive) {
      stopCall();
    }
    
    // 通知父组件关闭
    onClose();
  };
  
  /**
   * 停止通话
   */
  const stopCall = () => {
    // 停止帧采集
    if (frameIntervalRef.current) {
      clearInterval(frameIntervalRef.current);
      frameIntervalRef.current = null;
    }
    
    // 停止音频上下文
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    
    if (audioPlayerRef.current) {
      audioPlayerRef.current.close();
      audioPlayerRef.current = null;
    }
    
    // 停止媒体流
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
      mediaStreamRef.current = null;
    }
    
    // 断开服务
    qwenRealtimeService.disconnect();
    
    setIsActive(false);
    setIsConnecting(false);
    setUserTranscript('');
    setAssistantTranscript('');
  };
  
  /**
   * 切换静音
   */
  const toggleMute = () => {
    setIsMuted(!isMuted);
  };
  
  /**
   * 切换视频
   */
  const toggleVideo = () => {
    setIsVideoEnabled(!isVideoEnabled);
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getVideoTracks().forEach(track => {
        track.enabled = !isVideoEnabled;
      });
    }
  };
  
  /**
   * 计算年龄
   */
  const calculateAge = (birthDate: string): number => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };
  
  // 组件卸载时清理
  useEffect(() => {
    return () => {
      if (isActive) {
        stopCall();
      }
    };
  }, [isActive]);
  
  return (
    <div className={`fixed z-50 transition-all duration-300 ${
      isMinimized 
        ? 'bottom-4 right-4 w-80 h-60' 
        : 'inset-0'
    }`}>
      <div className={`${isMinimized ? 'rounded-lg shadow-2xl' : ''} bg-black h-full flex flex-col overflow-hidden`}>
        {/* 视频区域 */}
        <div className="flex-1 relative">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-full object-cover"
          />
          
          {/* 隐藏的 canvas 用于帧提取 */}
          <canvas ref={canvasRef} className="hidden" />
          
          {/* 状态指示器 */}
          <div className="absolute top-2 right-2 flex flex-col items-end space-y-1">
            {/* 连接状态 */}
            <div className={`px-2 py-1 rounded-full text-xs font-bold flex items-center ${
              isActive ? 'bg-green-500' :
              isConnecting ? 'bg-yellow-500' :
              'bg-gray-500'
            } text-white`}>
              <div className={`w-1.5 h-1.5 rounded-full mr-1 ${
                isActive ? 'bg-white animate-pulse' : 'bg-white/50'
              }`} />
              {isActive ? 'AI 观察中' :
               isConnecting ? '连接中...' :
               '未连接'}
            </div>
            
            {/* 语音状态 */}
            {isSpeaking && (
              <div className="px-2 py-1 rounded-full text-xs font-bold bg-blue-500 text-white flex items-center">
                <Mic className="w-2 h-2 mr-1 animate-pulse" />
                说话中
              </div>
            )}
          </div>
          
          {/* 转录文本覆盖层（仅在非最小化时显示） */}
          {!isMinimized && (userTranscript || assistantTranscript) && (
            <div className="absolute bottom-20 left-4 right-4 space-y-2">
              {userTranscript && (
                <div className="bg-blue-500/90 text-white px-4 py-2 rounded-lg text-sm">
                  <span className="font-bold">你：</span> {userTranscript}
                </div>
              )}
              {assistantTranscript && (
                <div className="bg-green-500/90 text-white px-4 py-2 rounded-lg text-sm">
                  <span className="font-bold">AI 治疗师：</span> {assistantTranscript}
                </div>
              )}
            </div>
          )}
        </div>
        
        {/* 建议面板（仅在非最小化时显示） */}
        {!isMinimized && suggestions.length > 0 && (
          <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4">
            <h3 className="text-white font-bold mb-2 flex items-center">
              <Lightbulb className="w-4 h-4 mr-2" />
              实时建议
            </h3>
            <div className="space-y-2">
              {suggestions.map((suggestion, index) => (
                <div key={index} className="bg-white/20 text-white px-3 py-2 rounded text-sm">
                  {suggestion}
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* 控制栏 */}
        <div className={`bg-gray-900 ${isMinimized ? 'p-2' : 'p-4'} flex items-center justify-between`}>
          <div className="flex items-center space-x-2">
            {/* 静音按钮 */}
            <button
              onClick={toggleMute}
              disabled={!isActive}
              className={`${isMinimized ? 'p-2' : 'p-3'} rounded-full transition ${
                isMuted ? 'bg-red-500' : 'bg-gray-700'
              } ${!isActive ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}`}
              title={isMuted ? '取消静音' : '静音'}
            >
              {isMuted ? <MicOff className={`${isMinimized ? 'w-4 h-4' : 'w-5 h-5'} text-white`} /> : <Mic className={`${isMinimized ? 'w-4 h-4' : 'w-5 h-5'} text-white`} />}
            </button>
            
            {/* 视频按钮 */}
            <button
              onClick={toggleVideo}
              disabled={!isActive}
              className={`${isMinimized ? 'p-2' : 'p-3'} rounded-full transition ${
                !isVideoEnabled ? 'bg-red-500' : 'bg-gray-700'
              } ${!isActive ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}`}
              title={isVideoEnabled ? '关闭视频' : '开启视频'}
            >
              {isVideoEnabled ? <Video className={`${isMinimized ? 'w-4 h-4' : 'w-5 h-5'} text-white`} /> : <VideoOff className={`${isMinimized ? 'w-4 h-4' : 'w-5 h-5'} text-white`} />}
            </button>
          </div>
          
          {/* 中间：开始/结束按钮 */}
          {!isMinimized && (
            <div>
              {!isActive ? (
                <button
                  onClick={startCall}
                  disabled={isConnecting}
                  className="px-6 py-3 bg-green-500 text-white rounded-full font-bold flex items-center hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isConnecting ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                      连接中...
                    </>
                  ) : (
                    <>
                      <Camera className="w-5 h-5 mr-2" />
                      开始 AI 视频通话
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={stopCall}
                  className="px-6 py-3 bg-red-500 text-white rounded-full font-bold flex items-center hover:bg-red-600 transition"
                >
                  <X className="w-5 h-5 mr-2" />
                  结束通话
                </button>
              )}
            </div>
          )}
          
          {/* 右侧按钮组 */}
          <div className="flex items-center space-x-2">
            {/* 最小化/最大化按钮 */}
            {isActive && (
              <button
                onClick={() => setIsMinimized(!isMinimized)}
                className={`${isMinimized ? 'p-2' : 'p-3'} rounded-full bg-gray-700 hover:bg-gray-600 transition`}
                title={isMinimized ? '最大化' : '最小化'}
              >
                {isMinimized ? (
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 12H4" />
                  </svg>
                )}
              </button>
            )}
            
            {/* 关闭按钮 */}
            <button
              onClick={handleClose}
              className={`${isMinimized ? 'p-2' : 'p-3'} rounded-full bg-gray-700 hover:bg-gray-600 transition`}
              title="关闭"
            >
              <X className={`${isMinimized ? 'w-4 h-4' : 'w-5 h-5'} text-white`} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIVideoCall;
