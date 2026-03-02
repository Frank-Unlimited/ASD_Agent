import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { MemoryResult } from '../types';

interface MemoryResultsProps {
  results: MemoryResult[];
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

/**
 * 格式化日期
 */
function formatDate(dateStr: string | null): string {
  if (!dateStr) return '?';
  return dateStr.slice(0, 10);
}

export const MemoryResults: React.FC<MemoryResultsProps> = ({ results, query }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const keywords = extractKeywords(query || '');
  
  // 即使没有结果也显示查询信息
  const hasResults = results && results.length > 0;
  
  // 分类记忆
  const pending = hasResults ? results.filter(r => r.pending) : [];
  const active = hasResults ? results.filter(r => !r.pending && !r.invalid_at) : [];
  const outdated = hasResults ? results.filter(r => !r.pending && r.invalid_at) : [];

  return (
    <div className="memory-results">
      <button
        className="memory-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="memory-toggle-text">
          🔧 查询记忆：
          {keywords.length > 0 ? (
            <span className="keywords-container">
              {keywords.map((keyword, idx) => (
                <span key={idx} className="keyword-tag">【{keyword}】</span>
              ))}
            </span>
          ) : (
            ` 历史记录`
          )}
          {hasResults && ` (${results.length})`}
        </span>
        {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
      </button>

      {isExpanded && (
        <div className="memory-results-list">
          {!hasResults ? (
            <div className="memory-section">
              <div className="no-results">
                <div className="no-results-icon">🔍</div>
                <div className="no-results-text">暂无相关记录</div>
              </div>
            </div>
          ) : (
            <>
              {/* 最新观察 */}
              {pending.length > 0 && (
                <div className="memory-section">
                  <div className="section-header">
                    <span className="section-title">📝 最新观察 ({pending.length})</span>
                    <span className="section-subtitle">尚未提炼的原始记录</span>
                  </div>
                  {pending.map((result, index) => (
                    <div key={`pending-${index}`} className="memory-item pending">
                      <div className="memory-date">
                        <Clock size={12} />
                        {formatDate(result.valid_at)}
                      </div>
                      <div className="memory-text">{result.text}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* 当前有效事实 */}
              {active.length > 0 && (
                <div className="memory-section">
                  <div className="section-header">
                    <span className="section-title">✅ 当前有效事实 ({active.length})</span>
                    <span className="section-subtitle">已提炼的结构化记忆</span>
                  </div>
                  {active.map((result, index) => (
                    <div key={`active-${index}`} className="memory-item active">
                      <div className="memory-date">
                        <Clock size={12} />
                        {formatDate(result.valid_at)}
                      </div>
                      <div className="memory-text">{result.text}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* 历史事实 */}
              {outdated.length > 0 && (
                <div className="memory-section">
                  <div className="section-header">
                    <span className="section-title">📜 历史事实 ({outdated.length})</span>
                    <span className="section-subtitle">已被新事实覆盖</span>
                  </div>
                  {outdated.map((result, index) => (
                    <div key={`outdated-${index}`} className="memory-item outdated">
                      <div className="memory-date">
                        <Clock size={12} />
                        {formatDate(result.valid_at)} → {formatDate(result.invalid_at)}
                      </div>
                      <div className="memory-text">{result.text}</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}

      <style>{`
        .memory-results {
          margin: 12px 0;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          overflow: hidden;
          background: #f9fafb;
        }

        .memory-toggle {
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

        .memory-toggle:hover {
          background: #f3f4f6;
        }

        .memory-toggle-text {
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
          color: #059669;
          white-space: nowrap;
        }

        .memory-results-list {
          border-top: 1px solid #e5e7eb;
          background: white;
          max-height: 500px;
          overflow-y: auto;
        }

        .memory-section {
          padding: 12px 14px;
          border-bottom: 1px solid #f3f4f6;
        }

        .memory-section:last-child {
          border-bottom: none;
        }

        .section-header {
          display: flex;
          flex-direction: column;
          gap: 2px;
          margin-bottom: 10px;
        }

        .section-title {
          font-size: 13px;
          font-weight: 600;
          color: #1f2937;
        }

        .section-subtitle {
          font-size: 11px;
          color: #9ca3af;
        }

        .memory-item {
          padding: 8px 10px;
          margin-bottom: 8px;
          border-radius: 6px;
          border-left: 3px solid;
        }

        .memory-item:last-child {
          margin-bottom: 0;
        }

        .memory-item.pending {
          background: #fef3c7;
          border-left-color: #f59e0b;
        }

        .memory-item.active {
          background: #d1fae5;
          border-left-color: #10b981;
        }

        .memory-item.outdated {
          background: #f3f4f6;
          border-left-color: #9ca3af;
        }

        .memory-date {
          display: flex;
          align-items: center;
          gap: 4px;
          font-size: 11px;
          color: #6b7280;
          margin-bottom: 4px;
        }

        .memory-text {
          font-size: 13px;
          color: #374151;
          line-height: 1.5;
        }

        /* 滚动条样式 */
        .memory-results-list::-webkit-scrollbar {
          width: 6px;
        }

        .memory-results-list::-webkit-scrollbar-track {
          background: #f3f4f6;
        }

        .memory-results-list::-webkit-scrollbar-thumb {
          background: #d1d5db;
          border-radius: 3px;
        }

        .memory-results-list::-webkit-scrollbar-thumb:hover {
          background: #9ca3af;
        }

        /* 无结果样式 */
        .no-results {
          padding: 20px;
          text-align: center;
        }

        .no-results-icon {
          font-size: 32px;
          margin-bottom: 8px;
        }

        .no-results-text {
          font-size: 14px;
          color: #6b7280;
          margin-bottom: 16px;
        }
      `}</style>
    </div>
  );
};
