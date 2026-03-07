/**
 * 行为与兴趣整合页面组件
 * 将雷达图和行为数据整合到一个页面中
 */

import { useState, useEffect, useMemo } from 'react';
import { Activity, TrendingUp, X, Play, Pause, RotateCcw, Info, ChevronRight, Smile, Frown, Dna, Sprout, HelpCircle, Gamepad2, FileText } from 'lucide-react';
import { BehaviorAnalysis, ChildProfile, InterestDimensionType } from '../types';
import { behaviorStorageService } from '../services/behaviorStorage';
import { getTimelineData, getDimensionLabel } from '../services/radarChartService';
import type { RadarChartType } from '../types';
import { getDimensionConfig } from '../utils/helpers';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  Legend,
  Tooltip
} from 'recharts';

interface BehaviorAndInterestPageProps {
  childProfile: ChildProfile | null;
}

export const BehaviorAndInterestPage: React.FC<BehaviorAndInterestPageProps> = ({
  childProfile
}) => {
  // ===== 雷达图相关状态 =====
  const [chartType, setChartType] = useState<RadarChartType>('both');
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // ===== 行为数据相关状态 =====
  const [behaviors, setBehaviors] = useState<BehaviorAnalysis[]>([]);
  const [filterDimension, setFilterDimension] = useState<string>('全部');
  const [filterSource, setFilterSource] = useState<string>('全部');
  const [stats, setStats] = useState<any>(null);
  const [selectedBehavior, setSelectedBehavior] = useState<BehaviorAnalysis | null>(null);
  const [showHelpModal, setShowHelpModal] = useState(false);

  // ===== 数据获取 =====
  const timelineData = useMemo(() => getTimelineData(), []);

  // 初始化时设置当前索引为最新数据
  useEffect(() => {
    if (timelineData.length > 0) {
      setCurrentIndex(timelineData.length - 1);
    }
  }, [timelineData]);

  // 加载行为数据
  useEffect(() => {
    loadBehaviors();
  }, [filterDimension, filterSource]);

  // 自动播放雷达图时间轴
  useEffect(() => {
    if (!isPlaying || timelineData.length === 0) return;

    const interval = setInterval(() => {
      setCurrentIndex(prev => {
        if (prev >= timelineData.length - 1) {
          setIsPlaying(false);
          return prev;
        }
        return prev + 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isPlaying, timelineData.length]);

  const loadBehaviors = () => {
    let allBehaviors = behaviorStorageService.getAllBehaviors();

    // 按维度筛选
    if (filterDimension !== '全部') {
      allBehaviors = allBehaviors.filter(b =>
        b.matches.some(m => m.dimension === filterDimension)
      );
    }

    // 按来源筛选
    if (filterSource !== '全部') {
      allBehaviors = allBehaviors.filter(b => b.source === filterSource);
    }

    setBehaviors(allBehaviors);
    setStats(behaviorStorageService.getStatistics());
  };

  const handleDeleteBehavior = (id: string) => {
    if (confirm('确定要删除这条行为记录吗？')) {
      behaviorStorageService.deleteBehavior(id);
      loadBehaviors();
    }
  };

  // 处理拖动条变化
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(e.target.value);
    setCurrentIndex(value);
    setIsPlaying(false); // 手动拖动时停止自动播放
  };

  // 播放/暂停
  const togglePlay = () => {
    if (currentIndex >= timelineData.length - 1) {
      setCurrentIndex(0); // 如果已经到最后，从头开始
    }
    setIsPlaying(!isPlaying);
  };

  // 重置到开始
  const handleReset = () => {
    setCurrentIndex(0);
    setIsPlaying(false);
  };

  // 当前时间点的数据
  const currentData = timelineData[currentIndex] || {
    date: '',
    data: [],
    totalBehaviors: 0,
    summary: '暂无数据'
  };

  // 转换数据格式供 Recharts 使用
  const chartData = currentData.data.map(point => ({
    dimension: getDimensionLabel(point.dimension),
    关联度: point.weight,
    强度: point.intensity,
    count: point.count
  }));

  // 自定义 Tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-bold text-gray-800 mb-2">{payload[0].payload.dimension}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value.toFixed(2)}
            </p>
          ))}
          <p className="text-xs text-gray-500 mt-1">
            记录数: {payload[0].payload.count}
          </p>
        </div>
      );
    }
    return null;
  };

  const dimensions: InterestDimensionType[] = ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'];
  const sources = ['全部', 'GAME', 'REPORT', 'CHAT'];
  const dimensionFilters = ['全部', ...dimensions];

  // 行为详情弹窗
  const BehaviorDetailModal = ({ behavior, onClose }: { behavior: BehaviorAnalysis, onClose: () => void }) => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between rounded-t-2xl">
          <h3 className="font-bold text-gray-800">行为详情</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* 行为描述 */}
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <h5 className="text-sm font-bold text-blue-700 mb-2 flex items-center">
              <Activity className="w-4 h-4 mr-2" />
              行为描述
            </h5>
            <p className="text-sm text-gray-800 leading-relaxed">{behavior.behavior}</p>
          </div>

          {/* 兴趣关联 */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-200">
            <h5 className="text-sm font-bold text-green-700 mb-3 flex items-center">
              <Dna className="w-4 h-4 mr-2" />
              兴趣维度分析
            </h5>
            <div className="space-y-3">
              {behavior.matches.map((match, idx) => {
                const config = getDimensionConfig(match.dimension);
                const weightPercentage = (match.weight * 100).toFixed(0);
                const intensity = match.intensity !== undefined ? match.intensity : 0;
                const intensityPercentage = Math.abs(intensity * 100);
                const isPositive = intensity >= 0;

                return (
                  <div key={idx} className="bg-white rounded-lg p-3 border border-gray-100">
                    <div className="flex items-center justify-between mb-2">
                      <div className={`flex items-center px-2 py-1 rounded-md text-xs font-bold ${config.color}`}>
                        <config.icon className="w-3 h-3 mr-1" />
                        {config.label}
                      </div>
                    </div>

                    {/* 关联度 */}
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-600 font-medium">关联度</span>
                        <span className="text-sm font-bold text-gray-800">{weightPercentage}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${config.color.split(' ')[0].replace('text', 'bg')} transition-all duration-500`}
                          style={{ width: `${weightPercentage}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* 强度 */}
                    <div className="mb-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-600 font-medium">喜好强度</span>
                        <div className="flex items-center">
                          {isPositive ? (
                            <Smile className="w-3 h-3 text-green-600 mr-1" />
                          ) : (
                            <Frown className="w-3 h-3 text-red-600 mr-1" />
                          )}
                          <span className={`text-sm font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            {isPositive ? '+' : ''}{(intensity * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden relative">
                        {/* 中心线 */}
                        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300"></div>
                        {/* 强度条 */}
                        {isPositive ? (
                          <div
                            className="h-full bg-green-500 transition-all duration-500 absolute left-1/2"
                            style={{ width: `${intensityPercentage / 2}%` }}
                          ></div>
                        ) : (
                          <div
                            className="h-full bg-red-500 transition-all duration-500 absolute right-1/2"
                            style={{ width: `${intensityPercentage / 2}%` }}
                          ></div>
                        )}
                      </div>
                      <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                        <span>讨厌</span>
                        <span>中性</span>
                        <span>喜欢</span>
                      </div>
                    </div>

                    {match.reasoning && (
                      <p className="text-xs text-gray-500 mt-2 italic border-t border-gray-200 pt-2">💡 {match.reasoning}</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 元数据 */}
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-gray-500">记录时间：</span>
                <span className="font-medium text-gray-700 block mt-1">
                  {behavior.timestamp ? new Date(behavior.timestamp).toLocaleString('zh-CN') : '未知'}
                </span>
              </div>
              <div>
                <span className="text-gray-500">数据来源：</span>
                <span className="font-medium text-gray-700 block mt-1">
                  {behavior.source === 'GAME' ? '游戏互动' :
                    behavior.source === 'REPORT' ? '报告分析' :
                      behavior.source === 'CHAT' ? 'AI对话' : '未知'}
                </span>
              </div>
            </div>
          </div>

          {/* 删除按钮 */}
          <button
            onClick={() => {
              if (behavior.id) {
                handleDeleteBehavior(behavior.id);
                onClose();
              }
            }}
            className="w-full bg-red-50 text-red-600 py-3 rounded-xl font-bold hover:bg-red-100 transition flex items-center justify-center"
          >
            <X className="w-4 h-4 mr-2" />
            删除此记录
          </button>
        </div>
      </div>
    </div>
  );

  // 使用说明弹窗
  const HelpModal = () => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setShowHelpModal(false)}>
      <div className="bg-white rounded-2xl max-w-md w-full p-6" onClick={(e) => e.stopPropagation()}>
        <h3 className="font-bold text-gray-800 mb-4">雷达图使用说明</h3>
        <ul className="space-y-3 text-sm text-gray-600">
          <li className="flex items-start">
            <span className="text-emerald-500 mr-2">•</span>
            <span>拖动时间轴滑块查看不同时间点的数据</span>
          </li>
          <li className="flex items-start">
            <span className="text-emerald-500 mr-2">•</span>
            <span>点击"播放"按钮自动演示数据变化过程</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-500 mr-2">•</span>
            <span><strong>关联度</strong>：行为与该兴趣维度的关联程度累计值</span>
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">•</span>
            <span><strong>强度</strong>：孩子对该维度的喜好程度累计值（正值=喜欢，负值=讨厌）</span>
          </li>
          <li className="flex items-start">
            <span className="text-gray-400 mr-2">•</span>
            <span className="text-gray-500">数值为从开始到当前时间点的所有行为记录累计</span>
          </li>
        </ul>
        <button
          onClick={() => setShowHelpModal(false)}
          className="w-full mt-6 py-2.5 bg-emerald-500 text-white rounded-lg font-medium hover:bg-emerald-600 transition"
        >
          知道了
        </button>
      </div>
    </div>
  );

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-emerald-50 via-white to-teal-50 p-4 pb-20">
      {/* 主标题卡片 */}
      <div className="mb-4 bg-white rounded-xl p-5 shadow-sm border-l-4 border-emerald-500">
        <h2 className="text-xl font-bold text-gray-800 flex items-center">
          <Sprout className="w-6 h-6 mr-2 text-emerald-500" />
          成长足迹
        </h2>
        <p className="text-sm text-gray-500 mt-1">
          记录孩子的兴趣发现和成长点滴
        </p>
      </div>

      {/* 浅色分隔线 */}
      <div className="border-t border-gray-200 my-4" />

      {/* 雷达图部分 */}
      {timelineData.length > 0 ? (
        <>
          {/* 雷达图标题和切换按钮 */}
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-700">兴趣演变趋势</h3>
            <div className="flex gap-2">
              <button
                onClick={() => setChartType('weight')}
                className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                  chartType === 'weight'
                    ? 'bg-emerald-500 text-white shadow-md'
                    : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                }`}
              >
                关联度
              </button>
              <button
                onClick={() => setChartType('intensity')}
                className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                  chartType === 'intensity'
                    ? 'bg-emerald-500 text-white shadow-md'
                    : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                }`}
              >
                强度
              </button>
              <button
                onClick={() => setChartType('both')}
                className={`px-3 py-1.5 text-xs rounded-lg font-medium transition-all ${
                  chartType === 'both'
                    ? 'bg-emerald-500 text-white shadow-md'
                    : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                }`}
              >
                两者
              </button>
            </div>
          </div>

          {/* 时间轴控制 */}
          <div className="bg-gradient-to-br from-white to-purple-50 rounded-xl p-4 shadow-lg border-2 border-purple-100 mb-4">
            {/* 当前日期和数据摘要 */}
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <div>
                  <p className="text-lg font-bold text-gray-800">{currentData.date}</p>
                  <p className="text-xs text-gray-500">
                    累计 {currentData.totalBehaviors} 条行为记录
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">
                    {currentIndex + 1} / {timelineData.length}
                  </p>
                </div>
              </div>

              {/* 数据摘要 */}
              <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-blue-100">
                <div className="flex items-start">
                  <Info className="w-4 h-4 text-blue-600 mr-2 flex-shrink-0 mt-0.5" />
                  <p className="text-xs text-gray-700">{currentData.summary}</p>
                </div>
              </div>
            </div>

            {/* 时间轴滑块 */}
            <div className="mb-4">
              <input
                type="range"
                min="0"
                max={timelineData.length - 1}
                value={currentIndex}
                onChange={handleSliderChange}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                style={{
                  background: `linear-gradient(to right, #10b981 0%, #10b981 ${(currentIndex / (timelineData.length - 1)) * 100}%, #d1d5db ${(currentIndex / (timelineData.length - 1)) * 100}%, #d1d5db 100%)`
                }}
              />

              {/* 时间刻度 */}
              <div className="flex justify-between mt-2 text-xs text-gray-400">
                <span>{timelineData[0]?.date || ''}</span>
                <span>{timelineData[timelineData.length - 1]?.date || ''}</span>
              </div>
            </div>

            {/* 播放控制按钮 */}
            <div className="flex gap-2">
              <button
                onClick={handleReset}
                disabled={currentIndex === 0}
                className="flex items-center justify-center px-4 py-2.5 bg-white border-2 border-gray-200 text-gray-700 rounded-lg font-bold hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 hover:border-gray-300 transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <RotateCcw className="w-4 h-4 mr-1" />
                重置
              </button>
              <button
                onClick={togglePlay}
                disabled={timelineData.length <= 1}
                className="flex-1 flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-lg font-bold hover:shadow-lg transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isPlaying ? (
                  <>
                    <Pause className="w-4 h-4 mr-1" />
                    暂停
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-1" />
                    {currentIndex >= timelineData.length - 1 ? '从头播放' : '播放'}
                  </>
                )}
              </button>
            </div>
          </div>

          {/* 雷达图 */}
          {currentData.totalBehaviors > 0 ? (
            <div className="bg-gradient-to-br from-white to-indigo-50 rounded-xl p-4 shadow-lg border-2 border-indigo-100 mb-4">
              <ResponsiveContainer width="100%" height={400}>
                <RadarChart data={chartData}>
                  <PolarGrid stroke="#e5e7eb" />
                  <PolarAngleAxis
                    dataKey="dimension"
                    tick={{ fill: '#6b7280', fontSize: 12 }}
                  />
                  <PolarRadiusAxis
                    angle={90}
                    domain={[0, 'auto']}
                    tick={{ fill: '#9ca3af', fontSize: 10 }}
                  />

                  {(chartType === 'weight' || chartType === 'both') && (
                    <Radar
                      name="关联度"
                      dataKey="关联度"
                      stroke="#3b82f6"
                      fill="#3b82f6"
                      fillOpacity={0.3}
                      strokeWidth={2}
                      animationDuration={300}
                    />
                  )}

                  {(chartType === 'intensity' || chartType === 'both') && (
                    <Radar
                      name="强度"
                      dataKey="强度"
                      stroke="#10b981"
                      fill="#10b981"
                      fillOpacity={0.3}
                      strokeWidth={2}
                      animationDuration={300}
                    />
                  )}

                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="circle"
                  />
                  <Tooltip content={<CustomTooltip />} />
                </RadarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="bg-white rounded-xl p-12 text-center shadow-sm border border-gray-100 mb-4">
              <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <p className="text-gray-500 font-medium">该时间点暂无数据</p>
              <p className="text-sm text-gray-400 mt-2">拖动时间轴查看其他时间点</p>
            </div>
          )}

          {/* 使用说明提示条 */}
          <div
            onClick={() => setShowHelpModal(true)}
            className="flex items-center justify-center p-3 bg-blue-50 rounded-lg cursor-pointer hover:bg-blue-100 transition mb-4"
          >
            <HelpCircle className="w-4 h-4 text-blue-600 mr-2" />
            <span className="text-sm text-blue-700 font-medium">如何查看使用说明</span>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-xl p-6 text-center shadow-sm border border-gray-100 mb-4">
          <Info className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500 font-medium">暂无行为记录</p>
          <p className="text-sm text-gray-400 mt-1">开始记录行为后即可查看时间轴</p>
        </div>
      )}

      {/* 浅色分隔线 */}
      <div className="border-t border-gray-200 my-4" />

      {/* 行为数据部分 */}
      {/* 统计数据条 */}
      <div className="bg-emerald-50 rounded-xl p-4 mb-4">
        <div className="flex items-center justify-around">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-600" />
            <div>
              <p className="text-xs text-gray-500">总记录</p>
              <p className="text-lg font-bold text-emerald-700">{stats?.total || 0}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Gamepad2 className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-xs text-gray-500">游戏</p>
              <p className="text-lg font-bold text-blue-700">{stats?.sourceCounts?.GAME || 0}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <FileText className="w-5 h-5 text-purple-600" />
            <div>
              <p className="text-xs text-gray-500">报告</p>
              <p className="text-lg font-bold text-purple-700">{stats?.sourceCounts?.REPORT || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100 mb-4">
        <h4 className="text-sm font-bold text-gray-700 mb-3">筛选条件</h4>

        {/* 按兴趣维度筛选 */}
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-2">兴趣维度</p>
          <div className="flex flex-wrap gap-2">
            {dimensionFilters.map(dim => (
              <button
                key={dim}
                onClick={() => setFilterDimension(dim)}
                className={`text-xs px-3 py-2 rounded-full font-bold transition-all transform hover:scale-105 ${
                  filterDimension === dim
                    ? 'bg-gradient-to-r from-primary to-teal-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 border-2 border-gray-200'
                }`}
              >
                {dim === '全部' ? dim : getDimensionConfig(dim as InterestDimensionType).label}
              </button>
            ))}
          </div>
        </div>

        {/* 按来源筛选 */}
        <div>
          <p className="text-xs text-gray-500 mb-2">数据来源</p>
          <div className="flex gap-2">
            {sources.map(source => (
              <button
                key={source}
                onClick={() => setFilterSource(source)}
                className={`text-xs px-3 py-2 rounded-full font-bold transition-all transform hover:scale-105 ${
                  filterSource === source
                    ? 'bg-gradient-to-r from-secondary to-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gradient-to-r hover:from-gray-50 hover:to-gray-100 border-2 border-gray-200'
                }`}
              >
                {source === '全部' ? '全部' :
                  source === 'GAME' ? '游戏' :
                    source === 'REPORT' ? '报告' : '对话'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 行为列表 */}
      <div className="space-y-3 pb-4">
        <div className="flex items-center justify-between">
          <h4 className="text-lg font-semibold text-gray-700">
            观察记录 ({behaviors.length})
          </h4>
          {behaviors.length > 0 && (
            <button
              onClick={() => {
                if (confirm('确定要清空所有行为记录吗？此操作不可恢复！')) {
                  behaviorStorageService.clearAllBehaviors();
                  loadBehaviors();
                }
              }}
              className="text-xs text-red-500 hover:text-red-700 font-medium"
            >
              清空全部
            </button>
          )}
        </div>

        {behaviors.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <Activity className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p>暂无行为记录</p>
            <p className="text-xs mt-2">完成游戏或导入报告后会自动记录</p>
          </div>
        ) : (
          behaviors.map((behavior) => (
            <div
              key={behavior.id}
              onClick={() => setSelectedBehavior(behavior)}
              className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 cursor-pointer hover:border-primary/30 transition"
            >
              <div className="flex items-start justify-between mb-2">
                <p className="text-sm font-bold text-gray-800 flex-1 line-clamp-2">
                  {behavior.behavior}
                </p>
                <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" />
              </div>

              {/* 兴趣标签 */}
              <div className="flex flex-wrap gap-1.5 mb-2">
                {behavior.matches.slice(0, 3).map((match, idx) => {
                  const config = getDimensionConfig(match.dimension);
                  return (
                    <div key={idx} className={`flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold ${config.color}`}>
                      <config.icon className="w-3 h-3 mr-1" />
                      {config.label} {(match.weight * 100).toFixed(0)}%
                    </div>
                  );
                })}
                {behavior.matches.length > 3 && (
                  <span className="text-[10px] text-gray-400 px-2 py-0.5">
                    +{behavior.matches.length - 3}
                  </span>
                )}
              </div>

              {/* 元信息 */}
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>
                  {behavior.source === 'GAME' ? '🎮 游戏' :
                    behavior.source === 'REPORT' ? '📄 报告' :
                      behavior.source === 'CHAT' ? '💬 对话' : '❓'}
                </span>
                <span>
                  {behavior.timestamp ? new Date(behavior.timestamp).toLocaleDateString('zh-CN') : ''}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 详情弹窗 */}
      {selectedBehavior && (
        <BehaviorDetailModal
          behavior={selectedBehavior}
          onClose={() => setSelectedBehavior(null)}
        />
      )}

      {/* 使用说明弹窗 */}
      {showHelpModal && <HelpModal />}
    </div>
  );
};

export default BehaviorAndInterestPage;
