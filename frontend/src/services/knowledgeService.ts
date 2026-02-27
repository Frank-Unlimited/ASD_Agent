/**
 * 统一知识检索服务
 * 并行调用联网搜索 + RAG 知识库，合并结果
 */

import { bochaSearchService } from './bochaSearchService';
import { ragService } from './ragService';

export interface KnowledgeSearchResult {
  web: string;       // 联网搜索结果
  rag: string;       // RAG 结果
  combined: string;  // 合并后的结果
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
        ? bochaSearchService.searchAndFormat(query, options?.webCount || 5)
        : Promise.resolve(''),
      useRAG
        ? ragService.searchAndFormat(query, options?.ragCount || 5)
        : Promise.resolve(''),
    ]);

    const web = webResult.status === 'fulfilled' ? webResult.value : '';
    const rag = ragResult.status === 'fulfilled' ? ragResult.value : '';

    return {
      web,
      rag,
      combined: this.mergeResults(web, rag),
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
