/**
 * 游戏实时记录 API 通信服务
 * 与后端 API 通信，管理游戏会话的记录与快照
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

// ─── 类型定义 ───────────────────────────────────────────────

export interface ButtonConfig {
  id: string;
  label: string;
  icon: string;
  valence: number;       // -1 ~ 1，正向/负向
  sub_options?: string[]; // 长按展开的二级选项
}

export interface GameSessionConfig {
  session_id: string;
  child_id: string;
  game_type: string;
  game_name: string;
  start_time: string;
  planned_duration_minutes: number;
  fixed_buttons: ButtonConfig[];
  dynamic_buttons: ButtonConfig[];
}

export interface BehaviorEvent {
  session_id: string;
  game_type: string;
  event_type: string;
  detail?: string;
  valence: number;
  source: 'parent_click' | 'timed_snapshot' | 'ai_probe_response';
  game_phase?: string;
}

export interface SnapshotInfo {
  snapshot_id: string;
  scheduled_at: string;
  countdown_seconds: number;
  options: { label: string; value: string; color: string }[];
}

export interface StartSessionParams {
  child_id: string;
  game_type: string;
  game_name: string;
  planned_duration_minutes: number;
}

// ─── AI 推断 / 探测 类型 ─────────────────────────────────────────

export interface AIInference {
  id: string;
  timestamp: string;
  inference_text: string;
  inference_type: string;
  valence: number;        // -1 ~ 1
  confidence: number;     // 0 ~ 1
  is_confirmed: boolean | null;
}

export interface AIProbe {
  id: string;
  question_text: string;
  options: string[];
  game_phase?: string;
}

export interface SessionSummary {
  duration_minutes: number;
  total_events: number;
  event_type_counts: Record<string, number>;
  engagement_score: number;
  ai_summary: string;
}

// ─── API 函数 ───────────────────────────────────────────────

/**
 * 启动游戏会话
 * 返回会话配置（含固定按钮和动态按钮）
 */
export async function startGameSession(params: StartSessionParams): Promise<GameSessionConfig> {
  try {
    const res = await fetch(`${API_BASE}/api/game/session/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    if (!result?.data) throw new Error('startGameSession 响应缺少 data 字段');
    return result.data as GameSessionConfig;
  } catch (error) {
    console.warn('[gameRecordingService] startGameSession 失败，使用本地默认配置:', error);
    // 离线或后端未就绪时返回默认配置
    return getDefaultSessionConfig(params);
  }
}

/**
 * 记录行为事件
 */
export async function recordBehaviorEvent(event: BehaviorEvent): Promise<{ success: boolean }> {
  try {
    // 后端 BehaviorRecordRequest.valence 要求 int (-1/0/1)，前端 valence 可能为小数
    const valenceInt = event.valence > 0 ? 1 : event.valence < 0 ? -1 : 0;
    const payload = { ...event, valence: valenceInt };
    const res = await fetch(`${API_BASE}/api/observation/record`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    return { success: result?.success ?? true };
  } catch (error) {
    console.warn('[gameRecordingService] recordBehaviorEvent 失败，已本地缓存:', error);
    // 本地缓存事件以便稍后同步
    cacheEventLocally(event);
    return { success: true };
  }
}

/**
 * 提交快照响应
 */
export async function submitSnapshotResponse(params: {
  session_id: string;
  snapshot_id: string;
  response: string;
}): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/api/snapshot/response`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } catch (error) {
    console.warn('[gameRecordingService] submitSnapshotResponse 失败:', error);
  }
}

/**
 * 获取下一个快照信息
 */
export async function getNextSnapshotInfo(sessionId: string): Promise<SnapshotInfo | null> {
  try {
    const res = await fetch(`${API_BASE}/api/snapshot/next/${sessionId}`);
    if (!res.ok) return null;
    const result = await res.json();
    if (!result?.data) return null;
    return result.data as SnapshotInfo;
  } catch (error) {
    console.warn('[gameRecordingService] getNextSnapshotInfo 失败:', error);
    return null;
  }
}

/**
 * 完成游戏会话
 */
export async function completeGameSession(sessionId: string): Promise<{ summary: string; total_events: number }> {
  try {
    const res = await fetch(`${API_BASE}/api/game/session/${sessionId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    const data = result?.data ?? {};
    return {
      summary: data.ai_summary ?? '',
      total_events: data.total_events ?? 0,
    };
  } catch (error) {
    console.warn('[gameRecordingService] completeGameSession 失败:', error);
    return { summary: '', total_events: 0 };
  }
}

/**
 * 完成会话并获取摘要
 * 对应 POST /api/game/session/{id}/complete
 */
export async function completeSessionWithSummary(
  sessionId: string,
  notes?: string
): Promise<SessionSummary | null> {
  try {
    const res = await fetch(`${API_BASE}/api/game/session/${sessionId}/complete`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ notes: notes || '' }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    if (!result?.data) return null;
    const d = result.data;
    return {
      duration_minutes: d.duration_minutes ?? 0,
      total_events: d.total_events ?? 0,
      event_type_counts: d.event_type_counts ?? {},
      engagement_score: d.engagement_score ?? 0,
      ai_summary: d.ai_summary ?? '',
    };
  } catch (error) {
    console.warn('[gameRecordingService] completeSessionWithSummary 失败:', error);
    return null;
  }
}

// ─── AI 推断 API ─────────────────────────────────────────────

/**
 * 获取会话的 AI 推断列表
 * GET /api/ai-inference/{session_id}
 */
export async function getInferences(sessionId: string): Promise<AIInference[]> {
  try {
    const res = await fetch(`${API_BASE}/api/ai-inference/${sessionId}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    if (Array.isArray(result?.data)) return result.data as AIInference[];
    if (Array.isArray(result)) return result as AIInference[];
    return [];
  } catch (error) {
    console.warn('[gameRecordingService] getInferences 失败:', error);
    return [];
  }
}

/**
 * 确认 / 否定 AI 推断
 * PUT /api/ai-inference/{inference_id}/confirm
 */
export async function confirmInference(
  inferenceId: string,
  confirmed: boolean
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/api/ai-inference/${inferenceId}/confirm`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ is_confirmed: confirmed }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } catch (error) {
    console.warn('[gameRecordingService] confirmInference 失败:', error);
  }
}

// ─── AI 探测 API ─────────────────────────────────────────────

/**
 * 获取当前待回答的探测问题
 * GET /api/ai-probe/{session_id}
 */
export async function getCurrentProbe(sessionId: string): Promise<AIProbe | null> {
  try {
    const res = await fetch(`${API_BASE}/api/ai-probe/${sessionId}`);
    if (res.status === 204 || res.status === 404) return null;
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const result = await res.json();
    const probe = result?.data ?? null;
    if (!probe || !probe.id) return null;
    return probe as AIProbe;
  } catch (error) {
    console.warn('[gameRecordingService] getCurrentProbe 失败:', error);
    return null;
  }
}

/**
 * 回应 AI 探测问题
 * POST /api/ai-probe/{probe_id}/respond
 */
export async function respondToProbe(
  probeId: string,
  selectedOption: string
): Promise<void> {
  try {
    const res = await fetch(`${API_BASE}/api/ai-probe/${probeId}/respond`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selected_option: selectedOption }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
  } catch (error) {
    console.warn('[gameRecordingService] respondToProbe 失败:', error);
  }
}

// ─── 本地辅助函数 ─────────────────────────────────────────────

function getDefaultSessionConfig(params: StartSessionParams): GameSessionConfig {
  return {
    session_id: `local_${Date.now()}`,
    child_id: params.child_id,
    game_type: params.game_type,
    game_name: params.game_name,
    start_time: new Date().toISOString(),
    planned_duration_minutes: params.planned_duration_minutes,
    fixed_buttons: [
      { id: 'eye_contact', label: '眼神接触', icon: '👀', valence: 0.8, sub_options: ['短暂对视', '持续注视', '回避目光'] },
      { id: 'interaction', label: '主动互动', icon: '🤝', valence: 0.9, sub_options: ['语言互动', '肢体互动', '模仿行为'] },
      { id: 'positive', label: '积极情绪', icon: '😊', valence: 1.0, sub_options: ['微笑', '大笑', '兴奋'] },
      { id: 'withdrawal', label: '退缩回避', icon: '😟', valence: -0.7, sub_options: ['转身离开', '沉默不语', '拒绝参与'] },
    ],
    dynamic_buttons: [
      { id: 'focus', label: '专注投入', icon: '🎯', valence: 0.8 },
      { id: 'imitation', label: '模仿行为', icon: '🪞', valence: 0.7 },
      { id: 'verbal', label: '语言表达', icon: '💬', valence: 0.6 },
    ],
  };
}

const LOCAL_EVENT_CACHE_KEY = 'asd_game_events_cache';

function cacheEventLocally(event: BehaviorEvent): void {
  try {
    const existing = JSON.parse(localStorage.getItem(LOCAL_EVENT_CACHE_KEY) || '[]');
    existing.push({ ...event, cached_at: new Date().toISOString() });
    localStorage.setItem(LOCAL_EVENT_CACHE_KEY, JSON.stringify(existing));
  } catch {
    // 静默忽略
  }
}

/**
 * 获取本地缓存的事件（用于重连后同步）
 */
export function getCachedEvents(): BehaviorEvent[] {
  try {
    return JSON.parse(localStorage.getItem(LOCAL_EVENT_CACHE_KEY) || '[]');
  } catch {
    return [];
  }
}

/**
 * 清除本地缓存的事件
 */
export function clearCachedEvents(): void {
  localStorage.removeItem(LOCAL_EVENT_CACHE_KEY);
}
