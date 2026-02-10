/**
 * Assessment & Recommendation Example
 * 展示如何使用综合评估和游戏推荐Agent
 */

import { generateComprehensiveAssessment } from './assessmentAgent';
import { recommendGameForChild } from './gameRecommendAgent';
import { collectHistoricalData, checkDataCompleteness } from './historicalDataHelper';
import { saveAssessment, getLatestAssessment, saveRecommendation } from './assessmentStorage';
import { ChildProfile, ParentPreference } from '../types';

/**
 * 示例1：生成综合评估
 */
export const exampleGenerateAssessment = async () => {
  // 1. 准备孩子档案
  const childProfile: ChildProfile = {
    name: '辰辰',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍（ASD），轻度',
    avatar: '',
    createdAt: '2024-01-01T00:00:00.000Z'
  };

  // 2. 检查数据完整性
  const dataCheck = checkDataCompleteness();
  console.log('数据检查:', dataCheck);
  
  if (!dataCheck.isReady) {
    console.warn(dataCheck.message);
    // 可以选择继续或提示用户
  }

  // 3. 收集历史数据
  const historicalData = collectHistoricalData();
  console.log('历史数据:', {
    评估次数: historicalData.recentAssessments.length,
    报告数量: historicalData.recentReports.length,
    行为记录: historicalData.recentBehaviors.length,
    游戏评估: historicalData.recentGames.length
  });

  // 4. 生成综合评估
  try {
    console.log('正在生成综合评估...');
    const assessment = await generateComprehensiveAssessment(
      childProfile,
      historicalData
    );
    
    // 5. 保存评估结果
    saveAssessment(assessment);
    
    console.log('评估完成:', {
      id: assessment.id,
      timestamp: assessment.timestamp,
      currentProfile: assessment.currentProfile,
      nextStepSuggestion: assessment.nextStepSuggestion,
      keyFindings: assessment.keyFindings,
      strengths: assessment.strengths,
      concerns: assessment.concerns
    });
    
    return assessment;
  } catch (error) {
    console.error('评估失败:', error);
    throw error;
  }
};

/**
 * 示例2：推荐游戏
 */
export const exampleRecommendGame = async () => {
  // 1. 准备孩子档案
  const childProfile: ChildProfile = {
    name: '辰辰',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍（ASD），轻度',
    avatar: '',
    createdAt: '2024-01-01T00:00:00.000Z'
  };

  // 2. 获取最新评估
  const latestAssessment = getLatestAssessment();
  if (!latestAssessment) {
    console.error('请先生成综合评估');
    throw new Error('No assessment found. Please generate assessment first.');
  }

  // 3. 收集历史数据
  const historicalData = collectHistoricalData();

  // 4. 设置家长偏好
  const parentPreference: ParentPreference = {
    duration: 'medium',        // 中等时长
    difficulty: 'moderate',    // 适中难度
    environment: 'indoor',     // 室内
    focus: ['双向沟通', '自我调节'], // 重点训练的能力
    avoidTopics: [],           // 避免的主题
    notes: '孩子对视觉刺激比较敏感，建议选择视觉元素丰富的游戏'
  };

  // 5. 推荐游戏
  try {
    console.log('正在推荐游戏...');
    const recommendation = await recommendGameForChild(
      childProfile,
      latestAssessment,
      historicalData,
      parentPreference
    );
    
    // 6. 保存推荐结果
    saveRecommendation(recommendation);
    
    console.log('推荐完成:', {
      id: recommendation.id,
      timestamp: recommendation.timestamp,
      game: recommendation.game,
      reason: recommendation.reason,
      expectedOutcome: recommendation.expectedOutcome,
      parentGuidance: recommendation.parentGuidance,
      adaptationSuggestions: recommendation.adaptationSuggestions
    });
    
    return recommendation;
  } catch (error) {
    console.error('推荐失败:', error);
    throw error;
  }
};

/**
 * 示例3：完整流程（评估 + 推荐）
 */
export const exampleFullWorkflow = async () => {
  const childProfile: ChildProfile = {
    name: '辰辰',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍（ASD），轻度',
    avatar: '',
    createdAt: '2024-01-01T00:00:00.000Z'
  };

  const parentPreference: ParentPreference = {
    duration: 'medium',
    difficulty: 'moderate',
    environment: 'indoor',
    focus: ['双向沟通', '自我调节']
  };

  try {
    // Step 1: 生成评估
    console.log('=== 步骤1：生成综合评估 ===');
    const assessment = await exampleGenerateAssessment();
    
    console.log('\n当前画像:');
    console.log(assessment.currentProfile);
    
    console.log('\n下一步建议:');
    console.log(assessment.nextStepSuggestion);
    
    console.log('\n关键发现:');
    assessment.keyFindings.forEach((f, i) => console.log(`${i + 1}. ${f}`));
    
    // Step 2: 推荐游戏
    console.log('\n=== 步骤2：推荐游戏 ===');
    const historicalData = collectHistoricalData();
    const recommendation = await recommendGameForChild(
      childProfile,
      assessment,
      historicalData,
      parentPreference
    );
    
    saveRecommendation(recommendation);
    
    console.log('\n推荐游戏:', recommendation.game.title);
    console.log('推荐理由:', recommendation.reason);
    console.log('预期效果:', recommendation.expectedOutcome);
    
    console.log('\n家长指导:');
    console.log(recommendation.parentGuidance);
    
    console.log('\n适应性建议:');
    recommendation.adaptationSuggestions.forEach((s, i) => 
      console.log(`${i + 1}. ${s}`)
    );
    
    return { assessment, recommendation };
  } catch (error) {
    console.error('流程执行失败:', error);
    throw error;
  }
};

/**
 * 示例4：自定义家长偏好
 */
export const exampleCustomPreference = async () => {
  const childProfile: ChildProfile = {
    name: '辰辰',
    gender: '男',
    birthDate: '2020-03-15',
    diagnosis: '自闭症谱系障碍（ASD），轻度',
    avatar: '',
    createdAt: '2024-01-01T00:00:00.000Z'
  };

  // 自定义偏好：短时、简单、户外、重点训练运动和社交
  const customPreference: ParentPreference = {
    duration: 'short',         // 短时（10-15分钟）
    difficulty: 'easy',        // 简单
    environment: 'outdoor',    // 户外
    focus: ['自我调节', '亲密感'], // 重点训练
    avoidTopics: ['VR', '电子设备'], // 避免VR和电子设备
    notes: '孩子最近对户外活动很感兴趣，希望多一些户外游戏'
  };

  const latestAssessment = getLatestAssessment();
  if (!latestAssessment) {
    throw new Error('请先生成综合评估');
  }

  const historicalData = collectHistoricalData();
  
  const recommendation = await recommendGameForChild(
    childProfile,
    latestAssessment,
    historicalData,
    customPreference
  );
  
  saveRecommendation(recommendation);
  
  return recommendation;
};
