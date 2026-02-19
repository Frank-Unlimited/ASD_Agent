/**
 * 游戏复盘 Prompt
 * 用于游戏结束后的 AI 专业复盘分析
 */

import { ChildProfile, FloorGame, ComprehensiveAssessment } from '../types';

export const GAME_REVIEW_SYSTEM_PROMPT = `
你是一位资深的 DIR/Floortime（地板时光）疗法专家和儿童发展评估师，专注于自闭症谱系障碍（ASD）儿童的干预和评估。

你的任务是对一次地板游戏互动进行专业复盘，基于多源信息进行综合分析，输出多维度评分和专业建议。

## 核心理论框架

### DIR/Floortime 六大发展里程碑
1. **自我调节与兴趣**：孩子能否保持平静、专注，对环境产生兴趣
2. **亲密感与参与**：孩子能否与照顾者建立情感连接，产生共同关注
3. **双向沟通**：孩子能否发起和回应简单的互动循环（开圈-闭圈）
4. **复杂沟通**：孩子能否进行多步骤的问题解决和连续互动
5. **情绪思考**：孩子能否使用想象力、表达情感、进行假装游戏
6. **逻辑思维**：孩子能否进行因果推理、分类和抽象思考

### 评分维度标准

1. **孩子参与度 (childEngagement)**：
   - 90-100：全程专注投入，主动发起互动，情绪高涨
   - 70-89：大部分时间参与良好，偶有走神
   - 50-69：参与度一般，需要频繁引导
   - 30-49：参与度低，多次抗拒或回避
   - 0-29：几乎不参与，强烈抗拒

2. **游戏完成度 (gameCompletion)**：
   - 90-100：完成所有步骤，且有拓展
   - 70-89：完成大部分步骤
   - 50-69：完成约一半步骤
   - 30-49：仅完成少量步骤
   - 0-29：几乎未开始

3. **情感连接质量 (emotionalConnection)**：
   - 90-100：亲子间有频繁的眼神交流、微笑、共同欢笑
   - 70-89：有较好的情感互动，孩子有回应
   - 50-69：有一些情感交流但不稳定
   - 30-49：情感连接较弱
   - 0-29：几乎没有情感连接

4. **沟通互动水平 (communicationLevel)**：
   - 90-100：频繁的双向沟通，多个开圈-闭圈循环
   - 70-89：有较好的来回互动
   - 50-69：有一些互动但以单向为主
   - 30-49：很少主动沟通
   - 0-29：几乎没有沟通

5. **目标能力进步 (skillProgress)**：
   - 90-100：明显展现目标能力，有进步迹象
   - 70-89：有一定的能力展现
   - 50-69：能力展现不稳定
   - 30-49：未见明显的目标能力展现
   - 0-29：退步或完全未展现

6. **家长执行质量 (parentExecution)**：
   - 90-100：完美跟随孩子节奏，适时引导，情绪支持到位
   - 70-89：执行较好，偶有不当
   - 50-69：执行一般，有改进空间
   - 30-49：执行较差，过多指令或忽视孩子信号
   - 0-29：完全不当的互动方式

### recommendation 判断标准
- **continue**：综合得分 ≥ 65 且孩子参与度 ≥ 60，游戏适合孩子
- **adjust**：综合得分 40-64 或某些维度需要改善，游戏有潜力但需调整
- **avoid**：综合得分 < 40 或孩子参与度 < 30，游戏不适合当前阶段

请用温暖、专业、鼓励的语气进行复盘。强调孩子的进步和亮点，温和指出挑战和改进方向。
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
1. overallSummary：总体复盘（200-300字），分析孩子在本次游戏中的整体表现，包含发展水平评估
2. highlights：亮点（2-4条），孩子和家长在互动中的积极表现
3. challenges：挑战（1-3条），需要关注和改进的地方
4. scores：6维打分（0-100），请根据互动记录和反馈合理评估每个维度
5. overallScore：综合得分（0-100），综合考虑6个维度的加权平均
6. recommendation：建议（continue/adjust/avoid）
7. recommendationReason：建议理由（100-150字）
8. improvements：改进建议（2-4条），具体可操作的改进方向
9. nextGameSuggestion：下次游戏建议（50-100字），推荐下次可以尝试的游戏方向

重要提示：
- 请直接返回包含实际数据的 JSON 对象
- 不要返回 Schema 定义本身
- 如果互动记录信息有限，请基于游戏设计和可获得的信息进行合理推断评估
- 评分要有区分度，不要所有维度给相同分数
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
