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

const ASSESSMENT_SYSTEM_PROMPT = `
你是一位资深的 DIR/Floortime 疗法专家和儿童发展评估师。
你的任务是基于孩子的历史数据进行综合评估，生成当前画像和下一步干预建议。

评估原则：
1. 全面性：综合考虑兴趣维度、能力维度、行为表现、游戏反馈
2. 发展性：关注孩子的进步趋势和潜力
3. 个性化：基于孩子的独特兴趣点设计建议
4. 可操作性：提供具体、可执行的干预建议
5. 鼓励性：强调优势，温和指出需要改进的地方

八大兴趣维度：
- Visual(视觉)：对视觉刺激的兴趣，如颜色、形状、光影
- Auditory(听觉)：对声音、音乐、节奏的兴趣
- Tactile(触觉)：对触摸、质地、温度的兴趣
- Motor(运动)：对身体运动、大动作的兴趣
- Construction(建构)：对搭建、组装、创造的兴趣
- Order(秩序)：对规则、排列、分类的兴趣
- Cognitive(认知)：对思考、解决问题、学习的兴趣
- Social(社交)：对人际互动、情感连接的兴趣

DIR 六大能力维度：
- 自我调节：调节情绪、注意力和行为的能力
- 亲密感：与他人建立情感连接的能力
- 双向沟通：进行来回互动和交流的能力
- 复杂沟通：使用语言和非语言进行复杂交流的能力
- 情绪思考：理解和表达情绪的能力
- 逻辑思维：进行逻辑推理和抽象思考的能力

请用温暖、专业、鼓励的语气进行评估。
`;

/**
 * 生成综合评估
 */
export const generateComprehensiveAssessment = async (
  childProfile: ChildProfile,
  historicalData: HistoricalDataSummary
): Promise<ComprehensiveAssessment> => {
  try {
    const prompt = buildAssessmentPrompt(childProfile, historicalData);

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
  historicalData: HistoricalDataSummary
): string {
  const age = calculateAge(childProfile.birthDate);
  
  return `
请对以下儿童进行综合评估：

【基本信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${age}
出生日期：${childProfile.birthDate}
当前诊断：${childProfile.diagnosis || '暂无'}

【历史评估记录】（共${historicalData.recentAssessments.length}次）
${historicalData.recentAssessments.length > 0 
  ? historicalData.recentAssessments.map((a, i) => 
      `${i + 1}. [${formatDate(a.timestamp)}] ${a.nextStepSuggestion}`
    ).join('\n')
  : '暂无历史评估'}

【最近报告分析】（共${historicalData.recentReports.length}份）
${historicalData.recentReports.length > 0
  ? historicalData.recentReports.map((r, i) => 
      `${i + 1}. [${r.date}] ${r.summary}\n   画像：${r.diagnosis}`
    ).join('\n')
  : '暂无报告'}

【最近行为记录】（共${historicalData.recentBehaviors.length}条）
${historicalData.recentBehaviors.length > 0
  ? historicalData.recentBehaviors.slice(0, 10).map((b, i) => {
      const dimensions = b.matches.map(m => 
        `${m.dimension}(关联${m.weight.toFixed(1)}, 强度${m.intensity > 0 ? '+' : ''}${m.intensity.toFixed(1)})`
      ).join(', ');
      return `${i + 1}. ${b.behavior} - ${dimensions}`;
    }).join('\n')
  : '暂无行为记录'}

【最近游戏评估】（共${historicalData.recentGames.length}次）
${historicalData.recentGames.length > 0
  ? historicalData.recentGames.map((g, i) => 
      `${i + 1}. 综合${g.score}分, 反馈${g.feedbackScore}分, 探索${g.explorationScore}分\n   总结：${g.summary}\n   建议：${g.suggestion}`
    ).join('\n')
  : '暂无游戏评估'}

【兴趣维度趋势】
${Object.entries(historicalData.interestTrends).map(([dim, score]) => 
  `${dim}: ${score.toFixed(1)}分`
).join(', ')}

【能力维度趋势】
${Object.entries(historicalData.abilityTrends).map(([dim, score]) => 
  `${dim}: ${score.toFixed(1)}分`
).join(', ')}

请生成：
1. summary：评估摘要（50字以内）
   - 一句话概括孩子当前状态和主要特点
   - 简洁明了，让家长快速了解核心信息
   
2. currentProfile：当前孩子的详细画像（200-300字）
   - 包括性格特点、兴趣偏好、能力水平、社交表现、发展特点
   - 要具体、生动，让家长能"看到"自己的孩子
   - 综合兴趣维度和能力维度的分析
   
3. nextStepSuggestion：下一步干预建议（150-200字）
   - 具体、可操作的建议
   - 基于孩子的兴趣点设计活动
   - 针对需要提升的能力
   - 提供2-3个具体的活动建议

请严格按照 JSON Schema 返回结果。

重要提示：
- 请直接返回包含实际数据的 JSON 对象
- 不要返回 Schema 定义本身
- 确保返回的 JSON 包含所有必需字段的实际内容
- 示例格式：
{
  "summary": "这里是评估摘要，一句话概括...",
  "currentProfile": "这里是孩子的详细画像...",
  "nextStepSuggestion": "这里是下一步建议..."
}
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
