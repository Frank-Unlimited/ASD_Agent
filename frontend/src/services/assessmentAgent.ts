/**
 * Comprehensive Assessment Agent
 * 综合评估Agent - 基于历史数据生成孩子当前画像和下一步干预建议
 */

import { qwenStreamClient } from './qwenStreamClient';
import { ComprehensiveAssessmentSchema } from './qwenSchemas';
import {
  ComprehensiveAssessment,
  HistoricalDataSummary,
  ChildProfile
} from '../types';
import { fetchMemoryFacts, formatMemoryFactsForPrompt, MemoryFact } from './memoryService';
import { getAccountId } from './accountService';
import { ASSESSMENT_SYSTEM_PROMPT } from '../prompts';

/**
 * 生成综合评估
 */
export const generateComprehensiveAssessment = async (
  childProfile: ChildProfile,
  historicalData: HistoricalDataSummary
): Promise<ComprehensiveAssessment> => {
  try {
    // ── 拉取 graphiti 跨时间记忆（降级安全：不可用时返回空数组）──
    const memoryFacts: MemoryFact[] = await fetchMemoryFacts(
      getAccountId(),
      `${childProfile.name}完整干预历史：兴趣维度偏好与变化趋势、游戏活动参与情况与效果、行为表现规律、医疗报告诊断、历次评估画像与干预建议`,
      30
    );
    console.log(`[Assessment Agent] graphiti 记忆: 获取 ${memoryFacts.length} 条 facts`);

    const prompt = buildAssessmentPrompt(childProfile, historicalData, memoryFacts);

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Assessment Agent] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log(ASSESSMENT_SYSTEM_PROMPT);
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(prompt);
    console.log('='.repeat(80));

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: ASSESSMENT_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 3000,
        response_format: {
          type: 'json_schema',
          json_schema: ComprehensiveAssessmentSchema
        }
      }
    );

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Assessment Agent] 完整响应:');
    console.log('='.repeat(80));
    console.log(response);
    console.log('='.repeat(80));

    console.log('[Assessment Agent] Raw response:', response);
    
    // 尝试解析响应
    let data;
    try {
      data = JSON.parse(response);
    } catch (parseError) {
      console.error('[Assessment Agent] JSON parse error:', parseError);
      console.log('[Assessment Agent] Raw response text:', response);
      throw new Error('无法解析 LLM 响应，请重试');
    }
    
    // 如果返回的是数组，取第一个元素
    if (Array.isArray(data)) {
      console.log('[Assessment Agent] Response is array, taking first element');
      data = data[0];
    }
    
    // 检查是否返回了 Schema 定义而不是实际数据
    // Schema 定义会有 "type", "properties", "required" 等字段
    if (data.type === 'object' && data.properties && data.required) {
      console.error('[Assessment Agent] ❌ LLM 返回了 Schema 定义而不是数据！');
      console.log('[Assessment Agent] Schema properties:', Object.keys(data.properties));
      
      // 这是一个常见问题，尝试重新调用
      throw new Error('LLM 返回了 Schema 定义而不是实际数据。请再试一次，或者稍后重试。');
    }
    
    // 验证必需字段
    const requiredFields = ['summary', 'currentProfile', 'nextStepSuggestion'];
    const missingFields = requiredFields.filter(field => !data[field]);
    
    if (missingFields.length > 0) {
      console.error('[Assessment Agent] 缺少必需字段:', missingFields);
      console.log('[Assessment Agent] 实际返回的字段:', Object.keys(data));
      throw new Error(`评估数据不完整，缺少字段: ${missingFields.join(', ')}`);
    }
    
    console.log('[Assessment Agent] Parsed data:', data);
    
    const assessment: ComprehensiveAssessment = {
      id: `assessment_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      timestamp: new Date().toISOString(),
      summary: data.summary || '',
      currentProfile: data.currentProfile || '',
      nextStepSuggestion: data.nextStepSuggestion || ''
    };
    
    console.log('[Assessment Agent] Final assessment:', assessment);
    return assessment;
  } catch (error) {
    console.error('Comprehensive Assessment Failed:', error);
    throw error;
  }
};

/**
 * 构建评估提示词
 */
function buildAssessmentPrompt(
  childProfile: ChildProfile,
  historicalData: HistoricalDataSummary,
  memoryFacts: MemoryFact[] = []
): string {
  const age = calculateAge(childProfile.birthDate);
  const memorySection = formatMemoryFactsForPrompt(memoryFacts);

  return `
请对以下儿童进行综合评估：

【基本信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${age}
当前诊断：${childProfile.diagnosis || '暂无'}

${memorySection ? `【干预历史记忆】
${memorySection}
说明：优先参考"最新观察"（原始记录）和"当前有效事实"（现状依据）；"历史事实"已被覆盖，仅用于感知变化幅度；valid_at 表示事实生效时间。

` : ''}【兴趣维度趋势分数】（0-100，基于历史行为记录加权计算）
${Object.entries(historicalData.interestTrends).map(([dim, score]) =>
  `${dim}: ${score.toFixed(1)}分`
).join(', ')}

请生成以下三个字段：

1. summary（50字以内）：一句话概括孩子当前状态和主要特点

2. currentProfile（200-300字）：当前孩子的详细画像
   - 涵盖性格特点、兴趣偏好、社交表现、发展特点
   - 具体、生动，让家长能"看到"自己的孩子

3. nextStepSuggestion（150-200字）：下一步干预建议
   - 基于孩子的高分兴趣维度设计活动
   - 提供2-3个具体可执行的活动建议
`;
}

/**
 * 计算年龄
 */
function calculateAge(birthDate: string): string {
  const birth = new Date(birthDate);
  const now = new Date();
  const years = now.getFullYear() - birth.getFullYear();
  const months = now.getMonth() - birth.getMonth();
  
  let ageYears = years;
  let ageMonths = months;
  
  if (months < 0) {
    ageYears--;
    ageMonths = 12 + months;
  }
  
  if (ageYears > 0) {
    return `${ageYears}岁${ageMonths}个月`;
  } else {
    return `${ageMonths}个月`;
  }
}

/**
 * 格式化日期
 */
function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}
