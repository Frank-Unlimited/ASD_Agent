/**
 * AI 视频通话组件
 * 使用 Qwen-Omni-Realtime 实现实时视频通话和行为观察
 */

import React, { useState, useRef, useEffect } from 'react';
import { Camera, Mic, MicOff, Video, VideoOff, X, Activity, Lightbulb, AlertCircle } from 'lucide-react';
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
      let isSpeaking = false;
      let silenceFrames = 0;
      let speechFrames = 0; // 连续语音帧计数
      const SPEECH_THRESHOLD = 0.05; // 语音检测阈值
      const SPEECH_FRAMES_THRESHOLD = 3; // 需要连续 3 帧超过阈值才认为是语音（约 0.75 秒）
      const SILENCE_FRAMES_THRESHOLD = 4; // 静音帧数阈值（约 1 秒）

      processor.onaudioprocess = (e) => {
        if (!isMutedRef.current && qwenRealtimeService.isConnectionActive()) {
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

          // 改进的 VAD 检测：需要连续多帧超过阈值才认为是语音
          const isSpeechDetected = maxAmplitude > SPEECH_THRESHOLD;

          if (isSpeechDetected) {
            speechFrames++;
            silenceFrames = 0;

            // 需要连续多帧超过阈值才触发语音开始
            if (!isSpeaking && speechFrames >= SPEECH_FRAMES_THRESHOLD) {
              console.log('[AI Video Call] 🎤 检测到语音开始 (振幅:', maxAmplitude.toFixed(3), ')');
              qwenRealtimeService.sendMessage({ type: 'speech_start' });
              isSpeaking = true;
            }
          } else {
            speechFrames = 0; // 重置语音帧计数

            if (isSpeaking) {
              silenceFrames++;
              if (silenceFrames >= SILENCE_FRAMES_THRESHOLD) {
                console.log('[AI Video Call] 🔇 检测到语音结束，自动提交');
                qwenRealtimeService.sendMessage({ type: 'speech_end' });
                qwenRealtimeService.sendMessage({ type: 'commit' });
                isSpeaking = false;
                silenceFrames = 0;
              }
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

  return (
    <div className={`${isInline
        ? 'relative h-full w-full'
        : `fixed z-50 inset-0 ${isMinimized ? 'bottom-4 right-4 w-80 h-60' : 'inset-0'}`
      } transition-all duration-300`}>
      <div className={`${isMinimized || isInline ? 'rounded-lg' : ''} ${isMinimized ? 'shadow-2xl' : ''} bg-black h-full flex flex-col overflow-hidden`}>
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
            <div className={`px-2 py-1 rounded-full text-xs font-bold flex items-center ${isActive ? 'bg-green-500' :
                isConnecting ? 'bg-yellow-500' :
                  'bg-gray-500'
              } text-white`}>
              <div className={`w-1.5 h-1.5 rounded-full mr-1 ${isActive ? 'bg-white animate-pulse' : 'bg-white/50'
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

        {/* 建议面板（仅在非最小化且非嵌入模式，或者嵌入模式但有空间时显示） */}
        {(!isMinimized && !isInline) && suggestions.length > 0 && (
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
        <div className={`bg-gray-900 ${isMinimized || isInline ? 'p-1.5' : 'p-4'} flex items-center justify-between shrink-0`}>
          <div className="flex items-center space-x-1.5">
            {/* 静音按钮 */}
            <button
              onClick={toggleMute}
              disabled={!isActive}
              className={`${isMinimized || isInline ? 'p-1.5' : 'p-3'} rounded-full transition ${isMuted ? 'bg-red-500' : 'bg-gray-700'
                } ${!isActive ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}`}
              title={isMuted ? '取消静音' : '静音'}
            >
              {isMuted ? <MicOff className={`${isMinimized || isInline ? 'w-3.5 h-3.5' : 'w-5 h-5'} text-white`} /> : <Mic className={`${isMinimized || isInline ? 'w-3.5 h-3.5' : 'w-5 h-5'} text-white`} />}
            </button>

            {/* 视频按钮 */}
            <button
              onClick={toggleVideo}
              disabled={!isActive}
              className={`${isMinimized || isInline ? 'p-1.5' : 'p-3'} rounded-full transition ${!isVideoEnabled ? 'bg-red-500' : 'bg-gray-700'
                } ${!isActive ? 'opacity-50 cursor-not-allowed' : 'hover:bg-gray-600'}`}
              title={isVideoEnabled ? '关闭视频' : '开启视频'}
            >
              {isVideoEnabled ? <Video className={`${isMinimized || isInline ? 'w-3.5 h-3.5' : 'w-5 h-5'} text-white`} /> : <VideoOff className={`${isMinimized || isInline ? 'w-3.5 h-3.5' : 'w-5 h-5'} text-white`} />}
            </button>
          </div>

          {/* 中间：开始/结束按钮 */}
          {(!isMinimized) && (
            <div className="flex-1 px-2 flex justify-center">
              {!isActive ? (
                <button
                  onClick={startCall}
                  disabled={isConnecting}
                  className={`${isInline ? 'px-4 py-1.5 text-xs' : 'px-6 py-3'} bg-green-500 text-white rounded-full font-bold flex items-center hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap`}
                >
                  {isConnecting ? (
                    <>
                      <div className={`${isInline ? 'w-3 h-3' : 'w-5 h-5'} border-2 border-white border-t-transparent rounded-full animate-spin mr-2`} />
                      连接中...
                    </>
                  ) : (
                    <>
                      <Camera className={`${isInline ? 'w-3.5 h-3.5' : 'w-5 h-5'} mr-1.5`} />
                      开始 AI 视频通话
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={stopCall}
                  className={`${isInline ? 'px-4 py-1.5 text-xs' : 'px-6 py-3'} bg-red-500 text-white rounded-full font-bold flex items-center hover:bg-red-600 transition whitespace-nowrap`}
                >
                  <X className={`${isInline ? 'w-3.5 h-3.5' : 'w-5 h-5'} mr-1.5`} />
                  结束通话
                </button>
              )}
            </div>
          )}

          {/* 右侧按钮组 */}
          <div className="flex items-center space-x-1.5">
            {/* 最小化/最大化按钮 - 仅在非嵌入模式下显示 */}
            {isActive && !isInline && (
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

            {/* 关闭按钮 - 仅在非嵌入模式下显示，或者嵌入模式下作为取消/重置 */}
            {!isInline && (
              <button
                onClick={handleClose}
                className={`${isMinimized ? 'p-2' : 'p-3'} rounded-full bg-gray-700 hover:bg-gray-600 transition`}
                title="关闭"
              >
                <X className={`${isMinimized ? 'w-4 h-4' : 'w-5 h-5'} text-white`} />
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIVideoCall;
