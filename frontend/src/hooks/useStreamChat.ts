/**
 * 流式聊天 Hook
 * 用于在 React 组件中使用 Qwen 流式对话
 */

import { useState, useCallback } from 'react';
import { sendQwenMessage } from '../services/qwenService';
import { ChatMessage } from '../types';

interface UseStreamChatReturn {
  sendMessage: (message: string, history: ChatMessage[], profileContext: string) => Promise<void>;
  isStreaming: boolean;
  currentResponse: string;
  toolCalls: any[];
}

export function useStreamChat(): UseStreamChatReturn {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [toolCalls, setToolCalls] = useState<any[]>([]);

  const sendMessage = useCallback(async (
    message: string,
    history: ChatMessage[],
    profileContext: string
  ) => {
    setIsStreaming(true);
    setCurrentResponse('');
    setToolCalls([]);

    try {
      await sendQwenMessage(message, history, profileContext, {
        onContent: (chunk) => {
          setCurrentResponse((prev) => prev + chunk);
        },
        onToolCall: (toolCall) => {
          setToolCalls((prev) => [...prev, toolCall]);
        },
        onComplete: (fullText, allToolCalls) => {
          setIsStreaming(false);
          console.log('Stream completed:', { fullText, toolCalls: allToolCalls });
        },
        onError: (error) => {
          console.error('Stream error:', error);
          setIsStreaming(false);
        }
      });
    } catch (error) {
      console.error('Send message error:', error);
      setIsStreaming(false);
      throw error;
    }
  }, []);

  return {
    sendMessage,
    isStreaming,
    currentResponse,
    toolCalls
  };
}
