/**
 * 阿里云百炼 RAG 知识库检索服务（前端客户端）
 * 通过后端 rag_service.py 代理调用
 */

export interface RAGNode {
  text: string;
  score: number;
  metadata: {
    doc_name?: string;
    title?: string;
    doc_id?: string;
    image_url?: string[];
    [key: string]: any;
  };
}

export interface RAGSearchResponse {
  nodes: RAGNode[];
  success: boolean;
  message?: string;
  request_id?: string;
}

class AlibabaRAGService {
  private baseUrl = import.meta.env.VITE_RAG_SERVICE_URL || 'http://localhost:8001';

  /**
   * 检查服务是否可用
   */
  async isConfigured(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/healthcheck`, {
        method: 'GET',
      });
      const data = await response.json();
      return data.status === 'healthy' && data.client_ready;
    } catch (error) {
      console.warn('RAG 服务不可用:', error);
      return false;
    }
  }

  /**
   * 检索知识库
   */
  async search(
    query: string,
    options?: {
      indexId?: string;
      topK?: number;
      enableReranking?: boolean;
      rerankMinScore?: number;
      denseSimilarityTopK?: number;
      sparseSimilarityTopK?: number;
    }
  ): Promise<RAGNode[]> {
    try {
      console.log('🔍 RAG 检索:', query);

      const response = await fetch(`${this.baseUrl}/search`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          index_id: options?.indexId,
          top_k: options?.topK || 5,
          enable_reranking: options?.enableReranking !== false,
          rerank_min_score: options?.rerankMinScore || 0.20,
          dense_similarity_top_k: options?.denseSimilarityTopK || 50,
          sparse_similarity_top_k: options?.sparseSimilarityTopK || 50,
        }),
      });

      if (!response.ok) {
        throw new Error(`RAG API 错误: ${response.status}`);
      }

      const data: RAGSearchResponse = await response.json();

      if (!data.success) {
        console.warn('⚠️  RAG 检索失败:', data.message);
        return [];
      }

      console.log(`✅ RAG 返回 ${data.nodes.length} 个结果`);
      return data.nodes;
    } catch (error) {
      console.error('❌ RAG 检索失败:', error);
      return [];
    }
  }

  /**
   * 检索并格式化为文本摘要
   */
  async searchAndFormat(query: string, topK: number = 5): Promise<string> {
    const nodes = await this.search(query, { topK });

    if (nodes.length === 0) {
      return '';
    }

    return nodes
      .map((node, index) => {
        const docName = node.metadata?.doc_name || node.metadata?.title || '未知文档';
        const score = ((node.score || 0) * 100).toFixed(1);
        // 保持完整文本供 LLM 使用
        return `${index + 1}. [相关度: ${score}%] ${node.text}\n   来源: ${docName}`;
      })
      .join('\n\n');
  }
}

// 导出单例
export const ragService = new AlibabaRAGService();
