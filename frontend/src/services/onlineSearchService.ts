/**
 * Online Search Service - 联网游戏搜索服务
 * 使用博查AI搜索从互联网搜索游戏信息
 * 然后使用 LLM 解析和结构化搜索结果
 */

import { Game } from '../types';
import { bochaSearchService } from './bochaSearchService';
import { qwenStreamClient } from './qwenStreamClient';

function buildSearchQuery(query: string): string {
  return `${query} 自闭症儿童 DIR Floortime 地板游戏 感统游戏`.trim();
}

function buildParsePrompt(searchResults: string, query: string, childContext: string): string {
  return `
你是一位专业的 DIR/Floortime 游戏设计师。请根据以下搜索结果，提取和推荐适合自闭症儿童的地板游戏。

【搜索结果】
${searchResults}

【搜索条件】
${query}

${childContext ? `【儿童情况】\n${childContext}\n` : ''}

【要求】
1. 从搜索结果中提取适合自闭症儿童的地板游戏、感统游戏、互动游戏
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
 * 联网搜索游戏（使用博查AI搜索 + LLM 解析）
 * 真正从互联网搜索适合的地板游戏
 * @returns { games: Game[], searchResults: WebSearchResult[] }
 */
export const searchGamesOnline = async (
  query: string,
  childContext: string = '',
  topK: number = 5
): Promise<{ games: Game[], searchResults: any[] }> => {
  try {
    console.log('🌐 开始联网搜索游戏...');

    // 使用博查AI搜索 联网搜索
    const searchQuery = buildSearchQuery(query);
    console.log('🔍 搜索关键词:', searchQuery);

    const rawSearchResults = await bochaSearchService.search(searchQuery, { 
      count: 10,
      summary: true 
    });

    if (!rawSearchResults || rawSearchResults.length === 0) {
      console.warn('⚠️  博查搜索无结果');
      return { games: [], searchResults: [] };
    }

    console.log('✅ 博查搜索返回结果');

    // 格式化搜索结果用于展示
    const searchResults = rawSearchResults.map(result => ({
      name: result.name,
      url: result.url,
      snippet: result.snippet,
      siteName: result.siteName
    }));

    // 格式化搜索结果用于LLM解析
    const searchResultsText = rawSearchResults
      .map((result, index) => {
        const summary = result.summary || result.snippet;
        return `${index + 1}. ${result.name}\n   ${summary}\n   来源: ${result.siteName}`;
      })
      .join('\n\n');

    // 使用 LLM 解析搜索结果并结构化
    const parsePrompt = buildParsePrompt(searchResultsText, query, childContext);

    // 打印完整的 prompt
    console.log('='.repeat(80));
    console.log('[Online Search Parser] 完整 Prompt:');
    console.log('='.repeat(80));
    console.log('System Prompt:');
    console.log('你是一位专业的 DIR/Floortime 游戏设计师。请根据搜索结果推荐适合自闭症儿童的地板游戏，并按照指定的 JSON 格式返回。');
    console.log('-'.repeat(80));
    console.log('User Prompt:');
    console.log(parsePrompt);
    console.log('='.repeat(80));

    const response = await qwenStreamClient.chat(
      [
        {
          role: 'system',
          content: `你是一位专业的 DIR/Floortime 游戏设计师。请根据搜索结果推荐适合自闭症儿童的地板游戏，并按照指定的 JSON 格式返回。`
        },
        {
          role: 'user',
          content: parsePrompt
        }
      ],
      {
        temperature: 0.7,
        max_tokens: 2000
      }
    );

    // 打印完整的响应
    console.log('='.repeat(80));
    console.log('[Online Search Parser] 完整响应:');
    console.log('='.repeat(80));
    console.log(response);
    console.log('='.repeat(80));

    console.log('📡 LLM 解析完成');

    const games = parseGamesFromSearchResult(response);

    console.log(`✅ 解析到 ${games.length} 个游戏`);

    return { 
      games: games.slice(0, topK),
      searchResults: searchResults.slice(0, 10)
    };
  } catch (error) {
    console.error('❌ 联网搜索出错:', error);
    return { games: [], searchResults: [] };
  }
};

/**
 * 解析搜索结果中的游戏信息
 */
function parseGamesFromSearchResult(content: string): Game[] {
  try {
    console.log('🔍 开始解析游戏信息...');

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
        return [];
      }
    }

    // 清理 JSON 字符串
    jsonStr = jsonStr.replace(/\/\/.*$/gm, '');
    jsonStr = jsonStr.replace(/\/\*[\s\S]*?\*\//g, '');
    jsonStr = jsonStr.replace(/,(\s*[}\]])/g, '$1');

    let gamesData: any[];
    try {
      gamesData = JSON.parse(jsonStr);
    } catch (parseError) {
      console.error('❌ JSON 解析失败，尝试修复...');
      
      let fixedJson = jsonStr.replace(/'/g, '"');
      fixedJson = fixedJson.replace(/\n/g, '\\n');

      try {
        gamesData = JSON.parse(fixedJson);
        console.log('✓ JSON 修复成功');
      } catch (secondError) {
        console.error('❌ JSON 修复失败');
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
      const steps = keyPoints.map((point: string, i: number) => ({
        stepTitle: `第${i + 1}步`,
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

      console.log(`  ${index + 1}. ${gameObj.title}`);
      return gameObj;
    });

    return games;
  } catch (error) {
    console.error('❌ 解析游戏信息失败:', error);
    return [];
  }
}
