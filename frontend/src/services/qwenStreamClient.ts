/**
 * Qwen 流式客户端
 * 支持 SSE 流式输出和 Function Calling
 */

interface QwenMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: ToolCall[];
  tool_call_id?: string;
  name?: string;
}

interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

interface QwenStreamRequest {
  model: string;
  messages: QwenMessage[];
  stream: true;
  modalities?: string[];
  temperature?: number;
  max_tokens?: number;
  tools?: any[];
  tool_choice?: 'auto' | 'none' | { type: 'function'; function: { name: string } };
  response_format?: {
    type: 'json_schema' | 'json_object';
    json_schema?: {
      name: string;
      schema: any;
      strict?: boolean;
    };
  };
}

interface StreamChunk {
  id: string;
  choices: Array<{
    index: number;
    delta: {
      role?: string;
      content?: string;
      tool_calls?: Array<{
        index: number;
        id?: string;
        type?: 'function';
        function?: {
          name?: string;
          arguments?: string;
        };
      }>;
    };
    finish_reason?: string | null;
  }>;
}

export interface StreamCallbacks {
  onContent?: (content: string) => void;
  onToolCall?: (toolCall: ToolCall) => void;
  onComplete?: (fullContent: string, toolCalls: ToolCall[]) => void;
  onError?: (error: Error) => void;
}

class QwenStreamClient {
  private apiKey: string;
  private baseUrl: string;
  private model: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_QWEN_API_KEY || '';
    this.baseUrl = import.meta.env.VITE_QWEN_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
    this.model = import.meta.env.VITE_QWEN_MODEL || 'qwen3-omni-flash';

    if (!this.apiKey) {
      console.warn('Qwen API Key not found. Please set VITE_QWEN_API_KEY in .env');
    }
  }

  /**
   * 流式调用 Qwen API
   */
  async streamChat(
    request: Omit<QwenStreamRequest, 'stream' | 'model'>,
    callbacks: StreamCallbacks
  ): Promise<void> {
    try {
      const fullRequest: QwenStreamRequest = {
        model: this.model,
        stream: true,
        modalities: ['text'], // 仅输出文本模态
        ...request
      };

      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(fullRequest)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Qwen API error: ${response.status} - ${errorText}`);
      }

      await this.processStream(response, callbacks);
    } catch (error) {
      console.error('Qwen stream error:', error);
      callbacks.onError?.(error as Error);
      throw error;
    }
  }

  /**
   * 处理 SSE 流
   */
  private async processStream(response: Response, callbacks: StreamCallbacks): Promise<void> {
    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error('No response body');
    }

    const decoder = new TextDecoder();
    let buffer = '';
    let fullContent = '';
    let toolCalls: ToolCall[] = [];
    let currentToolCall: Partial<ToolCall> | null = null;

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (!line.trim() || line.trim() === 'data: [DONE]') continue;
          
          if (line.startsWith('data: ')) {
            try {
              const jsonStr = line.slice(6);
              const chunk: StreamChunk = JSON.parse(jsonStr);

              for (const choice of chunk.choices) {
                const delta = choice.delta;

                // 处理文本内容
                if (delta.content) {
                  fullContent += delta.content;
                  callbacks.onContent?.(delta.content);
                }

                // 处理 tool calls
                if (delta.tool_calls) {
                  for (const toolCallDelta of delta.tool_calls) {
                    if (toolCallDelta.index !== undefined) {
                      // 新的 tool call
                      if (toolCallDelta.id) {
                        if (currentToolCall && currentToolCall.id) {
                          toolCalls.push(currentToolCall as ToolCall);
                        }
                        currentToolCall = {
                          id: toolCallDelta.id,
                          type: 'function',
                          function: {
                            name: toolCallDelta.function?.name || '',
                            arguments: toolCallDelta.function?.arguments || ''
                          }
                        };
                      } else if (currentToolCall) {
                        // 追加 arguments
                        if (toolCallDelta.function?.arguments) {
                          currentToolCall.function!.arguments += toolCallDelta.function.arguments;
                        }
                      }
                    }
                  }
                }

                // 完成
                if (choice.finish_reason) {
                  if (currentToolCall && currentToolCall.id) {
                    const completedToolCall = currentToolCall as ToolCall;
                    toolCalls.push(completedToolCall);
                    callbacks.onToolCall?.(completedToolCall);
                    currentToolCall = null;
                  }
                }
              }
            } catch (e) {
              console.warn('Failed to parse SSE chunk:', line, e);
            }
          }
        }
      }

      // 流结束
      console.log('[Qwen Stream] Stream ended, toolCalls:', toolCalls);
      callbacks.onComplete?.(fullContent, toolCalls);
    } finally {
      reader.releaseLock();
    }
  }

  /**
   * 非流式调用（用于结构化输出）
   */
  async chat(
    messages: QwenMessage[],
    options?: {
      temperature?: number;
      max_tokens?: number;
      response_format?: {
        type: 'json_schema' | 'json_object';
        json_schema?: {
          name: string;
          schema: any;
        };
      };
    }
  ): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: this.model,
          messages,
          stream: false,
          ...options
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Qwen API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      return data.choices[0].message.content;
    } catch (error) {
      console.error('Qwen chat error:', error);
      throw error;
    }
  }
}

// 导出单例
export const qwenStreamClient = new QwenStreamClient();
