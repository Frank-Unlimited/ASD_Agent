/**
 * Game Recommendation Conversational Agent
 * 游戏推荐 Agent（ReAct 版）
 *
 * 采用 ReAct（推理-行动-观察）循环模式：
 * LLM 自主决定何时调用 fetchMemory / fetchKnowledge，
 * 直到信息充足后输出最终 JSON。
 *
 * 两步流程：
 * 1. 兴趣分析（analyzeInterestDimensions）：分析8个维度的强度/探索度
 * 2. 地板游戏计划（generateFloorGamePlan）：设计完整游戏实施方案
 */

import { qwenStreamClient, QwenMessage, ToolDefinition } from './qwenStreamClient';
import { ReActInterestAnalysisTools, ReActGamePlanTools } from './qwenSchemas';
import {
  InterestAnalysisResult,
  GameImplementationPlan,
  ChildProfile,
  InterestDimensionType
} from '../types';
import { DimensionMetrics } from './historicalDataHelper';
import { fetchMemoryFacts, formatMemoryFactsForPrompt } from './memoryService';
import { knowledgeService } from './knowledgeService';
import { getAccountId } from './accountService';
import {
  REACT_INTEREST_ANALYSIS_SYSTEM_PROMPT,
  REACT_GAME_PLAN_SYSTEM_PROMPT,
  buildInterestAnalysisPrompt,
  buildFloorGamePlanPrompt
} from '../prompts';

const MAX_REACT_ITERATIONS = 5;

/**
 * ReAct 循环进度事件，用于将思维链实时推送给 UI
 */
export type ReActProgressEvent =
  | { type: 'tool_call'; toolName: 'fetchMemory' | 'fetchKnowledge'; query: string }
  | { type: 'tool_result'; toolName: 'fetchMemory' | 'fetchKnowledge'; result: string };

export type OnReActProgress = (event: ReActProgressEvent) => void;

/**
 * 清理 LLM 返回的 JSON 字符串
 * - 移除 <think>...</think> 思考标签
 * - 移除 markdown 代码块包裹（```json ... ```）
 */
function cleanLLMResponse(response: string): string {
  let cleaned = response;
  cleaned = cleaned.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
  cleaned = cleaned.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '').trim();
  return cleaned;
}

/**
 * ReAct 循环核心执行器
 *
 * 驱动 LLM 与工具交互，直到 LLM 输出最终内容（不再调用工具）为止。
 * 工具执行失败时将错误信息回传给 LLM，循环不中断。
 *
 * @param systemPrompt  ReAct 系统提示（包含 JSON 格式规范）
 * @param userPrompt    初始用户消息
 * @param tools         工具定义列表
 * @param toolHandlers  工具名称 → 异步执行函数的映射
 * @returns             LLM 最终输出的字符串（待调用方解析为 JSON）
 */
async function runReActLoop(
  systemPrompt: string,
  userPrompt: string,
  tools: ToolDefinition[],
  toolHandlers: Record<string, (args: Record<string, string>) => Promise<string>>,
  onProgress?: OnReActProgress
): Promise<string> {
  const messages: QwenMessage[] = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt }
  ];

  for (let iteration = 0; iteration < MAX_REACT_ITERATIONS; iteration++) {
    console.log(`[ReAct] 第 ${iteration + 1}/${MAX_REACT_ITERATIONS} 轮`);

    const result = await qwenStreamClient.chatWithTools(messages, tools, {
      temperature: 0.7,
      max_tokens: 4000
    });

    if (result.type === 'content') {
      console.log(`[ReAct] 第 ${iteration + 1} 轮获得最终答案，循环结束`);
      return result.content;
    }

    // LLM 请求调用工具 —— 先将 assistant 的 tool_calls turn 追加到消息历史
    messages.push({
      role: 'assistant',
      content: '',
      tool_calls: result.toolCalls
    });

    // 依次执行每个工具调用，结果作为 tool 消息追加
    for (const toolCall of result.toolCalls) {
      const toolName = toolCall.function.name;
      let toolResult: string;

      try {
        const args = JSON.parse(toolCall.function.arguments) as Record<string, string>;
        console.log(`[ReAct] 执行工具: ${toolName}`, args);

        // 通知 UI：工具被调用
        onProgress?.({
          type: 'tool_call',
          toolName: toolName as 'fetchMemory' | 'fetchKnowledge',
          query: args.query || ''
        });

        const handler = toolHandlers[toolName];
        if (!handler) {
          toolResult = `[错误] 未知工具：${toolName}`;
          console.error(`[ReAct] 未知工具: ${toolName}`);
        } else {
          toolResult = await handler(args);
          console.log(`[ReAct] 工具 ${toolName} 返回 ${toolResult.length} 字符`);
        }

        // 通知 UI：工具返回结果
        onProgress?.({
          type: 'tool_result',
          toolName: toolName as 'fetchMemory' | 'fetchKnowledge',
          result: toolResult
        });
      } catch (err) {
        // 工具执行失败不终止循环，将错误信息回传给 LLM 继续推理
        toolResult = `[工具执行失败] ${err instanceof Error ? err.message : String(err)}`;
        console.warn(`[ReAct] 工具 ${toolName} 执行失败:`, err);
        onProgress?.({
          type: 'tool_result',
          toolName: toolName as 'fetchMemory' | 'fetchKnowledge',
          result: toolResult
        });
      }

      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        name: toolCall.function.name,
        content: toolResult || '（无结果）'
      });
    }
  }

  throw new Error(
    `[ReAct] 达到最大迭代次数 (${MAX_REACT_ITERATIONS})，未获得最终答案。LLM 可能陷入工具调用循环。`
  );
}

/**
 * 构建兴趣分析阶段的工具处理器
 * 仅需 fetchMemory（无需联网搜索）
 */
function buildInterestAnalysisHandlers(accountId: string) {
  return {
    fetchMemory: async (args: Record<string, string>) => {
      const query = args.query || '';
      console.log('[ReAct/fetchMemory] 查询:', query);
      const facts = await fetchMemoryFacts(accountId, query, 15);
      return formatMemoryFactsForPrompt(facts) || '（暂无相关历史记忆）';
    }
  };
}

/**
 * 构建游戏计划阶段的工具处理器
 * fetchMemory + fetchKnowledge（联网搜索）
 */
function buildGamePlanHandlers(accountId: string) {
  return {
    fetchMemory: async (args: Record<string, string>) => {
      const query = args.query || '';
      console.log('[ReAct/fetchMemory] 查询:', query);
      const facts = await fetchMemoryFacts(accountId, query, 15);
      return formatMemoryFactsForPrompt(facts) || '（暂无相关历史记忆）';
    },
    fetchKnowledge: async (args: Record<string, string>) => {
      const query = args.query || '';
      console.log('[ReAct/fetchKnowledge] 搜索:', query);
      
      // 并行调用联网搜索 + RAG 知识库（搜索足够多的结果供 LLM 使用）
      const result = await knowledgeService.search(query, {
        useWeb: true,
        useRAG: true,
        webCount: 5,
        ragCount: 5
      });
      
      return result.combined || '（暂无相关搜索结果）';
    }
  };
}

/**
 * 步骤1：分析兴趣维度（ReAct 模式）
 *
 * LLM 自主决定何时调用 fetchMemory 查询历史记忆，
 * 信息充足后输出 InterestAnalysisResult JSON。
 */
export const analyzeInterestDimensions = async (
  childProfile: ChildProfile,
  dimensionMetrics: DimensionMetrics[],
  parentContext?: string,
  onProgress?: OnReActProgress
): Promise<InterestAnalysisResult> => {
  try {
    console.log('[analyzeInterestDimensions] 开始 ReAct 兴趣分析:', {
      childName: childProfile.name,
      metricsCount: dimensionMetrics.length
    });

    const userPrompt = buildInterestAnalysisPrompt({
      childProfile,
      dimensionMetrics,
      parentContext
      // 不再预注入 memorySection，由 LLM 通过 fetchMemory 工具自主获取
    });

    console.log('='.repeat(80));
    console.log('[Interest Analysis Agent] System Prompt:');
    console.log(REACT_INTEREST_ANALYSIS_SYSTEM_PROMPT);
    console.log('-'.repeat(80));
    console.log('[Interest Analysis Agent] User Prompt:');
    console.log(userPrompt);
    console.log('='.repeat(80));

    const finalResponse = await runReActLoop(
      REACT_INTEREST_ANALYSIS_SYSTEM_PROMPT,
      userPrompt,
      ReActInterestAnalysisTools,
      buildInterestAnalysisHandlers(getAccountId()),
      onProgress
    );

    console.log('='.repeat(80));
    console.log('[Interest Analysis Agent] 最终响应:');
    console.log(finalResponse);
    console.log('='.repeat(80));

    const cleanedResponse = cleanLLMResponse(finalResponse);
    console.log('[analyzeInterestDimensions] 清理后响应 (前500字):', cleanedResponse.substring(0, 500));

    const raw = JSON.parse(cleanedResponse);
    console.log('[analyzeInterestDimensions] 解析 JSON 成功');

    const result: InterestAnalysisResult = {
      summary: raw.summary || '',
      dimensions: raw.dimensions || [],
      leverageDimensions: raw.leverageDimensions || [],
      exploreDimensions: raw.exploreDimensions || [],
      avoidDimensions: raw.avoidDimensions || [],
      interventionSuggestions: raw.interventionSuggestions || []
    };

    console.log('[analyzeInterestDimensions] 分析完成:', {
      leverage: result.leverageDimensions,
      explore: result.exploreDimensions,
      avoid: result.avoidDimensions,
      suggestionsCount: result.interventionSuggestions.length
    });

    return result;
  } catch (error) {
    console.error('Analyze Interest Dimensions Failed:', error);
    throw error;
  }
};

/**
 * 步骤2：生成地板游戏计划（ReAct 模式）
 *
 * LLM 自主决定何时调用 fetchMemory（历史记录）和 fetchKnowledge（联网搜索），
 * 信息充足后输出 GameImplementationPlan JSON。
 */
export const generateFloorGamePlan = async (
  childProfile: ChildProfile,
  targetDimensions: InterestDimensionType[],
  strategy: 'leverage' | 'explore' | 'mixed',
  parentPreferences?: {
    environment?: string;
    duration?: string;
    otherRequirements?: string;
  },
  conversationHistory?: string,
  specificObjects?: Record<string, string[]>,
  onProgress?: OnReActProgress
): Promise<GameImplementationPlan> => {
  try {
    console.log('[generateFloorGamePlan] 开始 ReAct 游戏计划生成:', {
      childName: childProfile.name,
      targetDimensions,
      strategy,
      hasPreferences: !!parentPreferences
    });

    const userPrompt = buildFloorGamePlanPrompt({
      childProfile,
      targetDimensions,
      strategy,
      parentPreferences,
      conversationHistory,
      specificObjects
      // 不再预注入 memorySection 和 searchResults，由 LLM 通过工具自主获取
    });

    console.log('='.repeat(80));
    console.log('[Game Plan Agent] System Prompt:');
    console.log(REACT_GAME_PLAN_SYSTEM_PROMPT);
    console.log('-'.repeat(80));
    console.log('[Game Plan Agent] User Prompt:');
    console.log(userPrompt);
    console.log('='.repeat(80));

    const finalResponse = await runReActLoop(
      REACT_GAME_PLAN_SYSTEM_PROMPT,
      userPrompt,
      ReActGamePlanTools,
      buildGamePlanHandlers(getAccountId()),
      onProgress
    );

    console.log('='.repeat(80));
    console.log('[Game Plan Agent] 最终响应:');
    console.log(finalResponse);
    console.log('='.repeat(80));

    const cleanedPlanResponse = cleanLLMResponse(finalResponse);
    const data = JSON.parse(cleanedPlanResponse);

    console.log('[generateFloorGamePlan] 游戏计划生成完成:', data.gameTitle || '(未知)');
    if (data._analysis) {
      console.log('[LLM Analysis]', data._analysis);
    }

    return {
      gameId: `floor_game_${Date.now()}`,
      gameTitle: data.gameTitle || '地板游戏',
      summary: data.summary || '',
      goal: data.goal || '',
      steps: data.steps || [],
      materials: data.materials || [],
      _analysis: data._analysis || ''
    };
  } catch (error) {
    console.error('Generate Floor Game Plan Failed:', error);
    throw error;
  }
};
