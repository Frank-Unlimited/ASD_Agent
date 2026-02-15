/**
 * Online Search Service Test - 测试联网搜索功能
 */

import {
  searchGamesOnline
} from './onlineSearchService';

/**
 * 测试联网搜索
 */
export const testOnlineSearch = async () => {
  console.log('\n=== 测试联网搜索 ===\n');

  const query = '视觉 建构 双向沟通 适中难度 室内';
  const childContext = `
儿童基本信息：
- 姓名：辰辰
- 性别：男
- 诊断：自闭症谱系障碍（ASD），轻度

当前画像：
辰辰是一个4岁的男孩，对视觉刺激特别敏感，喜欢观察旋转的物体和鲜艳的颜色。
他在建构活动中表现出较强的专注力，能够独立完成简单的积木搭建。
在社交方面，辰辰开始对其他小朋友产生兴趣，但还需要成人的引导才能主动互动。

优势：
- 视觉注意力强
- 对建构活动有兴趣
- 能够遵循简单指令

需要关注：
- 主动社交能力较弱
- 语言表达需要提升
`;

  console.log('搜索条件:', query);
  console.log('儿童情况:', childContext.substring(0, 100) + '...');

  try {
    const games = await searchGamesOnline(query, childContext, 3);

    console.log(`\n✅ 找到 ${games.length} 个游戏:\n`);
    games.forEach((game, i) => {
      console.log(`${i + 1}. ${game.title}`);
      console.log(`   目标: ${game.target}`);
      console.log(`   时长: ${game.duration}`);
      console.log(`   特点: ${game.reason}`);
      console.log(`   步骤数: ${game.steps.length}`);
      console.log('');
    });

    return games;
  } catch (error) {
    console.error('❌ 联网搜索失败:', error);
    throw error;
  }
};

/**
 * 测试联网搜索（第二组查询）
 */
export const testHybridSearch = async () => {
  console.log('\n=== 测试联网搜索（第二组）===\n');

  const query = '听觉 音乐 节奏 社交';
  const childContext = `
儿童对音乐特别敏感，听到音乐就会摇摆身体。
需要提升社交互动能力和轮流意识。
`;

  console.log('搜索条件:', query);
  console.log('儿童情况:', childContext);

  try {
    const games = await searchGamesOnline(query, childContext, 5);

    console.log(`\n✅ 找到 ${games.length} 个游戏:\n`);
    games.forEach((game, i) => {
      console.log(`${i + 1}. ${game.title}`);
      console.log(`   目标: ${game.target}`);
      console.log(`   时长: ${game.duration}`);
      console.log('');
    });

    return games;
  } catch (error) {
    console.error('❌ 联网搜索失败:', error);
    throw error;
  }
};

/**
 * 运行所有测试
 */
export const runAllRAGTests = async () => {
  console.log('╔════════════════════════════════════════╗');
  console.log('║       联网搜索服务测试套件            ║');
  console.log('╚════════════════════════════════════════╝');

  try {
    await testOnlineSearch();

    console.log('\n等待 2 秒...\n');
    await new Promise(resolve => setTimeout(resolve, 2000));

    await testHybridSearch();

    console.log('\n╔════════════════════════════════════════╗');
    console.log('║        ✅ 所有测试通过！             ║');
    console.log('╚════════════════════════════════════════╝');
  } catch (error) {
    console.log('\n╔════════════════════════════════════════╗');
    console.log('║          ❌ 测试失败！               ║');
    console.log('╚════════════════════════════════════════╝');
    console.error(error);
  }
};

if (typeof window !== 'undefined') {
  (window as any).testOnlineSearch = testOnlineSearch;
  (window as any).testHybridSearch = testHybridSearch;
  (window as any).runAllRAGTests = runAllRAGTests;

  console.log('联网搜索测试函数已加载到 window 对象:');
  console.log('- window.testOnlineSearch()');
  console.log('- window.testHybridSearch()');
  console.log('- window.runAllRAGTests()');
}
