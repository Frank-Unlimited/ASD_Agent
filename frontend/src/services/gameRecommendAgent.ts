/**
 * Game Recommendation Agent
 * 游戏推荐Agent - 基于综合评估和家长偏好推荐最适合的地板游戏
 */

import { qwenStreamClient } from './qwenStreamClient';
import { GameRecommendationDetailedSchema } from './qwenSchemas';
import { searchGamesOnline } from './onlineSearchService';
import { 
  GameRecommendation, 
  ComprehensiveAssessment,
  HistoricalDataSummary,
  ChildProfile,
  ParentPreference
} from '../types';

const GAME_RECOMMEND_SYSTEM_PROMPT = `
你是一位经验丰富的 DIR/Floortime 游戏设计师和干预专家。
你的任务是基于孩子的综合评估和家长偏好，从游戏库中推荐最适合的地板游戏。

推荐原则：
1. 目标导向：游戏应针对下一步干预建议中的重点能力
2. 兴趣驱动：利用孩子的高兴趣维度作为切入点
3. 适度挑战：难度略高于当前水平，但不会让孩子挫败
4. 家长友好：考虑家长的时间、环境、能力限制
5. 可调整性：提供适应性调整建议，灵活应对孩子状态

DIR/Floortime 核心理念：
- 跟随孩子的引导（Follow the child's lead）
- 进入孩子的世界（Enter the child's world）
- 扩展互动（Expand the interaction）
- 建立情感连接（Build emotional connection）

请用温暖、鼓励、实用的语气提供推荐。
`;

/**
 * 为孩子推荐游戏
 */
export const recommendGameForChild = async (
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment,
  historicalData: HistoricalDataSummary,
  parentPreference: ParentPreference
): Promise<GameRecommendation> => {
  try {
    // Step 1: 使用混合搜索（本地库 + 联网搜索）
    const searchQuery = buildSearchQuery(latestAssessment, historicalData, parentPreference);
    const childContext = buildChildContext(childProfile, latestAssessment);
    const candidateGames = await searchGamesOnline(searchQuery, childContext, 5);

    // Step 2: LLM 选择最佳游戏并生成详细推荐
    const prompt = buildRecommendationPrompt(
      childProfile,
      latestAssessment,
      historicalData,
      parentPreference,
      candidateGames
    );

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Game Recommend Agent] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log(GAME_RECOMMEND_SYSTEM_PROMPT);
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(prompt);
    console.log('='.repeat(80));

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: GAME_RECOMMEND_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 3000,
        response_format: {
          type: 'json_schema',
          json_schema: GameRecommendationDetailedSchema
        }
      }
    );

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Game Recommend Agent] 完整响应:');
    console.log('='.repeat(80));
    console.log(response);
    console.log('='.repeat(80));

    const data = JSON.parse(response);
    
    return {
      id: `recommendation_${Date.now()}_${Math.random().toString(36).substring(2, 9)}`,
      timestamp: new Date().toISOString(),
      assessmentId: latestAssessment.id,
      ...data
    };
  } catch (error) {
    console.error('Game Recommendation Failed:', error);
    throw error;
  }
};

/**
 * 构建搜索查询
 */
function buildSearchQuery(
  assessment: ComprehensiveAssessment,
  historicalData: HistoricalDataSummary,
  preference: ParentPreference
): string {
  const highInterests = Object.entries(historicalData.interestTrends)
    .filter(([_, score]) => score > 60)
    .map(([dim]) => dim);
  
  const lowAbilities = Object.entries(historicalData.abilityTrends)
    .filter(([_, score]) => score < 50)
    .map(([dim]) => dim);

  const parts = [
    `兴趣：${highInterests.join(' ')}`,
    `能力：${preference.focus.join(' ')}`,
    `目标：${lowAbilities.join(' ')}`,
    `难度：${preference.difficulty}`,
    `时长：${preference.duration}`,
    `环境：${preference.environment}`
  ];

  return parts.join(' ');
}

/**
 * 构建儿童上下文信息（用于联网搜索）
 */
function buildChildContext(
  childProfile: ChildProfile,
  assessment: ComprehensiveAssessment
): string {
  return `
儿童基本信息：
- 姓名：${childProfile.name}
- 性别：${childProfile.gender}
- 诊断：${childProfile.diagnosis || '自闭症谱系障碍'}

当前画像：
${assessment.currentProfile}

评估摘要：
${assessment.summary}
`.trim();
}

/**
 * 构建推荐提示词
 */
function buildRecommendationPrompt(
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment,
  historicalData: HistoricalDataSummary,
  parentPreference: ParentPreference,
  candidateGames: any[]
): string {
  const highInterests = Object.entries(historicalData.interestTrends)
    .filter(([_, score]) => score > 60)
    .map(([dim, score]) => `${dim}(${score.toFixed(0)}分)`);
  
  const lowAbilities = Object.entries(historicalData.abilityTrends)
    .filter(([_, score]) => score < 50)
    .map(([dim, score]) => `${dim}(${score.toFixed(0)}分)`);

  return `
请为以下儿童推荐一个最适合的地板游戏：

【基本信息】
姓名：${childProfile.name}
性别：${childProfile.gender}

【当前画像】
${latestAssessment.currentProfile}

【最新评估】
评估摘要：${latestAssessment.summary}
下一步建议：${latestAssessment.nextStepSuggestion}

【兴趣维度】
高兴趣维度：${highInterests.length > 0 ? highInterests.join(', ') : '暂无明显高兴趣'}

【能力维度】
需要提升：${lowAbilities.length > 0 ? lowAbilities.join(', ') : '整体均衡'}

【家长偏好】
时长偏好：${getDurationLabel(parentPreference.duration)}
难度偏好：${getDifficultyLabel(parentPreference.difficulty)}
环境偏好：${getEnvironmentLabel(parentPreference.environment)}
重点训练：${parentPreference.focus.join('、')}
${parentPreference.avoidTopics && parentPreference.avoidTopics.length > 0 
  ? `避免主题：${parentPreference.avoidTopics.join('、')}` 
  : ''}
${parentPreference.notes ? `备注：${parentPreference.notes}` : ''}

【候选游戏库】
${candidateGames.map((g, i: number) => 
  `${i + 1}. ID: ${g.id}
   名称：${g.title}
   目标：${g.target}
   时长：${g.duration}
   ${g.isVR ? '[VR游戏]' : ''}
   特点：${g.reason}
   步骤：${g.steps.map((s: any) => s.instruction).join(' → ')}`
).join('\n\n')}

请从候选游戏中选择最合适的一个，并生成：

1. game：选中的游戏完整信息
   - 必须从候选游戏中选择一个
   - 包括完整的 id, title, target, duration, steps, isVR 等字段
   - steps 必须是数组，每个元素包含 instruction 和 guidance
   
2. reason：详细推荐理由（150-200字）
   - 为什么这个游戏最适合这个孩子
   - 如何利用孩子的兴趣点
   - 如何针对需要提升的能力
   - 为什么符合家长的偏好
   
3. parentGuidance：家长指导要点（150字左右）
   - 如何引导孩子参与
   - 需要注意的事项
   - 如何观察孩子的反应
   - 如何调整互动方式
   - 地板游戏的核心是跟随孩子的主导，家长应该观察和回应，而不是控制
   
4. adaptationSuggestions：3-5条适应性调整建议（每条30-50字）
   - 如果孩子不感兴趣怎么办
   - 如果孩子太兴奋怎么办
   - 如果孩子遇到困难怎么办
   - 如何增加难度
   - 如何降低难度

请严格按照 JSON Schema 返回结果。
`;
}

/**
 * 获取时长标签
 */
function getDurationLabel(duration: string): string {
  const labels: Record<string, string> = {
    short: '短时（10-15分钟）',
    medium: '中等（15-20分钟）',
    long: '长时（20-30分钟）'
  };
  return labels[duration] || duration;
}

/**
 * 获取难度标签
 */
function getDifficultyLabel(difficulty: string): string {
  const labels: Record<string, string> = {
    easy: '简单（适合初学）',
    moderate: '适中（有一定挑战）',
    challenging: '有挑战（需要努力）'
  };
  return labels[difficulty] || difficulty;
}

/**
 * 获取环境标签
 */
function getEnvironmentLabel(environment: string): string {
  const labels: Record<string, string> = {
    indoor: '室内',
    outdoor: '户外',
    both: '室内外均可'
  };
  return labels[environment] || environment;
}
