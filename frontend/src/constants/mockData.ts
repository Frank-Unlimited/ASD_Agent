/**
 * Mock 数据常量
 */

import { CalendarEvent, UserInterestProfile, UserAbilityProfile } from '../types';

export const WEEK_DATA: CalendarEvent[] = [
  { day: 20, weekday: '周一', status: 'completed', gameTitle: '积木高塔', progress: '眼神接触 +3次' },
  { day: 21, weekday: '周二', status: 'today', time: '10:00', gameTitle: '感官泡泡' },
  { day: 22, weekday: '周三', status: 'future' },
  { day: 23, weekday: '周四', status: 'future' },
  { day: 24, weekday: '周五', status: 'future' },
  { day: 25, weekday: '周六', status: 'future' },
  { day: 26, weekday: '周日', status: 'future' },
];

export const INITIAL_TREND_DATA = [
  { name: '第1周', engagement: 30 },
  { name: '第2周', engagement: 45 },
  { name: '第3周', engagement: 60 },
  { name: '第4周', engagement: 75 },
];

export const INITIAL_INTEREST_SCORES: UserInterestProfile = { 
  Visual: 5, 
  Auditory: 2, 
  Tactile: 3, 
  Motor: 8, 
  Construction: 6, 
  Order: 1, 
  Cognitive: 4, 
  Social: 7 
};

export const INITIAL_ABILITY_SCORES: UserAbilityProfile = { 
  '自我调节': 80, 
  '亲密感': 90, 
  '双向沟通': 60, 
  '复杂沟通': 50, 
  '情绪思考': 70, 
  '逻辑思维': 40 
};
