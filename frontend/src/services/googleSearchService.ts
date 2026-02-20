/**
 * Google Custom Search API 服务
 * 提供真正的联网搜索功能（不通过 LLM）
 * 
 * 使用说明：
 * 1. 访问 https://developers.google.com/custom-search/v1/introduction
 * 2. 创建 API Key：https://console.cloud.google.com/apis/credentials
 * 3. 创建 Programmable Search Engine：https://programmablesearchengine.google.com/
 * 4. 将 API Key 和 Search Engine ID 配置到 .env 文件
 * 
 * 免费额度：每天 100 次查询
 */

export interface GoogleSearchResult {
  title: string;
  link: string;
  snippet: string;
  displayLink: string;
}

export interface GoogleSearchResponse {
  items?: GoogleSearchResult[];
  searchInformation?: {
    totalResults: string;
    searchTime: number;
  };
}

class GoogleSearchService {
  private apiKey: string;
  private searchEngineId: string;
  private baseUrl = 'https://www.googleapis.com/customsearch/v1';

  constructor() {
    this.apiKey = import.meta.env.VITE_GOOGLE_SEARCH_API_KEY || '';
    this.searchEngineId = import.meta.env.VITE_GOOGLE_SEARCH_ENGINE_ID || '';

    if (!this.apiKey || !this.searchEngineId) {
      console.warn('Google Search API 未配置。请在 .env 中设置 VITE_GOOGLE_SEARCH_API_KEY 和 VITE_GOOGLE_SEARCH_ENGINE_ID');
    }
  }

  /**
   * 检查是否已配置 API
   */
  isConfigured(): boolean {
    return !!(this.apiKey && this.searchEngineId);
  }

  /**
   * 执行搜索
   * @param query 搜索关键词
   * @param options 搜索选项
   * @returns 搜索结果
   */
  async search(
    query: string,
    options?: {
      num?: number;        // 返回结果数量（1-10，默认10）
      start?: number;      // 起始位置（默认1）
      lr?: string;         // 语言限制（如 'lang_zh-CN'）
      safe?: 'off' | 'medium' | 'high';  // 安全搜索
    }
  ): Promise<GoogleSearchResult[]> {
    if (!this.isConfigured()) {
      console.warn('Google Search API 未配置，返回空结果');
      return [];
    }

    try {
      const params = new URLSearchParams({
        key: this.apiKey,
        cx: this.searchEngineId,
        q: query,
        num: String(options?.num || 10),
        start: String(options?.start || 1),
        lr: options?.lr || 'lang_zh-CN',
        safe: options?.safe || 'off'
      });

      const url = `${this.baseUrl}?${params.toString()}`;
      
      console.log('🔍 Google Search:', query);
      
      const response = await fetch(url);

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Google Search API error: ${response.status} - ${errorText}`);
      }

      const data: GoogleSearchResponse = await response.json();

      if (!data.items || data.items.length === 0) {
        console.warn('⚠️  Google Search 无结果');
        return [];
      }

      console.log(`✅ Google Search 返回 ${data.items.length} 个结果`);
      
      return data.items;
    } catch (error) {
      console.error('❌ Google Search 失败:', error);
      return [];
    }
  }

  /**
   * 搜索并格式化为文本摘要
   * @param query 搜索关键词
   * @param maxResults 最多返回结果数
   * @returns 格式化的文本摘要
   */
  async searchAndFormat(query: string, maxResults: number = 5): Promise<string> {
    const results = await this.search(query, { num: maxResults });

    if (results.length === 0) {
      return '';
    }

    return results
      .map((result, index) => 
        `${index + 1}. ${result.title}\n   ${result.snippet}\n   来源: ${result.displayLink}`
      )
      .join('\n\n');
  }
}

// 导出单例
export const googleSearchService = new GoogleSearchService();
