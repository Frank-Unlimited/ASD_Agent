/**
 * 游戏复盘 Prompt
 * 用于游戏结束后的 AI 专业复盘分析
 */

import { ChildProfile, FloorGame, ComprehensiveAssessment } from '../types';

export const GAME_REVIEW_SYSTEM_PROMPT = `
你是一位资深的 DIR/Floortime（地板时光）疗法专家和儿童发展评估师，专注于自闭症谱系障碍（ASD）儿童的干预和评估。

你的任务是对一次地板游戏互动进行专业复盘，重点关注：
1. 游戏过程中孩子的表现和亲子互动质量
2. 这类游戏对该孩子的适合程度，是否应继续、调整还是避免
3. 未来干预的方向和改进建议

## 核心理论框架

### DIR/Floortime 六大发展里程碑
1. **自我调节与兴趣**：孩子能否保持平静、专注，对环境产生兴趣
2. **亲密感与参与**：孩子能否与照顾者建立情感连接，产生共同关注
3. **双向沟通**：孩子能否发起和回应简单的互动循环（开圈-闭圈）
4. **复杂沟通**：孩子能否进行多步骤的问题解决和连续互动
5. **情绪思考**：孩子能否使用想象力、表达情感、进行假装游戏
6. **逻辑思维**：孩子能否进行因果推理、分类和抽象思考

### recommendation 判断标准
- **continue**：游戏整体效果好，孩子参与度高，适合继续使用
- **adjust**：游戏有潜力但某些方面需要调整（难度、节奏、互动方式等）
- **avoid**：游戏明显不适合当前阶段的孩子，应暂时避免

请用温暖、专业、鼓励的语气进行复盘。强调孩子的进步，温和指出需要改进的方向。
`;

/**
 * 构建游戏复盘用户 prompt
 */
export function buildGameReviewPrompt(params: {
  childProfile: ChildProfile;
  game: FloorGame;
  chatHistory: string;
  videoSummary?: string;
  parentFeedback: string;
  latestAssessment?: ComprehensiveAssessment | null;
}): string {
  const { childProfile, game, chatHistory, videoSummary, parentFeedback, latestAssessment } = params;

  const age = calculateAge(childProfile.birthDate);
  const gameDuration = calculateDuration(game.dtstart, game.dtend);
  const stepsText = game.steps.map((s, i) => `${i + 1}. ${s.stepTitle || s.instruction}`).join('\n');

  let prompt = `
请对以下地板游戏互动进行专业复盘：

【孩子信息】
姓名：${childProfile.name}
性别：${childProfile.gender}
年龄：${age}
当前诊断/画像：${childProfile.diagnosis || '暂无'}
`;

  if (latestAssessment) {
    prompt += `
【最近一次综合评估】
时间：${formatDate(latestAssessment.timestamp)}
摘要：${latestAssessment.summary}
画像：${latestAssessment.currentProfile.substring(0, 200)}...
建议：${latestAssessment.nextStepSuggestion.substring(0, 150)}...
`;
  }

  prompt += `
【游戏信息】
游戏名称：${game.gameTitle}
游戏目标：${game.goal}
游戏步骤：
${stepsText}
游戏时长：${gameDuration}
游戏状态：${game.status === 'completed' ? '已完成' : game.status === 'aborted' ? '中止' : '进行中'}
`;

  if (game.materials && game.materials.length > 0) {
    prompt += `所需材料：${game.materials.join('、')}\n`;
  }

  prompt += `
【游戏中互动记录】
${chatHistory || '无互动记录'}
`;

  if (videoSummary) {
    prompt += `
【视频观察总结】
${videoSummary}
`;
  }

  prompt += `
【家长反馈】
${parentFeedback || '家长未提供额外反馈'}

【输出要求】
请基于以上信息，从 DIR/Floortime 专业视角进行复盘，生成：

1. reviewSummary：游戏过程总结与复盘（200-400字）
   - 回顾本次游戏的整体过程
   - 分析孩子的参与度、情绪状态、互动质量
   - 评估亲子互动中的亮点和不足

2. scores：多维度打分（每项 0-100），请根据互动记录合理评估，各维度要有区分度：
   - childEngagement：孩子参与度/配合度
   - gameCompletion：游戏完成度
   - emotionalConnection：情感连接质量
   - communicationLevel：沟通互动水平
   - skillProgress：目标能力进步
   - parentExecution：家长执行质量

3. recommendation：建议（continue/adjust/avoid）
   - 这类游戏是否适合该孩子继续进行

4. nextStepSuggestion：下一步建议（200-300字）
   - 解释为什么给出 continue/adjust/avoid 的建议
   - 如果是 adjust，具体说明需要在哪些方面做出改进
   - 给出未来干预的方向和可尝试的游戏类型

重要提示：
- 请直接返回包含实际数据的 JSON 对象
- 不要返回 Schema 定义本身
- 如果互动记录信息有限，请基于游戏设计和可获得的信息进行合理推断
`;

  return prompt;
}

function calculateAge(birthDate: string): string {
  const birth = new Date(birthDate);
  const now = new Date();
  const years = now.getFullYear() - birth.getFullYear();
  const months = now.getMonth() - birth.getMonth();
  let ageYears = years;
  let ageMonths = months;
  if (months < 0) {
    ageYears--;
    ageMonths = 12 + months;
  }
  return ageYears > 0 ? `${ageYears}岁${ageMonths}个月` : `${ageMonths}个月`;
}

function calculateDuration(dtstart: string, dtend: string): string {
  if (!dtstart || !dtend) return '未知';
  const start = new Date(dtstart).getTime();
  const end = new Date(dtend).getTime();
  const diffMs = end - start;
  if (diffMs <= 0) return '未知';
  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return '不到1分钟';
  return `${minutes}分钟`;
}

function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`;
}
