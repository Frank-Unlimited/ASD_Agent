/**
 * Assessment Storage Service
 * 管理综合评估和游戏推荐的本地存储
 */

import { ComprehensiveAssessment, GameRecommendation } from '../types';

const ASSESSMENT_STORAGE_KEY = 'asd_comprehensive_assessments';
const RECOMMENDATION_STORAGE_KEY = 'asd_game_recommendations';

// ==================== 综合评估存储 ====================

/**
 * 保存综合评估
 */
export const saveAssessment = (assessment: ComprehensiveAssessment): void => {
  const existing = getAssessments();
  existing.unshift(assessment);
  // 只保留最近20条
  const toSave = existing.slice(0, 20);
  localStorage.setItem(ASSESSMENT_STORAGE_KEY, JSON.stringify(toSave));
};

/**
 * 获取所有评估
 */
export const getAssessments = (): ComprehensiveAssessment[] => {
  const data = localStorage.getItem(ASSESSMENT_STORAGE_KEY);
  return data ? JSON.parse(data) : [];
};

/**
 * 获取最新评估
 */
export const getLatestAssessment = (): ComprehensiveAssessment | null => {
  const assessments = getAssessments();
  return assessments.length > 0 ? assessments[0] : null;
};

/**
 * 获取最近N次评估
 */
export const getRecentAssessments = (count: number = 3): ComprehensiveAssessment[] => {
  return getAssessments().slice(0, count);
};

/**
 * 根据ID获取评估
 */
export const getAssessmentById = (id: string): ComprehensiveAssessment | null => {
  const assessments = getAssessments();
  return assessments.find(a => a.id === id) || null;
};

/**
 * 删除评估
 */
export const deleteAssessment = (id: string): void => {
  const existing = getAssessments();
  const filtered = existing.filter(a => a.id !== id);
  localStorage.setItem(ASSESSMENT_STORAGE_KEY, JSON.stringify(filtered));
};

/**
 * 清空所有评估
 */
export const clearAssessments = (): void => {
  localStorage.removeItem(ASSESSMENT_STORAGE_KEY);
};

// ==================== 游戏推荐存储 ====================

/**
 * 保存游戏推荐
 */
export const saveRecommendation = (recommendation: GameRecommendation): void => {
  const existing = getRecommendations();
  existing.unshift(recommendation);
  // 只保留最近50条
  const toSave = existing.slice(0, 50);
  localStorage.setItem(RECOMMENDATION_STORAGE_KEY, JSON.stringify(toSave));
};

/**
 * 获取所有推荐
 */
export const getRecommendations = (): GameRecommendation[] => {
  const data = localStorage.getItem(RECOMMENDATION_STORAGE_KEY);
  return data ? JSON.parse(data) : [];
};

/**
 * 获取最新推荐
 */
export const getLatestRecommendation = (): GameRecommendation | null => {
  const recommendations = getRecommendations();
  return recommendations.length > 0 ? recommendations[0] : null;
};

/**
 * 根据评估ID获取推荐
 */
export const getRecommendationsByAssessment = (
  assessmentId: string
): GameRecommendation[] => {
  return getRecommendations().filter(r => r.assessmentId === assessmentId);
};

/**
 * 根据ID获取推荐
 */
export const getRecommendationById = (id: string): GameRecommendation | null => {
  const recommendations = getRecommendations();
  return recommendations.find(r => r.id === id) || null;
};

/**
 * 删除推荐
 */
export const deleteRecommendation = (id: string): void => {
  const existing = getRecommendations();
  const filtered = existing.filter(r => r.id !== id);
  localStorage.setItem(RECOMMENDATION_STORAGE_KEY, JSON.stringify(filtered));
};

/**
 * 清空所有推荐
 */
export const clearRecommendations = (): void => {
  localStorage.removeItem(RECOMMENDATION_STORAGE_KEY);
};

// ==================== 统计信息 ====================

/**
 * 获取统计信息
 */
export const getStorageStats = () => {
  return {
    assessmentCount: getAssessments().length,
    recommendationCount: getRecommendations().length,
    latestAssessmentDate: getLatestAssessment()?.timestamp || null,
    latestRecommendationDate: getLatestRecommendation()?.timestamp || null
  };
};
