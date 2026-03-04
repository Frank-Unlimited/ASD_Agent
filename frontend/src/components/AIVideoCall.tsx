/**
 * AI 视频通话组件
 * 使用 Qwen-Omni-Realtime 实现实时视频通话和行为观察
 */

import React, { useState, useRef, useEffect } from 'react';
import { Camera, Mic, MicOff, Video, VideoOff, X, Activity, Lightbulb, AlertCircle, Maximize2, Minimize2, GripVertical } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { qwenRealtimeService } from '../services/qwenRealtimeService';
import { ChildProfile, FloorGame } from '../types';
import { floorGameStorageService } from '../services/floorGameStorage';
import { collectVideoCallContext } from '../services/videoCallContextHelper';

interface AIVideoCallProps {
  childProfile: ChildProfile | null;
  gameData?: FloorGame | null; // 改为可选
  gameId?: string; // 当前游戏的 ID，用于保存聊天记录
  onClose: () => void;
  isInline?: boolean; // 新增：是否嵌入式显示（非全屏）
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

const AIVideoCall: React.FC<AIVideoCallProps> = ({
  childProfile,
  gameData,
  gameId,
  onClose,
  isInline = false
}) => {
  const [isActive, setIsActive] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [isVideoEnabled, setIsVideoEnabled] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [userTranscript, setUserTranscript] = useState(''); // 当前用户说的话
  const [assistantTranscript, setAssistantTranscript] = useState(''); // 当前 AI 说的话
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isSpeaking, setIsSpeaking] = useState(false);

  // 聊天历史记录（预留，用于后续存储）
  const conversationHistoryRef = useRef<Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  }>>([]);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const audioWorkletNodeRef = useRef<AudioWorkletNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const frameIntervalRef = useRef<number | null>(null);
  const audioPlayerRef = useRef<AudioContext | null>(null);
  const audioQueueRef = useRef<ArrayBuffer[]>([]);
  const isPlayingRef = useRef(false);
  const isMutedRef = useRef(false); // 使用 ref 避免闭包问题
  const currentAudioSourceRef = useRef<AudioBufferSourceNode | null>(null); // 当前播放的音频源

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

      // 3. 收集完整的上下文信息
      console.log('[AI Video Call] 收集上下文信息...');
      const contextData = await collectVideoCallContext(childProfile, gameData || null);
      console.log('[AI Video Call] 上下文信息:', contextData);

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
          console.log('[AI Video Call] 📝 收到用户转录:', transcript);
          // 显示用户当前说的话
          setUserTranscript(transcript);

          // 保存到历史记录
          conversationHistoryRef.current.push({
            role: 'user',
            content: transcript,
            timestamp: Date.now()
          });
          console.log('[AI Video Call] ✅ 用户消息已保存到历史记录，当前总数:', conversationHistoryRef.current.length);
        },
        onAssistantTranscript: (delta) => {
          // 累积当前这一轮 AI 的回复
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

          // 用户开始说话，清空当前显示的用户文本（准备显示新的）
          setUserTranscript('');

          // 打断 AI：停止当前播放的音频
          if (currentAudioSourceRef.current) {
            try {
              currentAudioSourceRef.current.stop();
              currentAudioSourceRef.current = null;
              console.log('[AI Video Call] 用户打断，停止 AI 音频播放');
            } catch (e) {
              // 音频可能已经停止，忽略错误
            }
          }

          // 清空音频队列
          audioQueueRef.current = [];
          isPlayingRef.current = false;
        },
        onSpeechStopped: () => {
          setIsSpeaking(false);
        },
        onResponseStarted: () => {
          // AI 开始新的回复，清空上一轮的文本和音频
          console.log('[AI Video Call] AI 开始新的回复，清空上一轮文本和音频');
          setAssistantTranscript('');

          // 停止当前播放的音频（如果有）
          if (currentAudioSourceRef.current) {
            try {
              currentAudioSourceRef.current.stop();
              currentAudioSourceRef.current = null;
              console.log('[AI Video Call] 停止上一轮 AI 音频播放');
            } catch (e) {
              // 音频可能已经停止，忽略错误
            }
          }

          // 清空音频队列，准备播放新的回复
          audioQueueRef.current = [];
          isPlayingRef.current = false;
        },
        onResponseCompleted: (fullTranscript) => {
          // AI 回复完成，保存到历史记录
          if (fullTranscript) {
            conversationHistoryRef.current.push({
              role: 'assistant',
              content: fullTranscript,
              timestamp: Date.now()
            });
            console.log('[AI Video Call] ✅ AI 消息已保存到历史记录，当前总数:', conversationHistoryRef.current.length);
          } else {
            console.warn('[AI Video Call] ⚠️  AI 回复完成但文本为空');
          }
        }
      }, contextData);

    } catch (error) {
      console.error('[AI Video Call] 启动失败:', error);
      alert('无法访问摄像头或麦克风，请检查权限设置');
      setIsConnecting(false);
    }
  };
  /**
   * 启动音频采集（使用 AudioWorklet，降级到 ScriptProcessorNode）
   */
  const startAudioCapture = async (stream: MediaStream) => {
    try {
      audioContextRef.current = new AudioContext({ sampleRate: 16000 });
      const source = audioContextRef.current.createMediaStreamSource(stream);

      const supportsAudioWorklet = 'audioWorklet' in audioContextRef.current;

      if (supportsAudioWorklet) {
        try {
          console.log('[AI Video Call] 使用 AudioWorklet 进行音频采集');
          
          await audioContextRef.current.audioWorklet.addModule('/audio-processor.js');
          
          const workletNode = new AudioWorkletNode(
            audioContextRef.current,
            'audio-capture-processor'
          );

          workletNode.port.onmessage = (e) => {
            if (e.data.type === 'speech_start') {
              console.log('[AI Video Call] �️ 检测到语音开始 (振幅:', e.data.amplitude?.toFixed(3), ')');
              
              // 打断机制：用户开始说话时，立即停止 AI 音频播放
              if (currentAudioSourceRef.current) {
                console.log('[AI Video Call] ⚡ 用户打断，停止 AI 音频播放');
                currentAudioSourceRef.current.stop();
                currentAudioSourceRef.current = null;
              }
              // 清空音频队列
              audioQueueRef.current = [];
              isPlayingRef.current = false;
              
              qwenRealtimeService.sendMessage({ type: 'speech_start' });
            } else if (e.data.type === 'speech_end') {
              console.log('[AI Video Call] 🔇 检测到语音结束，自动提交');
              qwenRealtimeService.sendMessage({ type: 'speech_end' });
              qwenRealtimeService.sendMessage({ type: 'commit' });
            } else if (e.data.type === 'audio_data') {
              if (qwenRealtimeService.isConnectionActive()) {
                qwenRealtimeService.sendAudio(e.data.data);
              }
            }
          };

          source.connect(workletNode);
          workletNode.connect(audioContextRef.current.destination);

          audioWorkletNodeRef.current = workletNode;

          console.log('[AI Video Call] AudioWorklet 音频采集已启动 - 采样率:', audioContextRef.current.sampleRate, 'Hz');
          return;

        } catch (workletError) {
          console.warn('[AI Video Call] AudioWorklet 初始化失败，降级到 ScriptProcessor:', workletError);
        }
      } else {
        console.warn('[AI Video Call] 浏览器不支持 AudioWorklet，使用 ScriptProcessor');
      }

      const processor = audioContextRef.current.createScriptProcessor(4096, 1, 1);

      console.log('[AI Video Call] ScriptProcessor 音频采集已启动 - 采样率:', audioContextRef.current.sampleRate, 'Hz, 缓冲区:', 4096, '样本');

      let packetCount = 0;
      let isSpeaking = false;
      let silenceFrames = 0;
      let speechFrames = 0;
      
      // 智能 VAD 参数
      const SPEECH_THRESHOLD = 0.05;
      const SPEECH_FRAMES_THRESHOLD = 3;
      const SHORT_SILENCE_THRESHOLD = 12;  // 短停顿：1.5秒
      const LONG_SILENCE_THRESHOLD = 24;   // 长停顿：3秒
      
      // 音量趋势分析
      let recentAmplitudes: number[] = [];
      const AMPLITUDE_HISTORY_SIZE = 10;
      let lastSpeechAmplitude = 0;
      let energyDecayDetected = false;

      processor.onaudioprocess = (e) => {
        if (!isMutedRef.current && qwenRealtimeService.isConnectionActive()) {
          const inputData = e.inputBuffer.getChannelData(0);

          let hasAudio = false;
          let maxAmplitude = 0;
          for (let i = 0; i < inputData.length; i++) {
            const abs = Math.abs(inputData[i]);
            if (abs > maxAmplitude) maxAmplitude = abs;
            if (abs > 0.001) {
              hasAudio = true;
            }
          }

          const isSpeechDetected = maxAmplitude > SPEECH_THRESHOLD;

          if (isSpeechDetected) {
            speechFrames++;
            silenceFrames = 0;
            energyDecayDetected = false;
            
            // 记录音量历史
            recentAmplitudes.push(maxAmplitude);
            if (recentAmplitudes.length > AMPLITUDE_HISTORY_SIZE) {
              recentAmplitudes.shift();
            }
            lastSpeechAmplitude = maxAmplitude;

            if (!isSpeaking && speechFrames >= SPEECH_FRAMES_THRESHOLD) {
              console.log('[AI Video Call] 🎙️ 检测到语音开始 (振幅:', maxAmplitude.toFixed(3), ')');
              
              // 打断机制：用户开始说话时，立即停止 AI 音频播放
              if (currentAudioSourceRef.current) {
                console.log('[AI Video Call] ⚡ 用户打断，停止 AI 音频播放');
                currentAudioSourceRef.current.stop();
                currentAudioSourceRef.current = null;
              }
              // 清空音频队列
              audioQueueRef.current = [];
              isPlayingRef.current = false;
              
              qwenRealtimeService.sendMessage({ type: 'speech_start' });
              isSpeaking = true;
            }
          } else {
            speechFrames = 0;

            if (isSpeaking) {
              silenceFrames++;
              
              // 智能判断：区分停顿和结束
              let shouldEnd = false;
              
              // 1. 短停顿（1.5秒内）：检测能量衰减
              if (silenceFrames >= SHORT_SILENCE_THRESHOLD && silenceFrames < LONG_SILENCE_THRESHOLD) {
                if (recentAmplitudes.length >= 5) {
                  const recent5 = recentAmplitudes.slice(-5);
                  const avgRecent = recent5.reduce((a, b) => a + b, 0) / recent5.length;
                  
                  // 如果最后的音量明显低于平均值（能量衰减），可能是结束
                  if (lastSpeechAmplitude < avgRecent * 0.6) {
                    energyDecayDetected = true;
                  }
                }
                
                // 如果检测到能量衰减，提前结束
                if (energyDecayDetected) {
                  shouldEnd = true;
                  console.log('[AI Video Call] 💡 检测到能量衰减，判定为说话结束');
                }
              }
              
              // 2. 长停顿（3秒）：直接结束
              if (silenceFrames >= LONG_SILENCE_THRESHOLD) {
                shouldEnd = true;
                console.log('[AI Video Call] ⏱️ 长时间静音，确认说话结束');
              }
              
              if (shouldEnd) {
                console.log('[AI Video Call] 🔇 语音结束，自动提交');
                qwenRealtimeService.sendMessage({ type: 'speech_end' });
                qwenRealtimeService.sendMessage({ type: 'commit' });
                isSpeaking = false;
                silenceFrames = 0;
                recentAmplitudes = [];
                energyDecayDetected = false;
              }
            }
          }

          if (!hasAudio) {
            if (packetCount < 3) {
              console.log(`[AI Video Call] 跳过静音包 #${packetCount + 1}`);
              packetCount++;
            }
            return;
          }

          const pcm16 = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            const s = Math.max(-1, Math.min(1, inputData[i]));
            pcm16[i] = s < 0 ? Math.floor(s * 0x8000) : Math.floor(s * 0x7FFF);
          }

          const firstBytes = new Uint8Array(pcm16.buffer.slice(0, 20));
          const hasDataAtStart = Array.from(firstBytes).some(b => b !== 0);

          if (!hasDataAtStart) {
            if (packetCount < 3) {
              console.log(`[AI Video Call] 跳过前面全是 0 的音频包 #${packetCount + 1}`);
              packetCount++;
            }
            return;
          }

          if (packetCount < 3) {
            packetCount++;
          }

          qwenRealtimeService.sendAudio(pcm16.buffer);
        }
      };

      source.connect(processor);
      processor.connect(audioContextRef.current.destination);

    } catch (error) {
      console.error('[AI Video Call] 音频采集失败:', error);
      throw error;
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

      // 转换为 JPEG base64（但不立即发送，等待音频发送时一起发送）
      canvas.toBlob((blob) => {
        if (blob) {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64 = reader.result as string;
            // 只有在连接活跃时才发送
            if (qwenRealtimeService.isConnectionActive()) {
              qwenRealtimeService.sendImage(base64);
            }
          };
          reader.readAsDataURL(blob);
        }
      }, 'image/jpeg', 0.6); // 降低质量到 0.6，减少数据量

    }, 3000); // 改为每3秒一帧，进一步降低频率
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
        console.log('[AI Video Call] 创建新的 AudioContext');
      } catch (error) {
        console.error('[AI Video Call] 无法创建 AudioContext:', error);
        isPlayingRef.current = false;
        return;
      }
    }

    while (audioQueueRef.current.length > 0) {
      const audioData = audioQueueRef.current.shift();
      if (!audioData) continue;

      try {
        // 再次检查 AudioContext（可能在循环中被关闭）
        if (!audioPlayerRef.current || audioPlayerRef.current.state === 'closed') {
          console.warn('[AI Video Call] AudioContext 已关闭，停止播放');
          break;
        }

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

        // 保存当前音频源，以便用户打断时停止
        currentAudioSourceRef.current = source;

        source.start();

        // 等待播放完成
        await new Promise(resolve => {
          source.onended = () => {
            currentAudioSourceRef.current = null; // 播放完成，清空引用
            resolve(null);
          };
        });

      } catch (error) {
        console.error('[AI Video Call] 音频播放失败:', error);
        // 继续处理下一个音频
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
    // 保存聊天记录到游戏数据
    console.log('[AI Video Call] 准备保存聊天记录...');
    console.log('[AI Video Call] gameId:', gameId);
    console.log('[AI Video Call] 历史记录数量:', conversationHistoryRef.current.length);
    console.log('[AI Video Call] 历史记录内容:', conversationHistoryRef.current);

    if (gameId && conversationHistoryRef.current.length > 0) {
      try {
        const chatHistory = JSON.stringify(conversationHistoryRef.current);
        console.log('[AI Video Call] 序列化后的聊天记录:', chatHistory);

        floorGameStorageService.updateGame(gameId, {
          chat_history_in_game: chatHistory
        });
        console.log('[AI Video Call] ✅ 聊天记录已保存到游戏数据:', gameId);
      } catch (error) {
        console.error('[AI Video Call] ❌ 保存聊天记录失败:', error);
      }
    } else {
      if (!gameId) {
        console.warn('[AI Video Call] ⚠️  未提供 gameId，无法保存聊天记录');
      }
      if (conversationHistoryRef.current.length === 0) {
        console.warn('[AI Video Call] ⚠️  聊天记录为空，跳过保存');
      }
    }

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
   * 获取聊天历史记录（预留接口）
   * 可用于后续保存到数据库或导出
   */
  const getConversationHistory = () => {
    return conversationHistoryRef.current;
  };

  /**
   * 切换静音
   */
  const toggleMute = () => {
    setIsMuted(prev => {
      const newMuted = !prev;
      isMutedRef.current = newMuted; // 同步更新 ref
      
      // 通知 AudioWorklet 节点
      if (audioWorkletNodeRef.current) {
        audioWorkletNodeRef.current.port.postMessage({
          type: 'setMuted',
          value: newMuted
        });
      }
      
      console.log('[AI Video Call] 麦克风状态切换:', prev ? '静音' : '开启', '->', newMuted ? '静音' : '开启');
      return newMuted;
    });
  };

  /**
   * 切换视频
   */
  const toggleVideo = () => {
    setIsVideoEnabled(prev => {
      const newEnabled = !prev;
      console.log('[AI Video Call] 视频状态切换:', prev ? '开启' : '关闭', '->', newEnabled ? '开启' : '关闭');

      if (videoRef.current && videoRef.current.srcObject) {
        const stream = videoRef.current.srcObject as MediaStream;
        stream.getVideoTracks().forEach(track => {
          track.enabled = newEnabled;
        });
      }

      return newEnabled;
    });
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

  const windowVariants = {
    floating: {
      width: '280px',
      height: '380px',
      bottom: '100px',
      right: '16px',
      borderRadius: '24px',
      transition: { type: 'spring' as const, damping: 25, stiffness: 200 }
    },
    full: {
      width: '100vw',
      height: '100vh',
      bottom: '0px',
      right: '0px',
      borderRadius: '0px',
      transition: { type: 'spring' as const, damping: 25, stiffness: 200 }
    }
  };

  return (
    <motion.div
      initial="floating"
      animate={isFullScreen ? "full" : "floating"}
      variants={windowVariants}
      drag={!isFullScreen}
      dragConstraints={{ left: -300, right: 0, top: -500, bottom: 0 }}
      dragElastic={0.1}
      dragMomentum={false}
      className="fixed z-[60] bg-black shadow-[0_20px_50px_rgba(0,0,0,0.3)] overflow-hidden flex flex-col border border-white/10 backdrop-blur-xl"
    >
      {/* Video Content */}
      <div className="relative flex-1 bg-gray-900 overflow-hidden">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-full object-cover"
        />

        {/* Hidden canvas for frame capture */}
        <canvas ref={canvasRef} className="hidden" />

        {/* Glassmorphic Overlays */}
        <div className="absolute top-4 left-4 right-4 flex justify-between items-start pointer-events-none">
          {/* Status Badge */}
          <div className="flex flex-col space-y-2 pointer-events-auto">
            <div className={`px-3 py-1.5 rounded-full text-[10px] font-bold flex items-center backdrop-blur-md border border-white/20 ${isActive ? 'bg-green-500/80' : isConnecting ? 'bg-yellow-500/80' : 'bg-gray-500/80'} text-white shadow-lg`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${isActive ? 'bg-white animate-pulse' : 'bg-white/50'}`} />
              {isActive ? 'AI 观察中' : isConnecting ? '连接中...' : '准备就绪'}
            </div>

            {isSpeaking && (
              <motion.div
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className="px-3 py-1.5 rounded-full text-[10px] font-bold bg-blue-500/80 text-white flex items-center backdrop-blur-md border border-white/20 shadow-lg"
              >
                <div className="flex space-x-0.5 mr-2">
                  <div className="w-1 h-3 bg-white rounded-full animate-[bounce_1s_infinite_0s]" />
                  <div className="w-1 h-4 bg-white rounded-full animate-[bounce_1s_infinite_0.2s]" />
                  <div className="w-1 h-3 bg-white rounded-full animate-[bounce_1s_infinite_0.4s]" />
                </div>
                听取中
              </motion.div>
            )}
          </div>

          {/* Window Controls */}
          <div className="flex space-x-2 pointer-events-auto">
            <button
              onClick={() => setIsFullScreen(!isFullScreen)}
              className="p-2 rounded-full bg-black/30 hover:bg-black/50 text-white backdrop-blur-md border border-white/10 transition-all active:scale-95"
            >
              {isFullScreen ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
            </button>
            <button
              onClick={handleClose}
              className="p-2 rounded-full bg-red-500/80 hover:bg-red-600 text-white backdrop-blur-md border border-white/10 transition-all active:scale-95"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Transcripts (Subtitle Style) */}
        <AnimatePresence>
          {(userTranscript || assistantTranscript) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className={`absolute bottom-6 left-4 right-4 space-y-2 pointer-events-none`}
            >
              {userTranscript && (
                <div className="flex justify-end">
                  <div className="bg-white/90 text-gray-800 px-3 py-1.5 rounded-2xl rounded-tr-none text-xs font-medium shadow-lg backdrop-blur-md max-w-[80%]">
                    {userTranscript}
                  </div>
                </div>
              )}
              {assistantTranscript && (
                <div className="flex justify-start">
                  <div className="bg-indigo-600/90 text-white px-3 py-1.5 rounded-2xl rounded-tl-none text-xs font-medium shadow-lg backdrop-blur-md border border-white/10 max-w-[80%]">
                    {assistantTranscript}
                  </div>
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Control Bar (Glass Bottom) */}
      <div className={`p-4 bg-black/80 backdrop-blur-2xl border-t border-white/5 flex items-center justify-between shrink-0`}>
        <div className="flex items-center space-x-3">
          <button
            onClick={toggleMute}
            disabled={!isActive}
            className={`p-3 rounded-2xl transition-all shadow-lg border ${isMuted ? 'bg-red-500/80 text-white border-red-400' : 'bg-white/10 text-white border-white/10 hover:bg-white/20'} ${!isActive ? 'opacity-30' : 'active:scale-90'}`}
          >
            {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
          </button>

          <button
            onClick={toggleVideo}
            disabled={!isActive}
            className={`p-3 rounded-2xl transition-all shadow-lg border ${!isVideoEnabled ? 'bg-red-500/80 text-white border-red-400' : 'bg-white/10 text-white border-white/10 hover:bg-white/20'} ${!isActive ? 'opacity-30' : 'active:scale-90'}`}
          >
            {isVideoEnabled ? <Video className="w-5 h-5" /> : <VideoOff className="w-5 h-5" />}
          </button>
        </div>

        {/* Start/Stop Interaction */}
        <div className="flex-1 px-4 flex justify-center">
          {!isActive ? (
            <button
              onClick={startCall}
              disabled={isConnecting}
              className={`px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-2xl font-bold text-xs flex items-center transition-all shadow-xl shadow-indigo-500/20 active:scale-95 disabled:opacity-50`}
            >
              {isConnecting ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
              ) : (
                <Camera className="w-4 h-4 mr-2" />
              )}
              {isConnecting ? '连接中' : '开始观察'}
            </button>
          ) : (
            <button
              onClick={stopCall}
              className="px-5 py-2.5 bg-red-500/20 hover:bg-red-500/30 text-red-500 rounded-2xl font-bold text-xs flex items-center transition-all border border-red-500/30 active:scale-95"
            >
              <X className="w-4 h-4 mr-2" />
              结束互动
            </button>
          )}
        </div>

        {/* Small interaction count or metadata could go here */}
        {!isFullScreen && (
          <div className="w-10 flex justify-end opacity-40">
            <GripVertical className="w-4 h-4 text-white" />
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default AIVideoCall;
