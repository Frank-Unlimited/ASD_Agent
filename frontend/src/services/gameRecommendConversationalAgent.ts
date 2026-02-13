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
import {
  CONVERSATIONAL_SYSTEM_PROMPT,
  buildGameDirectionsPrompt,
  buildGenerateGamesPrompt,
  buildImplementationPlanPrompt
} from '../prompts';

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
    // TODO: 查询最近的地板游戏实施数据（只查询已实施的）
    // 用于避免重复推荐相同类型的游戏，提供更多样化的建议
    // 数据结构示例：
    // const recentGames = await getRecentImplementedGames(childProfile.id, 5);
    // recentGames = [
    //   { title: "彩虹手指画", category: "感官探索", implementedDate: "2024-01-15" },
    //   { title: "积木高塔", category: "建构游戏", implementedDate: "2024-01-14" }
    // ]
    const recentGames: any[] = []; // 暂时为空，等待数据接口
    
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

    const prompt = buildGameDirectionsPrompt({
      childProfile,
      latestAssessment,
      historicalData,
      interestDetails,
      abilityDetails,
      highInterests,
      lowAbilities,
      recentGames,
      userPreferences,
      conversationHistory
    });

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
  count: number = 3,
  additionalRequirements?: string,
  conversationHistory?: string
): Promise<CandidateGame[]> => {
  try {
    // 从 sessionStorage 读取上下文信息
    const contextStr = sessionStorage.getItem('game_recommendation_context');
    if (!contextStr) {
      console.error('[searchCandidateGames] 未找到游戏推荐上下文');
      throw new Error('未找到游戏推荐上下文，请先调用 suggest_game_directions');
    }
    
    const context = JSON.parse(contextStr);
    const childProfile = context.childProfile;
    const latestAssessment = context.latestAssessment;
    
    console.log('[searchCandidateGames] 从 sessionStorage 读取上下文:', {
      childName: childProfile?.name,
      hasAssessment: !!latestAssessment
    });
    
    let candidateGames: CandidateGame[] = [];
    
    // 步骤1：先从联网搜索获取游戏概要
    console.log('[Hybrid Strategy] 步骤1：联网搜索游戏概要...');
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
      
      // 转换为候选游戏格式（只保留概要信息）
      candidateGames = games.map((game) => {
        // 使用 summary 字段（如果有），否则从关键要点生成概要
        const summary = game.summary || 
          (game.steps.length > 0 
            ? game.steps.slice(0, 3).map(s => s.instruction).join('，') 
            : '暂无概要');
        
        // 使用 reason 字段作为适合理由
        const reason = game.reason || `适合${childProfile.name}的${direction.name}训练`;
        
        // 提取材料
        const materials = game.materials || extractMaterials(game);
        
        return {
          id: game.id,
          title: game.title,
          summary: summary, // 游戏玩法概要
          reason: reason, // 适合理由
          materials: materials, // 所需材料
          duration: game.duration,
          difficulty: estimateDifficulty(game),
          challenges: generateChallenges(game),
          fullGame: game, // 保存完整游戏对象（包含关键要点，但不是详细步骤）
          source: 'online' as const  // 标记来源
        };
      });
      
      console.log(`[Hybrid Strategy] 联网搜索到 ${candidateGames.length} 个游戏概要`);
    } catch (error) {
      console.warn('[Hybrid Strategy] 联网搜索失败:', error);
    }
    
    // 步骤2：如果检索结果不足，或有特殊要求，调用 LLM 生成游戏概要
    const needGenerate = candidateGames.length < count || additionalRequirements;
    
    if (needGenerate) {
      const generateCount = Math.max(1, count - candidateGames.length);
      console.log(`[Hybrid Strategy] 步骤2：LLM 生成 ${generateCount} 个游戏概要...`);
      
      try {
        const generatedGames = await generateGamesWithLLM(
          direction,
          generateCount,
          additionalRequirements,
          conversationHistory
        );
        
        console.log(`[Hybrid Strategy] LLM 生成了 ${generatedGames.length} 个游戏概要`);
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
  count: number,
  additionalRequirements?: string,
  conversationHistory?: string
): Promise<CandidateGame[]> {
  try {
    // 从 sessionStorage 读取上下文信息
    const contextStr = sessionStorage.getItem('game_recommendation_context');
    if (!contextStr) {
      console.error('[generateGamesWithLLM] 未找到游戏推荐上下文');
      throw new Error('未找到游戏推荐上下文');
    }
    
    const context = JSON.parse(contextStr);
    const childProfile = context.childProfile;
    const latestAssessment = context.latestAssessment;
    const conversationContext = conversationHistory 
      ? `
【对话历史】
${conversationHistory}

请结合对话历史中用户的需求和反馈来设计游戏。
`
      : '';

    const prompt = `
${conversationContext}

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
\`\`\`json
{
  "games": [
    {
      "title": "游戏名称（简洁有趣）",
      "target": "训练目标（如：提升手眼协调和社交互动能力）",
      "duration": "游戏时长（如：10-15分钟）",
      "reason": "为什么这个游戏适合${childProfile.name}（结合孩子的具体情况，2-3句话）",
      "summary": "游戏玩法概要（2-3句话描述游戏的核心玩法和流程）",
      "materials": ["材料1", "材料2", "材料3"],
      "keyPoints": [
        "关键要点1（10-15字）",
        "关键要点2",
        "关键要点3",
        "关键要点4",
        "关键要点5"
      ]
    }
  ]
}
\`\`\`

只返回 JSON，不要其他说明。注意：只需要概要信息，不要详细步骤。
`;

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.8,  // 提高创造性
        max_tokens: 2000
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
      
      // 将 keyPoints 转换为简单的步骤格式（用于临时存储）
      const keyPoints = game.keyPoints || [];
      const steps = keyPoints.map((point: string) => ({
        instruction: point,
        guidance: '' // 概要阶段不需要详细引导
      }));
      
      return {
        id: gameId,
        title: game.title,
        summary: game.summary || keyPoints.slice(0, 3).join('，'),
        reason: game.reason,
        materials: game.materials || [],
        duration: game.duration,
        difficulty: estimateDifficultyFromSteps(keyPoints),
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
          steps: steps, // 只保存关键要点，不是详细步骤
          summary: game.summary,
          materials: game.materials
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
  customizations: string[] = [],
  conversationHistory?: string
): Promise<GameImplementationPlan> => {
  try {
    // 从 sessionStorage 读取上下文信息
    const contextStr = sessionStorage.getItem('game_recommendation_context');
    if (!contextStr) {
      console.error('[generateImplementationPlan] 未找到游戏推荐上下文');
      throw new Error('未找到游戏推荐上下文，请先调用 suggest_game_directions');
    }
    
    const context = JSON.parse(contextStr);
    const childProfile = context.childProfile;
    const latestAssessment = context.latestAssessment;
    
    console.log('[generateImplementationPlan] 从 sessionStorage 读取上下文:', {
      childName: childProfile?.name,
      hasAssessment: !!latestAssessment
    });
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

    const prompt = `
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

    const response = await qwenStreamClient.chat(
      [
        { role: 'system', content: CONVERSATIONAL_SYSTEM_PROMPT },
        { role: 'user', content: prompt }
      ],
      {
        temperature: 0.7,
        max_tokens: 3000 // 增加 token 限制以支持更详细的内容
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
