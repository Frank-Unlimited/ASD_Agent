/**
 * API Service for ASD Agent
 * Connects to local Python backend for Chat, uses Mock data for others (temporarily)
 */
import { ChildProfile, Game, CalendarEvent, ChatMessage, GameState, InterestCategory } from '../types';

// Configuration
export const API_BASE_URL = 'http://localhost:7860';
export const USE_REAL_API = true; // 已启用真实后端服务

// Type Definitions
export interface ToolCall {
  tool_name: string;
  tool_display_name: string;
  result: {
    success: boolean;
    message: string;
    data?: any;
    [key: string]: any;
  };
}

export interface ChatResponse {
  response: string;
  conversation_history: ChatMessage[];
  tool_calls: ToolCall[];
}

export interface StreamEvent {
  type: 'tool_call' | 'tool_result' | 'content' | 'done' | 'error';
  data: any;
}

// Session Management
const SESSION_KEY = 'asd_agent_session_id';

export const getSessionId = (): string => {
  let sessionId = localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
};

// API Methods
export const ApiService = {
  /**
   * Send a chat message (non-streaming)
   */
  async sendMessage(
    message: string,
    arg2?: string | any[],
    arg3?: any[]
  ): Promise<string> {
    let childId = "test_child_001";
    let history: any[] = [];

    if (typeof arg2 === 'string') {
      childId = arg2;
      history = arg3 || [];
    } else if (Array.isArray(arg2)) {
      history = arg2;
    }

    const mappedHistory = history.map(msg => ({
      role: msg.role === 'model' ? 'assistant' : msg.role,
      content: msg.text || msg.content
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          child_id: childId,
          conversation_history: mappedHistory,
        }),
      });

      if (!response.ok) {
        const errText = await response.text();
        console.error("Backend Error:", response.status, errText);
        throw new Error(`API Error: ${response.status}`);
      }

      const data: ChatResponse = await response.json();

      let finalResponse = data.response;

      // Phase 7: Transform tool_calls into UI markers
      if (data.tool_calls && data.tool_calls.length > 0) {
        data.tool_calls.forEach(tool => {
          if (tool.tool_name === 'recommend_game' && tool.result.success && tool.result.game) {
            const game = tool.result.game;
            const markerData = {
              id: game.game_id,
              title: game.name,
              reason: game.design_rationale || game.description
            };
            finalResponse += `\n\n:::GAME_RECOMMENDATION:${JSON.stringify(markerData)}:::`;
          }

          if (tool.tool_name === 'generate_assessment' && tool.result.success) {
            const markerData = {
              page: 'PROFILE',
              title: '查看最新评估报告',
              reason: '新的评估报告已生成，点击查看详细分析。'
            };
            finalResponse += `\n\n:::NAVIGATION_CARD:${JSON.stringify(markerData)}:::`;
          }
        });
      }

      return finalResponse;
    } catch (e) {
      console.error("API Call Failed", e);
      throw e;
    }
  },

  /**
   * Send a chat message (streaming via SSE)
   */
  async sendMessageStream(
    message: string,
    childId: string,
    history: any[],
    onContent: (text: string) => void,
    onToolCall?: (toolName: string, displayName: string) => void,
    onToolResult?: (result: any) => void,
    onDone?: (toolCalls: ToolCall[]) => void,
    onError?: (error: string) => void
  ): Promise<void> {
    const mappedHistory = history.map(msg => ({
      role: msg.role === 'model' ? 'assistant' : msg.role,
      content: msg.text || msg.content
    }));

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          child_id: childId,
          conversation_history: mappedHistory,
        }),
      });

      if (!response.ok) {
        const errText = await response.text();
        console.error("Backend Error:", response.status, errText);
        throw new Error(`API Error: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No reader available');

      const decoder = new TextDecoder();
      let buffer = '';
      const toolCalls: ToolCall[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Parse SSE events
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        let eventType = '';
        for (const line of lines) {
          if (line.startsWith('event: ')) {
            eventType = line.slice(7).trim();
          } else if (line.startsWith('data: ') && eventType) {
            const dataStr = line.slice(6);
            try {
              const data = JSON.parse(dataStr);

              switch (eventType) {
                case 'content':
                  if (data.text) {
                    onContent(data.text);
                  }
                  break;
                case 'tool_call':
                  if (onToolCall && data.tool_name) {
                    onToolCall(data.tool_name, data.tool_display_name || data.tool_name);
                  }
                  break;
                case 'tool_result':
                  if (data.tool_name && data.result) {
                    toolCalls.push({
                      tool_name: data.tool_name,
                      tool_display_name: data.tool_display_name || data.tool_name,
                      result: data.result
                    });
                    if (onToolResult) {
                      onToolResult(data);
                    }
                  }
                  break;
                case 'done':
                  if (onDone) {
                    onDone(toolCalls);
                  }
                  break;
                case 'error':
                  if (onError && data.error) {
                    onError(data.error);
                  }
                  break;
              }
            } catch (e) {
              console.warn('Failed to parse SSE data:', dataStr);
            }
            eventType = '';
          }
        }
      }
    } catch (e) {
      console.error("Stream API Call Failed", e);
      if (onError) {
        onError(e instanceof Error ? e.message : 'Unknown error');
      }
      throw e;
    }
  },

  async getProfile(childId?: string): Promise<ChildProfile> {
    if (!childId) {
      childId = localStorage.getItem('active_child_id') || 'test_child_001';
    }
    const res = await fetch(`${API_BASE_URL}/api/profile/${childId}`);
    if (!res.ok) {
      throw new Error(`Failed to fetch profile: ${res.status}`);
    }
    return await res.json();
  },

  async listProfiles(): Promise<ChildProfile[]> {
    const res = await fetch(`${API_BASE_URL}/api/profile/`);
    if (!res.ok) {
      throw new Error(`Failed to list profiles: ${res.status}`);
    }
    const data = await res.json();
    return data.profiles || [];
  },

  async importProfileFromImage(file: File): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE_URL}/api/profile/import/image`, {
      method: 'POST',
      body: formData,
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(err || 'Import failed');
    }

    return await res.json();
  },

  async getGames(): Promise<Game[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/game/list`);
      if (!res.ok) {
        throw new Error(`Failed to fetch games: ${res.status}`);
      }
      const data = await res.json();
      return data.games || [];
    } catch (e) {
      console.error('Failed to fetch games:', e);
      throw e;
    }
  },

  async getCalendar(): Promise<CalendarEvent[]> {
    try {
      const childId = localStorage.getItem('active_child_id') || 'test_child_001';
      const res = await fetch(`${API_BASE_URL}/api/game/calendar/${childId}`);
      if (!res.ok) {
        throw new Error(`Failed to fetch calendar: ${res.status}`);
      }
      const data = await res.json();
      return data.events || [];
    } catch (e) {
      console.error('Failed to fetch calendar:', e);
      throw e;
    }
  },

  async getStats(): Promise<any> {
    try {
      const childId = localStorage.getItem('active_child_id') || 'test_child_001';
      const res = await fetch(`${API_BASE_URL}/api/profile/${childId}/stats`);
      if (!res.ok) {
        throw new Error(`Failed to fetch stats: ${res.status}`);
      }
      return await res.json();
    } catch (e) {
      console.error('Failed to fetch stats:', e);
      throw e;
    }
  },

  async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/chat/health`);
      return res.ok;
    } catch (e) {
      return false;
    }
  }
};

export const api = ApiService;
