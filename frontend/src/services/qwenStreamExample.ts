/**
 * Qwen 流式对话使用示例
 * 展示如何在 React 组件中使用流式输出和 Function Calling
 */

import { useState } from 'react';
import { sendQwenMessage } from './qwenService';
import { ChatMessage } from '../types';

/**
 * 示例 1: 基础流式对话
 */
export async function exampleBasicStream(
  message: string,
  history: ChatMessage[],
  profileContext: string,
  onChunk: (text: string) => void
) {
  let fullResponse = '';

  await sendQwenMessage(message, history, profileContext, {
    onContent: (content) => {
      fullResponse += content;
      onChunk(content); // 实时更新 UI
    },
    onComplete: (fullContent) => {
      console.log('Stream completed:', fullContent);
    },
    onError: (error) => {
      console.error('Stream error:', error);
    }
  });

  return fullResponse;
}

/**
 * 示例 2: 处理 Function Call
 */
export async function exampleWithFunctionCall(
  message: string,
  history: ChatMessage[],
  profileContext: string,
  onChunk: (text: string) => void,
  onGameRecommend: (game: { id: string; title: string; reason: string }) => void,
  onBehaviorLog: (log: { behavior: string; tags: string[]; analysis: string }) => void
) {
  await sendQwenMessage(message, history, profileContext, {
    onContent: (content) => {
      onChunk(content);
    },
    onToolCall: (toolCall) => {
      console.log('Tool called:', toolCall);

      try {
        const args = JSON.parse(toolCall.function.arguments);

        switch (toolCall.function.name) {
          case 'recommend_game':
            onGameRecommend(args);
            break;
          case 'log_behavior':
            onBehaviorLog(args);
            break;
          case 'create_weekly_plan':
            console.log('Weekly plan:', args);
            break;
          case 'navigate_page':
            console.log('Navigate to:', args.page);
            break;
        }
      } catch (e) {
        console.error('Failed to parse tool arguments:', e);
      }
    },
    onComplete: (fullContent, toolCalls) => {
      console.log('Completed with', toolCalls.length, 'tool calls');
    },
    onError: (error) => {
      console.error('Error:', error);
    }
  });
}

/**
 * 示例 3: React Hook 使用
 */
export function useQwenChat() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');

  const sendMessage = async (
    message: string,
    history: ChatMessage[],
    profileContext: string
  ) => {
    setIsStreaming(true);
    setCurrentResponse('');

    try {
      await sendQwenMessage(message, history, profileContext, {
        onContent: (content) => {
          setCurrentResponse((prev) => prev + content);
        },
        onToolCall: (toolCall) => {
          // 处理工具调用
          console.log('Tool called:', toolCall);
        },
        onComplete: () => {
          setIsStreaming(false);
        },
        onError: (error) => {
          console.error('Chat error:', error);
          setIsStreaming(false);
        }
      });
    } catch (error) {
      setIsStreaming(false);
      throw error;
    }
  };

  return {
    sendMessage,
    isStreaming,
    currentResponse
  };
}
