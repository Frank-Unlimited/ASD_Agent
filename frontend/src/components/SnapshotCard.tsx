import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Clock } from 'lucide-react';

interface SnapshotCardProps {
  visible: boolean;
  snapshotId: string;
  countdownSeconds?: number;
  onRespond: (snapshotId: string, response: string) => void;
  onSkip: (snapshotId: string) => void;
  onTimeout: (snapshotId: string) => void;
}

const ENGAGEMENT_OPTIONS = [
  { label: '投入', value: 'engaged', emoji: '🟢', color: 'bg-emerald-50 border-emerald-200 text-emerald-700', activeColor: 'bg-emerald-500 text-white border-emerald-500' },
  { label: '一般', value: 'neutral', emoji: '🟡', color: 'bg-amber-50 border-amber-200 text-amber-700', activeColor: 'bg-amber-500 text-white border-amber-500' },
  { label: '脱离', value: 'disengaged', emoji: '🔴', color: 'bg-red-50 border-red-200 text-red-700', activeColor: 'bg-red-500 text-white border-red-500' },
];

export const SnapshotCard: React.FC<SnapshotCardProps> = ({
  visible,
  snapshotId,
  countdownSeconds = 15,
  onRespond,
  onSkip,
  onTimeout,
}) => {
  const [timeLeft, setTimeLeft] = useState(countdownSeconds);
  const [selected, setSelected] = useState<string | null>(null);

  // 重置倒计时
  useEffect(() => {
    if (visible) {
      setTimeLeft(countdownSeconds);
      setSelected(null);
    }
  }, [visible, snapshotId, countdownSeconds]);

  // 倒计时逻辑
  useEffect(() => {
    if (!visible) return;
    if (timeLeft <= 0) {
      onTimeout(snapshotId);
      return;
    }
    const timer = setTimeout(() => setTimeLeft(t => t - 1), 1000);
    return () => clearTimeout(timer);
  }, [visible, timeLeft, snapshotId, onTimeout]);

  const handleSelect = useCallback((value: string) => {
    setSelected(value);
    // 短暂延迟后提交，让用户看到选中状态
    setTimeout(() => onRespond(snapshotId, value), 300);
  }, [snapshotId, onRespond]);

  const progressPercent = (timeLeft / countdownSeconds) * 100;

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ y: -80, opacity: 0, scale: 0.95 }}
          animate={{ y: 0, opacity: 1, scale: 1 }}
          exit={{ opacity: 0, scale: 0.95, y: -20 }}
          transition={{ type: 'spring', stiffness: 300, damping: 25 }}
          className="absolute top-4 left-4 right-4 z-40"
        >
          <div className="bg-white/95 backdrop-blur-xl rounded-3xl shadow-2xl shadow-black/10 border border-white/60 p-5 relative overflow-hidden">
            {/* 进度条 */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-gray-100">
              <motion.div
                className="h-full bg-gradient-to-r from-primary to-emerald-400"
                initial={{ width: '100%' }}
                animate={{ width: `${progressPercent}%` }}
                transition={{ duration: 0.3 }}
              />
            </div>

            {/* 头部 */}
            <div className="flex items-center justify-between mb-4 mt-1">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                <span className="text-sm font-bold text-gray-700">孩子现在状态如何？</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-3.5 h-3.5 text-gray-400" />
                <span className={`text-xs font-bold ${timeLeft <= 5 ? 'text-red-500' : 'text-gray-400'}`}>
                  {timeLeft}s
                </span>
                <button
                  onClick={() => onSkip(snapshotId)}
                  className="ml-1 p-1 rounded-full hover:bg-gray-100 transition"
                >
                  <X className="w-4 h-4 text-gray-400" />
                </button>
              </div>
            </div>

            {/* 选项按钮 */}
            <div className="flex space-x-3">
              {ENGAGEMENT_OPTIONS.map((option) => (
                <motion.button
                  key={option.value}
                  whileTap={{ scale: 0.92 }}
                  onClick={() => handleSelect(option.value)}
                  className={`flex-1 flex flex-col items-center py-3 px-2 rounded-2xl border-2 transition-all duration-200 ${
                    selected === option.value ? option.activeColor : option.color
                  }`}
                >
                  <span className="text-2xl mb-1">{option.emoji}</span>
                  <span className="text-xs font-bold">{option.label}</span>
                </motion.button>
              ))}
            </div>

            {/* 跳过按钮 */}
            <button
              onClick={() => onSkip(snapshotId)}
              className="w-full mt-3 py-2 text-xs text-gray-400 font-medium hover:text-gray-600 transition"
            >
              跳过本次
            </button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
