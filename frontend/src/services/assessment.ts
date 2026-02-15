/**
 * Assessment & Recommendation - 统一导出入口
 * 方便其他模块导入使用
 */

// ==================== Agents ====================
export { generateComprehensiveAssessment } from './assessmentAgent';
export { recommendGameForChild } from './gameRecommendAgent';
export { analyzeBehavior } from './behaviorAnalysisAgent';

// ==================== Storage ====================
export {
  // 评估存储
  saveAssessment,
  getAssessments,
  getLatestAssessment,
  getRecentAssessments,
  getAssessmentById,
  deleteAssessment,
  clearAssessments,
  
  // 推荐存储
  saveRecommendation,
  getRecommendations,
  getLatestRecommendation,
  getRecommendationsByAssessment,
  getRecommendationById,
  deleteRecommendation,
  clearRecommendations,
  
  // 统计
  getStorageStats
} from './assessmentStorage';

// ==================== Helpers ====================
export {
  collectHistoricalData,
  checkDataCompleteness
} from './historicalDataHelper';

// ==================== Online Search ====================
export {
  searchGamesOnline
} from './onlineSearchService';

// ==================== Examples ====================
export {
  exampleGenerateAssessment,
  exampleRecommendGame,
  exampleFullWorkflow,
  exampleCustomPreference
} from './assessmentExample';

// ==================== Tests ====================
export {
  createTestData,
  testAssessment,
  testRecommendation,
  runFullTest
} from './assessmentTest';

// ==================== Utils ====================
export { clearAllCache } from '../utils/clearCache';

// ==================== Types ====================
export type {
  ComprehensiveAssessment,
  GameRecommendation,
  ParentPreference,
  HistoricalDataSummary
} from '../types';
