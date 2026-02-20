/**
 * 视频通话上下文数据收集辅助函数
 * 用于为 AI 视频通话准备完整的上下文信息
 */

import { ChildProfile, FloorGame, BehaviorAnalysis, InterestDimensionType, AbilityDimensionType } from '../types';
import { behaviorStorageService } from './behaviorStorage';
import { floorGameStorageService } from './floorGameStorage';

/**
 * 计算兴趣维度分数
 */
export function calculateInterestProfile(behaviors: BehaviorAnalysis[]): Record<InterestDimensionType, { weight: number; intensity: number }> {
  const profile: Record<InterestDimensionType, { weight: number; intensity: number }> = {
    Visual: { weight: 0, intensity: 0 },
    Auditory: { weight: 0, intensity: 0 },
    Tactile: { weight: 0, intensity: 0 },
    Motor: { weight: 0, intensity: 0 },
    Construction: { weight: 0, intensity: 0 },
    Order: { weight: 0, intensity: 0 },
    Cognitive: { weight: 0, intensity: 0 },
    Social: { weight: 0, intensity: 0 }
  };

  const counts: Record<InterestDimensionType, number> = {
    Visual: 0, Auditory: 0, Tactile: 0, Motor: 0,
    Construction: 0, Order: 0, Cognitive: 0, Social: 0
  };

  behaviors.forEach(behavior => {
    if (!behavior.matches || !Array.isArray(behavior.matches)) {
      console.warn('[calculateInterestProfile] Behavior has no matches:', behavior);
      return;
    }
    
    behavior.matches.forEach(match => {
      // 防御性检查：确保 match 对象完整
      if (!match || !match.dimension) {
        console.warn('[calculateInterestProfile] Invalid match:', match);
        return;
      }
      
      // 确保 dimension 存在于 profile 中
      if (profile[match.dimension]) {
        profile[match.dimension].weight += match.weight || 0;
        profile[match.dimension].intensity += match.intensity || 0;
        counts[match.dimension]++;
      } else {
        console.warn(`[calculateInterestProfile] Unknown dimension: ${match.dimension}`);
      }
    });
  });

  // 计算平均值
  Object.keys(profile).forEach(dim => {
    const dimension = dim as InterestDimensionType;
    if (counts[dimension] > 0) {
      profile[dimension].weight /= counts[dimension];
      profile[dimension].intensity /= counts[dimension];
    }
  });

  return profile;
}

/**
 * 计算能力维度分数（从游戏评估中提取）
 */
export function calculateAbilityScores(games: FloorGame[]): Record<AbilityDimensionType, number> {
  const scores: Record<AbilityDimensionType, number> = {
    '自我调节': 50,
    '亲密感': 50,
    '双向沟通': 50,
    '复杂沟通': 50,
    '情绪思考': 50,
    '逻辑思维': 50
  };

  // 从最近的游戏评估中提取能力分数
  // 这里简化处理，实际应该有更复杂的逻辑
  const completedGames = games.filter(g => g.status === 'completed' && g.evaluation);
  
  if (completedGames.length > 0) {
    // 使用最近游戏的评估分数作为基准
    const recentScore = completedGames[0].evaluation?.score || 50;
    Object.keys(scores).forEach(key => {
      scores[key as AbilityDimensionType] = recentScore;
    });
  }

  return scores;
}

/**
 * 提取成功策略
 */
export function extractSuccessfulStrategies(games: FloorGame[]): string[] {
  const strategies: string[] = [];
  
  games
    .filter(g => g.status === 'completed' && g.evaluation && g.evaluation.score >= 70)
    .forEach(game => {
      if (game.evaluation?.suggestion) {
        strategies.push(`${game.gameTitle}: ${game.evaluation.suggestion}`);
      }
    });

  return strategies.slice(0, 5); // 最多返回5条
}

/**
 * 识别挑战领域
 */
export function identifyChallenges(games: FloorGame[]): string[] {
  const challenges: string[] = [];
  
  games
    .filter(g => g.status === 'completed' && g.evaluation && g.evaluation.score < 60)
    .forEach(game => {
      if (game.evaluation?.summary) {
        challenges.push(`${game.gameTitle}: ${game.evaluation.summary}`);
      }
    });

  return challenges.slice(0, 5); // 最多返回5条
}

/**
 * 格式化最近行为为简短描述
 */
export function formatRecentBehaviors(behaviors: BehaviorAnalysis[]): string[] {
  return behaviors.map(b => {
    const topMatch = b.matches.sort((a, b) => b.weight - a.weight)[0];
    const sentiment = topMatch.intensity > 0 ? '喜欢' : topMatch.intensity < 0 ? '不喜欢' : '中性';
    return `${b.behavior} (${topMatch.dimension}, ${sentiment})`;
  });
}

/**
 * 收集完整的视频通话上下文
 */
export async function collectVideoCallContext(
  childProfile: ChildProfile | null,
  gameData: FloorGame | null
): Promise<{
  childInfo: {
    name: string;
    age: number;
    diagnosis: string;
    currentAbilities: Record<AbilityDimensionType, number>;
    interestProfile: Record<InterestDimensionType, { weight: number; intensity: number }>;
    recentBehaviors: string[];
  };
  gameInfo: {
    title: string;
    goal: string;
    summary: string;
    steps: Array<{
      stepTitle: string;
      instruction: string;
      expectedOutcome: string;
    }>;
    materials: string[];
    currentStep: number;
  };
  historyInfo: {
    recentGames: Array<{
      title: string;
      result: string;
      evaluation: {
        score: number;
        summary: string;
      };
    }>;
    successfulStrategies: string[];
    challengingAreas: string[];
  };
}> {
  // 获取最近的行为记录
  const recentBehaviors = behaviorStorageService.getRecentBehaviors(10);
  
  // 获取最近的游戏记录
  const recentGames = floorGameStorageService.getRecentGames(5);
  
  // 计算兴趣和能力分数
  const interestProfile = calculateInterestProfile(recentBehaviors);
  const abilityScores = calculateAbilityScores(recentGames);
  
  // 提取成功策略和挑战
  const successfulStrategies = extractSuccessfulStrategies(recentGames);
  const challengingAreas = identifyChallenges(recentGames);
  
  // 格式化行为描述
  const behaviorDescriptions = formatRecentBehaviors(recentBehaviors);
  
  // 计算年龄
  let age = 0;
  if (childProfile?.birthDate) {
    const birthDate = new Date(childProfile.birthDate);
    const today = new Date();
    age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
  }
  
  return {
    childInfo: {
      name: childProfile?.name || '孩子',
      age,
      diagnosis: childProfile?.diagnosis || '暂无诊断信息',
      currentAbilities: abilityScores,
      interestProfile,
      recentBehaviors: behaviorDescriptions
    },
    gameInfo: {
      title: gameData?.gameTitle || '自由游戏',
      goal: gameData?.goal || '观察孩子的行为和互动',
      summary: gameData?.summary || '通过视频观察孩子的兴趣点和互动方式',
      steps: gameData?.steps || [],
      materials: gameData?.materials || [],
      currentStep: 0
    },
    historyInfo: {
      recentGames: recentGames
        .filter(g => g.status === 'completed')
        .map(g => ({
          title: g.gameTitle,
          result: g.status,
          evaluation: {
            score: g.evaluation?.score || 0,
            summary: g.evaluation?.summary || ''
          }
        })),
      successfulStrategies,
      challengingAreas
    }
  };
}
