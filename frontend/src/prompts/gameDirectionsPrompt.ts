/**
 * 游戏方向建议生成的 Prompt 模板
 */

import { ChildProfile, ComprehensiveAssessment, HistoricalDataSummary } from '../types';

export interface GameDirectionsPromptParams {
  childProfile: ChildProfile;
  latestAssessment: ComprehensiveAssessment | null;
  historicalData: HistoricalDataSummary;
  interestDetails: string;
  abilityDetails: string;
  highInterests: string[];
  lowAbilities: string[];
  recentGames: any[];
  userPreferences?: {
    environment?: string;
    duration?: string;
    avoidMaterials?: string[];
    preferMaterials?: string[];
    otherRequirements?: string;
  };
  conversationHistory?: string;
}

export function buildGameDirectionsPrompt(params: GameDirectionsPromptParams): string {
  const {
    childProfile,
    latestAssessment,
    interestDetails,
    abilityDetails,
    highInterests,
    lowAbilities,
    recentGames,
    userPreferences,
    conversationHistory
  } = params;

  // 构建最近游戏历史信息
  let recentGamesText = '';
  if (recentGames.length > 0) {
    recentGamesText = `
【最近实施的游戏】
${recentGames.map((g: any) => `- ${g.title}（${g.category}，${g.implementedDate}）`).join('\n')}

⚠️ 重要：为了提供多样化的体验，请避免推荐与最近游戏相同类型的方向。尝试推荐不同的游戏类型和训练目标。
`;
  }

  // 构建用户偏好说明
  let preferencesText = '';
  if (userPreferences) {
    const prefs = [];
    
    if (userPreferences.environment && userPreferences.environment !== 'any') {
      const envMap: Record<string, string> = {
        'indoor': '室内',
        'outdoor': '户外',
        'both': '室内或户外都可以'
      };
      prefs.push(`🏠 环境：${envMap[userPreferences.environment] || userPreferences.environment}`);
    }
    
    if (userPreferences.duration && userPreferences.duration !== 'any') {
      const durationMap: Record<string, string> = {
        'short': '短时间（10分钟内）',
        'medium': '中等时长（10-20分钟）',
        'long': '长时间（20分钟以上）'
      };
      prefs.push(`⏱️ 时长：${durationMap[userPreferences.duration] || userPreferences.duration}`);
    }
    
    if (userPreferences.avoidMaterials && userPreferences.avoidMaterials.length > 0) {
      prefs.push(`🚫 避免材料：${userPreferences.avoidMaterials.join('、')}`);
    }
    
    if (userPreferences.preferMaterials && userPreferences.preferMaterials.length > 0) {
      prefs.push(`✅ 偏好材料：${userPreferences.preferMaterials.join('、')}`);
    }
    
    if (userPreferences.otherRequirements) {
      prefs.push(`💡 其他要求：${userPreferences.otherRequirements}`);
    }
    
    if (prefs.length > 0) {
      preferencesText = `
【用户偏好】
${prefs.join('\n')}

⚠️ 重要：推荐的游戏方向必须符合这些偏好！如果用户要求避免某些材料，绝对不要推荐需要这些材料的游戏。
`;
    }
  }

  // 如果没有评估，使用基础信息
  const assessmentInfo = latestAssessment 
    ? `
【当前画像】
${latestAssessment.currentProfile}

【最新评估】
评估摘要：${latestAssessment.summary}
下一步建议：${latestAssessment.nextStepSuggestion}
`
    : `
【当前画像】
这是${childProfile.name}的首次使用，我们将根据基础信息和初步观察来推荐游戏方向。
`;

  const conversationContext = conversationHistory 
    ? `
【对话历史】
${conversationHistory}

请结合对话历史中用户的需求和反馈来生成游戏方向。
`
    : '';

  return `
${preferencesText}
${recentGamesText}
${conversationContext}

请为以下儿童生成3个游戏方向建议（只要3个，不要太多）：

【基本信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childProfile.birthDate ? `${new Date().getFullYear() - new Date(childProfile.birthDate).getFullYear()}岁` : '未知'}
${assessmentInfo}

【兴趣维度详细数据】
${interestDetails || '暂无数据'}

【能力维度详细数据】
${abilityDetails || '暂无数据'}

【分析要点】
- 高兴趣维度（可作为切入点）：${highInterests.length > 0 ? highInterests.join(', ') : '暂无明显高兴趣'}
- 需要提升的能力维度：${lowAbilities.length > 0 ? lowAbilities.join(', ') : '整体均衡'}

${!latestAssessment ? '注意：这是首次使用，请基于基础信息和通用的ASD儿童发展需求来推荐游戏方向。' : ''}

重要要求：
1. 只生成3个方向，不要太多
2. 推荐理由要充实但简洁（2-3句话）：
   - 第一句：说明为什么适合这个年龄/性别的孩子
   - 第二句：说明这个方向的特点和吸引力
   - 第三句（可选）：说明对孩子发展的好处
3. 如果所有维度都是50分（初始数据），基于年龄和性别推荐通用但实用的方向
4. 方向名称要具体（如"玩水游戏"而不是"感官探索小达人"）
5. 目标要明确具体（如"锻炼手眼协调和身体追踪能力"）
6. 场景描述要实用（如"室内或阳台，10-15分钟"）

请生成3个游戏方向，每个方向包含：
1. name: 方向名称（具体实际，如"玩水游戏"、"搭积木"、"追泡泡"）
2. reason: 推荐理由（2-3句话，充实但不冗长）
3. goal: 预期目标（明确具体，如"锻炼手眼协调和身体追踪能力"）
4. scene: 适合场景（实用，如"室内或阳台，10-15分钟"）

返回 JSON 格式：
{
  "directions": [
    {
      "name": "具体游戏方向名称",
      "reason": "简短实际的理由（1-2句话）",
      "goal": "简短的目标",
      "scene": "简短的场景描述"
    }
  ]
}
`;
}
