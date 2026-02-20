import React, { useState } from 'react';
import { Lightbulb, ChevronLeft, ChevronRight, AlertTriangle, Timer, X } from 'lucide-react';
import { Game, FloorGame } from '../types';

interface GameStepCardProps {
    game: Game | FloorGame;
    currentStepIndex: number;
    timer: number;
    stepImages: Map<number, string>;
    onStepChange: (index: number) => void;
    onComplete: () => void;
    onAbort: () => void;
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
    formatTime
}) => {
    const [showHint, setShowHint] = useState(true);

    const steps = 'steps' in game ? game.steps : [];
    const currentStep = steps[currentStepIndex];
    const isLastStep = currentStepIndex === steps.length - 1;


    return (
        <div className="flex flex-col h-full bg-white rounded-3xl shadow-sm border border-gray-100 overflow-hidden relative">
            {/* Top Bar inside Card */}
            <div className="flex items-center px-6 py-3 bg-gray-50/50 border-b border-gray-100 shrink-0">
                {/* Left: Step Info */}
                <div className="w-1/3 flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm shadow-sm ring-1 ring-blue-100">
                        {currentStepIndex + 1}
                    </div>
                    <span className="text-xs font-bold text-gray-400 uppercase tracking-wider hidden sm:inline">
                        步骤 {currentStepIndex + 1} / {steps.length}
                    </span>
                </div>

                {/* Center: Timer */}
                <div className="w-1/3 flex justify-center">
                    <div className="flex items-center text-primary font-mono font-bold text-lg bg-blue-50 px-3 py-1 rounded-full ring-1 ring-blue-100 shadow-sm">
                        <Timer className="w-4 h-4 mr-1.5" />
                        {formatTime(timer)}
                    </div>
                </div>

                {/* Right: Abort Button */}
                <div className="w-1/3 flex justify-end">
                    <button
                        onClick={onAbort}
                        className="text-red-500 font-bold text-xs hover:bg-red-50 px-3 py-1.5 rounded-lg transition-colors flex items-center border border-red-100"
                    >
                        <X className="w-3.5 h-3.5 mr-1" />
                        退出互动
                    </button>
                </div>
            </div>

            {/* Main Content Area */}
            <div className="flex-1 overflow-y-auto no-scrollbar p-6 flex flex-col items-center">
                {stepImages.get(currentStepIndex) && (
                    <div className="w-full max-h-48 mb-6 rounded-2xl overflow-hidden shadow-md ring-4 ring-white shrink-0">
                        <img
                            src={stepImages.get(currentStepIndex)}
                            alt="步骤插图"
                            className="w-full h-full object-cover"
                        />
                    </div>
                )}

                <h2 className="text-xl md:text-2xl font-black text-gray-800 leading-tight text-center mb-6 px-4">
                    {currentStep?.instruction}
                </h2>

                {/* Hint Box - Minimalist Toggle */}
                <div className="w-full transition-all duration-300">
                    <button
                        onClick={() => setShowHint(!showHint)}
                        className="flex items-center space-x-2 text-xs font-bold text-blue-600 mb-2 hover:opacity-80 transition"
                    >
                        <Lightbulb className={`w-3.5 h-3.5 ${showHint ? 'fill-yellow-400 text-yellow-500' : ''}`} />
                        <span>{showHint ? '隐藏互动建议' : '查看互动建议'}</span>
                    </button>

                    {showHint && (
                        <div className="bg-blue-50/80 p-5 rounded-2xl border border-blue-100 text-left w-full animate-in fade-in slide-in-from-top-2 duration-300">
                            <p className="text-blue-900/80 text-sm leading-relaxed font-medium">
                                {currentStep?.guidance}
                            </p>
                        </div>
                    )}
                </div>
            </div>

            {/* Navigation Footer */}
            <div className="p-4 bg-gray-50/50 border-t border-gray-100 flex justify-between items-center shrink-0">
                <button
                    onClick={() => onStepChange(Math.max(0, currentStepIndex - 1))}
                    disabled={currentStepIndex === 0}
                    className={`flex items-center text-gray-500 font-bold transition px-4 py-2 rounded-xl hover:bg-white active:scale-95 ${currentStepIndex === 0 ? 'opacity-20 cursor-not-allowed' : ''}`}
                >
                    <ChevronLeft className="w-5 h-5 mr-1" />
                    上一步
                </button>

                {isLastStep ? (
                    <button
                        onClick={onComplete}
                        className="bg-primary text-white px-8 py-2.5 rounded-full font-bold shadow-lg shadow-primary/30 flex items-center hover:bg-green-600 transition transform active:scale-95"
                    >
                        完成挑战
                    </button>
                ) : (
                    <button
                        onClick={() => onStepChange(currentStepIndex + 1)}
                        className="bg-secondary text-white px-8 py-2.5 rounded-full font-bold shadow-lg shadow-secondary/30 flex items-center hover:bg-blue-600 transition transform active:scale-95"
                    >
                        下一步
                        <ChevronRight className="w-5 h-5 ml-1" />
                    </button>
                )}
            </div>

        </div>
    );
};
