/**
 * Game Review Agent
 * 游戏复盘 Agent - 游戏结束后进行专业的 DIR/Floortime 视角复盘
 */

import { qwenStreamClient } from './qwenStreamClient';
import { GameReviewSchema } from './qwenSchemas';
import { FloorGame, GameReviewResult, ChildProfile } from '../types';
import { floorGameStorageService } from './floorGameStorage';
import { getLatestAssessment } from './assessmentStorage';
import { GAME_REVIEW_SYSTEM_PROMPT, buildGameReviewPrompt } from '../prompts/gameReviewPrompt';

/**
 * 对一次地板游戏进行复盘分析
 */
export async function reviewFloorGame(params: {
  game: FloorGame;
  chatHistory: string;
  videoSummary?: string;
  parentFeedback: string;
}): Promise<GameReviewResult> {
  const { game, chatHistory, videoSummary, parentFeedback } = params;

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

  // 读取最近评估
  const latestAssessment = getLatestAssessment();

  // 构建 prompt
  const userPrompt = buildGameReviewPrompt({
    childProfile,
    game,
    chatHistory,
    videoSummary,
    parentFeedback,
    latestAssessment
  });

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
