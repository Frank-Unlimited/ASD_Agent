import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BookOpen, Star } from 'lucide-react';
import { RAGResult } from '../types';

interface RAGResultsProps {
  results: RAGResult[];
  query?: string;
}

/**
 * 提取查询关键词中的关键词标签
 * 支持中文长句，智能分词
 */
function extractKeywords(query: string): string[] {
  if (!query) return [];
  
  // 移除标点符号，按空格、逗号、顿号等分割
  const cleaned = query.replace(/[，。、；：！？""''（）【】《》\s]+/g, ' ').trim();
  
  // 分割并过滤空字符串
  const words = cleaned.split(/\s+/).filter(k => k.length > 0);
  
  // 如果分词后只有1-2个词，且总长度很长，说明是长句，截取前30字
  if (words.length <= 2 && query.length > 30) {
    return [query.substring(0, 30) + '...'];
  }
  
  // 否则返回前5个关键词
  return words.slice(0, 5);
}

export const RAGResults: React.FC<RAGResultsProps> = ({ results, query }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!results || results.length === 0) {
    return null;
  }

  const keywords = extractKeywords(query || '');

  return (
    <div className="rag-results">
      <button
        className="rag-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="rag-toggle-text">
          📚 知识库检索：
          {keywords.length > 0 ? (
            <span className="keywords-container">
              {keywords.map((keyword, idx) => (
                <span key={idx} className="keyword-tag">【{keyword}】</span>
              ))}
            </span>
          ) : (
            ` 专业知识 (${results.length})`
          )}
        </span>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isExpanded && (
        <div className="rag-results-list">
          {results.map((result, index) => (
            <div key={index} className="rag-item">
              <div className="rag-header">
                <div className="rag-doc-info">
                  <BookOpen size={14} className="doc-icon" />
                  <span className="doc-name">{result.docName}</span>
                </div>
                <div className="rag-score">
                  <Star size={12} className="star-icon" />
                  <span className="score-text">{(result.score * 100).toFixed(0)}%</span>
                </div>
              </div>
              <div className="rag-text">{result.text}</div>
            </div>
          ))}
        </div>
      )}

      <style>{`
        .rag-results {
          margin: 12px 0;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          overflow: hidden;
          background: #fef3c7;
        }

        .rag-toggle {
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

        .rag-toggle:hover {
          background: #fde68a;
        }

        .rag-toggle-text {
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
          color: #d97706;
          white-space: nowrap;
        }

        .rag-results-list {
          border-top: 1px solid #fbbf24;
          background: white;
          max-height: 500px;
          overflow-y: auto;
          padding: 12px 14px;
        }

        .rag-item {
          padding: 12px;
          margin-bottom: 12px;
          border-radius: 8px;
          background: #fffbeb;
          border-left: 3px solid #f59e0b;
        }

        .rag-item:last-child {
          margin-bottom: 0;
        }

        .rag-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-bottom: 8px;
        }

        .rag-doc-info {
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .doc-icon {
          color: #d97706;
          flex-shrink: 0;
        }

        .doc-name {
          font-size: 12px;
          font-weight: 600;
          color: #92400e;
        }

        .rag-score {
          display: flex;
          align-items: center;
          gap: 4px;
          padding: 2px 8px;
          background: #fef3c7;
          border-radius: 12px;
        }

        .star-icon {
          color: #f59e0b;
        }

        .score-text {
          font-size: 11px;
          font-weight: 600;
          color: #d97706;
        }

        .rag-text {
          font-size: 13px;
          color: #374151;
          line-height: 1.6;
          white-space: pre-wrap;
        }

        /* 滚动条样式 */
        .rag-results-list::-webkit-scrollbar {
          width: 6px;
        }

        .rag-results-list::-webkit-scrollbar-track {
          background: #fef3c7;
        }

        .rag-results-list::-webkit-scrollbar-thumb {
          background: #fbbf24;
          border-radius: 3px;
        }

        .rag-results-list::-webkit-scrollbar-thumb:hover {
          background: #f59e0b;
        }
      `}</style>
    </div>
  );
};
