/**
 * Behavior Analysis Agent
 * 行为分析Agent - 专门用于解析行为并关联兴趣维度
 */

import { qwenStreamClient } from './qwenStreamClient';
import { BehaviorAnalysis, InterestDimensionType, ChildProfile } from '../types';

const BEHAVIOR_ANALYSIS_SYSTEM_PROMPT = `
你是一位专业的儿童行为分析师，专注于 ASD（自闭症谱系障碍）儿童的兴趣维度分析。
你的任务是分析儿童的具体行为，识别相关的兴趣维度，并评估关联度和强度。

八大兴趣维度：
- Visual(视觉)：对视觉刺激的兴趣，如颜色、形状、光影、图案
- Auditory(听觉)：对声音、音乐、节奏、音调的兴趣
- Tactile(触觉)：对触摸、质地、温度、触感的兴趣
- Motor(运动)：对身体运动、大动作、跑跳的兴趣
- Construction(建构)：对搭建、组装、创造、拼装的兴趣
- Order(秩序)：对规则、排列、分类、整理的兴趣
- Cognitive(认知)：对思考、解决问题、学习、探索的兴趣
- Social(社交)：对人际互动、情感连接、交流的兴趣

分析原则：
1. **关联度（weight）**：行为与兴趣维度的关联程度（0.1-1.0，只能是正值）
   - 1.0 = 强关联：行为直接体现该维度（如"玩积木"与 Construction）
   - 0.7 = 中等关联：行为部分体现该维度（如"玩积木"与 Visual）
   - 0.4 = 弱关联：行为间接涉及该维度（如"玩积木"与 Social）
   - 只标注关联度 >= 0.4 的维度

2. **强度（intensity）**：孩子对该维度的情绪态度（-1.0 到 1.0）
   - +1.0 = 非常喜欢：兴奋、主动、不愿停止
   - +0.5 = 比较喜欢：专注、投入、愿意参与
   - 0.0 = 中性：被动接受、无明显情绪
   - -0.5 = 比较抗拒：回避、不情愿、需要引导
   - -1.0 = 非常讨厌：哭闹、拒绝、强烈抗拒

3. **推理说明（reasoning）**：
   - 解释为什么该行为与该维度相关（关联度）
   - 说明孩子的情绪态度和参与度（强度）
   - 提供具体的观察依据

4. **分析要点**：
   - 不要给所有维度都设置相同的值
   - 根据行为的实际特征区分主次
   - 关注孩子的情绪反应和参与度
   - 提供具体、可观察的分析

请用专业、客观、准确的语气进行分析。
`;

/**
 * 分析行为并关联兴趣维度
 */
export const analyzeBehavior = async (
  behaviorDescription: string,
  childProfile?: ChildProfile,
  conversationContext?: string
): Promise<BehaviorAnalysis> => {
  try {
    const prompt = buildAnalysisPrompt(behaviorDescription, childProfile, conversationContext);

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Behavior Analysis Agent] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log(BEHAVIOR_ANALYSIS_SYSTEM_PROMPT);
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(prompt);
    console.log('='.repeat(80));

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: BEHAVIOR_ANALYSIS_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 1500,
        response_format: {
          type: 'json_schema',
          json_schema: {
            name: 'behavior_analysis',
            schema: {
              type: 'object',
              properties: {
                behavior: {
                  type: 'string',
                  description: '精简的行为描述（10-20字），例如："正在玩积木"、"盯着旋转物体"'
                },
                dimensions: {
                  type: 'array',
                  description: '相关的兴趣维度列表（只包含关联度 >= 0.4 的维度）',
                  items: {
                    type: 'object',
                    properties: {
                      dimension: {
                        type: 'string',
                        enum: ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'],
                        description: '兴趣维度名称'
                      },
                      weight: {
                        type: 'number',
                        description: '关联度 (0.4-1.0)：该行为与该兴趣维度的关联程度',
                        minimum: 0.4,
                        maximum: 1.0
                      },
                      intensity: {
                        type: 'number',
                        description: '强度 (-1.0 到 1.0)：孩子对该维度的情绪态度',
                        minimum: -1.0,
                        maximum: 1.0
                      },
                      reasoning: {
                        type: 'string',
                        description: '推理说明（30-50字）：解释关联度和强度的依据'
                      }
                    },
                    required: ['dimension', 'weight', 'intensity', 'reasoning'],
                    additionalProperties: false
                  }
                },
                analysis: {
                  type: 'string',
                  description: '一句话分析其发展意义（20-30字），例如："显示出对建构活动的兴趣，有助于精细动作发展"'
                }
              },
              required: ['behavior', 'dimensions', 'analysis'],
              additionalProperties: false
            }
          }
        }
      }
    );

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Behavior Analysis Agent] 完整响应:');
    console.log('='.repeat(80));
    console.log(response);
    console.log('='.repeat(80));
    
    // 解析响应
    let data;
    try {
      const parsed = JSON.parse(response);
      // 如果返回的是数组，取第一个元素
      data = Array.isArray(parsed) ? parsed[0] : parsed;
    } catch (parseError) {
      console.error('[Behavior Analysis Agent] JSON parse error:', parseError);
      throw new Error('无法解析行为分析结果，请重试');
    }
    
    // 验证必需字段
    if (!data || !data.behavior || !data.dimensions || !Array.isArray(data.dimensions) || !data.analysis) {
      console.error('[Behavior Analysis Agent] 缺少必需字段:', data);
      console.error('[Behavior Analysis Agent] 期望字段: behavior, dimensions, analysis');
      throw new Error('行为分析数据不完整');
    }
    
    // 转换为 BehaviorAnalysis 格式
    const behaviorAnalysis: BehaviorAnalysis = {
      behavior: data.behavior,
      matches: data.dimensions.map((dim: any) => ({
        dimension: dim.dimension as InterestDimensionType,
        weight: dim.weight,
        intensity: dim.intensity,
        reasoning: dim.reasoning
      })),
      timestamp: new Date().toISOString(),
      source: 'CHAT'
    };
    
    console.log('[Behavior Analysis Agent] Analysis result:', behaviorAnalysis);
    return behaviorAnalysis;
  } catch (error) {
    console.error('Behavior Analysis Failed:', error);
    throw error;
  }
};

/**
 * 构建分析提示词
 */
function buildAnalysisPrompt(
  behaviorDescription: string,
  childProfile?: ChildProfile,
  conversationContext?: string
): string {
  let prompt = `请分析以下儿童行为：\n\n`;
  
  // 添加孩子信息（如果有）
  if (childProfile) {
    const age = calculateAge(childProfile.birthDate);
    prompt += `【儿童信息】\n`;
    prompt += `姓名：${childProfile.name}\n`;
    prompt += `性别：${childProfile.gender}\n`;
    prompt += `年龄：${age}\n`;
    prompt += `诊断：${childProfile.diagnosis || '暂无'}\n\n`;
  }
  
  // 添加对话上下文（如果有）
  if (conversationContext) {
    prompt += `【对话上下文】\n${conversationContext}\n\n`;
  }
  
  // 添加行为描述
  prompt += `【行为描述】\n${behaviorDescription}\n\n`;
  
  prompt += `请完成以下任务：\n\n`;
  prompt += `1. 提炼行为描述：将行为描述精简为10-20字的核心描述\n`;
  prompt += `2. 识别相关维度：分析该行为涉及哪些兴趣维度（只标注关联度 >= 0.4 的维度）\n`;
  prompt += `3. 评估关联度：为每个维度评估关联度（0.4-1.0）\n`;
  prompt += `4. 评估强度：根据孩子的情绪反应和参与度评估强度（-1.0 到 1.0）\n`;
  prompt += `5. 提供推理：为每个维度提供30-50字的推理说明\n`;
  prompt += `6. 发展意义：用一句话（20-30字）总结该行为的发展意义\n\n`;
  
  prompt += `注意事项：\n`;
  prompt += `- 不要给所有维度都设置相同的值\n`;
  prompt += `- 根据行为的实际特征区分主次\n`;
  prompt += `- 关注孩子的情绪反应和参与度\n`;
  prompt += `- 提供具体、可观察的分析\n`;
  prompt += `- 如果行为描述中没有明确的情绪信息，强度默认为 0.5（比较喜欢）\n\n`;
  
  prompt += `请严格按照 JSON Schema 返回结果。`;
  
  return prompt;
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
