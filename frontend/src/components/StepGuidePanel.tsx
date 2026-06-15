import { motion, AnimatePresence } from 'framer-motion';
import { Check, ChevronLeft, ChevronRight, Clock, FileText, Lightbulb, Flag } from 'lucide-react';
import { GameStep } from '../types';

interface StepGuidePanelProps {
  steps: GameStep[];
  currentStep: number;
  onStepChange: (index: number) => void;
  gameTitle: string;
  elapsedTime: string;
  totalEvents: number;
}

// ─── 调色板 ──────────────────────────────────────────────────
const palette = {
  bg: '#f8fffe',
  primary: '#10b981',
  primaryDark: '#059669',
  primarySoft: '#d1fae5',
  primaryTint: '#ecfdf5',
  text: '#0f172a',
  textMuted: '#64748b',
  textFaint: '#94a3b8',
  border: '#e5e7eb',
  borderSoft: '#f1f5f9',
  cardShadow: '0 4px 16px rgba(16, 185, 129, 0.08), 0 1px 3px rgba(15, 23, 42, 0.04)',
};

// ─── 单步骤行 ────────────────────────────────────────────────
interface StepItemProps {
  step: GameStep;
  index: number;
  isCurrent: boolean;
  isCompleted: boolean;
  isLast: boolean;
  onClick: () => void;
}

const StepItem: React.FC<StepItemProps> = ({ step, index, isCurrent, isCompleted, isLast, onClick }) => {
  // 圆圈样式
  const circleStyle: React.CSSProperties = {
    width: 32,
    height: 32,
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0,
    fontSize: 13,
    fontWeight: 600,
    fontVariantNumeric: 'tabular-nums',
    transition: 'all 0.25s ease',
    zIndex: 1,
    position: 'relative',
    ...(isCompleted
      ? {
          background: palette.primary,
          color: '#fff',
          boxShadow: `0 0 0 3px ${palette.primarySoft}`,
        }
      : isCurrent
      ? {
          background: palette.primary,
          color: '#fff',
          boxShadow: `0 0 0 4px ${palette.primarySoft}, 0 4px 10px rgba(16, 185, 129, 0.35)`,
          transform: 'scale(1.08)',
        }
      : {
          background: '#fff',
          color: palette.textFaint,
          border: `1.5px solid ${palette.border}`,
        }),
  };

  // 连接线样式
  const connectorStyle: React.CSSProperties = {
    position: 'absolute',
    left: 15.25,
    top: 32,
    bottom: -16,
    width: 1.5,
    background: isCompleted ? palette.primary : palette.border,
    transition: 'background 0.3s ease',
  };

  // 标题样式
  const titleStyle: React.CSSProperties = {
    fontSize: 15,
    fontWeight: isCurrent ? 700 : isCompleted ? 500 : 500,
    color: isCurrent ? palette.text : isCompleted ? palette.textMuted : palette.textFaint,
    letterSpacing: isCurrent ? '-0.01em' : 0,
    lineHeight: 1.5,
    transition: 'all 0.2s ease',
    textDecoration: isCompleted ? 'line-through' : 'none',
    textDecorationColor: 'rgba(100, 116, 139, 0.4)',
    textDecorationThickness: '1px',
  };

  return (
    <div style={{ position: 'relative', paddingBottom: isLast ? 0 : 16 }}>
      {!isLast && <div style={connectorStyle} />}

      <div
        onClick={onClick}
        style={{
          display: 'flex',
          gap: 14,
          cursor: 'pointer',
          alignItems: 'flex-start',
        }}
      >
        <div style={circleStyle}>
          {isCompleted ? <Check size={16} strokeWidth={3} /> : index + 1}
        </div>

        <div style={{ flex: 1, minWidth: 0, paddingTop: 5 }}>
          <div style={titleStyle}>{step.stepTitle}</div>

          {/* 当前步骤详情卡片 */}
          <AnimatePresence initial={false}>
            {isCurrent && (
              <motion.div
                key="detail"
                initial={{ opacity: 0, height: 0, marginTop: 0 }}
                animate={{ opacity: 1, height: 'auto', marginTop: 12 }}
                exit={{ opacity: 0, height: 0, marginTop: 0 }}
                transition={{ duration: 0.28, ease: [0.4, 0, 0.2, 1] }}
                style={{ overflow: 'hidden' }}
              >
                {/* instruction 卡片 */}
                <div
                  style={{
                    background: '#fff',
                    borderRadius: 12,
                    padding: '12px 14px',
                    boxShadow: palette.cardShadow,
                    border: `1px solid ${palette.borderSoft}`,
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 6,
                      fontSize: 11,
                      fontWeight: 600,
                      color: palette.primaryDark,
                      textTransform: 'uppercase',
                      letterSpacing: '0.08em',
                      marginBottom: 6,
                    }}
                  >
                    <FileText size={12} strokeWidth={2.5} />
                    操作
                  </div>
                  <div
                    style={{
                      fontSize: 14,
                      color: palette.text,
                      lineHeight: 1.6,
                    }}
                  >
                    {step.instruction}
                  </div>
                </div>

                {/* guidance 卡片 */}
                {step.guidance && (
                  <div
                    style={{
                      marginTop: 8,
                      background: palette.primaryTint,
                      borderRadius: 12,
                      padding: '10px 14px 10px 12px',
                      borderLeft: `3px solid ${palette.primary}`,
                      display: 'flex',
                      gap: 10,
                      alignItems: 'flex-start',
                    }}
                  >
                    <Lightbulb
                      size={15}
                      strokeWidth={2.2}
                      style={{ color: palette.primaryDark, flexShrink: 0, marginTop: 2 }}
                    />
                    <div
                      style={{
                        fontSize: 13,
                        fontStyle: 'italic',
                        color: palette.primaryDark,
                        lineHeight: 1.6,
                      }}
                    >
                      {step.guidance}
                    </div>
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

// ─── 主组件 ──────────────────────────────────────────────────
const StepGuidePanel: React.FC<StepGuidePanelProps> = ({
  steps,
  currentStep,
  onStepChange,
  gameTitle,
  elapsedTime,
  totalEvents,
}) => {
  const isFirst = currentStep === 0;
  const isLast = currentStep === steps.length - 1;
  const safeStep = Math.max(0, Math.min(currentStep, steps.length - 1));

  // 进度百分比
  const progress = steps.length > 0 ? ((safeStep + 1) / steps.length) * 100 : 0;

  // 通用按钮样式
  const navButtonBase: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    gap: 4,
    padding: '8px 14px',
    fontSize: 13,
    fontWeight: 600,
    borderRadius: 10,
    border: 'none',
    cursor: 'pointer',
    transition: 'all 0.18s ease',
    fontFamily: 'inherit',
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        background: palette.bg,
        borderRadius: 0,
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      {/* ─── 顶部：标题 + 统计 ─── */}
      <div
        style={{
          padding: '18px 20px 14px',
          borderBottom: `1px solid ${palette.border}`,
          background: `linear-gradient(180deg, #ffffff 0%, ${palette.bg} 100%)`,
          flexShrink: 0,
        }}
      >
        <h2
          style={{
            margin: 0,
            fontSize: 18,
            fontWeight: 700,
            color: palette.text,
            letterSpacing: '-0.02em',
            lineHeight: 1.3,
          }}
        >
          {gameTitle}
        </h2>

        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            marginTop: 6,
            fontSize: 12,
            color: palette.textMuted,
          }}
        >
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <Clock size={12} strokeWidth={2} />
            <span style={{ fontVariantNumeric: 'tabular-nums', fontWeight: 500 }}>{elapsedTime}</span>
          </span>
          <span style={{ color: palette.borderSoft }}>·</span>
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
            <FileText size={12} strokeWidth={2} />
            <span style={{ fontVariantNumeric: 'tabular-nums', fontWeight: 500 }}>{totalEvents}</span>
            <span>事件</span>
          </span>
        </div>

        {/* 顶部进度条 */}
        <div
          style={{
            marginTop: 12,
            height: 3,
            background: palette.borderSoft,
            borderRadius: 999,
            overflow: 'hidden',
          }}
        >
          <motion.div
            initial={false}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
            style={{
              height: '100%',
              background: `linear-gradient(90deg, ${palette.primary} 0%, ${palette.primaryDark} 100%)`,
              borderRadius: 999,
            }}
          />
        </div>
      </div>

      {/* ─── 步骤列表（可滚动） ─── */}
      <div
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px 20px 12px',
          minHeight: 0,
        }}
      >
        {steps.length === 0 ? (
          <div
            style={{
              textAlign: 'center',
              padding: '40px 20px',
              color: palette.textFaint,
              fontSize: 13,
            }}
          >
            暂无步骤
          </div>
        ) : (
          steps.map((step, i) => (
            <StepItem
              key={i}
              step={step}
              index={i}
              isCurrent={i === safeStep}
              isCompleted={i < safeStep}
              isLast={i === steps.length - 1}
              onClick={() => onStepChange(i)}
            />
          ))
        )}
      </div>

      {/* ─── 底部导航 ─── */}
      <div
        style={{
          padding: '12px 16px',
          borderTop: `1px solid ${palette.border}`,
          background: '#fff',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          gap: 8,
          flexShrink: 0,
        }}
      >
        <button
          onClick={() => onStepChange(safeStep - 1)}
          disabled={isFirst}
          style={{
            ...navButtonBase,
            background: isFirst ? palette.borderSoft : '#fff',
            color: isFirst ? palette.textFaint : palette.textMuted,
            border: `1px solid ${isFirst ? palette.borderSoft : palette.border}`,
            opacity: isFirst ? 0.6 : 1,
            cursor: isFirst ? 'not-allowed' : 'pointer',
          }}
          onMouseEnter={(e) => {
            if (!isFirst) {
              e.currentTarget.style.background = palette.primaryTint;
              e.currentTarget.style.borderColor = palette.primarySoft;
              e.currentTarget.style.color = palette.primaryDark;
            }
          }}
          onMouseLeave={(e) => {
            if (!isFirst) {
              e.currentTarget.style.background = '#fff';
              e.currentTarget.style.borderColor = palette.border;
              e.currentTarget.style.color = palette.textMuted;
            }
          }}
        >
          <ChevronLeft size={15} strokeWidth={2.2} />
          上一步
        </button>

        {/* 进度文字 */}
        <div
          style={{
            fontSize: 12,
            fontWeight: 600,
            color: palette.textMuted,
            fontVariantNumeric: 'tabular-nums',
            letterSpacing: '0.02em',
          }}
        >
          Step <span style={{ color: palette.primaryDark, fontSize: 13 }}>{safeStep + 1}</span>
          <span style={{ color: palette.textFaint }}> / {steps.length}</span>
        </div>

        <button
          onClick={() => onStepChange(safeStep + 1)}
          style={{
            ...navButtonBase,
            background: isLast
              ? `linear-gradient(135deg, ${palette.primaryDark} 0%, ${palette.primary} 100%)`
              : `linear-gradient(135deg, ${palette.primary} 0%, ${palette.primaryDark} 100%)`,
            color: '#fff',
            boxShadow: '0 2px 6px rgba(16, 185, 129, 0.28)',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'translateY(-1px)';
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(16, 185, 129, 0.4)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = '0 2px 6px rgba(16, 185, 129, 0.28)';
          }}
        >
          {isLast ? (
            <>
              <Flag size={14} strokeWidth={2.4} />
              完成
            </>
          ) : (
            <>
              下一步
              <ChevronRight size={15} strokeWidth={2.2} />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default StepGuidePanel;
