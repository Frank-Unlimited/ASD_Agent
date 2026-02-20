/**
 * Game Recommendation Conversational Agent
 * 游戏推荐 Agent（重构版）
 *
 * 两步流程：
 * 1. 兴趣分析（analyzeInterestDimensions）：分析8个维度的强度/探索度
 * 2. 地板游戏计划（generateFloorGamePlan）：设计完整游戏实施方案
 */

import { qwenStreamClient } from './qwenStreamClient';
import { searchGamesOnline } from './onlineSearchService';
import {
  InterestAnalysisResult,
  GameImplementationPlan,
  ChildProfile,
  ComprehensiveAssessment,
  BehaviorAnalysis,
  InterestDimensionType
} from '../types';
import { DimensionMetrics } from './historicalDataHelper';
import {
  CONVERSATIONAL_SYSTEM_PROMPT,
  buildInterestAnalysisPrompt,
  buildFloorGamePlanPrompt
} from '../prompts';

/**
 * 清理 LLM 返回的 JSON 字符串
 * - 移除 <think>...</think> 思考标签
 * - 移除 markdown 代码块包裹（```json ... ```）
 */
function cleanLLMResponse(response: string): string {
  let cleaned = response;
  // 移除 <think>...</think> 标签及其内容
  cleaned = cleaned.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
  // 移除 markdown 代码块包裹
  cleaned = cleaned.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '').trim();
  return cleaned;
}

/**
 * 步骤1：分析兴趣维度
 */
export const analyzeInterestDimensions = async (
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment | null,
  dimensionMetrics: DimensionMetrics[],
  recentBehaviors: BehaviorAnalysis[],
  parentContext?: string
): Promise<InterestAnalysisResult> => {
  try {
    console.log('[analyzeInterestDimensions] 开始兴趣分析:', {
      childName: childProfile.name,
      hasAssessment: !!latestAssessment,
      behaviorsCount: recentBehaviors.length,
      metricsCount: dimensionMetrics.length
    });

    const prompt = buildInterestAnalysisPrompt({
      childProfile,
      latestAssessment,
      dimensionMetrics,
      recentBehaviors,
      parentContext
    });

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 4000,
        response_format: {
          type: 'json_object'
        }
      }
    );

    console.log('[analyzeInterestDimensions] Raw LLM response:', response);
    
    if (!response || typeof response !== 'string') {
      throw new Error(`Invalid LLM response: ${typeof response}`);
    }
    
    const cleanedResponse = cleanLLMResponse(response);
    console.log('[analyzeInterestDimensions] Cleaned response (first 500 chars):', cleanedResponse.substring(0, 500));
    
    const raw = JSON.parse(cleanedResponse);
    console.log('[analyzeInterestDimensions] Parsed JSON:', raw);
    // 确保所有字段都有默认值，防止 LLM 返回不完整
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
 * 步骤2：生成地板游戏计划
 * 并行执行：联网搜索 + LLM 生成
 */
export const generateFloorGamePlan = async (
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment | null,
  targetDimensions: InterestDimensionType[],
  strategy: 'leverage' | 'explore' | 'mixed',
  recentBehaviors: BehaviorAnalysis[],
  parentPreferences?: {
    environment?: string;
    duration?: string;
    otherRequirements?: string;
  },
  conversationHistory?: string,
  specificObjects?: Record<string, string[]>
): Promise<GameImplementationPlan> => {
  try {
    console.log('[generateFloorGamePlan] 开始生成游戏计划:', {
      childName: childProfile.name,
      targetDimensions,
      strategy,
      hasPreferences: !!parentPreferences
    });

    // 并行：联网搜索参考资料 + 准备 prompt
    let searchResults = '';
    try {
      // 从 specificObjects 中提取与目标维度相关的具体对象
      const objectKeywords = specificObjects
        ? targetDimensions
            .flatMap(dim => specificObjects[dim] || [])
            .slice(0, 4) // 最多取4个，避免关键词过长
            .join(' ')
        : '';
      const searchQuery = `${targetDimensions.join(' ')} ${objectKeywords} 自闭症儿童 DIR Floortime 地板游戏 ${strategy === 'explore' ? '探索' : '互动'}`.trim();
      const childContext = `
儿童：${childProfile.name}，${childProfile.gender}
${latestAssessment ? `画像：${latestAssessment.currentProfile}` : '首次使用'}
目标维度：${targetDimensions.join('、')}
${objectKeywords ? `感兴趣的对象：${objectKeywords}` : ''}
策略：${strategy}
`;
      const games = await searchGamesOnline(searchQuery, childContext, 3);
      if (games.length > 0) {
        searchResults = games.map(g =>
          `- ${g.title}：${g.summary || g.reason}（${g.duration}）`
        ).join('\n');
        console.log(`[generateFloorGamePlan] 联网搜索到 ${games.length} 个参考游戏`);
      }
    } catch (err) {
      console.warn('[generateFloorGamePlan] 联网搜索失败，仅使用LLM生成:', err);
    }

    const prompt = buildFloorGamePlanPrompt({
      childProfile,
      latestAssessment,
      targetDimensions,
      strategy,
      recentBehaviors,
      parentPreferences,
      conversationHistory,
      searchResults: searchResults || undefined,
      specificObjects
    });

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.8,
        max_tokens: 3000,
        response_format: {
          type: 'json_object'
        },
        extra_body: {
          enable_search: true  // 启用 LLM 联网搜索，获取最新游戏信息
        }
      }
    );

    // console.log('[generateFloorGamePlan] Raw LLM response:', response);
    const cleanedPlanResponse = cleanLLMResponse(response);
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
