import React, { useState, useRef, useEffect } from 'react';
import { Camera, MessageSquare, Send, Bot, User, Sparkles, Mic, Video } from 'lucide-react';
import { ChildProfile, ChatMessage, FloorGame } from '../types';
import AIVideoCall from './AIVideoCall';
import { sendQwenMessage } from '../services/qwenService';

interface AIAssistantPanelProps {
    childProfile: ChildProfile | null;
    gameData?: FloorGame | null;
    gameContext: string;
    initialMode?: 'video' | 'chat';
}

export const AIAssistantPanel: React.FC<AIAssistantPanelProps> = ({
    childProfile,
    gameData,
    gameContext,
    initialMode = 'video'
}) => {
    const [activeTab, setActiveTab] = useState<'video' | 'chat'>(initialMode);
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

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

    return (
        <div className="h-full flex flex-col bg-white rounded-t-3xl shadow-[0_-4px_20px_-5px_rgba(0,0,0,0.1)] border-t border-gray-100 overflow-hidden">
            {/* Tabs - More compact margins */}
            <div className="flex bg-gray-50/50 p-1 m-3 mb-1.5 rounded-xl ring-1 ring-gray-100 shrink-0">
                <button
                    onClick={() => setActiveTab('video')}
                    className={`flex-1 flex items-center justify-center py-2 rounded-lg text-sm font-bold transition-all duration-300 ${activeTab === 'video'
                        ? 'bg-white text-primary shadow-sm ring-1 ring-gray-100'
                        : 'text-gray-400 hover:text-gray-600'
                        }`}
                >
                    <Camera className={`w-3.5 h-3.5 mr-1.5 ${activeTab === 'video' ? 'text-primary' : ''}`} />
                    视频分析
                </button>
                <button
                    onClick={() => setActiveTab('chat')}
                    className={`flex-1 flex items-center justify-center py-2 rounded-lg text-sm font-bold transition-all duration-300 ${activeTab === 'chat'
                        ? 'bg-white text-primary shadow-sm ring-1 ring-gray-100'
                        : 'text-gray-400 hover:text-gray-600'
                        }`}
                >
                    <MessageSquare className={`w-3.5 h-3.5 mr-1.5 ${activeTab === 'chat' ? 'text-primary' : ''}`} />
                    助手对话
                </button>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden relative">
                {activeTab === 'video' ? (
                    <div className="h-full">
                        <AIVideoCall
                            childProfile={childProfile}
                            gameData={gameData}
                            gameId={gameData?.id}
                            onClose={() => { }} // Optional: might not need a close button here
                            isInline={true}
                        />
                    </div>
                ) : (
                    <div className="h-full flex flex-col">
                        {/* Messages */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar min-h-0">
                            {messages.length === 0 && (
                                <div className="flex flex-col items-center justify-center h-full text-center space-y-3 opacity-40">
                                    <Bot className="w-10 h-10 text-primary" />
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">
                                        我是你的助手，随时为你提供游戏建议
                                    </p>
                                </div>
                            )}
                            {messages.map((msg) => (
                                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm ${msg.role === 'user'
                                        ? 'bg-primary text-white font-medium rounded-tr-none'
                                        : 'bg-gray-100 text-gray-800 rounded-tl-none border border-gray-200'
                                        }`}>
                                        {msg.text}
                                    </div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Quick Actions */}
                        {messages.length === 0 && (
                            <div className="px-4 pb-2 flex space-x-2 overflow-x-auto no-scrollbar shrink-0">
                                {['孩子不理我怎么办？', '如何加大难度？', '再讲一遍玩法'].map(hint => (
                                    <button
                                        key={hint}
                                        onClick={() => setInput(hint)}
                                        className="whitespace-nowrap bg-blue-50 text-blue-600 text-[10px] font-bold px-3 py-1.5 rounded-full border border-blue-100 hover:bg-blue-100 transition"
                                    >
                                        {hint}
                                    </button>
                                ))}
                            </div>
                        )}

                        {/* Input area - More compact */}
                        <div className="p-3 pt-1 border-t border-gray-100 bg-white shrink-0">
                            <div className="flex items-center space-x-2 bg-gray-50 rounded-xl p-1 ring-1 ring-gray-100">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder="询问即时建议..."
                                    className="flex-1 bg-transparent border-none focus:ring-0 text-sm px-3 py-1"
                                />
                                <button
                                    onClick={handleSend}
                                    disabled={loading || !input.trim()}
                                    className={`p-1.5 rounded-lg transition ${loading || !input.trim() ? 'bg-gray-200 text-gray-400' : 'bg-primary text-white shadow-md active:scale-95'
                                        }`}
                                >
                                    <Send className="w-3.5 h-3.5" />
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
