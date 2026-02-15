
import { ChildProfile, Game, CalendarEvent, InterestCategory, ChatMessage, LogEntry, BehaviorAnalysis, ProfileUpdate } from '../types';
import { sendQwenMessageSync, evaluateSession, analyzeReport, recommendGame } from './qwenService';
import { MEDICAL_REPORT_ANALYSIS_PROMPT, VERBAL_DESCRIPTION_ANALYSIS_PROMPT } from '../prompts';

// --- Configuration ---
export const USE_REAL_API = true;
const API_BASE_URL = 'http://127.0.0.1:8000';

// --- API Client ---

export const api = {
  // 3. Dialogue Agent: Chat with Context
  sendMessage: async (message: string, history: ChatMessage[], profileContext: string): Promise<string> => {
    if (USE_REAL_API) {
      try {
        return await sendQwenMessageSync(message, history, profileContext);
      } catch (err: any) {
        console.warn("Qwen API failed, using fallback.");
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
            console.warn("Qwen Evaluation failed, using mock.");
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
              console.warn("Qwen Report Analysis failed.");
          }
      }
      return { source: 'REPORT', interestUpdates: [], abilityUpdates: [] };
  },

  // 7. Diagnosis Agent: Report Analysis for Child Profile
  analyzeReportForDiagnosis: async (reportText: string): Promise<string> => {
      if (USE_REAL_API) {
          try {
              const prompt = MEDICAL_REPORT_ANALYSIS_PROMPT.replace('{reportContent}', reportText);
              const response = await sendQwenMessageSync(prompt, [], '');
              return response;
          } catch(err) {
              console.warn("Qwen Diagnosis Analysis failed.");
              return '报告分析失败，请稍后重试。';
          }
      }
      return '离线模式下无法分析报告。';
  },

  // 8. Diagnosis Agent: Verbal Input Analysis
  analyzeVerbalInput: async (verbalInput: string): Promise<string> => {
      if (USE_REAL_API) {
          try {
              const prompt = VERBAL_DESCRIPTION_ANALYSIS_PROMPT.replace('{verbalDescription}', verbalInput);
              const response = await sendQwenMessageSync(prompt, [], '');
              return response;
          } catch(err) {
              console.warn("Qwen Verbal Analysis failed.");
              return '分析失败，请稍后重试。';
          }
      }
      return '离线模式下无法分析。';
  }
};
