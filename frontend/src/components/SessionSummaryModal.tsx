import React, { useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
    ClipboardList,
    Check,
    X,
    Eye,
    Handshake,
    Smile,
    Frown,
    Sparkles,
    Save,
    ArrowLeft,
    Clock,
    Activity,
} from 'lucide-react';
import type {
    AIInference,
    SessionSummary,
} from '../services/gameRecordingService';

interface SessionSummaryModalProps {
    isOpen: boolean;
    sessionId: string;
    summary: SessionSummary | null;
    unconfirmedInferences: AIInference[];
    onConfirmInference: (id: string, confirmed: boolean) => void;
    onSave: (notes: string) => void;
    onContinue: () => void;
}

// ── 事件类型 → 图标 + 色彩映射 ─────────────────────────────────
const EVENT_TYPE_META: Record<
    string,
    { label: string; icon: React.ComponentType<any>; tone: 'positive' | 'caution' }
> = {
    eye_contact: { label: '眼神接触', icon: Eye, tone: 'positive' },
    interaction: { label: '主动互动', icon: Handshake, tone: 'positive' },
    positive: { label: '积极情绪', icon: Smile, tone: 'positive' },
    withdrawal: { label: '退缩回避', icon: Frown, tone: 'caution' },
    focus: { label: '专注投入', icon: Activity, tone: 'positive' },
    imitation: { label: '模仿行为', icon: Sparkles, tone: 'positive' },
    verbal: { label: '语言表达', icon: Sparkles, tone: 'positive' },
};

function getEventMeta(key: string) {
    return (
        EVENT_TYPE_META[key] ?? {
            label: key,
            icon: Activity,
            tone: 'positive' as const,
        }
    );
}

function formatHM(timestamp: string): string {
    try {
        const d = new Date(timestamp);
        if (isNaN(d.getTime())) return '--:--';
        return d.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        });
    } catch {
        return '--:--';
    }
}

const SessionSummaryModal: React.FC<SessionSummaryModalProps> = ({
    isOpen,
    summary,
    unconfirmedInferences,
    onConfirmInference,
    onSave,
    onContinue,
}) => {
    const [notes, setNotes] = useState('');
    const [saving, setSaving] = useState(false);

    const engagementPct = useMemo(() => {
        const v = summary?.engagement_score ?? 0;
        // 兼容 0~1 与 0~100 两种返回
        const normalized = v > 1 ? v / 100 : v;
        return Math.max(0, Math.min(1, normalized));
    }, [summary]);

    const eventEntries = useMemo(
        () => Object.entries(summary?.event_type_counts ?? {}),
        [summary],
    );

    const handleSave = async () => {
        setSaving(true);
        try {
            await Promise.resolve(onSave(notes));
        } finally {
            setSaving(false);
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    key="summary-backdrop"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="fixed inset-0 z-[120] flex items-stretch justify-center bg-gradient-to-b from-slate-900/60 via-slate-900/50 to-slate-900/70 backdrop-blur-sm sm:items-center sm:p-6"
                    role="dialog"
                    aria-modal="true"
                >
                    <motion.div
                        key="summary-card"
                        initial={{ y: 40, opacity: 0, scale: 0.98 }}
                        animate={{ y: 0, opacity: 1, scale: 1 }}
                        exit={{ y: 24, opacity: 0, scale: 0.98 }}
                        transition={{ type: 'spring', damping: 28, stiffness: 240 }}
                        className="relative flex w-full max-w-2xl flex-col overflow-hidden bg-[#FAFAF7] sm:rounded-3xl sm:shadow-2xl"
                        style={{ maxHeight: '100dvh' }}
                    >
                        {/* ── Header ───────────────────────────────────── */}
                        <header className="relative shrink-0 overflow-hidden border-b border-emerald-100/60 bg-white px-5 pt-6 pb-5">
                            {/* 顶部色带 */}
                            <div
                                aria-hidden
                                className="absolute inset-x-0 top-0 h-1"
                                style={{
                                    background:
                                        'linear-gradient(90deg, #10b981 0%, #34d399 50%, #fbbf24 100%)',
                                }}
                            />
                            {/* 装饰光晕 */}
                            <div
                                aria-hidden
                                className="pointer-events-none absolute -right-16 -top-16 h-48 w-48 rounded-full opacity-50"
                                style={{
                                    background:
                                        'radial-gradient(circle, rgba(16,185,129,0.22), transparent 70%)',
                                }}
                            />

                            <div className="relative flex items-start gap-3">
                                <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 text-white shadow-md shadow-emerald-200">
                                    <ClipboardList className="h-5 w-5" strokeWidth={2.2} />
                                </span>
                                <div className="min-w-0 flex-1">
                                    <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-emerald-700/80">
                                        Session Debrief · 本次游戏总结
                                    </p>
                                    <h2 className="mt-1 text-[20px] font-bold leading-tight text-gray-900">
                                        互动告一段落，让我们一起回顾
                                    </h2>
                                    <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[12px] text-gray-500">
                                        <span className="inline-flex items-center gap-1 font-mono tabular-nums">
                                            <Clock className="h-3 w-3" />
                                            {summary?.duration_minutes ?? 0} 分钟
                                        </span>
                                        <span className="text-gray-300">·</span>
                                        <span className="font-mono tabular-nums">
                                            共 {summary?.total_events ?? 0} 条记录
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </header>

                        {/* ── Body ─────────────────────────────────────── */}
                        <div className="flex-1 overflow-y-auto px-5 py-5">
                            {/* 1. 事件统计 */}
                            <Section title="事件统计" eyebrow="Behaviors observed">
                                {eventEntries.length === 0 ? (
                                    <p className="rounded-xl bg-white px-3 py-4 text-center text-[12px] text-gray-400">
                                        暂无统计数据
                                    </p>
                                ) : (
                                    <ul className="grid grid-cols-2 gap-2">
                                        {eventEntries.map(([key, count]) => (
                                            <EventStatPill
                                                key={key}
                                                eventKey={key}
                                                count={count}
                                            />
                                        ))}
                                    </ul>
                                )}
                            </Section>

                            {/* 2. 整体参与度 */}
                            <Section title="整体参与度" eyebrow="Engagement score">
                                <EngagementBar pct={engagementPct} />
                            </Section>

                            {/* 3. AI 摘要 */}
                            {summary?.ai_summary && (
                                <Section title="AI 观察摘要" eyebrow="AI narrative">
                                    <div className="relative rounded-2xl border border-emerald-100 bg-white px-4 py-3.5 shadow-sm">
                                        <span
                                            aria-hidden
                                            className="absolute left-0 top-3 h-[calc(100%-24px)] w-1 rounded-r-full bg-gradient-to-b from-emerald-400 to-emerald-200"
                                        />
                                        <p className="pl-2 text-[13px] leading-relaxed text-gray-700">
                                            {summary.ai_summary}
                                        </p>
                                    </div>
                                </Section>
                            )}

                            {/* 4. AI 推断待确认 */}
                            <Section
                                title="AI 推断待确认"
                                eyebrow="Awaiting your judgment"
                                badge={
                                    unconfirmedInferences.length > 0
                                        ? `${unconfirmedInferences.length} 条`
                                        : undefined
                                }
                            >
                                {unconfirmedInferences.length === 0 ? (
                                    <div className="flex items-center gap-2 rounded-xl bg-emerald-50/60 px-3 py-3 text-[12px] text-emerald-700">
                                        <Check className="h-4 w-4" strokeWidth={2.6} />
                                        所有推断都已处理 · 无需进一步确认
                                    </div>
                                ) : (
                                    <ul className="space-y-2">
                                        {unconfirmedInferences.map((inf) => (
                                            <UnconfirmedRow
                                                key={inf.id}
                                                inference={inf}
                                                onConfirm={onConfirmInference}
                                            />
                                        ))}
                                    </ul>
                                )}
                            </Section>

                            {/* 5. 备注 */}
                            <Section title="补充备注" eyebrow="Your note">
                                <div className="rounded-2xl border border-gray-200 bg-white p-2 transition focus-within:border-emerald-400 focus-within:shadow-md focus-within:shadow-emerald-100">
                                    <textarea
                                        value={notes}
                                        onChange={(e) => setNotes(e.target.value)}
                                        rows={3}
                                        placeholder="今天有什么特别想记下的瞬间？孩子的反应、你的感受、想到的下一步…"
                                        className="block w-full resize-none rounded-xl bg-transparent px-2 py-2 text-[13px] leading-relaxed text-gray-800 placeholder:text-gray-400 focus:outline-none"
                                    />
                                </div>
                            </Section>
                        </div>

                        {/* ── Footer 操作区 ─────────────────────────────── */}
                        <footer className="shrink-0 border-t border-gray-100 bg-white px-5 py-3 pb-[calc(env(safe-area-inset-bottom,0)+12px)]">
                            <div className="flex gap-2">
                                <button
                                    type="button"
                                    onClick={onContinue}
                                    className="flex min-h-[48px] flex-1 items-center justify-center gap-1.5 rounded-2xl border border-gray-200 bg-white px-3 text-[13px] font-semibold text-gray-700 transition active:scale-[0.98] hover:bg-gray-50"
                                >
                                    <ArrowLeft className="h-4 w-4" strokeWidth={2.2} />
                                    继续记录
                                </button>
                                <button
                                    type="button"
                                    onClick={handleSave}
                                    disabled={saving}
                                    className="flex min-h-[48px] flex-[1.4] items-center justify-center gap-1.5 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 px-3 text-[14px] font-bold text-white shadow-lg shadow-emerald-200 transition active:scale-[0.98] disabled:opacity-60"
                                >
                                    <Save className="h-4 w-4" strokeWidth={2.4} />
                                    {saving ? '保存中…' : '确认并保存'}
                                </button>
                            </div>
                        </footer>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

// ─────────────────────────────────────────────────────────────────
// 通用区块容器
// ─────────────────────────────────────────────────────────────────
const Section: React.FC<{
    title: string;
    eyebrow?: string;
    badge?: string;
    children: React.ReactNode;
}> = ({ title, eyebrow, badge, children }) => (
    <section className="mb-5 last:mb-2">
        <header className="mb-2 flex items-baseline justify-between">
            <div className="flex items-baseline gap-2">
                {eyebrow && (
                    <span className="text-[9px] font-bold uppercase tracking-[0.2em] text-emerald-700/60">
                        {eyebrow}
                    </span>
                )}
                <h3 className="text-[14px] font-bold tracking-tight text-gray-900">
                    {title}
                </h3>
            </div>
            {badge && (
                <span className="rounded-full bg-amber-50 px-2 py-0.5 text-[10px] font-bold text-amber-600">
                    {badge}
                </span>
            )}
        </header>
        {children}
    </section>
);

// ─────────────────────────────────────────────────────────────────
// 单个事件统计卡
// ─────────────────────────────────────────────────────────────────
const EventStatPill: React.FC<{ eventKey: string; count: number }> = ({
    eventKey,
    count,
}) => {
    const meta = getEventMeta(eventKey);
    const Icon = meta.icon;
    const isCaution = meta.tone === 'caution';
    return (
        <li
            className="flex items-center gap-2 rounded-xl border bg-white px-3 py-2.5 shadow-sm"
            style={{
                borderColor: isCaution ? '#fed7aa' : '#bbf7d0',
            }}
        >
            <span
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl"
                style={{
                    backgroundColor: isCaution ? '#fff7ed' : '#ecfdf5',
                    color: isCaution ? '#ea580c' : '#059669',
                }}
            >
                <Icon className="h-4 w-4" strokeWidth={2.2} />
            </span>
            <div className="min-w-0 flex-1">
                <p className="truncate text-[12px] font-semibold text-gray-800">
                    {meta.label}
                </p>
                <p className="text-[10px] font-medium text-gray-400">
                    {isCaution ? '需关注' : '积极信号'}
                </p>
            </div>
            <span className="font-mono text-[16px] font-bold tabular-nums text-gray-900">
                {count}
            </span>
        </li>
    );
};

// ─────────────────────────────────────────────────────────────────
// 参与度进度条
// ─────────────────────────────────────────────────────────────────
const EngagementBar: React.FC<{ pct: number }> = ({ pct }) => {
    const percentage = Math.round(pct * 100);
    const tone =
        percentage >= 70
            ? { from: '#10b981', to: '#34d399', label: '高参与度' }
            : percentage >= 40
                ? { from: '#f59e0b', to: '#fbbf24', label: '中等参与度' }
                : { from: '#ef4444', to: '#f87171', label: '需要更多引导' };

    return (
        <div className="rounded-2xl border border-gray-100 bg-white p-3.5 shadow-sm">
            <div className="mb-2 flex items-baseline justify-between">
                <span className="text-[11px] font-medium uppercase tracking-wider text-gray-500">
                    {tone.label}
                </span>
                <span className="font-mono text-[20px] font-bold tabular-nums text-gray-900">
                    {percentage}
                    <span className="ml-0.5 text-[11px] font-medium text-gray-400">/ 100</span>
                </span>
            </div>
            <div className="relative h-2.5 w-full overflow-hidden rounded-full bg-gray-100">
                <motion.span
                    initial={{ width: 0 }}
                    animate={{ width: `${percentage}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    className="block h-full rounded-full"
                    style={{
                        background: `linear-gradient(90deg, ${tone.from}, ${tone.to})`,
                    }}
                />
                {/* 刻度 */}
                <div className="pointer-events-none absolute inset-0 flex justify-between px-[10%]">
                    {[0, 1, 2, 3].map((i) => (
                        <span key={i} className="h-full w-px bg-white/60" />
                    ))}
                </div>
            </div>
        </div>
    );
};

// ─────────────────────────────────────────────────────────────────
// 待确认推断行
// ─────────────────────────────────────────────────────────────────
const UnconfirmedRow: React.FC<{
    inference: AIInference;
    onConfirm: (id: string, confirmed: boolean) => void;
}> = ({ inference, onConfirm }) => {
    const isConfirmed = inference.is_confirmed === true;
    const isRejected = inference.is_confirmed === false;
    const valenceColor =
        inference.valence > 0
            ? '#22c55e'
            : inference.valence < 0
                ? '#ef4444'
                : '#eab308';

    return (
        <li
            className="flex items-stretch gap-2 rounded-xl border bg-white p-2.5"
            style={{
                borderColor: '#f3f4f6',
                borderLeft: `3px solid ${valenceColor}`,
            }}
        >
            <div className="flex w-12 shrink-0 flex-col items-start pt-0.5">
                <span className="font-mono text-[10px] font-semibold tabular-nums text-gray-500">
                    {formatHM(inference.timestamp)}
                </span>
                <span className="mt-0.5 text-[9px] uppercase tracking-wider text-gray-400">
                    {Math.round(inference.confidence * 100)}%
                </span>
            </div>
            <p
                className={`flex-1 self-center text-[12.5px] leading-snug text-gray-700 ${isRejected ? 'text-gray-400 line-through' : ''
                    }`}
            >
                {inference.inference_text}
            </p>
            <div className="flex shrink-0 items-center gap-1.5">
                <button
                    type="button"
                    onClick={() => onConfirm(inference.id, true)}
                    aria-label="确认"
                    className={`flex h-11 w-11 items-center justify-center rounded-xl border transition active:scale-90 ${isConfirmed
                            ? 'border-emerald-500 bg-emerald-500 text-white'
                            : 'border-emerald-200 bg-white text-emerald-600 hover:bg-emerald-50'
                        }`}
                >
                    <Check className="h-4 w-4" strokeWidth={2.6} />
                </button>
                <button
                    type="button"
                    onClick={() => onConfirm(inference.id, false)}
                    aria-label="否定"
                    className={`flex h-11 w-11 items-center justify-center rounded-xl border transition active:scale-90 ${isRejected
                            ? 'border-red-500 bg-red-500 text-white'
                            : 'border-gray-200 bg-white text-gray-400 hover:border-red-200 hover:bg-red-50 hover:text-red-500'
                        }`}
                >
                    <X className="h-4 w-4" strokeWidth={2.6} />
                </button>
            </div>
        </li>
    );
};

export default SessionSummaryModal;
