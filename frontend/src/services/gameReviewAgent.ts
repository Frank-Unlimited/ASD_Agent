/**
 * Game Review Agent
 * 游戏复盘 Agent - 游戏结束后进行专业的 DIR/Floortime 视角复盘
 */

import { qwenStreamClient } from './qwenStreamClient';
import { GameReviewSchema } from './qwenSchemas';
import { FloorGame, GameReviewResult, ChildProfile, EvidenceSnippet } from '../types';
import { floorGameStorageService } from './floorGameStorage';
import { GAME_REVIEW_SYSTEM_PROMPT, buildGameReviewPrompt } from '../prompts/gameReviewPrompt';
import { fetchMemoryFacts, formatMemoryFactsForPrompt } from './memoryService';
import { getAccountId } from './accountService';

/**
 * 专家会诊层 (Specialist Agent): DIR/Floortime 游戏复盘专家
 * 结合历史事实(Facts)与当场提取的证据(Evidences)，给出专业点评
 */
export async function reviewFloorGame(params: {
  game: FloorGame;
  evidences: EvidenceSnippet[];
  parentFeedback: string;
}): Promise<GameReviewResult> {
  const { game, evidences, parentFeedback } = params;

  console.log('[GameReview] 开始复盘，游戏:', game.gameTitle);

  // 读取孩子档案
  let childProfile: ChildProfile;
  try {
    const saved = localStorage.getItem('asd_floortime_child_profile');
    if (!saved) throw new Error('未找到孩子档案');
    childProfile = JSON.parse(saved);
  } catch (e) {
    console.error('[GameReview] 读取孩子档案失败:', e);
    throw new Error('无法读取孩子档案，请先创建孩子档案');
  }

  // 拉取历史互动记忆
  const memoryFacts = await fetchMemoryFacts(
    getAccountId(),
    `${childProfile.name}在游戏中的参与模式、情感反应规律和有效的互动策略`,
    10
  );
  const memorySection = formatMemoryFactsForPrompt(memoryFacts);

  // 构建 prompt
  const userPrompt = buildGameReviewPrompt({
    childProfile,
    game,
    evidences,
    parentFeedback,
    memorySection: memorySection || undefined
  });

  // 打印完整的 prompt
  console.log('='.repeat(80));
  console.log('[Game Review Agent] 完整 Prompt:');
  console.log('='.repeat(80));
  console.log('System Prompt:');
  console.log(GAME_REVIEW_SYSTEM_PROMPT);
  console.log('-'.repeat(80));
  console.log('User Prompt:');
  console.log(userPrompt);
  console.log('='.repeat(80));

  // 调用 LLM
  const response = await qwenStreamClient.chat(
    [
      { role: 'system', content: GAME_REVIEW_SYSTEM_PROMPT },
      { role: 'user', content: userPrompt }
    ],
    {
      temperature: 0.7,
      max_tokens: 3000,
      response_format: {
        type: 'json_schema',
        json_schema: GameReviewSchema
      }
    }
  );

  // 打印完整的响应
  console.log('='.repeat(80));
  console.log('[Game Review Agent] 完整响应:');
  console.log('='.repeat(80));
  console.log(response);
  console.log('='.repeat(80));

  console.log('[GameReview] Raw response:', response);

  // 解析响应
  let data;
  try {
    data = JSON.parse(response);
  } catch (parseError) {
    console.error('[GameReview] JSON parse error:', parseError);
    throw new Error('无法解析复盘结果，请重试');
  }

  if (Array.isArray(data)) {
    data = data[0];
  }

  if (data.type === 'object' && data.properties && data.required) {
    console.error('[GameReview] LLM 返回了 Schema 定义而不是数据！');
    throw new Error('LLM 返回了 Schema 定义而不是实际数据，请再试一次');
  }

  // 验证必需字段
  const requiredFields = ['reviewSummary', 'scores', 'recommendation', 'nextStepSuggestion'];
  const missingFields = requiredFields.filter(field => !(field in data));
  if (missingFields.length > 0) {
    console.error('[GameReview] 缺少必需字段:', missingFields);
    throw new Error(`复盘数据不完整，缺少字段: ${missingFields.join(', ')}`);
  }

  const clamp = (v: number) => Math.max(0, Math.min(100, Math.round(v)));
  const review: GameReviewResult = {
    reviewSummary: data.reviewSummary,
    scores: {
      childEngagement: clamp(data.scores.childEngagement),
      gameCompletion: clamp(data.scores.gameCompletion),
      emotionalConnection: clamp(data.scores.emotionalConnection),
      communicationLevel: clamp(data.scores.communicationLevel),
      skillProgress: clamp(data.scores.skillProgress),
      parentExecution: clamp(data.scores.parentExecution)
    },
    recommendation: data.recommendation,
    nextStepSuggestion: data.nextStepSuggestion
  };

  console.log('[GameReview] 复盘结果:', review);

  // 持久化到 FloorGame 记录
  try {
    floorGameStorageService.updateGame(game.id, { review });
    console.log('[GameReview] 复盘结果已保存到游戏记录');
  } catch (e) {
    console.warn('[GameReview] 保存复盘结果失败:', e);
  }

  return review;
}
