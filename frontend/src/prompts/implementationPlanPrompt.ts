/**
 * 游戏实施方案生成的 Prompt 模板
 */

import { Game, ChildProfile, ComprehensiveAssessment } from '../types';

export interface ImplementationPlanPromptParams {
  selectedGame: Game;
  childProfile: ChildProfile;
  latestAssessment: ComprehensiveAssessment | null;
  customizations: string[];
  conversationHistory?: string;
}

export function buildImplementationPlanPrompt(params: ImplementationPlanPromptParams): string {
  const {
    selectedGame,
    childProfile,
    latestAssessment,
    customizations,
    conversationHistory
  } = params;

  const conversationContext = conversationHistory 
    ? `
【对话历史】
${conversationHistory}

请结合对话历史中用户的需求和反馈来生成实施方案。
`
    : '';

  // 构建儿童详细信息
  const childDetails = latestAssessment 
    ? `
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childProfile.birthDate ? `${new Date().getFullYear() - new Date(childProfile.birthDate).getFullYear()}岁` : '未知'}

【当前画像】
${latestAssessment.currentProfile}

【评估摘要】
${latestAssessment.summary}

【发展建议】
${latestAssessment.nextStepSuggestion}
`
    : `
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childProfile.birthDate ? `${new Date().getFullYear() - new Date(childProfile.birthDate).getFullYear()}岁` : '未知'}
（首次使用，请基于年龄和性别设计通用方案）
`;

  return `
${conversationContext}

【工作流程】
请先在内心总结收集到的关键信息（游戏概要、孩子情况、评估建议、特殊要求、对话历史等），然后基于这些信息设计详细的实施方案。

系统会自动提取你的分析过程，确保方案充分考虑了孩子的个性化需求。

---

你是一位经验丰富的 DIR/Floortime 游戏设计师。现在需要为以下游戏设计一套完整、详细、可操作的实施方案。

【游戏概要】
名称：${selectedGame.title}
训练目标：${selectedGame.target}
时长：${selectedGame.duration}
适合理由：${selectedGame.reason}
${selectedGame.summary ? `玩法概要：${selectedGame.summary}` : ''}
${selectedGame.materials && selectedGame.materials.length > 0 ? `所需材料：${selectedGame.materials.join('、')}` : ''}
${selectedGame.steps && selectedGame.steps.length > 0 ? `关键要点：\n${selectedGame.steps.map((s, i) => `${i + 1}. ${s.instruction}`).join('\n')}` : ''}

【儿童详细信息】
${childDetails}

${customizations.length > 0 ? `
【家长特殊要求】
${customizations.join('\n')}
⚠️ 重要：必须在设计中体现这些要求！
` : ''}

【任务要求】
请基于以上游戏概要，为 ${childProfile.name} 量身定制一套详细的实施方案。要求：

1. **游戏概要**：
   - 用2-3句话描述游戏的核心玩法和流程
   - 让家长快速理解游戏怎么玩

2. **游戏目标**：
   - 明确的训练目标（如"提升双向沟通能力和触觉感知能力"）
   - 结合孩子的具体发展需求

3. **详细步骤**（5-8个步骤）：
   - 每个步骤包含：步骤标题、详细指令、预期效果
   - 步骤标题：如"第一步：准备材料"、"第二步：引导孩子触摸"
   - 详细指令：家长应该做什么，要具体到动作和语言（2-3句话）
   - 预期效果：这一步期望达到什么效果（1-2句话）
   - 步骤要循序渐进，从简单到复杂
   - 考虑 ${childProfile.name} 的具体情况进行个性化调整

【返回格式】
系统会使用 JSON Schema 强制结构化输出，你需要返回包含以下字段的 JSON 对象：

1. analysis（分析总结）：
   - 一段简短的话（50-80字）
   - 总结你收集到的关键信息：游戏的核心内容、孩子的特点和发展需求、评估中的关键建议、家长的特殊要求、对话历史
   - 说明基于这些信息的实施方案设计思路
   - 例如："为'触觉沙盘探索'设计方案。小明6岁，触觉兴趣强但双向沟通弱，评估建议增加互动环节，家长要求简化步骤。因此设计分阶段引导、强调亲子对话的详细方案。"

2. gameTitle（游戏名称）：游戏的名称

3. summary（游戏概要）：2-3句话描述游戏的核心玩法和流程

4. goal（游戏目标）：明确的训练目标

5. steps（游戏步骤）：5-8个详细步骤，每个步骤包含：
   - stepTitle：步骤标题（如"第一步：准备材料"）
   - instruction：详细指令（家长应该做什么，2-3句话）
   - expectedOutcome：预期效果（这一步期望达到什么效果，1-2句话）

重要提示：
- analysis 会直接显示给用户，让他们了解你的分析过程
- 步骤要详细到家长可以直接执行，不要模糊的描述
- 要结合 ${childProfile.name} 的具体情况进行个性化设计
- 语言要温暖、鼓励、易懂
- 每个指令要包含具体的动作、语言、时机
- 步骤要循序渐进，从简单到复杂
`;
}
