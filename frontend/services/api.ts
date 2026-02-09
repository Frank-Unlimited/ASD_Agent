
import { ChildProfile, Game, CalendarEvent, InterestCategory, ChatMessage, LogEntry, BehaviorAnalysis, ProfileUpdate } from '../types';
import { sendGeminiMessage, evaluateSession, analyzeReport, recommendGame } from './geminiService';

// --- Configuration ---
export const USE_REAL_API = true;
const API_BASE_URL = 'http://127.0.0.1:8000'; 

// --- Mock Data (Fallback) ---
const MOCK_GAMES: Game[] = [
  {
    id: '1',
    title: '积木高塔轮流堆',
    target: '共同注意 (Shared Attention)',
    duration: '15 分钟',
    reason: '通过结构化的轮流互动，建立规则感和眼神接触。',
    steps: [
        { instruction: '和孩子面对面坐好，保持视线平齐。', guidance: '位置是关键！确保你能直接看到他的眼睛。' },
        { instruction: '你放一块积木，然后递给孩子一块。', guidance: '动作要慢。拿积木的时候，把积木举到你眼睛旁边。' },
        { instruction: '等待孩子看你一眼（眼神接触）再松手给他。', guidance: '数默数1-2-3，等待那个眼神接触的瞬间。' },
        { instruction: '当塔很高倒塌时，一起夸张地大笑庆祝！', guidance: '情感共鸣很重要。' }
    ]
  },
  {
    id: '2',
    title: '感官泡泡追逐战',
    target: '自我调节 (Self-Regulation)',
    duration: '10 分钟',
    reason: '帮助孩子进行情绪调节，同时增加非语言的共同参与。',
    steps: [
        { instruction: '缓慢地吹出泡泡。', guidance: '观察他的反应。' },
        { instruction: '鼓励孩子去戳破泡泡。', guidance: '如果他不敢碰，你可以先示范戳破一个。' },
        { instruction: '突然停止，做出夸张的表情等待（暂停）。', guidance: '这是“中断模式”。' },
        { instruction: '等待孩子发出信号（声音或手势）要求更多，再继续吹。', guidance: '任何信号都可以！' }
    ]
  },
  {
    id: '3',
    title: 'VR 奇幻森林绘画',
    target: '创造力 & 空间感知',
    duration: '20 分钟',
    reason: '利用沉浸式VR体验，让孩子在3D空间中自由涂鸦。',
    isVR: true,
    steps: [
        { instruction: '帮助孩子佩戴 VR 眼镜，进入“魔法森林”画室。', guidance: '刚开始可能会有不适感，先让孩子适应1-2分钟。' },
        { instruction: '选择“光之画笔”，在空中画出第一条线。', guidance: '示范动作要夸张。' },
        { instruction: '进行“接龙绘画”：你画一部分，孩子补全一部分。', guidance: '这是建立共同关注的好时机。' },
        { instruction: '保存作品并“具象化”展示。', guidance: '在虚拟空间中把画作“挂”在树上。' }
    ]
  }
];

// --- Helper ---
async function fetchWithFallback<T>(endpoint: string, mockData: T): Promise<T> {
  if (!USE_REAL_API) return mockData;
  // Simplified fetch logic for demo
  return mockData; 
}

// --- API Client ---

export const api = {
  getGames: async () => MOCK_GAMES,
  
  // 3. Dialogue Agent: Chat with Context
  sendMessage: async (message: string, history: ChatMessage[], profileContext: string): Promise<string> => {
    if (USE_REAL_API) {
      try {
        return await sendGeminiMessage(message, history, profileContext);
      } catch (err: any) {
        console.warn("Gemini API failed, using fallback.");
      }
    }
    return "网络连接不稳定，请稍后再试。";
  },

  // 4. Recommendation Agent: Explicit Recommendation
  getRecommendation: async (profileContext: string) => {
      if (USE_REAL_API) {
          try {
              return await recommendGame(profileContext);
          } catch (e) {
              console.warn("Recommendation failed");
          }
      }
      return { id: '1', title: '积木高塔 (离线推荐)', reason: '无法连接AI，推荐基础互动游戏。' };
  },

  // 5. Evaluation Agent: Session Analysis
  analyzeSession: async (logs: LogEntry[]) => {
     if (USE_REAL_API) {
        try {
            return await evaluateSession(logs);
        } catch (err) {
            console.warn("Gemini Evaluation failed, using mock.");
        }
     }
     return {
         score: 80,
         feedbackScore: 85,
         explorationScore: 75,
         summary: `模拟分析：互动良好。`,
         suggestion: "继续保持。",
         interestAnalysis: []
     };
  },

  // 6. Evaluation Agent: Report Analysis
  analyzeReport: async (reportText: string): Promise<ProfileUpdate> => {
      if (USE_REAL_API) {
          try {
              return await analyzeReport(reportText);
          } catch(err) {
              console.warn("Gemini Report Analysis failed.");
          }
      }
      return { source: 'REPORT', interestUpdates: [], abilityUpdates: [] };
  },

  // 7. Diagnosis Agent: Report Analysis for Child Profile
  analyzeReportForDiagnosis: async (reportText: string): Promise<string> => {
      if (USE_REAL_API) {
          try {
              const response = await sendGeminiMessage(
                  `请作为专业的ASD孤独症诊断专家，分析以下医疗报告或评估报告。请提取关键信息并给出孩子的整体画像，包括：
1. 核心症状表现
2. 社交沟通能力
3. 重复刻板行为
4. 感觉处理特点
5. 认知发展水平
6. 优势和挑战领域

请用简洁专业的语言描述，字数控制在300字以内。

报告内容：
${reportText}`,
                  [],
                  ''
              );
              return response;
          } catch(err) {
              console.warn("Gemini Diagnosis Analysis failed.");
              return '报告分析失败，请稍后重试。';
          }
      }
      return '离线模式下无法分析报告。';
  },

  // 8. Diagnosis Agent: Verbal Input Analysis
  analyzeVerbalInput: async (verbalInput: string): Promise<string> => {
      if (USE_REAL_API) {
          try {
              const response = await sendGeminiMessage(
                  `请作为专业的ASD孤独症诊断专家，根据家长的描述，分析孩子的情况并给出专业的画像评估。

请从以下维度进行分析：
1. 社交互动特点
2. 沟通表达能力
3. 行为模式和兴趣
4. 感觉处理特点
5. 认知发展水平
6. 优势领域和需要支持的方面

请用温和、专业的语言描述，让家长能够理解，字数控制在300字以内。

家长描述：
${verbalInput}`,
                  [],
                  ''
              );
              return response;
          } catch(err) {
              console.warn("Gemini Verbal Analysis failed.");
              return '分析失败，请稍后重试。';
          }
      }
      return '离线模式下无法分析。';
  }
};
