import OpenAI from 'openai';
import { env } from '../config/env';

/**
 * AI Service - Supports both DeepSeek and OpenAI
 */
class AIService {
  private client: OpenAI;
  private provider: string;

  constructor() {
    this.provider = env.AI_PROVIDER || 'deepseek';

    console.log('🔧 AI Service Configuration:');
    console.log('  Provider:', this.provider);
    console.log('  DeepSeek API Key:', env.DEEPSEEK_API_KEY ? `${env.DEEPSEEK_API_KEY.substring(0, 10)}...` : 'NOT SET');
    console.log('  DeepSeek Base URL:', env.DEEPSEEK_BASE_URL);
    console.log('  OpenAI API Key:', env.OPENAI_API_KEY ? `${env.OPENAI_API_KEY.substring(0, 10)}...` : 'NOT SET');

    // Initialize client based on provider
    if (this.provider === 'deepseek') {
      if (!env.DEEPSEEK_API_KEY || env.DEEPSEEK_API_KEY === 'your-deepseek-api-key-here') {
        console.error('❌ DeepSeek API key not configured! Please set DEEPSEEK_API_KEY in .env file');
        console.log('💡 Tip: Get your API key from https://platform.deepseek.com/');
      }
      this.client = new OpenAI({
        apiKey: env.DEEPSEEK_API_KEY,
        baseURL: env.DEEPSEEK_BASE_URL
      });
      console.log('✅ AI Service initialized with DeepSeek');
    } else {
      if (!env.OPENAI_API_KEY || env.OPENAI_API_KEY === 'your-openai-api-key-here') {
        console.error('❌ OpenAI API key not configured! Please set OPENAI_API_KEY in .env file');
        console.log('💡 Tip: Get your API key from https://platform.openai.com/');
      }
      this.client = new OpenAI({
        apiKey: env.OPENAI_API_KEY
      });
      console.log('✅ AI Service initialized with OpenAI');
    }
  }

  /**
   * Get the appropriate model name based on provider
   */
  private getModel(): string {
    if (this.provider === 'deepseek') {
      return 'deepseek-chat';
    }
    return 'gpt-4';
  }

  /**
   * Analyze assessment report and generate child profile
   */
  async analyzeAssessment(assessmentData: any): Promise<any> {
    try {
      console.log('🤖 Starting AI analysis...');
      console.log('  Provider:', this.provider);
      console.log('  Model:', this.getModel());
      
      const prompt = this.buildAssessmentPrompt(assessmentData);
      console.log('  Prompt length:', prompt.length, 'characters');

      const response = await this.client.chat.completions.create({
        model: this.getModel(),
        messages: [
          {
            role: 'system',
            content: '你是一位专业的ASD（孤独症谱系障碍）儿童发育治疗师，擅长分析评估报告并制定干预方案。请使用中文回答。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 2000
      });

      console.log('✅ AI response received');
      console.log('  Usage:', response.usage);

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('AI服务未返回结果');
      }

      // 尝试解析JSON
      try {
        const parsed = JSON.parse(result);
        console.log('✅ Successfully parsed AI response as JSON');
        return parsed;
      } catch {
        console.log('⚠️ Response is not pure JSON, trying to extract...');
        // 如果返回的不是纯JSON，尝试提取JSON部分
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]);
          console.log('✅ Successfully extracted and parsed JSON from response');
          return parsed;
        }
        throw new Error('无法解析AI返回的结果');
      }
    } catch (error: any) {
      console.error('❌ AI分析失败:', error);
      console.error('  Error type:', error.constructor.name);
      console.error('  Error message:', error.message);
      if (error.status) {
        console.error('  HTTP Status:', error.status);
      }
      if (error.code) {
        console.error('  Error code:', error.code);
      }
      throw error;
    }
  }

  /**
   * Build prompt for assessment analysis
   */
  private buildAssessmentPrompt(assessmentData: any): string {
    return `你是专业的ASD儿童发育治疗师，请分析以下评估报告，生成孩子的多维度画像。

评估报告内容：
${assessmentData}

请按以下JSON格式返回分析结果（只返回JSON，不要其他文字）：

{
  "profile": {
    "interests": ["兴趣1", "兴趣2"],
    "strengths": ["优势1", "优势2"],
    "challenges": ["挑战1", "挑战2"]
  },
  "recommendedDimensions": [
    {"name": "维度名", "description": "描述", "priority": "high"}
  ],
  "initialGoals": ["目标1", "目标2", "目标3"],
  "analysis": "整体分析总结"
}`;
  }

  /**
   * Recommend games based on child profile
   */
  async recommendGames(childProfile: any, observations: any[] = []): Promise<any> {
    try {
      const prompt = this.buildGameRecommendationPrompt(childProfile, observations);

      const response = await this.client.chat.completions.create({
        model: this.getModel(),
        messages: [
          {
            role: 'system',
            content: '你是一位专业的地板时光治疗师，擅长为ASD儿童推荐合适的干预游戏。请使用中文回答。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.8,
        max_tokens: 2000
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('AI服务未返回结果');
      }

      try {
        return JSON.parse(result);
      } catch {
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
        throw new Error('无法解析AI返回的结果');
      }
    } catch (error) {
      console.error('游戏推荐失败:', error);
      throw error;
    }
  }

  /**
   * Build prompt for game recommendation
   */
  private buildGameRecommendationPrompt(childProfile: any, observations: any[]): string {
    const obsText = observations.length > 0
      ? `最近观察：\n${observations.map(o => `- ${o.description || o.text || o}`).join('\n')}`
      : '';

    return `请为以下ASD儿童推荐合适的地板时光游戏：

孩子画像：
- 兴趣：${childProfile.interests?.join('、') || '待观察'}
- 优势：${childProfile.strengths?.join('、') || '待评估'}
- 挑战：${childProfile.challenges?.join('、') || '待评估'}

${obsText}

请推荐3个最适合的游戏，按以下JSON格式返回（只返回JSON）：

{
  "recommendations": [
    {
      "id": "game_001",
      "name": "游戏名称",
      "description": "游戏描述",
      "targetGoals": ["目标1", "目标2"],
      "difficulty": "初级",
      "duration": "15分钟",
      "reason": "推荐理由"
    }
  ]
}`;
  }

  /**
   * Analyze session and generate summary
   */
  async analyzeSession(gameName: string, observations: any[], duration: number): Promise<any> {
    try {
      const obsDescriptions = observations.map(o => o.description || o.text || o.label || '').join('\n');

      const prompt = `请总结本次ASD地板时光干预游戏会话：

游戏：${gameName}
时长：${duration}分钟

观察记录：
${obsDescriptions}

请按以下JSON格式返回分析（只返回JSON）：

{
  "highlights": ["亮点1", "亮点2"],
  "concerns": ["关注点1"],
  "overallAssessment": "整体评价",
  "comparisonWithLast": "与上次对比",
  "nextFocus": ["下一步重点1", "重点2"]
}`;

      const response = await this.client.chat.completions.create({
        model: this.getModel(),
        messages: [
          {
            role: 'system',
            content: '你是一位专业的儿童治疗师，擅长总结ASD干预会话并提供专业建议。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 1500
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('AI服务未返回结果');
      }

      try {
        return JSON.parse(result);
      } catch {
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
        throw new Error('无法解析AI返回的结果');
      }
    } catch (error) {
      console.error('会话分析失败:', error);
      throw error;
    }
  }

  /**
   * Generate feedback form based on session summary
   */
  async generateFeedbackForm(sessionSummary: any): Promise<any> {
    try {
      const prompt = `请为家长生成个性化的游戏反馈问卷：

本次游戏总结：
- 亮点：${sessionSummary.highlights?.join(', ') || '无'}
- 关注：${sessionSummary.concerns?.join(', ') || '无'}
- 整体评价：${sessionSummary.overallAssessment}

请生成3-5个问题，按以下JSON格式返回（只返回JSON）：

{
  "questions": [
    {
      "id": "q1",
      "type": "rating",
      "question": "问题内容",
      "scale": [1,2,3,4,5],
      "labels": ["标签1", "标签5"]
    }
  ]
}`;

      const response = await this.client.chat.completions.create({
        model: this.getModel(),
        messages: [
          {
            role: 'system',
            content: '你是一位专业的儿童治疗师，擅长设计反馈问卷。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 1500
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('AI服务未返回结果');
      }

      try {
        return JSON.parse(result);
      } catch {
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
        throw new Error('无法解析AI返回的结果');
      }
    } catch (error) {
      console.error('生成反馈表失败:', error);
      throw error;
    }
  }

  /**
   * Re-evaluate child based on all data
   */
  async reEvaluateChild(childId: number, allObservations: any[], allSessions: any[], previousProfile: any): Promise<any> {
    try {
      const recentObs = allObservations.slice(-20).map(o => o.description || o.text || '').join('\n');
      const sessionSummaries = allSessions.map(s => s.summary || '已完成会话').join('\n');

      const prompt = `请综合评估ASD儿童的进展情况：

初始画像：
${JSON.stringify(previousProfile, null, 2)}

最近观察：
${recentObs}

历史会话：
${sessionSummaries}

请重新评估并按以下JSON格式返回（只返回JSON）：

{
  "progressReport": {
    "overallVelocity": "快速/中速/慢速",
    "dimensionProgress": {"眼神接触": "+65%", "双向沟通": "+40%"},
    "milestonesAchieved": ["里程碑1", "里程碑2"]
  },
  "updatedProfile": {
    "interests": ["更新的兴趣"],
    "strengths": ["更新的优势"],
    "challenges": ["更新的挑战"]
  },
  "dimensionHealth": [
    {"dimension": "眼神接触", "score": 8.5, "status": "excellent", "action": "maintain"},
    {"dimension": "情绪调节", "score": 5.8, "status": "needs_attention", "action": "change_strategy"}
  ],
  "nextSteps": [
    {"dimension": "眼神接触", "action": "maintain", "strategy": "继续当前策略"}
  ]
}`;

      const response = await this.client.chat.completions.create({
        model: this.getModel(),
        messages: [
          {
            role: 'system',
            content: '你是一位专业的儿童发育治疗师，擅长评估ASD儿童的进展。'
          },
          {
            role: 'user',
            content: prompt
          }
        ],
        temperature: 0.7,
        max_tokens: 2500
      });

      const result = response.choices[0].message?.content;
      if (!result) {
        throw new Error('AI服务未返回结果');
      }

      try {
        return JSON.parse(result);
      } catch {
        const jsonMatch = result.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]);
        }
        throw new Error('无法解析AI返回的结果');
      }
    } catch (error) {
      console.error('再评估失败:', error);
      throw error;
    }
  }
}

// Export singleton instance
const aiService = new AIService();
export { aiService, AIService };
