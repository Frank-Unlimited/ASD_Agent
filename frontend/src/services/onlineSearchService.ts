// TODO: 接入云端游戏库检索

/**
 * Online Search Service - 联网游戏搜索服务
 * 通过 qwenStreamClient 调用大模型联网搜索适合的地板游戏
 */

import { Game } from '../types';

function buildSearchGamesPrompt(query: string, childContext: string): string {
  return `
请从互联网搜索适合自闭症儿童的 DIR/Floortime 地板游戏，要求：

【搜索条件】
${query}

${childContext ? `【儿童情况】\n${childContext}\n` : ''}

【要求】
1. 搜索适合自闭症儿童的地板游戏、感统游戏、互动游戏
2. 游戏应该基于 DIR/Floortime 理念
3. 游戏应该有明确的训练目标
4. 只需要提供游戏的大致玩法概要，不需要详细步骤

【返回格式】
请以 JSON 数组格式返回，每个游戏包含：
- title: 游戏名称
- target: 训练目标
- duration: 游戏时长
- reason: 适合理由
- summary: 游戏玩法概要（2-3句话）
- materials: 所需材料列表
- keyPoints: 3-5个关键要点

请返回 3-5 个游戏。
`;
}

/**
 * 联网搜索游戏（使用 qwenStreamClient）
 * 实时从互联网搜索适合的地板游戏
 */
export const searchGamesOnline = async (
  query: string,
  childContext: string = '',
  topK: number = 5
): Promise<Game[]> => {
  try {
    console.log('🌐 开始联网搜索游戏...');

    const searchPrompt = buildSearchGamesPrompt(query, childContext);

    const { qwenStreamClient } = await import('./qwenStreamClient');

    const response = await qwenStreamClient.chat(
      [
        {
          role: 'system',
          content: `你是一位专业的 DIR/Floortime 游戏设计师。请推荐适合自闭症儿童的地板游戏，并按照指定的 JSON 格式返回。`
        },
        {
          role: 'user',
          content: searchPrompt
        }
      ],
      {
        temperature: 0.7,
        max_tokens: 2000
      }
    );

    console.log('📡 API 响应:', response.substring(0, 200) + '...');
    console.log('📡 完整响应长度:', response.length);

    if (response.length < 50) {
      console.warn('⚠️  API 响应内容过短，可能出错');
      console.log('完整响应:', response);
    }

    if (!response) {
      console.warn('⚠️  API 返回内容为空');
      throw new Error('Empty response from API');
    }

    const games = parseGamesFromSearchResult(response);

    console.log(`✅ 解析到 ${games.length} 个游戏`);

    if (games.length === 0) {
      console.warn('⚠️  联网搜索无结果');
      return [];
    }

    return games.slice(0, topK);
  } catch (error) {
    console.error('❌ 联网搜索出错:', error);
    return [];
  }
};

/**
 * 解析搜索结果中的游戏信息
 */
function parseGamesFromSearchResult(content: string): Game[] {
  try {
    console.log('🔍 开始解析游戏信息...');
    console.log('原始内容长度:', content.length);

    let jsonStr = '';

    const codeBlockMatch = content.match(/```json\s*([\s\S]*?)\s*```/);
    if (codeBlockMatch) {
      jsonStr = codeBlockMatch[1];
      console.log('✓ 从代码块中提取 JSON');
    } else {
      const arrayMatch = content.match(/\[[\s\S]*\]/);
      if (arrayMatch) {
        jsonStr = arrayMatch[0];
        console.log('✓ 从内容中提取 JSON 数组');
      } else {
        console.warn('⚠️  未找到 JSON 格式内容');
        console.log('内容预览:', content.substring(0, 500));
        return [];
      }
    }

    // 清理 JSON 字符串
    jsonStr = jsonStr.replace(/\/\/.*$/gm, '');
    jsonStr = jsonStr.replace(/\/\*[\s\S]*?\*\//g, '');
    jsonStr = jsonStr.replace(/,(\s*[}\]])/g, '$1');

    console.log('清理后的 JSON 预览:', jsonStr.substring(0, 300) + '...');

    let gamesData;
    try {
      gamesData = JSON.parse(jsonStr);
    } catch (parseError) {
      console.error('❌ JSON 解析失败，尝试修复...');
      console.log('解析错误:', parseError instanceof Error ? parseError.message : String(parseError));

      let fixedJson = jsonStr.replace(/'/g, '"');
      fixedJson = fixedJson.replace(/\n/g, '\\n');

      try {
        gamesData = JSON.parse(fixedJson);
        console.log('✓ JSON 修复成功');
      } catch (secondError) {
        console.error('❌ JSON 修复失败:', secondError);
        console.log('失败的 JSON:', fixedJson.substring(0, 500));
        return [];
      }
    }

    if (!Array.isArray(gamesData)) {
      console.warn('⚠️  解析的数据不是数组');
      return [];
    }

    console.log(`✅ 成功解析 ${gamesData.length} 个游戏`);

    const games = gamesData.map((game, index) => {
      const keyPoints = game.keyPoints || [];
      const steps = keyPoints.map((point: string) => ({
        instruction: point,
        guidance: ''
      }));

      const gameObj: Game = {
        id: `online_${Date.now()}_${index}`,
        title: game.title || '未命名游戏',
        target: game.target || '综合训练',
        duration: game.duration || '15-20分钟',
        reason: game.reason || '',
        isVR: game.isVR || false,
        steps: steps,
        summary: game.summary || '',
        materials: game.materials || []
      };

      console.log(`  ${index + 1}. ${gameObj.title} (概要: ${keyPoints.length} 个关键点)`);
      return gameObj;
    });

    return games;
  } catch (error) {
    console.error('❌ 解析游戏信息失败:', error);
    console.log('错误详情:', error instanceof Error ? error.message : String(error));
    return [];
  }
}
