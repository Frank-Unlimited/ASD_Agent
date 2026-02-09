/**
 * Mock 数据常量
 */

import { Game, CalendarEvent, UserInterestProfile, UserAbilityProfile } from '../types';

export const MOCK_GAMES: Game[] = [
  {
    id: '1',
    title: '积木高塔轮流堆',
    target: '共同注意 (Shared Attention)',
    duration: '15 分钟',
    reason: '通过结构化的轮流互动，建立规则感和眼神接触。',
    steps: [
      { instruction: '和孩子面对面坐好，保持视线平齐。', guidance: '位置是关键！确保你能直接看到他的眼睛。' },
      { instruction: '你放一块积木，然后递给孩子一块。', guidance: '动作要慢。拿积木的时候，把积木举到你眼睛旁边。' },
      { instruction: '等待孩子看你一眼（眼神接触）再松手给他。', guidance: '数默数1-2-3，等待那个眼神接触的瞬间。' },
      { instruction: '当塔很高倒塌时，一起夸张地大笑庆祝！', guidance: '情感共鸣很重要。' }
    ]
  },
  {
    id: '2',
    title: '感官泡泡追逐战',
    target: '自我调节 (Self-Regulation)',
    duration: '10 分钟',
    reason: '帮助孩子进行情绪调节，同时增加非语言的共同参与。',
    steps: [
      { instruction: '缓慢地吹出泡泡。', guidance: '观察他的反应。' },
      { instruction: '鼓励孩子去戳破泡泡。', guidance: '如果他不敢碰，你可以先示范戳破一个。' },
      { instruction: '突然停止，做出夸张的表情等待（暂停）。', guidance: '这是"中断模式"。' },
      { instruction: '等待孩子发出信号（声音或手势）要求更多，再继续吹。', guidance: '任何信号都可以！' }
    ]
  },
  {
    id: '3',
    title: 'VR 奇幻森林绘画',
    target: '创造力 & 空间感知',
    duration: '20 分钟',
    reason: '利用沉浸式VR体验，让孩子在3D空间中自由涂鸦。',
    isVR: true,
    steps: [
      { instruction: '帮助孩子佩戴 VR 眼镜，进入"魔法森林"画室。', guidance: '刚开始可能会有不适感，先让孩子适应1-2分钟。' },
      { instruction: '选择"光之画笔"，在空中画出第一条线。', guidance: '示范动作要夸张。' },
      { instruction: '进行"接龙绘画"：你画一部分，孩子补全一部分。', guidance: '这是建立共同关注的好时机。' },
      { instruction: '保存作品并"具象化"展示。', guidance: '在虚拟空间中把画作"挂"在树上。' }
    ]
  }
];

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
