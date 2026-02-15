/**
 * Behavior Analysis Agent Test
 * 测试行为分析Agent
 */

import { analyzeBehavior } from './behaviorAnalysisAgent';
import { ChildProfile } from '../types';

/**
 * 测试行为分析Agent
 */
export const testBehaviorAnalysis = async () => {
  console.log('========== 行为分析Agent测试 ==========\n');
  
  // 创建测试用的孩子档案
  const testChild: ChildProfile = {
    name: '小明',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍，语言发展迟缓',
    avatar: '',
    createdAt: new Date().toISOString()
  };
  
  // 测试案例1：玩积木
  console.log('测试案例1：玩积木');
  console.log('行为描述：孩子正在玩积木，很专注地搭建高塔，看起来很兴奋，不愿意停下来\n');
  
  try {
    const result1 = await analyzeBehavior(
      '孩子正在玩积木，很专注地搭建高塔，看起来很兴奋，不愿意停下来',
      testChild
    );
    
    console.log('分析结果：');
    console.log('- 行为：', result1.behavior);
    console.log('- 兴趣维度：');
    result1.matches.forEach(match => {
      console.log(`  * ${match.dimension}:`);
      console.log(`    - 关联度: ${match.weight.toFixed(2)}`);
      console.log(`    - 强度: ${match.intensity > 0 ? '+' : ''}${match.intensity.toFixed(2)}`);
      console.log(`    - 推理: ${match.reasoning}`);
    });
    console.log('\n');
  } catch (error) {
    console.error('测试失败:', error);
  }
  
  // 测试案例2：盯着旋转物体
  console.log('测试案例2：盯着旋转物体');
  console.log('行为描述：他现在一直盯着旋转的风扇，眼睛都不眨，叫他也不理\n');
  
  try {
    const result2 = await analyzeBehavior(
      '他现在一直盯着旋转的风扇，眼睛都不眨，叫他也不理',
      testChild
    );
    
    console.log('分析结果：');
    console.log('- 行为：', result2.behavior);
    console.log('- 兴趣维度：');
    result2.matches.forEach(match => {
      console.log(`  * ${match.dimension}:`);
      console.log(`    - 关联度: ${match.weight.toFixed(2)}`);
      console.log(`    - 强度: ${match.intensity > 0 ? '+' : ''}${match.intensity.toFixed(2)}`);
      console.log(`    - 推理: ${match.reasoning}`);
    });
    console.log('\n');
  } catch (error) {
    console.error('测试失败:', error);
  }
  
  // 测试案例3：排列玩具（抗拒被打断）
  console.log('测试案例3：排列玩具（抗拒被打断）');
  console.log('行为描述：她刚才在排列玩具，把所有小汽车排成一排，我想帮她调整一下，她就哭了\n');
  
  try {
    const result3 = await analyzeBehavior(
      '她刚才在排列玩具，把所有小汽车排成一排，我想帮她调整一下，她就哭了',
      testChild
    );
    
    console.log('分析结果：');
    console.log('- 行为：', result3.behavior);
    console.log('- 兴趣维度：');
    result3.matches.forEach(match => {
      console.log(`  * ${match.dimension}:`);
      console.log(`    - 关联度: ${match.weight.toFixed(2)}`);
      console.log(`    - 强度: ${match.intensity > 0 ? '+' : ''}${match.intensity.toFixed(2)}`);
      console.log(`    - 推理: ${match.reasoning}`);
    });
    console.log('\n');
  } catch (error) {
    console.error('测试失败:', error);
  }
  
  console.log('========== 测试完成 ==========');
};

// 如果直接运行此文件，执行测试
if (import.meta.url === `file://${process.argv[1]}`) {
  testBehaviorAnalysis();
}
