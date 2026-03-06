import React, { useState } from 'react';
import { BehaviorType } from '../types';

interface QuickRecordBarProps {
  onRecord: (behaviorType: BehaviorType) => void;
}

const BEHAVIORS = [
  { type: BehaviorType.EYE_CONTACT, icon: '👁️', label: '眼神', color: 'from-blue-400 to-blue-500' },
  { type: BehaviorType.ACTIVE_RESPONSE, icon: '🗣️', label: '回应', color: 'from-green-400 to-green-500' },
  { type: BehaviorType.SMILE_HAPPY, icon: '😄', label: '开心', color: 'from-yellow-400 to-orange-400' },
  { type: BehaviorType.REFUSE_RESISTANT, icon: '🚫', label: '拒绝', color: 'from-red-400 to-red-500' },
  { type: BehaviorType.DISTRACTED, icon: '📱', label: '分心', color: 'from-purple-400 to-purple-500' },
  { type: BehaviorType.FOCUSED_ENGAGED, icon: '🎯', label: '专注', color: 'from-teal-400 to-teal-500' },
];

export const QuickRecordBar: React.FC<QuickRecordBarProps> = ({ onRecord }) => {
  const [feedback, setFeedback] = useState<string | null>(null);

  const handleClick = (behaviorType: BehaviorType, label: string) => {
    onRecord(behaviorType);

    // 显示反馈
    setFeedback(`✓ 已记录：${label}`);
    setTimeout(() => setFeedback(null), 800);
  };

  return (
    <div className="flex flex-col items-center bg-white rounded-t-3xl shadow-md border-b border-gray-100 py-3 px-2">
      {/* 反馈提示 */}
      {feedback && (
        <div className="text-xs font-bold text-green-600 mb-2 animate-pulse">
          {feedback}
        </div>
      )}

      {/* 按钮组 */}
      <div className="flex justify-around items-center w-full max-w-lg">
        {BEHAVIORS.map((behavior) => (
          <button
            key={behavior.type}
            className={`flex flex-col items-center bg-gradient-to-br ${behavior.color} w-12 h-12 rounded-full shadow-md active:scale-90 transition-transform hover:shadow-lg`}
            onClick={() => handleClick(behavior.type, behavior.label)}
            title={behavior.label}
          >
            <span className="text-2xl">{behavior.icon}</span>
            <span className="text-[10px] text-white font-bold mt-0.5">{behavior.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};
