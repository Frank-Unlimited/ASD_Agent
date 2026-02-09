/**
 * Qwen Service - 替代 Gemini Service
 * 使用 qwen3-omni-flash 模型，支持流式输出、Function Calling 和结构化输出
 */

import { qwenStreamClient, StreamCallbacks } from './qwenStreamClient';
import {
  GameRecommendationSchema,
  SessionEvaluationSchema,
  BehaviorAnalysisListSchema,
  ProfileUpdateSchema,
  ChatTools
} from './qwenSchemas';
import { ChatMessage, LogEntry, BehaviorAnalysis, ProfileUpdate } from '../types';

const GAMES_LIBRARY = `
现有游戏库（ID - 名称 - 目标 - 适合特征）：
1 - 积木高塔轮流堆 - 共同注意 - 适合视觉关注强、需要建立轮流规则的孩子。
2 - 感官泡泡追逐战 - 自我调节 - 适合需要调节兴奋度、喜欢动态视觉追踪的孩子。
3 - VR 奇幻森林绘画 - 创造力 - 适合喜欢视觉刺激、空间探索，需要提升手眼协调的孩子。
`;

const SYSTEM_INSTRUCTION_BASE = `
你是一位温暖、专业且充满鼓励的 DIR/Floortime（地板时光）疗法助手。
你的核心任务是基于孩子的**个人档案分析**来辅助家长。

${GAMES_LIBRARY}

交互规则：
1. **个性化回复**：始终参考提供的[当前孩子档案]，利用其中的兴趣点（如喜欢汽车、恐龙）来打比方或提供建议。

2. **推荐游戏**：当家长询问玩什么，或你认为需要通过游戏干预时，请调用 recommend_game 工具。

3. **行为记录确认**：当家长描述了孩子具体的日常行为时，请调用 log_behavior 工具记录。

4. **本周计划概览**：当家长询问"这周练什么"或"查看计划"时，请调用 create_weekly_plan 工具。

5. **页面跳转**：需要更新档案或查看完整日历时，请调用 navigate_page 工具。

请始终使用**中文**回答。
`;

const INTEREST_DIMENSIONS_DEF = `
八大兴趣维度定义：
Visual(视觉), Auditory(听觉), Tactile(触觉), Motor(运动), Construction(建构), Order(秩序), Cognitive(认知), Social(社交)。
`;

const ABILITY_DIMENSIONS_DEF = `
DIR 六大能力维度：
自我调节, 亲密感, 双向沟通, 复杂沟通, 情绪思考, 逻辑思维。
`;

/**
 * AGENT 1: RECOMMENDATION AGENT
 * 推荐游戏（结构化输出）
 */
export const recommendGame = async (
  profileContext: string
): Promise<{ id: string; title: string; reason: string } | null> => {
  try {
    const prompt = `
作为推荐 Agent，请分析以下儿童档案，从游戏库中选择一个最适合当前发展需求的游戏。

${GAMES_LIBRARY}

${profileContext}

决策逻辑：
1. 优先选择能利用孩子"高兴趣维度"的游戏（作为切入点）。
2. 针对孩子"低分能力维度"进行训练（作为目标）。

请严格按照 JSON Schema 返回结果。
`;

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: SYSTEM_INSTRUCTION_BASE },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 1000,
        response_format: {
          type: 'json_schema',
          json_schema: GameRecommendationSchema
        }
      }
    );

    return JSON.parse(response);
  } catch (e) {
    console.error('Recommendation Agent Failed:', e);
    return null;
  }
};

/**
 * AGENT 2: EVALUATION AGENT (Session)
 * 评估会话（结构化输出）
 */
export const evaluateSession = async (
  logs: LogEntry[]
): Promise<{
  score: number;
  feedbackScore: number;
  explorationScore: number;
  summary: string;
  suggestion: string;
  interestAnalysis: BehaviorAnalysis[];
}> => {
  try {
    const logContent = logs.map((l) => `[${l.type}] ${l.content}`).join('\n');

    const evalPrompt = `
作为评估 Agent，请分析互动记录：
${logContent}

请评估以下两个维度（0-100分）：
1. feedbackScore: 单次反馈得分（关注互动的质量、回应的及时性和情感连结）。
2. explorationScore: 探索度得分（关注行为的多样性、尝试新事物的意愿和兴趣广度）。

综合得分 score = (feedbackScore + explorationScore) / 2。

请严格按照 JSON Schema 返回结果。
`;

    // 并行执行评估和兴趣分析
    const [evalResponse, interestData] = await Promise.all([
      qwenStreamClient.chat(
        [
          { role: 'system', content: SYSTEM_INSTRUCTION_BASE },
          { role: 'user', content: evalPrompt }
        ],
        {
          temperature: 0.7,
          max_tokens: 1500,
          response_format: {
            type: 'json_schema',
            json_schema: SessionEvaluationSchema
          }
        }
      ),
      analyzeInterests(logContent)
    ]);

    const evalData = JSON.parse(evalResponse);

    return {
      score: evalData.score || 70,
      feedbackScore: evalData.feedbackScore || 70,
      explorationScore: evalData.explorationScore || 70,
      summary: evalData.summary || '记录已分析。',
      suggestion: evalData.suggestion || '继续保持。',
      interestAnalysis: interestData
    };
  } catch (error) {
    console.error('Evaluation Agent Failed:', error);
    return {
      score: 75,
      feedbackScore: 75,
      explorationScore: 75,
      summary: '分析中断，但互动记录已保存。',
      suggestion: '请继续观察孩子反应。',
      interestAnalysis: []
    };
  }
};

/**
 * AGENT 2: EVALUATION AGENT (Report)
 * 分析报告（结构化输出）
 */
export const analyzeReport = async (reportText: string): Promise<ProfileUpdate> => {
  try {
    const prompt = `
作为评估 Agent，分析这份报告并更新档案：
${INTEREST_DIMENSIONS_DEF}
${ABILITY_DIMENSIONS_DEF}

报告内容：
"${reportText}"

请严格按照 JSON Schema 返回 ProfileUpdate 结构。
`;

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: SYSTEM_INSTRUCTION_BASE },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 2000,
        response_format: {
          type: 'json_schema',
          json_schema: ProfileUpdateSchema
        }
      }
    );

    const data = JSON.parse(response);
    return {
      source: 'REPORT',
      interestUpdates: data.interestUpdates || [],
      abilityUpdates: data.abilityUpdates || []
    };
  } catch (e) {
    console.error('Report Analysis Failed:', e);
    return { source: 'REPORT', interestUpdates: [], abilityUpdates: [] };
  }
};

/**
 * Helper: 提取兴趣（结构化输出）
 */
export const analyzeInterests = async (textInput: string): Promise<BehaviorAnalysis[]> => {
  try {
    const prompt = `
任务：提取行为并映射到八大兴趣维度。
${INTEREST_DIMENSIONS_DEF}
文本： "${textInput}"

请严格按照 JSON Schema 返回结果。
`;

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: SYSTEM_INSTRUCTION_BASE },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 1500,
        response_format: {
          type: 'json_schema',
          json_schema: BehaviorAnalysisListSchema
        }
      }
    );

    const data = JSON.parse(response);
    return data.analyses || [];
  } catch (e) {
    console.error('Interest Analysis Failed:', e);
    return [];
  }
};

/**
 * AGENT 3: DIALOGUE AGENT
 * 对话代理（流式输出 + Function Calling）
 */
export const sendQwenMessage = async (
  currentMessage: string,
  history: ChatMessage[],
  profileContext: string,
  callbacks: StreamCallbacks
): Promise<void> => {
  try {
    // 构建消息历史
    const messages = [
      {
        role: 'system' as const,
        content: `${SYSTEM_INSTRUCTION_BASE}\n\n[当前孩子档案]\n${profileContext}`
      },
      ...history.map((msg) => ({
        role: msg.role === 'user' ? ('user' as const) : ('assistant' as const),
        content: msg.text
      })),
      {
        role: 'user' as const,
        content: currentMessage
      }
    ];

    // 流式调用，支持 Function Calling
    await qwenStreamClient.streamChat(
      {
        messages,
        temperature: 0.8,
        max_tokens: 2000,
        tools: ChatTools,
        tool_choice: 'auto'
      },
      callbacks
    );
  } catch (error) {
    console.error('Dialogue Agent Error:', error);
    throw error;
  }
};

/**
 * 非流式对话（用于简单场景）
 */
export const sendQwenMessageSync = async (
  currentMessage: string,
  history: ChatMessage[],
  profileContext: string
): Promise<string> => {
  try {
    const messages = [
      {
        role: 'system' as const,
        content: `${SYSTEM_INSTRUCTION_BASE}\n\n[当前孩子档案]\n${profileContext}`
      },
      ...history.map((msg) => ({
        role: msg.role === 'user' ? ('user' as const) : ('assistant' as const),
        content: msg.text
      })),
      {
        role: 'user' as const,
        content: currentMessage
      }
    ];

    return await qwenStreamClient.chat(messages, {
      temperature: 0.8,
      max_tokens: 2000
    });
  } catch (error) {
    console.error('Dialogue Agent Error:', error);
    throw error;
  }
};
