/**
 * 综合评估报告卡片（聊天页面简略展示）
 */

import React from 'react';
import { FileText, TrendingUp, Calendar, ArrowRight } from 'lucide-react';
import type { ComprehensiveAssessmentReport } from '../types';

interface AssessmentReportCardProps {
  report: ComprehensiveAssessmentReport;
  onClick: () => void;
}

export const AssessmentReportCard: React.FC<AssessmentReportCardProps> = ({
  report,
  onClick
}) => {
  // 计算总体趋势
  const calculateOverallTrend = () => {
    const trends = [
      report.developmentalTrajectory.socialEngagement.trend,
      report.developmentalTrajectory.communication.trend,
      report.developmentalTrajectory.playSkills.trend,
      report.developmentalTrajectory.emotionalRegulation.trend
    ];
    
    const improvingCount = trends.filter(t => t === 'improving').length;
    const decliningCount = trends.filter(t => t === 'declining').length;
    
    if (improvingCount > decliningCount) return 'improving';
    if (decliningCount > improvingCount) return 'declining';
    return 'stable';
  };

  const overallTrend = calculateOverallTrend();
  
  const trendConfig = {
    improving: {
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      label: '整体进步',
      icon: '📈'
    },
    stable: {
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      label: '保持稳定',
      icon: '➡️'
    },
    declining: {
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      label: '需要关注',
      icon: '📉'
    }
  };

  const config = trendConfig[overallTrend];

  return (
    <div
      onClick={onClick}
      className={`mt-2 w-full max-w-[90%] ${config.bgColor} p-5 rounded-xl border-2 ${config.borderColor} shadow-md hover:shadow-lg transition-all cursor-pointer animate-in fade-in`}
    >
      {/* 标题栏 */}
      <div className="flex items-center justify-between mb-4 pb-3 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="bg-white p-2 rounded-lg shadow-sm">
            <FileText className="w-5 h-5 text-primary" />
          </div>
          <div>
            <h3 className="font-bold text-gray-800 text-base">综合评估报告</h3>
            <p className="text-xs text-gray-500">{report.childName}</p>
          </div>
        </div>
        <ArrowRight className="w-5 h-5 text-gray-400" />
      </div>

      {/* 报告信息 */}
      <div className="space-y-3 mb-4">
        {/* 日期和周期 */}
        <div className="flex items-center space-x-2 text-sm">
          <Calendar className="w-4 h-4 text-gray-500" />
          <span className="text-gray-600">
            {report.reportingPeriod} · {report.assessmentDate}
          </span>
        </div>

        {/* 整体趋势 */}
        <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${config.bgColor} border ${config.borderColor}`}>
          <TrendingUp className={`w-4 h-4 ${config.color}`} />
          <span className={`text-sm font-medium ${config.color}`}>
            {config.icon} {config.label}
          </span>
        </div>

        {/* 关键指标 */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="bg-white/70 rounded-lg p-2">
            <div className="text-gray-500 mb-1">干预次数</div>
            <div className="font-bold text-gray-800">
              {report.homeInterventionSummary.totalSessions} 次
            </div>
          </div>
          <div className="bg-white/70 rounded-lg p-2">
            <div className="text-gray-500 mb-1">主导兴趣</div>
            <div className="font-bold text-gray-800">
              {report.interestProfile.dominantInterests.length} 个
            </div>
          </div>
        </div>
      </div>

      {/* 底部提示 */}
      <div className="pt-3 border-t border-gray-200">
        <p className="text-xs text-gray-500 text-center">
          点击查看完整报告 · 可打印/导出
        </p>
      </div>
    </div>
  );
};
