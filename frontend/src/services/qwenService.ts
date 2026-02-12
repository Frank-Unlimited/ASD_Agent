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
import { ChatMessage, LogEntry, BehaviorAnalysis, ProfileUpdate, Game } from '../types';
import { getAllGames } from './ragService';

// 动态生成游戏库描述
const getGamesLibraryDescription = () => {
  const games = getAllGames();
  return `
现有游戏库（ID - 名称 - 目标 - 适合特征）：
${games.map(g => `${g.id} - ${g.title} - ${g.target} - ${g.reason}`).join('\n')}
`;
};

const GAMES_LIBRARY = getGamesLibraryDescription();

const SYSTEM_INSTRUCTION_BASE = `
你是一位温暖、专业且充满鼓励的 DIR/Floortime（地板时光）疗法助手。
你的核心任务是基于孩子的**个人档案分析**来辅助家长。

${GAMES_LIBRARY}

交互规则：
1. **个性化回复**：始终参考提供的[当前孩子档案]，利用其中的兴趣点（如喜欢汽车、恐龙）来打比方或提供建议。

2. **游戏推荐（协商式对话）**：采用三阶段流程
   
   阶段1 - 需求探讨（纯文字对话）：
   - 当家长询问"推荐游戏"、"今天玩什么"等时，调用 suggest_game_directions 工具
   - 工具会返回3-5个游戏方向，你要用自然语言介绍每个方向及其理由
   - 不要显示卡片，只用文字讨论
   - 询问家长倾向哪个方向，或者家长有什么其他想法
   
   阶段2 - 方案细化（纯文字对话）：
   - 家长选择方向后（可能说"第一个"、"视觉建构"、"户外的那个"等），调用 search_candidate_games 工具
   - 工具会返回3-5个候选游戏，你要用自然语言介绍每个游戏、理由、材料、时长等
   - 不要显示卡片，只用文字讨论
   - 询问家长选择哪个游戏
   
   阶段3 - 生成游戏卡片：
   - 家长选择具体游戏后（可能说"第二个"、"积木游戏"等），调用 recommend_game_final 工具
   - 这时才会显示游戏卡片，包含完整的实施方案
   - 询问家长是否开始游戏
   
   重要：
   - 前两个阶段都是纯文字对话，不显示卡片
   - 理由必须个性化，引用孩子的具体数据（如"{孩子名}的Visual维度82分，说明视觉兴趣很强"）
   - 使用温暖鼓励的语气，使用表情符号（🎯 🎮 👨‍👩‍👧 🔧）
   
   灵活对话：
   - 如果家长说"都不太合适"、"有没有其他的"、"换一批"等，要询问具体原因（时长？难度？场景？），然后重新调用相应工具
   - 如果家长描述了具体需求（如"想要户外的"、"时间短一点的"、"不需要太多材料的"），要理解需求后重新推荐
   - 不要只依赖按钮交互，要能处理家长的自然语言反馈
   - 保持对话的连贯性，记住之前推荐过什么，避免重复推荐相同的方向

3. **行为记录（重要）**：当家长描述了孩子的**任何具体行为**时，你必须立即调用 log_behavior 工具记录。
   - 行为包括但不限于：正在玩什么、做什么动作、表现出什么情绪、对什么感兴趣、重复什么行为等
   - 例如："孩子正在玩积木"、"他一直盯着旋转的风扇"、"她喜欢排列玩具"、"他在跳来跳去"
   - 即使是简单的日常行为描述，也要记录并分析其兴趣维度
   
   - **关联度（weight）说明**：为每个兴趣维度指定准确的 weight 值（0.1-1.0，只能是正值）
     * 1.0 = 强关联：行为直接体现该维度（如"玩积木"与 Construction）
     * 0.7 = 中等关联：行为部分体现该维度（如"玩积木"与 Visual，需要视觉但不是主要）
     * 0.4 = 弱关联：行为间接涉及该维度（如"玩积木"与 Social，可能有互动但不明显）
   
   - **强度（intensity）说明**：为每个兴趣维度指定准确的 intensity 值（-1.0 到 1.0）
     * +1.0 = 非常喜欢：孩子表现出强烈的兴趣和积极情绪（如"兴奋地玩积木"）
     * +0.5 = 喜欢：孩子表现出明显的兴趣（如"专注地玩积木"）
     * 0.0 = 中性：孩子没有明显的喜欢或讨厌（如"被动地接受"）
     * -0.5 = 不喜欢：孩子表现出抗拒或回避（如"推开积木"）
     * -1.0 = 非常讨厌：孩子表现出强烈的负面情绪（如"哭闹着拒绝"）
   
   - 不要给所有维度都设置相同的 weight 和 intensity，要根据行为的实际特征区分主次
   - 记录后，简短确认即可，不需要长篇大论

4. **本周计划概览**：当家长询问"这周练什么"或"查看计划"时，请调用 create_weekly_plan 工具。

5. **综合评估报告（重要）**：当家长询问以下内容时，你必须立即调用 generate_assessment 工具：
   - "孩子的评估报告"、"评估报告"、"生成评估"
   - "孩子的发展情况"、"发展情况怎么样"
   - "孩子的当前状态"、"现在什么水平"
   - "孩子的进步情况"、"有什么进步"
   - "综合评估"、"查看评估"
   这个工具会基于历史数据生成正式的、结构化的评估报告，不要自己总结，必须调用工具。

6. **页面跳转**：需要更新档案或查看完整日历时，请调用 navigate_page 工具。

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
    const { searchGamesHybrid } = await import('./ragService');
    const candidateGames = await searchGamesHybrid(searchQuery, profileContext, 5);
    
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

重要说明：
1. 为每个兴趣维度指定准确的关联度（weight，0.1-1.0）：
   - 1.0 = 强关联：行为直接体现该维度
   - 0.7 = 中等关联：行为部分体现该维度
   - 0.4 = 弱关联：行为间接涉及该维度
2. 为每个兴趣维度指定准确的强度（intensity，-1.0 到 1.0）：
   - +1.0 = 非常喜欢，+0.5 = 喜欢，0.0 = 中性，-0.5 = 不喜欢，-1.0 = 非常讨厌
3. 不要给所有维度设置相同的 weight 和 intensity，要根据行为的实际特征区分主次
4. 在 reasoning 中解释为什么这个行为与该维度相关，以及孩子的情绪倾向

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
