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
  recentBehaviors?: any[];  // 新增：最近行为记录（可选，从 sessionStorage 读取）
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
    recentBehaviors,  // 新增
    recentGames,
    userPreferences,
    conversationHistory
  } = params;

  // 构建最近行为记录信息
  let recentBehaviorsText = '';
  if (recentBehaviors && recentBehaviors.length > 0) {
    recentBehaviorsText = `
【最近行为记录】（供参考，了解孩子最近的兴趣表现）
${recentBehaviors.slice(0, 5).map((b: any) => {
  const topDimensions = b.dimensions
    .sort((a: any, b: any) => b.weight - a.weight)
    .slice(0, 2)
    .map((d: any) => `${d.dimension}(关联${(d.weight * 100).toFixed(0)}%，强度${d.intensity > 0 ? '+' : ''}${d.intensity.toFixed(1)})`)
    .join('、');
  return `- ${b.behavior}（${b.date}）→ ${topDimensions}`;
}).join('\n')}

💡 提示：这些行为记录可以帮助你了解孩子最近的兴趣倾向，但不要局限于此，也可以尝试新的方向。
`;
  }

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

⚠️ 重要提示：
- 如果对话历史中显示用户说"换一批"、"再推荐"、"不喜欢这些"等，说明用户对之前的推荐不满意
- 请仔细查看对话历史中之前推荐过的游戏方向名称（如"积木合作搭桥"、"追泡泡游戏"、"颜色配对"等）
- 本次推荐必须完全不同，避免推荐相同或相似的方向
- 尝试从不同的兴趣维度、不同的游戏类型、不同的训练目标出发
- 例如：如果之前推荐了"积木"、"泡泡"、"颜色配对"，本次可以推荐"音乐节奏"、"角色扮演"、"感官探索"等完全不同的方向
`
    : '';

  return `
${preferencesText}
${recentBehaviorsText}
${recentGamesText}
${conversationContext}

【工作流程】
请先在内心总结收集到的关键信息（孩子情况、兴趣特点、能力水平、用户偏好、最近行为等），然后基于这些信息生成3个游戏方向建议。

系统会自动提取你的分析过程，确保推荐充分考虑了所有信息。

---

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
7. 🚨 **避免重复推荐**：
   - 如果对话历史中显示用户说"换一批"、"再推荐"、"不喜欢这些"，说明用户对之前的推荐不满意
   - 仔细查看对话历史，识别之前推荐过的游戏方向（如"积木"、"泡泡"、"颜色配对"等关键词）
   - 本次推荐必须完全不同，从不同的角度出发：
     * 如果之前推荐了"建构类"（积木、搭建），本次推荐"感官类"（触觉、听觉）或"运动类"（追逐、跳跃）
     * 如果之前推荐了"视觉类"（颜色、光影），本次推荐"社交类"（角色扮演、合作）或"认知类"（分类、配对）
     * 如果之前推荐了"静态游戏"，本次推荐"动态游戏"
   - 创造性地探索新的游戏类型，不要局限于常见的几种

请生成3个游戏方向，每个方向包含：
1. name: 方向名称（具体实际，如"玩水游戏"、"搭积木"、"追泡泡"）
2. reason: 推荐理由（2-3句话，充实但不冗长）
3. goal: 预期目标（明确具体，如"锻炼手眼协调和身体追踪能力"）
4. scene: 适合场景（实用，如"室内或阳台，10-15分钟"）

【返回格式要求】
系统会使用 JSON Schema 强制结构化输出，你需要返回包含以下字段的 JSON 对象：

1. analysis（分析总结）：
   - 一段简短的话（50-80字）
   - 总结你收集到的关键信息：孩子的基本情况、兴趣特点、能力水平、用户偏好、最近行为
   - 说明基于这些信息的推荐思路
   - 例如："小明是6岁男孩，触觉和运动兴趣突出（8分、11.5分），双向沟通能力需提升（40分），家长偏好室内短时游戏，最近喜欢玩积木。因此推荐结合触觉探索和互动沟通的方向。"

2. directions（游戏方向列表）：
   - name: 方向名称（具体实际，如"玩水游戏"、"搭积木"、"追泡泡"）
   - reason: 推荐理由（2-3句话，充实但不冗长）
   - goal: 预期目标（明确具体，如"锻炼手眼协调和身体追踪能力"）
   - scene: 适合场景（实用，如"室内或阳台，10-15分钟"）

注意：analysis 会直接显示给用户，让他们了解你的分析过程。
`;
}
