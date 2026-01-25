// AI配置检查脚本
require('dotenv').config();

console.log('🔍 检查AI配置...\n');

const provider = process.env.AI_PROVIDER || 'deepseek';
console.log('当前AI提供商:', provider);
console.log('');

if (provider === 'deepseek') {
  console.log('📌 DeepSeek配置:');
  const apiKey = process.env.DEEPSEEK_API_KEY;
  const baseUrl = process.env.DEEPSEEK_BASE_URL;
  
  console.log('  API Key:', apiKey ? `${apiKey.substring(0, 10)}...` : '❌ 未设置');
  console.log('  Base URL:', baseUrl || '❌ 未设置');
  
  if (!apiKey || apiKey === 'your-deepseek-api-key-here') {
    console.log('\n❌ DeepSeek API Key 未正确配置！');
    console.log('\n解决方案:');
    console.log('1. 访问 https://platform.deepseek.com/ 注册账号');
    console.log('2. 获取API Key');
    console.log('3. 在 .env 文件中设置: DEEPSEEK_API_KEY=你的key');
    console.log('\n或者切换到OpenAI:');
    console.log('在 .env 文件中设置: AI_PROVIDER=openai');
  } else {
    console.log('\n✅ DeepSeek配置看起来正确');
  }
} else {
  console.log('📌 OpenAI配置:');
  const apiKey = process.env.OPENAI_API_KEY;
  
  console.log('  API Key:', apiKey ? `${apiKey.substring(0, 10)}...` : '❌ 未设置');
  
  if (!apiKey || apiKey === 'your-openai-api-key-here') {
    console.log('\n❌ OpenAI API Key 未正确配置！');
    console.log('\n解决方案:');
    console.log('1. 访问 https://platform.openai.com/ 注册账号');
    console.log('2. 获取API Key');
    console.log('3. 在 .env 文件中设置: OPENAI_API_KEY=你的key');
  } else {
    console.log('\n✅ OpenAI配置看起来正确');
  }
}

console.log('\n💡 提示:');
console.log('- 修改 .env 文件后需要重启服务器');
console.log('- 确保API Key有足够的额度');
console.log('- 检查网络连接是否正常');
