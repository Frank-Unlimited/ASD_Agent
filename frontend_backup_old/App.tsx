import React, { useState, useEffect, useRef } from 'react';
import {
  MessageCircle,
  Calendar as CalendarIcon,
  User,
  Gamepad2,
  Menu,
  ChevronLeft,
  ChevronRight,
  Mic,
  Camera,
  CheckCircle2,
  Play,
  Upload,
  TrendingUp,
  Activity,
  Award,
  ArrowRight,
  Smile,
  Eye,
  Handshake,
  Frown,
  Search,
  FileText,
  X,
  Flame,
  Lightbulb,
  Sparkles,
  Paperclip,
  ArrowUpRight
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from 'recharts';
import { Page, GameState, ChildProfile, Game, CalendarEvent, ChatMessage, LogEntry, InterestCategory } from './types';
import { api } from './services/api';

// --- Components ---

const Sidebar = ({ isOpen, onClose, setPage, profile }: { isOpen: boolean, onClose: () => void, setPage: (p: Page) => void, profile: ChildProfile | null }) => {
  return (
    <div className={`fixed inset-0 z-50 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out`}>
      <div className="absolute inset-0 bg-black/50" onClick={onClose}></div>
      <div className="absolute left-0 top-0 h-full w-64 bg-white shadow-xl flex flex-col p-6">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-xl font-bold text-gray-800">菜单</h2>
          <button onClick={onClose}><X className="w-6 h-6 text-gray-500" /></button>
        </div>

        <nav className="space-y-4">
          <button onClick={() => { setPage(Page.CHAT); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium">
            <MessageCircle className="w-5 h-5 text-primary" />
            <span>AI 对话助手</span>
          </button>
          <button onClick={() => { setPage(Page.CALENDAR); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium">
            <CalendarIcon className="w-5 h-5 text-primary" />
            <span>成长日历</span>
          </button>
          <button onClick={() => { setPage(Page.PROFILE); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium">
            <User className="w-5 h-5 text-primary" />
            <span>孩子档案</span>
          </button>
          <button onClick={() => { setPage(Page.GAMES); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium">
            <Gamepad2 className="w-5 h-5 text-primary" />
            <span>地板游戏库</span>
          </button>
        </nav>

        <div className="mt-auto pt-6 border-t border-gray-100">
          <div className="flex items-center space-x-3">
            {profile && <img src={profile.avatar} alt="Profile" className="w-10 h-10 rounded-full" />}
            <div>
              <p className="font-semibold text-sm">{profile?.name || "加载中..."}</p>
              <p className="text-xs text-gray-500">{profile?.diagnosis}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper interfaces for parsed cards
interface GameRecommendation {
  type: 'GAME';
  id: string;
  title: string;
  reason: string;
  fullGame?: Game; // Added to support playing ad-hoc recommended games
}

interface NavCard {
  type: 'NAV';
  page: 'PROFILE' | 'CALENDAR';
  title: string;
  reason: string;
}

type ParsedCard = GameRecommendation | NavCard;

const PageAIChat = ({ navigateTo, onStartGame, profile }: { navigateTo: (p: Page) => void, onStartGame: (id: string, fullGame?: Game) => void, profile: ChildProfile | null }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          id: '1',
          role: 'model',
          text: `你好！我是你的地板时光助手。${profile?.name ? profile.name : "待解析"}今天状态怎么样？有什么进步或者困难想和我聊聊吗？\n\n目前多模态解析支持**图片格式**的评估报告。如果您有诊断建议或观察记录，可以直接上传照片，我会为您深度分析。`,
          timestamp: new Date()
        }
      ]);
    }
  }, [profile]);

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    const modelMsgId = (Date.now() + 1).toString();
    let accumulatedText = '';

    // Add empty model message placeholder
    setMessages(prev => [...prev, { id: modelMsgId, role: 'model', text: '', timestamp: new Date() }]);

    try {
      const childId = localStorage.getItem('active_child_id') || "test_child_001";

      await api.sendMessageStream(
        userMsg.text,
        childId,
        messages,
        // onContent - streaming text
        (text: string) => {
          accumulatedText += text;
          setMessages(prev => prev.map(msg =>
            msg.id === modelMsgId ? { ...msg, text: accumulatedText } : msg
          ));
        },
        // onToolCall
        (toolName: string, displayName: string) => {
          console.log(`Tool called: ${displayName}`);
        },
        // onToolResult
        (result: any) => {
          // Handle tool results - append markers for games/navigation
          if (result.tool_name === 'recommend_game' && result.result?.success && result.result?.game) {
            const game = result.result.game;
            const markerData = {
              id: game.game_id,
              title: game.name,
              reason: game.design_rationale || game.description
            };
            accumulatedText += `\n\n:::GAME_RECOMMENDATION:${JSON.stringify(markerData)}:::`;
            setMessages(prev => prev.map(msg =>
              msg.id === modelMsgId ? { ...msg, text: accumulatedText } : msg
            ));
          }

          if (result.tool_name === 'generate_assessment' && result.result?.success) {
            const markerData = {
              page: 'PROFILE',
              title: '查看最新评估报告',
              reason: '新的评估报告已生成，点击查看详细分析。'
            };
            accumulatedText += `\n\n:::NAVIGATION_CARD:${JSON.stringify(markerData)}:::`;
            setMessages(prev => prev.map(msg =>
              msg.id === modelMsgId ? { ...msg, text: accumulatedText } : msg
            ));
          }
        },
        // onDone
        () => {
          setLoading(false);
        },
        // onError
        (error: string) => {
          console.error('Stream error:', error);
          setMessages(prev => prev.map(msg =>
            msg.id === modelMsgId ? { ...msg, text: accumulatedText || "连接服务器失败，请检查网络或后端状态。" } : msg
          ));
          setLoading(false);
        }
      );
    } catch (e) {
      console.error(e);
      setMessages(prev => prev.map(msg =>
        msg.id === modelMsgId ? { ...msg, text: "连接服务器失败，请检查网络或后端状态。" } : msg
      ));
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Add immediate feedback
    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: `📎 已上传文件: ${file.name}`, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      if (file.type.startsWith('image/')) {
        const result = await api.importProfileFromImage(file);
        const modelMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'model',
          text: `档案导入成功！已为 ${result.profile_summary ? "孩子" : "新用户"} 创建档案。正在重新加载数据...`,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, modelMsg]);

        // Finalize onboarding for this child
        localStorage.setItem('active_child_id', result.child_id);
        setTimeout(() => window.location.reload(), 2000);
      } else {
        // PDF or other - manual archive (simplified)
        const modelMsg: ChatMessage = {
          id: (Date.now() + 1).toString(),
          role: 'model',
          text: "目前多模态解析仅支持图片格式的报告。如果是 PDF 或其他格式，我已将其标记为手动记录。",
          timestamp: new Date()
        };
        setMessages(prev => [...prev, modelMsg]);
      }
    } catch (err) {
      console.error(err);
      const modelMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'model',
        text: "上传解析失败，请检查网络连接或报告格式。",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, modelMsg]);
    } finally {
      setLoading(false);
    }
  };

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      // Mock result of speech-to-text
      setInput(prev => prev + "（语音输入内容：孩子今天玩得很开心）");
    } else {
      setIsRecording(true);
    }
  };

  // Parsing function for both Game and Navigation cards
  const parseMessageContent = (text: string): { cleanText: string, card: ParsedCard | null } => {
    const gameRegex = /:::GAME_RECOMMENDATION:(.*?):::/;
    const navRegex = /:::NAVIGATION_CARD:(.*?):::/;

    let match = text.match(gameRegex);
    if (match && match[1]) {
      try {
        const data = JSON.parse(match[1]);
        return {
          cleanText: text.replace(gameRegex, '').trim(),
          card: { ...data, type: 'GAME' }
        };
      } catch (e) { }
    }

    match = text.match(navRegex);
    if (match && match[1]) {
      try {
        const data = JSON.parse(match[1]);
        return {
          cleanText: text.replace(navRegex, '').trim(),
          card: { ...data, type: 'NAV' }
        };
      } catch (e) { }
    }

    return { cleanText: text, card: null };
  };

  return (
    <div className="flex flex-col h-full bg-background relative">
      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 pb-32">
        {messages.map(msg => {
          const { cleanText, card } = parseMessageContent(msg.text);

          return (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[85%] p-4 rounded-2xl shadow-sm leading-relaxed ${msg.role === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none'}`}>
                {msg.role === 'user' ? (
                  cleanText
                ) : (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={{
                        p: ({ node, ...props }) => <p className="mb-2 last:mb-0" {...props} />,
                        ul: ({ node, ...props }) => <ul className="list-disc ml-4 mb-2" {...props} />,
                        ol: ({ node, ...props }) => <ol className="list-decimal ml-4 mb-2" {...props} />,
                        li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                        table: ({ node, ...props }) => (
                          <div className="overflow-x-auto my-2">
                            <table className="min-w-full border-collapse border border-gray-200" {...props} />
                          </div>
                        ),
                        th: ({ node, ...props }) => <th className="border border-gray-200 px-2 py-1 bg-gray-50 text-left font-bold" {...props} />,
                        td: ({ node, ...props }) => <td className="border border-gray-200 px-2 py-1" {...props} />,
                        code: ({ node, inline, ...props }: any) => (
                          inline
                            ? <code className="bg-gray-100 rounded px-1 py-0.5" {...props} />
                            : <code className="block bg-gray-100 rounded p-2 my-2 overflow-x-auto" {...props} />
                        )
                      }}
                    >
                      {cleanText}
                    </ReactMarkdown>
                  </div>
                )}
              </div>

              {/* Render Cards */}
              {card && card.type === 'GAME' && (
                <div className="mt-2 max-w-[85%] bg-white p-3 rounded-xl border-l-4 border-secondary shadow-md animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <Sparkles className="w-4 h-4 text-secondary fill-secondary/20" />
                      <span className="text-xs font-bold text-secondary uppercase tracking-wider">推荐游戏</span>
                    </div>
                  </div>
                  <h4 className="font-bold text-gray-800 text-lg mb-1">{card.title}</h4>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{card.reason}</p>
                  <button
                    onClick={() => onStartGame(card.id, (card as GameRecommendation).fullGame)}
                    className="w-full bg-secondary text-white py-2 rounded-lg text-sm font-bold flex items-center justify-center hover:bg-blue-600 transition"
                  >
                    <Play className="w-4 h-4 mr-2 fill-current" /> 开始游戏
                  </button>
                </div>
              )}

              {card && card.type === 'NAV' && (
                <div className="mt-2 max-w-[85%] bg-white p-3 rounded-xl border-l-4 border-primary shadow-md animate-in fade-in slide-in-from-bottom-4 duration-500">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <ArrowUpRight className="w-4 h-4 text-primary" />
                      <span className="text-xs font-bold text-primary uppercase tracking-wider">建议操作</span>
                    </div>
                  </div>
                  <h4 className="font-bold text-gray-800 text-lg mb-1">{card.title}</h4>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{card.reason}</p>
                  <button
                    onClick={() => navigateTo(card.page === 'CALENDAR' ? Page.CALENDAR : Page.PROFILE)}
                    className="w-full bg-primary/10 text-primary py-2 rounded-lg text-sm font-bold flex items-center justify-center hover:bg-primary/20 transition"
                  >
                    前往查看
                  </button>
                </div>
              )}
            </div>
          );
        })}
        {loading && <div className="text-gray-400 text-sm ml-4">思考中...</div>}
        <div ref={messagesEndRef} />
      </div>

      {/* Floating Action Buttons */}
      <div className="absolute bottom-24 left-0 right-0 px-4 flex justify-center space-x-3">
        <button onClick={() => navigateTo(Page.PROFILE)} className="bg-white/95 backdrop-blur shadow-lg px-5 py-2.5 rounded-full text-sm font-semibold text-primary border border-green-100 flex items-center transform active:scale-95 transition">
          <FileText className="w-4 h-4 mr-2" /> 孩童评估
        </button>
        <button onClick={() => navigateTo(Page.GAMES)} className="bg-white/95 backdrop-blur shadow-lg px-5 py-2.5 rounded-full text-sm font-semibold text-secondary border border-blue-100 flex items-center transform active:scale-95 transition">
          <Gamepad2 className="w-4 h-4 mr-2" /> 地板游戏
        </button>
      </div>

      {/* Input Area */}
      <div className="bg-white p-4 border-t border-gray-100">
        <div className="flex items-center bg-gray-100 rounded-full px-2 py-2">

          {/* File Upload Button */}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            className="hidden"
            accept=".pdf,.doc,.docx,.txt,image/*"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="p-2 text-gray-500 hover:text-primary transition active:scale-90"
          >
            <Paperclip className="w-5 h-5" />
          </button>

          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && handleSend()}
            placeholder={isRecording ? "正在听..." : "输入消息..."}
            className="flex-1 bg-transparent outline-none text-gray-700 placeholder-gray-400 ml-2"
          />

          {/* Voice Input Button */}
          <button
            onClick={toggleRecording}
            className={`p-2 mr-1 transition rounded-full ${isRecording ? 'text-red-500 bg-red-100 animate-pulse' : 'text-gray-500 hover:text-primary'}`}
          >
            <Mic className="w-5 h-5" />
          </button>

          <button onClick={handleSend} className="p-2 bg-primary rounded-full text-white ml-1 hover:bg-green-600 transition shadow-md">
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

const PageCalendar = ({ navigateTo, onStartGame, calendarData }: { navigateTo: (p: Page) => void, onStartGame: (gameId: string, fullGame?: Game) => void, calendarData: CalendarEvent[] }) => {
  return (
    <div className="p-4 space-y-6 h-full overflow-y-auto bg-background">
      {/* Weekly Goal */}
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-5 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10">
          <h3 className="text-green-100 text-sm font-medium uppercase tracking-wide mb-1">本周目标</h3>
          <p className="text-xl font-bold mb-3">提升“持续眼神接触”的频率</p>
          <div className="h-2 bg-green-800/30 rounded-full w-full overflow-hidden">
            <div className="h-full bg-white/90 w-[60%] rounded-full"></div>
          </div>
          <p className="text-xs mt-2 text-green-100">已完成 3/5 个互动单元</p>
        </div>
        <Award className="absolute -right-4 -bottom-4 w-32 h-32 text-white/10" />
      </div>

      {/* Calendar Grid */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-gray-800 text-lg">2025年 1月</h3>
          <button className="text-sm text-primary font-bold bg-green-50 px-3 py-1 rounded-full">生成下周计划</button>
        </div>
        <div className="grid grid-cols-7 gap-2">
          {['一', '二', '三', '四', '五', '六', '日'].map((d, i) => (
            <div key={i} className="text-center text-xs text-gray-400 font-medium mb-2">{d}</div>
          ))}
          {calendarData.map((day) => {
            // 状态颜色逻辑：已完成(深色) -> 今日(蓝色/高亮) -> 未来(灰色)
            let bgClass = 'bg-white border-gray-200';
            let textClass = 'text-gray-600';

            if (day.status === 'completed') {
              bgClass = 'bg-emerald-100 border-emerald-200';
              textClass = 'text-emerald-700';
            }
            if (day.status === 'today') {
              bgClass = 'bg-blue-50 border-blue-200 ring-2 ring-blue-400 ring-offset-1';
              textClass = 'text-blue-700';
            }

            return (
              <div key={day.day}
                onClick={() => {
                  if (day.status === 'today' && day.gameId) {
                    onStartGame(day.gameId);
                  }
                }}
                className={`aspect-square rounded-xl border flex flex-col items-center justify-center p-1 cursor-pointer transition active:scale-95 ${bgClass}`}>
                <span className={`text-xs font-bold mb-1 ${textClass}`}>{day.day}</span>
                {day.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
                {day.status === 'today' && <CalendarIcon className="w-4 h-4 text-blue-500" />}
              </div>
            )
          })}
        </div>
      </div>

      {/* Day Detail Card (Today) */}
      {calendarData.find(d => d.status === 'today') && (
        <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
          <div className="flex justify-between items-start mb-4">
            <div>
              <span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded font-medium">今日, {calendarData.find(d => d.status === 'today')?.time || "10:00"}</span>
              <h3 className="text-lg font-bold text-gray-800 mt-2">{calendarData.find(d => d.status === 'today')?.gameTitle}</h3>
              <p className="text-sm text-gray-500">目标: {calendarData.find(d => d.status === 'today')?.gameId === 'game-002' ? '感官调节' : '发展目标'}</p>
            </div>
            <button
              onClick={() => {
                const todayGame = calendarData.find(d => d.status === 'today');
                if (todayGame?.gameId) onStartGame(todayGame.gameId);
              }}
              className="w-12 h-12 bg-primary rounded-full flex items-center justify-center shadow-lg text-white hover:bg-green-600 transition animate-pulse">
              <Play className="w-6 h-6 ml-1" />
            </button>
          </div>
        </div>
      )}

      {/* Past Detail Card */}
      <div className="bg-gray-50 rounded-2xl p-4 border border-dashed border-gray-300">
        <div className="flex items-center space-x-3 opacity-80">
          <div className="w-10 h-10 rounded-full bg-emerald-100 flex items-center justify-center flex-shrink-0">
            <CheckCircle2 className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <h4 className="font-semibold text-gray-800 text-sm">积木高塔轮流堆 (昨日)</h4>
            <p className="text-xs text-emerald-700 font-medium bg-emerald-50 px-2 py-0.5 rounded inline-block mt-1">进步: 眼神接触 +3次</p>
          </div>
        </div>
      </div>
    </div>
  );
};

const PageProfile = ({ profile, radarData, trendData, interests }: { profile: ChildProfile | null, radarData: any[], trendData: any[], interests: InterestCategory[] }) => {
  if (!profile) return <div className="p-10 text-center text-gray-500">加载档案中...</div>;

  return (
    <div className="p-4 space-y-6 h-full overflow-y-auto bg-background">
      <div className="flex items-center space-x-4 bg-white p-5 rounded-2xl shadow-sm">
        <img src={profile.avatar} className="w-16 h-16 rounded-full border-2 border-white shadow" alt={profile.name} />
        <div>
          <h2 className="text-2xl font-bold text-gray-800">{profile.name}, {profile.age}岁</h2>
          <p className="text-gray-500 font-medium">{profile.diagnosis}</p>
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm">
        <h3 className="font-bold text-gray-700 mb-4 flex items-center"><Activity className="w-4 h-4 mr-2 text-primary" /> DIR 六大能力维度</h3>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
              <PolarGrid stroke="#e5e7eb" />
              <PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 11, fontWeight: 500 }} />
              <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
              <Radar name={profile.name} dataKey="A" stroke="#10B981" fill="#10B981" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Interest Heatmap Matrix */}
      <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-bold text-gray-700 flex items-center">
            <Flame className="w-4 h-4 mr-2 text-accent" /> 兴趣热力图
          </h3>
          <span className="text-[10px] text-gray-400 bg-gray-50 px-2 py-1 rounded-full">强度 1-5</span>
        </div>

        <div className="space-y-5">
          {interests.map((section, idx) => (
            <div key={idx}>
              <div className="flex items-center mb-2">
                <div className="w-2 h-2 rounded-full bg-gray-300 mr-2"></div>
                <h4 className="text-xs font-bold text-gray-500">{section.category}</h4>
              </div>
              <div className="grid grid-cols-3 gap-2">
                {section.items.map((item, i) => {
                  // Color scale logic
                  let colorClass = 'bg-gray-50 text-gray-400';
                  if (item.level >= 5) colorClass = 'bg-orange-500 text-white shadow-md shadow-orange-200';
                  else if (item.level >= 4) colorClass = 'bg-orange-400 text-white';
                  else if (item.level >= 3) colorClass = 'bg-orange-300 text-white';
                  else if (item.level >= 2) colorClass = 'bg-orange-100 text-orange-800';

                  return (
                    <div key={i} className={`${colorClass} rounded-xl p-2 flex flex-col items-center justify-center text-center h-20 transition hover:scale-105`}>
                      <span className="text-xs font-bold mb-1 leading-tight">{item.name}</span>
                      <div className="flex space-x-0.5">
                        {[...Array(item.level)].map((_, starI) => (
                          <div key={starI} className={`w-1 h-1 rounded-full ${item.level >= 3 ? 'bg-white/70' : 'bg-orange-500/40'}`}></div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow-sm">
        <h3 className="font-bold text-gray-700 mb-4 flex items-center"><TrendingUp className="w-4 h-4 mr-2 text-secondary" /> 互动参与度趋势</h3>
        <div className="h-48 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" />
              <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#9ca3af' }} axisLine={false} tickLine={false} />
              <YAxis hide />
              <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} />
              <Line type="monotone" dataKey="engagement" stroke="#3B82F6" strokeWidth={3} dot={{ r: 4, fill: '#3B82F6', strokeWidth: 2, stroke: '#fff' }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <button className="w-full py-4 rounded-xl border border-gray-200 text-gray-600 font-semibold bg-white hover:bg-gray-50 flex justify-center items-center shadow-sm">
        <Upload className="w-5 h-5 mr-2" /> 导出报告给医生
      </button>
    </div>
  );
};

const PageGames = ({ initialGameId, gameState, setGameState, onBack, games }: { initialGameId?: string, gameState: GameState, setGameState: (s: GameState) => void, onBack: () => void, games: Game[] }) => {
  const [activeGame, setActiveGame] = useState<Game | undefined>(initialGameId ? games.find(g => g.id === initialGameId) : undefined);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [timer, setTimer] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [summary, setSummary] = useState<any>(null);
  const [isFinishing, setIsFinishing] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Search & Filter State
  const [searchText, setSearchText] = useState('');
  const [activeFilter, setActiveFilter] = useState('全部');
  const FILTERS = ['全部', '共同注意', '自我调节', '亲密感', '双向沟通', '情绪思考', '创造力'];

  // Sync initialGameId with component state if provided
  useEffect(() => {
    if (initialGameId) {
      const game = games.find(g => g.id === initialGameId);
      if (game) {
        setActiveGame(game);
        // If we are moving into playing state, reset counters
        if (gameState === GameState.PLAYING && (!activeGame || activeGame.id !== game.id)) {
          setCurrentStepIndex(0);
          setTimer(0);
          setLogs([]);
        }
      }
    }
  }, [initialGameId, games, gameState]);

  useEffect(() => {
    if (gameState === GameState.PLAYING) {
      timerRef.current = setInterval(() => setTimer(t => t + 1), 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [gameState]);

  const handleStartGame = async (game: Game) => {
    setActiveGame(game);
    setGameState(GameState.PLAYING);
    setCurrentStepIndex(0);
    setTimer(0);
    setLogs([]);
    setSummary(null);

    // Start backend session
    try {
      const childId = localStorage.getItem('active_child_id') || "test_child_001";
      const res = await api.startSession(childId, game.id);
      setSessionId(res.session_id);
    } catch (e) {
      console.error("Failed to start session:", e);
    }
  };

  const handleLog = async (type: 'emoji' | 'voice', content: string) => {
    setLogs(prev => [...prev, { type, content, timestamp: new Date() }]);

    // Log to backend if session exists
    if (sessionId) {
      try {
        await api.addObservation(sessionId, content);
      } catch (e) {
        console.error("Failed to log observation:", e);
      }
    }
  };

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  if (gameState === GameState.LIST) {
    const filteredGames = games.filter(game => {
      const matchesSearch = game.title.toLowerCase().includes(searchText.toLowerCase()) ||
        game.reason.toLowerCase().includes(searchText.toLowerCase()) ||
        game.target.toLowerCase().includes(searchText.toLowerCase());
      const matchesFilter = activeFilter === '全部' || game.target.includes(activeFilter);
      return matchesSearch && matchesFilter;
    });

    return (
      <div className="h-full bg-background p-4 overflow-y-auto">
        <div className="sticky top-0 bg-background z-10 pb-2 -mx-4 px-4 pt-2">
          <div className="relative mb-3">
            <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
            <input
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              className="w-full bg-white pl-10 pr-4 py-3 rounded-xl shadow-sm outline-none border border-transparent focus:border-primary/30 transition"
              placeholder="搜索游戏（如：积木）"
            />
          </div>

          {/* Filters */}
          <div className="flex space-x-2 overflow-x-auto pb-2 no-scrollbar">
            {FILTERS.map(f => (
              <button
                key={f}
                onClick={() => setActiveFilter(f)}
                className={`whitespace-nowrap px-4 py-1.5 rounded-full text-xs font-bold transition border ${activeFilter === f
                  ? 'bg-primary text-white border-primary shadow-sm'
                  : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'
                  }`}
              >
                {f}
              </button>
            ))}
          </div>
        </div>

        <h3 className="font-bold text-gray-700 mb-3 flex items-center justify-between mt-2">
          <span>推荐游戏库</span>
          <span className="text-xs font-normal text-gray-400 bg-gray-100 px-2 py-1 rounded-full">{filteredGames.length} 个结果</span>
        </h3>

        <div className="space-y-4 pb-20">
          {filteredGames.length > 0 ? (
            filteredGames.map(game => (
              <div key={game.id} onClick={() => handleStartGame(game)} className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 active:scale-98 transition transform cursor-pointer group hover:border-primary/30">
                <div className="flex justify-between items-start">
                  <h4 className="font-bold text-gray-800 text-lg group-hover:text-primary transition flex items-center">
                    {game.title}
                    {game.isVR && (
                      <span className="ml-2 bg-indigo-600 text-white text-[10px] px-2 py-0.5 rounded-md shadow-sm font-bold flex items-center animate-pulse">
                        <Sparkles className="w-3 h-3 mr-1 fill-current" /> VR体验
                      </span>
                    )}
                  </h4>
                  <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full font-medium shrink-0 ml-2">{game.duration}</span>
                </div>
                <p className="text-gray-500 text-sm mt-1 line-clamp-2">{game.reason}</p>
                <div className="mt-4 flex items-center text-xs font-bold text-blue-600 bg-blue-50 w-fit px-3 py-1.5 rounded-lg">
                  目标: {game.target}
                </div>
              </div>
            ))
          ) : (
            <div className="text-center py-10 text-gray-400 flex flex-col items-center">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                <Search className="w-8 h-8 text-gray-300" />
              </div>
              <p>没有找到匹配的游戏</p>
              <button onClick={() => { setSearchText(''); setActiveFilter('全部') }} className="mt-2 text-primary font-bold text-sm">清除筛选</button>
            </div>
          )}
        </div>
      </div>
    );
  }

  if (gameState === GameState.PLAYING && activeGame) {
    const currentStep = activeGame.steps[currentStepIndex];
    const isLastStep = currentStepIndex === activeGame.steps.length - 1;

    return (
      <div className="h-full flex flex-col bg-background">

        {/* Timer - Block Element to avoid crossing */}
        <div className="w-full flex flex-col items-center py-4 bg-background z-0">
          <h3 className="font-bold text-sm text-gray-500 mb-1">{activeGame.title}</h3>
          <div className="text-green-600 font-mono text-3xl font-bold">{formatTime(timer)}</div>
        </div>

        {/* Unified Step Card */}
        <div className="flex-1 px-4 pb-2 flex flex-col min-h-0">
          <div className="bg-white rounded-[2rem] shadow-sm border border-gray-100 flex-1 flex flex-col p-6 relative overflow-hidden">

            {/* Step Number Badge */}
            <div className="w-full flex justify-center mb-6 shrink-0">
              <div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xl shadow-sm">
                {currentStepIndex + 1}
              </div>
            </div>

            {/* Main Content Centered Vertically */}
            <div className="flex-1 flex flex-col justify-center overflow-y-auto no-scrollbar">
              <h2 className="text-2xl font-bold text-gray-800 leading-normal text-center mb-8">
                {currentStep.instruction}
              </h2>

              {/* Guidance Box - Vertically Centered below steps, left aligned text */}
              <div className="bg-blue-50/80 p-5 rounded-2xl border border-blue-100 text-left w-full">
                <h4 className="text-blue-800 font-bold mb-2 flex items-center text-sm">
                  <Lightbulb className="w-4 h-4 mr-2 text-yellow-500 fill-current" />
                  互动小贴士
                </h4>
                <p className="text-blue-900/80 text-sm leading-relaxed font-medium">
                  {currentStep.guidance}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Buttons - Updated with Centered Step Counter */}
        <div className="flex items-center justify-between px-6 py-4 mb-2">
          <button
            onClick={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))}
            disabled={currentStepIndex === 0}
            className={`flex items-center text-gray-400 font-bold transition px-4 py-3 ${currentStepIndex === 0 ? 'opacity-30 cursor-not-allowed' : 'hover:text-gray-600'}`}
          >
            <ChevronLeft className="w-5 h-5 mr-1" /> 上一步
          </button>

          {/* Step Counter moved here */}
          <div className="bg-white px-4 py-2 rounded-xl shadow-sm border border-gray-100 text-xs font-bold text-gray-500 tracking-wide">
            步骤 {currentStepIndex + 1} / {activeGame.steps.length}
          </div>

          {isLastStep ? (
            <button
              onClick={() => setGameState(GameState.SUMMARY)}
              className="bg-primary text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-primary/30 flex items-center hover:bg-green-600 transition transform active:scale-95"
            >
              完成 <CheckCircle2 className="w-5 h-5 ml-2" />
            </button>
          ) : (
            <button
              onClick={() => setCurrentStepIndex(currentStepIndex + 1)}
              className="bg-secondary text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-secondary/30 flex items-center hover:bg-blue-600 transition transform active:scale-95"
            >
              下一步 <ChevronRight className="w-5 h-5 ml-1" />
            </button>
          )}
        </div>

        {/* Quick Log Controls - Fixed at Bottom */}
        <div className="p-4 bg-white border-t border-gray-100 pb-8 rounded-t-3xl shadow-[0_-4px_20px_-5px_rgba(0,0,0,0.1)] z-20 relative">
          <p className="text-center text-[10px] text-gray-400 mb-3 uppercase tracking-widest font-bold">快速记录当前反应</p>
          <div className="flex justify-between max-w-sm mx-auto mb-3 space-x-2">
            {[
              { icon: Smile, label: '微笑', color: 'text-yellow-600 bg-yellow-100' },
              { icon: Eye, label: '眼神', color: 'text-blue-600 bg-blue-100' },
              { icon: Handshake, label: '互动', color: 'text-green-600 bg-green-100' },
              { icon: Frown, label: '抗拒', color: 'text-red-500 bg-red-100' }
            ].map((btn, i) => (
              <button key={i} onClick={() => handleLog('emoji', btn.label)} className={`flex-1 py-3 rounded-xl shadow-sm active:scale-95 transition flex flex-col items-center justify-center ${btn.color}`}>
                <btn.icon className="w-5 h-5 mb-1" />
                <span className="text-[10px] font-bold">{btn.label}</span>
              </button>
            ))}
          </div>
          <button
            onClick={async () => {
              if (sessionId) {
                setIsFinishing(true);
                try {
                  await api.endSession(sessionId, {});
                  const summaryRes = await api.summarizeSession(sessionId);
                  setSummary(summaryRes.summary);
                } catch (e) {
                  console.error("Failed to finish session:", e);
                } finally {
                  setIsFinishing(false);
                }
              }
              setGameState(GameState.SUMMARY);
            }}
            disabled={isFinishing}
            className="flex-1 bg-primary text-white py-4 rounded-2xl font-bold shadow-lg hover:bg-green-600 transition active:scale-95 text-lg disabled:opacity-50"
          >
            {isFinishing ? "分析中..." : "完成游戏"}
          </button>
        </div>

        {/* Observation Log Bottom Sheet - Floating Bubble for easier access */}
        <div className="px-6 pb-6">
          <button
            onClick={() => handleLog('voice', '记录了一些观察...')}
            className="w-full bg-white border-2 border-dashed border-gray-200 py-3 rounded-xl flex items-center justify-center text-gray-400 font-medium hover:border-primary/30 hover:text-primary transition"
          >
            <Mic className="w-4 h-4 mr-2" /> 按住说话 记录观察笔记
          </button>
        </div>
      </div>
    );
  }

  if (gameState === GameState.SUMMARY) {
    return (
      <div className="h-full bg-background p-6 overflow-y-auto">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">做得好！🎉</h2>

        {/* Video Upload */}
        <div className="bg-white p-6 rounded-2xl shadow-sm text-center mb-6 border-dashed border-2 border-gray-200">
          <Camera className="w-10 h-10 text-gray-300 mx-auto mb-2" />
          <p className="text-gray-500 text-sm mb-4">上传互动视频以便 AI 分析 (可选)</p>
          <div className="flex space-x-2 justify-center">
            <button className="px-5 py-2 bg-gray-100 text-gray-600 rounded-lg text-sm font-medium hover:bg-gray-200">跳过</button>
            <button className="px-5 py-2 bg-primary text-white rounded-lg text-sm font-medium shadow-md hover:bg-green-600">上传视频</button>
          </div>
        </div>

        {/* AI Summary */}
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white p-5 rounded-2xl shadow-lg mb-6">
          <h3 className="font-bold flex items-center mb-2"><Activity className="w-4 h-4 mr-2" /> AI 互动总结</h3>
          <p className="text-indigo-100 text-sm leading-relaxed">
            {summary ? summary.overall_assessment : "基于你的快速记录，系统正在同步分析中..."}
          </p>
          {summary && summary.highlights && summary.highlights.length > 0 && (
            <div className="mt-3 pt-3 border-t border-white/20">
              <p className="text-xs font-bold text-indigo-200 uppercase mb-2">亮点时刻</p>
              <ul className="space-y-1">
                {summary.highlights.slice(0, 3).map((h: string, i: number) => (
                  <li key={i} className="text-xs flex items-start">
                    <span className="mr-2">✨</span> {h}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Feedback Form */}
        <div className="bg-white p-5 rounded-2xl shadow-sm mb-20">
          <h3 className="font-bold text-gray-700 mb-4">快速反馈</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-500 mb-2">乐乐的参与度评分 (1-5)</label>
              <div className="flex justify-between bg-gray-50 rounded-lg p-1">
                {[1, 2, 3, 4, 5].map(n => (
                  <button key={n} className="flex-1 h-10 rounded-md text-sm font-bold text-gray-600 hover:bg-white hover:shadow-md hover:text-primary transition focus:bg-white focus:shadow-md focus:text-primary">{n}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-500 mb-2">是否有感官过载或情绪问题？</label>
              <textarea className="w-full bg-gray-50 rounded-lg p-3 text-sm outline-none border border-transparent focus:border-primary/30 focus:bg-white transition" rows={2} placeholder="输入或使用语音..."></textarea>
            </div>
          </div>
        </div>

        <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100">
          <button onClick={() => { setGameState(GameState.LIST); onBack(); }} className="w-full bg-primary text-white py-3.5 rounded-xl font-bold shadow-lg hover:bg-green-600 transition active:scale-95">
            提交并返回
          </button>
        </div>
      </div>
    );
  }

  return <div>加载中...</div>;
};

// --- New Welcome/Onboarding Component ---
const PageWelcome = ({ onComplete }: { onComplete: (childId: string) => void }) => {
  const [isImporting, setIsImporting] = useState(false);
  const [status, setStatus] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    setStatus("正在上传并解析报告...");
    try {
      const result = await api.importProfileFromImage(file);
      setStatus("档案创建成功！正在为您生成画像...");
      setTimeout(() => {
        onComplete(result.child_id);
      }, 1500);
    } catch (err) {
      console.error(err);
      setStatus("上传失败，请重试。");
      setIsImporting(false);
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center p-8 bg-background text-center">
      <div className="w-20 h-20 bg-green-100 rounded-3xl flex items-center justify-center mb-6 animate-bounce">
        <Upload className="w-10 h-10 text-primary" />
      </div>
      <h2 className="text-2xl font-bold text-gray-800 mb-2">欢迎使用 ASD 地板时光助手</h2>
      <p className="text-gray-500 mb-8 leading-relaxed">
        为了为您提供个性化的干预建议，请先上传一张孩子的医学诊断报告或评估表图片。我们将为您自动建立档案。
      </p>

      <input
        type="file"
        ref={fileInputRef}
        onChange={handleUpload}
        className="hidden"
        accept="image/*"
      />

      <button
        onClick={() => fileInputRef.current?.click()}
        disabled={isImporting}
        className={`w-full py-4 rounded-xl font-bold shadow-lg transition transform active:scale-95 flex items-center justify-center ${isImporting ? 'bg-gray-300 cursor-not-allowed' : 'bg-primary text-white hover:bg-green-600'
          }`}
      >
        {isImporting ? (
          <Activity className="w-5 h-5 mr-2 animate-spin" />
        ) : (
          <Camera className="w-5 h-5 mr-2" />
        )}
        {isImporting ? status : "点击上传评估报告"}
      </button>

      {isImporting && (
        <p className="mt-4 text-sm text-primary font-medium animate-pulse">{status}</p>
      )}

      {!isImporting && (
        <button
          onClick={() => onComplete("test_child_001")}
          className="mt-6 text-sm text-gray-400 hover:text-gray-600 underline"
        >
          暂时跳过，使用演示账号
        </button>
      )}
    </div>
  );
};

// --- Main App Layout ---

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>(Page.CHAT);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [activeGameId, setActiveGameId] = useState<string | undefined>(undefined);
  const [gameMode, setGameMode] = useState<GameState>(GameState.LIST);

  // --- State for Data fetched from Backend ---
  const [profile, setProfile] = useState<ChildProfile | null>(null);
  const [games, setGames] = useState<Game[]>([]);
  const [calendarData, setCalendarData] = useState<CalendarEvent[]>([]);
  const [stats, setStats] = useState<{ radar: any[], trend: any[], interests: InterestCategory[] } | null>(null);

  // Fetch data on mount
  useEffect(() => {
    const loadData = async () => {
      try {
        // Try to get real profiles list
        let profiles: any[] = [];
        try {
          profiles = await api.listProfiles();
        } catch (e) {
          console.warn("Failed to fetch profiles, redirecting to welcome page");
          localStorage.removeItem('active_child_id');
          setCurrentPage(Page.WELCOME);
          return;
        }

        // Get active ID from storage
        const storedId = localStorage.getItem('active_child_id');

        // If no profiles exist, go to welcome page
        if (!profiles || profiles.length === 0) {
          if (storedId) localStorage.removeItem('active_child_id');
          setCurrentPage(Page.WELCOME);
          return;
        }

        // Validate if storedId is in the real list
        const profileExists = profiles.some((p: any) => p.child_id === storedId);

        let activeProfileId = profileExists ? storedId : (profiles[0] as any).child_id;

        // Update storage if we picked a new default from profiles[0]
        if (activeProfileId !== storedId) {
          localStorage.setItem('active_child_id', activeProfileId);
        }

        const [p, g, c, s] = await Promise.all([
          api.getProfile(activeProfileId),
          api.getGames(),
          api.getCalendar(),
          api.getStats()
        ]);

        if (!p && activeProfileId) {
          console.warn("Stored child ID not found, resetting to Welcome page");
          localStorage.removeItem('active_child_id');
          setCurrentPage(Page.WELCOME);
          return;
        }

        setProfile(p);
        setGames(g);
        setCalendarData(c);
        setStats(s);
      } catch (err) {
        console.error("Failed to load initial data", err);
        // On any error, redirect to welcome page
        localStorage.removeItem('active_child_id');
        setCurrentPage(Page.WELCOME);
      }
    };
    loadData();
  }, []);

  const handleOnboardingComplete = (childId: string) => {
    localStorage.setItem('active_child_id', childId);
    window.location.reload(); // Quick refresh to reload all data with new ID
  };

  const handleNavigate = (page: Page) => {
    setCurrentPage(page);
    setActiveGameId(undefined); // Reset active game on nav
    setGameMode(GameState.LIST);
  };

  useEffect(() => {
    const fetchGames = async () => {
      try {
        const libraryGames = await api.getGames();
        setGames(libraryGames);
      } catch (e) {
        console.error("Failed to load games:", e);
      }
    };
    fetchGames();
  }, []);

  const handleStartGame = (gameId: string, fullGame?: Game) => {
    if (fullGame) {
      // If we have full game data, ensure it's in the games list or handle it specially
      setGames(prev => {
        if (prev.some(g => g.id === gameId)) return prev;
        return [...prev, fullGame];
      });
    }
    setActiveGameId(gameId);
    setCurrentPage(Page.GAMES);
    setGameMode(GameState.PLAYING);
  };

  // Dynamically render the header title
  const getHeaderTitle = () => {
    switch (currentPage) {
      case Page.CHAT: return "AI 地板时光助手";
      case Page.CALENDAR: return "游戏计划";
      case Page.PROFILE: return `${profile?.name || "孩子"}的档案`;
      case Page.GAMES: return "游戏库";
      case Page.WELCOME: return "开启成长之旅";
      default: return "App";
    }
  };

  return (
    <div className="max-w-md mx-auto h-screen bg-gray-50 flex flex-col shadow-2xl overflow-hidden relative">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} setPage={handleNavigate} profile={profile} />

      {/* Header */}
      {currentPage !== Page.WELCOME && (
        <header className="bg-white px-4 py-3 flex items-center justify-between border-b border-gray-100 z-10 sticky top-0">
          <div className="flex items-center">
            {currentPage !== Page.CHAT && (
              <button onClick={() => setCurrentPage(Page.CHAT)} className="mr-3 text-gray-500 hover:text-primary transition">
                <ChevronLeft className="w-6 h-6" />
              </button>
            )}
            {currentPage === Page.CHAT && (
              <button onClick={() => setSidebarOpen(true)} className="mr-3 text-gray-700 hover:text-primary transition">
                <Menu className="w-6 h-6" />
              </button>
            )}
            <h1 className="text-lg font-bold text-gray-800">{getHeaderTitle()}</h1>
          </div>

          {/* Conditional Right Action */}
          {currentPage === Page.GAMES && gameMode === GameState.PLAYING ? (
            <button
              onClick={() => setGameMode(GameState.SUMMARY)}
              className="text-red-500 font-bold text-sm h-8 flex items-center px-2 rounded hover:bg-red-50 transition"
            >
              结束
            </button>
          ) : (
            <div className="w-8 h-8 rounded-full bg-gray-100 overflow-hidden border border-gray-200">
              {profile && <img src={profile.avatar} alt="User" />}
            </div>
          )}
        </header>
      )}

      {/* Main Content Area */}
      <main className="flex-1 overflow-hidden relative">
        {currentPage === Page.WELCOME && <PageWelcome onComplete={handleOnboardingComplete} />}
        {currentPage === Page.CHAT && <PageAIChat navigateTo={handleNavigate} onStartGame={handleStartGame} profile={profile} />}
        {currentPage === Page.CALENDAR && <PageCalendar navigateTo={handleNavigate} onStartGame={handleStartGame} calendarData={calendarData} />}
        {currentPage === Page.PROFILE && <PageProfile profile={profile} radarData={stats?.radar || []} trendData={stats?.trend || []} interests={stats?.interests || []} />}
        {currentPage === Page.GAMES && (
          <PageGames
            initialGameId={activeGameId}
            gameState={gameMode}
            setGameState={setGameMode}
            onBack={() => setCurrentPage(Page.CALENDAR)}
            games={games}
          />
        )}
      </main>
    </div>
  );
}