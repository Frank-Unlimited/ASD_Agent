/**
 * 步骤示意图生成服务
 * 调用 DashScope 文生图 API，为地板游戏每个步骤生成儿童绘本风格插画
 * 流程: 提交任务 → 轮询结果 → 下载图片转 base64 → 存入 IndexedDB
 */

import { imageStorageService } from './imageStorage';

const API_KEY = import.meta.env.VITE_DASHSCOPE_API_KEY;
const MODEL = import.meta.env.VITE_IMAGE_GEN_MODEL || 'wanx2.1-t2i-turbo';

const SUBMIT_URL = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis';
const TASK_URL = 'https://dashscope.aliyuncs.com/api/v1/tasks';

const POLL_INTERVAL = 3000; // 3 秒轮询间隔
const MAX_POLL_TIME = 120000; // 最多等待 2 分钟
const STEP_DELAY = 2000; // 步骤间隔 2 秒，避免速率限制

function buildStepImagePrompt(gameTitle: string, stepTitle: string, instruction: string): string {
  return `儿童绘本插画风格，温暖柔和的色彩，圆润可爱的卡通人物。场景：一位家长和一个小孩子在一起进行亲子互动游戏。游戏名称："${gameTitle}"，当前步骤："${stepTitle}"，具体内容：${instruction}。画面温馨、简洁、富有童趣，适合自闭症儿童家庭使用的教学示意图。`;
}

async function submitTask(prompt: string): Promise<string> {
  const response = await fetch(SUBMIT_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
      'X-DashScope-Async': 'enable',
    },
    body: JSON.stringify({
      model: MODEL,
      input: { prompt },
      parameters: { size: '768*512', n: 1 },
    }),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`提交图片生成任务失败: ${response.status} ${text}`);
  }

  const data = await response.json();
  const taskId = data.output?.task_id;
  if (!taskId) throw new Error('未获取到 task_id');
  return taskId;
}

async function pollTask(taskId: string): Promise<string> {
  const startTime = Date.now();

  while (Date.now() - startTime < MAX_POLL_TIME) {
    await new Promise(r => setTimeout(r, POLL_INTERVAL));

    const response = await fetch(`${TASK_URL}/${taskId}`, {
      headers: { 'Authorization': `Bearer ${API_KEY}` },
    });

    if (!response.ok) {
      throw new Error(`轮询任务失败: ${response.status}`);
    }

    const data = await response.json();
    const status = data.output?.task_status;

    if (status === 'SUCCEEDED') {
      const imageUrl = data.output?.results?.[0]?.url;
      if (!imageUrl) throw new Error('任务成功但未返回图片 URL');
      return imageUrl;
    }

    if (status === 'FAILED') {
      throw new Error(`图片生成失败: ${data.output?.message || '未知错误'}`);
    }

    // PENDING or RUNNING, continue polling
    console.log(`[StepImages] 任务 ${taskId} 状态: ${status}`);
  }

  throw new Error('图片生成超时（2分钟）');
}

async function downloadAsDataUrl(imageUrl: string): Promise<string> {
  const response = await fetch(imageUrl);
  if (!response.ok) throw new Error(`下载图片失败: ${response.status}`);
  const blob = await response.blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result as string);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

export async function generateAndSaveStepImages(
  gameId: string,
  gameTitle: string,
  steps: Array<{ stepTitle: string; instruction: string }>
): Promise<void> {
  if (!API_KEY) {
    console.warn('[StepImages] VITE_DASHSCOPE_API_KEY 未配置，跳过图片生成');
    return;
  }

  console.log(`[StepImages] 开始为游戏 "${gameTitle}" 生成 ${steps.length} 张步骤插画`);

  for (let i = 0; i < steps.length; i++) {
    try {
      const step = steps[i];
      const prompt = buildStepImagePrompt(gameTitle, step.stepTitle, step.instruction);

      console.log(`[StepImages] 步骤 ${i + 1}/${steps.length}: 提交任务...`);
      const taskId = await submitTask(prompt);
      console.log(`[StepImages] 步骤 ${i + 1}: task_id=${taskId}, 轮询中...`);

      const imageUrl = await pollTask(taskId);
      console.log(`[StepImages] 步骤 ${i + 1}: 下载图片...`);

      const dataUrl = await downloadAsDataUrl(imageUrl);
      await imageStorageService.saveStepImage(gameId, i, dataUrl);
      console.log(`[StepImages] 步骤 ${i + 1}: 已保存到 IndexedDB`);

      // 通知 UI 更新
      window.dispatchEvent(new CustomEvent('floorGameStepImagesUpdated', {
        detail: { gameId, stepIndex: i },
      }));

      // 步骤间间隔，避免速率限制（最后一步不需要等待）
      if (i < steps.length - 1) {
        await new Promise(r => setTimeout(r, STEP_DELAY));
      }
    } catch (err) {
      console.warn(`[StepImages] 步骤 ${i + 1} 图片生成失败:`, err);
      // 单步失败不影响其他步骤
    }
  }

  console.log(`[StepImages] 游戏 "${gameTitle}" 图片生成完成`);
}
