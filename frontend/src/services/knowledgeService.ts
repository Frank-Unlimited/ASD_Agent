/**
 * 统一知识检索服务
 * 并行调用联网搜索 + RAG 知识库，合并结果
 */

import { bochaSearchService, BochaSearchResult } from './bochaSearchService';
import { ragService } from './ragService';
import { WebSearchResult } from '../types';

export interface KnowledgeSearchResult {
  web: string;       // 联网搜索结果（文本）
  rag: string;       // RAG 结果
  combined: string;  // 合并后的结果
  webResults?: WebSearchResult[];  // 联网搜索结果（结构化）
}

class KnowledgeService {
  /**
   * 并行检索联网搜索 + RAG 知识库
   */
  async search(
    query: string,
    options?: {
      useWeb?: boolean;
      useRAG?: boolean;
      webCount?: number;
      ragCount?: number;
    }
  ): Promise<KnowledgeSearchResult> {
    const useWeb = options?.useWeb !== false && bochaSearchService.isConfigured();
    const useRAG = options?.useRAG !== false && await ragService.isConfigured();

    console.log(`[Knowledge Search] 查询: "${query}" (Web: ${useWeb}, RAG: ${useRAG})`);

    // 并行调用
    const [webResult, ragResult] = await Promise.allSettled([
      useWeb
        ? bochaSearchService.search(query, { count: options?.webCount || 5, summary: true })
        : Promise.resolve([]),
      useRAG
        ? ragService.searchAndFormat(query, options?.ragCount || 5)
        : Promise.resolve(''),
    ]);

    const webSearchResults = webResult.status === 'fulfilled' ? webResult.value : [];
    const rag = ragResult.status === 'fulfilled' ? ragResult.value : '';

    // 格式化web搜索结果为文本
    const webText = webSearchResults.length > 0
      ? webSearchResults
          .map((result, index) => {
            const summary = result.summary || result.snippet;
            return `${index + 1}. ${result.name}\n   ${summary}\n   来源: ${result.siteName}`;
          })
          .join('\n\n')
      : '';

    // 转换为WebSearchResult格式
    const webResults: WebSearchResult[] = webSearchResults.map(result => ({
      name: result.name,
      url: result.url,
      snippet: result.snippet,
      siteName: result.siteName
    }));

    return {
      web: webText,
      rag,
      combined: this.mergeResults(webText, rag),
      webResults
    };
  }

  /**
   * 合并结果：RAG 优先（权威性），联网搜索补充（时效性）
   */
  private mergeResults(web: string, rag: string): string {
    console.log('[Knowledge] 合并结果 - Web长度:', web.length, 'RAG长度:', rag.length);
    
    const parts: string[] = [];

    // RAG 结果优先（专业知识库）
    if (rag) {
      parts.push('📚 **专业知识库**：\n' + rag);
    }

    // 联网搜索补充（网络资源）
    if (web) {
      parts.push('🌐 **网络资源**：\n' + web);
    }

    const result = parts.join('\n\n') || '（暂无相关搜索结果）';
    console.log('[Knowledge] 合并后总长度:', result.length);
    return result;
  }
}

// 导出单例
export const knowledgeService = new KnowledgeService();
