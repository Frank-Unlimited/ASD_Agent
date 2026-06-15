import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Lightbulb, X, MessageCircleQuestion } from 'lucide-react';
import type { AIProbe } from '../services/gameRecordingService';

interface AIProbeCardProps {
    probe: AIProbe | null;
    onRespond: (probeId: string, option: string) => void;
    onDismiss: () => void;
}

const AUTO_MINIMIZE_MS = 20_000;

/**
 * AI 探测卡片
 * - 探测到达 → 从顶部滑入展开
 * - 20 秒无操作 → 收起为小条提示（不消失）
 * - 用户点击小条 → 重新展开
 * - 点击"跳过" → 通过 onDismiss 关闭
 */
const AIProbeCard: React.FC<AIProbeCardProps> = ({ probe, onRespond, onDismiss }) => {
    const [minimized, setMinimized] = useState(false);
    const timerRef = useRef<number | null>(null);

    const probeId = probe?.id ?? null;

    // 新探测到达：重置为展开 + 启动计时器
    useEffect(() => {
        if (timerRef.current) {
            window.clearTimeout(timerRef.current);
            timerRef.current = null;
        }
        if (!probeId) {
            setMinimized(false);
            return;
        }
        setMinimized(false);
        timerRef.current = window.setTimeout(() => {
            setMinimized(true);
        }, AUTO_MINIMIZE_MS);

        return () => {
            if (timerRef.current) {
                window.clearTimeout(timerRef.current);
                timerRef.current = null;
            }
        };
    }, [probeId]);

    // 任意交互都重置计时器
    const resetTimer = () => {
        if (timerRef.current) window.clearTimeout(timerRef.current);
        timerRef.current = window.setTimeout(() => {
            setMinimized(true);
        }, AUTO_MINIMIZE_MS);
    };

    const handleSelect = (option: string) => {
        if (!probe) return;
        onRespond(probe.id, option);
    };

    const handleSkip = () => {
        if (!probe) return;
        onRespond(probe.id, '__skip__');
        onDismiss();
    };

    const handleExpand = () => {
        setMinimized(false);
        resetTimer();
    };

    return (
        <AnimatePresence mode="wait">
            {probe && (
                <motion.div
                    key={`probe-${probe.id}-${minimized ? 'min' : 'open'}`}
                    initial={{ y: -40, opacity: 0, scale: 0.96 }}
                    animate={{ y: 0, opacity: 1, scale: 1 }}
                    exit={{ y: -24, opacity: 0, scale: 0.96 }}
                    transition={{ type: 'spring', damping: 24, stiffness: 240 }}
                    className="pointer-events-auto"
                >
                    {minimized ? (
                        <MinimizedBar
                            phase={probe.game_phase}
                            onClick={handleExpand}
                        />
                    ) : (
                        <ExpandedCard
                            probe={probe}
                            onSelect={handleSelect}
                            onSkip={handleSkip}
                            onInteract={resetTimer}
                        />
                    )}
                </motion.div>
            )}
        </AnimatePresence>
    );
};

// ─────────────────────────────────────────────────────────────────
// 展开态：完整问题卡片
// ─────────────────────────────────────────────────────────────────
interface ExpandedCardProps {
    probe: AIProbe;
    onSelect: (option: string) => void;
    onSkip: () => void;
    onInteract: () => void;
}

const ExpandedCard: React.FC<ExpandedCardProps> = ({
    probe,
    onSelect,
    onSkip,
    onInteract,
}) => {
    return (
        <div
            onPointerDown={onInteract}
            className="relative w-full overflow-hidden rounded-3xl border border-amber-100/80 bg-gradient-to-br from-amber-50/90 via-white to-white p-4 shadow-[0_12px_40px_rgba(245,158,11,0.18)] backdrop-blur"
        >
            {/* 顶部装饰条 — 编辑刊物风格 */}
            <div
                aria-hidden
                className="absolute inset-x-0 top-0 h-[3px]"
                style={{
                    background:
                        'linear-gradient(90deg, #f59e0b 0%, #fbbf24 40%, #fde68a 80%, transparent 100%)',
                }}
            />
            {/* 背景纹理：柔和的圆形光晕 */}
            <div
                aria-hidden
                className="pointer-events-none absolute -right-10 -bottom-12 h-40 w-40 rounded-full opacity-50"
                style={{
                    background:
                        'radial-gradient(circle, rgba(251,191,36,0.25), transparent 70%)',
                }}
            />

            {/* 标题行 */}
            <div className="relative flex items-start justify-between gap-2">
                <div className="flex items-center gap-2.5">
                    <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-gradient-to-br from-amber-400 to-amber-500 text-white shadow-md shadow-amber-200">
                        <Lightbulb className="h-4 w-4" strokeWidth={2.4} />
                    </span>
                    <div>
                        <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-amber-700">
                            AI 想了解更多
                        </p>
                        {probe.game_phase && (
                            <p className="mt-0.5 text-[10px] font-medium text-amber-600/70">
                                · {probe.game_phase} ·
                            </p>
                        )}
                    </div>
                </div>
                <button
                    type="button"
                    onClick={onSkip}
                    aria-label="跳过"
                    className="flex h-9 w-9 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 hover:text-gray-600"
                >
                    <X className="h-4 w-4" strokeWidth={2.2} />
                </button>
            </div>

            {/* 问题正文 */}
            <p className="relative mt-3 text-[15px] font-semibold leading-snug text-gray-800">
                {probe.question_text}
            </p>

            {/* 选项区 — 自适应网格 */}
            <div className="relative mt-4 grid grid-cols-2 gap-2">
                {probe.options.map((opt, i) => (
                    <motion.button
                        key={`${opt}-${i}`}
                        type="button"
                        onClick={() => onSelect(opt)}
                        whileTap={{ scale: 0.96 }}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.05 + i * 0.04 }}
                        className="group relative flex min-h-[44px] items-center justify-center rounded-2xl border border-amber-200/70 bg-white px-3 py-2.5 text-[13px] font-medium text-gray-800 shadow-sm transition hover:border-amber-400 hover:bg-amber-50 hover:shadow-md"
                    >
                        <span className="line-clamp-2">{opt}</span>
                    </motion.button>
                ))}

                {/* 跳过按钮 — 占满最后一格 / 单独一行 */}
                <button
                    type="button"
                    onClick={onSkip}
                    className={`col-span-2 flex min-h-[44px] items-center justify-center gap-1 rounded-2xl border border-dashed border-gray-300 bg-white/60 px-3 py-2 text-[12px] font-medium text-gray-500 transition hover:border-gray-400 hover:bg-white hover:text-gray-700`}
                >
                    跳过这次提问
                </button>
            </div>

            {/* 底部计时提示 */}
            <p className="relative mt-2.5 text-center text-[10px] font-medium tracking-wide text-amber-600/60">
                20 秒后自动收起 · 不会打断你
            </p>
        </div>
    );
};

// ─────────────────────────────────────────────────────────────────
// 收起态：小条提示
// ─────────────────────────────────────────────────────────────────
interface MinimizedBarProps {
    phase?: string;
    onClick: () => void;
}

const MinimizedBar: React.FC<MinimizedBarProps> = ({ phase, onClick }) => (
    <button
        type="button"
        onClick={onClick}
        className="group relative flex w-full items-center gap-3 overflow-hidden rounded-full border border-amber-200 bg-white/95 py-2.5 pl-2.5 pr-4 shadow-md backdrop-blur transition active:scale-[0.98]"
        style={{ minHeight: 44 }}
    >
        {/* 微动画 dot */}
        <span className="relative flex h-7 w-7 items-center justify-center">
            <span className="absolute inset-0 animate-ping rounded-full bg-amber-400/40" />
            <span className="relative flex h-7 w-7 items-center justify-center rounded-full bg-gradient-to-br from-amber-400 to-amber-500 text-white">
                <MessageCircleQuestion className="h-3.5 w-3.5" strokeWidth={2.4} />
            </span>
        </span>
        <span className="flex-1 truncate text-left">
            <span className="block text-[10px] font-bold uppercase tracking-[0.18em] text-amber-600">
                有一个问题
            </span>
            <span className="block truncate text-[12px] font-semibold text-gray-700">
                {phase ? `${phase} · 待回答` : '点击查看 AI 的提问'}
            </span>
        </span>
        <span className="text-[10px] font-bold uppercase tracking-widest text-amber-500 group-hover:text-amber-600">
            展开 →
        </span>
    </button>
);

export default AIProbeCard;
