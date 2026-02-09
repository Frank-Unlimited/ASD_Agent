/**
 * 工具函数
 */

import { 
  Eye, Ear, Hand, Activity, Layers, ListOrdered, 
  BrainCircuit, Users, Sparkles 
} from 'lucide-react';

/**
 * 获取兴趣维度配置
 */
export const getDimensionConfig = (dim: string) => {
  switch (dim) {
    case 'Visual': return { icon: Eye, color: 'text-purple-600 bg-purple-100', label: '视觉偏好' };
    case 'Auditory': return { icon: Ear, color: 'text-blue-600 bg-blue-100', label: '听觉敏感' };
    case 'Tactile': return { icon: Hand, color: 'text-amber-600 bg-amber-100', label: '触觉探索' };
    case 'Motor': return { icon: Activity, color: 'text-green-600 bg-green-100', label: '运动前庭' };
    case 'Construction': return { icon: Layers, color: 'text-cyan-600 bg-cyan-100', label: '建构拼搭' };
    case 'Order': return { icon: ListOrdered, color: 'text-slate-600 bg-slate-100', label: '秩序规律' };
    case 'Cognitive': return { icon: BrainCircuit, color: 'text-indigo-600 bg-indigo-100', label: '认知学习' };
    case 'Social': return { icon: Users, color: 'text-pink-600 bg-pink-100', label: '社交互动' };
    default: return { icon: Sparkles, color: 'text-gray-600 bg-gray-100', label: dim };
  }
};

/**
 * 计算年龄
 */
export const calculateAge = (birthDate: string): number => {
  const birth = new Date(birthDate);
  const today = new Date();
  let age = today.getFullYear() - birth.getFullYear();
  const monthDiff = today.getMonth() - birth.getMonth();
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
    age--;
  }
  
  return age;
};

/**
 * 格式化时间（秒转分:秒）
 */
export const formatTime = (seconds: number): string => {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s < 10 ? '0' : ''}${s}`;
};

/**
 * 获取兴趣等级（1-5）
 */
export const getInterestLevel = (score: number): 1 | 2 | 3 | 4 | 5 => {
  return Math.min(5, Math.max(1, Math.floor(score / 5) + 1)) as 1 | 2 | 3 | 4 | 5;
};
