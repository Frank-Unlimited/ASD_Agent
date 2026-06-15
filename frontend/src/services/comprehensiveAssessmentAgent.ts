/**
 * 综合评估 Agent（React 模式）
 * 生成专业的医疗评估报告
 */

import { qwenStreamClient, QwenMessage, ToolDefinition } from './qwenStreamClient';
import { fetchMemoryFacts, formatMemoryFactsForPrompt } from './memoryService';
import { knowledgeService } from './knowledgeService';
import { getAccountId } from './accountService';
import { COMPREHENSIVE_ASSESSMENT_REPORT_SCHEMA } from './comprehensiveAssessmentSchemas';
import type { ComprehensiveAssessmentReport } from '../types';
import type { ChildProfile, UserInterestProfile, UserAbilityProfile, WebSearchResult } from '../types';

const MAX_REACT_ITERATIONS = 10;

/**
 * ReAct 循环进度事件
 */
export type ReActProgressEvent =
  | { type: 'tool_call'; toolName: 'fetch_memory' | 'fetch_knowledge'; query: string }
  | { type: 'tool_result'; toolName: 'fetch_memory' | 'fetch_knowledge'; result: string; searchResults?: WebSearchResult[]; memoryResults?: any[]; ragResults?: any[] };

export type OnReActProgress = (event: ReActProgressEvent) => void;

/**
 * 清理 LLM 返回的 JSON 字符串
 */
function cleanLLMResponse(response: string): string {
  let cleaned = response;
  cleaned = cleaned.replace(/<think>[\s\S]*?<\/think>/g, '').trim();
  cleaned = cleaned.replace(/^```(?:json)?\s*\n?/i, '').replace(/\n?```\s*$/i, '').trim();
  return cleaned;
}

/**
 * ReAct 循环核心执行器
 */
async function runReActLoop(
  systemPrompt: string,
  userPrompt: string,
  tools: ToolDefinition[],
  toolHandlers: Record<string, (args: Record<string, any>) => Promise<string | { text: string; searchResults?: WebSearchResult[]; memoryResults?: any[]; ragResults?: any[] }>>,
  onProgress?: OnReActProgress
): Promise<string> {
  const messages: QwenMessage[] = [
    { role: 'system', content: systemPrompt },
    { role: 'user', content: userPrompt }
  ];

  for (let iteration = 0; iteration < MAX_REACT_ITERATIONS; iteration++) {
    console.log(`[ReAct Assessment] 第 ${iteration + 1}/${MAX_REACT_ITERATIONS} 轮`);

    const result = await qwenStreamClient.chatWithTools(messages, tools, {
      temperature: 0.7,
      max_tokens: 4000
    });

    if (result.type === 'content') {
      console.log(`[ReAct Assessment] 第 ${iteration + 1} 轮获得最终答案，循环结束`);
      return result.content;
    }

    // LLM 请求调用工具
    messages.push({
      role: 'assistant',
      content: '',
      tool_calls: result.toolCalls
    });

    // 执行每个工具调用
    for (const toolCall of result.toolCalls) {
      const toolName = toolCall.function.name;
      let toolResult: string = '';

      try {
        const args = JSON.parse(toolCall.function.arguments) as Record<string, any>;
        console.log(`[ReAct Assessment] 执行工具: ${toolName}`, args);

        // 通知 UI：工具被调用
        onProgress?.({
          type: 'tool_call',
          toolName: toolName as 'fetch_memory' | 'fetch_knowledge',
          query: args.query || ''
        });

        const handler = toolHandlers[toolName];
        if (!handler) {
          toolResult = `[错误] 未知工具：${toolName}`;
          console.error(`[ReAct Assessment] 未知工具: ${toolName}`);
        } else {
          const handlerResult = await handler(args);
          let memoryResults: any[] | undefined;
          let ragResults: any[] | undefined;
          let searchResults: WebSearchResult[] | undefined;
          
          // 如果返回对象，提取 text 和结果数据
          if (handlerResult && typeof handlerResult === 'object' && 'text' in handlerResult) {
            toolResult = handlerResult.text;
            searchResults = handlerResult.searchResults;
            memoryResults = (handlerResult as any).memoryResults;
            ragResults = (handlerResult as any).ragResults;
            
            // 通知 UI：工具返回结果
            onProgress?.({
              type: 'tool_result',
              toolName: toolName as 'fetch_memory' | 'fetch_knowledge',
              result: toolResult,
              searchResults,
              memoryResults,
              ragResults
            });
          } else if (typeof handlerResult === 'string') {
            toolResult = handlerResult;
            onProgress?.({
              type: 'tool_result',
              toolName: toolName as 'fetch_memory' | 'fetch_knowledge',
              result: toolResult
            });
          }
          console.log(`[ReAct Assessment] 工具 ${toolName} 返回 ${toolResult.length} 字符`);
        }
      } catch (err) {
        toolResult = `[工具执行失败] ${err instanceof Error ? err.message : String(err)}`;
        console.warn(`[ReAct Assessment] 工具 ${toolName} 执行失败:`, err);
        onProgress?.({
          type: 'tool_result',
          toolName: toolName as 'fetch_memory' | 'fetch_knowledge',
          result: toolResult
        });
      }

      messages.push({
        role: 'tool',
        tool_call_id: toolCall.id,
        name: toolCall.function.name,
        content: toolResult || '（无结果）'
      });
    }
  }

  throw new Error(
    `[ReAct Assessment] 达到最大迭代次数 (${MAX_REACT_ITERATIONS})，未获得最终答案`
  );
}

/**
 * 构建综合评估的工具处理器
 */
function buildAssessmentHandlers(accountId: string) {
  return {
    fetch_memory: async (args: Record<string, any>) => {
      const query = args.query || '';
      console.log('[ReAct Assessment/fetch_memory] 查询:', query);
      const facts = await fetchMemoryFacts(accountId, query, 30);
      
      return {
        text: formatMemoryFactsForPrompt(facts) || '（暂无相关历史记忆）',
        memoryResults: facts
      };
    },
    fetch_knowledge: async (args: Record<string, any>) => {
      const query = args.query || '';
      console.log('[ReAct Assessment/fetch_knowledge] 搜索:', query);
      
      // 并行调用联网搜索 + RAG 知识库
      const result = await knowledgeService.search(query, {
        useWeb: true,
        useRAG: true,
        webCount: 5,
        ragCount: 5
      });
      
      return {
        text: result.combined || '（暂无相关搜索结果）',
        searchResults: result.webResults || [],
        ragResults: result.ragResults || []
      };
    }
  };
}

// 系统提示词
const SYSTEM_PROMPT = `# 角色：儿童发育评估专家

你是一位专业的儿童发育评估专家，负责生成符合医疗标准的孤独症谱系障碍（ASD）儿童综合评估报告。

## 报告目标

这份报告将提交给医院的主治医生，作为：
1. 家庭干预效果的专业记录
2. 医生调整治疗方案的参考依据
3. 家长与医疗团队沟通的桥梁

## 报告标准

参考 ADOS（孤独症诊断观察量表）和 ADI-R（孤独症诊断访谈量表）的专业格式。

## 可用工具

你可以使用以下工具获取数据：
- **fetch_memory**：从记忆系统中检索孩子的历史行为记录、游戏记录等数据
- **fetch_knowledge**：从知识库中检索专业的干预方法、评估标准等信息

## 工作流程

1. 使用 fetch_memory 获取历史数据（行为记录、游戏记录、能力变化等）
2. 使用 fetch_knowledge 获取专业评估标准和干预方法（如需要）
3. 分析数据，生成各个部分的内容
4. 输出完整的 JSON 格式报告

## 输出格式

严格按照以下 JSON Schema 输出（不要包含任何其他文字）：

\`\`\`json
${JSON.stringify(COMPREHENSIVE_ASSESSMENT_REPORT_SCHEMA, null, 2)}
\`\`\`

## 写作要求

1. **专业性**：使用医疗术语，但保持可读性
2. **客观性**：基于数据和观察，避免主观臆断
3. **具体性**：提供具体例子和数据支持
4. **建设性**：既指出挑战，也强调进步和优势
5. **可操作性**：建议要具体、可执行

开始生成报告！`;

// 工具定义（用于 ReAct 模式）
const TOOLS: ToolDefinition[] = [
  {
    type: 'function',
    function: {
      name: 'fetch_memory',
      description: '从记忆系统中检索孩子的历史行为记录、游戏记录等数据',
      parameters: {
        type: 'object' as const,
        properties: {
          query: {
            type: 'string',
            description: '搜索查询，例如："最近3个月的游戏记录"、"社交互动相关的行为"、"能力发展变化"'
          }
        },
        required: ['query']
      }
    }
  },
  {
    type: 'function',
    function: {
      name: 'fetch_knowledge',
      description: '从知识库中检索专业的干预方法、评估标准等信息',
      parameters: {
        type: 'object' as const,
        properties: {
          query: {
            type: 'string',
            description: '知识查询，例如："ADOS评估标准"、"地板时光干预方法"、"ASD儿童发育里程碑"'
          }
        },
        required: ['query']
      }
    }
  }
];

interface GenerateReportOptions {
  childProfile: ChildProfile;
  interestProfile: UserInterestProfile;
  abilityProfile: UserAbilityProfile;
  reportingPeriod?: string;
  onProgress?: (step: string, message: string) => void;
  onToolCall?: (toolName: string, args: any) => void;
}

/**
 * 生成综合评估报告（ReAct 模式）
 */
export async function generateComprehensiveAssessment(
  options: GenerateReportOptions
): Promise<ComprehensiveAssessmentReport> {
  const {
    childProfile,
    interestProfile,
    abilityProfile,
    reportingPeriod,
    onProgress,
    onToolCall
  } = options;

  try {
    console.log('[generateComprehensiveAssessment] 开始 ReAct 评估报告生成:', {
      childName: childProfile.name,
      reportingPeriod
    });

    // 构建用户提示
    const userPrompt = `请为 ${childProfile.name} 生成一份综合评估报告。

**基本信息：**
- 姓名：${childProfile.name}
- 性别：${childProfile.gender}
- 出生日期：${childProfile.birthDate}
- 当前诊断：${childProfile.diagnosis}
${reportingPeriod ? `- 报告周期：${reportingPeriod}` : ''}

**当前能力水平：**
${Object.entries(abilityProfile).map(([dim, score]) => `- ${dim}：${score}/100`).join('\n')}

**兴趣档案（累积分数）：**
${Object.entries(interestProfile).map(([dim, score]) => 
  `- ${dim}：${score.toFixed(1)} 分`
).join('\n')}

请按照以下步骤生成报告：
1. 使用 fetch_memory 获取历史数据（行为记录、游戏记录、能力变化等）
2. 如需要，使用 fetch_knowledge 获取专业评估标准和干预方法
3. 分析数据，生成完整的 JSON 格式报告

开始吧！`;

    console.log('='.repeat(80));
    console.log('[Assessment Agent] System Prompt:');
    console.log(SYSTEM_PROMPT.substring(0, 500) + '...');
    console.log('-'.repeat(80));
    console.log('[Assessment Agent] User Prompt:');
    console.log(userPrompt);
    console.log('='.repeat(80));

    // 创建进度回调包装器
    const progressWrapper: OnReActProgress = (event) => {
      if (event.type === 'tool_call') {
        onProgress?.(event.toolName, `正在${event.toolName === 'fetch_memory' ? '检索历史数据' : '查询知识库'}：${event.query}`);
        onToolCall?.(event.toolName, { query: event.query });
      } else if (event.type === 'tool_result') {
        onProgress?.(event.toolName, `获取到 ${event.result.length} 字符的数据`);
      }
    };

    // 运行 ReAct 循环
    const finalResponse = await runReActLoop(
      SYSTEM_PROMPT,
      userPrompt,
      TOOLS,
      buildAssessmentHandlers(getAccountId()),
      progressWrapper
    );

    console.log('='.repeat(80));
    console.log('[Assessment Agent] 最终响应 (前500字):');
    console.log(finalResponse.substring(0, 500));
    console.log('='.repeat(80));

    // 清理并解析响应
    const cleanedResponse = cleanLLMResponse(finalResponse);
    console.log('[generateComprehensiveAssessment] 清理后响应 (前500字):', cleanedResponse.substring(0, 500));

    const data = JSON.parse(cleanedResponse);
    console.log('[generateComprehensiveAssessment] 解析 JSON 成功');

    // 构建完整报告
    const report: ComprehensiveAssessmentReport = {
      reportId: `assessment_${Date.now()}`,
      childName: childProfile.name,
      assessmentDate: new Date().toISOString().split('T')[0],
      reportingPeriod: reportingPeriod || '最近3个月',
      generatedBy: 'AI辅助生成',
      createdAt: new Date().toISOString(),
      ...data
    };

    console.log('[generateComprehensiveAssessment] 报告生成完成');
    return report;

  } catch (error) {
    console.error('Comprehensive Assessment Failed:', error);
    throw error;
  }
}
