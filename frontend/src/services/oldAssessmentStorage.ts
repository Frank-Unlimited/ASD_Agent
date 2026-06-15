/**
 * 旧版综合评估存储服务
 * 用于存储简单的 ComprehensiveAssessment 类型
 */

import type { ComprehensiveAssessment } from '../types';

const STORAGE_KEY = 'asd_assessments';

/**
 * 保存评估
 */
export function saveAssessment(assessment: ComprehensiveAssessment): void {
  try {
    const assessments = getRecentAssessments(100);
    assessments.unshift(assessment);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(assessments));
  } catch (error) {
    console.error('Failed to save assessment:', error);
  }
}

/**
 * 获取最近的评估记录
 */
export function getRecentAssessments(count: number = 10): ComprehensiveAssessment[] {
  try {
    const data = localStorage.getItem(STORAGE_KEY);
    if (!data) return [];
    const assessments = JSON.parse(data) as ComprehensiveAssessment[];
    return assessments.slice(0, count);
  } catch (error) {
    console.error('Failed to load assessments:', error);
    return [];
  }
}

/**
 * 清空所有评估
 */
export function clearAssessments(): void {
  localStorage.removeItem(STORAGE_KEY);
}
