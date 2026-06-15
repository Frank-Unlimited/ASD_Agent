/**
 * 综合评估报告存储服务
 */

import type { ComprehensiveAssessmentReport } from '../types';

const STORAGE_KEY = 'comprehensive_assessments';

export const assessmentStorage = {
  /**
   * 保存报告
   */
  save: (report: ComprehensiveAssessmentReport): void => {
    const reports = assessmentStorage.getAll();
    reports.push(report);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reports));
  },
  
  /**
   * 获取所有报告
   */
  getAll: (): ComprehensiveAssessmentReport[] => {
    try {
      const data = localStorage.getItem(STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load assessment reports:', error);
      return [];
    }
  },
  
  /**
   * 根据ID获取报告
   */
  getById: (id: string): ComprehensiveAssessmentReport | undefined => {
    return assessmentStorage.getAll().find(r => r.reportId === id);
  },
  
  /**
   * 删除报告
   */
  delete: (id: string): void => {
    const reports = assessmentStorage.getAll().filter(r => r.reportId !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(reports));
  },
  
  /**
   * 清空所有报告
   */
  clear: (): void => {
    localStorage.removeItem(STORAGE_KEY);
  }
};
