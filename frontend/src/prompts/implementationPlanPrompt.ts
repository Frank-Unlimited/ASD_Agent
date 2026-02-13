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

1. **深度细化游戏步骤**：
   - 将游戏分为三个阶段：准备阶段（2-3分钟）、游戏阶段（主体部分）、结束阶段（2-3分钟）
   - 每个阶段包含3-5个具体、可操作的指令
   - 每个指令要详细到家长可以直接照着做
   - 考虑 ${childProfile.name} 的具体情况进行个性化调整

2. **家长指导要点**（4-6条）：
   - 如何观察孩子的反应
   - 如何调整互动节奏
   - 如何鼓励和引导
   - 注意事项和安全提示

3. **预期效果**（3-5条）：
   - 具体可观察的行为改善
   - 能力提升的表现
   - 短期和长期效果

4. **问题应对**（4-6个常见问题）：
   - 孩子可能出现的各种反应
   - 每个问题的具体解决方案
   - 如何灵活调整游戏

【返回格式】
请严格按照以下 JSON 格式返回：

\`\`\`json
{
  "steps": [
    {
      "title": "准备阶段",
      "duration": "2-3分钟",
      "instructions": [
        "详细指令1（要具体到动作和语言）",
        "详细指令2",
        "详细指令3"
      ]
    },
    {
      "title": "游戏阶段",
      "duration": "8-10分钟",
      "instructions": [
        "详细指令1",
        "详细指令2",
        "详细指令3",
        "详细指令4",
        "详细指令5"
      ]
    },
    {
      "title": "结束阶段",
      "duration": "2-3分钟",
      "instructions": [
        "详细指令1",
        "详细指令2",
        "详细指令3"
      ]
    }
  ],
  "parentGuidance": [
    "指导要点1（具体可操作）",
    "指导要点2",
    "指导要点3",
    "指导要点4"
  ],
  "expectedOutcome": [
    "预期效果1（具体可观察）",
    "预期效果2",
    "预期效果3"
  ],
  "troubleshooting": [
    {
      "problem": "孩子可能出现的问题1",
      "solution": "详细的解决方案1"
    },
    {
      "problem": "孩子可能出现的问题2",
      "solution": "详细的解决方案2"
    },
    {
      "problem": "孩子可能出现的问题3",
      "solution": "详细的解决方案3"
    },
    {
      "problem": "孩子可能出现的问题4",
      "solution": "详细的解决方案4"
    }
  ]
}
\`\`\`

重要提示：
- 步骤要详细到家长可以直接执行，不要模糊的描述
- 要结合 ${childProfile.name} 的具体情况进行个性化设计
- 语言要温暖、鼓励、易懂
- 每个指令要包含具体的动作、语言、时机
`;
}
