import { GoogleGenAI, Chat } from "@google/genai";

// Initialize the client. 
// NOTE: In a real production app, ensure your API key is secure.
const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

// Define the available games context so the AI knows what to recommend
const GAMES_LIBRARY = `
现有游戏库（请仅推荐以下 ID 的游戏）：
ID: "1", 名称: "积木高塔轮流堆", 目标: "共同注意", 适合: 需要提升眼神接触和轮流互动规则的孩子。
ID: "2", 名称: "感官泡泡追逐战", 目标: "自我调节", 适合: 需要调节情绪兴奋度或增加非语言互动的孩子。
ID: "3", 名称: "VR 奇幻森林绘画", 目标: "创造力", 适合: 喜欢视觉刺激、需要提升空间感知和想象力的孩子，这是本软件的特色功能。
`;

// System instruction to guide the persona
// 更新为中文指令，专注于地板时光（DIR/Floortime）疗法
const SYSTEM_INSTRUCTION = `
你是一位温暖、专业且充满鼓励的 DIR/Floortime（地板时光）疗法助手。
你的任务是帮助自闭症谱系障碍（ASD）儿童的家长，通过游戏互动促进孩子的情感和智力发展。

${GAMES_LIBRARY}

你的功能包括：
1. 推荐适合孩子当前发展阶段（FEDC）的互动游戏。
2. 分析家长的观察记录，提供进步反馈。
3. 在家长感到沮丧时提供情感支持。
4. 引导家长完善孩子档案或查看日程。

请始终使用**中文**回答。回答要简洁、实用、富有同理心。

**重要交互规则 - 卡片生成：**

1. **推荐游戏**：当适合推荐特定游戏时，请在回答最后另起一行输出：
:::GAME_RECOMMENDATION:{"id": "ID号", "title": "游戏名称", "reason": "一句话推荐理由"}:::

2. **页面跳转**：当需要家长去更新档案（例如：你觉得缺乏信息）、上传报告、或查看日程安排时，请在回答最后另起一行输出：
:::NAVIGATION_CARD:{"page": "PROFILE" 或 "CALENDAR", "title": "卡片标题", "reason": "跳转理由"}:::

例如：
我们需要更多信息来定制计划，请更新一下档案。
:::NAVIGATION_CARD:{"page": "PROFILE", "title": "完善孩子档案", "reason": "上传最新的评估报告以便分析"}:::
`;

export const createChatSession = (): Chat => {
  return ai.chats.create({
    model: 'gemini-3-flash-preview',
    config: {
      systemInstruction: SYSTEM_INSTRUCTION,
    },
  });
};

export const generateGamePlan = async (childInfo: string): Promise<string> => {
    try {
        const response = await ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: `为以下情况的孩子生成一个为期1周的地板时光游戏计划：${childInfo}。请返回JSON格式，包含日期（day）、游戏名称（gameTitle）和目标（goal）。确保内容为中文。`,
            config: {
                responseMimeType: "application/json"
            }
        });
        return response.text || "{}";
    } catch (error) {
        console.error("Error generating plan:", error);
        return JSON.stringify({ error: "生成计划失败" });
    }
};

export const summarizeSession = async (logs: string[]): Promise<string> => {
    try {
         const response = await ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: `基于这些游戏过程中的记录，总结本次地板时光的效果：${logs.join(', ')}。请用中文回答，强调2个成功互动的亮点和1个可以改进的地方。`,
        });
        return response.text || "非常棒的互动！继续保持。";
    } catch (error) {
        console.error("Error summarizing:", error);
        return "暂时无法生成总结。";
    }
}