/**
 * 报告存储服务
 * 使用 localStorage 存储医疗报告数据
 */

import { MedicalReport } from '../types';

const REPORTS_STORAGE_KEY = 'asd_floortime_medical_reports';

class ReportStorageService {
  /**
   * 获取所有报告
   */
  getAllReports(): MedicalReport[] {
    try {
      const data = localStorage.getItem(REPORTS_STORAGE_KEY);
      return data ? JSON.parse(data) : [];
    } catch (error) {
      console.error('Failed to load reports:', error);
      return [];
    }
  }

  /**
   * 根据 ID 获取报告
   */
  getReportById(id: string): MedicalReport | null {
    const reports = this.getAllReports();
    return reports.find(r => r.id === id) || null;
  }

  /**
   * 保存报告
   */
  saveReport(report: MedicalReport): void {
    try {
      const reports = this.getAllReports();
      
      // 检查是否已存在相同 ID 的报告
      const existingIndex = reports.findIndex(r => r.id === report.id);
      
      if (existingIndex >= 0) {
        // 更新现有报告
        reports[existingIndex] = report;
      } else {
        // 添加新报告
        reports.push(report);
      }
      
      // 按创建时间倒序排列（最新的在前）
      reports.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());
      
      localStorage.setItem(REPORTS_STORAGE_KEY, JSON.stringify(reports));
    } catch (error) {
      console.error('Failed to save report:', error);
      throw new Error('保存报告失败');
    }
  }

  /**
   * 删除报告
   */
  deleteReport(id: string): void {
    try {
      const reports = this.getAllReports();
      const filtered = reports.filter(r => r.id !== id);
      localStorage.setItem(REPORTS_STORAGE_KEY, JSON.stringify(filtered));
    } catch (error) {
      console.error('Failed to delete report:', error);
      throw new Error('删除报告失败');
    }
  }

  /**
   * 获取最新报告
   */
  getLatestReport(): MedicalReport | null {
    const reports = this.getAllReports();
    return reports.length > 0 ? reports[0] : null;
  }

  /**
   * 清空所有报告
   */
  clearAllReports(): void {
    try {
      localStorage.removeItem(REPORTS_STORAGE_KEY);
    } catch (error) {
      console.error('Failed to clear reports:', error);
    }
  }

  /**
   * 生成报告 ID
   */
  generateReportId(): string {
    return `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }
}

// 导出单例
export const reportStorageService = new ReportStorageService();
