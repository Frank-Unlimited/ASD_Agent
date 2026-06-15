import React, { useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Plus, X } from 'lucide-react';
import { ButtonConfig } from '../services/gameRecordingService';

interface DynamicButtonGroupProps {
  buttons: ButtonConfig[];
  onButtonClick: (button: ButtonConfig, detail?: string) => void;
  onAddCustomButton: (label: string) => void;
}

export const DynamicButtonGroup: React.FC<DynamicButtonGroupProps> = ({
  buttons,
  onButtonClick,
  onAddCustomButton,
}) => {
  const [showAddInput, setShowAddInput] = useState(false);
  const [customLabel, setCustomLabel] = useState('');

  const handleAdd = useCallback(() => {
    const trimmed = customLabel.trim();
    if (trimmed) {
      onAddCustomButton(trimmed);
      setCustomLabel('');
      setShowAddInput(false);
    }
  }, [customLabel, onAddCustomButton]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleAdd();
    if (e.key === 'Escape') { setShowAddInput(false); setCustomLabel(''); }
  };

  return (
    <div className="px-4 pb-2">
      <div className="flex items-center flex-wrap gap-2">
        {buttons.map((btn) => (
          <motion.button
            key={btn.id}
            whileTap={{ scale: 0.92 }}
            onClick={() => onButtonClick(btn)}
            className="flex items-center space-x-1.5 px-4 py-2.5 rounded-full border-2 border-primary/20 bg-primary/5 text-primary font-bold text-sm transition-all hover:bg-primary/10 hover:border-primary/40 active:bg-primary/20 min-h-[44px]"
          >
            <span className="text-base">{btn.icon}</span>
            <span>{btn.label}</span>
          </motion.button>
        ))}

        {/* 添加自定义按钮 */}
        <AnimatePresence mode="wait">
          {showAddInput ? (
            <motion.div
              key="input"
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 'auto', opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="flex items-center space-x-1 overflow-hidden"
            >
              <input
                autoFocus
                value={customLabel}
                onChange={(e) => setCustomLabel(e.target.value)}
                onKeyDown={handleKeyDown}
                onBlur={() => { if (!customLabel.trim()) setShowAddInput(false); }}
                placeholder="输入行为名"
                className="w-24 px-3 py-2 text-sm border-2 border-primary/30 rounded-full focus:outline-none focus:border-primary bg-white"
                maxLength={8}
              />
              <button
                onClick={handleAdd}
                disabled={!customLabel.trim()}
                className="p-2 rounded-full bg-primary text-white disabled:opacity-40 transition min-w-[36px] min-h-[36px] flex items-center justify-center"
              >
                <Plus className="w-4 h-4" />
              </button>
              <button
                onClick={() => { setShowAddInput(false); setCustomLabel(''); }}
                className="p-2 rounded-full bg-gray-100 text-gray-500 hover:bg-gray-200 transition min-w-[36px] min-h-[36px] flex items-center justify-center"
              >
                <X className="w-4 h-4" />
              </button>
            </motion.div>
          ) : (
            <motion.button
              key="add-btn"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              whileTap={{ scale: 0.92 }}
              onClick={() => setShowAddInput(true)}
              className="flex items-center justify-center w-11 h-11 rounded-full border-2 border-dashed border-gray-300 text-gray-400 hover:border-primary hover:text-primary transition"
            >
              <Plus className="w-5 h-5" />
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};
