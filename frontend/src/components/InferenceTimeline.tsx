import React, { useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Bot, Check, X, ChevronDown, Sparkles } from 'lucide-react';
import type { AIInference } from '../services/gameRecordingService';

interface InferenceTimelineProps {
    sessionId: string;
    inferences: AIInference[];
    onConfirm: (id: string, confirmed: boolean) => void;
    isExpanded: boolean;
    onToggle: () => void;
}

// ── 视觉常量：把"AI 笔记本"做成一份临床日志风格 ─────────────────────
const VALENCE_THEME = {
    positive: {
        border: '#22c55e',
        glow: 'rgba(34,197,94,0.18)',
        soft: '#ecfdf5',
        label: '积极',
    },
    neutral: {
        border: '#eab308',
        glow: 'rgba(234,179,8,0.18)',
        soft: '#fefce8',
        label: '中性',
    },
    negative: {
        border: '#ef4444',
        glow: 'rgba(239,68,68,0.18)',
        soft: '#fef2f2',
        label: '注意',
    },
};

function getValenceTheme(v: number) {
    if (v > 0) return VALENCE_THEME.positive;
    if (v < 0) return VALENCE_THEME.negative;
    return VALENCE_THEME.neutral;
}

function formatHM(timestamp: string): string {
    try {
        const d = new Date(timestamp);
        if (isNaN(d.getTime())) return timestamp.slice(11, 16) || '--:--';
        return d.toLocaleTimeString('zh-CN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: false,
        });
    } catch {
        return '--:--';
    }
}

const InferenceTimeline: React.FC<InferenceTimelineProps> = ({
    inferences,
    onConfirm,
    isExpanded,
    onToggle,
}) => {
    // 按时间倒序，最新在最上面
    const sorted = useMemo(
        () =>
            [...inferences].sort(
                (a, b) =>
                    new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime(),
            ),
        [inferences],
    );

    const pendingCount = useMemo(
        () => sorted.filter((i) => i.is_confirmed === null).length,
        [sorted],
    );

    return (
        <motion.div
            layout
            transition={{ type: 'spring', damping: 26, stiffness: 220 }}
            className="relative w-full"
        >
            {/* ── 头部条：折叠态指示器 / 展开态标题 ────────────────── */}
            <button
                type="button"
                onClick={onToggle}
                aria-expanded={isExpanded}
                className="group relative w-full overflow-hidden rounded-2xl border border-emerald-100 bg-white px-4 py-3 text-left shadow-[0_2px_12px_rgba(16,185,129,0.06)] transition active:scale-[0.99]"
                style={{ minHeight: 56 }}
            >
                {/* 微纹理装饰：右侧的环形光晕 */}
                <div
                    aria-hidden
                    className="pointer-events-none absolute -right-10 -top-10 h-32 w-32 rounded-full opacity-60"
                    style={{
                        background:
                            'radial-gradient(circle, rgba(16,185,129,0.18), transparent 70%)',
                    }}
                />

                <div className="relative flex items-center justify-between gap-3">
                    <div className="flex min-w-0 items-center gap-3">
                        <span className="relative flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-emerald-50 to-emerald-100 ring-1 ring-emerald-200/60">
                            <Bot className="h-5 w-5 text-emerald-600" strokeWidth={2.2} />
                            {pendingCount > 0 && (
                                <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-amber-500 px-1 text-[10px] font-bold text-white shadow-sm">
                                    {pendingCount}
                                </span>
                            )}
                        </span>

                        <div className="min-w-0">
                            <div className="flex items-center gap-2">
                                <span className="text-[10px] font-bold uppercase tracking-[0.18em] text-emerald-700/70">
                                    AI Field Notes
                                </span>
                                <span className="text-[10px] text-gray-300">·</span>
                                <span className="text-[10px] font-medium text-gray-400">
                                    实时观察
                                </span>
                            </div>
                            <div className="mt-0.5 truncate text-sm font-semibold text-gray-800">
                                {sorted.length > 0
                                    ? `已记录 ${sorted.length} 条推断`
                                    : '正在留意孩子的细微反应…'}
                                {pendingCount > 0 && (
                                    <span className="ml-2 text-xs font-medium text-amber-600">
                                        · {pendingCount} 条待确认
                                    </span>
                                )}
                            </div>
                        </div>
                    </div>

                    <motion.span
                        animate={{ rotate: isExpanded ? 180 : 0 }}
                        transition={{ type: 'spring', damping: 18, stiffness: 260 }}
                        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-50 text-gray-500 group-hover:bg-emerald-50 group-hover:text-emerald-600"
                    >
                        <ChevronDown className="h-4 w-4" />
                    </motion.span>
                </div>
            </button>

            {/* ── 展开态：时间线 ─────────────────────────────────── */}
            <AnimatePresence initial={false}>
                {isExpanded && (
                    <motion.div
                        key="timeline"
                        layout
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ type: 'spring', damping: 28, stiffness: 220 }}
                        className="overflow-hidden"
                    >
                        <div className="mt-3 rounded-2xl border border-gray-100 bg-gradient-to-b from-white to-gray-50/40 p-4 shadow-inner">
                            {sorted.length === 0 ? (
                                <EmptyState />
                            ) : (
                                <ol className="relative space-y-2">
                                    {/* 垂直时间线主轴 */}
                                    <span
                                        aria-hidden
                                        className="absolute left-[58px] top-2 bottom-2 w-px bg-gradient-to-b from-emerald-200/60 via-gray-200 to-transparent"
                                    />
                                    {sorted.map((inf, idx) => (
                                        <InferenceRow
                                            key={inf.id}
                                            inference={inf}
                                            index={idx}
                                            onConfirm={onConfirm}
                                        />
                                    ))}
                                </ol>
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

// ─────────────────────────────────────────────────────────────────
// 单条推断行
// ─────────────────────────────────────────────────────────────────
interface InferenceRowProps {
    inference: AIInference;
    index: number;
    onConfirm: (id: string, confirmed: boolean) => void;
}

const InferenceRow: React.FC<InferenceRowProps> = ({
    inference,
    index,
    onConfirm,
}) => {
    const theme = getValenceTheme(inference.valence);
    const lowConfidence = inference.confidence < 0.7;
    const isConfirmed = inference.is_confirmed === true;
    const isRejected = inference.is_confirmed === false;
    const isPending = inference.is_confirmed === null;

    return (
        <motion.li
            layout
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ delay: Math.min(index * 0.025, 0.2) }}
            className="relative flex items-stretch gap-3"
        >
            {/* 时间戳列 — 等宽数字 */}
            <div className="flex w-12 shrink-0 flex-col items-end pt-2.5">
                <span
                    className="font-mono text-[11px] font-semibold tabular-nums text-gray-500"
                    style={{ letterSpacing: '0.02em' }}
                >
                    {formatHM(inference.timestamp)}
                </span>
            </div>

            {/* 时间线节点 */}
            <div className="relative flex w-4 shrink-0 justify-center pt-3.5">
                <span
                    className="block h-2.5 w-2.5 rounded-full ring-4 ring-white"
                    style={{
                        backgroundColor: theme.border,
                        boxShadow: `0 0 0 4px ${theme.glow}`,
                    }}
                />
            </div>

            {/* 卡片内容 */}
            <div
                className="relative min-h-[44px] flex-1 rounded-xl bg-white p-3 transition"
                style={{
                    borderLeft: `3px ${lowConfidence ? 'dashed' : 'solid'} ${theme.border}`,
                    boxShadow: isPending
                        ? `0 1px 0 rgba(0,0,0,0.02), 0 4px 16px ${theme.glow}`
                        : '0 1px 0 rgba(0,0,0,0.02)',
                    opacity: lowConfidence ? 0.78 : 1,
                }}
            >
                <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                        {/* 类型标签 + 置信度 */}
                        <div className="mb-1 flex flex-wrap items-center gap-1.5">
                            <span
                                className="inline-flex items-center rounded-full px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-widest"
                                style={{
                                    backgroundColor: theme.soft,
                                    color: theme.border,
                                }}
                            >
                                {inference.inference_type || theme.label}
                            </span>
                            <ConfidenceBar confidence={inference.confidence} color={theme.border} />
                            {lowConfidence && (
                                <span className="text-[9px] font-medium uppercase tracking-wider text-gray-400">
                                    低置信
                                </span>
                            )}
                            {isConfirmed && (
                                <span className="inline-flex items-center gap-0.5 rounded-full bg-emerald-50 px-1.5 py-0.5 text-[9px] font-bold text-emerald-600">
                                    <Check className="h-2.5 w-2.5" strokeWidth={3} /> 已确认
                                </span>
                            )}
                            {isRejected && (
                                <span className="inline-flex items-center gap-0.5 rounded-full bg-red-50 px-1.5 py-0.5 text-[9px] font-bold text-red-500">
                                    <X className="h-2.5 w-2.5" strokeWidth={3} /> 已否定
                                </span>
                            )}
                        </div>

                        <p
                            className={`text-[13px] leading-snug text-gray-800 ${isRejected ? 'text-gray-400 line-through' : ''
                                }`}
                            style={{ opacity: lowConfidence && !isRejected ? 0.85 : 1 }}
                        >
                            {inference.inference_text}
                        </p>
                    </div>

                    {/* 操作按钮区 — 始终保持 ≥44px 命中区 */}
                    <div className="flex shrink-0 flex-col gap-1.5">
                        <button
                            type="button"
                            onClick={() => onConfirm(inference.id, true)}
                            aria-label="确认这条推断"
                            className={`flex h-11 w-11 items-center justify-center rounded-xl border transition active:scale-90 ${isConfirmed
                                    ? 'border-emerald-500 bg-emerald-500 text-white shadow-md shadow-emerald-200'
                                    : 'border-emerald-200 bg-white text-emerald-600 hover:bg-emerald-50'
                                }`}
                        >
                            <Check className="h-4 w-4" strokeWidth={2.6} />
                        </button>
                        <button
                            type="button"
                            onClick={() => onConfirm(inference.id, false)}
                            aria-label="否定这条推断"
                            className={`flex h-11 w-11 items-center justify-center rounded-xl border transition active:scale-90 ${isRejected
                                    ? 'border-red-500 bg-red-500 text-white shadow-md shadow-red-200'
                                    : 'border-gray-200 bg-white text-gray-400 hover:border-red-200 hover:bg-red-50 hover:text-red-500'
                                }`}
                        >
                            <X className="h-4 w-4" strokeWidth={2.6} />
                        </button>
                    </div>
                </div>
            </div>
        </motion.li>
    );
};

// ─────────────────────────────────────────────────────────────────
// 置信度小条
// ─────────────────────────────────────────────────────────────────
const ConfidenceBar: React.FC<{ confidence: number; color: string }> = ({
    confidence,
    color,
}) => {
    const pct = Math.max(0, Math.min(1, confidence));
    return (
        <span
            className="inline-flex items-center gap-1"
            title={`置信度 ${Math.round(pct * 100)}%`}
        >
            <span className="relative block h-1 w-8 overflow-hidden rounded-full bg-gray-200">
                <span
                    className="absolute inset-y-0 left-0 rounded-full"
                    style={{ width: `${pct * 100}%`, backgroundColor: color }}
                />
            </span>
            <span className="font-mono text-[9px] tabular-nums text-gray-400">
                {Math.round(pct * 100)}
            </span>
        </span>
    );
};

// ─────────────────────────────────────────────────────────────────
// 空状态
// ─────────────────────────────────────────────────────────────────
const EmptyState: React.FC = () => (
    <div className="flex flex-col items-center justify-center gap-2 py-8 text-center">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-emerald-50">
            <Sparkles className="h-5 w-5 text-emerald-500" />
        </span>
        <p className="text-xs font-bold uppercase tracking-[0.18em] text-gray-400">
            尚无推断
        </p>
        <p className="max-w-[240px] text-xs leading-relaxed text-gray-400">
            随着互动展开，AI 会在这里写下它对孩子状态的观察。
        </p>
    </div>
);

export default InferenceTimeline;
