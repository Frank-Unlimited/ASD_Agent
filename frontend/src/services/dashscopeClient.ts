/**
 * 阿里云 DashScope API 客户端
 * 用于调用通义千问多模态模型
 */

interface DashScopeMessage {
  role: 'user' | 'assistant' | 'system';
  content: Array<{
    type: 'text' | 'image_url';
    text?: string;
    image_url?: {
      url: string;
    };
  }>;
}

interface DashScopeRequest {
  model: string;
  messages: DashScopeMessage[];
  temperature?: number;
  max_tokens?: number;
  response_format?: {
    type: 'json_object' | 'text';
  };
}

interface DashScopeResponse {
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
  }>;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

class DashScopeClient {
  private apiKey: string;
  private baseUrl: string;
  private model: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_DASHSCOPE_API_KEY || '';
    this.baseUrl = import.meta.env.VITE_DASHSCOPE_BASE_URL || 'https://dashscope.aliyuncs.com/compatible-mode/v1';
    this.model = import.meta.env.VITE_DASHSCOPE_MODEL || 'qwen-vl-plus';

    if (!this.apiKey) {
      console.warn('DashScope API Key not found. Please set VITE_DASHSCOPE_API_KEY in .env');
    }
  }

  /**
   * 调用 DashScope API
   */
  async callAPI(request: DashScopeRequest): Promise<string> {
    try {
      const response = await fetch(`${this.baseUrl}/chat/completions`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`DashScope API error: ${response.status} - ${errorText}`);
      }

      const data: DashScopeResponse = await response.json();
      
      if (!data.choices || data.choices.length === 0) {
        throw new Error('No response from DashScope API');
      }

      return data.choices[0].message.content;
    } catch (error) {
      console.error('DashScope API call failed:', error);
      throw error;
    }
  }

  /**
   * 分析图片
   */
  async analyzeImage(
    base64Image: string, 
    prompt: string = '请详细分析这张图片',
    useJsonFormat: boolean = false
  ): Promise<string> {
    const request: DashScopeRequest = {
      model: this.model,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'text',
            text: prompt
          },
          {
            type: 'image_url',
            image_url: {
              url: `data:image/jpeg;base64,${base64Image}`
            }
          }
        ]
      }],
      temperature: 0.7,
      max_tokens: 2000
    };

    // 如果需要 JSON 格式输出，添加 response_format
    if (useJsonFormat) {
      request.response_format = {
        type: 'json_object'
      };
    }

    return await this.callAPI(request);
  }

  /**
   * 分析视频（如果支持）
   */
  async analyzeVideo(base64Video: string, prompt: string = '请分析这个视频'): Promise<string> {
    // 注意：视频分析可能需要不同的 API 端点或模型
    // 这里使用相同的接口，实际使用时可能需要调整
    const request: DashScopeRequest = {
      model: this.model,
      messages: [{
        role: 'user',
        content: [
          {
            type: 'text',
            text: prompt
          },
          {
            type: 'image_url', // 视频可能需要特殊处理
            image_url: {
              url: `data:video/mp4;base64,${base64Video}`
            }
          }
        ]
      }],
      temperature: 0.7,
      max_tokens: 3000
    };

    return await this.callAPI(request);
  }

  /**
   * 纯文本对话
   */
  async chat(text: string): Promise<string> {
    const request: DashScopeRequest = {
      model: this.model,
      messages: [{
        role: 'user',
        content: [{
          type: 'text',
          text: text
        }]
      }],
      temperature: 0.7,
      max_tokens: 2000
    };

    return await this.callAPI(request);
  }
}

// 导出单例
export const dashscopeClient = new DashScopeClient();
