/**
 * 博查AI搜索服务
 * 文档：https://open.bocha.cn
 * 
 * 国内可访问，专为AI优化的搜索API
 */

export interface BochaSearchResult {
  name: string;           // 标题
  url: string;            // URL
  snippet: string;        // 简短描述
  summary?: string;       // 详细摘要（当请求时）
  siteName: string;       // 网站名称
  siteIcon?: string;      // 网站图标
  datePublished?: string; // 发布时间
}

export interface BochaSearchResponse {
  code: number;
  log_id: string;
  msg: string | null;
  data: {
    _type: string;
    queryContext: {
      originalQuery: string;
    };
    webPages: {
      webSearchUrl: string;
      totalEstimatedMatches: number;
      value: BochaSearchResult[];
    };
    images?: {
      value: Array<{
        thumbnailUrl: string;
        contentUrl: string;
        hostPageUrl: string;
      }>;
    };
  };
}

class BochaSearchService {
  private apiKey: string;
  private baseUrl = 'https://api.bocha.cn/v1';

  constructor() {
    this.apiKey = import.meta.env.VITE_BOCHA_API_KEY || '';

    if (!this.apiKey) {
      console.warn('博查AI搜索未配置。请在 .env 中设置 VITE_BOCHA_API_KEY');
    }
  }

  /**
   * 检查是否已配置 API
   */
  isConfigured(): boolean {
    return !!this.apiKey;
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
      freshness?: 'noLimit' | 'oneDay' | 'oneWeek' | 'oneMonth' | 'oneYear';
      summary?: boolean;    // 是否返回摘要
      count?: number;       // 返回结果数量（1-50）
      include?: string;     // 指定搜索的网站范围（多个用|分隔）
      exclude?: string;     // 排除搜索的网站范围（多个用|分隔）
    }
  ): Promise<BochaSearchResult[]> {
    if (!this.isConfigured()) {
      console.warn('博查AI搜索未配置，返回空结果');
      return [];
    }

    try {
      const url = `${this.baseUrl}/web-search`;
      
      const payload = {
        query,
        freshness: options?.freshness || 'noLimit',
        summary: options?.summary || false,
        count: options?.count || 10,
        ...(options?.include && { include: options.include }),
        ...(options?.exclude && { exclude: options.exclude }),
      };

      console.log('🔍 博查搜索:', query);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { message: errorText };
        }
        throw new Error(`博查搜索 API 错误: ${response.status} - ${JSON.stringify(errorData)}`);
      }

      const data: BochaSearchResponse = await response.json();

      if (data.code !== 200) {
        throw new Error(`博查搜索失败: ${data.msg || '未知错误'}`);
      }

      if (!data.data?.webPages?.value || data.data.webPages.value.length === 0) {
        console.warn('⚠️  博查搜索无结果');
        return [];
      }

      console.log(`✅ 博查搜索返回 ${data.data.webPages.value.length} 个结果`);
      
      return data.data.webPages.value;
    } catch (error) {
      console.error('❌ 博查搜索失败:', error);
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
    const results = await this.search(query, { 
      count: maxResults,
      summary: true  // 启用摘要
    });

    if (results.length === 0) {
      return '';
    }

    return results
      .map((result, index) => {
        const summary = result.summary || result.snippet;
        return `${index + 1}. ${result.name}\n   ${summary}\n   来源: ${result.siteName} (${result.url})`;
      })
      .join('\n\n');
  }
}

// 导出单例
export const bochaSearchService = new BochaSearchService();
