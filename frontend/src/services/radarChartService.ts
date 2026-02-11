/**
 * Radar Chart Service
 * 兴趣维度雷达图数据服务 - 时间轴版本
 */

import { 
  RadarDataPoint, 
  InterestDimensionType,
  BehaviorAnalysis 
} from '../types';
import { behaviorStorageService } from './behaviorStorage';

// 时间轴数据点
export interface TimelineDataPoint {
  date: string; // YYYY-MM-DD
  data: RadarDataPoint[]; // 8个维度的累计数据
  totalBehaviors: number; // 截止到该日期的总行为数
  summary: string; // 数据摘要
}

/**
 * 获取时间轴数据
 * 返回按日期排序的累计数据点数组
 */
export const getTimelineData = (): TimelineDataPoint[] => {
  // 获取所有行为记录
  const allBehaviors = behaviorStorageService.getAllBehaviors();
  
  if (allBehaviors.length === 0) {
    return [];
  }
  
  // 按日期分组行为记录
  const behaviorsByDate = groupBehaviorsByDate(allBehaviors);
  
  // 获取所有日期并排序
  const dates = Object.keys(behaviorsByDate).sort();
  
  // 生成时间轴数据点
  const timelineData: TimelineDataPoint[] = [];
  let cumulativeBehaviors: BehaviorAnalysis[] = [];
  
  dates.forEach(date => {
    // 累加到当前日期的所有行为
    cumulativeBehaviors = [...cumulativeBehaviors, ...behaviorsByDate[date]];
    
    // 计算累计的雷达图数据
    const radarData = calculateRadarData(cumulativeBehaviors);
    
    // 生成摘要
    const summary = generateSummary(radarData, cumulativeBehaviors.length);
    
    timelineData.push({
      date,
      data: radarData,
      totalBehaviors: cumulativeBehaviors.length,
      summary
    });
  });
  
  return timelineData;
};

/**
 * 按日期分组行为记录
 */
function groupBehaviorsByDate(behaviors: BehaviorAnalysis[]): Record<string, BehaviorAnalysis[]> {
  const grouped: Record<string, BehaviorAnalysis[]> = {};
  
  behaviors.forEach(behavior => {
    if (!behavior.timestamp) return;
    
    // 提取日期部分 YYYY-MM-DD
    const date = behavior.timestamp.split('T')[0];
    
    if (!grouped[date]) {
      grouped[date] = [];
    }
    
    grouped[date].push(behavior);
  });
  
  return grouped;
}

/**
 * 计算雷达图数据
 */
function calculateRadarData(behaviors: BehaviorAnalysis[]): RadarDataPoint[] {
  const dimensions: InterestDimensionType[] = [
    'Visual', 'Auditory', 'Tactile', 'Motor',
    'Construction', 'Order', 'Cognitive', 'Social'
  ];
  
  // 初始化每个维度的累计值
  const dimensionData: Record<InterestDimensionType, {
    weightSum: number;
    intensitySum: number;
    count: number;
  }> = {} as any;
  
  dimensions.forEach(dim => {
    dimensionData[dim] = {
      weightSum: 0,
      intensitySum: 0,
      count: 0
    };
  });
  
  // 累加每个行为的关联度和强度
  behaviors.forEach(behavior => {
    behavior.matches.forEach(match => {
      const dim = match.dimension;
      dimensionData[dim].weightSum += match.weight;
      dimensionData[dim].intensitySum += match.intensity !== undefined ? match.intensity : 0;
      dimensionData[dim].count += 1;
    });
  });
  
  // 转换为雷达图数据点
  return dimensions.map(dim => ({
    dimension: dim,
    weight: dimensionData[dim].weightSum,
    intensity: dimensionData[dim].intensitySum,
    count: dimensionData[dim].count
  }));
}

/**
 * 生成数据摘要
 */
function generateSummary(
  data: RadarDataPoint[], 
  totalBehaviors: number
): string {
  if (totalBehaviors === 0) {
    return '暂无行为记录';
  }
  
  // 找出关联度最高的维度
  const maxWeightDim = data.reduce((max, curr) => 
    curr.weight > max.weight ? curr : max
  );
  
  // 找出强度最高（最喜欢）的维度
  const maxIntensityDim = data.reduce((max, curr) => 
    curr.intensity > max.intensity ? curr : max
  );
  
  // 找出强度最低（最不喜欢）的维度
  const minIntensityDim = data.reduce((min, curr) => 
    curr.intensity < min.intensity ? curr : min
  );
  
  const dimensionNames: Record<string, string> = {
    'Visual': '视觉',
    'Auditory': '听觉',
    'Tactile': '触觉',
    'Motor': '运动',
    'Construction': '建构',
    'Order': '秩序',
    'Cognitive': '认知',
    'Social': '社交'
  };
  
  // 构建摘要
  const parts: string[] = [];
  
  if (maxWeightDim.weight > 0) {
    parts.push(`关联度最高：${dimensionNames[maxWeightDim.dimension]}（${maxWeightDim.weight.toFixed(1)}）`);
  }
  
  if (maxIntensityDim.intensity > 0) {
    parts.push(`最喜欢：${dimensionNames[maxIntensityDim.dimension]}（+${maxIntensityDim.intensity.toFixed(1)}）`);
  }
  
  if (minIntensityDim.intensity < 0) {
    parts.push(`最抗拒：${dimensionNames[minIntensityDim.dimension]}（${minIntensityDim.intensity.toFixed(1)}）`);
  }
  
  return parts.length > 0 ? parts.join('，') : '数据较为均衡';
}

/**
 * 获取维度配置（用于UI显示）
 */
export const getDimensionLabel = (dimension: InterestDimensionType): string => {
  const labels: Record<InterestDimensionType, string> = {
    'Visual': '视觉',
    'Auditory': '听觉',
    'Tactile': '触觉',
    'Motor': '运动',
    'Construction': '建构',
    'Order': '秩序',
    'Cognitive': '认知',
    'Social': '社交'
  };
  return labels[dimension];
};
