/**
 * 测试数据注入脚本
 * 用于生成跨越多个日期的行为数据，测试雷达图时间轴功能
 */

import { ChildProfile, BehaviorAnalysis, InterestDimensionType } from '../types';

/**
 * 清空所有数据
 */
export const clearAllData = () => {
  localStorage.clear();
  console.log('✅ 所有数据已清空');
};

/**
 * 生成测试用的孩子档案
 */
export const seedChildProfile = () => {
  const profile: ChildProfile = {
    name: '小明',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '轻度自闭症谱系障碍，语言发展迟缓，对视觉和建构类活动表现出较强兴趣',
    avatar: 'https://ui-avatars.com/api/?name=小明&background=10B981&color=fff&size=200',
    createdAt: new Date('2024-01-01').toISOString()
  };
  
  localStorage.setItem('asd_floortime_child_profile', JSON.stringify(profile));
  console.log('✅ 孩子档案已创建:', profile.name);
  return profile;
};

/**
 * 生成随机的行为数据
 */
const generateBehavior = (
  date: Date,
  behaviorText: string,
  dimensions: Array<{
    dimension: InterestDimensionType;
    weight: number;
    intensity: number;
    reasoning: string;
  }>,
  source: 'GAME' | 'REPORT' | 'CHAT' = 'CHAT'
): BehaviorAnalysis => {
  return {
    id: `behavior_${date.getTime()}_${Math.random().toString(36).substr(2, 9)}`,
    behavior: behaviorText,
    matches: dimensions,
    timestamp: date.toISOString(),
    source
  };
};

/**
 * 生成30天的测试数据
 * 模拟孩子兴趣的逐步发展过程
 */
export const seedBehaviorData = () => {
  const behaviors: BehaviorAnalysis[] = [];
  const today = new Date();
  
  // 第1-5天：初期探索，主要是视觉和触觉
  for (let i = 29; i >= 25; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    behaviors.push(
      generateBehavior(
        date,
        '孩子盯着旋转的风车看了很久，眼睛一直追随着转动',
        [
          { dimension: 'Visual', weight: 0.9, intensity: 0.8, reasoning: '对视觉刺激表现出强烈兴趣' },
          { dimension: 'Motor', weight: 0.3, intensity: 0.2, reasoning: '轻微的身体摇摆' }
        ],
        'CHAT'
      )
    );
    
    behaviors.push(
      generateBehavior(
        date,
        '用手反复触摸不同材质的布料，特别喜欢柔软的绒布',
        [
          { dimension: 'Tactile', weight: 0.8, intensity: 0.7, reasoning: '主动探索触觉体验' },
          { dimension: 'Cognitive', weight: 0.4, intensity: 0.3, reasoning: '在比较不同材质' }
        ],
        'CHAT'
      )
    );
  }
  
  // 第6-10天：开始出现建构兴趣
  for (let i = 24; i >= 20; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    behaviors.push(
      generateBehavior(
        date,
        '尝试把积木叠高，虽然经常倒塌但会重新尝试',
        [
          { dimension: 'Construction', weight: 0.7, intensity: 0.6, reasoning: '开始对建构活动感兴趣' },
          { dimension: 'Visual', weight: 0.5, intensity: 0.4, reasoning: '观察积木的形状和颜色' },
          { dimension: 'Motor', weight: 0.6, intensity: 0.5, reasoning: '手部精细动作练习' }
        ],
        'GAME'
      )
    );
    
    behaviors.push(
      generateBehavior(
        date,
        '听到音乐会停下来，身体随着节奏轻轻摇摆',
        [
          { dimension: 'Auditory', weight: 0.7, intensity: 0.5, reasoning: '对音乐有反应' },
          { dimension: 'Motor', weight: 0.5, intensity: 0.4, reasoning: '身体律动' }
        ],
        'CHAT'
      )
    );
  }
  
  // 第11-15天：建构兴趣增强，开始出现秩序感
  for (let i = 19; i >= 15; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    behaviors.push(
      generateBehavior(
        date,
        '能够搭建简单的积木塔，并且会按照颜色分类摆放',
        [
          { dimension: 'Construction', weight: 0.9, intensity: 0.8, reasoning: '建构能力明显提升' },
          { dimension: 'Order', weight: 0.7, intensity: 0.6, reasoning: '开始按规则分类' },
          { dimension: 'Cognitive', weight: 0.6, intensity: 0.5, reasoning: '理解分类概念' }
        ],
        'GAME'
      )
    );
    
    behaviors.push(
      generateBehavior(
        date,
        '玩具必须按照固定顺序摆放，如果顺序错了会重新排列',
        [
          { dimension: 'Order', weight: 0.9, intensity: 0.7, reasoning: '对秩序有强烈需求' },
          { dimension: 'Visual', weight: 0.4, intensity: 0.3, reasoning: '视觉检查排列' }
        ],
        'CHAT'
      )
    );
  }
  
  // 第16-20天：认知能力提升，开始简单社交互动
  for (let i = 14; i >= 10; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    behaviors.push(
      generateBehavior(
        date,
        '能够完成简单的拼图，会主动寻找正确的位置',
        [
          { dimension: 'Cognitive', weight: 0.8, intensity: 0.7, reasoning: '问题解决能力提升' },
          { dimension: 'Visual', weight: 0.7, intensity: 0.6, reasoning: '视觉匹配能力' },
          { dimension: 'Construction', weight: 0.5, intensity: 0.4, reasoning: '空间构建' }
        ],
        'GAME'
      )
    );
    
    behaviors.push(
      generateBehavior(
        date,
        '看到妈妈会主动伸手，希望被抱起来',
        [
          { dimension: 'Social', weight: 0.6, intensity: 0.5, reasoning: '开始主动寻求互动' },
          { dimension: 'Motor', weight: 0.4, intensity: 0.3, reasoning: '伸手动作' }
        ],
        'CHAT'
      )
    );
  }
  
  // 第21-25天：社交兴趣增强，运动能力提升
  for (let i = 9; i >= 5; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    behaviors.push(
      generateBehavior(
        date,
        '和其他小朋友一起玩球，会模仿别人的动作',
        [
          { dimension: 'Social', weight: 0.8, intensity: 0.7, reasoning: '主动参与群体活动' },
          { dimension: 'Motor', weight: 0.8, intensity: 0.7, reasoning: '大运动能力提升' },
          { dimension: 'Cognitive', weight: 0.5, intensity: 0.4, reasoning: '模仿学习' }
        ],
        'GAME'
      )
    );
    
    behaviors.push(
      generateBehavior(
        date,
        '喜欢跑来跑去，精力充沛，笑声增多',
        [
          { dimension: 'Motor', weight: 0.9, intensity: 0.8, reasoning: '运动成为主要兴趣' },
          { dimension: 'Social', weight: 0.4, intensity: 0.5, reasoning: '情绪表达增多' }
        ],
        'CHAT'
      )
    );
  }
  
  // 第26-30天：全面发展，各维度均衡
  for (let i = 4; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    behaviors.push(
      generateBehavior(
        date,
        '能够和家长进行简单的对话，表达自己的需求',
        [
          { dimension: 'Social', weight: 0.9, intensity: 0.8, reasoning: '社交沟通能力显著提升' },
          { dimension: 'Cognitive', weight: 0.7, intensity: 0.7, reasoning: '语言理解和表达' },
          { dimension: 'Auditory', weight: 0.6, intensity: 0.5, reasoning: '听觉处理' }
        ],
        'CHAT'
      )
    );
    
    behaviors.push(
      generateBehavior(
        date,
        '搭建了一个复杂的积木城堡，并邀请妈妈一起玩',
        [
          { dimension: 'Construction', weight: 0.9, intensity: 0.9, reasoning: '建构能力达到新高度' },
          { dimension: 'Social', weight: 0.7, intensity: 0.8, reasoning: '主动邀请互动' },
          { dimension: 'Cognitive', weight: 0.8, intensity: 0.7, reasoning: '复杂规划能力' },
          { dimension: 'Visual', weight: 0.6, intensity: 0.6, reasoning: '空间视觉' }
        ],
        'GAME'
      )
    );
    
    // 添加一些负面强度的数据，展示孩子的抗拒
    if (i % 2 === 0) {
      behaviors.push(
        generateBehavior(
          date,
          '听到突然的噪音会捂住耳朵，表现出不适',
          [
            { dimension: 'Auditory', weight: 0.8, intensity: -0.6, reasoning: '对突然的声音敏感和抗拒' }
          ],
          'CHAT'
        )
      );
    }
  }
  
  // 保存到 localStorage
  localStorage.setItem('asd_floortime_behaviors', JSON.stringify(behaviors));
  console.log(`✅ 已生成 ${behaviors.length} 条行为记录，跨越 30 天`);
  
  // 打印统计信息
  const stats = {
    总记录数: behaviors.length,
    日期范围: `${behaviors[behaviors.length - 1].timestamp?.split('T')[0]} 至 ${behaviors[0].timestamp?.split('T')[0]}`,
    来源分布: {
      CHAT: behaviors.filter(b => b.source === 'CHAT').length,
      GAME: behaviors.filter(b => b.source === 'GAME').length,
      REPORT: behaviors.filter(b => b.source === 'REPORT').length
    }
  };
  console.table(stats);
  
  return behaviors;
};

/**
 * 完整的数据初始化流程
 */
export const initializeTestData = () => {
  console.log('🚀 开始初始化测试数据...\n');
  
  // 1. 清空现有数据
  clearAllData();
  
  // 2. 创建孩子档案
  const profile = seedChildProfile();
  
  // 3. 生成行为数据
  const behaviors = seedBehaviorData();
  
  console.log('\n✨ 测试数据初始化完成！');
  console.log('📊 现在可以访问"兴趣雷达图"页面查看时间轴效果');
  console.log('💡 提示：拖动时间轴滑块或点击播放按钮查看数据变化\n');
  
  return {
    profile,
    behaviors
  };
};

// 在浏览器控制台中可用的全局函数
if (typeof window !== 'undefined') {
  (window as any).initTestData = initializeTestData;
  (window as any).clearData = clearAllData;
  (window as any).seedProfile = seedChildProfile;
  (window as any).seedBehaviors = seedBehaviorData;
  
  console.log('💡 测试数据工具已加载！');
  console.log('📝 可用命令：');
  console.log('  - initTestData()    : 清空并初始化所有测试数据');
  console.log('  - clearData()       : 清空所有数据');
  console.log('  - seedProfile()     : 仅创建孩子档案');
  console.log('  - seedBehaviors()   : 仅生成行为数据');
}
