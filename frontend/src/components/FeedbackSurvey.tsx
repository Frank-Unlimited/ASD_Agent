import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronRight, ChevronLeft, Check, Star, MessageSquare, Heart, Activity, ThumbsUp, ThumbsDown, Camera, Video, X, Upload } from 'lucide-react';
import { FeedbackData } from '../types';

interface FeedbackSurveyProps {
    onComplete: (data: FeedbackData) => void;
    onSkip?: () => void;
    gameTitle?: string;
    videoFile?: File | null;
    onVideoChange?: (file: File | null) => void;
    isProcessingVideo?: boolean;
}

const FeedbackSurvey: React.FC<FeedbackSurveyProps> = ({
    onComplete,
    onSkip,
    gameTitle,
    videoFile,
    onVideoChange,
    isProcessingVideo
}) => {
    const [step, setStep] = useState(1);
    const videoInputRef = React.useRef<HTMLInputElement>(null);
    const [data, setData] = useState<FeedbackData>({
        q1: '',
        q2: '',
        q3: '',
        q4: '',
        q5: ''
    });

    const totalSteps = 5;

    const nextStep = () => {
        if (step < totalSteps) setStep(step + 1);
        else onComplete(data);
    };

    const prevStep = () => {
        if (step > 1) setStep(step - 1);
    };

    const updateData = (key: keyof FeedbackData, value: string, autoNext = false) => {
        setData(prev => ({ ...prev, [key]: value }));
        if (autoNext) {
            setTimeout(() => {
                if (step < totalSteps) setStep(step + 1);
                else onComplete({ ...data, [key]: value });
            }, 300);
        }
    };

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <motion.div
                        key="step1"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="space-y-6"
                    >
                        <div className="text-center">
                            <span className="text-primary text-xs font-bold uppercase tracking-widest">维度 1：共同注意</span>
                            <h3 className="text-xl font-bold text-gray-800 mt-2">互动中，孩子的参与状态是？</h3>
                        </div>
                        <div className="grid gap-3">
                            {[
                                { id: '高度同步', icon: '🌟', label: '高度同步', desc: '眼神交流多，能持续跟随互动' },
                                { id: '基本配合', icon: '⛅', label: '基本配合', desc: '参与了，但容易断线或分心' },
                                { id: '回避游离', icon: '🌑', label: '回避/游离', desc: '进入自我世界或拒绝互动' }
                            ].map(opt => (
                                <button
                                    key={opt.id}
                                    onClick={() => updateData('q1', opt.id, true)}
                                    className={`flex items-center p-4 rounded-2xl border-2 transition-all text-left ${data.q1 === opt.id ? 'border-primary bg-blue-50' : 'border-gray-100 hover:border-blue-200'
                                        }`}
                                >
                                    <span className="text-2xl mr-4">{opt.icon}</span>
                                    <div>
                                        <div className="font-bold text-gray-800">{opt.label}</div>
                                        <div className="text-xs text-gray-500">{opt.desc}</div>
                                    </div>
                                    {data.q1 === opt.id && <Check className="ml-auto text-primary w-5 h-5" />}
                                </button>
                            ))}
                        </div>
                    </motion.div>
                );
            case 2:
                return (
                    <motion.div
                        key="step2"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="space-y-6"
                    >
                        <div className="text-center">
                            <span className="text-primary text-xs font-bold uppercase tracking-widest">维度 2：沟通循环</span>
                            <h3 className="text-xl font-bold text-gray-800 mt-2">孩子今天发起了多少次主动沟通？</h3>
                            <p className="text-xs text-gray-400 mt-1">包括眼神、表情、动作或发声的往返</p>
                        </div>
                        <div className="flex flex-col space-y-3">
                            {[
                                { id: '1-3次', label: '1-3次', desc: '初级循环', color: 'bg-green-50 text-green-700' },
                                { id: '4-10次', label: '4-10次', desc: '进阶循环', color: 'bg-blue-50 text-blue-700' },
                                { id: '10次以上', label: '10次以上', desc: '长循环', color: 'bg-purple-50 text-purple-700' }
                            ].map(opt => (
                                <button
                                    key={opt.id}
                                    onClick={() => updateData('q2', opt.id, true)}
                                    className={`p-5 rounded-2xl border-2 transition-all flex justify-between items-center ${data.q2 === opt.id ? 'border-primary bg-blue-50' : 'border-gray-100 hover:border-blue-200'
                                        }`}
                                >
                                    <div>
                                        <span className="text-lg font-bold">{opt.label}</span>
                                        <span className="ml-3 text-xs opacity-60 font-medium">({opt.desc})</span>
                                    </div>
                                    {data.q2 === opt.id && <Check className="text-primary w-5 h-5" />}
                                </button>
                            ))}
                        </div>
                    </motion.div>
                );
            case 3:
                return (
                    <motion.div
                        key="step3"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="space-y-6"
                    >
                        <div className="text-center">
                            <span className="text-primary text-xs font-bold uppercase tracking-widest">维度 3：情绪调节</span>
                            <h3 className="text-xl font-bold text-gray-800 mt-2">孩子在互动中的情绪状态是？</h3>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            {[
                                { id: '平静愉悦', icon: '😊', label: '平静愉悦' },
                                { id: '兴奋高涨', icon: '🤩', label: '兴奋高涨' },
                                { id: '焦虑不安', icon: '😟', label: '焦虑不安' },
                                { id: '情绪爆发', icon: '😫', label: '情绪爆发' }
                            ].map(opt => (
                                <button
                                    key={opt.id}
                                    onClick={() => updateData('q3', opt.id, true)}
                                    className={`flex flex-col items-center justify-center p-6 rounded-3xl border-2 transition-all ${data.q3 === opt.id ? 'border-primary bg-blue-50 shadow-lg shadow-blue-100' : 'border-gray-50 bg-gray-50/50 hover:bg-white hover:border-blue-100'
                                        }`}
                                >
                                    <span className="text-4xl mb-3">{opt.icon}</span>
                                    <span className="font-bold text-sm text-gray-700">{opt.label}</span>
                                </button>
                            ))}
                        </div>
                    </motion.div>
                );
            case 4:
                return (
                    <motion.div
                        key="step4"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="space-y-6"
                    >
                        <div className="text-center">
                            <span className="text-primary text-xs font-bold uppercase tracking-widest">维度 4：互动随手记</span>
                            <h3 className="text-xl font-bold text-gray-800 mt-2">互动中有哪些“闪光点”或挑战？</h3>
                        </div>
                        <textarea
                            value={data.q4}
                            onChange={(e) => updateData('q4', e.target.value)}
                            className="w-full bg-gray-50 rounded-2xl p-5 text-sm min-h-[160px] focus:bg-white focus:ring-2 focus:ring-primary/20 outline-none transition border border-gray-100"
                            placeholder="例如：孩子主动递给我玩具；我们通过玩车建立了良好的循环..."
                        />
                        <div className="flex flex-wrap gap-2">
                            {['眼神对视', '模仿动作', '主动发起', '共享快乐', '处理挑战'].map(tag => (
                                <button
                                    key={tag}
                                    onClick={() => updateData('q4', data.q4 ? `${data.q4} #${tag}` : `#${tag}`)}
                                    className="px-3 py-1.5 bg-gray-100 rounded-full text-[10px] font-bold text-gray-500 hover:bg-primary hover:text-white transition-colors"
                                >
                                    #{tag}
                                </button>
                            ))}
                        </div>

                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <h4 className="text-xs font-bold text-gray-500 mb-3 flex items-center">
                                <Camera className="w-3 h-3 mr-1" /> 上传互动视频 (可选)
                            </h4>
                            <input
                                type="file"
                                ref={videoInputRef}
                                hidden
                                accept="video/*"
                                onChange={(e) => onVideoChange?.(e.target.files?.[0] || null)}
                            />
                            {videoFile ? (
                                <div className="flex items-center justify-between bg-blue-50 p-3 rounded-xl">
                                    <div className="flex items-center">
                                        <Video className="w-4 h-4 text-primary mr-2" />
                                        <div className="max-w-[120px]">
                                            <p className="text-[10px] font-bold text-gray-800 truncate">{videoFile.name}</p>
                                        </div>
                                    </div>
                                    <button onClick={() => onVideoChange?.(null)} className="p-1 text-gray-400 hover:text-red-500"><X className="w-4 h-4" /></button>
                                </div>
                            ) : (
                                <button
                                    onClick={() => videoInputRef.current?.click()}
                                    className="w-full border-2 border-dashed border-gray-100 rounded-xl py-4 flex items-center justify-center space-x-2 hover:bg-gray-50 transition group"
                                >
                                    <Upload className="w-4 h-4 text-gray-300 group-hover:text-primary transition" />
                                    <span className="text-[10px] font-bold text-gray-400 group-hover:text-gray-600">选择视频文件</span>
                                </button>
                            )}
                        </div>
                    </motion.div>
                );
            case 5:
                return (
                    <motion.div
                        key="step5"
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        className="space-y-6"
                    >
                        <div className="text-center">
                            <span className="text-primary text-xs font-bold uppercase tracking-widest">维度 5：助手反馈</span>
                            <h3 className="text-xl font-bold text-gray-800 mt-2">AI 助手的建议对您是否有帮助？</h3>
                        </div>
                        <div className="flex justify-center space-x-6">
                            {[
                                { id: '非常有用', icon: <ThumbsUp className="w-8 h-8" />, label: '很有帮助' },
                                { id: '有待改进', icon: <ThumbsDown className="w-8 h-8" />, label: '需要改进' }
                            ].map(opt => (
                                <button
                                    key={opt.id}
                                    onClick={() => updateData('q5', opt.id)}
                                    className={`flex flex-col items-center justify-center w-32 h-32 rounded-3xl border-2 transition-all ${data.q5 === opt.id ? 'border-primary bg-primary text-white shadow-lg shadow-blue-200' : 'border-gray-50 bg-gray-50/50 text-gray-400 hover:border-blue-100 hover:bg-white hover:text-primary'
                                        }`}
                                >
                                    {opt.icon}
                                    <span className="font-bold text-xs mt-3">{opt.label}</span>
                                </button>
                            ))}
                        </div>
                        <div className="pt-4 text-center">
                            <button
                                onClick={() => onComplete(data)}
                                disabled={!data.q5}
                                className={`px-10 py-4 rounded-2xl font-bold transition-all ${data.q5 ? 'bg-primary text-white shadow-xl shadow-blue-200 active:scale-95' : 'bg-gray-100 text-gray-300'
                                    }`}
                            >
                                生成复盘报告
                            </button>
                        </div>
                    </motion.div>
                );
            default:
                return null;
        }
    };

    return (
        <div className="flex flex-col h-full max-w-md mx-auto relative pt-4 pb-8">
            {/* Progress Header */}
            <div className="px-6 mb-8 mt-2">
                <div className="flex justify-between items-center mb-2">
                    <span className="text-[10px] font-bold text-gray-400">调查进度 {step}/{totalSteps}</span>
                    <div className="flex space-x-1">
                        {[1, 2, 3, 4, 5].map(i => (
                            <div
                                key={i}
                                className={`h-1 rounded-full transition-all duration-300 ${i === step ? 'w-6 bg-primary' : i < step ? 'w-2 bg-primary/40' : 'w-2 bg-gray-100'
                                    }`}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Survey Content */}
            <div className="flex-1 px-6">
                <AnimatePresence mode="wait">
                    {renderStep()}
                </AnimatePresence>
            </div>

            {/* Navigation Footer */}
            <div className="px-6 pt-6 flex items-center justify-between shrink-0">
                <button
                    onClick={prevStep}
                    disabled={step === 1}
                    className={`p-4 rounded-2xl transition-colors ${step === 1 ? 'text-gray-200' : 'text-gray-400 hover:bg-gray-50 active:scale-90'
                        }`}
                >
                    <ChevronLeft className="w-6 h-6" />
                </button>

                {onSkip && step === 1 && (
                    <button
                        onClick={onSkip}
                        className="text-gray-400 text-xs font-bold hover:text-gray-600 transition-colors"
                    >
                        跳过并生成
                    </button>
                )}

                <button
                    onClick={nextStep}
                    disabled={step === totalSteps || (step < 4 && !data[`q${step}` as keyof FeedbackData])}
                    className={`p-4 rounded-2xl transition-all ${step === totalSteps || (step < 4 && !data[`q${step}` as keyof FeedbackData])
                        ? 'text-gray-200'
                        : 'text-primary hover:bg-blue-50 active:scale-90'
                        }`}
                >
                    <ChevronRight className="w-6 h-6" />
                </button>
            </div>
        </div>
    );
};

export default FeedbackSurvey;
