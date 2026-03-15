# 行为与兴趣页面整合实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将行为数据页面和兴趣雷达图页面整合为一个统一的"行为与兴趣"页面，保留所有原有功能。

**Architecture:** 创建新的整合组件 `BehaviorAndInterestPage.tsx`，将雷达图部分和行为数据部分垂直堆叠在同一滚动容器中。两个部分的数据状态保持独立，雷达图的时间轴不影响行为数据列表的显示。

**Tech Stack:** React 18, TypeScript, Recharts, Tailwind CSS, Lucide Icons

---

## Task 1: 创建整合页面组件基础结构

**Files:**
- Create: `frontend/src/components/BehaviorAndInterestPage.tsx`

**Step 1: 创建组件文件和基础结构**

创建新文件 `frontend/src/components/BehaviorAndInterestPage.tsx`，包含基本的组件结构和导入语句：

```tsx
/**
 * 行为与兴趣整合页面组件
 * 将雷达图和行为数据整合到一个页面中
 */

import { useState, useEffect, useMemo } from 'react';
import { Activity, TrendingUp, X } from 'lucide-react';
import { BehaviorAnalysis, ChildProfile } from '../types';
import { behaviorStorageService } from '../services/behaviorStorage';
import { getTimelineData, getDimensionLabel } from '../services/radarChartService';
import type { RadarChartType } from '../types';
import { getDimensionConfig } from '../utils/helpers';

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

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-indigo-50 via-white to-purple-50 p-4 pb-20">
      {/* TODO: 添加页面内容 */}
      <div className="text-center py-20 text-gray-400">
        <TrendingUp className="w-16 h-16 mx-auto mb-4" />
        <p>行为与兴趣整合页面</p>
        <p className="text-xs mt-2">正在开发中...</p>
      </div>
    </div>
  );
};
```

**Step 2: 验证组件可以正常导入**

在 `frontend/src/App.tsx` 中测试导入：

```tsx
import { BehaviorAndInterestPage } from './components/BehaviorAndInterestPage';
```

运行开发服务器确保没有语法错误：

```bash
cd frontend
npm run dev
```

**Step 3: 提交基础组件**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "feat: 创建行为与兴趣整合页面基础组件"
```

---

## Task 2: 添加页面统一标题

**Files:**
- Modify: `frontend/src/components/BehaviorAndInterestPage.tsx`

**Step 1: 添加标题组件**

在组件的 return 语句中，替换 TODO 占位符为标题：

```tsx
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

    {/* TODO: 添加雷达图和行为数据部分 */}
    <div className="text-center py-20 text-gray-400">
      <Activity className="w-16 h-16 mx-auto mb-4" />
      <p>雷达图和行为数据区域</p>
      <p className="text-xs mt-2">正在开发中...</p>
    </div>
  </div>
);
```

**Step 2: 验证标题显示**

在浏览器中查看页面，确认标题正确显示。

**Step 3: 提交标题组件**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "feat: 添加页面统一标题"
```

---

## Task 3: 复制雷达图部分代码

**Files:**
- Modify: `frontend/src/components/BehaviorAndInterestPage.tsx`
- Reference: `frontend/src/components/RadarChartPage.tsx`

**Step 1: 导入雷达图相关组件**

在文件顶部添加 Recharts 相关导入：

```tsx
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

import {
  Play,
  Pause,
  RotateCcw,
  Info
} from 'lucide-react';
```

**Step 2: 添加雷达图辅助函数和组件**

在组件内部，添加以下代码（在 loadBehaviors 函数之后）：

```tsx
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
```

**Step 3: 添加雷达图 JSX**

替换 TODO 注释，添加雷达图部分的完整 JSX：

```tsx
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
```

**Step 4: 验证雷达图显示**

在浏览器中查看页面，确认雷达图部分正确显示。

**Step 5: 提交雷达图部分**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "feat: 添加雷达图部分到整合页面"
```

---

## Task 4: 添加行为数据部分

**Files:**
- Modify: `frontend/src/components/BehaviorAndInterestPage.tsx`
- Reference: `frontend/src/App.tsx` (PageBehaviors 组件)

**Step 1: 添加额外导入**

在文件顶部添加需要的图标导入：

```tsx
import { ChevronRight, Smile, Frown, Dna } from 'lucide-react';
```

**Step 2: 添加行为数据辅助变量**

在组件内部添加（在 CustomTooltip 之后）：

```tsx
const dimensions: InterestDimensionType[] = ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'];
const sources = ['全部', 'GAME', 'REPORT', 'CHAT'];
const dimensionFilters = ['全部', ...dimensions];
```

**Step 3: 添加分隔线和行为数据部分**

在雷达图部分之后添加：

```tsx
{/* 浅色分隔线 */}
<div className="border-t border-gray-200 my-4" />

{/* 行为数据部分 */}
{/* 统计卡片 */}
<div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl p-5 text-white shadow-lg mb-4">
  <div className="flex items-center justify-between mb-3">
    <h3 className="font-bold text-lg">行为数据统计</h3>
    <Activity className="w-6 h-6" />
  </div>
  <div className="grid grid-cols-3 gap-3">
    <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
      <p className="text-xs text-purple-100 mb-1">总记录数</p>
      <p className="text-2xl font-bold">{stats?.total || 0}</p>
    </div>
    <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
      <p className="text-xs text-purple-100 mb-1">游戏记录</p>
      <p className="text-2xl font-bold">{stats?.sourceCounts?.GAME || 0}</p>
    </div>
    <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
      <p className="text-xs text-purple-100 mb-1">报告记录</p>
      <p className="text-2xl font-bold">{stats?.sourceCounts?.REPORT || 0}</p>
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
    <h4 className="text-sm font-bold text-gray-700">
      行为记录 ({behaviors.length})
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
```

**Step 4: 验证行为数据显示**

在浏览器中查看页面，确认行为数据部分正确显示。

**Step 5: 提交行为数据部分**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "feat: 添加行为数据部分到整合页面"
```

---

## Task 5: 添加行为详情弹窗

**Files:**
- Modify: `frontend/src/components/BehaviorAndInterestPage.tsx`

**Step 1: 添加行为详情弹窗组件**

在组件内部，在 return 语句之前添加详情弹窗组件：

```tsx
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
```

**Step 2: 在 return 中添加弹窗渲染**

在组件 return 的最后，添加弹窗渲染：

```tsx
{/* 详情弹窗 */}
{selectedBehavior && (
  <BehaviorDetailModal
    behavior={selectedBehavior}
    onClose={() => setSelectedBehavior(null)}
  />
)}
```

**Step 3: 验证弹窗功能**

点击行为记录卡片，确认详情弹窗正确显示。

**Step 4: 提交弹窗功能**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "feat: 添加行为详情弹窗到整合页面"
```

---

## Task 6: 更新 App.tsx 导航和路由

**Files:**
- Modify: `frontend/src/App.tsx`

**Step 1: 导入新组件**

在 `frontend/src/App.tsx` 顶部添加导入：

```tsx
import { BehaviorAndInterestPage } from './components/BehaviorAndInterestPage';
```

**Step 2: 更新页面路由**

找到 Page.BEHAVIORS 和 Page.RADAR 的渲染代码，替换为：

```tsx
{currentPage === Page.BEHAVIORS && <BehaviorAndInterestPage childProfile={childProfile} />}
{currentPage === Page.RADAR && <BehaviorAndInterestPage childProfile={childProfile} />}
```

**Step 3: 更新导航菜单**

找到侧边栏导航菜单中的"行为数据"和"兴趣雷达图"按钮，替换为：

```tsx
<button onClick={() => { setPage(Page.BEHAVIORS); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium">
  <TrendingUp className="w-5 h-5 text-primary" />
  <span>行为与兴趣</span>
</button>
```

删除原有的"兴趣雷达图"菜单项。

**Step 4: 更新页面标题函数**

找到 `getHeaderTitle` 函数，更新 Page.BEHAVIORS 的标题：

```tsx
case Page.BEHAVIORS: return "行为与兴趣";
```

保持 Page.RADAR 的标题不变（用于向后兼容）。

**Step 5: 验证导航功能**

1. 点击侧边栏的"行为与兴趣"菜单项
2. 确认页面正确显示整合后的内容
3. 确认页面标题显示"行为与兴趣"

**Step 6: 提交导航更新**

```bash
git add frontend/src/App.tsx
git commit -m "feat: 更新导航菜单和路由以使用整合页面"
```

---

## Task 7: 添加类型定义导出

**Files:**
- Modify: `frontend/src/components/BehaviorAndInterestPage.tsx`

**Step 1: 添加默认导出**

在文件末尾添加：

```tsx
export default BehaviorAndInterestPage;
```

**Step 2: 验证导出**

确认组件可以正确导入和使用。

**Step 3: 提交导出更新**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "feat: 添加组件默认导出"
```

---

## Task 8: 清理和优化（可选）

**Files:**
- Modify: `frontend/src/components/BehaviorAndInterestPage.tsx`

**Step 1: 添加代码注释**

为复杂的逻辑部分添加注释，提高代码可读性。

**Step 2: 检查代码一致性**

确保所有样式、命名和代码风格与项目其他部分保持一致。

**Step 3: 提交优化**

```bash
git add frontend/src/components/BehaviorAndInterestPage.tsx
git commit -m "refactor: 优化代码注释和一致性"
```

---

## Task 9: 测试功能完整性

**Files:**
- Manual testing

**Step 1: 测试雷达图功能**

1. 打开"行为与兴趣"页面
2. 测试图表类型切换（关联度/强度/两者）
3. 测试时间轴滑块拖动
4. 测试播放/暂停/重置按钮
5. 验证雷达图正确显示数据
6. 验证 Tooltip 正确显示

**Step 2: 测试行为数据功能**

1. 测试兴趣维度筛选
2. 测试数据来源筛选
3. 测试行为记录列表显示
4. 测试点击查看详情
5. 测试删除单条记录
6. 测试清空全部记录

**Step 3: 测试页面滚动**

1. 验证页面可以整体滚动
2. 验证雷达图和行为数据在同一滚动容器中
3. 验证滚动流畅性

**Step 4: 测试响应式布局**

1. 在不同屏幕尺寸下测试
2. 验证布局在移动端正常显示

**Step 5: 记录测试结果**

如果发现问题，记录并修复。

---

## Task 10: 更新文档

**Files:**
- Create: `frontend/README.md` (如果不存在)
- Modify: `README.md` (主文档)

**Step 1: 更新前端 README**

在 `frontend/README.md` 中添加整合页面的说明：

```markdown
## 页面说明

### 行为与兴趣页面

整合了原有的行为数据和兴趣雷达图功能，提供统一的数据视图。

**功能特性：**
- 兴趣维度雷达图可视化
- 时间轴播放控制
- 行为记录筛选和查看
- 行为详情弹窗

**访问路径：** 侧边栏 > 行为与兴趣
```

**Step 2: 提交文档更新**

```bash
git add frontend/README.md README.md
git commit -m "docs: 更新页面功能说明"
```

---

## Task 11: 最终提交和代码审查

**Files:**
- Git commit

**Step 1: 查看所有更改**

```bash
git diff
```

**Step 2: 查看提交历史**

```bash
git log --oneline -10
```

**Step 3: 创建最终合并提交**

```bash
git add .
git commit -m "feat: 完成行为与兴趣页面整合

- 创建整合页面组件 BehaviorAndInterestPage
- 保留雷达图所有功能（时间轴、播放控制、图表切换）
- 保留行为数据所有功能（筛选、详情、删除）
- 统一页面标题为"行为与兴趣"
- 更新导航菜单和路由
- 添加浅色分隔线分隔两个部分
- 实现整体滚动布局

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 验收标准

### 功能完整性

- [ ] 雷达图所有功能正常工作
- [ ] 行为数据所有功能正常工作
- [ ] 页面滚动流畅
- [ ] 导航菜单正确跳转
- [ ] 详情弹窗正确显示

### 视觉一致性

- [ ] 页面标题正确显示"行为与兴趣"
- [ ] 雷达图部分约占 40-50% 高度
- [ ] 行为数据部分约占 50-60% 高度
- [ ] 分隔线浅色不突兀
- [ ] 样式与项目其他页面一致

### 数据独立性

- [ ] 雷达图时间轴不影响行为数据列表
- [ ] 行为数据始终显示所有记录
- [ ] 两个部分的状态完全独立

### 性能要求

- [ ] 页面加载时间 < 2 秒
- [ ] 滚动流畅无卡顿
- [ ] 时间轴切换响应迅速

---

## 后续优化建议

1. **性能优化**
   - 考虑使用虚拟滚动优化长列表
   - 懒加载雷达图组件

2. **功能增强**
   - 添加数据导出功能
   - 添加自定义时间范围筛选
   - 添加行为数据与雷达图的联动筛选（可选）

3. **UI/UX 改进**
   - 添加页面内快速导航（锚点跳转）
   - 优化移动端体验
   - 添加暗色模式支持

---

## 附录

### 相关文档

- 设计文档：`docs/plans/2026-03-07-behavior-interest-integration-design.md`
- 原雷达图页面：`frontend/src/components/RadarChartPage.tsx`
- 原行为数据页面：`frontend/src/App.tsx` (PageBehaviors 组件)

### 依赖���务

- `frontend/src/services/radarChartService.ts` - 雷达图数据服务
- `frontend/src/services/behaviorStorage.ts` - 行为数据存储服务
- `frontend/src/utils/helpers.ts` - 辅助函数和配置

---

**计划版本**: 1.0
**创建日期**: 2026-03-07
**预计工时**: 5-8 小时
**状态**: ✅ 准备执行
