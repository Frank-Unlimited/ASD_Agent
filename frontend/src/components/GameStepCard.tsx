import React, { useState } from 'react';
import { Timer, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { Game, FloorGame, BehaviorType } from '../types';
import { QuickRecordBar } from './QuickRecordBar';

interface GameStepCardProps {
  game: Game | FloorGame;
  currentStepIndex: number;
  timer: number;
  stepImages: Map<number, string>;
  onStepChange: (index: number) => void;
  onComplete: () => void;
  onAbort: () => void;
  onRecord: (behaviorType: BehaviorType) => void;
  formatTime: (seconds: number) => string;
}

export const GameStepCard: React.FC<GameStepCardProps> = ({
  game,
  currentStepIndex,
  timer,
  stepImages,
  onStepChange,
  onComplete,
  onAbort,
  onRecord,
  formatTime
}) => {
  const steps = 'steps' in game ? game.steps : [];
  const currentStep = steps[currentStepIndex];
  const isLastStep = currentStepIndex === steps.length - 1;

  const stepTitle = currentStep && 'stepTitle' in currentStep ? currentStep.stepTitle : `步骤 ${currentStepIndex + 1}`;
  const instruction = currentStep && 'instruction' in currentStep ? currentStep.instruction : '';
  const guidance = currentStep && 'guidance' in currentStep ? currentStep.guidance : '';

  // 获取游戏标题，处理 Game 和 FloorGame 两种类型
  const gameTitle = 'title' in game ? game.title : game.gameTitle;

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-blue-50/30 via-white to-green-50/20 overflow-hidden">
      {/* 极简顶部栏 */}
      <div className="flex items-center justify-between px-4 py-3 bg-white/60 backdrop-blur-sm border-b border-blue-100/50 shrink-0 h-[60px]">
        {/* 左侧：图标 + 标题 */}
        <div className="flex items-center space-x-2 flex-1">
          {stepImages.get(currentStepIndex) && (
            <img
              src={stepImages.get(currentStepIndex)}
              alt="游戏图标"
              className="w-5 h-5 rounded-lg object-cover"
            />
          )}
          <span className="text-sm font-bold text-gray-800 truncate">{gameTitle}</span>
        </div>

        {/* 中间：计时器 */}
        <div className="flex items-center justify-center px-4">
          <div className="flex items-center text-blue-600 font-mono font-bold text-sm bg-blue-100/60 px-3 py-1 rounded-full">
            <Timer className="w-3 h-3 mr-1" />
            {formatTime(timer)}
          </div>
        </div>

        {/* 右侧：退出按钮 */}
        <button
          onClick={onAbort}
          className="text-red-500 font-bold text-xs hover:bg-red-50/80 px-3 py-1.5 rounded-lg transition-colors flex items-center border border-red-200/60"
        >
          <X className="w-3 h-3 mr-1" />
          退出
        </button>
      </div>

      {/* 步骤说明区域（可滚动） */}
      <div className="flex-1 overflow-y-auto px-4 py-4">
        {/* 步骤标题 */}
        <div className="mb-3">
          <span className="text-xs font-bold text-blue-600 bg-blue-100/60 px-3 py-1 rounded-full">
            {stepTitle}
          </span>
        </div>

        {/* 步骤说明 */}
        <h2 className="text-lg font-bold text-gray-800 text-left mb-4 leading-relaxed">
          {instruction}
        </h2>

        {/* 互动建议 */}
        {guidance && (
          <div className="bg-blue-50/60 p-4 rounded-2xl border border-blue-200/50 mb-4">
            <p className="text-sm text-blue-900/80 leading-relaxed">
              <span className="font-bold">💡 互动建议：</span>
              {guidance}
            </p>
          </div>
        )}

        {/* 步骤图片（如果有且不是小图标） */}
        {stepImages.get(currentStepIndex) && (
          <div className="w-full rounded-2xl overflow-hidden shadow-md ring-4 ring-white/80 mb-4">
            <img
              src={stepImages.get(currentStepIndex)}
              alt="步骤插图"
              className="w-full h-auto object-cover"
            />
          </div>
        )}
      </div>

      {/* 快捷按钮栏 */}
      <QuickRecordBar onRecord={onRecord} />

      {/* 步骤导航按钮 */}
      <div className="flex items-center justify-between px-4 py-3 bg-white/60 backdrop-blur-sm border-t border-blue-100/50 shrink-0 h-[60px]">
        <button
          onClick={() => onStepChange(Math.max(0, currentStepIndex - 1))}
          disabled={currentStepIndex === 0}
          className={`flex items-center text-gray-600 font-bold transition px-6 py-2.5 rounded-full border-2 border-blue-200 bg-white/80 hover:bg-white active:scale-95 ${currentStepIndex === 0 ? 'opacity-30 cursor-not-allowed' : ''}`}
        >
          <ChevronLeft className="w-4 h-4 mr-1" />
          上一步
        </button>

        {isLastStep ? (
          <button
            onClick={onComplete}
            className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-2.5 rounded-full font-bold shadow-lg shadow-blue-500/30 flex items-center hover:shadow-xl transition transform active:scale-95"
          >
            ✓ 完成挑战
          </button>
        ) : (
          <button
            onClick={() => onStepChange(currentStepIndex + 1)}
            className="bg-gradient-to-r from-blue-500 to-blue-600 text-white px-8 py-2.5 rounded-full font-bold shadow-lg shadow-blue-500/30 flex items-center hover:shadow-xl transition transform active:scale-95"
          >
            下一步
            <ChevronRight className="w-4 h-4 ml-1" />
          </button>
        )}
      </div>
    </div>
  );
};
