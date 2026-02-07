import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
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
  ArrowUpRight,
  RefreshCw,
  Zap,
  Thermometer,
  Meh,
  Angry,
  BrainCircuit,
  Ear,
  Hand,
  Dna,
  Layers,
  ListOrdered,
  Users,
  ClipboardCheck,
  CalendarClock,
  Tag
} from 'lucide-react';
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
import { Page, GameState, ChildProfile, Game, CalendarEvent, ChatMessage, LogEntry, InterestCategory, BehaviorAnalysis, InterestDimensionType, EvaluationResult, UserInterestProfile, UserAbilityProfile, AbilityDimensionType, ProfileUpdate } from './types';
import { api } from './services/api';

// --- Mock Data ---
const MOCK_PROFILE: ChildProfile = {
  name: "乐乐",
  age: 4,
  diagnosis: "ASD 谱系一级",
  avatar: "https://picsum.photos/200"
};

const MOCK_GAMES: Game[] = [
  {
    id: '1',
    title: '积木高塔轮流堆',
    target: '共同注意 (Shared Attention)',
    duration: '15 分钟',
    reason: '通过结构化的轮流互动，建立规则感和眼神接触。',
    steps: [
      { instruction: '和孩子面对面坐好，保持视线平齐。', guidance: '位置是关键！确保你能直接看到他的眼睛。' },
      { instruction: '你放一块积木，然后递给孩子一块。', guidance: '动作要慢。拿积木的时候，把积木举到你眼睛旁边。' },
      { instruction: '等待孩子看你一眼（眼神接触）再松手给他。', guidance: '数默数1-2-3，等待那个眼神接触的瞬间。' },
      { instruction: '当塔很高倒塌时，一起夸张地大笑庆祝！', guidance: '情感共鸣很重要。' }
    ]
  },
  {
    id: '2',
    title: '感官泡泡追逐战',
    target: '自我调节 (Self-Regulation)',
    duration: '10 分钟',
    reason: '帮助孩子进行情绪调节，同时增加非语言的共同参与。',
    steps: [
      { instruction: '缓慢地吹出泡泡。', guidance: '观察他的反应。' },
      { instruction: '鼓励孩子去戳破泡泡。', guidance: '如果他不敢碰，你可以先示范戳破一个。' },
      { instruction: '突然停止，做出夸张的表情等待（暂停）。', guidance: '这是“中断模式”。' },
      { instruction: '等待孩子发出信号（声音或手势）要求更多，再继续吹。', guidance: '任何信号都可以！' }
    ]
  },
  {
    id: '3',
    title: 'VR 奇幻森林绘画',
    target: '创造力 & 空间感知',
    duration: '20 分钟',
    reason: '利用沉浸式VR体验，让孩子在3D空间中自由涂鸦。',
    isVR: true,
    steps: [
      { instruction: '帮助孩子佩戴 VR 眼镜，进入“魔法森林”画室。', guidance: '刚开始可能会有不适感，先让孩子适应1-2分钟。' },
      { instruction: '选择“光之画笔”，在空中画出第一条线。', guidance: '示范动作要夸张。' },
      { instruction: '进行“接龙绘画”：你画一部分，孩子补全一部分。', guidance: '这是建立共同关注的好时机。' },
      { instruction: '保存作品并“具象化”展示。', guidance: '在虚拟空间中把画作“挂”在树上。' }
    ]
  }
];

const WEEK_DATA: CalendarEvent[] = [
  { day: 20, weekday: '周一', status: 'completed', gameTitle: '积木高塔', progress: '眼神接触 +3次' },
  { day: 21, weekday: '周二', status: 'today', time: '10:00', gameTitle: '感官泡泡' },
  { day: 22, weekday: '周三', status: 'future' },
  { day: 23, weekday: '周四', status: 'future' },
  { day: 24, weekday: '周五', status: 'future' },
  { day: 25, weekday: '周六', status: 'future' },
  { day: 26, weekday: '周日', status: 'future' },
];

// --- Helper Components ---
const getDimensionConfig = (dim: string) => {
  switch (dim) {
    case 'Visual': return { icon: Eye, color: 'text-purple-600 bg-purple-100', label: '视觉偏好' };
    case 'Auditory': return { icon: Ear, color: 'text-blue-600 bg-blue-100', label: '听觉敏感' };
    case 'Tactile': return { icon: Hand, color: 'text-amber-600 bg-amber-100', label: '触觉探索' };
    case 'Motor': return { icon: Activity, color: 'text-green-600 bg-green-100', label: '运动前庭' };
    case 'Construction': return { icon: Layers, color: 'text-cyan-600 bg-cyan-100', label: '建构拼搭' };
    case 'Order': return { icon: ListOrdered, color: 'text-slate-600 bg-slate-100', label: '秩序规律' };
    case 'Cognitive': return { icon: BrainCircuit, color: 'text-indigo-600 bg-indigo-100', label: '认知学习' };
    case 'Social': return { icon: Users, color: 'text-pink-600 bg-pink-100', label: '社交互动' };
    default: return { icon: Sparkles, color: 'text-gray-600 bg-gray-100', label: dim };
  }
};

const Sidebar = ({ isOpen, onClose, setPage }: { isOpen: boolean, onClose: () => void, setPage: (p: Page) => void }) => {
  return (
    <div className={`fixed inset-0 z-50 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out`}>
      <div className="absolute inset-0 bg-black/50" onClick={onClose}></div>
      <div className="absolute left-0 top-0 h-full w-64 bg-white shadow-xl flex flex-col p-6">
        <div className="flex justify-between items-center mb-8">
          <h2 className="text-xl font-bold text-gray-800">菜单</h2>
          <button onClick={onClose}><X className="w-6 h-6 text-gray-500" /></button>
        </div>
        <nav className="space-y-4">
          <button onClick={() => { setPage(Page.CHAT); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium"><MessageCircle className="w-5 h-5 text-primary" /><span>AI 对话助手</span></button>
          <button onClick={() => { setPage(Page.CALENDAR); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium"><CalendarIcon className="w-5 h-5 text-primary" /><span>成长日历</span></button>
          <button onClick={() => { setPage(Page.PROFILE); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium"><User className="w-5 h-5 text-primary" /><span>孩子档案</span></button>
          <button onClick={() => { setPage(Page.GAMES); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium"><Gamepad2 className="w-5 h-5 text-primary" /><span>地板游戏库</span></button>
        </nav>
        <div className="mt-auto pt-6 border-t border-gray-100">
          <div className="flex items-center space-x-3">
            <img src={MOCK_PROFILE.avatar} alt="Profile" className="w-10 h-10 rounded-full" />
            <div><p className="font-semibold text-sm">{MOCK_PROFILE.name}</p><p className="text-xs text-gray-500">{MOCK_PROFILE.diagnosis}</p></div>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- Page Components ---

const PageAIChat = ({ 
  navigateTo, 
  onStartGame, 
  onProfileUpdate, 
  profileContext 
}: { 
  navigateTo: (p: Page) => void, 
  onStartGame: (id: string) => void, 
  onProfileUpdate: (u: ProfileUpdate) => void,
  profileContext: string // Passed from App parent
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { 
      id: '1', 
      role: 'model', 
      text: "**你好！我是乐乐的地板时光助手。** 👋 \n\n我已读取了乐乐的最新档案。今天我们重点关注什么？", 
      timestamp: new Date(),
      options: ["🎮 推荐今日游戏", "📝 记录刚才的互动", "🤔 咨询孩子行为问题", "📅 查看本周计划"] 
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  const [checkInStep, setCheckInStep] = useState(0); 
  const [targetGameId, setTargetGameId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  const startCheckInFlow = (gameId: string, gameTitle: string) => {
      setTargetGameId(gameId);
      setCheckInStep(1);
      setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'model',
          text: `太棒了！我们准备开始玩 **${gameTitle}**。在此之前，为了确保互动效果，请先确认一下：\n\n**1. 孩子现在的情绪怎么样？**`,
          timestamp: new Date(),
          options: ["开心/兴奋", "平静/专注", "烦躁/低落"]
      }]);
  };

  const handleSend = async (textOverride?: string) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim()) return;

    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: textToSend, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    if (checkInStep > 0) {
        if (checkInStep === 1) {
            setTimeout(() => {
                setCheckInStep(2);
                setMessages(prev => [...prev, {
                    id: Date.now().toString(),
                    role: 'model',
                    text: "**2. 那他的能量水平（觉醒度）如何？**",
                    timestamp: new Date(),
                    options: ["低能量", "适中", "高亢/过载"]
                }]);
            }, 600);
            return;
        }
        if (checkInStep === 2) {
            setTimeout(() => {
                setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', text: "收到，状态确认完毕！正在为您进入游戏页面...", timestamp: new Date() }]);
                setTimeout(() => {
                    if (targetGameId) onStartGame(targetGameId);
                    setCheckInStep(0);
                    setTargetGameId(null);
                }, 1500);
            }, 600);
            return;
        }
    }

    setLoading(true);
    try {
      // *** Dialogue Agent Call with Profile Context ***
      const responseText = await api.sendMessage(textToSend, messages, profileContext);
      
      const modelMsg: ChatMessage = { 
        id: (Date.now() + 1).toString(), 
        role: 'model', 
        text: responseText, 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, modelMsg]);
    } catch (e) {
      console.error(e);
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', text: "我在听，请继续告诉我互动的细节。", timestamp: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setMessages(prev => [...prev, { id: Date.now().toString(), role: 'user', text: `📎 已上传文件: ${file.name}`, timestamp: new Date() }]);
      setLoading(true);

      try {
        let textContent = file.type === "text/plain" ? await file.text() : `文件名: ${file.name}。假设这是一份医疗评估报告。`;
        
        // *** Evaluation Agent Call (Report) ***
        const analysis = await api.analyzeReport(textContent);
        onProfileUpdate(analysis);

        const abilityChanges = analysis.abilityUpdates.map(u => `${u.dimension} ${u.scoreChange > 0 ? '+' : ''}${u.scoreChange}`).join('、');
        const replyText = `收到您的报告。我已经分析完毕并更新了孩子档案。\n\n**分析结果：**\n- 发现 ${analysis.interestUpdates.length} 个兴趣点\n- 能力维度调整：${abilityChanges || "无明显变化"}`;
        
        setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'model', text: replyText, timestamp: new Date() }]);

      } catch (e) {
          setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', text: "分析报告时出错了，请稍后再试。", timestamp: new Date() }]);
      } finally {
        setLoading(false);
        if (fileInputRef.current) fileInputRef.current.value = "";
      }
    }
  };

  const parseMessageContent = (text: string) => {
    const gameRegex = /:::GAME_RECOMMENDATION:\s*([\s\S]*?)\s*:::/;
    const navRegex = /:::NAVIGATION_CARD:\s*([\s\S]*?)\s*:::/;
    const behaviorRegex = /:::BEHAVIOR_LOG_CARD:\s*([\s\S]*?)\s*:::/;
    const weeklyRegex = /:::WEEKLY_PLAN_CARD:\s*([\s\S]*?)\s*:::/;
    
    let cleanText = text;
    let card: any = null;

    // Check patterns in priority order, but ensure cleanText removes ALL patterns
    const gameMatch = text.match(gameRegex);
    if (gameMatch?.[1]) { try { card = { ...JSON.parse(gameMatch[1]), type: 'GAME' }; } catch (e) {} }

    const navMatch = text.match(navRegex);
    if (navMatch?.[1] && !card) { try { card = { ...JSON.parse(navMatch[1]), type: 'NAV' }; } catch (e) {} }

    const behaviorMatch = text.match(behaviorRegex);
    if (behaviorMatch?.[1] && !card) { try { card = { ...JSON.parse(behaviorMatch[1]), type: 'BEHAVIOR' }; } catch (e) {} }

    const weeklyMatch = text.match(weeklyRegex);
    if (weeklyMatch?.[1] && !card) { try { card = { ...JSON.parse(weeklyMatch[1]), type: 'WEEKLY' }; } catch (e) {} }

    cleanText = cleanText
        .replace(gameRegex, '')
        .replace(navRegex, '')
        .replace(behaviorRegex, '')
        .replace(weeklyRegex, '')
        .trim();
        
    return { cleanText, card };
  };

  return (
    <div className="flex flex-col h-full bg-background relative">
       <div className="flex-1 overflow-y-auto p-4 space-y-5 pb-32">
        {messages.map((msg) => {
          const { cleanText, card } = parseMessageContent(msg.text);
          return (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[88%] p-4 rounded-2xl shadow-sm leading-relaxed text-sm ${msg.role === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none'}`}>
                {msg.role === 'user' ? cleanText : <ReactMarkdown components={{strong: ({node, ...props}) => <span className="font-bold text-gray-900" {...props} />}}>{cleanText}</ReactMarkdown>}
              </div>
              {msg.options && (
                <div className="mt-3 flex flex-wrap gap-2 animate-in fade-in max-w-[90%]">
                  {msg.options.map((opt, idx) => (
                    <button key={idx} onClick={() => handleSend(opt)} className="bg-white border border-primary/20 text-primary text-xs font-bold px-3 py-2 rounded-full shadow-sm hover:bg-green-50 active:scale-95 transition">{opt}</button>
                  ))}
                </div>
              )}
              {/* Card Rendering */}
              {card && card.type === 'GAME' && (
                <div className="mt-2 max-w-[85%] bg-white p-3 rounded-xl border-l-4 border-secondary shadow-md animate-in fade-in">
                   <div className="flex items-center space-x-2 mb-2"><Sparkles className="w-4 h-4 text-secondary" /><span className="text-xs font-bold text-secondary uppercase">推荐游戏 (基于分析)</span></div>
                   <h4 className="font-bold text-gray-800 text-lg mb-1">{card.title}</h4>
                   <p className="text-sm text-gray-600 mb-3 line-clamp-2">{card.reason}</p>
                   <button onClick={() => startCheckInFlow(card.id, card.title)} className="w-full bg-secondary text-white py-2 rounded-lg text-sm font-bold flex items-center justify-center hover:bg-blue-600 transition"><Play className="w-4 h-4 mr-2" /> 开始游戏</button>
                </div>
              )}
              {card && card.type === 'NAV' && (
                <div className="mt-2 max-w-[85%] bg-white p-3 rounded-xl border-l-4 border-primary shadow-md animate-in fade-in">
                   <div className="flex items-center space-x-2 mb-2"><ArrowUpRight className="w-4 h-4 text-primary" /><span className="text-xs font-bold text-primary uppercase">建议操作</span></div>
                   <h4 className="font-bold text-gray-800 text-lg mb-1">{card.title}</h4>
                   <p className="text-sm text-gray-600 mb-3 line-clamp-2">{card.reason}</p>
                   <button onClick={() => navigateTo(card.page === 'CALENDAR' ? Page.CALENDAR : Page.PROFILE)} className="w-full bg-primary/10 text-primary py-2 rounded-lg text-sm font-bold flex items-center justify-center hover:bg-primary/20 transition">前往查看</button>
                </div>
              )}
              {card && card.type === 'BEHAVIOR' && (
                <div className="mt-2 max-w-[85%] bg-white p-4 rounded-xl border border-emerald-100 shadow-md animate-in fade-in">
                   <div className="flex items-center space-x-2 mb-3 pb-2 border-b border-gray-100">
                     <div className="bg-emerald-100 p-1.5 rounded-full"><ClipboardCheck className="w-4 h-4 text-emerald-600" /></div>
                     <span className="text-xs font-bold text-emerald-700 uppercase">行为已记录</span>
                   </div>
                   <div className="mb-3">
                     <p className="text-gray-800 font-bold text-base mb-1">"{card.behavior}"</p>
                     <p className="text-xs text-gray-500">{card.analysis}</p>
                   </div>
                   {card.tags && (
                     <div className="flex flex-wrap gap-1">
                       {card.tags.map((t: string, i: number) => (
                         <span key={i} className="flex items-center bg-gray-100 text-gray-500 text-[10px] px-2 py-1 rounded-full font-medium">
                           <Tag className="w-3 h-3 mr-1" /> {t}
                         </span>
                       ))}
                     </div>
                   )}
                </div>
              )}
              {card && card.type === 'WEEKLY' && (
                 <div className="mt-2 w-full max-w-[90%] bg-white p-4 rounded-xl border-t-4 border-accent shadow-md animate-in fade-in">
                    <div className="flex items-center justify-between mb-3">
                       <div className="flex items-center space-x-2"><CalendarClock className="w-5 h-5 text-accent" /><span className="font-bold text-gray-800">本周计划概览</span></div>
                       <span className="text-[10px] bg-accent/10 text-accent px-2 py-1 rounded-full font-bold">{card.focus}</span>
                    </div>
                    <div className="space-y-2">
                       {card.schedule?.map((item: any, i: number) => (
                          <div key={i} className="flex items-center p-2 rounded-lg bg-gray-50 border border-gray-100">
                             <span className="text-xs font-bold text-gray-400 w-10">{item.day}</span>
                             <div className="h-4 w-[1px] bg-gray-200 mx-2"></div>
                             <span className="text-sm text-gray-700 font-medium">{item.task}</span>
                          </div>
                       ))}
                    </div>
                    <button onClick={() => navigateTo(Page.CALENDAR)} className="w-full mt-3 text-xs font-bold text-gray-400 hover:text-accent transition flex items-center justify-center py-2">查看完整日历 <ChevronRight className="w-3 h-3 ml-1" /></button>
                 </div>
              )}
            </div>
          );
        })}
        {loading && <div className="flex items-start"><div className="bg-white p-4 rounded-2xl rounded-bl-none shadow-sm flex space-x-2"><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></div><div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></div></div></div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="absolute bottom-24 left-0 right-0 px-4 flex justify-center space-x-3 pointer-events-none">
        <div className="pointer-events-auto flex space-x-3">
          <button onClick={() => navigateTo(Page.PROFILE)} className="bg-white/95 backdrop-blur shadow-lg px-5 py-2.5 rounded-full text-sm font-semibold text-primary border border-green-100 flex items-center transform active:scale-95 transition"><FileText className="w-4 h-4 mr-2" /> 孩童评估</button>
          <button onClick={() => navigateTo(Page.GAMES)} className="bg-white/95 backdrop-blur shadow-lg px-5 py-2.5 rounded-full text-sm font-semibold text-secondary border border-blue-100 flex items-center transform active:scale-95 transition"><Gamepad2 className="w-4 h-4 mr-2" /> 地板游戏</button>
        </div>
      </div>

      <div className="bg-white p-4 border-t border-gray-100">
        <div className="flex items-center bg-gray-100 rounded-full px-2 py-2">
          <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.doc,.docx,.txt" />
          <button onClick={() => fileInputRef.current?.click()} className="p-2 text-gray-500 hover:text-primary transition active:scale-90"><Paperclip className="w-5 h-5" /></button>
          <input value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSend()} placeholder={isRecording ? "正在听..." : "输入消息..."} className="flex-1 bg-transparent outline-none text-gray-700 placeholder-gray-400 ml-2" />
          <button onClick={() => { setIsRecording(!isRecording); if(!isRecording) setInput(prev => prev + " (语音...)"); }} className={`p-2 mr-1 transition rounded-full ${isRecording ? 'text-red-500 bg-red-100 animate-pulse' : 'text-gray-500 hover:text-primary'}`}><Mic className="w-5 h-5" /></button>
          <button onClick={() => handleSend()} className="p-2 bg-primary rounded-full text-white ml-1 hover:bg-green-600 transition shadow-md"><ArrowRight className="w-4 h-4" /></button>
        </div>
      </div>
    </div>
  );
};

const PageCalendar = ({ navigateTo, onStartGame }: { navigateTo: (p: Page) => void, onStartGame: (gameId: string) => void }) => {
  return (
    <div className="p-4 space-y-6 h-full overflow-y-auto bg-background">
      <div className="bg-gradient-to-r from-green-500 to-emerald-600 rounded-2xl p-5 text-white shadow-lg relative overflow-hidden">
        <div className="relative z-10"><h3 className="text-green-100 text-sm font-medium uppercase tracking-wide mb-1">本周目标</h3><p className="text-xl font-bold mb-3">提升“持续眼神接触”的频率</p><div className="h-2 bg-green-800/30 rounded-full w-full overflow-hidden"><div className="h-full bg-white/90 w-[60%] rounded-full"></div></div><p className="text-xs mt-2 text-green-100">已完成 3/5 个互动单元</p></div><Award className="absolute -right-4 -bottom-4 w-32 h-32 text-white/10" />
      </div>
      <div>
        <div className="flex justify-between items-center mb-4"><h3 className="font-bold text-gray-800 text-lg">2025年 1月</h3><button className="text-sm text-primary font-bold bg-green-50 px-3 py-1 rounded-full">生成下周计划</button></div>
        <div className="grid grid-cols-7 gap-2">
          {['一', '二', '三', '四', '五', '六', '日'].map((d, i) => <div key={i} className="text-center text-xs text-gray-400 font-medium mb-2">{d}</div>)}
          {WEEK_DATA.map((day) => {
             let bgClass = 'bg-white border-gray-200'; let textClass = 'text-gray-600';
             if (day.status === 'completed') { bgClass = 'bg-emerald-100 border-emerald-200'; textClass = 'text-emerald-700'; }
             if (day.status === 'today') { bgClass = 'bg-blue-50 border-blue-200 ring-2 ring-blue-400 ring-offset-1'; textClass = 'text-blue-700'; }
             return (<div key={day.day} onClick={() => { if(day.status === 'today' || day.day === 21) onStartGame('2'); }} className={`aspect-square rounded-xl border flex flex-col items-center justify-center p-1 cursor-pointer transition active:scale-95 ${bgClass}`}><span className={`text-xs font-bold mb-1 ${textClass}`}>{day.day}</span>{day.status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}{day.status === 'today' && <CalendarIcon className="w-4 h-4 text-blue-500" />}</div>)
          })}
        </div>
      </div>
      <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100"><div className="flex justify-between items-start mb-4"><div><span className="bg-blue-100 text-blue-700 text-xs px-2 py-1 rounded font-medium">今日, 10:00</span><h3 className="text-lg font-bold text-gray-800 mt-2">感官泡泡追逐战</h3><p className="text-sm text-gray-500">目标: 自我调节</p></div><button onClick={() => onStartGame('2')} className="w-12 h-12 bg-primary rounded-full flex items-center justify-center shadow-lg text-white hover:bg-green-600 transition animate-pulse"><Play className="w-6 h-6 ml-1" /></button></div></div>
    </div>
  );
};

const PageProfile = ({ trendData, interestProfile, abilityProfile }: { trendData: any[], interestProfile: UserInterestProfile, abilityProfile: UserAbilityProfile }) => {
  const getLevel = (score: number) => Math.min(5, Math.max(1, Math.floor(score / 5) + 1));
  const radarChartData = Object.entries(abilityProfile).map(([subject, score]) => ({ subject, A: Math.min(100, score), fullMark: 100 }));
  const categories = [
    { name: "感官偏好", dims: ['Visual', 'Auditory', 'Tactile', 'Motor'] as InterestDimensionType[] },
    { name: "认知与探索", dims: ['Construction', 'Order', 'Cognitive'] as InterestDimensionType[] },
    { name: "社交互动", dims: ['Social'] as InterestDimensionType[] }
  ];

  return (
    <div className="p-4 space-y-6 h-full overflow-y-auto bg-background">
      <div className="flex items-center space-x-4 bg-white p-5 rounded-2xl shadow-sm"><img src={MOCK_PROFILE.avatar} className="w-16 h-16 rounded-full border-2 border-white shadow" alt="乐乐" /><div><h2 className="text-2xl font-bold text-gray-800">{MOCK_PROFILE.name}, {MOCK_PROFILE.age}岁</h2><p className="text-gray-500 font-medium">{MOCK_PROFILE.diagnosis}</p></div></div>
      <div className="bg-white p-4 rounded-2xl shadow-sm"><h3 className="font-bold text-gray-700 mb-4 flex items-center"><Activity className="w-4 h-4 mr-2 text-primary"/> DIR 六大能力维度 (实时)</h3><div className="h-64 w-full"><ResponsiveContainer width="100%" height="100%"><RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarChartData}><PolarGrid stroke="#e5e7eb" /><PolarAngleAxis dataKey="subject" tick={{ fill: '#4b5563', fontSize: 11, fontWeight: 500 }} /><PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} /><Radar name="乐乐" dataKey="A" stroke="#10B981" fill="#10B981" fillOpacity={0.4} /></RadarChart></ResponsiveContainer></div></div>
       <div className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100"><div className="flex justify-between items-center mb-4"><h3 className="font-bold text-gray-700 flex items-center"><Flame className="w-4 h-4 mr-2 text-accent"/> 兴趣热力图 (实时分析)</h3><span className="text-[10px] text-gray-400 bg-gray-50 px-2 py-1 rounded-full">强度 1-5</span></div><div className="space-y-5">{categories.map((cat, idx) => (<div key={idx}><div className="flex items-center mb-2"><div className="w-2 h-2 rounded-full bg-gray-300 mr-2"></div><h4 className="text-xs font-bold text-gray-500">{cat.name}</h4></div><div className="grid grid-cols-2 sm:grid-cols-3 gap-2">{cat.dims.map((dim, i) => { const rawScore = interestProfile[dim] || 0; const level = getLevel(rawScore); const config = getDimensionConfig(dim); let colorClass = 'bg-gray-50 text-gray-400'; if (level >= 5) colorClass = 'bg-orange-500 text-white shadow-md shadow-orange-200'; else if (level >= 4) colorClass = 'bg-orange-400 text-white'; else if (level >= 3) colorClass = 'bg-orange-300 text-white'; else if (level >= 2) colorClass = 'bg-orange-100 text-orange-800'; return (<div key={i} className={`${colorClass} rounded-xl p-2 flex flex-col items-center justify-center text-center h-20 transition hover:scale-105`}><div className="flex items-center space-x-1 mb-1"><config.icon className="w-3 h-3" /><span className="text-xs font-bold leading-tight">{config.label}</span></div><div className="flex space-x-0.5">{[...Array(level)].map((_, starI) => (<div key={starI} className={`w-1 h-1 rounded-full ${level >= 3 ? 'bg-white/70' : 'bg-orange-500/40'}`}></div>))}</div></div>); })}</div></div>))}</div></div>
      <div className="bg-white p-4 rounded-2xl shadow-sm"><h3 className="font-bold text-gray-700 mb-4 flex items-center"><TrendingUp className="w-4 h-4 mr-2 text-secondary"/> 互动参与度趋势</h3><div className="h-48 w-full"><ResponsiveContainer width="100%" height="100%"><LineChart data={trendData}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" /><XAxis dataKey="name" tick={{fontSize: 10, fill: '#9ca3af'}} axisLine={false} tickLine={false} /><YAxis hide domain={[0, 100]} /><Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} /><Line type="monotone" dataKey="engagement" stroke="#3B82F6" strokeWidth={3} dot={{r: 4, fill: '#3B82F6', strokeWidth: 2, stroke: '#fff'}} animationDuration={1500} /></LineChart></ResponsiveContainer></div></div>
    </div>
  );
};

const PageGames = ({ 
  initialGameId, 
  gameState, 
  setGameState, 
  onBack, 
  trendData,
  onUpdateTrend,
  onProfileUpdate, 
  activeGame 
}: { 
  initialGameId?: string, 
  gameState: GameState, 
  setGameState: (s: GameState) => void, 
  onBack: () => void,
  trendData: any[],
  onUpdateTrend: (score: number) => void,
  onProfileUpdate: (u: ProfileUpdate) => void,
  activeGame?: Game
}) => {
  const [internalActiveGame, setInternalActiveGame] = useState<Game | undefined>(
      activeGame || (initialGameId ? MOCK_GAMES.find(g => g.id === initialGameId) : undefined)
  );
  useEffect(() => { if (initialGameId && !internalActiveGame) setInternalActiveGame(MOCK_GAMES.find(g => g.id === initialGameId)); }, [initialGameId]);

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [timer, setTimer] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0); 
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [clickedLog, setClickedLog] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [hasUpdatedTrend, setHasUpdatedTrend] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [activeFilter, setActiveFilter] = useState('全部');
  const FILTERS = ['全部', '共同注意', '自我调节', '亲密感', '双向沟通', '情绪思考', '创造力'];

  useEffect(() => {
    if (initialGameId && gameState !== GameState.PLAYING) {
        const game = MOCK_GAMES.find(g => g.id === initialGameId);
        if (game) {
            setInternalActiveGame(game);
            setCurrentStepIndex(0); setTimer(0); setLogs([]); setEvaluation(null); setHasUpdatedTrend(false);
        }
    }
  }, [initialGameId]);

  useEffect(() => {
    if (gameState === GameState.PLAYING) { timerRef.current = setInterval(() => setTimer(t => t + 1), 1000); } 
    else { if (timerRef.current) clearInterval(timerRef.current); }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [gameState]);

  useEffect(() => { if (gameState === GameState.SUMMARY && !evaluation && !isAnalyzing) performAnalysis(); }, [gameState]);

  const performAnalysis = async () => {
      setIsAnalyzing(true);
      try {
          const logsToAnalyze = logs.length > 0 ? logs : [{type: 'emoji', content: '完成了游戏', timestamp: new Date()} as LogEntry];
          
          // *** Evaluation Agent Call (Session) ***
          const result = await api.analyzeSession(logsToAnalyze);
          setEvaluation(result);
          
          if (result.score > 0 && !hasUpdatedTrend) {
             onUpdateTrend(result.score);
             const target = internalActiveGame?.target || "";
             let matchedDim: AbilityDimensionType | null = null;
             if (target.includes('自我调节')) matchedDim = '自我调节';
             else if (target.includes('共同注意')) matchedDim = '亲密感';
             else if (target.includes('创造力')) matchedDim = '情绪思考';

             const abilityUpdates = matchedDim ? [{
                 dimension: matchedDim,
                 scoreChange: Math.min(5, result.score / 20),
                 reason: `游戏训练: ${internalActiveGame?.title}`
             }] : [];

             onProfileUpdate({
                 source: 'GAME',
                 interestUpdates: result.interestAnalysis || [],
                 abilityUpdates: abilityUpdates
             });
             setHasUpdatedTrend(true);
          }
      } catch (e) { console.error(e); } finally { setIsAnalyzing(false); }
  };

  const handleStartGame = (game: Game) => { setInternalActiveGame(game); setGameState(GameState.PLAYING); setCurrentStepIndex(0); setTimer(0); setLogs([]); setEvaluation(null); setHasUpdatedTrend(false); };
  const handleLog = (type: 'emoji' | 'voice', content: string) => { setLogs(prev => [...prev, { type, content, timestamp: new Date() }]); setClickedLog(content); setTimeout(() => setClickedLog(null), 300); };
  const formatTime = (seconds: number) => { const m = Math.floor(seconds / 60); const s = seconds % 60; return `${m}:${s < 10 ? '0' : ''}${s}`; };

  if (gameState === GameState.LIST) {
    const filteredGames = MOCK_GAMES.filter(game => {
      const matchesSearch = game.title.toLowerCase().includes(searchText.toLowerCase()) || game.reason.toLowerCase().includes(searchText.toLowerCase()) || game.target.toLowerCase().includes(searchText.toLowerCase());
      const matchesFilter = activeFilter === '全部' || game.target.includes(activeFilter);
      return matchesSearch && matchesFilter;
    });

    return (
      <div className="h-full bg-background p-4 overflow-y-auto">
        <div className="sticky top-0 bg-background z-10 pb-2 -mx-4 px-4 pt-2">
            <div className="relative mb-3"><Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" /><input value={searchText} onChange={(e) => setSearchText(e.target.value)} className="w-full bg-white pl-10 pr-4 py-3 rounded-xl shadow-sm outline-none border border-transparent focus:border-primary/30 transition" placeholder="搜索游戏（如：积木）" /></div>
            <div className="flex space-x-2 overflow-x-auto pb-2 no-scrollbar">{FILTERS.map(f => (<button key={f} onClick={() => setActiveFilter(f)} className={`whitespace-nowrap px-4 py-1.5 rounded-full text-xs font-bold transition border ${activeFilter === f ? 'bg-primary text-white border-primary shadow-sm' : 'bg-white text-gray-500 border-gray-200 hover:bg-gray-50'}`}>{f}</button>))}</div>
        </div>
        <h3 className="font-bold text-gray-700 mb-3 flex items-center justify-between mt-2"><span>推荐游戏库</span><span className="text-xs font-normal text-gray-400 bg-gray-100 px-2 py-1 rounded-full">{filteredGames.length} 个结果</span></h3>
        <div className="space-y-4 pb-20">
          {filteredGames.length > 0 ? (filteredGames.map(game => (<div key={game.id} onClick={() => handleStartGame(game)} className="bg-white p-5 rounded-2xl shadow-sm border border-gray-100 active:scale-98 transition transform cursor-pointer group hover:border-primary/30"><div className="flex justify-between items-start"><h4 className="font-bold text-gray-800 text-lg group-hover:text-primary transition flex items-center">{game.title}{game.isVR && (<span className="ml-2 bg-indigo-600 text-white text-[10px] px-2 py-0.5 rounded-md shadow-sm font-bold flex items-center animate-pulse"><Sparkles className="w-3 h-3 mr-1 fill-current" /> VR体验</span>)}</h4><span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full font-medium shrink-0 ml-2">{game.duration}</span></div><p className="text-gray-500 text-sm mt-1 line-clamp-2">{game.reason}</p><div className="mt-4 flex items-center text-xs font-bold text-blue-600 bg-blue-50 w-fit px-3 py-1.5 rounded-lg">目标: {game.target}</div></div>))) : (<div className="text-center py-10 text-gray-400 flex flex-col items-center"><div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4"><Search className="w-8 h-8 text-gray-300" /></div><p>没有找到匹配的游戏</p><button onClick={() => {setSearchText(''); setActiveFilter('全部')}} className="mt-2 text-primary font-bold text-sm">清除筛选</button></div>)}
        </div>
      </div>
    );
  }

  if (gameState === GameState.PLAYING && internalActiveGame) {
    const currentStep = internalActiveGame.steps[currentStepIndex];
    const isLastStep = currentStepIndex === internalActiveGame.steps.length - 1;
    return (
      <div className="h-full flex flex-col bg-background">
        <div className="w-full flex flex-col items-center py-4 bg-background z-0"><h3 className="font-bold text-sm text-gray-500 mb-1">{internalActiveGame.title}</h3><div className="text-green-600 font-mono text-3xl font-bold">{formatTime(timer)}</div></div>
        <div className="flex-1 px-4 pb-2 flex flex-col min-h-0"><div className="bg-white rounded-[2rem] shadow-sm border border-gray-100 flex-1 flex flex-col p-6 relative overflow-hidden"><div className="w-full flex justify-center mb-6 shrink-0"><div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xl shadow-sm">{currentStepIndex + 1}</div></div><div className="flex-1 flex flex-col justify-center overflow-y-auto no-scrollbar"><h2 className="text-2xl font-bold text-gray-800 leading-normal text-center mb-8">{currentStep.instruction}</h2><div className="bg-blue-50/80 p-5 rounded-2xl border border-blue-100 text-left w-full"><h4 className="text-blue-800 font-bold mb-2 flex items-center text-sm"><Lightbulb className="w-4 h-4 mr-2 text-yellow-500 fill-current"/> 互动小贴士</h4><p className="text-blue-900/80 text-sm leading-relaxed font-medium">{currentStep.guidance}</p></div></div></div></div>
        <div className="flex items-center justify-between px-6 py-4 mb-2"><button onClick={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))} disabled={currentStepIndex === 0} className={`flex items-center text-gray-400 font-bold transition px-4 py-3 ${currentStepIndex === 0 ? 'opacity-30 cursor-not-allowed' : 'hover:text-gray-600'}`}><ChevronLeft className="w-5 h-5 mr-1" /> 上一步</button><div className="bg-white px-4 py-2 rounded-xl shadow-sm border border-gray-100 text-xs font-bold text-gray-500 tracking-wide">步骤 {currentStepIndex + 1} / {internalActiveGame.steps.length}</div>{isLastStep ? (<button onClick={() => setGameState(GameState.SUMMARY)} className="bg-primary text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-primary/30 flex items-center hover:bg-green-600 transition transform active:scale-95">完成 <CheckCircle2 className="w-5 h-5 ml-2" /></button>) : (<button onClick={() => setCurrentStepIndex(currentStepIndex + 1)} className="bg-secondary text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-secondary/30 flex items-center hover:bg-blue-600 transition transform active:scale-95">下一步 <ChevronRight className="w-5 h-5 ml-1" /></button>)}</div>
        <div className="p-4 bg-white border-t border-gray-100 pb-8 rounded-t-3xl shadow-[0_-4px_20px_-5px_rgba(0,0,0,0.1)] z-20 relative"><p className="text-center text-[10px] text-gray-400 mb-3 uppercase tracking-widest font-bold">快速记录当前反应</p><div className="flex justify-between max-w-sm mx-auto mb-3 space-x-2">{[{ icon: Smile, label: '微笑', color: 'text-yellow-600 bg-yellow-100 ring-yellow-300' }, { icon: Eye, label: '眼神', color: 'text-blue-600 bg-blue-100 ring-blue-300' }, { icon: Handshake, label: '互动', color: 'text-green-600 bg-green-100 ring-green-300' }, { icon: Frown, label: '抗拒', color: 'text-red-500 bg-red-100 ring-red-300' }].map((btn, i) => (<button key={i} onClick={() => handleLog('emoji', btn.label)} className={`flex-1 py-3 rounded-xl shadow-sm active:scale-95 transition flex flex-col items-center justify-center ${btn.color} ${clickedLog === btn.label ? 'ring-4 ring-offset-2 scale-110 bg-opacity-100' : ''}`}><btn.icon className="w-5 h-5 mb-1" /><span className="text-[10px] font-bold">{btn.label}</span></button>))}</div><button onMouseDown={() => { setClickedLog('voice'); handleLog('voice', '录音开始...'); }} onMouseUp={() => handleLog('voice', '录音结束')} className={`w-full bg-gray-50 border border-gray-200 py-3 rounded-xl text-gray-600 font-bold flex items-center justify-center shadow-sm active:bg-gray-200 active:scale-98 transition text-sm ${clickedLog === 'voice' ? 'ring-2 ring-gray-300 bg-gray-100' : ''}`}><Mic className="w-4 h-4 mr-2" /> 按住说话 记录观察笔记</button></div>
      </div>
    );
  }

  if (gameState === GameState.SUMMARY) {
    return (
      <div className="h-full bg-background p-6 overflow-y-auto">
         {isAnalyzing ? (
           <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6 animate-in fade-in duration-700"><div className="relative"><div className="w-20 h-20 border-4 border-gray-200 rounded-full"></div><div className="w-20 h-20 border-4 border-primary border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div><Activity className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-primary w-8 h-8" /></div><div><h2 className="text-xl font-bold text-gray-800">AI 正在复盘互动数据...</h2><p className="text-gray-500 text-sm mt-2">分析眼神接触频率、情绪稳定度及八大兴趣维度</p></div></div>
         ) : evaluation ? (
           <div className="animate-in slide-in-from-bottom-10 duration-700 fade-in pb-10">
              <div className="text-center mb-8"><h2 className="text-2xl font-bold text-gray-800">本次互动评估</h2><p className="text-gray-400 text-xs mt-1">{new Date().toLocaleDateString()}</p></div>
              <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 relative overflow-hidden text-center">
                  <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-green-400 to-blue-500"></div>
                  <div className="mb-2 text-gray-500 font-bold text-sm uppercase tracking-wider">综合互动分</div>
                  <div className="text-6xl font-black text-gray-800 mb-2 tracking-tighter">{evaluation.score}</div>
                  <div className="flex justify-center mb-4"><div className="flex space-x-1">{[1,2,3,4,5].map(star => (<div key={star} className={`w-2 h-2 rounded-full ${evaluation.score >= star * 18 ? 'bg-yellow-400' : 'bg-gray-200'}`}></div>))}</div></div>
                  
                  {/* New: Score Breakdown */}
                  <div className="flex justify-center space-x-8 mt-6 border-t border-gray-100 pt-4">
                    <div className="text-center">
                        <div className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-1">反馈质量</div>
                        <div className="text-2xl font-bold text-blue-600">{evaluation.feedbackScore || 0}</div>
                    </div>
                    <div className="w-px bg-gray-200"></div>
                    <div className="text-center">
                        <div className="text-xs text-gray-400 font-bold uppercase tracking-wider mb-1">探索广度</div>
                        <div className="text-2xl font-bold text-purple-600">{evaluation.explorationScore || 0}</div>
                    </div>
                  </div>

                  <p className="text-gray-600 text-sm leading-relaxed px-2 mt-4">{evaluation.summary}</p>
              </div>
              {evaluation.interestAnalysis && evaluation.interestAnalysis.length > 0 && (<div className="bg-white p-5 rounded-2xl shadow-sm mb-6 border border-gray-100"><h3 className="font-bold text-gray-700 mb-4 flex items-center"><Dna className="w-5 h-5 mr-2 text-indigo-500"/> 兴趣探索度分析</h3><div className="space-y-4">{evaluation.interestAnalysis.map((item, idx) => (<div key={idx} className="bg-gray-50 rounded-xl p-3 border border-gray-100"><p className="text-sm font-semibold text-gray-800 mb-2">"{item.behavior}"</p><div className="flex flex-wrap gap-2">{item.matches.map((match, mIdx) => { const config = getDimensionConfig(match.dimension); return (<div key={mIdx} className="flex flex-col"><div className={`flex items-center px-2 py-1 rounded-md text-xs font-bold ${config.color}`}><config.icon className="w-3 h-3 mr-1" />{config.label} {(match.weight * 100).toFixed(0)}%</div></div>) })}</div>{item.matches[0] && (<p className="text-[10px] text-gray-500 mt-2 italic border-t border-gray-200 pt-1">💡 {item.matches[0].reasoning}</p>)}</div>))}</div></div>)}
              <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white p-5 rounded-2xl shadow-lg mb-6 relative overflow-hidden"><div className="relative z-10"><h3 className="font-bold flex items-center mb-3"><Lightbulb className="w-4 h-4 mr-2 text-yellow-300"/> 下一步建议</h3><p className="text-indigo-100 text-sm leading-relaxed font-medium">{evaluation.suggestion}</p></div><Sparkles className="absolute -right-2 -bottom-2 text-white/10 w-24 h-24 rotate-12" /></div>
              <div className="bg-white p-4 rounded-2xl shadow-sm mb-20 border border-gray-100"><h3 className="font-bold text-gray-700 mb-4 flex items-center justify-between"><span className="flex items-center"><TrendingUp className="w-4 h-4 mr-2 text-green-500"/> 成长曲线已更新</span><span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold">+1 记录</span></h3><div className="h-40 w-full"><ResponsiveContainer width="100%" height="100%"><LineChart data={trendData}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" /><XAxis dataKey="name" tick={{fontSize: 9, fill: '#9ca3af'}} axisLine={false} tickLine={false} interval={0} /><YAxis hide domain={[0, 100]} /><Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} /><Line type="monotone" dataKey="engagement" stroke="#10B981" strokeWidth={3} dot={(props: any) => { const isLast = props.index === trendData.length - 1; return (<circle cx={props.cx} cy={props.cy} r={isLast ? 6 : 4} fill={isLast ? "#10B981" : "#fff"} stroke="#10B981" strokeWidth={2} />); }} isAnimationActive={true} /></LineChart></ResponsiveContainer></div></div>
              <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100"><button onClick={() => { setGameState(GameState.LIST); onBack(); }} className="w-full bg-gray-900 text-white py-3.5 rounded-xl font-bold shadow-lg hover:bg-gray-800 transition active:scale-95 flex items-center justify-center"><RefreshCw className="w-4 h-4 mr-2" /> 返回游戏库</button></div>
           </div>
         ) : (<div className="text-center mt-20 text-gray-400"><p>无法生成评估结果</p><button onClick={() => setGameState(GameState.LIST)} className="mt-4 text-primary">返回</button></div>)}
      </div>
    );
  }

  return <div>加载中...</div>;
};

// --- App Root ---

const INITIAL_TREND_DATA = [
  { name: '第1周', engagement: 30 },
  { name: '第2周', engagement: 45 },
  { name: '第3周', engagement: 40 },
  { name: '第4周', engagement: 60 },
  { name: '第5周', engagement: 75 },
];

const INITIAL_INTEREST_SCORES: UserInterestProfile = { Visual: 5, Auditory: 2, Tactile: 3, Motor: 8, Construction: 6, Order: 1, Cognitive: 4, Social: 7 };
const INITIAL_ABILITY_SCORES: UserAbilityProfile = { '自我调节': 80, '亲密感': 90, '双向沟通': 60, '复杂沟通': 50, '情绪思考': 70, '逻辑思维': 40 };

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>(Page.CHAT);
  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [activeGameId, setActiveGameId] = useState<string | undefined>(undefined);
  const [gameMode, setGameMode] = useState<GameState>(GameState.LIST);
  const [trendData, setTrendData] = useState(INITIAL_TREND_DATA);

  const [interestProfile, setInterestProfile] = useState<UserInterestProfile>(() => {
    try { const saved = localStorage.getItem('asd_floortime_interests_v1'); if (saved) return JSON.parse(saved); } catch (e) {}
    return INITIAL_INTEREST_SCORES;
  });

  const [abilityProfile, setAbilityProfile] = useState<UserAbilityProfile>(() => {
    try { const saved = localStorage.getItem('asd_floortime_abilities_v1'); if (saved) return JSON.parse(saved); } catch (e) {}
    return INITIAL_ABILITY_SCORES;
  });

  // *** Serialize Profile Context for Agents ***
  const profileContextString = `
  [当前兴趣画像]
  ${Object.entries(interestProfile).map(([k,v]) => `${k}: ${v}`).join(', ')}
  
  [当前能力画像]
  ${Object.entries(abilityProfile).map(([k,v]) => `${k}: ${v}`).join(', ')}
  `;

  useEffect(() => { localStorage.setItem('asd_floortime_interests_v1', JSON.stringify(interestProfile)); }, [interestProfile]);
  useEffect(() => { localStorage.setItem('asd_floortime_abilities_v1', JSON.stringify(abilityProfile)); }, [abilityProfile]);

  const handleProfileUpdate = (update: ProfileUpdate) => {
    if (update.interestUpdates?.length > 0) {
      setInterestProfile(prev => {
        const next = { ...prev };
        update.interestUpdates.forEach(item => { item.matches.forEach(match => { next[match.dimension] = (next[match.dimension] || 0) + (match.weight * 5); }); });
        return next;
      });
    }
    if (update.abilityUpdates?.length > 0) {
      setAbilityProfile(prev => {
        const next = { ...prev };
        update.abilityUpdates.forEach(u => { next[u.dimension] = Math.max(0, Math.min(100, (next[u.dimension] || 0) + u.scoreChange)); });
        return next;
      });
    }
  };

  const handleNavigate = (page: Page) => { setCurrentPage(page); setActiveGameId(undefined); setGameMode(GameState.LIST); };
  const handleStartGame = (gameId: string) => { setActiveGameId(gameId); setGameMode(GameState.PLAYING); setCurrentPage(Page.GAMES); };
  const handleUpdateTrend = (newScore: number) => { setTrendData(prev => [...prev, { name: '本次', engagement: newScore }]); };
  const getHeaderTitle = () => { switch (currentPage) { case Page.CHAT: return "AI 地板时光助手"; case Page.CALENDAR: return "游戏计划"; case Page.PROFILE: return "乐乐的档案"; case Page.GAMES: return "游戏库"; default: return "App"; } };

  return (
    <div className="max-w-md mx-auto h-screen bg-gray-50 flex flex-col shadow-2xl overflow-hidden relative">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} setPage={handleNavigate} />
      <header className="bg-white px-4 py-3 flex items-center justify-between border-b border-gray-100 z-10 sticky top-0"><div className="flex items-center">{currentPage !== Page.CHAT && (<button onClick={() => setCurrentPage(Page.CHAT)} className="mr-3 text-gray-500 hover:text-primary transition"><ChevronLeft className="w-6 h-6" /></button>)}{currentPage === Page.CHAT && (<button onClick={() => setSidebarOpen(true)} className="mr-3 text-gray-700 hover:text-primary transition"><Menu className="w-6 h-6" /></button>)}<h1 className="text-lg font-bold text-gray-800">{getHeaderTitle()}</h1></div>{currentPage === Page.GAMES && gameMode === GameState.PLAYING ? (<button onClick={() => setGameMode(GameState.SUMMARY)} className="text-red-500 font-bold text-sm h-8 flex items-center px-2 rounded hover:bg-red-50 transition">结束</button>) : (<div className="w-8 h-8 rounded-full bg-gray-100 overflow-hidden border border-gray-200"><img src={MOCK_PROFILE.avatar} alt="User" /></div>)}</header>
      <main className="flex-1 overflow-hidden relative">
        {currentPage === Page.CHAT && <PageAIChat navigateTo={handleNavigate} onStartGame={handleStartGame} onProfileUpdate={handleProfileUpdate} profileContext={profileContextString} />}
        {currentPage === Page.CALENDAR && <PageCalendar navigateTo={handleNavigate} onStartGame={handleStartGame} />}
        {currentPage === Page.PROFILE && <PageProfile trendData={trendData} interestProfile={interestProfile} abilityProfile={abilityProfile} />}
        {currentPage === Page.GAMES && (<PageGames initialGameId={activeGameId} gameState={gameMode} setGameState={setGameMode} onBack={() => setCurrentPage(Page.CALENDAR)} trendData={trendData} onUpdateTrend={handleUpdateTrend} onProfileUpdate={handleProfileUpdate} />)}
      </main>
    </div>
  );
}