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
  MedicalReport
} from '../types';
import { getRecentAssessments } from './assessmentStorage';
import { reportStorageService } from './reportStorage';

/**
 * 收集历史数据摘要
 */
export const collectHistoricalData = (): HistoricalDataSummary => {
  // 获取最近的评估
  const recentAssessments = getRecentAssessments(3);
  
  // 获取最近的报告
  const allReports = reportStorageService.getAllReports();
  const recentReports = allReports.slice(0, 3);
  
  // 获取最近的行为记录
  const recentBehaviors = getRecentBehaviors(10);
  
  // 获取最近的游戏评估
  const recentGames = getRecentGameEvaluations(5);
  
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
 * 获取最近的行为记录
 */
function getRecentBehaviors(count: number): BehaviorAnalysis[] {
  const stored = localStorage.getItem('asd_behavior_analyses');
  if (!stored) return [];
  
  try {
    const behaviors: BehaviorAnalysis[] = JSON.parse(stored);
    return behaviors.slice(0, count);
  } catch (e) {
    console.error('Failed to parse behavior analyses:', e);
    return [];
  }
}

/**
 * 获取最近的游戏评估
 */
function getRecentGameEvaluations(count: number): EvaluationResult[] {
  const stored = localStorage.getItem('asd_game_evaluations');
  if (!stored) return [];
  
  try {
    const evaluations: EvaluationResult[] = JSON.parse(stored);
    return evaluations.slice(0, count);
  } catch (e) {
    console.error('Failed to parse game evaluations:', e);
    return [];
  }
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
 * 保存行为分析（供其他模块调用）
 */
export const saveBehaviorAnalysis = (analysis: BehaviorAnalysis): void => {
  const stored = localStorage.getItem('asd_behavior_analyses');
  let behaviors: BehaviorAnalysis[] = [];
  
  if (stored) {
    try {
      behaviors = JSON.parse(stored);
    } catch (e) {
      console.error('Failed to parse existing behaviors:', e);
    }
  }
  
  behaviors.unshift({
    ...analysis,
    timestamp: new Date().toISOString(),
    id: `behavior_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  });
  
  // 只保留最近100条
  behaviors = behaviors.slice(0, 100);
  
  localStorage.setItem('asd_behavior_analyses', JSON.stringify(behaviors));
};

/**
 * 保存游戏评估（供其他模块调用）
 */
export const saveGameEvaluation = (evaluation: EvaluationResult): void => {
  const stored = localStorage.getItem('asd_game_evaluations');
  let evaluations: EvaluationResult[] = [];
  
  if (stored) {
    try {
      evaluations = JSON.parse(stored);
    } catch (e) {
      console.error('Failed to parse existing evaluations:', e);
    }
  }
  
  evaluations.unshift(evaluation);
  
  // 只保留最近50条
  evaluations = evaluations.slice(0, 50);
  
  localStorage.setItem('asd_game_evaluations', JSON.stringify(evaluations));
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
