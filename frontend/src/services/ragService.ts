/**
 * RAG Service - 游戏库检索服务
 * 提供基于关键词和语义的游戏检索功能
 * 支持本地游戏库 + 联网搜索
 */

import { Game } from '../types';

// 阿里云 Web-Search 配置
const DASHSCOPE_API_KEY = import.meta.env.VITE_DASHSCOPE_API_KEY;
const WEB_SEARCH_ENDPOINT = 'https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation';

// 游戏库（实际应该从后端或本地数据库加载）
const GAMES_LIBRARY: Game[] = [
  {
    id: '1',
    title: '积木高塔轮流堆',
    target: '共同注意',
    duration: '15-20分钟',
    reason: '适合视觉关注强、需要建立轮流规则的孩子',
    steps: [
      { 
        instruction: '准备积木', 
        guidance: '让孩子选择喜欢的颜色和形状的积木，观察他的偏好。用夸张的语气说"哇，你选了红色的！"来吸引注意力。准备10-15块积木即可，不要太多以免分散注意力。'
      },
      { 
        instruction: '轮流堆积木', 
        guidance: '明确说"妈妈/爸爸放一块，然后轮到你放一块"。用手势指向孩子，建立轮流意识。如果孩子想连续放，温和地说"等等，现在是我的回合"。每次轮流后给予鼓励："你等得真好！"'
      },
      { 
        instruction: '观察高塔', 
        guidance: '每放几块就停下来，用手指着高塔说"看，我们的塔越来越高了！"引导孩子一起观察。可以用尺子量一量高度，或者和孩子比比谁高。制造共同关注的时刻。'
      },
      { 
        instruction: '倒塌重来', 
        guidance: '当塔倒塌时，不要沮丧，而是笑着说"哎呀，倒了！没关系，我们再来一次！"帮助孩子理解失败是正常的。可以故意让塔倒下，让孩子看到你也会"失败"。重新开始时说"这次我们能搭得更高吗？"'
      }
    ]
  },
  {
    id: '2',
    title: '感官泡泡追逐战',
    target: '自我调节',
    duration: '10-15分钟',
    reason: '适合需要调节兴奋度、喜欢动态视觉追踪的孩子',
    steps: [
      { 
        instruction: '吹泡泡', 
        guidance: '开始时慢慢吹，观察孩子的反应。如果孩子很兴奋，保持慢节奏；如果孩子不太感兴趣，可以吹得快一些。用夸张的表情和声音"看，泡泡飞起来了！"吸引注意力。注意观察孩子是否过度兴奋或焦虑。'
      },
      { 
        instruction: '追逐泡泡', 
        guidance: '鼓励孩子用手指轻轻戳泡泡，而不是用力拍打。说"轻轻地，慢慢地"来帮助孩子控制力度。如果孩子太兴奋，暂停一下，深呼吸，然后继续。可以设置规则："我们只用一根手指戳泡泡"。'
      },
      { 
        instruction: '戳破泡泡', 
        guidance: '当孩子成功戳破泡泡时，给予即时鼓励："你做到了！"练习手眼协调的同时，也在练习预测泡泡的移动轨迹。可以数一数戳破了几个泡泡，增加成就感。'
      },
      { 
        instruction: '调整节奏', 
        guidance: '根据孩子的状态灵活调整。如果孩子过度兴奋，减少泡泡数量，放慢节奏，甚至暂停让孩子平静下来。如果孩子注意力分散，增加泡泡数量或改变吹泡泡的位置。游戏结束时，引导孩子坐下来，做几次深呼吸，帮助过渡到下一个活动。'
      }
    ]
  },
  {
    id: '3',
    title: 'VR 奇幻森林绘画',
    target: '创造力',
    duration: '20-25分钟',
    reason: '适合喜欢视觉刺激、空间探索，需要提升手眼协调的孩子',
    isVR: true,
    steps: [
      { 
        instruction: '进入VR环境', 
        guidance: '第一次使用VR时，先让孩子戴上头显适应几分钟，不要立即开始游戏。确保头显舒适，不要太紧。告诉孩子"如果感觉不舒服，随时告诉我"。开始时选择简单、明亮的场景，避免过于复杂或黑暗的环境。观察孩子是否有眩晕或不适。'
      },
      { 
        instruction: '探索森林', 
        guidance: '鼓励孩子慢慢移动，观察周围的树木、动物、花朵。问开放式问题："你看到了什么？""那是什么颜色的？"不要催促，让孩子按自己的节奏探索。如果孩子害怕某些元素（如大型动物），可以一起"躲"起来，或者切换到其他区域。'
      },
      { 
        instruction: '自由绘画', 
        guidance: '示范如何使用VR画笔，然后让孩子自由创作。不要评判或纠正孩子的画，而是问"你画的是什么？""能告诉我这个故事吗？"鼓励孩子尝试不同的颜色和笔触。如果孩子不知道画什么，可以建议"我们一起画一棵树吧"或"你想画你喜欢的东西吗？"'
      },
      { 
        instruction: '分享作品', 
        guidance: '游戏结束后，让孩子摘下头显，一起回顾他的作品（如果可以截图）。用具体的语言描述："我看到你用了很多蓝色""这条线画得很长"。问孩子"你最喜欢哪一部分？""下次你想画什么？"帮助孩子用语言表达创作过程，建立自信心。注意控制VR使用时间，避免过度疲劳。'
      }
    ]
  },
  {
    id: '4',
    title: '音乐节奏模仿',
    target: '双向沟通',
    duration: '15-20分钟',
    reason: '适合听觉敏感、喜欢音乐的孩子，训练模仿和轮流',
    steps: [
      { 
        instruction: '播放音乐', 
        guidance: '选择孩子熟悉和喜欢的音乐，节奏要清晰明显。音量不要太大，避免听觉过载。可以从孩子最喜欢的儿歌开始，观察他的反应。如果孩子对某首歌特别有反应（摇摆、微笑），就多用这首歌。'
      },
      { 
        instruction: '拍打节奏', 
        guidance: '家长先示范简单的节奏，如"拍-拍-停-拍"。用夸张的动作和表情，让孩子看清楚。可以拍手、拍腿、拍桌子，增加趣味性。开始时节奏要慢，只有2-3拍，等孩子掌握后再增加复杂度。边拍边数"一、二、三"帮助孩子理解节奏。'
      },
      { 
        instruction: '孩子模仿', 
        guidance: '鼓励孩子跟着你的节奏拍。如果孩子拍错了，不要纠正，而是继续示范。可以握着孩子的手一起拍，帮助他感受节奏。当孩子成功模仿时，立即给予热情的鼓励："太棒了！你跟上了！"逐渐减少辅助，让孩子独立模仿。'
      },
      { 
        instruction: '角色互换', 
        guidance: '当孩子能够模仿后，说"现在轮到你当老师了！"让孩子创造节奏，家长来模仿。这能大大提升孩子的主动性和自信心。即使孩子的节奏很简单或不规则，也要认真模仿，并说"我在学你的节奏！"可以故意"模仿错"，让孩子纠正你，增加互动的乐趣。'
      }
    ]
  },
  {
    id: '5',
    title: '触觉探索箱',
    target: '感官整合',
    duration: '10-15分钟',
    reason: '适合触觉敏感或触觉寻求的孩子，帮助感官整合',
    steps: [
      { 
        instruction: '准备材料', 
        guidance: '准备一个不透明的盒子或袋子，放入不同质地的物品：光滑的（丝绸）、粗糙的（砂纸）、软的（棉花）、硬的（积木）、冷的（金属勺子）、温的（毛绒玩具）。对于触觉敏感的孩子，先从他能接受的质地开始，逐渐引入新的触感。对于触觉寻求的孩子，可以加入更强烈的刺激如豆子、米粒等。'
      },
      { 
        instruction: '摸索猜测', 
        guidance: '让孩子把手伸进盒子，不要看，只用手摸。问"这个摸起来怎么样？""是软的还是硬的？"如果孩子抗拒，不要强迫，可以先让他看着摸，或者家长先示范。可以玩猜谜游戏："我摸到了一个圆圆的、硬硬的东西，你猜是什么？"增加趣味性。'
      },
      { 
        instruction: '描述感受', 
        guidance: '引导孩子用语言描述触感。提供词汇选项："是软软的，还是硬硬的？""是光滑的，还是粗糙的？"如果孩子语言能力有限，可以用表情或手势表达。家长也要描述自己的感受："哇，这个摸起来凉凉的！"示范如何表达感官体验。'
      },
      { 
        instruction: '分类整理', 
        guidance: '把所有物品拿出来，一起按质地分类：软的一堆、硬的一堆；光滑的一堆、粗糙的一堆。可以用两个盒子或画两个圈来分类。这个过程帮助孩子整合触觉信息和认知分类能力。可以问"这个应该放在哪一堆？""为什么？"鼓励孩子解释自己的分类逻辑。'
      }
    ]
  },
  {
    id: '6',
    title: '障碍赛跑',
    target: '运动协调',
    duration: '15-20分钟',
    reason: '适合精力旺盛、需要大运动训练的孩子',
    steps: [
      { 
        instruction: '设置障碍', 
        guidance: '用家里的安全物品设置障碍路线：枕头（跨过）、椅子（绕过）、毯子（爬过）、胶带线（走直线）。障碍不要太多，3-5个即可。确保空间安全，移开尖锐物品。可以让孩子参与设置，问"你想把枕头放在哪里？"增加参与感。根据孩子能力调整难度，开始时简单一些。'
      },
      { 
        instruction: '示范路线', 
        guidance: '家长先慢慢走一遍，边走边说："先跨过枕头，然后绕过椅子，最后爬过毯子。"用夸张的动作让孩子看清楚每个步骤。可以重复示范2-3次，让孩子记住路线。如果路线复杂，可以分段示范，先完成前半段，再加入后半段。'
      },
      { 
        instruction: '孩子尝试', 
        guidance: '鼓励孩子尝试，不要催促。如果孩子忘记下一步，给予提示："接下来要绕过椅子哦！"如果孩子做错了，不要批评，而是说"没关系，我们再试一次！"可以在旁边陪伴，必要时提供身体辅助（如扶着手）。每完成一个障碍就鼓励："太棒了！继续加油！"'
      },
      { 
        instruction: '增加难度', 
        guidance: '当孩子熟练后，可以逐步增加挑战：加快速度、增加障碍数量、倒着走、单脚跳等。也可以加入竞赛元素："我们比比谁更快！"或者计时："这次用了10秒，下次能更快吗？"但要注意不要让孩子过度疲劳或沮丧，保持游戏的趣味性。可以设置"休息站"，让孩子在中途喝水休息。'
      }
    ]
  },
  {
    id: '7',
    title: '玩具排列游戏',
    target: '秩序感',
    duration: '10-15分钟',
    reason: '适合喜欢秩序、需要建立规则意识的孩子',
    steps: [
      { 
        instruction: '准备玩具', 
        guidance: '选择5-10个不同颜色、大小、形状的玩具（如积木、小汽车、动物玩偶）。对于喜欢秩序的孩子，这个游戏会让他们很有成就感。准备一个平坦的表面（桌子或地板），确保有足够的空间排列。可以准备一些辅助工具如小盒子、线条（用胶带贴）来帮助排列。'
      },
      { 
        instruction: '按规则排列', 
        guidance: '先从简单的规则开始，如"按颜色排列：红色、蓝色、红色、蓝色"或"按大小排列：大、中、小"。家长先示范排列前几个，然后让孩子继续。可以边排边说出规则："红色、蓝色、接下来应该是什么颜色？"如果孩子排错了，不要立即纠正，而是问"我们看看，这个规则是什么？"引导孩子自己发现。'
      },
      { 
        instruction: '打乱重排', 
        guidance: '完成一种排列后，说"现在我们换一种方法排列！"可以按形状、按类型（动物一组、车一组）、按功能等。让孩子参与决定新的规则："这次我们按什么排列呢？"打乱时可以让孩子帮忙，增加参与感。每次重排都是一次新的认知挑战，帮助孩子理解同一组物品可以有多种分类方式。'
      },
      { 
        instruction: '创造规则', 
        guidance: '最后，鼓励孩子自己创造排列规则。问"你想怎么排列这些玩具？"接受孩子的任何规则，即使看起来不合逻辑。如果孩子说不出规则，可以观察他的排列，然后描述出来："哦，你把所有会动的放在一起了！"帮助孩子意识到自己的分类逻辑。这个过程培养创造性思维和规则意识。'
      }
    ]
  },
  {
    id: '8',
    title: '故事接龙',
    target: '逻辑思维',
    duration: '15-20分钟',
    reason: '适合语言能力较好、需要提升逻辑思维的孩子',
    steps: [
      { 
        instruction: '开始故事', 
        guidance: '家长说一个简单的开头，使用孩子熟悉的元素。例如："从前有一只小兔子，它住在森林里。"或者用孩子喜欢的角色："小猪佩奇今天要去公园玩。"开头要简单明了，为孩子留下续编的空间。可以用图片或玩具作为道具，帮助孩子理解和想象。'
      },
      { 
        instruction: '孩子接龙', 
        guidance: '鼓励孩子续编故事："然后呢？小兔子做了什么？"如果孩子不知道说什么，给予选择："小兔子是去找朋友，还是去找食物？"接受孩子的任何想法，即使不合逻辑也没关系。如果孩子说"小兔子飞到天上了"，可以说"哇，小兔子会飞！真厉害！"然后继续："它在天上看到了什么？"'
      },
      { 
        instruction: '轮流讲述', 
        guidance: '建立明确的轮流规则："我说一句，你说一句。"可以用手势或道具（如传递一个"故事棒"）来标记轮次。家长的部分要简短，给孩子更多机会。如果孩子说得很长，不要打断，耐心听完。如果孩子说得很短，可以追问："然后呢？""为什么？"帮助孩子扩展思路。'
      },
      { 
        instruction: '总结故事', 
        guidance: '故事结束后，一起回顾："我们的故事讲了什么？"帮助孩子回忆情节："首先小兔子做了什么？然后呢？最后呢？"可以画出故事的主要情节，或者用玩具重演。问孩子："你最喜欢故事的哪一部分？""如果再讲一次，你想改变什么？"这个过程培养记忆力、逻辑思维和叙事能力。'
      }
    ]
  },
  {
    id: '9',
    title: '角色扮演游戏',
    target: '情绪思考',
    duration: '20-25分钟',
    reason: '适合需要提升情绪理解和社交能力的孩子',
    steps: [
      { 
        instruction: '选择角色', 
        guidance: '让孩子选择想扮演的角色，可以是动物、职业（医生、老师）、家庭成员、或动画角色。准备简单的道具（帽子、玩具听诊器、围裙等）增加真实感。如果孩子不知道选什么，提供2-3个选项："你想当医生还是消防员？"尊重孩子的选择，即使他每次都选同一个角色。'
      },
      { 
        instruction: '设定情境', 
        guidance: '创造简单的情境，与日常生活相关。例如："小熊生病了，需要看医生"或"娃娃饿了，我们给她做饭吧"。情境要有明确的问题需要解决，这样孩子才有动机参与。可以用玩偶或毛绒玩具作为"病人"或"客人"，降低社交压力。家长扮演配角，引导情节发展。'
      },
      { 
        instruction: '演绎互动', 
        guidance: '在角色扮演中，引导孩子表达和识别情绪。例如："小熊肚子疼，它感觉怎么样？""它是开心还是难过？"示范情绪表达："哎呀，我好疼啊！"用夸张的表情和语气。鼓励孩子用语言和动作表达角色的感受。如果孩子说"小熊哭了"，追问"为什么哭？""我们怎么帮助它？"'
      },
      { 
        instruction: '讨论感受', 
        guidance: '游戏结束后，脱离角色，讨论刚才的情境。问"小熊为什么难过？""医生怎么帮助它的？""最后小熊感觉怎么样？"帮助孩子理解情绪的因果关系。也可以问孩子自己的感受："你扮演医生的时候，感觉怎么样？"连接角色情绪和真实情绪。可以画出不同的表情，帮助孩子识别情绪。'
      }
    ]
  },
  {
    id: '10',
    title: '拼图挑战',
    target: '认知能力',
    duration: '15-20分钟',
    reason: '适合视觉空间能力强、需要提升问题解决能力的孩子',
    steps: [
      { 
        instruction: '选择拼图', 
        guidance: '根据孩子的能力选择合适难度的拼图。初学者：4-6块大块拼图；进阶：12-24块；高级：50块以上。选择孩子感兴趣的主题（动物、车辆、动画角色）。确保拼图块大小适合孩子的手部操作。准备一个平坦、光线充足的工作区域。可以准备拼图垫或托盘，方便移动和保存进度。'
      },
      { 
        instruction: '观察图案', 
        guidance: '开始前，和孩子一起仔细观察完整图案。问"你看到了什么？""有哪些颜色？""这是什么动物/东西？"指出图案的主要特征："看，这里有一只大象，它的耳朵很大。"帮助孩子建立整体印象。可以讨论拼图策略："我们先找边缘的，还是先找某个颜色的？"'
      },
      { 
        instruction: '分类拼接', 
        guidance: '教孩子拼图策略：先找四个角、再找边缘、然后按颜色或图案分类。示范如何旋转拼图块找到正确方向。当孩子尝试时，给予具体的提示："这块是蓝色的，可能是天空的一部分"或"这块有直边，可能是边缘"。如果孩子受挫，提供帮助："我们一起找这块的位置"。庆祝小成功："太好了！你找到了正确的位置！"'
      },
      { 
        instruction: '完成庆祝', 
        guidance: '拼图完成后，热情庆祝："你做到了！我们完成了！"一起欣赏完成的作品，回顾过程："你记得最难的是哪一块吗？""你是怎么找到它的位置的？"拍照留念，或者把拼图保留一段时间展示。问孩子："下次你想挑战更难的拼图吗？"如果孩子喜欢，可以把拼图粘起来装框，增加成就感。讨论拼图教会我们的：耐心、坚持、问题解决。'
      }
    ]
  }
];

/**
 * 简单的关键词检索（模拟向量检索）
 */
export const searchGamesFromLibrary = async (
  query: string,
  topK: number = 5
): Promise<Game[]> => {
  // 简化处理：关键词匹配
  // 实际应该使用向量数据库（如 Pinecone, Weaviate）或通义千问的 embedding API
  
  const keywords = query.toLowerCase().split(/[,，\s]+/).filter(k => k.length > 0);
  
  const scoredGames = GAMES_LIBRARY.map(game => {
    let score = 0;
    const gameText = `${game.title} ${game.target} ${game.reason}`.toLowerCase();
    
    keywords.forEach(keyword => {
      if (gameText.includes(keyword)) {
        score += 1;
      }
    });
    
    // 额外加分：匹配步骤内容
    game.steps.forEach(step => {
      const stepText = `${step.instruction} ${step.guidance}`.toLowerCase();
      keywords.forEach(keyword => {
        if (stepText.includes(keyword)) {
          score += 0.5;
        }
      });
    });
    
    return { game, score };
  });
  
  // 按分数排序，返回前 topK 个
  const results = scoredGames
    .filter(item => item.score > 0) // 只返回有匹配的
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .map(item => item.game);
  
  // 如果没有匹配，返回随机几个
  if (results.length === 0) {
    return GAMES_LIBRARY.slice(0, topK);
  }
  
  return results;
};

/**
 * 获取所有游戏
 */
export const getAllGames = (): Game[] => {
  return GAMES_LIBRARY;
};

/**
 * 根据ID获取游戏
 */
export const getGameById = (id: string): Game | undefined => {
  return GAMES_LIBRARY.find(game => game.id === id);
};

/**
 * 根据目标能力筛选游戏
 */
export const getGamesByTarget = (target: string): Game[] => {
  return GAMES_LIBRARY.filter(game => 
    game.target.toLowerCase().includes(target.toLowerCase())
  );
};

/**
 * 未来扩展：接入真正的向量检索
 * 使用通义千问的 text-embedding API
 */
export const searchGamesWithEmbedding = async (
  query: string,
  topK: number = 5
): Promise<Game[]> => {
  // TODO: 接入通义千问的 text-embedding API
  // 1. 获取 query 的 embedding
  // 2. 在游戏库的 embeddings 中检索
  // 3. 返回最相关的游戏
  
  console.warn('Embedding-based search not implemented yet, falling back to keyword search');
  return searchGamesFromLibrary(query, topK);
};

/**
 * 联网搜索游戏（使用阿里云 Web-Search）
 * 实时从互联网搜索适合的地板游戏
 */
export const searchGamesOnline = async (
  query: string,
  childContext: string = '',
  topK: number = 5
): Promise<Game[]> => {
  try {
    console.log('🌐 开始联网搜索游戏...');
    
    // 构建搜索提示词
    const searchPrompt = buildSearchPrompt(query, childContext);
    
    // 调用通义千问 + Web-Search
    const response = await fetch(WEB_SEARCH_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${DASHSCOPE_API_KEY}`,
        'X-DashScope-SSE': 'disable'
      },
      body: JSON.stringify({
        model: 'qwen-plus',
        input: {
          messages: [
            {
              role: 'system',
              content: `你是一位专业的 DIR/Floortime 游戏设计师。请从互联网搜索适合自闭症儿童的地板游戏，并按照指定的 JSON 格式返回。`
            },
            {
              role: 'user',
              content: searchPrompt
            }
          ]
        },
        parameters: {
          result_format: 'message',
          enable_search: true, // 启用联网搜索
          temperature: 0.7,
          max_tokens: 2000
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ 联网搜索失败:', response.status, errorText);
      throw new Error(`Web search failed: ${response.statusText}`);
    }

    const data = await response.json();
    console.log('📡 API 响应:', data);
    
    const content = data.output?.choices?.[0]?.message?.content || '';
    
    if (!content) {
      console.warn('⚠️  API 返回内容为空');
      throw new Error('Empty response from API');
    }
    
    console.log('📝 返回内容:', content.substring(0, 200) + '...');
    
    // 解析返回的游戏信息
    const games = parseGamesFromSearchResult(content);
    
    console.log(`✅ 解析到 ${games.length} 个游戏`);
    
    // 如果联网搜索没有结果，回退到本地库
    if (games.length === 0) {
      console.warn('⚠️  联网搜索无结果，回退到本地游戏库');
      return searchGamesFromLibrary(query, topK);
    }
    
    return games.slice(0, topK);
  } catch (error) {
    console.error('❌ 联网搜索出错:', error);
    // 出错时回退到本地库
    console.log('🔄 回退到本地游戏库');
    return searchGamesFromLibrary(query, topK);
  }
};

/**
 * 混合搜索：本地库 + 联网搜索
 * 优先使用本地库，如果不够再联网搜索补充
 */
export const searchGamesHybrid = async (
  query: string,
  childContext: string = '',
  topK: number = 5
): Promise<Game[]> => {
  try {
    // 先从本地库搜索
    const localGames = await searchGamesFromLibrary(query, topK);
    
    // 如果本地库结果充足，直接返回
    if (localGames.length >= topK) {
      return localGames;
    }
    
    // 否则联网搜索补充
    const onlineGames = await searchGamesOnline(query, childContext, topK - localGames.length);
    
    // 合并结果，去重
    const allGames = [...localGames];
    const existingIds = new Set(localGames.map(g => g.id));
    
    for (const game of onlineGames) {
      if (!existingIds.has(game.id)) {
        allGames.push(game);
        existingIds.add(game.id);
      }
    }
    
    return allGames.slice(0, topK);
  } catch (error) {
    console.error('Hybrid search failed:', error);
    return searchGamesFromLibrary(query, topK);
  }
};

/**
 * 构建搜索提示词
 */
function buildSearchPrompt(query: string, childContext: string): string {
  return `
请从互联网搜索适合自闭症儿童的 DIR/Floortime 地板游戏，要求：

【搜索条件】
${query}

${childContext ? `【儿童情况】\n${childContext}\n` : ''}

【要求】
1. 搜索适合自闭症儿童的地板游戏、感统游戏、互动游戏
2. 游戏应该基于 DIR/Floortime 理念
3. 游戏应该有明确的训练目标
4. 游戏步骤要具体可操作

【返回格式】
请以 JSON 数组格式返回，每个游戏包含：
- title: 游戏名称
- target: 训练目标
- duration: 游戏时长
- reason: 适合理由
- steps: 游戏步骤数组，每个步骤包含 instruction 和 guidance

示例：
\`\`\`json
[
  {
    "title": "游戏名称",
    "target": "训练目标",
    "duration": "15-20分钟",
    "reason": "适合理由",
    "steps": [
      {"instruction": "步骤1", "guidance": "引导要点1"},
      {"instruction": "步骤2", "guidance": "引导要点2"}
    ]
  }
]
\`\`\`

请返回 3-5 个游戏。
`;
}

/**
 * 解析搜索结果中的游戏信息
 */
function parseGamesFromSearchResult(content: string): Game[] {
  try {
    console.log('🔍 开始解析游戏信息...');
    console.log('原始内容长度:', content.length);
    
    // 尝试提取 JSON 内容
    const jsonMatch = content.match(/```json\s*([\s\S]*?)\s*```/) || 
                     content.match(/\[[\s\S]*?\]/);
    
    if (!jsonMatch) {
      console.warn('⚠️  未找到 JSON 格式内容');
      console.log('内容预览:', content.substring(0, 500));
      return [];
    }
    
    const jsonStr = jsonMatch[1] || jsonMatch[0];
    console.log('提取的 JSON:', jsonStr.substring(0, 200) + '...');
    
    const gamesData = JSON.parse(jsonStr);
    
    if (!Array.isArray(gamesData)) {
      console.warn('⚠️  解析的数据不是数组');
      return [];
    }
    
    console.log(`✅ 成功解析 ${gamesData.length} 个游戏`);
    
    // 转换为 Game 类型
    const games = gamesData.map((game, index) => {
      const gameObj: Game = {
        id: `online_${Date.now()}_${index}`,
        title: game.title || '未命名游戏',
        target: game.target || '综合训练',
        duration: game.duration || '15-20分钟',
        reason: game.reason || '',
        isVR: game.isVR || false,
        steps: Array.isArray(game.steps) ? game.steps.map((step: any) => ({
          instruction: step.instruction || step,
          guidance: step.guidance || '请根据孩子的反应灵活调整'
        })) : []
      };
      
      console.log(`  ${index + 1}. ${gameObj.title} (${gameObj.steps.length} 个步骤)`);
      return gameObj;
    });
    
    return games;
  } catch (error) {
    console.error('❌ 解析游戏信息失败:', error);
    console.log('错误详情:', error instanceof Error ? error.message : String(error));
    return [];
  }
}
