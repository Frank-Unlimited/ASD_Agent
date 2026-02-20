import React, { useState, useRef, useEffect } from 'react';
import { Camera, MessageSquare, Send, Bot, User, Sparkles, Mic, Video, ChevronUp, ChevronDown, GripHorizontal } from 'lucide-react';
import { motion, AnimatePresence, useDragControls } from 'framer-motion';
import { ChildProfile, ChatMessage, FloorGame } from '../types';
import AIVideoCall from './AIVideoCall';
import { sendQwenMessage } from '../services/qwenService';
import { chatStorageService } from '../services/chatStorage';

interface AIAssistantPanelProps {
    childProfile: ChildProfile | null;
    gameData?: FloorGame | null;
    gameContext: string;
    onVideoToggle?: (active: boolean) => void;
    isVideoActive?: boolean;
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
    childProfile,
    gameData,
    gameContext,
    onVideoToggle,
    isVideoActive = false
}) => {
    const [drawerState, setDrawerState] = useState<'min' | 'mid' | 'max'>('min');
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initialize with a game-specific greeting
        const greeting: ChatMessage = {
            id: 'init-' + Date.now(),
            role: 'model',
            text: `**你好！我是你的互动助手。** 👋 \n\n我已经准备好协助你进行“${gameData?.gameTitle || '当前互动'}”。有什么我可以帮你的吗？`,
            timestamp: new Date()
        };
        setMessages([greeting]);
    }, [gameData?.id]);

    useEffect(() => {
        if (drawerState !== 'min') {
            messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, drawerState]);

    const handleSend = async () => {
        if (!input.trim() || loading) return;

        const userMsg: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            text: input,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        const tempMsgId = (Date.now() + 1).toString();
        const tempMsg: ChatMessage = {
            id: tempMsgId,
            role: 'model',
            text: '',
            timestamp: new Date()
        };
        setMessages(prev => [...prev, tempMsg]);

        try {
            let fullResponse = '';
            await sendQwenMessage(input, messages, `当前游戏上下文：\n${gameContext}\n孩子档案：${JSON.stringify(childProfile)}`, {
                onContent: (chunk) => {
                    fullResponse += chunk;
                    setMessages(prev =>
                        prev.map(msg =>
                            msg.id === tempMsgId ? { ...msg, text: fullResponse } : msg
                        )
                    );
                }
            });
        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev =>
                prev.map(msg =>
                    msg.id === tempMsgId ? { ...msg, text: '抱歉，我现在遇到点问题，请稍后再试。' } : msg
                )
            );
        } finally {
            setLoading(false);
        }
    };

    const drawerVariants = {
        min: { height: '84px' },
        mid: { height: '50vh' },
        max: { height: '90vh' }
    };

    return (
        <motion.div
            initial="min"
            animate={drawerState}
            variants={drawerVariants}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="fixed bottom-0 left-0 right-0 bg-white rounded-t-[32px] shadow-[0_-8px_30px_rgba(0,0,0,0.12)] border-t border-gray-100 flex flex-col z-[50] overflow-hidden"
            drag="y"
            dragConstraints={{ top: 0, bottom: 0 }}
            dragElastic={0.1}
            onDragEnd={(e, info) => {
                const threshold = 50;
                if (info.offset.y < -threshold) {
                    if (drawerState === 'min') setDrawerState('mid');
                    else if (drawerState === 'mid') setDrawerState('max');
                } else if (info.offset.y > threshold) {
                    if (drawerState === 'max') setDrawerState('mid');
                    else if (drawerState === 'mid') setDrawerState('min');
                }
            }}
        >
            {/* Drag Handle */}
            <div className="w-full flex justify-center py-2 cursor-grab active:cursor-grabbing shrink-0">
                <div className="w-12 h-1.5 bg-gray-200 rounded-full" />
            </div>

            {/* Chat Body (History) */}
            <div className="flex-1 overflow-hidden flex flex-col">
                <AnimatePresence>
                    {drawerState !== 'min' && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            exit={{ opacity: 0 }}
                            className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar min-h-0"
                        >
                            {messages.length === 0 ? (
                                <div className="flex flex-col items-center justify-center h-full text-center space-y-3 opacity-40 py-10">
                                    <Bot className="w-10 h-10 text-primary" />
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest px-10">
                                        我是你的助手，随时为你提供互动建议。尝试发送消息或开启视频墙。
                                    </p>
                                </div>
                            ) : (
                                messages.map((msg) => (
                                    <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === 'user'
                                            ? 'bg-primary text-white font-medium rounded-tr-none'
                                            : 'bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200'
                                            }`}>
                                            {msg.text}
                                        </div>
                                    </div>
                                ))
                            )}
                            <div ref={messagesEndRef} />
                        </motion.div>
                    )}
                </AnimatePresence>

                {/* Input Bar (Always Visible) */}
                <div className="p-4 pt-1 bg-white shrink-0">
                    {/* Quick Hints (Only in mid/max) */}
                    <AnimatePresence>
                        {drawerState !== 'min' && messages.length === 0 && (
                            <motion.div
                                initial={{ height: 0, opacity: 0 }}
                                animate={{ height: 'auto', opacity: 1 }}
                                exit={{ height: 0, opacity: 0 }}
                                className="pb-3 flex space-x-2 overflow-x-auto no-scrollbar shrink-0"
                            >
                                {['孩子不理我怎么办？', '如何加大难度？', '再讲一遍玩法'].map(hint => (
                                    <button
                                        key={hint}
                                        onClick={() => setInput(hint)}
                                        className="whitespace-nowrap bg-blue-50 text-blue-600 text-[10px] font-bold px-3 py-1.5 rounded-full border border-blue-100 hover:bg-blue-100 transition whitespace-nowrap"
                                    >
                                        {hint}
                                    </button>
                                ))}
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <div className="flex items-center space-x-2">
                        {/* Video Call Toggle Button */}
                        <button
                            onClick={() => onVideoToggle?.(!isVideoActive)}
                            className={`p-3 rounded-2xl transition shadow-sm border ${isVideoActive
                                ? 'bg-indigo-600 text-white border-indigo-500 shadow-indigo-200'
                                : 'bg-gray-50 text-gray-400 border-gray-100 hover:bg-white hover:text-indigo-600'
                                }`}
                        >
                            <Video className={`w-5 h-5 ${isVideoActive ? 'animate-pulse' : ''}`} />
                        </button>

                        {/* Text Input Container */}
                        <div className="flex-1 flex items-center bg-gray-50 rounded-2xl p-1.5 ring-1 ring-gray-100 focus-within:ring-primary/20 focus-within:bg-white transition shadow-inner">
                            <input
                                type="text"
                                value={input}
                                onFocus={() => drawerState === 'min' && setDrawerState('mid')}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                placeholder="询问即时建议..."
                                className="flex-1 bg-transparent border-none focus:ring-0 text-sm px-3 py-2"
                            />
                            <button
                                onClick={handleSend}
                                disabled={loading || !input.trim()}
                                className={`p-2 rounded-xl transition ${loading || !input.trim()
                                    ? 'bg-gray-200 text-gray-400'
                                    : 'bg-primary text-white shadow-md active:scale-95'
                                    }`}
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </motion.div>
    );
};
