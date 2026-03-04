/**
 * 兴趣分析 Prompt 模板
 * 用于 analyze_interest 工具
 */

import { ChildProfile } from '../types';
import { DimensionMetrics } from '../services/historicalDataHelper';

export interface InterestAnalysisPromptParams {
  childProfile: ChildProfile;
  dimensionMetrics: DimensionMetrics[];
  parentContext?: string;
  memorySection?: string;
}

export function buildInterestAnalysisPrompt(params: InterestAnalysisPromptParams): string {
  const {
    childProfile,
    dimensionMetrics,
    parentContext,
    memorySection
  } = params;

  // 构建维度数据表
  const metricsTable = dimensionMetrics.map(m =>
    `${m.dimension}: 强度${m.strength}分, 探索度${m.exploration}分`
  ).join('\n');

  // 儿童信息
  const childAge = childProfile.birthDate
    ? `${new Date().getFullYear() - new Date(childProfile.birthDate).getFullYear()}岁`
    : '未知';

  return `
请基于以下数据，对${childProfile.name}的8个兴趣维度进行深度分析。

【儿童信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childAge}

${parentContext ? `【家长补充信息】\n${parentContext}\n` : ''}
${memorySection ? `【历史干预记忆】\n${memorySection}\n` : ''}
【维度量化数据】
强度（0-100）= 孩子对该维度的喜好程度；探索度（0-100）= 该维度被探索的深度和广度
${metricsTable}

【分类规则】
1. **leverage（可利用）**：强度 ≥ 60 —— 孩子已有明显兴趣，作为游戏切入点
2. **explore（可探索）**：强度 40-59 且 探索度 < 50 —— 有潜力但尚未充分探索
3. **neutral（中性）**：强度 40-59 且 探索度 ≥ 50 —— 有一定兴趣且已探索，暂无明显倾向
4. **avoid（应避免）**：强度 < 40 —— 孩子表现出低兴趣或抗拒

【输出要求】
1. 从行为记录中提取各维度的具体兴趣对象（如 specificObjects: ['画册', '彩色积木']）
2. summary 总结孩子整体兴趣特点（100-150字），引用具体数据，语气温暖鼓励
3. 若所有维度强度均为50分（初始默认值），说明数据不足，在 summary 中提示建议先记录更多行为
4. dimensions 数组必须包含全部8个维度：Visual, Auditory, Tactile, Motor, Construction, Order, Cognitive, Social
5. leverageDimensions / exploreDimensions / avoidDimensions 填入对应分类的维度名称
6. 干预建议3-5条，结合 leverage 和 explore 维度，每条包含目标维度、策略类型、具体建议、原理说明、活动举例

按以下 JSON 格式输出（示例，请填入实际数据）：

\`\`\`json
{
  "summary": "小明在视觉和建构方面表现出较强兴趣，尤其喜欢观察色彩和搭建积木...",
  "dimensions": [
    {
      "dimension": "Visual",
      "strength": 75,
      "exploration": 60,
      "category": "leverage",
      "specificObjects": ["画册", "彩色积木"],
      "reasoning": "小明经常主动寻找色彩鲜艳的物品，视觉强度75分，属于可利用维度"
    },
    {
      "dimension": "Auditory",
      "strength": 35,
      "exploration": 20,
      "category": "avoid",
      "specificObjects": [],
      "reasoning": "听觉强度较低，孩子对声音刺激有回避倾向"
    }
  ],
  "leverageDimensions": ["Visual", "Construction"],
  "exploreDimensions": ["Tactile"],
  "avoidDimensions": ["Auditory"],
  "interventionSuggestions": [
    {
      "targetDimension": "Visual",
      "strategy": "leverage",
      "suggestion": "利用小明对色彩的兴趣，引入颜色分类游戏",
      "rationale": "视觉维度是小明的优势领域，可以作为互动的切入点",
      "exampleActivities": ["彩色积木分类", "颜色配对卡片"]
    }
  ]
}
\`\`\`
`;
}
