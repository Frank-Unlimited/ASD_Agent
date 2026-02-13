/**
 * 联网搜索游戏的 Prompt 模板
 */

export function buildSearchGamesPrompt(query: string, childContext: string): string {
  return `
请从互联网搜索适合自闭症儿童的 DIR/Floortime 地板游戏，要求：

【搜索条件】
${query}

${childContext ? `【儿童情况】\n${childContext}\n` : ''}

【要求】
1. 搜索适合自闭症儿童的地板游戏、感统游戏、互动游戏
2. 游戏应该基于 DIR/Floortime 理念
3. 游戏应该有明确的训练目标
4. 只需要提供游戏的大致玩法概要，不需要详细步骤（详细步骤会在后续细化）

【返回格式】
请以 JSON 数组格式返回，每个游戏包含：
- title: 游戏名称
- target: 训练目标
- duration: 游戏时长
- reason: 适合理由（结合儿童情况说明为什么适合）
- summary: 游戏玩法概要（2-3句话描述游戏的核心玩法和流程）
- materials: 所需材料列表
- keyPoints: 3-5个关键要点（简短的步骤提示，每个10-15字）

示例：
\`\`\`json
[
  {
    "title": "彩虹手指画冒险",
    "target": "感官整合、情绪调节",
    "duration": "10-15分钟",
    "reason": "适合视觉兴趣强的孩子，通过触觉刺激促进感官整合",
    "summary": "用手指蘸不同颜色的颜料在纸上作画，家长引导孩子观察颜色混合的变化，鼓励孩子表达感受。",
    "materials": ["颜料", "画纸", "湿巾"],
    "keyPoints": ["准备颜料和纸", "示范手指画", "引导颜色混合", "鼓励表达感受", "清洁收尾"]
  }
]
\`\`\`

请返回 3-5 个游戏。注意：只需要概要信息，不要详细步骤。
`;
}
