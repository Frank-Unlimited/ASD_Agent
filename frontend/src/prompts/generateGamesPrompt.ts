/**
 * LLM 生成游戏概要的 Prompt 模板
 */

import { ChildProfile, ComprehensiveAssessment, GameDirection } from '../types';

export interface GenerateGamesPromptParams {
  direction: GameDirection;
  childProfile: ChildProfile;
  latestAssessment: ComprehensiveAssessment | null;
  count: number;
  additionalRequirements?: string;
  conversationHistory?: string;
}

export function buildGenerateGamesPrompt(params: GenerateGamesPromptParams): string {
  const {
    direction,
    childProfile,
    latestAssessment,
    count,
    additionalRequirements,
    conversationHistory
  } = params;

  const conversationContext = conversationHistory 
    ? `
【对话历史】
${conversationHistory}

请结合对话历史中用户的需求和反馈来设计游戏。
`
    : '';

  return `
${conversationContext}

【工作流程】
请先在内心总结收集到的关键信息（游戏方向、孩子情况、特殊要求、对话历史等），然后基于这些信息设计 ${count} 个原创游戏概要。

系统会自动提取你的分析过程，确保游戏设计充分考虑了所有信息。

---

请为以下儿童设计 ${count} 个原创的 DIR/Floortime 地板游戏概要（只需要概要，不需要详细步骤）：

【游戏方向】
方向名称：${direction.name}
训练目标：${direction.goal}
适合场景：${direction.scene}
推荐理由：${direction.reason}

【儿童信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childProfile.birthDate ? `${new Date().getFullYear() - new Date(childProfile.birthDate).getFullYear()}岁` : '未知'}
${latestAssessment ? `
当前画像：${latestAssessment.currentProfile}
评估摘要：${latestAssessment.summary}
` : '首次使用，请基于年龄和性别设计通用游戏'}

${additionalRequirements ? `
【特殊要求】
${additionalRequirements}
⚠️ 重要：设计的游戏必须完全符合这些要求！
` : ''}

【设计要求】
1. 游戏必须原创，不要复制现有游戏
2. 游戏必须符合 DIR/Floortime 理念（以儿童兴趣为起点，促进互动）
3. 只需要提供游戏概要，不需要详细步骤（详细步骤会在后续细化）
4. 提供3-5个关键要点（简短的步骤提示，每个10-15字）
5. 游戏要适合家庭环境，材料易获取
6. 如果有特殊要求，必须严格遵守

请设计 ${count} 个游戏概要，返回 JSON 格式：

【返回格式要求】
系统会使用 JSON Schema 强制结构化输出，你需要返回包含以下字段的 JSON 对象：

1. analysis（分析总结）：
   - 一段简短的话（50-80字）
   - 总结你收集到的关键信息：选定的游戏方向、孩子的具体情况、用户的特殊要求、对话历史中的关键信息
   - 说明基于这些信息的游戏设计思路
   - 例如："基于'触觉探索'方向，小明6岁喜欢动手操作，家长要求材料简单、时长10分钟内。设计3个触觉丰富、易上手、互动性强的游戏。"

2. games（游戏列表）：
   - title: 游戏名称（简洁有趣）
   - target: 训练目标（如：提升手眼协调和社交互动能力）
   - duration: 游戏时长（如：10-15分钟）
   - reason: 为什么这个游戏适合${childProfile.name}（结合孩子的具体情况，2-3句话）
   - summary: 游戏玩法概要（2-3句话描述游戏的核心玩法和流程）
   - materials: 所需材料数组
   - keyPoints: 关键要点数组（每个10-15字）

注意：analysis 会直接显示给用户，让他们了解你的分析过程。只需要概要信息，不要详细步骤。
`;
}
