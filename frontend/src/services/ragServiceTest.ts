/**
 * RAG Service Test - 测试联网搜索功能
 */

import { 
  searchGamesFromLibrary, 
  searchGamesOnline, 
  searchGamesHybrid 
} from './ragService';

/**
 * 测试本地游戏库搜索
 */
export const testLocalSearch = async () => {
  console.log('\n=== 测试本地游戏库搜索 ===\n');
  
  const query = '视觉 建构 双向沟通';
  console.log('搜索条件:', query);
  
  const games = await searchGamesFromLibrary(query, 3);
  
  console.log(`\n找到 ${games.length} 个游戏:\n`);
  games.forEach((game, i) => {
    console.log(`${i + 1}. ${game.title}`);
    console.log(`   目标: ${game.target}`);
    console.log(`   时长: ${game.duration}`);
    console.log(`   特点: ${game.reason}`);
    console.log('');
  });
  
  return games;
};

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
 * 测试混合搜索
 */
export const testHybridSearch = async () => {
  console.log('\n=== 测试混合搜索（本地 + 联网）===\n');
  
  const query = '听觉 音乐 节奏 社交';
  const childContext = `
儿童对音乐特别敏感，听到音乐就会摇摆身体。
需要提升社交互动能力和轮流意识。
`;
  
  console.log('搜索条件:', query);
  console.log('儿童情况:', childContext);
  
  try {
    const games = await searchGamesHybrid(query, childContext, 5);
    
    console.log(`\n✅ 找到 ${games.length} 个游戏（本地 + 联网）:\n`);
    games.forEach((game, i) => {
      const source = game.id.startsWith('online_') ? '[联网]' : '[本地]';
      console.log(`${i + 1}. ${source} ${game.title}`);
      console.log(`   目标: ${game.target}`);
      console.log(`   时长: ${game.duration}`);
      console.log('');
    });
    
    return games;
  } catch (error) {
    console.error('❌ 混合搜索失败:', error);
    throw error;
  }
};

/**
 * 对比测试：本地 vs 联网
 */
export const testComparison = async () => {
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║     RAG 搜索对比测试（本地 vs 联网）  ║');
  console.log('╚════════════════════════════════════════╝\n');
  
  const query = '触觉 感官 自我调节';
  
  // 本地搜索
  console.log('【本地搜索】');
  const localGames = await searchGamesFromLibrary(query, 3);
  console.log(`结果数量: ${localGames.length}`);
  localGames.forEach((g, i) => console.log(`  ${i + 1}. ${g.title}`));
  
  console.log('\n等待 2 秒...\n');
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // 联网搜索
  console.log('【联网搜索】');
  try {
    const onlineGames = await searchGamesOnline(query, '', 3);
    console.log(`结果数量: ${onlineGames.length}`);
    onlineGames.forEach((g, i) => console.log(`  ${i + 1}. ${g.title}`));
  } catch (error) {
    console.log('联网搜索失败，可能是 API 配置问题');
  }
  
  console.log('\n等待 2 秒...\n');
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // 混合搜索
  console.log('【混合搜索】');
  const hybridGames = await searchGamesHybrid(query, '', 5);
  console.log(`结果数量: ${hybridGames.length}`);
  hybridGames.forEach((g, i) => {
    const source = g.id.startsWith('online_') ? '[联网]' : '[本地]';
    console.log(`  ${i + 1}. ${source} ${g.title}`);
  });
  
  console.log('\n╔════════════════════════════════════════╗');
  console.log('║          ✅ 对比测试完成！           ║');
  console.log('╚════════════════════════════════════════╝');
};

/**
 * 运行所有测试
 */
export const runAllRAGTests = async () => {
  console.log('╔════════════════════════════════════════╗');
  console.log('║       RAG 服务完整测试套件           ║');
  console.log('╚════════════════════════════════════════╝');
  
  try {
    // 测试1: 本地搜索
    await testLocalSearch();
    
    console.log('\n等待 2 秒...\n');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 测试2: 联网搜索
    await testOnlineSearch();
    
    console.log('\n等待 2 秒...\n');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 测试3: 混合搜索
    await testHybridSearch();
    
    console.log('\n等待 2 秒...\n');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 测试4: 对比测试
    await testComparison();
    
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

// 如果直接运行此文件
if (typeof window !== 'undefined') {
  (window as any).testLocalSearch = testLocalSearch;
  (window as any).testOnlineSearch = testOnlineSearch;
  (window as any).testHybridSearch = testHybridSearch;
  (window as any).testComparison = testComparison;
  (window as any).runAllRAGTests = runAllRAGTests;
  
  console.log('RAG 测试函数已加载到 window 对象:');
  console.log('- window.testLocalSearch()');
  console.log('- window.testOnlineSearch()');
  console.log('- window.testHybridSearch()');
  console.log('- window.testComparison()');
  console.log('- window.runAllRAGTests()');
}
