/**
 * Historical Data Helper
 * 辅助函数：收集和整理历史数据用于Agent输入
 */

import {
  HistoricalDataSummary,
  InterestDimensionType,
  AbilityDimensionType,
  BehaviorAnalysis,
  EvaluationResult,
} from '../types';

// 维度指标（用于兴趣分析 Agent）
export interface DimensionMetrics {
  dimension: InterestDimensionType;
  strength: number;      // 强度 0-100
  exploration: number;   // 探索度 0-100
}
import { getRecentAssessments } from './assessmentStorage';
import { reportStorageService } from './reportStorage';
import { floorGameStorageService } from './floorGameStorage';
import { behaviorStorageService } from './behaviorStorage';

/**
 * 收集历史数据摘要
 */
export const collectHistoricalData = (): HistoricalDataSummary => {
  // 获取最近的评估
  const recentAssessments = getRecentAssessments(3);

  // 获取最近的报告
  const allReports = reportStorageService.getAllReports();
  const recentReports = allReports.slice(0, 3);

  // 获取最近的行为记录（统一从 behaviorStorageService 读取）
  const recentBehaviors = behaviorStorageService.getRecentBehaviors(10);

  // 获取最近的游戏评估（从 FloorGame 记录中提取 evaluation 字段）
  const recentGames = getRecentGameEvaluationsFromFloorGames(5);

  // 计算兴趣趋势
  const interestTrends = calculateInterestTrends(recentBehaviors);

  // 计算能力趋势
  const abilityTrends = calculateAbilityTrends(recentGames);

  return {
    recentAssessments,
    recentReports,
    recentBehaviors,
    recentGames,
    interestTrends,
    abilityTrends
  };
};

/**
 * 从 FloorGame 记录中提取游戏评估
 */
function getRecentGameEvaluationsFromFloorGames(count: number): EvaluationResult[] {
  const games = floorGameStorageService.getAllGames();
  const evaluations: EvaluationResult[] = [];

  for (const game of games) {
    if (game.evaluation && (game.status === 'completed' || game.status === 'aborted')) {
      evaluations.push(game.evaluation);
      if (evaluations.length >= count) break;
    }
  }

  return evaluations;
}

/**
 * 计算兴趣趋势
 * 基于最近的行为记录，计算每个兴趣维度的加权平均分
 */
function calculateInterestTrends(
  behaviors: BehaviorAnalysis[]
): Record<InterestDimensionType, number> {
  const dimensions: InterestDimensionType[] = [
    'Visual', 'Auditory', 'Tactile', 'Motor',
    'Construction', 'Order', 'Cognitive', 'Social'
  ];

  const trends: Record<InterestDimensionType, number> = {
    Visual: 50,
    Auditory: 50,
    Tactile: 50,
    Motor: 50,
    Construction: 50,
    Order: 50,
    Cognitive: 50,
    Social: 50
  };

  if (behaviors.length === 0) {
    return trends;
  }

  // 累积每个维度的加权分数
  const accumulated: Record<string, { totalScore: number; totalWeight: number }> = {};

  dimensions.forEach(dim => {
    accumulated[dim] = { totalScore: 0, totalWeight: 0 };
  });

  behaviors.forEach(behavior => {
    behavior.matches.forEach(match => {
      const dim = match.dimension;
      // 分数 = intensity * weight * 50 + 50
      // intensity 范围 [-1, 1]，转换为 [0, 100]
      const score = (match.intensity * match.weight * 50) + 50;
      accumulated[dim].totalScore += score * match.weight;
      accumulated[dim].totalWeight += match.weight;
    });
  });

  // 计算加权平均
  dimensions.forEach(dim => {
    if (accumulated[dim].totalWeight > 0) {
      trends[dim] = accumulated[dim].totalScore / accumulated[dim].totalWeight;
    }
  });

  return trends;
}

/**
 * 计算能力趋势
 * 基于最近的游戏评估，估算每个能力维度的分数
 */
function calculateAbilityTrends(
  evaluations: EvaluationResult[]
): Record<AbilityDimensionType, number> {
  const trends: Record<AbilityDimensionType, number> = {
    '自我调节': 50,
    '亲密感': 50,
    '双向沟通': 50,
    '复杂沟通': 50,
    '情绪思考': 50,
    '逻辑思维': 50
  };

  if (evaluations.length === 0) {
    return trends;
  }

  // 简化处理：使用综合得分作为基准
  // 实际应该从游戏评估中提取具体的能力维度分数
  const avgScore = evaluations.reduce((sum, e) => sum + e.score, 0) / evaluations.length;

  // 根据反馈得分和探索得分调整不同维度
  const avgFeedback = evaluations.reduce((sum, e) => sum + e.feedbackScore, 0) / evaluations.length;
  const avgExploration = evaluations.reduce((sum, e) => sum + e.explorationScore, 0) / evaluations.length;

  trends['自我调节'] = avgScore;
  trends['亲密感'] = avgFeedback;
  trends['双向沟通'] = (avgFeedback + avgExploration) / 2;
  trends['复杂沟通'] = avgFeedback;
  trends['情绪思考'] = avgFeedback;
  trends['逻辑思维'] = avgExploration;

  return trends;
}

/**
 * 计算每个维度的强度和探索度指标
 * - 强度 = intensity × weight 的加权平均，归一化到 0-100
 * - 探索度 = 该维度所有行为记录中 weight 的累加，归一化到 0-100
 */
export const calculateDimensionMetrics = (
  behaviors: BehaviorAnalysis[]
): DimensionMetrics[] => {
  const dimensions: InterestDimensionType[] = [
    'Visual', 'Auditory', 'Tactile', 'Motor',
    'Construction', 'Order', 'Cognitive', 'Social'
  ];

  // 每个维度预期的最大探索度累计值（用于归一化）
  const maxExpectedExploration = 10; // 10条高关联行为约等于满分

  const accumulated: Record<string, {
    totalIntensityWeighted: number;
    totalWeight: number;
    explorationSum: number;
  }> = {};

  dimensions.forEach(dim => {
    accumulated[dim] = { totalIntensityWeighted: 0, totalWeight: 0, explorationSum: 0 };
  });

  behaviors.forEach(behavior => {
    behavior.matches.forEach(match => {
      const dim = match.dimension;
      if (!accumulated[dim]) return;
      // 强度：intensity × weight 的加权累计
      accumulated[dim].totalIntensityWeighted += match.intensity * match.weight;
      accumulated[dim].totalWeight += match.weight;
      // 探索度：weight 累加
      accumulated[dim].explorationSum += match.weight;
    });
  });

  return dimensions.map(dim => {
    const acc = accumulated[dim];

    // 强度：加权平均的 intensity [-1,1] 映射到 [0,100]
    let strength = 50; // 默认中性
    if (acc.totalWeight > 0) {
      const avgIntensity = acc.totalIntensityWeighted / acc.totalWeight; // [-1, 1]
      strength = Math.round((avgIntensity + 1) * 50); // [0, 100]
    }

    // 探索度：累加 weight 归一化到 [0,100]
    const exploration = Math.min(100, Math.round((acc.explorationSum / maxExpectedExploration) * 100));

    return { dimension: dim, strength, exploration };
  });
};

/**
 * 获取数据完整性检查
 */
export const checkDataCompleteness = (): {
  hasAssessments: boolean;
  hasReports: boolean;
  hasBehaviors: boolean;
  hasGames: boolean;
  isReady: boolean;
  message: string;
} => {
  const data = collectHistoricalData();

  const hasAssessments = data.recentAssessments.length > 0;
  const hasReports = data.recentReports.length > 0;
  const hasBehaviors = data.recentBehaviors.length > 0;
  const hasGames = data.recentGames.length > 0;

  const isReady = hasBehaviors || hasReports || hasGames;

  let message = '';
  if (!isReady) {
    message = '暂无足够的历史数据。请先记录一些行为、导入报告或完成游戏评估。';
  } else if (!hasBehaviors && !hasGames) {
    message = '建议记录更多行为或完成游戏评估，以获得更准确的评估结果。';
  } else {
    message = '数据充足，可以生成综合评估。';
  }

  return {
    hasAssessments,
    hasReports,
    hasBehaviors,
    hasGames,
    isReady,
    message
  };
};
