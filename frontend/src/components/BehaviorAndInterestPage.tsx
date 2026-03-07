/**
 * 行为与兴趣整合页面组件
 * 将雷达图和行为数据整合到一个页面中
 */

import { useState, useEffect, useMemo } from 'react';
import { Activity, TrendingUp, X, Play, Pause, RotateCcw, Info } from 'lucide-react';
import { BehaviorAnalysis, ChildProfile } from '../types';
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

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4 pb-20">
      {/* 统一标题 */}
      <div className="mb-4 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-5 text-white shadow-lg">
        <h2 className="text-xl font-bold flex items-center">
          <TrendingUp className="w-6 h-6 mr-2" />
          行为与兴趣分析
        </h2>
        <p className="text-sm text-indigo-100 mt-1">
          查看兴趣维度演变和行为记录数据
        </p>
      </div>

      {/* 浅色分隔线 */}
      <div className="border-t border-gray-200 my-4" />

      {/* 雷达图部分 */}
      {timelineData.length > 0 ? (
        <>
          {/* 图表类型选择 */}
          <div className="bg-gradient-to-br from-white to-indigo-50 rounded-xl p-4 shadow-lg border-2 border-indigo-100 mb-4">
            <label className="block text-sm font-bold text-gray-700 mb-2">
              显示类型
            </label>
            <div className="flex gap-2">
              <button
                onClick={() => setChartType('weight')}
                className={`flex-1 py-2.5 px-3 rounded-lg text-sm font-bold transition-all transform hover:scale-105 ${
                  chartType === 'weight'
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gradient-to-r hover:from-blue-50 hover:to-blue-100 border-2 border-gray-200'
                }`}
              >
                关联度
              </button>
              <button
                onClick={() => setChartType('intensity')}
                className={`flex-1 py-2.5 px-3 rounded-lg text-sm font-bold transition-all transform hover:scale-105 ${
                  chartType === 'intensity'
                    ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gradient-to-r hover:from-green-50 hover:to-green-100 border-2 border-gray-200'
                }`}
              >
                强度
              </button>
              <button
                onClick={() => setChartType('both')}
                className={`flex-1 py-2.5 px-3 rounded-lg text-sm font-bold transition-all transform hover:scale-105 ${
                  chartType === 'both'
                    ? 'bg-gradient-to-r from-purple-500 to-purple-600 text-white shadow-lg'
                    : 'bg-white text-gray-600 hover:bg-gradient-to-r hover:from-purple-50 hover:to-purple-100 border-2 border-gray-200'
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
                  background: `linear-gradient(to right, #10b981 0%, #10b981 ${(currentIndex / (timelineData.length - 1)) * 100}%, #e5e7eb ${(currentIndex / (timelineData.length - 1)) * 100}%, #e5e7eb 100%)`
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
                className="flex-1 flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-primary to-green-600 text-white rounded-lg font-bold hover:shadow-lg transform hover:scale-105 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
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

          {/* 使用说明 */}
          <div className="mb-4 bg-gray-50 rounded-xl p-4 border border-gray-200">
            <h4 className="text-sm font-bold text-gray-700 mb-2">使用说明</h4>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• 拖动时间轴滑块查看不同时间点的数据</li>
              <li>• 点击"播放"按钮自动演示数据变化过程</li>
              <li>• <span className="font-medium text-blue-600">关联度</span>：行为与该兴趣维度的关联程度累计值</li>
              <li>• <span className="font-medium text-green-600">强度</span>：孩子对该维度的喜好程度累计值（正值=喜欢，负值=讨厌）</li>
              <li>• 数值为从开始到当前时间点的所有行为记录累计</li>
            </ul>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-xl p-6 text-center shadow-sm border border-gray-100 mb-4">
          <Info className="w-12 h-12 mx-auto mb-3 text-gray-300" />
          <p className="text-gray-500 font-medium">暂无行为记录</p>
          <p className="text-sm text-gray-400 mt-1">开始记录行为后即可查看时间轴</p>
        </div>
      )}
    </div>
  );
};
