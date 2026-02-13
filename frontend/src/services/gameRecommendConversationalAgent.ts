/**
 * Game Recommendation Conversational Agent
 * 游戏推荐协商式对话 Agent
 * 
 * 采用三阶段对话流程：
 * 1. 需求探讨（Discussing）：分析档案，提出3-5个游戏方向
 * 2. 方案细化（Designing）：检索候选游戏，提供详细说明
 * 3. 实施确认（Confirming）：生成完整实施方案，等待确认
 */

import { qwenStreamClient } from './qwenStreamClient';
import { searchGamesHybrid } from './ragService';
import { 
  GameDirection, 
  CandidateGame, 
  GameImplementationPlan,
  ChildProfile,
  ComprehensiveAssessment,
  HistoricalDataSummary,
  Game
} from '../types';

const CONVERSATIONAL_SYSTEM_PROMPT = `
你是一位温暖、专业的 DIR/Floortime 游戏推荐专家。

重要：游戏推荐采用"协商式对话"流程，分为3个阶段：

阶段1 - 需求探讨（纯文字对话）：
- 当用户提出游戏推荐需求时，先分析孩子档案
- 提出3-5个游戏方向，每个方向包含：方向名称、推荐理由、预期目标、适合场景
- 理由必须结合孩子的兴趣维度（高分维度作为切入点）和能力维度（低分维度作为目标）
- 必须引用具体的维度分数（如"辰辰的Visual维度82分，说明视觉兴趣很强"）
- 用自然语言讨论，不显示卡片
- 使用温暖鼓励的语气，询问家长倾向哪个方向
- 如果家长对推荐的方向不满意，要倾听家长的具体需求和顾虑，然后调整推荐

阶段2 - 方案细化（纯文字对话）：
- 家长选择方向后，从游戏库检索3-5个候选游戏
- 为每个游戏提供：名称、玩法概述、个性化理由、材料、时长难度、挑战应对
- 用自然语言介绍，不显示卡片
- 使用表情符号和清晰的格式，让信息易于阅读
- 询问家长选择哪个游戏或需要调整
- 如果家长不满意，询问具体原因（时长？难度？材料？），然后调整推荐

阶段3 - 生成游戏卡片：
- 家长选择具体游戏后，生成完整实施方案
- 这时才显示游戏卡片，包含：详细步骤（准备-游戏-结束）、家长指导、预期效果、问题应对
- 使用编号和清晰的结构，方便家长理解
- 询问是否开始实施
- 如果家长有顾虑，提供调整建议或替代方案

灵活对话：
- 家长可以随时提出自己的想法和需求
- 如果家长说"都不太合适"、"有没有其他的"等，要询问具体原因，然后提供新的建议
- 如果家长描述了具体需求（如"想要户外的"、"时间短一点的"），要根据需求重新推荐
- 保持对话的连贯性，不要只依赖按钮交互

记住：
- 前两个阶段都是纯文字对话，不显示卡片
- 只有第三阶段才显示游戏卡片
- 理由必须个性化，引用孩子的具体数据（如"{孩子名}的Visual维度82分"）
- 语气温暖鼓励，避免说教
- 使用表情符号增加亲和力（🎯 🎮 👨‍👩‍👧 🔧 等）
- 要能灵活应对家长的各种反馈，不只是等待按钮点击
`;

/**
 * 阶段1：生成游戏方向建议
 */
export const generateGameDirections = async (
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment | null,
  historicalData: HistoricalDataSummary,
  userPreferences?: {
    environment?: string;
    duration?: string;
    avoidMaterials?: string[];
    preferMaterials?: string[];
    otherRequirements?: string;
  },
  conversationHistory?: string
): Promise<GameDirection[]> => {
  try {
    // 获取所有兴趣维度的详细数据
    const interestDetails = Object.entries(historicalData.interestTrends)
      .map(([dim, score]) => `${dim}: ${score.toFixed(0)}分`)
      .join(', ');
    
    // 获取所有能力维度的详细数据
    const abilityDetails = Object.entries(historicalData.abilityTrends)
      .map(([dim, score]) => `${dim}: ${score.toFixed(0)}分`)
      .join(', ');
    
    // 识别高兴趣维度（作为切入点）
    const highInterests = Object.entries(historicalData.interestTrends)
      .filter(([_, score]) => score > 60)
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([dim, score]) => `${dim}(${score.toFixed(0)}分)`);
    
    // 识别低能力维度（作为提升目标）
    const lowAbilities = Object.entries(historicalData.abilityTrends)
      .filter(([_, score]) => score < 50)
      .sort(([, a], [, b]) => a - b)
      .slice(0, 3)
      .map(([dim, score]) => `${dim}(${score.toFixed(0)}分)`);

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

    const prompt = `
${preferencesText}
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

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 1500
      }
    );

    // 提取 JSON
    let jsonContent = response;
    const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      jsonContent = jsonMatch[1];
    }

    const data = JSON.parse(jsonContent);
    return data.directions || [];
  } catch (error) {
    console.error('Generate Game Directions Failed:', error);
    return [];
  }
};

/**
 * 阶段2：检索候选游戏（混合策略：检索 + 生成）
 */
export const searchCandidateGames = async (
  direction: GameDirection,
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment | null,
  count: number = 3,
  additionalRequirements?: string,  // 新增：额外要求
  conversationHistory?: string
): Promise<CandidateGame[]> => {
  try {
    let candidateGames: CandidateGame[] = [];
    
    // 步骤1：先从游戏库检索
    console.log('[Hybrid Strategy] 步骤1：从游戏库检索...');
    try {
      const searchQuery = `${direction.name} ${direction.goal} 自闭症儿童 地板游戏`;
      const childContext = `
儿童：${childProfile.name}
${latestAssessment ? `当前画像：${latestAssessment.currentProfile}` : '首次使用'}
游戏方向：${direction.name}
目标：${direction.goal}
${additionalRequirements ? `额外要求：${additionalRequirements}` : ''}
`;

      const games = await searchGamesHybrid(searchQuery, childContext, count);
      
      // 转换为候选游戏格式
      candidateGames = games.map((game) => {
        const mainSteps = game.steps.slice(0, 3).map(s => s.instruction).join('，');
        const abilities = game.target || direction.goal;
        const description = `${mainSteps}。能锻炼${abilities}。`;
        
        return {
          id: game.id,
          title: game.title,
          summary: mainSteps,
          reason: description,
          materials: extractMaterials(game),
          duration: game.duration,
          difficulty: estimateDifficulty(game),
          challenges: generateChallenges(game),
          fullGame: game,
          source: 'library' as const  // 标记来源
        };
      });
      
      console.log(`[Hybrid Strategy] 从游戏库检索到 ${candidateGames.length} 个游戏`);
    } catch (error) {
      console.warn('[Hybrid Strategy] 游戏库检索失败:', error);
    }
    
    // 步骤2：如果检索结果不足，或有特殊要求，调用 LLM 生成游戏
    const needGenerate = candidateGames.length < count || additionalRequirements;
    
    if (needGenerate) {
      const generateCount = Math.max(1, count - candidateGames.length);
      console.log(`[Hybrid Strategy] 步骤2：LLM 生成 ${generateCount} 个游戏...`);
      
      try {
        const generatedGames = await generateGamesWithLLM(
          direction,
          childProfile,
          latestAssessment,
          generateCount,
          additionalRequirements,
          conversationHistory
        );
        
        console.log(`[Hybrid Strategy] LLM 生成了 ${generatedGames.length} 个游戏`);
        candidateGames = [...candidateGames, ...generatedGames];
      } catch (error) {
        console.warn('[Hybrid Strategy] LLM 生成游戏失败:', error);
      }
    }
    
    // 返回指定数量的候选游戏
    return candidateGames.slice(0, count);
  } catch (error) {
    console.error('Search Candidate Games Failed:', error);
    return [];
  }
};

/**
 * 使用 LLM 生成原创游戏
 */
async function generateGamesWithLLM(
  direction: GameDirection,
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment | null,
  count: number,
  additionalRequirements?: string,
  conversationHistory?: string
): Promise<CandidateGame[]> {
  try {
    const conversationContext = conversationHistory 
      ? `
【对话历史】
${conversationHistory}

请结合对话历史中用户的需求和反馈来设计游戏。
`
      : '';

    const prompt = `
${conversationContext}

请为以下儿童设计 ${count} 个原创的 DIR/Floortime 地板游戏：

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
3. 游戏步骤要具体可操作（至少5个步骤）
4. 每个步骤要包含家长引导要点
5. 游戏要适合家庭环境，材料易获取
6. 如果有特殊要求，必须严格遵守

请设计 ${count} 个游戏，返回 JSON 格式：
\`\`\`json
{
  "games": [
    {
      "title": "游戏名称（简洁有趣）",
      "target": "训练目标（如：提升手眼协调和社交互动能力）",
      "duration": "游戏时长（如：10-15分钟）",
      "reason": "为什么这个游戏适合${childProfile.name}（结合孩子的具体情况，2-3句话）",
      "materials": ["材料1", "材料2"],
      "steps": [
        {
          "instruction": "步骤1的具体操作",
          "guidance": "家长引导要点"
        },
        {
          "instruction": "步骤2的具体操作",
          "guidance": "家长引导要点"
        }
      ]
    }
  ]
}
\`\`\`

只返回 JSON，不要其他说明。
`;

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.8,  // 提高创造性
        max_tokens: 3000
      }
    );

    // 提取 JSON
    let jsonContent = response;
    const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      jsonContent = jsonMatch[1];
    } else {
      const arrayMatch = response.match(/\{[\s\S]*"games"[\s\S]*\}/);
      if (arrayMatch) {
        jsonContent = arrayMatch[0];
      }
    }

    const data = JSON.parse(jsonContent);
    
    if (!data.games || !Array.isArray(data.games)) {
      console.warn('LLM 返回的数据格式不正确');
      return [];
    }

    // 转换为 CandidateGame 格式
    const candidateGames: CandidateGame[] = data.games.map((game: any, index: number) => {
      const gameId = `generated_${Date.now()}_${index}`;
      const mainSteps = game.steps.slice(0, 3).map((s: any) => s.instruction).join('，');
      
      return {
        id: gameId,
        title: game.title,
        summary: mainSteps,
        reason: game.reason,
        materials: game.materials || extractMaterialsFromSteps(game.steps),
        duration: game.duration,
        difficulty: estimateDifficultyFromSteps(game.steps),
        challenges: [
          '孩子可能一开始不感兴趣 → 先观察，找到切入点',
          '孩子可能不理解规则 → 用视觉提示和示范',
          '孩子可能情绪激动 → 暂停游戏，先安抚情绪'
        ],
        fullGame: {
          id: gameId,
          title: game.title,
          target: game.target,
          duration: game.duration,
          reason: game.reason,
          isVR: false,
          steps: game.steps
        },
        source: 'generated' as const  // 标记来源
      };
    });

    return candidateGames;
  } catch (error) {
    console.error('Generate Games with LLM Failed:', error);
    return [];
  }
}

/**
 * 阶段3：生成游戏实施方案
 */
export const generateImplementationPlan = async (
  selectedGame: Game,
  childProfile: ChildProfile,
  latestAssessment: ComprehensiveAssessment | null,
  customizations: string[] = [],
  conversationHistory?: string
): Promise<GameImplementationPlan> => {
  try {
    const conversationContext = conversationHistory 
      ? `
【对话历史】
${conversationHistory}

请结合对话历史中用户的需求和反馈来生成实施方案。
`
      : '';

    const prompt = `
${conversationContext}

请为以下游戏生成完整的实施方案：

【游戏信息】
名称：${selectedGame.title}
目标：${selectedGame.target}
时长：${selectedGame.duration}
步骤：${selectedGame.steps.map((s, i) => `${i + 1}. ${s.instruction}`).join('\n')}

【儿童信息】
姓名：${childProfile.name}
${latestAssessment ? `当前画像：${latestAssessment.currentProfile}` : '首次使用'}

${customizations.length > 0 ? `【家长要求的调整】\n${customizations.join('\n')}` : ''}

请生成实施方案，包含：
1. steps: 游戏步骤（分为准备阶段、游戏阶段、结束阶段）
2. parentGuidance: 家长指导要点（3-5条）
3. expectedOutcome: 预期效果（3-5条）
4. troubleshooting: 问题应对（3-5个常见问题及解决方案）

返回 JSON 格式：
{
  "steps": [
    {
      "title": "准备阶段",
      "duration": "2分钟",
      "instructions": ["指令1", "指令2"]
    }
  ],
  "parentGuidance": ["要点1", "要点2"],
  "expectedOutcome": ["效果1", "效果2"],
  "troubleshooting": [
    {
      "problem": "问题描述",
      "solution": "解决方案"
    }
  ]
}
`;

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 2000
      }
    );

    // 提取 JSON
    let jsonContent = response;
    const jsonMatch = response.match(/```json\s*([\s\S]*?)\s*```/);
    if (jsonMatch) {
      jsonContent = jsonMatch[1];
    }

    const data = JSON.parse(jsonContent);
    return {
      gameId: selectedGame.id,
      ...data
    };
  } catch (error) {
    console.error('Generate Implementation Plan Failed:', error);
    throw error;
  }
};

// 辅助函数：从游戏中提取材料
function extractMaterials(game: Game): string[] {
  const materials: string[] = [];
  game.steps.forEach(step => {
    const instruction = step.instruction.toLowerCase();
    if (instruction.includes('积木')) materials.push('积木');
    if (instruction.includes('玩具车')) materials.push('玩具车');
    if (instruction.includes('卡片')) materials.push('卡片');
    if (instruction.includes('纸')) materials.push('纸张');
    if (instruction.includes('笔')) materials.push('笔');
  });
  return materials.length > 0 ? materials : ['根据游戏内容准备'];
}

// 辅助函数：从步骤中提取材料（用于 LLM 生成的游戏）
function extractMaterialsFromSteps(steps: any[]): string[] {
  const materials: string[] = [];
  steps.forEach(step => {
    const instruction = (step.instruction || '').toLowerCase();
    if (instruction.includes('积木')) materials.push('积木');
    if (instruction.includes('玩具车')) materials.push('玩具车');
    if (instruction.includes('卡片')) materials.push('卡片');
    if (instruction.includes('纸')) materials.push('纸张');
    if (instruction.includes('笔')) materials.push('笔');
    if (instruction.includes('水')) materials.push('水');
    if (instruction.includes('球')) materials.push('球');
    if (instruction.includes('泡泡')) materials.push('泡泡');
  });
  return materials.length > 0 ? materials : ['根据游戏内容准备'];
}

// 辅助函数：估算游戏难度
function estimateDifficulty(game: Game): number {
  const stepCount = game.steps.length;
  if (stepCount <= 3) return 2;
  if (stepCount <= 5) return 3;
  return 4;
}

// 辅助函数：从步骤数估算难度（用于 LLM 生成的游戏）
function estimateDifficultyFromSteps(steps: any[]): number {
  const stepCount = steps.length;
  if (stepCount <= 3) return 2;
  if (stepCount <= 5) return 3;
  return 4;
}

// 辅助函数：生成可能的挑战
function generateChallenges(game: Game): string[] {
  return [
    '孩子可能一开始不感兴趣 → 先观察，找到切入点',
    '孩子可能不理解规则 → 用视觉提示和示范',
    '孩子可能情绪激动 → 暂停游戏，先安抚情绪'
  ];
}
