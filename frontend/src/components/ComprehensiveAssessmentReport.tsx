/**
 * 综合评估报告完整展示（档案页面）
 */

import React from 'react';
import { 
  FileText, TrendingUp, TrendingDown, Minus, 
  Calendar, User, Activity, Brain, Heart,
  Target, Lightbulb, AlertCircle, CheckCircle,
  Download, Printer
} from 'lucide-react';
import type { ComprehensiveAssessmentReport } from '../types';

interface ComprehensiveAssessmentReportProps {
  report: ComprehensiveAssessmentReport;
  onClose?: () => void;
}

export const ComprehensiveAssessmentReportView: React.FC<ComprehensiveAssessmentReportProps> = ({
  report,
  onClose
}) => {
  // 趋势图标
  const TrendIcon = ({ trend }: { trend: 'improving' | 'stable' | 'declining' }) => {
    if (trend === 'improving') return <TrendingUp className="w-4 h-4 text-green-600" />;
    if (trend === 'declining') return <TrendingDown className="w-4 h-4 text-orange-600" />;
    return <Minus className="w-4 h-4 text-blue-600" />;
  };

  // 打印报告
  const handlePrint = () => {
    window.print();
  };

  // 导出报告
  const handleExport = () => {
    const dataStr = JSON.stringify(report, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `assessment_${report.childName}_${report.assessmentDate}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-5xl mx-auto bg-white rounded-xl shadow-lg p-8 print:shadow-none">
      {/* 报告头部 */}
      <div className="border-b-2 border-primary pb-6 mb-8">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              儿童发育综合评估报告
            </h1>
            <p className="text-gray-600">
              Comprehensive Developmental Assessment Report
            </p>
          </div>
          <div className="flex space-x-2 print:hidden">
            <button
              onClick={handlePrint}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
              title="打印报告"
            >
              <Printer className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={handleExport}
              className="p-2 hover:bg-gray-100 rounded-lg transition"
              title="导出数据"
            >
              <Download className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        </div>

        
        {/* 基本信息 */}
        <div className="mt-6 grid grid-cols-2 gap-4 text-sm">
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">儿童姓名：</span>
            <span className="font-medium">{report.childName}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Calendar className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">评估日期：</span>
            <span className="font-medium">{report.assessmentDate}</span>
          </div>
          <div className="flex items-center space-x-2">
            <FileText className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">报告周期：</span>
            <span className="font-medium">{report.reportingPeriod}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Activity className="w-4 h-4 text-gray-500" />
            <span className="text-gray-600">生成方式：</span>
            <span className="font-medium">{report.generatedBy}</span>
          </div>
        </div>
      </div>

      {/* 1. 发育史摘要 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
            <span className="text-primary font-bold">1</span>
          </div>
          发育史摘要
        </h2>
        <div className="bg-gray-50 rounded-lg p-6 space-y-4">
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">早期里程碑</h3>
            <p className="text-gray-700 leading-relaxed">
              {report.developmentalHistory.earlyMilestones}
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">语言发展</h3>
            <p className="text-gray-700 leading-relaxed">
              {report.developmentalHistory.languageDevelopment}
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">社交发展</h3>
            <p className="text-gray-700 leading-relaxed">
              {report.developmentalHistory.socialDevelopment}
            </p>
          </div>
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">运动发展</h3>
            <p className="text-gray-700 leading-relaxed">
              {report.developmentalHistory.motorDevelopment}
            </p>
          </div>
        </div>
      </section>


      {/* 2. 当前功能水平评估 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
            <span className="text-primary font-bold">2</span>
          </div>
          当前功能水平评估
        </h2>
        
        {/* 社交沟通 */}
        <div className="bg-blue-50 rounded-lg p-6 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 flex items-center">
              <Heart className="w-5 h-5 mr-2 text-blue-600" />
              社交沟通
            </h3>
            <div className="text-2xl font-bold text-blue-600">
              {report.currentFunctioning.socialCommunication.score}/100
            </div>
          </div>
          <p className="text-gray-700 mb-3">
            {report.currentFunctioning.socialCommunication.description}
          </p>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center">
                <CheckCircle className="w-4 h-4 mr-1" />
                优势
              </h4>
              <ul className="text-sm text-gray-700 space-y-1">
                {report.currentFunctioning.socialCommunication.strengths.map((s, i) => (
                  <li key={i} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold text-orange-700 mb-2 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                挑战
              </h4>
              <ul className="text-sm text-gray-700 space-y-1">
                {report.currentFunctioning.socialCommunication.challenges.map((c, i) => (
                  <li key={i} className="flex items-start">
                    <span className="mr-2">•</span>
                    <span>{c}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* 限制性行为 */}
        <div className="bg-purple-50 rounded-lg p-6 mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-purple-600" />
              限制性行为
            </h3>
            <div className="text-2xl font-bold text-purple-600">
              {report.currentFunctioning.restrictedBehaviors.score}/100
            </div>
          </div>
          <p className="text-gray-700 mb-3">
            {report.currentFunctioning.restrictedBehaviors.description}
          </p>
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">观察到的模式：</h4>
            <ul className="text-sm text-gray-700 space-y-1">
              {report.currentFunctioning.restrictedBehaviors.patterns.map((p, i) => (
                <li key={i} className="flex items-start">
                  <span className="mr-2">•</span>
                  <span>{p}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* 感觉处理 */}
        <div className="bg-green-50 rounded-lg p-6 mb-4">
          <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
            <Brain className="w-5 h-5 mr-2 text-green-600" />
            感觉处理
          </h3>
          <p className="text-gray-700 mb-3">
            {report.currentFunctioning.sensoryProfile.description}
          </p>
          <div>
            <h4 className="text-sm font-semibold text-gray-700 mb-2">感觉敏感性：</h4>
            <div className="flex flex-wrap gap-2">
              {report.currentFunctioning.sensoryProfile.sensitivities.map((s, i) => (
                <span key={i} className="px-3 py-1 bg-white rounded-full text-sm text-gray-700 border border-green-200">
                  {s}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* 认知能力 */}
        <div className="bg-yellow-50 rounded-lg p-6">
          <div className="flex items-center justify-between mb-3">
            <h3 className="font-semibold text-gray-800 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-yellow-600" />
              认知能力
            </h3>
            <div className="text-2xl font-bold text-yellow-600">
              {report.currentFunctioning.cognitiveAbilities.score}/100
            </div>
          </div>
          <p className="text-gray-700">
            {report.currentFunctioning.cognitiveAbilities.description}
          </p>
        </div>
      </section>


      {/* 3. 家庭干预记录 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
            <span className="text-primary font-bold">3</span>
          </div>
          家庭干预记录
        </h2>
        <div className="bg-gray-50 rounded-lg p-6">
          {/* 干预统计 */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-primary mb-1">
                {report.homeInterventionSummary.totalSessions}
              </div>
              <div className="text-sm text-gray-600">总游戏次数</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-3xl font-bold text-primary mb-1">
                {report.homeInterventionSummary.totalDuration}
              </div>
              <div className="text-sm text-gray-600">总时长</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center">
              <div className="text-lg font-bold text-primary mb-1">
                {report.homeInterventionSummary.interventionFrequency}
              </div>
              <div className="text-sm text-gray-600">干预频率</div>
            </div>
          </div>

          {/* 游戏活动分析 */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-800 mb-3">游戏活动分析</h3>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <h4 className="text-sm font-semibold text-green-700 mb-2">最吸引孩子</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {report.homeInterventionSummary.gameActivities.mostEngaging.map((g, i) => (
                    <li key={i}>• {g}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-orange-700 mb-2">不太感兴趣</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {report.homeInterventionSummary.gameActivities.leastEngaging.map((g, i) => (
                    <li key={i}>• {g}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-blue-700 mb-2">新出现技能</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {report.homeInterventionSummary.gameActivities.emergingSkills.map((s, i) => (
                    <li key={i}>• {s}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* 行为观察 */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-3">行为观察</h3>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-semibold text-green-700 mb-2 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-1" />
                  积极变化
                </h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {report.homeInterventionSummary.behaviorObservations.positiveChanges.map((c, i) => (
                    <li key={i}>• {c}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-orange-700 mb-2 flex items-center">
                  <AlertCircle className="w-4 h-4 mr-1" />
                  持续挑战
                </h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {report.homeInterventionSummary.behaviorObservations.persistentChallenges.map((c, i) => (
                    <li key={i}>• {c}</li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-sm font-semibold text-blue-700 mb-2">家长关注点</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  {report.homeInterventionSummary.behaviorObservations.parentConcerns.map((c, i) => (
                    <li key={i}>• {c}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>


      {/* 4. 兴趣档案分析 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
            <span className="text-primary font-bold">4</span>
          </div>
          兴趣档案分析
        </h2>
        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6">
          {/* 主导兴趣 */}
          <div className="mb-6">
            <h3 className="font-semibold text-gray-800 mb-3">主导兴趣领域</h3>
            <div className="space-y-3">
              {report.interestProfile.dominantInterests.map((interest, i) => (
                <div key={i} className="bg-white rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-800">{interest.dimension}</h4>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                          style={{ width: `${interest.intensity * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-medium text-gray-600">
                        {(interest.intensity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {interest.examples.map((ex, j) => (
                      <span key={j} className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs">
                        {ex}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 新兴兴趣和限制性模式 */}
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">新兴兴趣</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                {report.interestProfile.emergingInterests.map((i, idx) => (
                  <li key={idx}>• {i}</li>
                ))}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-800 mb-2">限制性模式</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                {report.interestProfile.restrictedPatterns.map((p, idx) => (
                  <li key={idx}>• {p}</li>
                ))}
              </ul>
            </div>
          </div>

          {/* 建议 */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-2">拓展建议</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              {report.interestProfile.recommendations.map((r, i) => (
                <li key={i}>• {r}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* 5. 能力发展轨迹 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
            <span className="text-primary font-bold">5</span>
          </div>
          能力发展轨迹
        </h2>
        <div className="grid grid-cols-2 gap-4">
          {Object.entries(report.developmentalTrajectory).map(([key, data]) => {
            const labels: Record<string, string> = {
              socialEngagement: '社交参与',
              communication: '沟通能力',
              playSkills: '游戏技能',
              emotionalRegulation: '情绪调节'
            };
            
            const change = data.current - data.baseline;
            const changePercent = ((change / data.baseline) * 100).toFixed(1);
            
            return (
              <div key={key} className="bg-white border-2 border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-gray-800">{labels[key]}</h3>
                  <TrendIcon trend={data.trend} />
                </div>
                <div className="flex items-end space-x-4 mb-3">
                  <div>
                    <div className="text-xs text-gray-500 mb-1">基线</div>
                    <div className="text-2xl font-bold text-gray-400">{data.baseline}</div>
                  </div>
                  <div className="text-2xl text-gray-300">→</div>
                  <div>
                    <div className="text-xs text-gray-500 mb-1">当前</div>
                    <div className="text-2xl font-bold text-primary">{data.current}</div>
                  </div>
                  <div className={`text-sm font-semibold ${
                    change > 0 ? 'text-green-600' : change < 0 ? 'text-orange-600' : 'text-blue-600'
                  }`}>
                    {change > 0 ? '+' : ''}{changePercent}%
                  </div>
                </div>
                <p className="text-sm text-gray-600">{data.notes}</p>
              </div>
            );
          })}
        </div>
      </section>


      {/* 6. 临床建议 */}
      <section className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <div className="w-8 h-8 bg-primary/10 rounded-lg flex items-center justify-center mr-3">
            <span className="text-primary font-bold">6</span>
          </div>
          临床建议
        </h2>
        <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-6 space-y-6">
          {/* 继续发挥的优势 */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <CheckCircle className="w-5 h-5 mr-2 text-green-600" />
              继续发挥的优势
            </h3>
            <ul className="text-sm text-gray-700 space-y-2">
              {report.clinicalRecommendations.continuedStrengths.map((s, i) => (
                <li key={i} className="flex items-start">
                  <span className="mr-2 text-green-600">✓</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 重点关注领域 */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <Target className="w-5 h-5 mr-2 text-orange-600" />
              需要重点关注的领域
            </h3>
            <ul className="text-sm text-gray-700 space-y-2">
              {report.clinicalRecommendations.targetAreas.map((a, i) => (
                <li key={i} className="flex items-start">
                  <span className="mr-2 text-orange-600">▸</span>
                  <span>{a}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 建议的干预方向 */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2 text-blue-600" />
              建议的干预方向
            </h3>
            <ul className="text-sm text-gray-700 space-y-2">
              {report.clinicalRecommendations.suggestedInterventions.map((i, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="mr-2 text-blue-600">→</span>
                  <span>{i}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 家长指导 */}
          <div>
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center">
              <Heart className="w-5 h-5 mr-2 text-purple-600" />
              给家长的指导
            </h3>
            <ul className="text-sm text-gray-700 space-y-2">
              {report.clinicalRecommendations.parentGuidance.map((g, i) => (
                <li key={i} className="flex items-start">
                  <span className="mr-2 text-purple-600">•</span>
                  <span>{g}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* 随访计划 */}
          <div className="bg-white rounded-lg p-4 border-l-4 border-primary">
            <h3 className="font-semibold text-gray-800 mb-2">随访计划</h3>
            <p className="text-sm text-gray-700">{report.clinicalRecommendations.followUpPlan}</p>
          </div>
        </div>
      </section>

      {/* 附加信息 */}
      {report.additionalNotes && (
        <section className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">附加信息</h2>
          <div className="bg-gray-50 rounded-lg p-6">
            <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
              {report.additionalNotes}
            </p>
          </div>
        </section>
      )}

      {/* 报告尾部 */}
      <div className="border-t-2 border-gray-200 pt-6 mt-8">
        <div className="text-sm text-gray-600 space-y-2">
          <p>
            <strong>报告编号：</strong>{report.reportId}
          </p>
          <p>
            <strong>生成时间：</strong>{new Date(report.createdAt).toLocaleString('zh-CN')}
          </p>
          {report.reviewedBy && (
            <p>
              <strong>审核医生：</strong>{report.reviewedBy}
            </p>
          )}
          <p className="text-xs text-gray-500 mt-4">
            本报告由AI辅助生成，基于家庭干预记录和行为观察数据。建议结合临床评估和专业医生意见综合判断。
          </p>
        </div>
      </div>
    </div>
  );
};
