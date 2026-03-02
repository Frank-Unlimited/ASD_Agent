import React from 'react';
import {
    Activity,
    Dna,
    Lightbulb,
    Sparkles,
    RefreshCw
} from 'lucide-react';
import { motion, Variants } from 'framer-motion';
import {
    Page,
    GameState,
    Game,
    EvaluationResult,
    GameReviewResult,
    InterestDimensionType
} from '../types';
import { getDimensionConfig } from '../utils/helpers';

interface GameSummaryPageProps {
    isAnalyzing: boolean;
    gameReview: GameReviewResult | null;
    activeGame: Game | null;
    gameReturnPage: Page;
    onBack: () => void;
    onReturnToList: () => void;
}

const GameSummaryPage: React.FC<GameSummaryPageProps> = ({
    isAnalyzing,
    gameReview,
    activeGame,
    gameReturnPage,
    onBack,
    onReturnToList
}) => {
    const gameStartTime = activeGame?.date
        ? new Date(activeGame.date).toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }).replace(/\//g, '-')
        : new Date().toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            hour12: false
        }).replace(/\//g, '-');

    const getReturnLabel = () => {
        switch (gameReturnPage) {
            case Page.CHAT: return '对话';
            case Page.CALENDAR: return '日历计划';
            default: return '游戏库';
        }
    };

    if (isAnalyzing) {
        return (
            <div className="h-full relative flex flex-col items-center justify-center min-h-[70vh] text-center px-10 overflow-hidden" style={{
                background: 'radial-gradient(circle at center, rgba(16, 185, 129, 0.05), transparent 70%), #F9FAFB'
            }}>
                <div className="relative mb-12">
                    {/* Background Pulsing Rings */}
                    <motion.div
                        className="absolute inset-0 bg-primary/10 rounded-full"
                        animate={{
                            scale: [1, 1.8, 1],
                            opacity: [0.1, 0, 0.1],
                        }}
                        transition={{
                            duration: 3,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    />
                    <motion.div
                        className="absolute inset-0 bg-primary/20 rounded-full"
                        animate={{
                            scale: [1, 1.4, 1],
                            opacity: [0.2, 0, 0.2],
                        }}
                        transition={{
                            duration: 3,
                            delay: 0.5,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    />

                    {/* Main Icon Container */}
                    <motion.div
                        className="relative z-10 w-24 h-24 bg-white rounded-3xl shadow-2xl flex items-center justify-center border border-white/40 backdrop-blur-md"
                        animate={{
                            y: [-5, 5, -5]
                        }}
                        transition={{
                            duration: 4,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    >
                        <Activity className="text-primary w-10 h-10" />

                        {/* Orbiting particles */}
                        <motion.div
                            className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full shadow-lg shadow-blue-200"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 5, repeat: Infinity, ease: "linear" }}
                            style={{ originX: "-30px", originY: "40px" }}
                        />
                        <motion.div
                            className="absolute -bottom-1 -left-1 w-2 h-2 bg-purple-500 rounded-full shadow-lg shadow-purple-200"
                            animate={{ rotate: -360 }}
                            transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                            style={{ originX: "40px", originY: "-30px" }}
                        />
                    </motion.div>
                </div>

                <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <h2 className="text-2xl font-black text-gray-900 tracking-tight mb-3">正在深度复盘...</h2>
                    <div className="flex flex-col items-center space-y-2">
                        <p className="text-gray-500 text-sm font-medium">AI 专家正在分析互动的底层兴趣动因</p>
                        <div className="flex items-center space-x-2">
                            <motion.span
                                className="w-1.5 h-1.5 bg-primary rounded-full"
                                animate={{ opacity: [0, 1, 0] }}
                                transition={{ repeat: Infinity, duration: 1 }}
                            />
                            <span className="text-[10px] text-primary/60 font-black tracking-widest uppercase">DIR 评估逻辑执行中</span>
                        </div>
                    </div>
                </motion.div>
            </div>
        );
    }

    if (!gameReview) {
        return (
            <div className="h-full bg-background p-6 flex flex-col items-center justify-center mt-20 text-gray-400">
                <p>无法生成复盘结果</p>
                <button onClick={onReturnToList} className="mt-4 text-primary">返回</button>
            </div>
        );
    }

    const containerVariants: Variants = {
        hidden: { opacity: 0 },
        visible: {
            opacity: 1,
            transition: {
                staggerChildren: 0.15
            }
        }
    };

    const itemVariants: Variants = {
        hidden: { y: 20, opacity: 0 },
        visible: {
            y: 0,
            opacity: 1,
            transition: {
                type: 'spring',
                stiffness: 100,
                damping: 15
            }
        }
    };

    return (
        <div className="h-full relative overflow-y-auto no-scrollbar" style={{
            background: 'radial-gradient(circle at top right, rgba(16, 185, 129, 0.08), transparent 40%), radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.08), transparent 40%), #F9FAFB'
        }}>
            <motion.div
                className="p-6 pb-24 max-w-2xl mx-auto"
                variants={containerVariants}
                initial="hidden"
                animate="visible"
            >
                <motion.div variants={itemVariants} className="text-center mb-10 mt-4">
                    <h2 className="text-3xl font-black text-gray-900 tracking-tight">互动复盘报告</h2>
                    <p className="text-gray-400 text-xs mt-2 font-medium tracking-widest uppercase">{gameStartTime}</p>
                </motion.div>

                <motion.div variants={itemVariants} className="bg-white/70 backdrop-blur-xl rounded-[2.5rem] shadow-xl shadow-emerald-900/5 p-8 mb-8 relative overflow-hidden border border-white/40">
                    <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-primary via-blue-500 to-purple-500"></div>

                    <div className="flex justify-around mb-8 border-b border-gray-100/50 pb-8">
                        <div className="text-center">
                            <div className="text-[10px] text-gray-400 font-black uppercase tracking-[0.2em] mb-2">反馈质量</div>
                            <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-br from-blue-600 to-blue-400 leading-none">
                                {gameReview.scores.feedbackScore || 0}
                            </div>
                        </div>
                        <div className="w-px bg-gradient-to-b from-transparent via-gray-200 to-transparent h-12 self-center"></div>
                        <div className="text-center">
                            <div className="text-[10px] text-gray-400 font-black uppercase tracking-[0.2em] mb-2">探索广度</div>
                            <div className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-br from-purple-600 to-purple-400 leading-none">
                                {gameReview.scores.explorationScore || 0}
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center mb-4 translate-x-[-4px]">
                        <div className="p-1.5 bg-primary/10 rounded-lg mr-3">
                            <Sparkles className="w-5 h-5 text-primary" />
                        </div>
                        <span className="text-base font-black text-gray-800 tracking-tight">专家总结</span>
                    </div>
                    <div className="relative">
                        <span className="absolute -left-2 -top-2 text-4xl text-primary/10 font-serif leading-none">“</span>
                        <p className="text-gray-600 text-sm leading-relaxed px-2 font-medium relative z-10">
                            {gameReview.reviewSummary}
                        </p>
                    </div>
                </motion.div>

                {/* 行为分析 Agent 输出 */}
                {gameReview.interestAnalysis && gameReview.interestAnalysis.length > 0 && (
                    <motion.div variants={itemVariants} className="bg-white/60 backdrop-blur-lg p-6 rounded-[2rem] shadow-sm mb-8 border border-white/40">
                        <h3 className="font-black text-gray-800 mb-6 flex items-center text-lg tracking-tight">
                            <div className="p-1.5 bg-indigo-500/10 rounded-lg mr-3">
                                <Dna className="w-5 h-5 text-indigo-600" />
                            </div>
                            行为证据与兴趣推演
                        </h3>
                        <div className="space-y-5">
                            {gameReview.interestAnalysis.map((item, idx) => (
                                <motion.div
                                    key={idx}
                                    whileHover={{ y: -4, backgroundColor: 'rgba(255,255,255,0.8)' }}
                                    className="bg-white/40 rounded-2xl p-4 border border-white/60 shadow-sm transition-all"
                                >
                                    <p className="text-sm font-bold text-gray-800 mb-3 ml-1 leading-snug">"{item.behavior}"</p>
                                    <div className="flex flex-wrap gap-2 mb-3">
                                        {item.matches.map((match, mIdx) => {
                                            const config = getDimensionConfig(match.dimension);
                                            return (
                                                <div key={mIdx} className={`flex items-center px-3 py-1.5 rounded-full text-[10px] font-black tracking-wider transition-colors ${config.color}`}>
                                                    <config.icon className="w-3 h-3 mr-1.5" />
                                                    {config.label.toUpperCase()} {(match.weight * 100).toFixed(0)}%
                                                </div>
                                            );
                                        })}
                                    </div>
                                    {item.matches[0] && (
                                        <div className="mt-2 pt-3 border-t border-gray-100/50 flex items-start">
                                            <span className="text-primary mr-2 text-xs">💡</span>
                                            <p className="text-[11px] text-gray-500 font-medium italic leading-relaxed">
                                                {item.matches[0].reasoning}
                                            </p>
                                        </div>
                                    )}
                                </motion.div>
                            ))}
                        </div>
                    </motion.div>
                )}

                {/* DIR 会诊报告与专业建议 */}
                <motion.div variants={itemVariants} className="bg-white/70 backdrop-blur-xl rounded-[2rem] p-6 border border-white/40 shadow-sm mb-8">
                    <div className="flex items-center justify-between mb-8">
                        <h3 className="font-black text-gray-800 flex items-center text-lg tracking-tight">
                            <div className="p-1.5 bg-primary/10 rounded-lg mr-3">
                                <Activity className="w-5 h-5 text-primary" />
                            </div>
                            DIR 专家会诊报告
                        </h3>
                        <span className={`text-[10px] px-3 py-1 rounded-full font-black tracking-widest uppercase ${gameReview.recommendation === 'continue' ? 'bg-green-100 text-green-700' :
                            gameReview.recommendation === 'adjust' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-red-100 text-red-700'
                            }`}>
                            {gameReview.recommendation === 'continue' ? '继续此游戏' :
                                gameReview.recommendation === 'adjust' ? '建议调整' : '建议避免'}
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5 mb-10">
                        {[
                            { key: 'childEngagement', label: '孩子参与度', color: 'from-green-400 to-emerald-500', shadow: 'shadow-emerald-200' },
                            { key: 'gameCompletion', label: '游戏完成度', color: 'from-blue-400 to-indigo-500', shadow: 'shadow-blue-200' },
                            { key: 'emotionalConnection', label: '情感连接', color: 'from-pink-400 to-rose-500', shadow: 'shadow-pink-200' },
                            { key: 'communicationLevel', label: '沟通互动', color: 'from-purple-400 to-violet-500', shadow: 'shadow-purple-200' },
                            { key: 'skillProgress', label: '能力进步', color: 'from-yellow-400 to-orange-500', shadow: 'shadow-yellow-200' },
                            { key: 'parentExecution', label: '家长指导', color: 'from-indigo-400 to-blue-600', shadow: 'shadow-indigo-200' }
                        ].map((dim) => {
                            const score = gameReview.scores[dim.key as keyof typeof gameReview.scores];
                            return (
                                <div key={dim.key} className="group">
                                    <div className="flex justify-between items-center mb-2">
                                        <span className="text-[11px] font-black text-gray-500 tracking-wider uppercase">{dim.label}</span>
                                        <span className="text-xs font-black text-gray-900">{score}</span>
                                    </div>
                                    <div className="w-full bg-gray-100/50 rounded-full h-1.5 overflow-hidden border border-gray-100/20">
                                        <motion.div
                                            initial={{ width: 0 }}
                                            animate={{ width: `${score}%` }}
                                            transition={{ duration: 1, delay: 0.5, ease: "easeOut" }}
                                            className={`bg-gradient-to-r ${dim.color} h-full rounded-full shadow-lg ${dim.shadow}`}
                                        />
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    <div className="bg-gradient-to-br from-indigo-600 to-blue-700 text-white p-6 rounded-[2rem] shadow-2xl shadow-indigo-200 relative overflow-hidden">
                        <div className="relative z-10">
                            <h3 className="font-black flex items-center mb-4 tracking-tight">
                                <div className="p-1 px-2 bg-white/20 rounded-md mr-3">
                                    <Lightbulb className="w-4 h-4 text-yellow-300" />
                                </div>
                                专业干预方案
                            </h3>
                            <p className="text-indigo-50 text-sm leading-relaxed font-medium">
                                {gameReview.nextStepSuggestion}
                            </p>
                        </div>
                        <Sparkles className="absolute -right-2 -bottom-2 text-white/10 w-32 h-32 rotate-12" />
                    </div>
                </motion.div>


                {/* 底部按钮 */}
                <motion.div variants={itemVariants} className="fixed bottom-0 left-0 right-0 p-6 bg-white/80 backdrop-blur-md border-t border-gray-100 z-50">
                    <button
                        onClick={onReturnToList}
                        className="w-full max-w-lg mx-auto bg-gray-900 text-white py-4 rounded-2xl font-black shadow-2xl hover:bg-gray-800 transition transform active:scale-[0.98] flex items-center justify-center tracking-widest uppercase text-xs"
                    >
                        <RefreshCw className="w-4 h-4 mr-3" />
                        返回{getReturnLabel()}
                    </button>
                </motion.div>
            </motion.div>
        </div>
    );
};

export default GameSummaryPage;
