import React from 'react';
import {
    Activity,
    Dna,
    Lightbulb,
    Sparkles,
    TrendingUp,
    RefreshCw
} from 'lucide-react';
import {
    ResponsiveContainer,
    LineChart,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    Line
} from 'recharts';
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
    evaluation: EvaluationResult | null;
    gameReview: GameReviewResult | null;
    activeGame: Game | null;
    trendData: any[];
    gameReturnPage: Page;
    onBack: () => void;
    onReturnToList: () => void;
}

const GameSummaryPage: React.FC<GameSummaryPageProps> = ({
    isAnalyzing,
    evaluation,
    gameReview,
    activeGame,
    trendData,
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
            <div className="h-full bg-background p-6 flex flex-col items-center justify-center h-[60vh] text-center space-y-6 animate-in fade-in duration-700">
                <div className="relative">
                    <div className="w-20 h-20 border-4 border-gray-200 rounded-full"></div>
                    <div className="w-20 h-20 border-4 border-primary border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div>
                    <Activity className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-primary w-8 h-8" />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-gray-800">AI 正在复盘互动数据...</h2>
                    <p className="text-gray-500 text-sm mt-2">分析眼神接触频率、情绪稳定度及八大兴趣维度</p>
                </div>
            </div>
        );
    }

    if (!evaluation) {
        return (
            <div className="h-full bg-background p-6 flex flex-col items-center justify-center mt-20 text-gray-400">
                <p>无法生成评估结果</p>
                <button onClick={onReturnToList} className="mt-4 text-primary">返回</button>
            </div>
        );
    }

    return (
        <div className="h-full bg-background p-6 overflow-y-auto">
            <div className="animate-in slide-in-from-bottom-10 duration-700 fade-in pb-10">
                <div className="text-center mb-8">
                    <h2 className="text-2xl font-bold text-gray-800">本次互动评估</h2>
                    <p className="text-gray-400 text-xs mt-1">{gameStartTime}</p>
                </div>

                {/* 核心反馈与摘要卡片 */}
                <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 relative overflow-hidden">
                    <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-green-400 to-blue-500"></div>

                    <div className="flex justify-around mb-6 border-b border-gray-100 pb-6">
                        <div className="text-center">
                            <div className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-1">反馈质量</div>
                            <div className="text-2xl font-bold text-blue-600">{evaluation.feedbackScore || 0}</div>
                        </div>
                        <div className="w-px bg-gray-200 h-10 self-center"></div>
                        <div className="text-center">
                            <div className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-1">探索广度</div>
                            <div className="text-2xl font-bold text-purple-600">{evaluation.explorationScore || 0}</div>
                        </div>
                    </div>

                    <p className="text-gray-600 text-sm leading-relaxed px-2">{evaluation.summary}</p>
                </div>

                {/* 兴趣探索度分析 */}
                {evaluation.interestAnalysis && evaluation.interestAnalysis.length > 0 && (
                    <div className="bg-white p-5 rounded-2xl shadow-sm mb-6 border border-gray-100">
                        <h3 className="font-bold text-gray-700 mb-4 flex items-center">
                            <Dna className="w-5 h-5 mr-2 text-indigo-500" /> 兴趣探索度分析
                        </h3>
                        <div className="space-y-4">
                            {evaluation.interestAnalysis.map((item, idx) => (
                                <div key={idx} className="bg-gray-50 rounded-xl p-3 border border-gray-100">
                                    <p className="text-sm font-semibold text-gray-800 mb-2">"{item.behavior}"</p>
                                    <div className="flex flex-wrap gap-2">
                                        {item.matches.map((match, mIdx) => {
                                            const config = getDimensionConfig(match.dimension);
                                            return (
                                                <div key={mIdx} className="flex flex-col">
                                                    <div className={`flex items-center px-2 py-1 rounded-md text-xs font-bold ${config.color}`}>
                                                        <config.icon className="w-3 h-3 mr-1" />
                                                        {config.label} {(match.weight * 100).toFixed(0)}%
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                    {item.matches[0] && (
                                        <p className="text-[10px] text-gray-500 mt-2 italic border-t border-gray-200 pt-1">
                                            💡 {item.matches[0].reasoning}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* 下一步建议 (基础) */}
                <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white p-5 rounded-2xl shadow-lg mb-6 relative overflow-hidden">
                    <div className="relative z-10">
                        <h3 className="font-bold flex items-center mb-3">
                            <Lightbulb className="w-4 h-4 mr-2 text-yellow-300" /> 互动建议
                        </h3>
                        <p className="text-indigo-100 text-sm leading-relaxed font-medium">{evaluation.suggestion}</p>
                    </div>
                    <Sparkles className="absolute -right-2 -bottom-2 text-white/10 w-24 h-24 rotate-12" />
                </div>

                {/* AI 专业复盘 */}
                {gameReview && (
                    <div className="space-y-4 mb-6">
                        <div className="bg-white rounded-2xl shadow-sm p-5 border border-gray-100">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-bold text-gray-700 flex items-center">
                                    <Activity className="w-5 h-5 mr-2 text-primary" /> AI 专业复盘
                                </h3>
                                <span className={`text-xs px-2.5 py-1 rounded-full font-bold ${gameReview.recommendation === 'continue' ? 'bg-green-100 text-green-700' :
                                    gameReview.recommendation === 'adjust' ? 'bg-yellow-100 text-yellow-700' :
                                        'bg-red-100 text-red-700'
                                    }`}>
                                    {gameReview.recommendation === 'continue' ? '继续此游戏' :
                                        gameReview.recommendation === 'adjust' ? '建议调整' : '建议避免'}
                                </span>
                            </div>
                            <p className="text-gray-600 text-sm leading-relaxed mb-5">{gameReview.reviewSummary}</p>

                            <div className="space-y-2.5">
                                {[
                                    { key: 'childEngagement', label: '孩子配合度', color: 'bg-green-500' },
                                    { key: 'gameCompletion', label: '游戏完成度', color: 'bg-blue-500' },
                                    { key: 'emotionalConnection', label: '情感连接', color: 'bg-pink-500' },
                                    { key: 'communicationLevel', label: '沟通互动', color: 'bg-purple-500' },
                                    { key: 'skillProgress', label: '能力进步', color: 'bg-yellow-500' },
                                    { key: 'parentExecution', label: '家长执行', color: 'bg-indigo-500' }
                                ].map((dim) => {
                                    const score = gameReview.scores[dim.key as keyof typeof gameReview.scores];
                                    return (
                                        <div key={dim.key}>
                                            <div className="flex justify-between items-center mb-1">
                                                <span className="text-xs font-bold text-gray-600">{dim.label}</span>
                                                <span className="text-xs font-bold text-gray-800">{score}</span>
                                            </div>
                                            <div className="w-full bg-gray-100 rounded-full h-2">
                                                <div className={`${dim.color} h-2 rounded-full transition-all duration-700`} style={{ width: `${score}%` }}></div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-teal-500 to-emerald-600 text-white p-5 rounded-2xl shadow-lg relative overflow-hidden">
                            <div className="relative z-10">
                                <h3 className="font-bold flex items-center mb-3">
                                    <Lightbulb className="w-4 h-4 mr-2 text-yellow-300" /> 专业建议
                                </h3>
                                <p className="text-teal-100 text-sm leading-relaxed">{gameReview.nextStepSuggestion}</p>
                            </div>
                        </div>
                    </div>
                )}

                {/* 成长曲线 */}
                <div className="bg-white p-4 rounded-2xl shadow-sm mb-20 border border-gray-100">
                    <h3 className="font-bold text-gray-700 mb-4 flex items-center justify-between">
                        <span className="flex items-center">
                            <TrendingUp className="w-4 h-4 mr-2 text-green-500" /> 成长曲线已更新
                        </span>
                        <span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold">+1 记录</span>
                    </h3>
                    <div className="h-40 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={trendData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
                                <XAxis dataKey="name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval={0} />
                                <YAxis hide domain={[0, 100]} />
                                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} />
                                <Line
                                    type="monotone"
                                    dataKey="engagement"
                                    stroke="#10B981"
                                    strokeWidth={3}
                                    dot={(props: any) => {
                                        const isLast = props.index === trendData.length - 1;
                                        return (<circle cx={props.cx} cy={props.cy} r={isLast ? 6 : 4} fill={isLast ? "#10B981" : "#fff"} stroke="#10B981" strokeWidth={2} />);
                                    }}
                                    isAnimationActive={true}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* 底部按钮 */}
                <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100">
                    <button
                        onClick={onReturnToList}
                        className="w-full bg-gray-900 text-white py-3.5 rounded-xl font-bold shadow-lg hover:bg-gray-800 transition active:scale-95 flex items-center justify-center"
                    >
                        <RefreshCw className="w-4 h-4 mr-2" />
                        返回{getReturnLabel()}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default GameSummaryPage;
