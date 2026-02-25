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
你是一位专业的 DIR/Floortime 儿童发展分析师。请基于以下数据，对孩子的8个兴趣维度进行深度分析。

【儿童信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${childAge}

${parentContext ? `【家长补充信息】\n${parentContext}\n` : ''}
${memorySection ? `【历史干预记忆（graphiti 提取，含历史行为偏好与维度变化）】\n${memorySection}\n` : ''}
【维度量化数据】（强度=孩子对该维度的喜好程度0-100, 探索度=该维度被探索的深度和广度0-100）
${metricsTable}

【分析规则】
请对每个维度进行分类：
1. **leverage（可利用）**：强度 ≥ 60 —— 孩子已有明显兴趣，可以作为游戏切入点
2. **explore（可探索）**：强度 40-59 且 探索度 < 50 —— 尚未充分探索，有潜力可以发展
3. **avoid（应避免）**：强度 < 40 或 (探索度 ≥ 50 且 强度 < 50) —— 孩子表现出抗拒或已探索但无兴趣
4. **neutral（中性）**：其他情况 —— 暂无明显倾向

【重要要求】
1. 从行为记录中提取具体对象（如"视觉维度喜欢画册"→ specificObjects=['画册']）
2. 干预建议要结合 leverage 和 explore 维度，给出3-5条具体可操作的建议
3. 每条建议包含：目标维度、策略类型、具体建议、原理说明、活动举例
4. summary 要总结孩子的整体兴趣特点（100-150字）
5. 如果所有维度强度都是50分（初始数据），说明数据不足，建议先记录更多行为
6. dimensions 数组必须包含全部8个维度的分析
7. leverageDimensions/exploreDimensions/avoidDimensions 必须包含对应分类的维度名称

请严格按照以下 JSON 格式输出（这是示例，请根据实际数据填写）：

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

注意：dimensions 数组必须包含全部8个维度（Visual, Auditory, Tactile, Motor, Construction, Order, Cognitive, Social），不能遗漏。
`;
}
