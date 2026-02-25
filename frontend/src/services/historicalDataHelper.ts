/**
 * Historical Data Helper
 * 辅助函数：收集和整理历史数据用于Agent输入
 */

import {
  HistoricalDataSummary,
  InterestDimensionType,
  BehaviorAnalysis,
} from '../types';
import { behaviorStorageService } from './behaviorStorage';

// 维度指标（用于兴趣分析 Agent）
export interface DimensionMetrics {
  dimension: InterestDimensionType;
  strength: number;      // 强度 0-100
  exploration: number;   // 探索度 0-100
}

/**
 * 收集历史数据摘要
 * 只保留 interestTrends（数值统计），其余历史数据由记忆层（graphiti）提供
 */
export const collectHistoricalData = (): HistoricalDataSummary => {
  const recentBehaviors = behaviorStorageService.getRecentBehaviors(10);
  const interestTrends = calculateInterestTrends(recentBehaviors);
  return { interestTrends };
};

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
    Visual: 50, Auditory: 50, Tactile: 50, Motor: 50,
    Construction: 50, Order: 50, Cognitive: 50, Social: 50
  };

  if (behaviors.length === 0) return trends;

  const accumulated: Record<string, { totalScore: number; totalWeight: number }> = {};
  dimensions.forEach(dim => { accumulated[dim] = { totalScore: 0, totalWeight: 0 }; });

  behaviors.forEach(behavior => {
    if (!behavior.matches || !Array.isArray(behavior.matches)) return;
    behavior.matches.forEach(match => {
      if (!match || !match.dimension) return;
      const dim = match.dimension;
      if (!accumulated[dim]) return;
      const intensity = match.intensity || 0;
      const weight = match.weight || 0;
      const score = (intensity * weight * 50) + 50;
      accumulated[dim].totalScore += score * weight;
      accumulated[dim].totalWeight += weight;
    });
  });

  dimensions.forEach(dim => {
    if (accumulated[dim].totalWeight > 0) {
      trends[dim] = accumulated[dim].totalScore / accumulated[dim].totalWeight;
    }
  });

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

  const maxExpectedExploration = 10;

  const accumulated: Record<string, {
    totalIntensityWeighted: number;
    totalWeight: number;
    explorationSum: number;
  }> = {};

  dimensions.forEach(dim => {
    accumulated[dim] = { totalIntensityWeighted: 0, totalWeight: 0, explorationSum: 0 };
  });

  behaviors.forEach(behavior => {
    if (!behavior.matches || !Array.isArray(behavior.matches)) return;
    behavior.matches.forEach(match => {
      if (!match || !match.dimension) return;
      const dim = match.dimension;
      if (!accumulated[dim]) return;
      const intensity = match.intensity || 0;
      const weight = match.weight || 0;
      accumulated[dim].totalIntensityWeighted += intensity * weight;
      accumulated[dim].totalWeight += weight;
      accumulated[dim].explorationSum += weight;
    });
  });

  return dimensions.map(dim => {
    const acc = accumulated[dim];
    let strength = 50;
    if (acc.totalWeight > 0) {
      const avgIntensity = acc.totalIntensityWeighted / acc.totalWeight;
      strength = Math.round((avgIntensity + 1) * 50);
    }
    const exploration = Math.min(100, Math.round((acc.explorationSum / maxExpectedExploration) * 100));
    return { dimension: dim, strength, exploration };
  });
};
