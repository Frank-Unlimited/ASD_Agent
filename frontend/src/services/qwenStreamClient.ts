/**
 * Qwen 流式客户端
 * 支持 SSE 流式输出和 Function Calling
 */

export interface QwenMessage {
  role: 'system' | 'user' | 'assistant' | 'tool';
  content: string;
  tool_calls?: ToolCall[];
  tool_call_id?: string;
  name?: string;
}

export interface ToolCall {
  id: string;
  type: 'function';
  function: {
    name: string;
    arguments: string;
  };
}

export interface ToolDefinition {
  type: 'function';
  function: {
    name: string;
    description: string;
    parameters: {
      type: 'object';
      properties: Record<string, unknown>;
      required?: string[];
    };
  };
}

export type ChatWithToolsResult =
  | { type: 'content'; content: string }
  | { type: 'tool_calls'; toolCalls: ToolCall[] };

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
  enable_search?: boolean;
  forced_search?: boolean;
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
    request: Omit<QwenStreamRequest, 'stream' | 'model'> & {
      extra_body?: {
        enable_search?: boolean;
        forced_search?: boolean;
      };
    },
    callbacks: StreamCallbacks
  ): Promise<void> {
    try {
      const { extra_body, ...restRequest } = request;
      
      const fullRequest: QwenStreamRequest = {
        model: this.model,
        stream: true,
        modalities: ['text'], // 仅输出文本模态
        ...restRequest
      };

      // 添加 extra_body 参数（联网搜索等）
      if (extra_body) {
        Object.assign(fullRequest, extra_body);
      }

      console.log('[Qwen Stream] Request:', {
        model: fullRequest.model,
        hasTools: !!fullRequest.tools,
        toolCount: fullRequest.tools?.length || 0,
        toolChoice: fullRequest.tool_choice
      });

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
                  console.log('[Tool Call Delta]', JSON.stringify(delta.tool_calls));
                  for (const toolCallDelta of delta.tool_calls) {
                    if (toolCallDelta.index !== undefined) {
                      // 检查是否是新的 tool call（id 改变或首次出现）
                      const isNewToolCall = toolCallDelta.id && (!currentToolCall || currentToolCall.id !== toolCallDelta.id);
                      
                      if (isNewToolCall) {
                        // 保存之前的 tool call
                        if (currentToolCall && currentToolCall.id) {
                          console.log('[Tool Call] Pushing completed tool call:', currentToolCall);
                          toolCalls.push(currentToolCall as ToolCall);
                        }
                        // 创建新的 tool call
                        currentToolCall = {
                          id: toolCallDelta.id!,
                          type: 'function',
                          function: {
                            name: toolCallDelta.function?.name || '',
                            arguments: toolCallDelta.function?.arguments || ''
                          }
                        };
                        console.log('[Tool Call] New tool call started:', currentToolCall);
                      } else if (currentToolCall) {
                        // 追加到当前 tool call
                        if (toolCallDelta.function?.name) {
                          console.log('[Tool Call] Appending name:', toolCallDelta.function.name);
                          currentToolCall.function!.name += toolCallDelta.function.name;
                        }
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
      extra_body?: {
        enable_search?: boolean;
        forced_search?: boolean;
      };
    }
  ): Promise<string> {
    try {
      const requestBody: any = {
        model: this.model,
        messages,
        stream: false,
        temperature: options?.temperature,
        max_tokens: options?.max_tokens,
        response_format: options?.response_format
      };

      // 添加 extra_body 参数（用于联网搜索）
      if (options?.extra_body) {
        Object.assign(requestBody, options.extra_body);
      }

      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Qwen API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      
      console.log('[Qwen Chat] Response data:', {
        hasChoices: !!data.choices,
        choicesLength: data.choices?.length,
        firstChoice: data.choices?.[0],
        messageContent: data.choices?.[0]?.message?.content
      });
      
      if (!data.choices || data.choices.length === 0) {
        throw new Error('No choices in response');
      }
      
      const content = data.choices[0].message.content;
      if (!content || typeof content !== 'string') {
        throw new Error(`Invalid content type: ${typeof content}`);
      }
      
      return content;
    } catch (error) {
      console.error('Qwen chat error:', error);
      throw error;
    }
  }

  /**
   * 非流式调用，支持工具调用（用于 ReAct 循环）
   * 注意：不传 response_format，DashScope 不支持 tools + json_schema 并存
   */
  async chatWithTools(
    messages: QwenMessage[],
    tools: ToolDefinition[],
    options?: {
      temperature?: number;
      max_tokens?: number;
      tool_choice?: 'auto' | 'none';
    }
  ): Promise<ChatWithToolsResult> {
    const requestBody = {
      model: this.model,
      messages,
      tools,
      tool_choice: options?.tool_choice ?? 'auto',
      stream: false,
      temperature: options?.temperature,
      max_tokens: options?.max_tokens
    };

    console.log('[Qwen chatWithTools] Request:', {
      messagesCount: messages.length,
      toolCount: tools.length,
      tool_choice: requestBody.tool_choice
    });

    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Qwen API error: ${response.status} - ${errorText}`);
    }

    const data = await response.json();
    const message = data.choices?.[0]?.message;

    console.log('[Qwen chatWithTools] Response:', {
      finish_reason: data.choices?.[0]?.finish_reason,
      hasToolCalls: !!message?.tool_calls?.length,
      contentLength: message?.content?.length ?? 0
    });

    if (!message) {
      throw new Error('chatWithTools: no message in response');
    }

    if (message.tool_calls?.length > 0) {
      return { type: 'tool_calls', toolCalls: message.tool_calls as ToolCall[] };
    }

    const content = message.content;
    if (typeof content === 'string' && content.length > 0) {
      return { type: 'content', content };
    }

    throw new Error(
      `chatWithTools: unexpected empty response (finish_reason=${data.choices?.[0]?.finish_reason})`
    );
  }
}

// 导出单例
export const qwenStreamClient = new QwenStreamClient();
