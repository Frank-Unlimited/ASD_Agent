/**
 * Assessment & Recommendation Test
 * 用于测试综合评估和游戏推荐功能
 */

import { generateComprehensiveAssessment } from './assessmentAgent';
import { recommendGameForChild } from './gameRecommendAgent';
import {
  collectHistoricalData,
  checkDataCompleteness
} from './historicalDataHelper';
import { saveAssessment, saveRecommendation } from './assessmentStorage';
import { behaviorStorageService } from './behaviorStorage';
import { floorGameStorageService } from './floorGameStorage';
import {
  ChildProfile,
  ParentPreference,
  BehaviorAnalysis,
  EvaluationResult
} from '../types';

/**
 * 创建测试数据
 */
export const createTestData = () => {
  console.log('创建测试数据...');
  
  // 创建一些测试行为记录
  const testBehaviors: BehaviorAnalysis[] = [
    {
      behavior: '正在玩积木，专注地搭建高塔',
      matches: [
        { dimension: 'Construction', weight: 1.0, intensity: 0.8, reasoning: '直接体现建构兴趣，表现出专注和兴奋' },
        { dimension: 'Visual', weight: 0.7, intensity: 0.6, reasoning: '需要视觉观察和空间感知' },
        { dimension: 'Cognitive', weight: 0.6, intensity: 0.5, reasoning: '需要思考如何平衡和稳定' }
      ]
    },
    {
      behavior: '听到音乐就开始摇摆身体',
      matches: [
        { dimension: 'Auditory', weight: 1.0, intensity: 0.9, reasoning: '对音乐有强烈兴趣，主动响应' },
        { dimension: 'Motor', weight: 0.8, intensity: 0.7, reasoning: '喜欢用身体表达对音乐的感受' }
      ]
    },
    {
      behavior: '喜欢把玩具按颜色排列成一排',
      matches: [
        { dimension: 'Order', weight: 1.0, intensity: 0.8, reasoning: '强烈的秩序感，喜欢分类和排列' },
        { dimension: 'Visual', weight: 0.7, intensity: 0.6, reasoning: '对颜色有敏感度' },
        { dimension: 'Cognitive', weight: 0.5, intensity: 0.4, reasoning: '需要认知分类能力' }
      ]
    },
    {
      behavior: '看到其他小朋友会主动靠近',
      matches: [
        { dimension: 'Social', weight: 1.0, intensity: 0.6, reasoning: '有社交意愿，但还比较被动' },
        { dimension: 'Visual', weight: 0.4, intensity: 0.5, reasoning: '通过观察了解他人' }
      ]
    },
    {
      behavior: '触摸不同质地的物品时会仔细感受',
      matches: [
        { dimension: 'Tactile', weight: 1.0, intensity: 0.7, reasoning: '对触觉刺激有兴趣，愿意探索' },
        { dimension: 'Cognitive', weight: 0.5, intensity: 0.5, reasoning: '通过触觉学习和认知' }
      ]
    }
  ];
  
  testBehaviors.forEach(behavior => {
    const behaviorWithMeta = {
      ...behavior,
      timestamp: new Date().toISOString(),
      id: behaviorStorageService.generateBehaviorId()
    };
    behaviorStorageService.saveBehavior(behaviorWithMeta);
  });
  
  // 创建一些测试游戏评估
  const testEvaluations: EvaluationResult[] = [
    {
      score: 75,
      feedbackScore: 78,
      explorationScore: 72,
      summary: '孩子在游戏中表现积极，能够跟随指令，但在主动探索方面还需要鼓励',
      suggestion: '下次可以尝试更开放式的游戏，给孩子更多自主选择的机会'
    },
    {
      score: 80,
      feedbackScore: 82,
      explorationScore: 78,
      summary: '孩子今天状态很好，主动性有所提升，能够尝试新的玩法',
      suggestion: '继续保持，可以逐步增加游戏难度'
    },
    {
      score: 70,
      feedbackScore: 68,
      explorationScore: 72,
      summary: '孩子今天有些疲惫，注意力不太集中，但还是完成了游戏',
      suggestion: '注意观察孩子的状态，适时调整游戏节奏'
    }
  ];
  
  testEvaluations.forEach((evaluation, i) => {
    const gameId = `floor_game_test_${Date.now()}_${i}`;
    floorGameStorageService.saveGame({
      id: gameId,
      gameTitle: `测试游戏 ${i + 1}`,
      summary: evaluation.summary,
      goal: '综合训练',
      steps: [],
      status: 'completed',
      dtstart: new Date().toISOString(),
      dtend: new Date().toISOString(),
      isVR: false,
      evaluation
    });
  });
  
  console.log('测试数据创建完成');
  console.log(`- 行为记录: ${testBehaviors.length} 条`);
  console.log(`- 游戏评估: ${testEvaluations.length} 条`);
};

/**
 * 测试综合评估
 */
export const testAssessment = async () => {
  console.log('\n=== 测试综合评估 ===\n');
  
  const childProfile: ChildProfile = {
    name: '辰辰',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍（ASD），轻度',
    avatar: '',
    createdAt: '2024-01-01T00:00:00.000Z'
  };
  
  // 检查数据
  const dataCheck = checkDataCompleteness();
  console.log('数据检查:', dataCheck);
  
  if (!dataCheck.isReady) {
    console.log('\n⚠️  数据不足，无法生成评估');
    console.log('提示：请先记录一些行为数据，或调用 window.createTestData() 创建测试数据\n');
    return null;
  }
  
  // 收集历史数据
  const historicalData = collectHistoricalData();
  console.log('\n历史数据统计:');
  console.log(`- 评估: ${historicalData.recentAssessments.length} 次`);
  console.log(`- 报告: ${historicalData.recentReports.length} 份`);
  console.log(`- 行为: ${historicalData.recentBehaviors.length} 条`);
  console.log(`- 游戏: ${historicalData.recentGames.length} 次`);
  
  // 生成评估
  console.log('\n正在生成综合评估...');
  try {
    const assessment = await generateComprehensiveAssessment(
      childProfile,
      historicalData
    );
    
    saveAssessment(assessment);
    
    console.log('\n✅ 评估完成！\n');
    console.log('【评估摘要】');
    console.log(assessment.summary);
    console.log('\n【当前画像】');
    console.log(assessment.currentProfile);
    console.log('\n【下一步建议】');
    console.log(assessment.nextStepSuggestion);
    
    return assessment;
  } catch (error) {
    console.error('\n❌ 评估失败:', error);
    throw error;
  }
};

/**
 * 测试游戏推荐
 */
export const testRecommendation = async () => {
  console.log('\n=== 测试游戏推荐 ===\n');
  
  const childProfile: ChildProfile = {
    name: '辰辰',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍（ASD），轻度',
    avatar: '',
    createdAt: '2024-01-01T00:00:00.000Z'
  };
  
  // 获取最新评估
  const { getLatestAssessment } = await import('./assessmentStorage');
  let latestAssessment = getLatestAssessment();
  
  if (!latestAssessment) {
    console.log('没有评估记录，先生成评估...');
    latestAssessment = await testAssessment();
  }
  
  // 设置家长偏好
  const parentPreference: ParentPreference = {
    duration: 'medium',
    difficulty: 'moderate',
    environment: 'indoor',
    focus: ['双向沟通', '自我调节'],
    notes: '孩子对视觉刺激比较敏感，建议选择视觉元素丰富的游戏'
  };
  
  console.log('\n家长偏好:');
  console.log(`- 时长: ${parentPreference.duration}`);
  console.log(`- 难度: ${parentPreference.difficulty}`);
  console.log(`- 环境: ${parentPreference.environment}`);
  console.log(`- 重点: ${parentPreference.focus.join('、')}`);
  
  // 推荐游戏
  console.log('\n正在推荐游戏...');
  try {
    const historicalData = collectHistoricalData();
    const recommendation = await recommendGameForChild(
      childProfile,
      latestAssessment,
      historicalData,
      parentPreference
    );
    
    saveRecommendation(recommendation);
    
    console.log('\n✅ 推荐完成！\n');
    console.log('【推荐游戏】', recommendation.game.title);
    console.log('【训练目标】', recommendation.game.target);
    console.log('【游戏时长】', recommendation.game.duration);
    console.log('\n【推荐理由】');
    console.log(recommendation.reason);
    console.log('\n【预期效果】');
    console.log(recommendation.expectedOutcome);
    console.log('\n【家长指导】');
    console.log(recommendation.parentGuidance);
    console.log('\n【适应性建议】');
    recommendation.adaptationSuggestions.forEach((s, i) => 
      console.log(`${i + 1}. ${s}`)
    );
    console.log('\n【游戏步骤】');
    recommendation.game.steps.forEach((step, i) => 
      console.log(`${i + 1}. ${step.instruction}\n   💡 ${step.guidance}`)
    );
    
    return recommendation;
  } catch (error) {
    console.error('\n❌ 推荐失败:', error);
    throw error;
  }
};

/**
 * 运行完整测试
 */
export const runFullTest = async () => {
  console.log('╔════════════════════════════════════════╗');
  console.log('║  综合评估与游戏推荐系统 - 完整测试  ║');
  console.log('╚════════════════════════════════════════╝');
  
  try {
    // 测试评估
    const assessment = await testAssessment();
    
    // 等待一下，避免API限流
    console.log('\n等待 2 秒...\n');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 测试推荐
    const recommendation = await testRecommendation();
    
    console.log('\n╔════════════════════════════════════════╗');
    console.log('║          ✅ 所有测试通过！           ║');
    console.log('╚════════════════════════════════════════╝');
    
    return { assessment, recommendation };
  } catch (error) {
    console.log('\n╔════════════════════════════════════════╗');
    console.log('║          ❌ 测试失败！               ║');
    console.log('╚════════════════════════════════════════╝');
    throw error;
  }
};

// 如果直接运行此文件
if (typeof window !== 'undefined') {
  (window as any).testAssessment = testAssessment;
  (window as any).testRecommendation = testRecommendation;
  (window as any).runFullTest = runFullTest;
  (window as any).createTestData = createTestData;
  
  console.log('测试函数已加载到 window 对象:');
  console.log('- window.createTestData() - 创建测试数据');
  console.log('- window.testAssessment() - 测试评估');
  console.log('- window.testRecommendation() - 测试推荐');
  console.log('- window.runFullTest() - 运行完整测试');
  console.log('');
  console.log('⚠️  注意：不会自动创建测试数据，需要手动调用 createTestData()');
}
