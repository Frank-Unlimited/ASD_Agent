/**
 * Memory Service Client
 * 前端调用 graphiti 记忆层的工具函数
 *
 * 搜索返回两类 facts，由 pending 字段区分：
 *   pending=false  graphiti 已处理的精炼事实（concise extracted sentences）
 *   pending=true   FIFO 队列中尚未写入 graphiti 的原始观察文本（full episode content）
 */

const MEMORY_SERVICE_URL = 'http://localhost:8000';

export interface MemoryFact {
  text: string;
  valid_at: string | null;    // ISO 8601，事实生效时间
  invalid_at: string | null;  // ISO 8601，事实失效时间（null = 当前有效）
  pending: boolean;           // true = 在队列中，尚未被 graphiti 提取为结构化事实
}

/**
 * 从记忆层搜索 facts
 * 返回值 = pending buffer 原文 + graphiti 精炼事实（按后端顺序）
 * 不可用时静默返回空数组
 */
export async function fetchMemoryFacts(
  groupId: string,
  query: string,
  numResults = 10
): Promise<MemoryFact[]> {
  try {
    const res = await fetch(`${MEMORY_SERVICE_URL}/api/memory/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_id: groupId, query, num_results: numResults }),
      signal: AbortSignal.timeout(5000),
    });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.facts ?? []) as MemoryFact[];
  } catch {
    return [];
  }
}

/**
 * 将 MemoryFact[] 格式化为可注入 prompt 的文本块
 *
 * 分三段输出：
 *   1. 待处理观察（pending=true）  最新的、未被提炼的原始观察，最先呈现
 *   2. 当前有效事实（pending=false, invalid_at=null）  graphiti 精炼的现状
 *   3. 历史事实（pending=false, invalid_at≠null）  被覆盖的旧事实，体现变化幅度
 */
export function formatMemoryFactsForPrompt(facts: MemoryFact[]): string {
  if (facts.length === 0) return '';

  const pending   = facts.filter(f =>  f.pending);
  const confirmed = facts.filter(f => !f.pending);

  const confirmedSorted = [...confirmed].sort(
    (a, b) => (a.valid_at ?? '').localeCompare(b.valid_at ?? '')
  );
  const active   = confirmedSorted.filter(f => !f.invalid_at);
  const outdated = confirmedSorted.filter(f =>  f.invalid_at);

  const lines: string[] = [];

  // ── 段一：待处理观察（队列中，最新）──
  if (pending.length > 0) {
    lines.push(`**最新观察（已记录，graphiti 处理中，共 ${pending.length} 条）**`);
    lines.push('注意：这些是尚未被提炼的原始观察，包含完整上下文，是最新的事实来源。');
    for (const f of pending) {
      const date = f.valid_at ? f.valid_at.slice(0, 10) : '?';
      lines.push(`- [${date}] ${f.text}`);
    }
    lines.push('');
  }

  // ── 段二：当前有效事实（graphiti 提炼，现状）──
  if (active.length > 0) {
    lines.push('**当前有效事实（graphiti 提炼，按时间升序）**');
    for (const f of active) {
      const date = f.valid_at ? f.valid_at.slice(0, 10) : '?';
      lines.push(`- [${date}] ${f.text}`);
    }
  }

  // ── 段三：历史事实（已被覆盖，体现变化幅度）──
  if (outdated.length > 0) {
    if (active.length > 0) lines.push('');
    lines.push('**历史事实（已被新事实覆盖，仅供感知变化幅度）**');
    for (const f of outdated) {
      const from = f.valid_at   ? f.valid_at.slice(0, 10)   : '?';
      const to   = f.invalid_at ? f.invalid_at.slice(0, 10) : '?';
      lines.push(`- [${from}→${to}] ${f.text}`);
    }
  }

  return lines.join('\n');
}
