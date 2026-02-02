/**
 * API Service for ASD Agent
 * Connects to local Python backend for Chat, uses Mock data for others (temporarily)
 */
import { ChildProfile, Game, CalendarEvent, ChatMessage, GameState, InterestCategory } from '../types';

// Configuration
export const API_BASE_URL = 'http://localhost:7860';
export const USE_REAL_API = true;

// --- Mock Data (Fallback for missing backend endpoints) ---

const MOCK_PROFILE: ChildProfile = {
  name: "乐乐",
  age: 4,
  diagnosis: "ASD 谱系一级",
  avatar: "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
};

const MOCK_GAMES: Game[] = [
  {
    id: '1',
    title: '积木高塔轮流堆',
    target: '共同注意 (Shared Attention)',
    duration: '15 分钟',
    reason: '通过结构化的轮流互动，建立规则感和眼神接触。',
    steps: [
      {
        instruction: '和孩子面对面坐好，保持视线平齐。',
        guidance: '位置是关键！确保你能直接看到他的眼睛。如果他坐在地上，你也趴在地上。'
      },
      {
        instruction: '你放一块积木，然后递给孩子一块。',
        guidance: '动作要慢。拿积木的时候，把积木举到你眼睛旁边，吸引他看你的脸。'
      },
      {
        instruction: '等待孩子看你一眼（即使是瞥一眼），再把积木给他。',
        guidance: '不要催促。如果他不看，轻轻叫名字，或者把积木移到视线中间。'
      }
    ]
  },
  {
    id: '2',
    title: '感官泡泡追逐战',
    target: '自我调节 (Self-Regulation)',
    duration: '10 分钟',
    reason: '利用泡泡的视觉刺激调节情绪，释放多余能量。',
    steps: [
      {
        instruction: '吹出大量泡泡，让孩子去追逐和戳破。',
        guidance: '观察孩子的兴奋度。如果过于兴奋开始尖叫，就吹慢一点，让他安静地观察泡泡落地。'
      },
      {
        instruction: '轮流吹泡泡：你吹一次，让孩子吹一次。',
        guidance: '通过"轮流"加入社交规则。'
      }
    ]
  }
];

const MOCK_CALENDAR: CalendarEvent[] = [
  { day: 20, weekday: '一', status: 'completed', gameTitle: '积木高塔' },
  { day: 21, weekday: '二', status: 'today', gameTitle: '感官泡泡', time: '10:00' },
  { day: 22, weekday: '三', status: 'future' },
  { day: 23, weekday: '四', status: 'future' },
  { day: 24, weekday: '五', status: 'future' },
  { day: 25, weekday: '六', status: 'future' },
  { day: 26, weekday: '日', status: 'future' },
];

const MOCK_STATS = {
  radar: [
    { subject: '共同注意', A: 80, fullMark: 100 },
    { subject: '情感互动', A: 65, fullMark: 100 },
    { subject: '语言沟通', A: 40, fullMark: 100 },
    { subject: '逻辑思维', A: 60, fullMark: 100 },
    { subject: '运动感知', A: 90, fullMark: 100 },
    { subject: '自我调节', A: 55, fullMark: 100 },
  ],
  trend: [
    { name: '周一', engagement: 40 },
    { name: '周二', engagement: 60 },
    { name: '周三', engagement: 55 },
    { name: '周四', engagement: 80 },
    { name: '周五', engagement: 70 },
    { name: '周六', engagement: 90 },
    { name: '周日', engagement: 85 },
  ],
  interests: [
    {
      category: "感官偏好",
      items: [
        { name: "旋转物体", level: 5 },
        { name: "举高高", level: 4 },
        { name: "玩水", level: 3 },
      ]
    },
    {
      category: "特定主题",
      items: [
        { name: "火车", level: 5 },
        { name: "对齐物品", level: 4 },
        { name: "数字", level: 2 },
      ]
    }
  ] as InterestCategory[]
};


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

  async getProfile(childId?: string): Promise<ChildProfile> {
    if (!childId) return MOCK_PROFILE;
    try {
      const res = await fetch(`${API_BASE_URL}/api/profile/${childId}`);
      if (res.ok) {
        return await res.json();
      } else if (res.status === 404) {
        console.info(`Profile ${childId} not found, falling back.`);
      }
    } catch (e) {
      console.warn("Failed to fetch real profile:", e);
    }
    return childId === "test_child_001" ? MOCK_PROFILE : null;
  },

  async listProfiles(): Promise<ChildProfile[]> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/profile/`);
      if (res.ok) {
        const data = await res.json();
        return data.profiles || [];
      }
    } catch (e) {
      console.error("Failed to list profiles", e);
    }
    return [];
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
    return MOCK_GAMES;
  },

  async getCalendar(): Promise<CalendarEvent[]> {
    return MOCK_CALENDAR;
  },

  async getStats(): Promise<any> {
    return MOCK_STATS;
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
