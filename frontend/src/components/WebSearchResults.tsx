import React, { useState } from 'react';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { WebSearchResult } from '../types';

interface WebSearchResultsProps {
  results: WebSearchResult[];
  query?: string; // 查询关键词
}

/**
 * 提取查询关键词中的关键词标签
 * 例如："DIR/Floortime 视觉感统游戏设计 2岁儿童 彩色积木"
 * 提取为：["DIR/Floortime", "视觉感统游戏设计", "2岁儿童", "彩色积木"]
 */
function extractKeywords(query: string): string[] {
  if (!query) return [];
  
  // 按空格分割，过滤空字符串
  const keywords = query.split(/\s+/).filter(k => k.length > 0);
  
  // 限制显示前5个关键词
  return keywords.slice(0, 5);
}

export const WebSearchResults: React.FC<WebSearchResultsProps> = ({ results, query }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!results || results.length === 0) {
    return null;
  }

  const keywords = extractKeywords(query || '');

  return (
    <div className="web-search-results">
      <button
        className="search-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="search-toggle-text">
          🔍 联网检索：
          {keywords.length > 0 ? (
            <span className="keywords-container">
              {keywords.map((keyword, idx) => (
                <span key={idx} className="keyword-tag">【{keyword}】</span>
              ))}
            </span>
          ) : (
            ` 参考来源 (${results.length})`
          )}
        </span>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isExpanded && (
        <div className="search-results-list">
          {results.map((result, index) => (
            <a
              key={index}
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="search-result-item"
            >
              <div className="result-header">
                <span className="result-number">{index + 1}</span>
                <span className="result-title">{result.name}</span>
                <ExternalLink size={14} className="external-icon" />
              </div>
              <p className="result-snippet">{result.snippet}</p>
              <span className="result-source">{result.siteName}</span>
            </a>
          ))}
        </div>
      )}

      <style>{`
        .web-search-results {
          margin: 12px 0;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          overflow: hidden;
          background: #f9fafb;
        }

        .search-toggle {
          width: 100%;
          padding: 10px 14px;
          display: flex;
          align-items: center;
          justify-content: space-between;
          background: transparent;
          border: none;
          cursor: pointer;
          font-size: 14px;
          color: #374151;
          transition: background-color 0.2s;
        }

        .search-toggle:hover {
          background: #f3f4f6;
        }

        .search-toggle-text {
          font-weight: 500;
          display: flex;
          align-items: center;
          gap: 4px;
          flex-wrap: wrap;
        }

        .keywords-container {
          display: inline-flex;
          align-items: center;
          gap: 4px;
          flex-wrap: wrap;
        }

        .keyword-tag {
          display: inline-block;
          font-size: 12px;
          font-weight: 500;
          color: #4f46e5;
          white-space: nowrap;
        }

        .search-results-list {
          border-top: 1px solid #e5e7eb;
          background: white;
          max-height: 400px;
          overflow-y: auto;
        }

        .search-result-item {
          display: block;
          padding: 12px 14px;
          border-bottom: 1px solid #f3f4f6;
          text-decoration: none;
          color: inherit;
          transition: background-color 0.2s;
        }

        .search-result-item:last-child {
          border-bottom: none;
        }

        .search-result-item:hover {
          background: #f9fafb;
        }

        .result-header {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 6px;
        }

        .result-number {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          width: 20px;
          height: 20px;
          background: #e5e7eb;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          color: #6b7280;
          flex-shrink: 0;
        }

        .result-title {
          flex: 1;
          font-weight: 500;
          font-size: 14px;
          color: #1f2937;
          line-height: 1.4;
        }

        .external-icon {
          color: #9ca3af;
          flex-shrink: 0;
        }

        .result-snippet {
          font-size: 13px;
          color: #6b7280;
          line-height: 1.5;
          margin: 0 0 6px 28px;
        }

        .result-source {
          display: inline-block;
          margin-left: 28px;
          font-size: 12px;
          color: #9ca3af;
        }

        /* 滚动条样式 */
        .search-results-list::-webkit-scrollbar {
          width: 6px;
        }

        .search-results-list::-webkit-scrollbar-track {
          background: #f3f4f6;
        }

        .search-results-list::-webkit-scrollbar-thumb {
          background: #d1d5db;
          border-radius: 3px;
        }

        .search-results-list::-webkit-scrollbar-thumb:hover {
          background: #9ca3af;
        }
      `}</style>
    </div>
  );
};
