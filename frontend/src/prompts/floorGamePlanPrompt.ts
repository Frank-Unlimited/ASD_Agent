/**
 * 地板游戏计划 Prompt 模板
 * 用于 plan_floor_game 工具
 */

import { ChildProfile, InterestDimensionType } from '../types';

export interface FloorGamePlanPromptParams {
  childProfile: ChildProfile;
  targetDimensions: InterestDimensionType[];
  strategy: 'leverage' | 'explore' | 'mixed';
  parentPreferences?: {
    environment?: string;
    duration?: string;
    otherRequirements?: string;
  };
  conversationHistory?: string;
  searchResults?: string; // RAG 搜索结果
  specificObjects?: Record<string, string[]>; // 维度→具体对象
  memorySection?: string;
}

export function buildFloorGamePlanPrompt(params: FloorGamePlanPromptParams): string {
  const {
    childProfile,
    targetDimensions,
    strategy,
    parentPreferences,
    conversationHistory,
    searchResults,
    specificObjects,
    memorySection
  } = params;

  const childAge = childProfile.birthDate
    ? `${new Date().getFullYear() - new Date(childProfile.birthDate).getFullYear()}岁`
    : '未知';

  // 家长偏好
  let prefsText = '';
  if (parentPreferences) {
    const prefs = [];
    if (parentPreferences.environment && parentPreferences.environment !== 'any') {
      const envMap: Record<string, string> = { indoor: '室内', outdoor: '户外', both: '都可以' };
      prefs.push(`环境：${envMap[parentPreferences.environment] || parentPreferences.environment}`);
    }
    if (parentPreferences.duration && parentPreferences.duration !== 'any') {
      const durMap: Record<string, string> = { short: '10分钟内', medium: '10-20分钟', long: '20分钟以上' };
      prefs.push(`时长：${durMap[parentPreferences.duration] || parentPreferences.duration}`);
    }
    if (parentPreferences.otherRequirements) {
      prefs.push(`其他：${parentPreferences.otherRequirements}`);
    }
    if (prefs.length > 0) {
      prefsText = `\n【家长偏好】\n${prefs.join('\n')}\n`;
    }
  }

  // 孩子感兴趣的具体对象
  let specificObjectsText = '';
  if (specificObjects && Object.keys(specificObjects).length > 0) {
    const lines = Object.entries(specificObjects)
      .filter(([, objs]) => objs.length > 0)
      .map(([dim, objs]) => `${dim}：${objs.join('、')}`);
    if (lines.length > 0) {
      specificObjectsText = `\n【孩子感兴趣的具体对象】\n${lines.join('\n')}\n`;
    }
  }

  const strategyMap: Record<string, string> = {
    leverage: '利用已有兴趣作为切入点，在游戏中融入训练目标',
    explore: '引导孩子探索较少接触的维度，拓展兴趣范围',
    mixed: '结合利用已有兴趣和探索新维度的混合策略'
  };

  const conversationContext = conversationHistory
    ? `【对话历史】\n${conversationHistory}\n请结合对话中家长的需求和反馈来设计游戏。\n\n`
    : '';

  const searchContext = searchResults
    ? `【参考游戏资料】（来自联网搜索和游戏库）\n${searchResults}\n请参考以上资料，但必须为${childProfile.name}量身定制。\n\n`
    : '';

  return `
${conversationContext}${searchContext}请为以下儿童设计一套完整的地板游戏实施方案。

【儿童信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childAge}
${memorySection ? `\n【历史游戏记忆】\n${memorySection}\n` : ''}${prefsText}${specificObjectsText}
【干预目标】
目标维度：${targetDimensions.join('、')}
策略：${strategyMap[strategy]}

【设计要求】
1. 基于 DIR/Floortime 理念（跟随儿童兴趣，促进双向互动）
2. 设计4-6个循序渐进的步骤，从准备到结束完整覆盖
3. 每个步骤包含：家长具体操作指引（instruction）和互动要点/注意事项（guidance）
4. 针对${childProfile.name}的具体情况个性化调整
5. 材料易获取，适合家庭环境，优先使用孩子已感兴趣的对象
6. 游戏有趣、互动性强，避免机械训练

按以下 JSON 格式输出（示例，请填入实际数据）：

\`\`\`json
{
  "_analysis": "基于小明对视觉色彩的强烈兴趣，设计以彩色泡泡为媒介的互动游戏，在追泡泡过程中自然融入触觉探索...",
  "materials": ["泡泡液", "泡泡棒", "彩色毛巾"],
  "gameTitle": "彩虹泡泡追逐",
  "summary": "通过彩色泡泡吸引孩子注意力，在追逐和触碰泡泡的过程中促进视觉追踪和触觉探索，同时增进亲子互动。",
  "goal": "利用视觉兴趣作为切入点，在自然互动中发展触觉感知和双向社交沟通能力",
  "steps": [
    {
      "stepTitle": "准备材料和环境",
      "instruction": "准备彩色泡泡液和泡泡棒，选择光线充足的室内空间，坐在孩子对面，保持轻松愉快的氛围。",
      "guidance": "环境不要过于嘈杂，提前移开容易分散注意力的玩具。"
    },
    {
      "stepTitle": "吹出第一串泡泡",
      "instruction": "慢慢吹出几个大泡泡，用夸张的语气说"哇，看！泡泡来啦！"观察孩子的视觉追踪反应。",
      "guidance": "先观察孩子的反应，不要急于引导，跟随孩子目光的方向移动泡泡。"
    }
  ]
}
\`\`\`
`;
}
