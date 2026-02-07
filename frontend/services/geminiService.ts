
import { GoogleGenAI, Chat, Content, Type } from "@google/genai";
import { ChatMessage, LogEntry, BehaviorAnalysis, InterestDimensionType, ProfileUpdate, AbilityDimensionType } from "../types";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const GAMES_LIBRARY = `
现有游戏库（ID - 名称 - 目标 - 适合特征）：
1 - 积木高塔轮流堆 - 共同注意 - 适合视觉关注强、需要建立轮流规则的孩子。
2 - 感官泡泡追逐战 - 自我调节 - 适合需要调节兴奋度、喜欢动态视觉追踪的孩子。
3 - VR 奇幻森林绘画 - 创造力 - 适合喜欢视觉刺激、空间探索，需要提升手眼协调的孩子。
`;

const SYSTEM_INSTRUCTION_BASE = `
你是一位温暖、专业且充满鼓励的 DIR/Floortime（地板时光）疗法助手。
你的核心任务是基于孩子的**个人档案分析**来辅助家长。

${GAMES_LIBRARY}

交互规则：
1. **个性化回复**：始终参考提供的[当前孩子档案]，利用其中的兴趣点（如喜欢汽车、恐龙）来打比方或提供建议。

2. **推荐游戏**：当家长询问玩什么，或你认为需要通过游戏干预时，请根据档案中的**能力短板**和**高兴趣点**选择游戏。
   输出格式：:::GAME_RECOMMENDATION:{"id": "ID号", "title": "游戏名称", "reason": "基于档案的推荐理由"}:::

3. **行为记录确认**：当家长描述了孩子具体的日常行为（如“他今天一直把车排成一排”或“他刚才看了我一眼”），请提取该行为并关联兴趣维度，生成确认卡片：
   输出格式：:::BEHAVIOR_LOG_CARD:{"behavior": "精简的行为描述", "tags": ["Visual", "Order"等相关维度], "analysis": "一句话分析其发展意义"}:::

4. **本周计划概览**：当家长询问“这周练什么”或“查看计划”时，基于当前能力短板生成一个简要的周计划卡片：
   输出格式：:::WEEKLY_PLAN_CARD:{"focus": "本周核心目标", "schedule": [{"day": "周一", "task": "活动名"}, {"day": "周三", "task": "活动名"}, {"day": "周五", "task": "活动名"}]}:::

5. **页面跳转**：需要更新档案或查看完整日历时输出：:::NAVIGATION_CARD:{"page": "PROFILE" 或 "CALENDAR", "title": "标题", "reason": "理由"}:::

请始终使用**中文**回答。
`;

const INTEREST_DIMENSIONS_DEF = `
八大兴趣维度定义：
Visual(视觉), Auditory(听觉), Tactile(触觉), Motor(运动), Construction(建构), Order(秩序), Cognitive(认知), Social(社交)。
`;

const ABILITY_DIMENSIONS_DEF = `
DIR 六大能力维度：
自我调节, 亲密感, 双向沟通, 复杂沟通, 情绪思考, 逻辑思维。
`;

/**
 * AGENT 1: RECOMMENDATION AGENT
 * Decides the best game based on the analysis of the file and the child's current state.
 */
export const recommendGame = async (profileContext: string): Promise<{id: string, title: string, reason: string} | null> => {
    try {
        const prompt = `
        作为推荐 Agent，请分析以下儿童档案，从游戏库中选择一个最适合当前发展需求的游戏。
        
        ${GAMES_LIBRARY}

        ${profileContext}

        决策逻辑：
        1. 优先选择能利用孩子"高兴趣维度"的游戏（作为切入点）。
        2. 针对孩子"低分能力维度"进行训练（作为目标）。
        
        请返回 JSON: { "id": "...", "title": "...", "reason": "..." }
        `;

        const response = await ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: prompt,
            config: { responseMimeType: "application/json" }
        });
        
        return JSON.parse(response.text || "null");
    } catch (e) {
        console.error("Recommendation Agent Failed:", e);
        return null;
    }
};

/**
 * AGENT 2: EVALUATION AGENT (Session)
 * Evaluates behavioral data from game sessions.
 */
export const evaluateSession = async (logs: LogEntry[]): Promise<{ score: number, feedbackScore: number, explorationScore: number, summary: string, suggestion: string, interestAnalysis: BehaviorAnalysis[] }> => {
    try {
        const logContent = logs.map(l => `[${l.type}] ${l.content}`).join('\n');
        
        const evalPrompt = `
        作为评估 Agent，请分析互动记录：
        ${logContent}
        
        请评估以下两个维度（0-100分）：
        1. feedbackScore: 单次反馈得分（关注互动的质量、回应的及时性和情感连结）。
        2. explorationScore: 探索度得分（关注行为的多样性、尝试新事物的意愿和兴趣广度）。
        
        综合得分 score = (feedbackScore + explorationScore) / 2。
        
        返回 JSON:
        {
            "feedbackScore": number,
            "explorationScore": number,
            "score": number,
            "summary": "总结",
            "suggestion": "建议"
        }
        `;

        // Parallel execution for efficiency
        const [evalResponse, interestData] = await Promise.all([
            ai.models.generateContent({
                model: 'gemini-3-flash-preview',
                contents: evalPrompt,
                config: { responseMimeType: "application/json" }
            }),
            analyzeInterests(logContent) // Reusing the interest extractor
        ]);

        const evalData = JSON.parse(evalResponse.text || "{}");

        return {
            score: evalData.score || 70,
            feedbackScore: evalData.feedbackScore || 70,
            explorationScore: evalData.explorationScore || 70,
            summary: evalData.summary || "记录已分析。",
            suggestion: evalData.suggestion || "继续保持。",
            interestAnalysis: interestData
        };

    } catch (error) {
        console.error("Evaluation Agent Failed:", error);
        return { 
            score: 75,
            feedbackScore: 75,
            explorationScore: 75,
            summary: "分析中断，但互动记录已保存。", 
            suggestion: "请继续观察孩子反应。",
            interestAnalysis: []
        };
    }
};

/**
 * AGENT 2: EVALUATION AGENT (Report)
 * Analyzes reported data (uploaded files) to create/update personal file analysis.
 */
export const analyzeReport = async (reportText: string): Promise<ProfileUpdate> => {
    try {
        const prompt = `
        作为评估 Agent，分析这份报告并更新档案：
        ${INTEREST_DIMENSIONS_DEF}
        ${ABILITY_DIMENSIONS_DEF}

        报告内容：
        "${reportText}"

        返回 JSON (ProfileUpdate结构):
        {
          "interestUpdates": [{ "behavior": "...", "matches": [{ "dimension": "...", "weight": 0.8 }] }],
          "abilityUpdates": [{ "dimension": "...", "scoreChange": 5, "reason": "..." }]
        }
        `;

        const response = await ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: prompt,
            config: { responseMimeType: "application/json" }
        });
        
        const data = JSON.parse(response.text || "{}");
        return {
            source: 'REPORT',
            interestUpdates: data.interestUpdates || [],
            abilityUpdates: data.abilityUpdates || []
        };
    } catch (e) {
        console.error("Report Analysis Failed:", e);
        return { source: 'REPORT', interestUpdates: [], abilityUpdates: [] };
    }
};

/**
 * Helper: Extract interests (Used by Evaluation Agent)
 */
export const analyzeInterests = async (textInput: string): Promise<BehaviorAnalysis[]> => {
    try {
        const prompt = `
        任务：提取行为并映射到八大兴趣维度。
        ${INTEREST_DIMENSIONS_DEF}
        文本： "${textInput}"
        返回 JSON: [{ "behavior": "...", "matches": [{ "dimension": "Visual", "weight": 0.9, "reasoning": "..." }] }]
        `;
        const response = await ai.models.generateContent({
            model: 'gemini-3-flash-preview',
            contents: prompt,
            config: { responseMimeType: "application/json" }
        });
        return JSON.parse(response.text || "[]");
    } catch (e) { return []; }
};

/**
 * AGENT 3: DIALOGUE AGENT
 * Handles conversation, capable of checking profile context.
 */
export const sendGeminiMessage = async (currentMessage: string, history: ChatMessage[], profileContext: string): Promise<string> => {
    try {
        // We inject the profile context as a high-priority system-level user message at the start of history
        // or effectively by prepending it to the chat if using stateless calls.
        
        const contextMsg: Content = {
            role: 'user',
            parts: [{ text: `[SYSTEM: 当前孩子档案分析数据]\n${profileContext}\n请基于此档案回答后续问题。` }]
        };

        const pastHistory: Content[] = history
            .filter(msg => msg.role === 'user' || msg.role === 'model') 
            .map(msg => ({
                role: msg.role,
                parts: [{ text: msg.text }]
            }));

        const chat = ai.chats.create({
            model: 'gemini-3-flash-preview',
            config: { systemInstruction: SYSTEM_INSTRUCTION_BASE },
            history: [contextMsg, ...pastHistory] // Inject context first
        });

        const result = await chat.sendMessage({ message: currentMessage });
        return result.text;
    } catch (error) {
        console.error("Dialogue Agent Error:", error);
        throw error;
    }
};
