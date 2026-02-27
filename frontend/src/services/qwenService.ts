/**
 * Qwen Service - 替代 Gemini Service
 * 使用 qwen3-omni-flash 模型，支持流式输出、Function Calling 和结构化输出
 */

import { qwenStreamClient, StreamCallbacks } from './qwenStreamClient';
import {
  GameRecommendationSchema,
  SessionEvaluationSchema,
  BehaviorAnalysisListSchema,
  BehaviorExtractionSchema,
  ProfileUpdateSchema,
  ChatTools
} from './qwenSchemas';
import { ChatMessage, LogEntry, BehaviorAnalysis, ProfileUpdate, Game, EvidenceSnippet } from '../types';
import { floorGameStorageService } from './floorGameStorage';
import { CHAT_SYSTEM_PROMPT } from '../prompts';

// 动态生成游戏库描述（从 floorGameStorage 读取）
const getGamesLibraryDescription = () => {
  const games = floorGameStorageService.getAllGames();
  if (games.length === 0) {
    return '\n（当前游戏库为空，请通过聊天推荐生成游戏）\n';
  }
  return `
现有游戏库（ID - 名称 - 目标 - 概要）：
${games.map(g => `${g.id} - ${g.gameTitle} - ${g.goal} - ${g.summary}`).join('\n')}
`;
};

const GAMES_LIBRARY = getGamesLibraryDescription();

const SYSTEM_INSTRUCTION_BASE = `${CHAT_SYSTEM_PROMPT}

${GAMES_LIBRARY}
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
 * 推荐游戏（使用联网搜索）
 * 返回完整的游戏对象，包含所有步骤信息
 */
export const recommendGame = async (
  profileContext: string
): Promise<Game | null> => {
  let response = '';
  try {
    console.log('[Recommend Agent] 开始推荐游戏，使用联网搜索');

    // 从 profileContext 中提取关键信息构建搜索查询
    const searchQuery = buildSearchQueryFromProfile(profileContext);
    console.log('[Recommend Agent] 搜索查询:', searchQuery);

    // 使用联网搜索获取候选游戏
    const { searchGamesOnline } = await import('./onlineSearchService');
    const candidateGames = await searchGamesOnline(searchQuery, profileContext, 5);

    console.log(`[Recommend Agent] 搜索到 ${candidateGames.length} 个候选游戏`);

    if (candidateGames.length === 0) {
      console.warn('[Recommend Agent] 未找到候选游戏');
      return null;
    }

    // 构建游戏库描述
    const gamesLibrary = `
候选游戏库（从联网搜索获取）：
${candidateGames.map((g, i) => `${i + 1}. ID: ${g.id}
   名称：${g.title}
   目标：${g.target}
   时长：${g.duration}
   ${g.isVR ? '[VR游戏]' : ''}
   特点：${g.reason || '适合自闭症儿童的地板游戏'}
   步骤数：${g.steps.length}`).join('\n\n')}
`;

    const prompt = `
作为推荐 Agent，请分析以下儿童档案，从候选游戏中选择一个最适合当前发展需求的游戏。

${gamesLibrary}

${profileContext}

决策逻辑：
1. 优先选择能利用孩子"高兴趣维度"的游戏（作为切入点）。
2. 针对孩子"低分能力维度"进行训练（作为目标）。
3. 必须从候选游戏中选择一个，返回其 ID（如 "1", "2", "3" 等）。

请只返回选中游戏的序号（1-${candidateGames.length}），例如：{"id": "2"}
`;

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Recommend Agent] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log(SYSTEM_INSTRUCTION_BASE);
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(prompt);
    console.log('='.repeat(80));

    response = await qwenStreamClient.chat(
      [
        { role: 'system', content: SYSTEM_INSTRUCTION_BASE },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 500
      }
    );

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Recommend Agent] 完整响应:');
    console.log('='.repeat(80));
    console.log(response);
    console.log('='.repeat(80));

    console.log('[Recommend Agent] 原始响应:', response);

    // 尝试提取 JSON
    let jsonContent = response;
    const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      jsonContent = jsonMatch[1];
    }

    // 提取选中的游戏序号
    const result = JSON.parse(jsonContent);
    const selectedIndex = parseInt(result.id) - 1; // 转换为数组索引

    if (selectedIndex >= 0 && selectedIndex < candidateGames.length) {
      const selectedGame = candidateGames[selectedIndex];
      console.log('[Recommend Agent] 推荐游戏:', selectedGame.title);
      return selectedGame; // 返回完整的游戏对象
    } else {
      console.warn('[Recommend Agent] 选中的序号无效:', result.id);
      // 如果序号无效，返回第一个游戏
      return candidateGames[0];
    }
  } catch (e) {
    console.error('[Recommend Agent] 推荐失败:', e);
    console.error('[Recommend Agent] 原始响应:', response);
    return null;
  }
};

/**
 * 从档案上下文中提取搜索查询
 */
function buildSearchQueryFromProfile(profileContext: string): string {
  // 提取关键词
  const keywords: string[] = [];

  // 提取兴趣维度
  if (profileContext.includes('Visual')) keywords.push('视觉');
  if (profileContext.includes('Auditory')) keywords.push('听觉');
  if (profileContext.includes('Tactile')) keywords.push('触觉');
  if (profileContext.includes('Motor')) keywords.push('运动');
  if (profileContext.includes('Construction')) keywords.push('建构');
  if (profileContext.includes('Order')) keywords.push('秩序');
  if (profileContext.includes('Cognitive')) keywords.push('认知');
  if (profileContext.includes('Social')) keywords.push('社交');

  // 提取能力维度
  if (profileContext.includes('自我调节')) keywords.push('情绪调节');
  if (profileContext.includes('双向沟通')) keywords.push('互动沟通');
  if (profileContext.includes('复杂沟通')) keywords.push('语言表达');

  // 基础查询
  const baseQuery = '自闭症儿童 地板游戏 DIR Floortime';

  // 组合查询
  return keywords.length > 0
    ? `${baseQuery} ${keywords.slice(0, 3).join(' ')}`
    : baseQuery;
}

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

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Evaluation Agent] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log(SYSTEM_INSTRUCTION_BASE);
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(evalPrompt);
    console.log('='.repeat(80));

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

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Evaluation Agent] 完整响应:');
    console.log('='.repeat(80));
    console.log(evalResponse);
    console.log('='.repeat(80));

    let evalData = JSON.parse(evalResponse);

    // 防御性解析：如果返回的是数组（比如包含了 tool call 对象）
    if (Array.isArray(evalData) && evalData.length > 0) {
      if (evalData[0].arguments) {
        // 取出 tool call 的 arguments
        evalData = typeof evalData[0].arguments === 'string'
          ? JSON.parse(evalData[0].arguments)
          : evalData[0].arguments;
      } else {
        evalData = evalData[0];
      }
    }

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

重要说明：
1. 提取报告中描述的具体行为
2. 为每个行为的兴趣维度指定准确的关联度（weight，0.1-1.0）：
   - 1.0 = 强关联：行为直接体现该维度
   - 0.7 = 中等关联：行为部分体现该维度
   - 0.4 = 弱关联：行为间接涉及该维度
3. 为每个行为的兴趣维度指定准确的强度（intensity，-1.0 到 1.0）：
   - +1.0 = 非常喜欢，+0.5 = 喜欢，0.0 = 中性，-0.5 = 不喜欢，-1.0 = 非常讨厌
4. 不要给所有维度设置相同的 weight 和 intensity
5. 在 reasoning 中解释关联原因和情绪倾向

请严格按照 JSON Schema 返回 ProfileUpdate 结构。
`;

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Report Analysis Agent] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log(SYSTEM_INSTRUCTION_BASE);
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(prompt);
    console.log('='.repeat(80));

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

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Report Analysis Agent] 完整响应:');
    console.log('='.repeat(80));
    console.log(response);
    console.log('='.repeat(80));

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
 * Helper: 保持向后兼容的旧版接口
 */
export const analyzeInterests = async (textInput: string): Promise<BehaviorAnalysis[]> => {
  // 构造模拟的 Evidence，然后通过 inferInterests 处理
  const dummyEvidences: EvidenceSnippet[] = [{
    behavior: textInput.substring(0, 100), // 简化截断
    context: 'Old Interface Call',
    source: 'LOG',
  }];
  return inferInterests(dummyEvidences);
};

/**
 * Universal Pipeline Stage 1: Behavior Extractor
 * 从多模态输入中提取结构化的原子行为证据
 */
export const extractBehaviors = async (
  logs: LogEntry[],
  videoSummary: string,
  parentFeedback: string
): Promise<EvidenceSnippet[]> => {
  try {
    const prompt = `
任务：从以下提供的跨场景互动记录中，提取孩子展现出的具体、可观察的行为片段。

[输入数据]
1. 互动日志 (Log):
${logs.map(l => `[${new Date(l.timestamp).toLocaleTimeString()}] ${l.type === 'emoji' ? '【动作】' : '【语音】'}: ${l.content}`).join('\n')}

2. 视频观察摘要 (Video):
${videoSummary || "无视频摘要"}

3. 家长口头反馈 (Parent):
${parentFeedback || "无家长反馈"}

提取要求：
1. 每条证据必须是具体的、客观的行为事实，避免主观评价或推测。
2. 详细描述行为的内容（behavior）以及发生的背景（context）。
3. 准确标注来源（source：LOG, VIDEO, 或 PARENT）。必须严格使用大写。
4. （预判）该行为可能关联的兴趣维度，如果是社交行为也可以标注。

请严格按照 JSON 格式返回结果，并符合指定的 Schema 结构。
`;

    console.log('[Universal Pipeline - Extractor] 开始提取事实证据...');

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: '你是一个专业的行为分析提取器，擅长从复杂的互动记录中提炼出纯净的、无主观评价的核心行为事实（Evidence），就像医疗化验单一样精准。请必须使用 JSON 格式返回。' },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.1, // 低温度，保证客观提取不发散
        max_tokens: 2000,
        response_format: {
          type: 'json_schema',
          json_schema: BehaviorExtractionSchema
        }
      }
    );

    const data = JSON.parse(response);
    const extractedList = data.evidences || data.evidence_list || data.evidence || [];
    console.log(`[Universal Pipeline - Extractor] 成功提取 ${extractedList.length} 条证据`);
    return extractedList;
  } catch (e) {
    console.error('Behavior Extraction Failed:', e);
    return [];
  }
};

/**
 * Universal Pipeline Stage 2: Interest Inferencer
 * 基于提取出的事实证据，推断兴趣维度的变化
 */
export const inferInterests = async (evidences: EvidenceSnippet[]): Promise<BehaviorAnalysis[]> => {
  try {
    if (evidences.length === 0) return [];

    const prompt = `
任务：基于以下提取出的事实证据（Evidence），映射并推断孩子在八大兴趣维度上的倾向。
${INTEREST_DIMENSIONS_DEF}

提供的证据列表：
${evidences.map((e, index) => `
证据 #${index + 1}:
- 行为: ${e.behavior}
- 背景: ${e.context}
- 来源: ${e.source}
- 潜在相关维度: ${e.relatedDimensions?.join(', ') || '未指定'}
`).join('\n')}

重要说明：
1. 为每个相关的兴趣维度指定准确的关联度（weight，0.1-1.0）。
2. 为每个兴趣维度指定准确的强度（intensity，-1.0 到 1.0）。正值代表喜欢/主动，负值代表讨厌/回避。
3. 在 reasoning 中，必须明确引用输入的“证据 #编号”来解释你的推断逻辑。例如：“基于证据 #1，孩子在看到积木时主动抓取，强度为正...”。

请严格按照 JSON 格式返回推断结果，并符合指定的 Schema 结构。
`;

    console.log('[Universal Pipeline - Inferencer] 开始基于证据推演兴趣...');

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: SYSTEM_INSTRUCTION_BASE + '\n请务必以内置的 JSON 格式返回。' },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.5,
        max_tokens: 1500,
        response_format: {
          type: 'json_schema',
          json_schema: BehaviorAnalysisListSchema
        }
      }
    );

    const data = JSON.parse(response);

    // 安全注入来源信息
    const analyses: BehaviorAnalysis[] = data.analyses || data.analysis || data.interests || data.behavior_analysis_list || [];
    const sourceMap: { [key: string]: 'GAME' | 'REPORT' | 'CHAT' } = {
      'LOG': 'CHAT',
      'VIDEO': 'GAME',
      'PARENT': 'GAME'
    };

    return analyses.map(a => ({
      ...a,
      // 尝试从推理内容中找出对应的证据来源（这是一个简化的 fallback，准确的方案应该是 schema 修改，这里由于 schema 限制暂时写死。
      // 由于 inferInterests 在 Pipeline 中可能由各种输入源调用，真实的来源会在 App.tsx 里被覆盖，所以这里先给个默认值。
      source: 'CHAT'
    }));
  } catch (e) {
    console.error('Interest Inference Failed:', e);
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
          .replace(/:::TOOL_CALL_START:::[\s\S]*?:::TOOL_CALL_END:::/g, '')
          .replace(/:::[A-Z_]+:[\s\S]*?:::/g, '')
          .trim()
      })).filter(m => m.content.length > 0),
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
          .replace(/:::TOOL_CALL_START:::[\s\S]*?:::TOOL_CALL_END:::/g, '')
          .replace(/:::[A-Z_]+:[\s\S]*?:::/g, '')
          .trim()
      })).filter(m => m.content.length > 0),
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
