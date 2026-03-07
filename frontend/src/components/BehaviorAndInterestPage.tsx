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
