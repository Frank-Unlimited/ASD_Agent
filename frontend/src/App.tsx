﻿import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendQwenMessage } from './services/qwenService';
import { clearAllCache } from './utils/clearCache'; // 导入清空缓存功能
import { generateComprehensiveAssessment } from './services/assessmentAgent';
import { collectHistoricalData } from './services/historicalDataHelper';
import { saveAssessment, getRecentAssessments } from './services/assessmentStorage';
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
  Settings,
  ChevronDown,
  ChevronUp,
  Tag,
  Keyboard,
  Package,
  LogOut
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
import { Page, GameState, ChildProfile, Game, CalendarEvent, ChatMessage, LogEntry, InterestCategory, BehaviorAnalysis, InterestDimensionType, EvaluationResult, UserInterestProfile, UserAbilityProfile, AbilityDimensionType, ProfileUpdate, Report, FloorGame, GameReviewResult } from './types';
import { api } from './services/api';
import { multimodalService } from './services/multimodalService';
import { fileUploadService } from './services/fileUpload';
import { speechService } from './services/speechService';
import { reportStorageService } from './services/reportStorage';
import { behaviorStorageService } from './services/behaviorStorage';
import { floorGameStorageService } from './services/floorGameStorage';
import { reviewFloorGame } from './services/gameReviewAgent';
import { chatStorageService } from './services/chatStorage';
import { ASD_REPORT_ANALYSIS_PROMPT } from './prompts';
import { WEEK_DATA, INITIAL_TREND_DATA, INITIAL_INTEREST_SCORES, INITIAL_ABILITY_SCORES } from './constants/mockData';
import { getDimensionConfig, calculateAge, formatTime, getInterestLevel } from './utils/helpers';
import { PageRadar } from './components/RadarChartPage';
import { PageCalendar } from './components/CalendarPage';
import AIVideoCall from './components/AIVideoCall';
import defaultAvatar from './img/cute_dog.jpg';

// --- Helper Components ---

const Sidebar = ({ isOpen, onClose, setPage, onLogout, childProfile }: { isOpen: boolean, onClose: () => void, setPage: (p: Page) => void, onLogout: () => void, childProfile: ChildProfile | null }) => {
  const [showProfileMenu, setShowProfileMenu] = useState(false);

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
          <button onClick={() => { setPage(Page.BEHAVIORS); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium"><Activity className="w-5 h-5 text-primary" /><span>行为数据</span></button>
          <button onClick={() => { setPage(Page.RADAR); onClose(); }} className="flex items-center space-x-3 w-full p-3 rounded-lg hover:bg-green-50 text-gray-700 font-medium"><TrendingUp className="w-5 h-5 text-primary" /><span>兴趣雷达图</span></button>
        </nav>
        <div className="mt-auto pt-6 border-t border-gray-100 relative">
          <div
            className="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition"
            onClick={() => setShowProfileMenu(!showProfileMenu)}
          >
            <img src={childProfile?.avatar || defaultAvatar} alt="Profile" className="w-10 h-10 rounded-full" />
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm truncate">{childProfile?.name || '未设置'}</p>
              <p className="text-xs text-gray-500 truncate">
                {childProfile?.birthDate
                  ? `${calculateAge(childProfile.birthDate)}岁 · ${childProfile.gender || ''}`
                  : '暂无信息'}
              </p>
            </div>
            <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform flex-shrink-0 ${showProfileMenu ? 'rotate-90' : ''}`} />
          </div>

          {/* 弹出菜单 */}
          {showProfileMenu && (
            <div className="absolute bottom-full left-0 right-0 mb-2 bg-white rounded-lg shadow-xl border border-gray-200 overflow-hidden animate-in fade-in slide-in-from-bottom-2">
              <button
                onClick={() => { setPage(Page.PROFILE); onClose(); setShowProfileMenu(false); }}
                className="w-full flex items-center space-x-3 px-4 py-3 hover:bg-gray-50 transition text-left"
              >
                <User className="w-4 h-4 text-gray-600" />
                <span className="text-sm font-medium text-gray-700">查看档案</span>
              </button>
              <button
                onClick={() => { onLogout(); setShowProfileMenu(false); }}
                className="w-full flex items-center space-x-3 px-4 py-3 hover:bg-red-50 transition text-left border-t border-gray-100"
              >
                <X className="w-4 h-4 text-red-600" />
                <span className="text-sm font-medium text-red-600">退出登录</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// --- Page Components ---

const PageWelcome = ({ onComplete }: { onComplete: (childInfo: any) => void }) => {
  const [step, setStep] = useState(1); // 1: 基本信息, 2: 孩子情况了解
  const [name, setName] = useState('');
  const [gender, setGender] = useState('');
  const [birthDate, setBirthDate] = useState('');

  // 第二步：导入报告或口述
  const [inputMode, setInputMode] = useState<'none' | 'report' | 'verbal'>('none');
  const [reportFile, setReportFile] = useState<File | null>(null);
  const [reportImageUrl, setReportImageUrl] = useState<string>(''); // 报告图片预览
  const [verbalInput, setVerbalInput] = useState('');
  const [ocrResult, setOcrResult] = useState<string>(''); // OCR 提取结果
  const [reportSummary, setReportSummary] = useState<string>(''); // 报告摘要
  const [childDiagnosis, setChildDiagnosis] = useState<string>(''); // 孩子画像
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleNextStep = () => {
    if (!name || !gender || !birthDate) {
      alert('请填写孩子的基本信息');
      return;
    }
    setStep(2);
  };

  const handleSubmit = () => {
    const childInfo = {
      name,
      gender,
      birthDate,
      diagnosis: childDiagnosis || '暂无评估信息',
      createdAt: new Date().toISOString()
    };
    onComplete(childInfo);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setReportFile(file);
    setIsAnalyzing(true);
    setOcrResult('');
    setReportSummary('');
    setChildDiagnosis('');

    // 创建图片预览 URL
    const imageUrl = URL.createObjectURL(file);
    setReportImageUrl(imageUrl);

    try {
      const category = fileUploadService.categorizeFile(file);

      if (category === 'image') {
        const result = await multimodalService.parseImage(
          file,
          ASD_REPORT_ANALYSIS_PROMPT,
          true  // 使用 JSON 格式输出
        );

        // 打印 AI 返回结果到控制台
        console.log('=== AI 返回结果 ===');
        console.log('原始内容:', result.content);
        console.log('==================');

        if (result.success) {
          // 尝试解析 JSON 格式的结果
          try {
            // 提取 JSON 内容（可能被包裹在 ```json ``` 中）
            let jsonContent = result.content;
            const jsonMatch = result.content.match(/```json\s*([\s\S]*?)\s*```/);
            if (jsonMatch) {
              jsonContent = jsonMatch[1];
            }

            const parsed = JSON.parse(jsonContent);

            console.log('=== 解析后的 JSON ===');
            console.log('OCR:', parsed.ocr);
            console.log('Summary:', parsed.summary);
            console.log('Profile:', parsed.profile);
            console.log('====================');

            // 确保转换为字符串
            const ocrText = typeof parsed.ocr === 'string' ? parsed.ocr : JSON.stringify(parsed.ocr, null, 2);
            const summaryText = typeof parsed.summary === 'string' ? parsed.summary : '';
            const profileText = typeof parsed.profile === 'string' ? parsed.profile : JSON.stringify(parsed.profile, null, 2);

            setOcrResult(ocrText || '（未提取到文字）');
            setReportSummary(summaryText || '（未生成摘要）');
            setChildDiagnosis(profileText || '（未生成画像）');

            // 保存报告到数据库
            const metadata = result.metadata;
            if (metadata?.base64) {
              const report: Report = {
                id: reportStorageService.generateReportId(),
                imageUrl: metadata.base64,
                ocrResult: ocrText,
                summary: summaryText,
                diagnosis: profileText,
                date: new Date().toISOString().split('T')[0],
                type: 'hospital',
                createdAt: new Date().toISOString()
              };

              reportStorageService.saveReport(report);
              console.log('报告已保存到数据库:', report.id);
            }
          } catch (parseError) {
            // 如果不是 JSON 格式，将整个内容作为画像
            console.warn('无法解析 JSON 格式，使用原始内容', parseError);
            console.log('解析错误详情:', parseError);
            setChildDiagnosis(result.content);
            setOcrResult('（OCR 提取失败，请查看画像内容）');
            setReportSummary('（未生成摘要）');
          }
        } else {
          console.error('报告分析失败:', result.error);
          alert('报告分析失败：' + result.error);
          setReportFile(null);
          setReportImageUrl('');
        }
      } else if (category === 'document') {
        const textContent = file.type === "text/plain" ? await file.text() : `文件名: ${file.name}`;
        const analysis = await api.analyzeReportForDiagnosis(textContent);
        setChildDiagnosis(analysis);
        setOcrResult(textContent);
      } else {
        alert('不支持的文件类型，请上传图片（JPG/PNG）或文档（TXT/PDF）');
        setReportFile(null);
        setReportImageUrl('');
      }
    } catch (error) {
      alert('报告分析失败：' + (error instanceof Error ? error.message : '未知错误'));
      setReportFile(null);
      setReportImageUrl('');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleVerbalAnalysis = async () => {
    if (!verbalInput.trim()) {
      alert('请先描述孩子的情况');
      return;
    }

    setIsAnalyzing(true);
    try {
      const analysis = await api.analyzeVerbalInput(verbalInput);
      setChildDiagnosis(analysis);
    } catch (error) {
      alert('分析失败：' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const canSubmit = step === 1 || (step === 2 && (inputMode === 'none' || childDiagnosis));

  return (
    <div className="h-full overflow-y-auto bg-gradient-to-br from-green-50 to-blue-50 p-6 flex items-center justify-center">
      <div className="w-full max-w-2xl bg-white rounded-3xl shadow-2xl p-8">
        {/* 标题 - 简化版 */}
        <div className="text-center mb-8">
          {/* 步骤指示器 */}
          <div className="flex items-center justify-center space-x-2">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step === 1 ? 'bg-primary text-white' : 'bg-green-500 text-white'}`}>
              {step > 1 ? <CheckCircle2 className="w-5 h-5" /> : '1'}
            </div>
            <div className={`w-12 h-1 rounded ${step === 2 ? 'bg-primary' : 'bg-gray-200'}`}></div>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step === 2 ? 'bg-primary text-white' : 'bg-gray-200 text-gray-600'}`}>2</div>
          </div>
        </div>

        {/* 第一步：基本信息 */}
        {step === 1 && (
          <div className="space-y-5 animate-in fade-in slide-in-from-right">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">孩子姓名 *</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="请输入孩子的姓名或昵称"
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">性别 *</label>
              <div className="flex gap-4">
                <button
                  onClick={() => setGender('男')}
                  className={`flex-1 py-3 rounded-xl border-2 transition ${gender === '男' ? 'border-primary bg-primary/10 text-primary font-medium' : 'border-gray-300 text-gray-600'
                    }`}
                >
                  男孩
                </button>
                <button
                  onClick={() => setGender('女')}
                  className={`flex-1 py-3 rounded-xl border-2 transition ${gender === '女' ? 'border-primary bg-primary/10 text-primary font-medium' : 'border-gray-300 text-gray-600'
                    }`}
                >
                  女孩
                </button>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">出生日期 *</label>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition"
              />
            </div>

            <button
              onClick={handleNextStep}
              disabled={!name || !gender || !birthDate}
              className="w-full py-4 bg-gradient-to-r from-primary to-secondary text-white rounded-xl font-medium hover:shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一步
            </button>
          </div>
        )}

        {/* 第二步：了解孩子情况 */}
        {step === 2 && (
          <div className="space-y-6 animate-in fade-in slide-in-from-left">
            {/* 引导说明 */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-5 border border-blue-100">
              <div className="flex items-start space-x-3">
                <Lightbulb className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
                <div>
                  <h3 className="font-bold text-gray-800 mb-2">帮助我们更好地了解{name}</h3>
                  <p className="text-sm text-gray-600 leading-relaxed">
                    您可以选择上传医疗评估报告，或者用自己的话描述孩子的情况。这将帮助我们为{name}提供更个性化的干预建议。
                    <span className="text-blue-600 font-medium">（此步骤可跳过，后续也可以在档案页面补充）</span>
                  </p>
                </div>
              </div>
            </div>

            {/* 选择输入方式 */}
            {inputMode === 'none' && (
              <div className="grid grid-cols-2 gap-4">
                <button
                  onClick={() => setInputMode('report')}
                  className="p-6 border-2 border-gray-200 rounded-xl hover:border-primary hover:bg-primary/5 transition group"
                >
                  <FileText className="w-12 h-12 text-gray-400 group-hover:text-primary mx-auto mb-3 transition" />
                  <h4 className="font-bold text-gray-800 mb-1">上传报告</h4>
                  <p className="text-xs text-gray-500">医疗评估报告、诊断书等</p>
                </button>
                <button
                  onClick={() => setInputMode('verbal')}
                  className="p-6 border-2 border-gray-200 rounded-xl hover:border-primary hover:bg-primary/5 transition group"
                >
                  <Keyboard className="w-12 h-12 text-gray-400 group-hover:text-primary mx-auto mb-3 transition" />
                  <h4 className="font-bold text-gray-800 mb-1">口述情况</h4>
                  <p className="text-xs text-gray-500">用您的话描述孩子</p>
                </button>
              </div>
            )}

            {/* 上传报告模式 */}
            {inputMode === 'report' && (
              <div className="space-y-4 animate-in fade-in">
                {!reportFile && (
                  <>
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-gray-800">上传医疗报告</h4>
                      <button
                        onClick={() => {
                          setInputMode('none');
                          setReportFile(null);
                          setReportImageUrl('');
                          setOcrResult('');
                          setChildDiagnosis('');
                        }}
                        className="text-sm text-gray-500 hover:text-gray-700"
                      >
                        <X className="w-5 h-5" />
                      </button>
                    </div>

                    <input
                      type="file"
                      ref={fileInputRef}
                      onChange={handleFileSelect}
                      className="hidden"
                      accept=".jpg,.jpeg,.png,.gif,.webp,.pdf,.txt"
                    />

                    <div
                      onClick={() => !isAnalyzing && fileInputRef.current?.click()}
                      className={`border-2 border-dashed rounded-xl p-8 text-center transition ${isAnalyzing ? 'border-gray-300 bg-gray-50 cursor-not-allowed' : 'border-gray-300 hover:border-primary hover:bg-primary/5 cursor-pointer'
                        }`}
                    >
                      {isAnalyzing ? (
                        <div className="flex flex-col items-center">
                          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mb-3"></div>
                          <p className="text-gray-600 font-medium">AI 正在分析报告...</p>
                          <p className="text-xs text-gray-400 mt-1">正在提取文字并生成画像</p>
                        </div>
                      ) : (
                        <div>
                          <Upload className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                          <p className="text-gray-700 font-medium mb-1">点击上传报告图片</p>
                          <p className="text-xs text-gray-400">支持 JPG、PNG 格式</p>
                        </div>
                      )}
                    </div>
                  </>
                )}

                {/* 分析结果展示 - 竖向排列 */}
                {reportFile && (ocrResult || childDiagnosis) && (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <h4 className="font-bold text-gray-800">分析结果</h4>
                      <button
                        onClick={() => {
                          setReportFile(null);
                          setReportImageUrl('');
                          setOcrResult('');
                          setReportSummary('');
                          setChildDiagnosis('');
                        }}
                        className="text-sm text-red-500 hover:text-red-700 flex items-center"
                      >
                        <X className="w-4 h-4 mr-1" />
                        重新上传
                      </button>
                    </div>

                    <div className="space-y-4">
                      {/* 报告摘要 */}
                      {reportSummary && (
                        <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
                          <h5 className="text-sm font-bold text-purple-700 mb-3 flex items-center">
                            <Sparkles className="w-4 h-4 mr-2" />
                            报告摘要
                          </h5>
                          <div className="bg-white rounded-lg p-3 text-sm text-gray-700 leading-relaxed">
                            {reportSummary}
                          </div>
                        </div>
                      )}

                      {/* 报告原图 */}
                      <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                        <h5 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
                          <FileText className="w-4 h-4 mr-2 text-blue-600" />
                          报告原图
                        </h5>
                        {reportImageUrl && (
                          <img
                            src={reportImageUrl}
                            alt="报告原图"
                            className="w-full rounded-lg border border-gray-300 cursor-pointer hover:opacity-90 transition"
                            onClick={() => window.open(reportImageUrl, '_blank')}
                          />
                        )}
                        <p className="text-xs text-gray-400 mt-2 text-center">点击查看大图</p>
                      </div>

                      {/* OCR 提取结果 */}
                      <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
                        <h5 className="text-sm font-bold text-blue-700 mb-3 flex items-center">
                          <Eye className="w-4 h-4 mr-2" />
                          文字提取
                        </h5>
                        <div className="bg-white rounded-lg p-3 max-h-80 overflow-y-auto text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
                          {ocrResult || '提取中...'}
                        </div>
                      </div>

                      {/* 孩子画像 */}
                      <div className="bg-green-50 rounded-xl p-4 border border-green-200">
                        <h5 className="text-sm font-bold text-green-700 mb-3 flex items-center">
                          <User className="w-4 h-4 mr-2" />
                          {name}的画像
                        </h5>
                        <div className="bg-white rounded-lg p-3 text-sm text-gray-700 leading-relaxed">
                          {childDiagnosis || '生成中...'}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 口述情况模式 */}
            {inputMode === 'verbal' && (
              <div className="space-y-4 animate-in fade-in">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-gray-800">描述{name}的情况</h4>
                  <button
                    onClick={() => {
                      setInputMode('none');
                      setVerbalInput('');
                      setChildDiagnosis('');
                    }}
                    className="text-sm text-gray-500 hover:text-gray-700"
                  >
                    <X className="w-5 h-5" />
                  </button>
                </div>

                <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 text-sm text-gray-700">
                  <p className="mb-2"><span className="font-medium">您可以描述：</span></p>
                  <ul className="space-y-1 text-xs text-gray-600 ml-4">
                    <li>• 孩子的社交互动特点（如眼神接触、与人互动的方式）</li>
                    <li>• 沟通表达能力（语言发展、非语言沟通）</li>
                    <li>• 行为模式（重复行为、特殊兴趣、日常习惯）</li>
                    <li>• 感觉处理特点（对声音、光线、触觉的反应）</li>
                    <li>• 优势和挑战（擅长的领域、需要支持的方面）</li>
                  </ul>
                </div>

                <textarea
                  value={verbalInput}
                  onChange={(e) => setVerbalInput(e.target.value)}
                  placeholder={`例如：${name}今年${new Date().getFullYear() - new Date(birthDate).getFullYear()}岁，平时比较喜欢独自玩耍，对旋转的物体特别感兴趣。语言表达还比较少，但能听懂简单的指令。对声音比较敏感，听到突然的响声会捂耳朵...`}
                  rows={8}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary focus:border-transparent transition resize-none"
                />

                <button
                  onClick={handleVerbalAnalysis}
                  disabled={!verbalInput.trim() || isAnalyzing}
                  className="w-full py-3 bg-primary text-white rounded-xl font-medium hover:bg-primary/90 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                      AI 分析中...
                    </>
                  ) : (
                    <>
                      <Sparkles className="w-5 h-5 mr-2" />
                      生成孩子画像
                    </>
                  )}
                </button>

                {childDiagnosis && (
                  <div className="bg-green-50 border border-green-200 rounded-xl p-4 animate-in fade-in">
                    <div className="flex items-center mb-3">
                      <CheckCircle2 className="w-5 h-5 text-green-600 mr-2" />
                      <span className="font-bold text-green-800">AI 分析结果 - {name}的画像</span>
                    </div>
                    <div className="bg-white rounded-lg p-4 max-h-64 overflow-y-auto text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {childDiagnosis}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* 按钮组 */}
            <div className="flex gap-3 pt-4">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition flex items-center"
              >
                <ChevronLeft className="w-5 h-5 mr-1" />
                上一步
              </button>

              {inputMode === 'none' && (
                <button
                  onClick={handleSubmit}
                  className="flex-1 py-3 bg-gray-200 text-gray-600 rounded-xl font-medium hover:bg-gray-300 transition"
                >
                  跳过此步骤
                </button>
              )}

              <button
                onClick={handleSubmit}
                disabled={!canSubmit}
                className={`flex-1 py-3 rounded-xl font-medium transition ${canSubmit
                  ? 'bg-gradient-to-r from-primary to-secondary text-white hover:shadow-lg'
                  : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
              >
                {childDiagnosis ? '完成并开始使用' : '开始使用'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const PageAIChat = ({
  navigateTo,
  onStartGame,
  onProfileUpdate,
  profileContext,
  childProfile
}: {
  navigateTo: (p: Page) => void,
  onStartGame: (id: string) => void,
  onProfileUpdate: (u: ProfileUpdate) => void,
  profileContext: string, // Passed from App parent
  childProfile: ChildProfile | null
}) => {
  // 从 localStorage 加载聊天历史
  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    return chatStorageService.getChatHistory();
  });

  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [voiceMode, setVoiceMode] = useState(false); // 语音模式开关
  const [recognizing, setRecognizing] = useState(false); // 识别中状态
  const [showNoSpeechToast, setShowNoSpeechToast] = useState(false); // 显示"未识别到文字"提示
  const [pendingFile, setPendingFile] = useState<File | null>(null); // 待发送文件
  const [previewUrl, setPreviewUrl] = useState<string | null>(null); // 预览URL

  const [checkInStep, setCheckInStep] = useState(0);
  const [targetGameId, setTargetGameId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 保存聊天历史到 localStorage
  useEffect(() => {
    chatStorageService.saveChatHistory(messages);
  }, [messages]);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  // 处理语音按钮长按开始
  const handleVoiceStart = async () => {
    if (!voiceMode) return;

    try {
      setIsRecording(true);
      await speechService.startRecording();
      console.log('[Voice] 开始录音');
    } catch (error) {
      console.error('[Voice] 录音失败:', error);
      alert(error instanceof Error ? error.message : '录音失败');
      setIsRecording(false);
    }
  };

  // 处理语音按钮松开
  const handleVoiceEnd = async () => {
    if (!voiceMode || !isRecording) return;

    setIsRecording(false);
    setRecognizing(true);

    try {
      console.log('[Voice] 停止录音，开始识别...');
      const result = await speechService.recordAndRecognize();

      if (result.success && result.text) {
        console.log('[Voice] 识别成功:', result.text);
        // 自动发送识别结果
        await handleSend(result.text);
      } else {
        console.error('[Voice] 识别失败:', result.error);
        // 显示淡淡的提示
        setShowNoSpeechToast(true);
        setTimeout(() => setShowNoSpeechToast(false), 800);
      }
    } catch (error) {
      console.error('[Voice] 处理失败:', error);
      // 显示淡淡的提示
      setShowNoSpeechToast(true);
      setTimeout(() => setShowNoSpeechToast(false), 800);
    } finally {
      setRecognizing(false);
    }
  };

  // 切换语音模式
  const toggleVoiceMode = () => {
    setVoiceMode(!voiceMode);
    setIsRecording(false);
    setRecognizing(false);
  };

  const startCheckInFlow = (game: Game) => {
    console.log('[Check-In Flow] 直接跳转到游戏页面:', game.title);

    // 直接记录一条 AI 消息并跳转
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: 'model',
      text: `收到！准备和孩子一起玩 **${game.title}** 吧，正在为您加载...`,
      timestamp: new Date()
    }]);

    // 延迟一秒跳转，让用户看一眼消息，体验更平滑
    setTimeout(() => {
      onStartGame(game.id);
    }, 800);
  };

  const clearPendingFile = () => {
    if (previewUrl && previewUrl !== 'VIDEO_ICON') URL.revokeObjectURL(previewUrl);
    setPendingFile(null);
    setPreviewUrl(null);
  };

  const handleSend = async (textOverride?: string) => {
    const textToSend = textOverride || input;
    if (!textToSend.trim() && !pendingFile) return;

    // 如果有待发送文件，走多模态路径
    if (pendingFile) {
      const file = pendingFile;
      const prompt = textToSend || "请分析这张图片/视频。";

      // 显示用户发送的消息
      const userMsg: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        text: textToSend ? `[文件] ${textToSend}` : "[文件]",
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMsg]);

      clearPendingFile();
      setInput('');
      setLoading(true);

      try {
        const category = fileUploadService.categorizeFile(file);
        let result;
        if (category === 'image') {
          result = await multimodalService.parseImage(file, prompt);
        } else {
          result = await multimodalService.parseVideo(file, prompt);
        }

        if (result.success) {
          const replyText = `**${category === 'image' ? '📸' : '🎬'} 分析完成**\n\n${result.content}`;
          setMessages(prev => [...prev, {
            id: (Date.now() + 1).toString(),
            role: 'model',
            text: replyText,
            timestamp: new Date()
          }]);
        } else {
          throw new Error(result.error);
        }
      } catch (err) {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: 'model',
          text: `❌ 分析失败: ${err instanceof Error ? err.message : '未知错误'}`,
          timestamp: new Date()
        }]);
      } finally {
        setLoading(false);
      }
      return;
    }

    const userMsg: ChatMessage = { id: Date.now().toString(), role: 'user', text: textToSend, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');

    // (原 Check-In Step 拦截逻辑已移除，改为直接直达模式)

    setLoading(true);

    // 捕获当前的 childProfile 值，避免闭包问题
    const currentChildProfile = childProfile;

    // 辅助函数：获取最近的对话历史（最多5轮）
    const getConversationHistory = () => {
      const recentMessages = messages.slice(-10); // 最近10条消息（5轮对话）
      return recentMessages
        .map(msg => `${msg.role === 'user' ? '用户' : 'AI'}: ${msg.text}`)
        .join('\n');
    };

    // 创建一个临时消息用于流式更新
    const tempMsgId = (Date.now() + 1).toString();
    const tempMsg: ChatMessage = {
      id: tempMsgId,
      role: 'model',
      text: '',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, tempMsg]);

    try {
      // *** 使用 Qwen 流式对话 ***
      let fullResponse = '';
      let toolCallsReceived: any[] = [];

      await sendQwenMessage(textToSend, messages, profileContext, {
        onContent: (chunk) => {
          // 实时更新消息内容
          fullResponse += chunk;
          setMessages(prev =>
            prev.map(msg =>
              msg.id === tempMsgId
                ? { ...msg, text: fullResponse }
                : msg
            )
          );
        },
        onToolCall: (toolCall) => {
          // 辅助函数：获取对话历史（JSON 安全版本）
          const getConversationHistory = () => {
            return messages
              .slice(-10) // 取最近10轮对话（增加到10轮，确保包含之前的推荐）
              .map(msg => {
                // 清理文本，但保留游戏方向名称
                let cleanText = msg.text
                  .replace(/:::TOOL_CALL_START:::.*?:::TOOL_CALL_END:::/gs, '') // 移除工具调用标记
                  .replace(/:::GAME_RECOMMENDATION:.*?:::/gs, '') // 移除游戏推荐标记
                  .replace(/:::GAME_IMPLEMENTATION_PLAN:.*?:::/gs, '') // 移除实施方案标记
                  .replace(/:::INTEREST_ANALYSIS:.*?:::/gs, '') // 移除兴趣分析标记
                  .replace(/💡[^💡🎯📍\n]+/g, '') // 移除 analysis 总结（保留游戏方向）
                  .replace(/\n+/g, ' ') // 将换行符替换为空格
                  .replace(/\s+/g, ' ') // 合并多个空格
                  .trim();

                // 限制长度（但不要太短，确保包含游戏方向名称）
                if (cleanText.length > 500) {
                  cleanText = cleanText.substring(0, 500) + '...';
                }

                return `${msg.role === 'user' ? '用户' : 'AI'}: ${cleanText}`;
              })
              .join('\\n'); // 使用转义的换行符
          };

          // 处理 Function Call
          console.log('Tool called:', toolCall);
          toolCallsReceived.push(toolCall);

          try {
            // 尝试解析工具参数
            let args;
            try {
              args = JSON.parse(toolCall.function.arguments);
            } catch (parseError) {
              console.error('❌ Failed to parse tool arguments:', parseError);
              console.log('🔧 Tool name:', toolCall.function.name);
              console.log('📄 Raw arguments (first 500 chars):', toolCall.function.arguments.substring(0, 500));
              console.log('📄 Raw arguments (around position 493):', toolCall.function.arguments.substring(480, 510));

              // 尝试修复常见的 JSON 错误
              let fixedArgs = toolCall.function.arguments;

              // 1. 移除尾随逗号
              fixedArgs = fixedArgs.replace(/,(\s*[}\]])/g, '$1');

              // 2. 移除注释
              fixedArgs = fixedArgs.replace(/\/\/.*$/gm, '');
              fixedArgs = fixedArgs.replace(/\/\*[\s\S]*?\*\//g, '');

              // 3. 再次尝试解析
              try {
                args = JSON.parse(fixedArgs);
                console.log('✓ JSON 修复成功');
              } catch (secondError) {
                console.error('❌ JSON 修复失败:', secondError);
                console.log('💾 Fixed args (first 500 chars):', fixedArgs.substring(0, 500));

                // 显示错误信息给用户
                fullResponse += `\n\n抱歉，工具调用参数格式错误。这可能是因为对话历史中包含特殊字符。请尝试重新开始对话。`;
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === tempMsgId
                      ? { ...msg, text: fullResponse }
                      : msg
                  )
                );
                return; // 跳过此工具调用
              }
            }

            switch (toolCall.function.name) {
              case 'analyze_interest':
                // 步骤1：兴趣分析
                (async () => {
                  try {
                    console.log('[Tool Call] 兴趣分析...', args);

                    fullResponse += `\n\n:::TOOL_CALL_START:::${JSON.stringify({
                      tool: 'analyze_interest',
                      status: 'running',
                      params: args
                    })}:::TOOL_CALL_END:::\n`;

                    fullResponse += `🔍 正在分析${currentChildProfile?.name || '孩子'}的兴趣维度...`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );

                    const { analyzeInterestDimensions } = await import('./services/gameRecommendConversationalAgent');
                    const { calculateDimensionMetrics } = await import('./services/historicalDataHelper');
                    const { getLatestAssessment } = await import('./services/assessmentStorage');

                    if (!currentChildProfile) {
                      fullResponse = fullResponse.replace(/🔍 正在分析.*?兴趣维度\.\.\./, '');
                      fullResponse += `\n\n需要先完善孩子的档案信息才能推荐游戏哦。`;
                      setMessages(prev =>
                        prev.map(msg =>
                          msg.id === tempMsgId
                            ? { ...msg, text: fullResponse }
                            : msg
                        )
                      );
                      return;
                    }

                    const latestAssessment = getLatestAssessment();
                    const recentBehaviors = behaviorStorageService.getRecentBehaviors(20);
                    const dimensionMetrics = calculateDimensionMetrics(recentBehaviors);

                    // TODO: 加入最近游戏实施情况（recentGamePlans），传给 agent 并存入 sessionStorage
                    // 保存上下文到 sessionStorage
                    const interestAnalysisContext = {
                      childProfile: currentChildProfile,
                      latestAssessment,
                      recentBehaviors,
                      dimensionMetrics,
                      timestamp: Date.now()
                    };
                    sessionStorage.setItem('interest_analysis_context', JSON.stringify(interestAnalysisContext));

                    const result = await analyzeInterestDimensions(
                      currentChildProfile,
                      latestAssessment,
                      dimensionMetrics,
                      recentBehaviors,
                      args.parentContext || ''
                    );

                    // 保存结果到 sessionStorage
                    sessionStorage.setItem('interest_analysis_result', JSON.stringify(result));

                    // 更新工具调用状态
                    fullResponse = fullResponse.replace(
                      /:::TOOL_CALL_START:::.*?"status":"running".*?:::TOOL_CALL_END:::/s,
                      (match) => {
                        const toolData = JSON.parse(match.replace(':::TOOL_CALL_START:::', '').replace(':::TOOL_CALL_END:::', ''));
                        toolData.status = 'success';
                        return `:::TOOL_CALL_START:::${JSON.stringify(toolData)}:::TOOL_CALL_END:::`;
                      }
                    );
                    fullResponse = fullResponse.replace(/🔍 正在分析.*?兴趣维度\.\.\./, '');

                    // 展示分析结果
                    fullResponse += `\n\n📊 **${currentChildProfile.name}的兴趣维度分析**\n\n`;
                    fullResponse += `${result.summary}\n\n`;

                    // 展示维度分类
                    const dimLabel = (d: string) => getDimensionConfig(d).label;
                    if (result.leverageDimensions.length > 0) {
                      fullResponse += `✅ **可利用的维度**（孩子已有兴趣）：${result.leverageDimensions.map(dimLabel).join('、')}\n`;
                    }
                    if (result.exploreDimensions.length > 0) {
                      fullResponse += `🔍 **可探索的维度**（有潜力发展）：${result.exploreDimensions.map(dimLabel).join('、')}\n`;
                    }
                    if (result.avoidDimensions.length > 0) {
                      fullResponse += `⚠️ **暂时避免的维度**：${result.avoidDimensions.map(dimLabel).join('、')}\n`;
                    }

                    // 展示干预建议
                    fullResponse += `\n💡 **干预建议**：\n`;
                    result.interventionSuggestions.forEach((s, idx) => {
                      const strategyLabel = s.strategy === 'leverage' ? '利用兴趣' : '探索拓展';
                      fullResponse += `\n${idx + 1}. **${getDimensionConfig(s.targetDimension).label}**（${strategyLabel}）\n`;
                      fullResponse += `   ${s.suggestion}\n`;
                      fullResponse += `   📌 ${s.rationale}\n`;
                    });

                    fullResponse += `\n您想从哪些维度入手？可以告诉我想用的策略（利用已有兴趣/探索新维度/混合）。`;

                    // 嵌入兴趣分析卡片标记
                    fullResponse += `\n\n:::INTEREST_ANALYSIS:${JSON.stringify(result)}:::`;

                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  } catch (error) {
                    console.error('[Tool Call] 兴趣分析失败:', error);
                    fullResponse = fullResponse.replace(/🔍 正在分析.*?兴趣维度\.\.\./, '');
                    fullResponse += `\n\n兴趣分析时出现错误，请稍后重试。`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  }
                })();
                break;

              case 'plan_floor_game':
                // 步骤2：生成地板游戏计划
                (async () => {
                  try {
                    console.log('[Tool Call] 生成地板游戏计划...', args);

                    fullResponse += `\n\n:::TOOL_CALL_START:::${JSON.stringify({
                      tool: 'plan_floor_game',
                      status: 'running',
                      params: args
                    })}:::TOOL_CALL_END:::\n`;

                    fullResponse += `\n✨ 正在设计游戏方案...`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );

                    // 从 sessionStorage 读取上下文
                    const contextStr = sessionStorage.getItem('interest_analysis_context');
                    if (!contextStr || !currentChildProfile) {
                      fullResponse = fullResponse.replace('✨ 正在设计游戏方案...', '');
                      fullResponse += `\n\n请先进行兴趣分析后再生成游戏方案。`;
                      setMessages(prev =>
                        prev.map(msg =>
                          msg.id === tempMsgId
                            ? { ...msg, text: fullResponse }
                            : msg
                        )
                      );
                      return;
                    }

                    const context = JSON.parse(contextStr);

                    // 从兴趣分析结果中提取 specificObjects
                    let specificObjects: Record<string, string[]> | undefined;
                    const resultStr = sessionStorage.getItem('interest_analysis_result');
                    if (resultStr) {
                      try {
                        const analysisResult = JSON.parse(resultStr);
                        if (analysisResult.dimensions) {
                          specificObjects = {};
                          for (const dim of analysisResult.dimensions) {
                            if (dim.specificObjects?.length > 0) {
                              specificObjects[dim.dimension] = dim.specificObjects;
                            }
                          }
                        }
                      } catch (e) {
                        console.warn('Failed to parse interest_analysis_result:', e);
                      }
                    }

                    const { generateFloorGamePlan } = await import('./services/gameRecommendConversationalAgent');

                    const plan = await generateFloorGamePlan(
                      currentChildProfile,
                      context.latestAssessment,
                      args.targetDimensions,
                      args.strategy,
                      context.recentBehaviors || [],
                      args.parentPreferences,
                      getConversationHistory(),
                      specificObjects
                    );

                    // 更新工具调用状态
                    fullResponse = fullResponse.replace(
                      /:::TOOL_CALL_START:::.*?"status":"running".*?:::TOOL_CALL_END:::/s,
                      (match) => {
                        const toolData = JSON.parse(match.replace(':::TOOL_CALL_START:::', '').replace(':::TOOL_CALL_END:::', ''));
                        toolData.status = 'success';
                        return `:::TOOL_CALL_START:::${JSON.stringify(toolData)}:::TOOL_CALL_END:::`;
                      }
                    );
                    fullResponse = fullResponse.replace('✨ 正在设计游戏方案...', '');

                    if (plan._analysis) {
                      fullResponse += `\n\n💡 ${plan._analysis}\n`;
                    }

                    fullResponse += `\n太棒了！我为${currentChildProfile.name}设计了"${plan.gameTitle}"：\n\n`;
                    fullResponse += `📝 **游戏概要**\n${plan.summary}\n\n`;
                    fullResponse += `🎯 **游戏目标**\n${plan.goal}\n\n`;
                    fullResponse += `📋 **游戏步骤**\n`;
                    plan.steps.forEach((step) => {
                      fullResponse += `\n**${step.stepTitle}**\n`;
                      fullResponse += `${step.instruction}\n`;
                    });

                    fullResponse += `\n如果您觉得这个方案合适，我们就可以开始游戏了！\n\n`;

                    // 构建 FloorGame 对象并持久化
                    const floorGame: FloorGame = {
                      id: plan.gameId,
                      gameTitle: plan.gameTitle,
                      summary: plan.summary,
                      goal: plan.goal,
                      steps: plan.steps.map(s => ({
                        stepTitle: s.stepTitle,
                        instruction: s.instruction
                      })),
                      materials: plan.materials || [],
                      _analysis: plan._analysis,
                      status: 'pending',
                      dtstart: new Date().toISOString(),
                      dtend: '',
                      isVR: false
                    };
                    floorGameStorageService.saveGame(floorGame);

                    // 异步生成步骤示意图（fire-and-forget，不阻塞游戏创建）
                    void (async () => {
                      try {
                        const { generateAndSaveStepImages } = await import('./services/stepImageService');
                        await generateAndSaveStepImages(floorGame.id, floorGame.gameTitle, floorGame.steps);
                      } catch (err) {
                        console.warn('[App] Background image generation error:', err);
                      }
                    })();

                    // 构建一个 Game 对象用于游戏卡片（UI 兼容）
                    const gameForCard = {
                      id: plan.gameId,
                      title: plan.gameTitle,
                      target: plan.goal,
                      duration: '15-20分钟',
                      reason: plan.summary,
                      isVR: false,
                      steps: plan.steps.map(s => ({
                        instruction: s.instruction,
                        guidance: s.instruction  // 地板游戏中，指令本身就是指导
                      })),
                      summary: plan.summary,
                      materials: []
                    };

                    fullResponse += `:::GAME_IMPLEMENTATION_PLAN:${JSON.stringify({ game: gameForCard, plan })}:::`;

                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  } catch (error) {
                    console.error('[Tool Call] 生成游戏计划失败:', error);
                    fullResponse = fullResponse.replace('✨ 正在设计游戏方案...', '');
                    fullResponse += `\n\n生成游戏方案时出现错误，请稍后重试。`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  }
                })();
                break;

              case 'log_behavior':
                // 调用行为分析Agent
                (async () => {
                  try {
                    console.log('[行为记录] 开始分析行为...', args);

                    // 添加工具调用卡片标记
                    fullResponse += `\n\n:::TOOL_CALL_START:::${JSON.stringify({
                      tool: 'log_behavior',
                      status: 'running',
                      params: args
                    })}:::TOOL_CALL_END:::\n`;

                    // 添加加载提示
                    fullResponse += `\n\n🔍 正在分析行为并关联兴趣维度...`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );

                    // 调用行为分析Agent
                    const { analyzeBehavior } = await import('./services/behaviorAnalysisAgent');

                    // 获取对话上下文（最近3轮对话）
                    const recentContext = messages
                      .slice(-6) // 最近6条消息（3轮对话）
                      .map(msg => `${msg.role === 'user' ? '家长' : 'AI'}: ${msg.text}`)
                      .join('\n');

                    const behaviorAnalysis = await analyzeBehavior(
                      args.behaviorDescription,
                      currentChildProfile || undefined,
                      recentContext
                    );

                    console.log('[行为记录] 分析完成:', behaviorAnalysis);

                    // 通过 ProfileUpdate 统一处理（会自动保存到数据库并更新档案）
                    onProfileUpdate({
                      source: 'CHAT',
                      interestUpdates: [behaviorAnalysis],
                      abilityUpdates: []
                    });

                    // 获取最新保存的行为ID（最后一条记录）
                    const allBehaviors = behaviorStorageService.getAllBehaviors();
                    const latestBehaviorId = allBehaviors.length > 0 ? allBehaviors[0].id : null;

                    // 为了兼容旧的卡片格式，构造 tags 数组
                    const tags = behaviorAnalysis.matches.map(m => m.dimension);
                    const cardData = {
                      behavior: behaviorAnalysis.behavior,
                      tags: tags,
                      analysis: behaviorAnalysis.matches[0]?.reasoning || '行为已记录',
                      behaviorId: latestBehaviorId
                    };

                    // 更新工具调用状态为成功
                    fullResponse = fullResponse.replace(
                      /:::TOOL_CALL_START:::.*?"tool":"log_behavior".*?"status":"running".*?:::TOOL_CALL_END:::/s,
                      (match) => {
                        const toolData = JSON.parse(match.replace(':::TOOL_CALL_START:::', '').replace(':::TOOL_CALL_END:::', ''));
                        toolData.status = 'success';
                        return `:::TOOL_CALL_START:::${JSON.stringify(toolData)}:::TOOL_CALL_END:::`;
                      }
                    );

                    // 移除加载提示
                    fullResponse = fullResponse.replace('🔍 正在分析行为并关联兴趣维度...', '');

                    // 添加行为记录卡片
                    fullResponse += `\n\n:::BEHAVIOR_LOG_CARD:${JSON.stringify(cardData)}:::`;

                    // 构建工具结果摘要，供 chatbot 继续对话
                    const dimensionNames = behaviorAnalysis.matches.map(m => {
                      const config = getDimensionConfig(m.dimension);
                      return config.label;
                    }).join('、');

                    const strongestMatch = behaviorAnalysis.matches.reduce((prev, current) =>
                      (current.weight > prev.weight) ? current : prev
                    );

                    const toolResultSummary = `帮你记录下来孩子新的行为啦：${behaviorAnalysis.behavior}`;

                    fullResponse += toolResultSummary;

                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  } catch (error) {
                    console.error('[行为记录] 分析失败:', error);

                    // 更新工具调用状态为失败
                    fullResponse = fullResponse.replace(
                      /:::TOOL_CALL_START:::.*?"tool":"log_behavior".*?"status":"running".*?:::TOOL_CALL_END:::/s,
                      (match) => {
                        const toolData = JSON.parse(match.replace(':::TOOL_CALL_START:::', '').replace(':::TOOL_CALL_END:::', ''));
                        toolData.status = 'error';
                        toolData.error = error instanceof Error ? error.message : '未知错误';
                        return `:::TOOL_CALL_START:::${JSON.stringify(toolData)}:::TOOL_CALL_END:::`;
                      }
                    );

                    fullResponse = fullResponse.replace('🔍 正在分析行为并关联兴趣维度...', '');
                    fullResponse += `\n\n❌ 行为分析失败：${error instanceof Error ? error.message : '未知错误'}`;

                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  }
                })();
                break;


              case 'navigate_page':
                // 添加工具调用卡片标记
                fullResponse += `\n\n:::TOOL_CALL_START:::${JSON.stringify({
                  tool: 'navigate_page',
                  status: 'success',
                  params: args
                })}:::TOOL_CALL_END:::\n`;

                // 添加导航卡片
                fullResponse += `\n\n:::NAVIGATION_CARD:${JSON.stringify(args)}:::`;
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === tempMsgId
                      ? { ...msg, text: fullResponse }
                      : msg
                  )
                );
                break;

              case 'generate_assessment':
                // 调用综合评估Agent
                (async () => {
                  try {
                    console.log('[综合评估] 开始生成评估报告...');

                    // 添加工具调用卡片标记
                    fullResponse += `\n\n:::TOOL_CALL_START:::${JSON.stringify({
                      tool: 'generate_assessment',
                      status: 'running',
                      params: args
                    })}:::TOOL_CALL_END:::\n`;

                    // 添加加载提示
                    fullResponse += `\n\n🔄 正在生成综合评估报告，请稍候...`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );

                    // 获取历史数据
                    const historicalData = collectHistoricalData();

                    // 使用外层已捕获的 currentChildProfile
                    if (!currentChildProfile) {
                      throw new Error('未找到孩子档案，请先完成初始设置');
                    }

                    // 调用综合评估Agent
                    const assessment = await generateComprehensiveAssessment(
                      currentChildProfile,
                      historicalData
                    );

                    console.log('[综合评估] 评估完成:', assessment);

                    // 保存评估结果到 assessmentStorage
                    saveAssessment(assessment);

                    // 同时将评估结果保存为 Report 到 reportStorage
                    const assessmentReport: Report = {
                      id: assessment.id,
                      summary: assessment.summary,
                      diagnosis: assessment.currentProfile,
                      nextStepSuggestion: assessment.nextStepSuggestion,
                      date: new Date().toISOString().split('T')[0],
                      type: 'ai_generated',
                      createdAt: assessment.timestamp
                    };
                    reportStorageService.saveReport(assessmentReport);
                    console.log('[综合评估] 已保存为报告:', assessmentReport.id);

                    // 更新工具调用状态为成功
                    fullResponse = fullResponse.replace(
                      /:::TOOL_CALL_START:::.*?"tool":"generate_assessment".*?"status":"running".*?:::TOOL_CALL_END:::/s,
                      (match) => {
                        const toolData = JSON.parse(match.replace(':::TOOL_CALL_START:::', '').replace(':::TOOL_CALL_END:::', ''));
                        toolData.status = 'success';
                        return `:::TOOL_CALL_START:::${JSON.stringify(toolData)}:::TOOL_CALL_END:::`;
                      }
                    );

                    // 移除加载提示，添加评估结果卡片
                    fullResponse = fullResponse.replace('🔄 正在生成综合评估报告，请稍候...', '');
                    fullResponse += `\n\n:::ASSESSMENT_CARD:${JSON.stringify(assessment)}:::`;

                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  } catch (error) {
                    console.error('[综合评估] 生成失败:', error);

                    // 更新工具调用状态为失败
                    fullResponse = fullResponse.replace(
                      /:::TOOL_CALL_START:::.*?"tool":"generate_assessment".*?"status":"running".*?:::TOOL_CALL_END:::/s,
                      (match) => {
                        const toolData = JSON.parse(match.replace(':::TOOL_CALL_START:::', '').replace(':::TOOL_CALL_END:::', ''));
                        toolData.status = 'error';
                        toolData.error = error instanceof Error ? error.message : '未知错误';
                        return `:::TOOL_CALL_START:::${JSON.stringify(toolData)}:::TOOL_CALL_END:::`;
                      }
                    );

                    fullResponse = fullResponse.replace('🔄 正在生成综合评估报告，请稍候...', '');
                    fullResponse += `\n\n❌ 评估报告生成失败：${error instanceof Error ? error.message : '未知错误'}`;
                    setMessages(prev =>
                      prev.map(msg =>
                        msg.id === tempMsgId
                          ? { ...msg, text: fullResponse }
                          : msg
                      )
                    );
                  }
                })();
                break;

              case 'query_child_profile':
                if (currentChildProfile) {
                  const birthDate = new Date(currentChildProfile.birthDate);
                  const now = new Date();
                  let ageYears = now.getFullYear() - birthDate.getFullYear();
                  const monthDiff = now.getMonth() - birthDate.getMonth();
                  if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birthDate.getDate())) {
                    ageYears--;
                  }
                  fullResponse += `\n\n【孩子基础信息】\n`;
                  fullResponse += `姓名：${currentChildProfile.name}\n`;
                  fullResponse += `性别：${currentChildProfile.gender}\n`;
                  fullResponse += `出生日期：${currentChildProfile.birthDate}（${ageYears}岁）\n`;
                  fullResponse += `诊断/画像：${currentChildProfile.diagnosis || '暂无'}\n`;
                  fullResponse += `创建时间：${currentChildProfile.createdAt}\n`;
                } else {
                  fullResponse += `\n\n尚未创建孩子档案。`;
                }
                setMessages(prev =>
                  prev.map(msg =>
                    msg.id === tempMsgId
                      ? { ...msg, text: fullResponse }
                      : msg
                  )
                );
                break;

              case 'query_recent_assessments':
                {
                  const count = args.count || 3;
                  const assessments = getRecentAssessments(count);
                  if (assessments.length > 0) {
                    fullResponse += `\n\n【最近评估记录】（共${assessments.length}条）\n`;
                    assessments.forEach((a, i) => {
                      const date = a.timestamp ? new Date(a.timestamp).toLocaleDateString('zh-CN') : '未知';
                      fullResponse += `${i + 1}. [${date}] 摘要：${a.summary}\n`;
                      fullResponse += `   画像：${a.currentProfile ? a.currentProfile.substring(0, 100) + (a.currentProfile.length > 100 ? '...' : '') : '暂无'}\n`;
                      fullResponse += `   建议：${a.nextStepSuggestion ? a.nextStepSuggestion.substring(0, 100) + (a.nextStepSuggestion.length > 100 ? '...' : '') : '暂无'}\n`;
                    });
                  } else {
                    fullResponse += `\n\n暂无评估记录。`;
                  }
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === tempMsgId
                        ? { ...msg, text: fullResponse }
                        : msg
                    )
                  );
                }
                break;

              case 'query_recent_behaviors':
                {
                  const count = args.count || 10;
                  const behaviors = behaviorStorageService.getRecentBehaviors(count);
                  if (behaviors.length > 0) {
                    fullResponse += `\n\n【最近行为记录】（共${behaviors.length}条）\n`;
                    behaviors.forEach((b, i) => {
                      const date = b.timestamp ? new Date(b.timestamp).toLocaleDateString('zh-CN') : '未知';
                      const dims = b.matches.map(m => `${m.dimension}(${m.intensity >= 0 ? '+' : ''}${m.intensity})`).join(', ');
                      fullResponse += `${i + 1}. [${date}] ${b.behavior} → ${dims}\n`;
                    });
                  } else {
                    fullResponse += `\n\n暂无行为记录。`;
                  }
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === tempMsgId
                        ? { ...msg, text: fullResponse }
                        : msg
                    )
                  );
                }
                break;

              case 'query_floor_games':
                {
                  const count = args.count || 5;
                  const games = floorGameStorageService.getRecentGames(count);
                  if (games.length > 0) {
                    fullResponse += `\n\n【地板游戏记录】（共${games.length}条）\n`;
                    games.forEach((g, i) => {
                      const date = g.dtstart ? new Date(g.dtstart).toLocaleDateString('zh-CN') : '未知';
                      const statusMap: Record<string, string> = { pending: '未开始', completed: '已完成', aborted: '已中止' };
                      const statusText = statusMap[g.status] || g.status;
                      fullResponse += `${i + 1}. [${date}] ${g.gameTitle} - ${statusText}\n`;
                      fullResponse += `   概要：${g.summary ? g.summary.substring(0, 100) + (g.summary.length > 100 ? '...' : '') : '暂无'}\n`;
                      fullResponse += `   目标：${g.goal ? g.goal.substring(0, 100) + (g.goal.length > 100 ? '...' : '') : '暂无'}\n`;
                    });
                  } else {
                    fullResponse += `\n\n暂无地板游戏记录。`;
                  }
                  setMessages(prev =>
                    prev.map(msg =>
                      msg.id === tempMsgId
                        ? { ...msg, text: fullResponse }
                        : msg
                    )
                  );
                }
                break;
            }
          } catch (e) {
            console.error('Failed to parse tool arguments:', e);
          }
        },
        onComplete: (fullText, toolCalls) => {
          console.log('Stream completed:', { fullText, toolCalls });

          // 检查是否有文本格式的工具调用（LLM 没有使用标准 Function Calling）
          const toolCallMatch = fullText.match(/:::TOOL_CALL_START:::([\s\S]*?):::TOOL_CALL_END:::/);
          if (toolCallMatch && toolCalls.length === 0) {
            console.warn('⚠️  检测到文本格式的工具调用，但 toolCalls 为空。');
            console.warn('⚠️  LLM 返回了文本格式的工具调用，而不是标准的 Function Calling。');
            console.warn('⚠️  请检查系统提示词和 tools 配置。');
            try {
              const toolData = JSON.parse(toolCallMatch[1]);
              console.log('解析到的工具调用:', toolData);
            } catch (e) {
              console.error('解析文本格式工具调用失败:', e);
            }
          }

          setLoading(false);
        },
        onError: (error) => {
          console.error('Stream error:', error);
          setMessages(prev =>
            prev.map(msg =>
              msg.id === tempMsgId
                ? { ...msg, text: '抱歉，我遇到了一些问题。请稍后再试。' }
                : msg
            )
          );
          setLoading(false);
        }
      });

    } catch (e) {
      console.error(e);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === tempMsgId
            ? { ...msg, text: '我在听，请继续告诉我互动的细节。' }
            : msg
        )
      );
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 清除之前的预览
    if (previewUrl) URL.revokeObjectURL(previewUrl);

    const category = fileUploadService.categorizeFile(file);

    // 如果是文档，保持原有立即分析逻辑（因其不需要配合Prompt）
    if (category === 'document') {
      setLoading(true);
      try {
        let textContent = file.type === "text/plain" ? await file.text() : `文件名: ${file.name}。假设这是一份医疗评估报告。`;
        const analysis = await api.analyzeReport(textContent);
        onProfileUpdate(analysis);
        const abilityChanges = analysis.abilityUpdates.map(u => `${u.dimension} ${u.scoreChange > 0 ? '+' : ''}${u.scoreChange}`).join('、');
        const replyText = `收到您的报告。我已经分析完毕并更新了孩子档案。\n\n**分析结果：**\n- 发现 ${analysis.interestUpdates.length} 个兴趣点\n- 能力维度调整：${abilityChanges || "无明显变化"}`;
        setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'model', text: replyText, timestamp: new Date() }]);
      } catch (e) {
        setMessages(prev => [...prev, { id: Date.now().toString(), role: 'model', text: `❌ 处理失败: ${e instanceof Error ? e.message : '未知错误'}`, timestamp: new Date() }]);
      } finally {
        setLoading(false);
      }
    } else {
      // 图片和视频进入 Pending 状态供后续组合 Prompt 发送
      setPendingFile(file);
      if (category === 'image') {
        setPreviewUrl(URL.createObjectURL(file));
      } else {
        setPreviewUrl('VIDEO_ICON'); // 视频暂显图标
      }
    }

    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const parseMessageContent = (text: string) => {
    const gameRegex = /:::GAME_RECOMMENDATION:\s*([\s\S]*?)\s*:::/;
    const navRegex = /:::NAVIGATION_CARD:\s*([\s\S]*?)\s*:::/;
    const behaviorRegex = /:::BEHAVIOR_LOG_CARD:\s*([\s\S]*?)\s*:::/;
    const weeklyRegex = /:::WEEKLY_PLAN_CARD:\s*([\s\S]*?)\s*:::/;
    const assessmentRegex = /:::ASSESSMENT_CARD:\s*([\s\S]*?)\s*:::/;
    const interestAnalysisRegex = /:::INTEREST_ANALYSIS:\s*([\s\S]*?)\s*:::/;
    const implementationPlanRegex = /:::GAME_IMPLEMENTATION_PLAN:\s*([\s\S]*?)\s*:::/;
    const toolCallRegex = /:::TOOL_CALL_START:::([\s\S]*?):::TOOL_CALL_END:::/;

    let cleanText = text;
    let card: any = null;

    // Check patterns in priority order, but ensure cleanText removes ALL patterns
    const gameMatch = text.match(gameRegex);
    if (gameMatch?.[1]) { try { card = { ...JSON.parse(gameMatch[1]), type: 'GAME' }; } catch (e) { } }

    const navMatch = text.match(navRegex);
    if (navMatch?.[1] && !card) { try { card = { ...JSON.parse(navMatch[1]), type: 'NAV' }; } catch (e) { } }

    const behaviorMatch = text.match(behaviorRegex);
    if (behaviorMatch?.[1] && !card) { try { card = { ...JSON.parse(behaviorMatch[1]), type: 'BEHAVIOR' }; } catch (e) { } }

    const weeklyMatch = text.match(weeklyRegex);
    if (weeklyMatch?.[1] && !card) { try { card = { ...JSON.parse(weeklyMatch[1]), type: 'WEEKLY' }; } catch (e) { } }

    const assessmentMatch = text.match(assessmentRegex);
    if (assessmentMatch?.[1] && !card) { try { card = { ...JSON.parse(assessmentMatch[1]), type: 'ASSESSMENT' }; } catch (e) { } }

    const interestAnalysisMatch = text.match(interestAnalysisRegex);
    if (interestAnalysisMatch?.[1] && !card) { try { card = { analysis: JSON.parse(interestAnalysisMatch[1]), type: 'INTEREST_ANALYSIS' }; } catch (e) { } }

    const implementationPlanMatch = text.match(implementationPlanRegex);
    if (implementationPlanMatch?.[1] && !card) { try { card = { ...JSON.parse(implementationPlanMatch[1]), type: 'IMPLEMENTATION_PLAN' }; } catch (e) { } }

    const toolCallMatch = text.match(toolCallRegex);
    if (toolCallMatch?.[1] && !card) { try { card = { ...JSON.parse(toolCallMatch[1]), type: 'TOOL_CALL' }; } catch (e) { } }

    cleanText = cleanText
      .replace(gameRegex, '')
      .replace(navRegex, '')
      .replace(behaviorRegex, '')
      .replace(weeklyRegex, '')
      .replace(assessmentRegex, '')
      .replace(interestAnalysisRegex, '')
      .replace(implementationPlanRegex, '')
      .replace(toolCallRegex, '')
      .trim();

    return { cleanText, card };
  };

  return (
    <div className="flex flex-col h-full bg-background relative">
      {/* 未识别到文字的提示 Toast */}
      {showNoSpeechToast && (
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 animate-in fade-in">
          <div className="bg-gray-800/40 text-white px-6 py-3 rounded-2xl shadow-lg backdrop-blur-sm">
            <p className="text-base font-medium">未识别到文字</p>
          </div>
        </div>
      )}

      {/* 清空历史按钮 */}
      {messages.length > 1 && (
        <div className="absolute top-2 right-2 z-10">
          <button
            onClick={() => {
              if (confirm('确定要清空所有聊天记录吗？')) {
                chatStorageService.resetToDefault();
                setMessages(chatStorageService.getChatHistory());
                // 清空游戏推荐相关的 sessionStorage 数据
                sessionStorage.removeItem('interest_analysis_context');
                sessionStorage.removeItem('interest_analysis_result');
                console.log('[SessionStorage] 清空对话时清除游戏推荐数据:', {
                  keys: ['interest_analysis_context', 'interest_analysis_result']
                });
                console.log('[Chat] 已清空对话历史和游戏推荐数据');
              }
            }}
            className="bg-white/90 backdrop-blur-sm text-gray-600 hover:text-red-600 px-3 py-1.5 rounded-full text-xs font-medium shadow-sm border border-gray-200 hover:border-red-300 transition flex items-center"
            title="清空聊天历史"
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            清空
          </button>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-4 space-y-5 pb-32">
        {messages.map((msg) => {
          const { cleanText, card } = parseMessageContent(msg.text);
          return (
            <div key={msg.id} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
              <div className={`max-w-[88%] p-4 rounded-2xl shadow-sm leading-relaxed text-sm ${msg.role === 'user' ? 'bg-primary text-white rounded-br-none' : 'bg-white text-gray-800 rounded-bl-none'}`}>
                {msg.role === 'user' ? cleanText : <ReactMarkdown components={{ strong: ({ node, ...props }) => <span className="font-bold text-gray-900" {...props} /> }}>{cleanText}</ReactMarkdown>}
              </div>
              {msg.options && (
                <div className="mt-3 flex flex-wrap gap-2 animate-in fade-in max-w-[90%]">
                  {msg.options.map((opt, idx) => (
                    <button key={idx} onClick={() => handleSend(opt)} className="bg-white border border-primary/20 text-primary text-xs font-bold px-3 py-2 rounded-full shadow-sm hover:bg-green-50 active:scale-95 transition">{opt}</button>
                  ))}
                </div>
              )}

              {/* 工具调用卡片 */}
              {card && card.type === 'TOOL_CALL' && (
                <div className="mt-2 max-w-[85%] bg-gradient-to-r from-indigo-50 to-purple-50 p-4 rounded-xl border border-indigo-200 shadow-md animate-in fade-in">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Settings className="w-4 h-4 text-indigo-600 animate-spin-slow" />
                      <span className="text-xs font-bold text-indigo-700 uppercase">工具调用</span>
                    </div>
                    <div className={`flex items-center space-x-1 text-xs font-medium px-2 py-1 rounded-full ${card.status === 'running' ? 'bg-yellow-100 text-yellow-700' :
                      card.status === 'success' ? 'bg-green-100 text-green-700' :
                        'bg-red-100 text-red-700'
                      }`}>
                      {card.status === 'running' && <><div className="w-2 h-2 bg-yellow-500 rounded-full animate-pulse"></div><span>执行中</span></>}
                      {card.status === 'success' && <><CheckCircle2 className="w-3 h-3" /><span>成功</span></>}
                      {card.status === 'error' && <><X className="w-3 h-3" /><span>失败</span></>}
                    </div>
                  </div>

                  <div className="bg-white/70 rounded-lg p-3 mb-2">
                    <div className="flex items-center space-x-2 mb-2">
                      <code className="text-xs font-mono text-indigo-900 bg-indigo-100 px-2 py-1 rounded">{card.tool}</code>
                    </div>
                    {card.params && Object.keys(card.params).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-xs text-gray-600 cursor-pointer hover:text-gray-800 flex items-center">
                          <ChevronDown className="w-3 h-3 mr-1" />
                          查看参数
                        </summary>
                        <pre className="mt-2 text-xs bg-gray-50 p-2 rounded overflow-x-auto">
                          {JSON.stringify(card.params, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              )}

              {/* Card Rendering */}
              {card && card.type === 'GAME' && (
                <div className="mt-2 max-w-[85%] bg-white p-3 rounded-xl border-l-4 border-secondary shadow-md animate-in fade-in">
                  <div className="flex items-center space-x-2 mb-2"><Sparkles className="w-4 h-4 text-secondary" /><span className="text-xs font-bold text-secondary uppercase">推荐游戏 (基于分析)</span></div>
                  <h4 className="font-bold text-gray-800 text-lg mb-1">{card.title}</h4>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">{card.reason}</p>
                  <button onClick={() => startCheckInFlow(card)} className="w-full bg-secondary text-white py-2 rounded-lg text-sm font-bold flex items-center justify-center hover:bg-blue-600 transition"><Play className="w-4 h-4 mr-2" /> 开始游戏</button>
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
                <div
                  onClick={() => {
                    if (card.behaviorId) {
                      // 跳转到行为页面
                      navigateTo(Page.BEHAVIORS);
                      // 使用 setTimeout 确保页面已切换，然后触发详情显示
                      setTimeout(() => {
                        const behavior = behaviorStorageService.getAllBehaviors().find(b => b.id === card.behaviorId);
                        if (behavior) {
                          // 触发一个自定义事件来显示详情
                          window.dispatchEvent(new CustomEvent('showBehaviorDetail', { detail: behavior }));
                        }
                      }, 100);
                    }
                  }}
                  className="mt-2 max-w-[85%] bg-white p-4 rounded-xl border border-emerald-100 shadow-md animate-in fade-in cursor-pointer hover:border-emerald-300 hover:shadow-lg transition-all active:scale-98"
                >
                  <div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-100">
                    <div className="flex items-center space-x-2">
                      <div className="bg-emerald-100 p-1.5 rounded-full"><ClipboardCheck className="w-4 h-4 text-emerald-600" /></div>
                      <span className="text-xs font-bold text-emerald-700 uppercase">行为已记录</span>
                    </div>
                    <ArrowUpRight className="w-4 h-4 text-emerald-500" />
                  </div>
                  <div className="mb-3">
                    <p className="text-gray-800 font-bold text-base mb-1">"{card.behavior}"</p>
                    <p className="text-xs text-gray-500">{card.analysis}</p>
                  </div>
                  {card.tags && (
                    <div className="flex flex-wrap gap-1.5">
                      {card.tags.map((t: string, i: number) => {
                        const config = getDimensionConfig(t as InterestDimensionType);
                        return (
                          <span key={i} className={`flex items-center text-[10px] px-2 py-1 rounded-full font-medium ${config.color}`}>
                            <config.icon className="w-3 h-3 mr-1" /> {config.label}
                          </span>
                        );
                      })}
                    </div>
                  )}
                  <div className="mt-3 pt-2 border-t border-gray-100">
                    <p className="text-xs text-gray-400 text-center">点击查看详情</p>
                  </div>
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
              {card && card.type === 'ASSESSMENT' && (
                <div className="mt-2 w-full max-w-[95%] bg-gradient-to-br from-purple-50 to-blue-50 p-5 rounded-2xl border border-purple-200 shadow-lg animate-in fade-in">
                  {/* 标题 */}
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-purple-200">
                    <div className="flex items-center space-x-2">
                      <div className="bg-purple-500 p-2 rounded-full">
                        <Award className="w-5 h-5 text-white" />
                      </div>
                      <span className="font-bold text-gray-800 text-lg">综合评估报告</span>
                    </div>
                    <span className="text-xs bg-purple-500 text-white px-3 py-1 rounded-full font-bold">
                      {new Date(card.timestamp).toLocaleDateString('zh-CN')}
                    </span>
                  </div>

                  {/* 评估摘要 */}
                  <div className="mb-4 bg-white rounded-xl p-4 shadow-sm border-l-4 border-purple-500">
                    <p className="text-sm text-gray-800 font-medium leading-relaxed">{card.summary}</p>
                  </div>

                  {/* 当前画像 */}
                  <div className="mb-4 bg-white rounded-xl p-4 shadow-sm">
                    <div className="flex items-center mb-2">
                      <User className="w-4 h-4 text-purple-600 mr-2" />
                      <h4 className="font-bold text-gray-800">当前画像</h4>
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">{card.currentProfile}</p>
                  </div>

                  {/* 下一步建议 */}
                  <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl p-4 shadow-sm">
                    <div className="flex items-center mb-2">
                      <Lightbulb className="w-4 h-4 text-yellow-300 mr-2" />
                      <h4 className="font-bold">下一步干预建议</h4>
                    </div>
                    <p className="text-sm leading-relaxed whitespace-pre-wrap">{card.nextStepSuggestion}</p>
                  </div>

                  {/* 查看详情按钮 */}
                  <button
                    onClick={() => navigateTo(Page.PROFILE)}
                    className="w-full mt-4 bg-white text-purple-600 py-2.5 rounded-xl font-bold hover:bg-purple-50 transition flex items-center justify-center shadow-sm"
                  >
                    <FileText className="w-4 h-4 mr-2" />
                    在档案页面查看完整报告
                  </button>
                </div>
              )}

              {/* 兴趣分析卡片 */}
              {card && card.type === 'INTEREST_ANALYSIS' && card.analysis && (
                <div className="mt-2 w-full max-w-[95%] bg-gradient-to-br from-purple-50 to-indigo-50 p-5 rounded-2xl border border-purple-200 shadow-lg animate-in fade-in">
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-purple-200">
                    <div className="flex items-center space-x-2">
                      <div className="bg-purple-500 p-2 rounded-full">
                        <Zap className="w-5 h-5 text-white" />
                      </div>
                      <span className="font-bold text-gray-800 text-lg">兴趣维度分析</span>
                    </div>
                    <span className="text-xs bg-purple-500 text-white px-3 py-1 rounded-full font-bold">8维度</span>
                  </div>

                  {/* 维度条形图 */}
                  <div className="mb-4 bg-white rounded-xl p-4 shadow-sm">
                    <h4 className="font-bold text-gray-800 mb-3 text-sm">维度强度 / 探索度</h4>
                    <div className="space-y-2">
                      {card.analysis.dimensions?.map((dim: any, idx: number) => {
                        const categoryColors: Record<string, string> = {
                          leverage: 'bg-green-500',
                          explore: 'bg-blue-500',
                          avoid: 'bg-red-400',
                          neutral: 'bg-gray-400'
                        };
                        const categoryLabels: Record<string, string> = {
                          leverage: '可利用',
                          explore: '可探索',
                          avoid: '避免',
                          neutral: '中性'
                        };
                        return (
                          <React.Fragment key={idx}>
                            <div className="flex items-center gap-2 text-xs">
                              <span className="w-20 text-gray-700 font-medium truncate">{getDimensionConfig(dim.dimension).label}</span>
                              <div className="flex-1 flex items-center gap-1">
                                <div className="flex-1 bg-gray-100 rounded-full h-3 relative overflow-hidden">
                                  <div
                                    className={`h-full rounded-full ${categoryColors[dim.category] || 'bg-gray-400'}`}
                                    style={{ width: `${dim.strength}%` }}
                                  />
                                </div>
                                <span className="w-8 text-right text-gray-500">{dim.strength}</span>
                              </div>
                              <span className={`px-1.5 py-0.5 rounded text-white text-[10px] ${categoryColors[dim.category] || 'bg-gray-400'}`}>
                                {categoryLabels[dim.category] || dim.category}
                              </span>
                            </div>
                            {dim.specificObjects?.length > 0 && (
                              <div className="ml-20 mt-0.5 flex flex-wrap gap-1">
                                {dim.specificObjects.map((obj: string, oi: number) => (
                                  <span key={oi} className="bg-purple-100 text-purple-600 px-1.5 py-0.5 rounded text-[10px]">{obj}</span>
                                ))}
                              </div>
                            )}
                          </React.Fragment>
                        );
                      })}
                    </div>
                  </div>

                  {/* 干预建议按钮 */}
                  {card.analysis.interventionSuggestions?.length > 0 && (
                    <div className="space-y-2">
                      <h4 className="font-bold text-gray-800 text-sm mb-2">💡 干预建议（点击选择）</h4>
                      {card.analysis.interventionSuggestions.map((s: any, idx: number) => (
                        <button
                          key={idx}
                          onClick={() => handleSend(`我想用建议${idx + 1}：从${getDimensionConfig(s.targetDimension).label}维度入手，策略是${s.strategy === 'leverage' ? '利用已有兴趣' : '探索拓展'}`)}
                          className="w-full text-left p-3 bg-white border-2 border-gray-200 rounded-xl hover:border-purple-400 hover:bg-purple-50 transition shadow-sm"
                        >
                          <div className="flex items-center gap-2 mb-1">
                            <span className="bg-purple-100 text-purple-700 px-2 py-0.5 rounded text-xs font-bold">{getDimensionConfig(s.targetDimension).label}</span>
                            <span className="text-xs text-gray-500">{s.strategy === 'leverage' ? '利用兴趣' : '探索拓展'}</span>
                          </div>
                          <p className="text-xs text-gray-700">{s.suggestion}</p>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* 游戏实施方案卡片 */}
              {card && card.type === 'IMPLEMENTATION_PLAN' && card.game && card.plan && (
                <div className="mt-2 w-full max-w-[95%] bg-gradient-to-br from-green-50 to-blue-50 p-5 rounded-2xl border border-green-200 shadow-lg animate-in fade-in">
                  {/* 标题 */}
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-green-200">
                    <div className="flex items-center space-x-2">
                      <div className="bg-green-500 p-2 rounded-full">
                        <Gamepad2 className="w-5 h-5 text-white" />
                      </div>
                      <span className="font-bold text-gray-800 text-lg">{card.plan.gameTitle || card.game.title}</span>
                    </div>
                    <span className="text-xs bg-green-500 text-white px-3 py-1 rounded-full font-bold">实施方案</span>
                  </div>

                  {/* 游戏概要 */}
                  {card.plan.summary && (
                    <div className="mb-4 bg-white rounded-xl p-4 shadow-sm">
                      <h4 className="font-bold text-gray-800 mb-2 flex items-center">
                        <FileText className="w-4 h-4 text-green-600 mr-2" />
                        游戏概要
                      </h4>
                      <p className="text-xs text-gray-700">{card.plan.summary}</p>
                    </div>
                  )}

                  {/* 准备材料 */}
                  {card.plan.materials && card.plan.materials.length > 0 && (
                    <div className="mb-4 bg-white rounded-xl p-4 shadow-sm">
                      <h4 className="font-bold text-gray-800 mb-2 flex items-center">
                        <Package className="w-4 h-4 text-orange-500 mr-2" />
                        准备材料
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {card.plan.materials.map((m: string, idx: number) => (
                          <span key={idx} className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full text-xs font-medium border border-orange-200">
                            {m}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* 游戏目标 */}
                  {card.plan.goal && (
                    <div className="mb-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 shadow-sm border border-blue-200">
                      <h4 className="font-bold text-gray-800 mb-2 flex items-center">
                        <Award className="w-4 h-4 text-blue-600 mr-2" />
                        游戏目标
                      </h4>
                      <p className="text-xs text-gray-700">{card.plan.goal}</p>
                    </div>
                  )}

                  {/* 游戏步骤 */}
                  <div className="mb-4 bg-white rounded-xl p-4 shadow-sm">
                    <h4 className="font-bold text-gray-800 mb-3 flex items-center">
                      <ListOrdered className="w-4 h-4 text-green-600 mr-2" />
                      游戏步骤
                    </h4>
                    <div className="space-y-3">
                      {card.plan.steps && card.plan.steps.map((step: any, idx: number) => (
                        <div key={idx} className="border-l-4 border-green-300 pl-3 pb-2">
                          <div className="mb-1">
                            <span className="font-bold text-sm text-gray-800">{step.stepTitle || step.title}</span>
                          </div>
                          <p className="text-xs text-gray-600 mb-1">{step.instruction}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 开始游戏按钮 */}
                  <button
                    onClick={() => startCheckInFlow(card.game)}
                    className="w-full bg-gradient-to-r from-green-500 to-blue-500 text-white py-3 rounded-xl font-bold hover:shadow-lg transition flex items-center justify-center"
                  >
                    <Play className="w-5 h-5 mr-2" />
                    开始游戏
                  </button>
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

      <div className="bg-white p-4 border-t border-gray-100 relative">
        {/* 文件预览区 */}
        {previewUrl && (
          <div className="absolute top-0 left-0 right-0 -translate-y-full px-4 py-2 bg-white/80 backdrop-blur-sm border-t border-gray-100 flex items-center animate-in slide-in-from-bottom">
            <div className="relative group">
              {previewUrl === 'VIDEO_ICON' ? (
                <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center border-2 border-primary/20">
                  <Camera className="w-8 h-8 text-primary" />
                  <span className="absolute bottom-1 right-1 text-[8px] bg-primary text-white px-1 rounded">VIDEO</span>
                </div>
              ) : (
                <img src={previewUrl} alt="Preview" className="w-16 h-16 object-cover rounded-lg border-2 border-primary/20 shadow-sm" />
              )}
              <button
                onClick={clearPendingFile}
                className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 shadow-md hover:bg-red-600 transition active:scale-90"
              >
                <X className="w-3 h-3" />
              </button>
            </div>
            <div className="ml-4 flex-1">
              <p className="text-xs font-bold text-gray-700">{pendingFile?.name}</p>
              <p className="text-[10px] text-gray-500">{(pendingFile?.size! / 1024 / 1024).toFixed(2)} MB • 等待发送</p>
            </div>
          </div>
        )}

        <div className="flex items-center bg-gray-100 rounded-full px-2 py-2">
          <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.webp,.mp4,.avi,.mov" />

          {!voiceMode ? (
            // 普通输入模式
            <>
              <button onClick={() => fileInputRef.current?.click()} className="p-2 text-gray-500 hover:text-primary transition active:scale-90" title="上传文件/图片/视频"><Paperclip className="w-5 h-5" /></button>
              <input value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === 'Enter' && handleSend()} placeholder="输入消息..." className="flex-1 bg-transparent outline-none text-gray-700 placeholder-gray-400 ml-2" />
              <button onClick={toggleVoiceMode} className="p-2 mr-1 transition rounded-full text-gray-500 hover:text-primary"><Mic className="w-5 h-5" /></button>
              <button onClick={() => handleSend()} className="p-2 bg-primary rounded-full text-white ml-1 hover:bg-green-600 transition shadow-md"><ArrowRight className="w-4 h-4" /></button>
            </>
          ) : (
            // 语音输入模式
            <>
              <button
                onMouseDown={handleVoiceStart}
                onMouseUp={handleVoiceEnd}
                onTouchStart={handleVoiceStart}
                onTouchEnd={handleVoiceEnd}
                disabled={recognizing}
                className={`flex-1 py-1.5 rounded-full font-bold transition transform active:scale-95 flex items-center justify-center ${recognizing
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  : isRecording
                    ? 'bg-red-500 text-white animate-pulse'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
              >
                <Mic className="w-5 h-5 mr-2" />
                {recognizing ? '识别中...' : isRecording ? '松开发送' : '按住说话'}
              </button>
              <button onClick={toggleVoiceMode} className="p-2 ml-2 text-gray-500 hover:text-primary transition" title="切换到键盘输入">
                <Keyboard className="w-5 h-5" />
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

// PageCalendar 已移至 frontend/src/components/CalendarPage.tsx

const PageBehaviors = ({ childProfile }: { childProfile: ChildProfile | null }) => {
  const [behaviors, setBehaviors] = useState<BehaviorAnalysis[]>([]);
  const [filterDimension, setFilterDimension] = useState<string>('全部');
  const [filterSource, setFilterSource] = useState<string>('全部');
  const [stats, setStats] = useState<any>(null);
  const [selectedBehavior, setSelectedBehavior] = useState<BehaviorAnalysis | null>(null);

  // 加载行为数据
  useEffect(() => {
    loadBehaviors();
  }, [filterDimension, filterSource]);

  // 监听从聊天页面跳转过来的事件
  useEffect(() => {
    const handleShowDetail = (event: any) => {
      const behavior = event.detail;
      if (behavior) {
        setSelectedBehavior(behavior);
      }
    };

    window.addEventListener('showBehaviorDetail', handleShowDetail);
    return () => {
      window.removeEventListener('showBehaviorDetail', handleShowDetail);
    };
  }, []);

  const loadBehaviors = () => {
    let allBehaviors = behaviorStorageService.getAllBehaviors();

    // 按维度筛选
    if (filterDimension !== '全部') {
      allBehaviors = allBehaviors.filter(b =>
        b.matches.some(m => m.dimension === filterDimension)
      );
    }

    // 按来源筛选
    if (filterSource !== '全部') {
      allBehaviors = allBehaviors.filter(b => b.source === filterSource);
    }

    setBehaviors(allBehaviors);
    setStats(behaviorStorageService.getStatistics());
  };

  const handleDeleteBehavior = (id: string) => {
    if (confirm('确定要删除这条行为记录吗？')) {
      behaviorStorageService.deleteBehavior(id);
      loadBehaviors();
    }
  };

  const dimensions: InterestDimensionType[] = ['Visual', 'Auditory', 'Tactile', 'Motor', 'Construction', 'Order', 'Cognitive', 'Social'];
  const sources = ['全部', 'GAME', 'REPORT', 'CHAT'];
  const dimensionFilters = ['全部', ...dimensions];

  // 行为详情弹窗
  const BehaviorDetailModal = ({ behavior, onClose }: { behavior: BehaviorAnalysis, onClose: () => void }) => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between rounded-t-2xl">
          <h3 className="font-bold text-gray-800">行为详情</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* 行为描述 */}
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <h5 className="text-sm font-bold text-blue-700 mb-2 flex items-center">
              <Activity className="w-4 h-4 mr-2" />
              行为描述
            </h5>
            <p className="text-sm text-gray-800 leading-relaxed">{behavior.behavior}</p>
          </div>

          {/* 兴趣关联 */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-200">
            <h5 className="text-sm font-bold text-green-700 mb-3 flex items-center">
              <Dna className="w-4 h-4 mr-2" />
              兴趣维度分析
            </h5>
            <div className="space-y-3">
              {behavior.matches.map((match, idx) => {
                const config = getDimensionConfig(match.dimension);
                const weightPercentage = (match.weight * 100).toFixed(0);
                const intensity = match.intensity !== undefined ? match.intensity : 0;
                const intensityPercentage = Math.abs(intensity * 100);
                const isPositive = intensity >= 0;

                return (
                  <div key={idx} className="bg-white rounded-lg p-3 border border-gray-100">
                    <div className="flex items-center justify-between mb-2">
                      <div className={`flex items-center px-2 py-1 rounded-md text-xs font-bold ${config.color}`}>
                        <config.icon className="w-3 h-3 mr-1" />
                        {config.label}
                      </div>
                    </div>

                    {/* 关联度 */}
                    <div className="mb-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-600 font-medium">关联度</span>
                        <span className="text-sm font-bold text-gray-800">{weightPercentage}%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${config.color.split(' ')[0].replace('text', 'bg')} transition-all duration-500`}
                          style={{ width: `${weightPercentage}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* 强度 */}
                    <div className="mb-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs text-gray-600 font-medium">喜好强度</span>
                        <div className="flex items-center">
                          {isPositive ? (
                            <Smile className="w-3 h-3 text-green-600 mr-1" />
                          ) : (
                            <Frown className="w-3 h-3 text-red-600 mr-1" />
                          )}
                          <span className={`text-sm font-bold ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                            {isPositive ? '+' : ''}{(intensity * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden relative">
                        {/* 中心线 */}
                        <div className="absolute left-1/2 top-0 bottom-0 w-px bg-gray-300"></div>
                        {/* 强度条 */}
                        {isPositive ? (
                          <div
                            className="h-full bg-green-500 transition-all duration-500 absolute left-1/2"
                            style={{ width: `${intensityPercentage / 2}%` }}
                          ></div>
                        ) : (
                          <div
                            className="h-full bg-red-500 transition-all duration-500 absolute right-1/2"
                            style={{ width: `${intensityPercentage / 2}%` }}
                          ></div>
                        )}
                      </div>
                      <div className="flex justify-between text-[10px] text-gray-400 mt-1">
                        <span>讨厌</span>
                        <span>中性</span>
                        <span>喜欢</span>
                      </div>
                    </div>

                    {match.reasoning && (
                      <p className="text-xs text-gray-500 mt-2 italic border-t border-gray-200 pt-2">💡 {match.reasoning}</p>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* 元数据 */}
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-gray-500">记录时间：</span>
                <span className="font-medium text-gray-700 block mt-1">
                  {behavior.timestamp ? new Date(behavior.timestamp).toLocaleString('zh-CN') : '未知'}
                </span>
              </div>
              <div>
                <span className="text-gray-500">数据来源：</span>
                <span className="font-medium text-gray-700 block mt-1">
                  {behavior.source === 'GAME' ? '游戏互动' :
                    behavior.source === 'REPORT' ? '报告分析' :
                      behavior.source === 'CHAT' ? 'AI对话' : '未知'}
                </span>
              </div>
            </div>
          </div>

          {/* 删除按钮 */}
          <button
            onClick={() => {
              if (behavior.id) {
                handleDeleteBehavior(behavior.id);
                onClose();
              }
            }}
            className="w-full bg-red-50 text-red-600 py-3 rounded-xl font-bold hover:bg-red-100 transition flex items-center justify-center"
          >
            <X className="w-4 h-4 mr-2" />
            删除此记录
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-4 space-y-4 h-full overflow-y-auto bg-background">
      {/* 统计卡片 */}
      <div className="bg-gradient-to-r from-purple-500 to-indigo-600 rounded-2xl p-5 text-white shadow-lg">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold text-lg">行为数据统计</h3>
          <Activity className="w-6 h-6" />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-100 mb-1">总记录数</p>
            <p className="text-2xl font-bold">{stats?.total || 0}</p>
          </div>
          <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-100 mb-1">游戏记录</p>
            <p className="text-2xl font-bold">{stats?.sourceCounts?.GAME || 0}</p>
          </div>
          <div className="bg-white/20 rounded-lg p-3 backdrop-blur-sm">
            <p className="text-xs text-purple-100 mb-1">报告记录</p>
            <p className="text-2xl font-bold">{stats?.sourceCounts?.REPORT || 0}</p>
          </div>
        </div>
      </div>

      {/* 筛选器 */}
      <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
        <h4 className="text-sm font-bold text-gray-700 mb-3">筛选条件</h4>

        {/* 按兴趣维度筛选 */}
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-2">兴趣维度</p>
          <div className="flex flex-wrap gap-2">
            {dimensionFilters.map(dim => (
              <button
                key={dim}
                onClick={() => setFilterDimension(dim)}
                className={`text-xs px-3 py-1.5 rounded-full font-bold transition ${filterDimension === dim
                  ? 'bg-primary text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
              >
                {dim === '全部' ? dim : getDimensionConfig(dim as InterestDimensionType).label}
              </button>
            ))}
          </div>
        </div>

        {/* 按来源筛选 */}
        <div>
          <p className="text-xs text-gray-500 mb-2">数据来源</p>
          <div className="flex gap-2">
            {sources.map(source => (
              <button
                key={source}
                onClick={() => setFilterSource(source)}
                className={`text-xs px-3 py-1.5 rounded-full font-bold transition ${filterSource === source
                  ? 'bg-secondary text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
              >
                {source === '全部' ? '全部' :
                  source === 'GAME' ? '游戏' :
                    source === 'REPORT' ? '报告' : '对话'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 行为列表 */}
      <div className="space-y-3 pb-4">
        <div className="flex items-center justify-between">
          <h4 className="text-sm font-bold text-gray-700">
            行为记录 ({behaviors.length})
          </h4>
          {behaviors.length > 0 && (
            <button
              onClick={() => {
                if (confirm('确定要清空所有行为记录吗？此操作不可恢复！')) {
                  behaviorStorageService.clearAllBehaviors();
                  loadBehaviors();
                }
              }}
              className="text-xs text-red-500 hover:text-red-700 font-medium"
            >
              清空全部
            </button>
          )}
        </div>

        {behaviors.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <Activity className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p>暂无行为记录</p>
            <p className="text-xs mt-2">完成游戏或导入报告后会自动记录</p>
          </div>
        ) : (
          behaviors.map((behavior) => (
            <div
              key={behavior.id}
              onClick={() => setSelectedBehavior(behavior)}
              className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 cursor-pointer hover:border-primary/30 transition"
            >
              <div className="flex items-start justify-between mb-2">
                <p className="text-sm font-bold text-gray-800 flex-1 line-clamp-2">
                  {behavior.behavior}
                </p>
                <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" />
              </div>

              {/* 兴趣标签 */}
              <div className="flex flex-wrap gap-1.5 mb-2">
                {behavior.matches.slice(0, 3).map((match, idx) => {
                  const config = getDimensionConfig(match.dimension);
                  return (
                    <div key={idx} className={`flex items-center px-2 py-0.5 rounded-md text-[10px] font-bold ${config.color}`}>
                      <config.icon className="w-3 h-3 mr-1" />
                      {config.label} {(match.weight * 100).toFixed(0)}%
                    </div>
                  );
                })}
                {behavior.matches.length > 3 && (
                  <span className="text-[10px] text-gray-400 px-2 py-0.5">
                    +{behavior.matches.length - 3}
                  </span>
                )}
              </div>

              {/* 元信息 */}
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>
                  {behavior.source === 'GAME' ? '🎮 游戏' :
                    behavior.source === 'REPORT' ? '📄 报告' :
                      behavior.source === 'CHAT' ? '💬 对话' : '❓'}
                </span>
                <span>
                  {behavior.timestamp ? new Date(behavior.timestamp).toLocaleDateString('zh-CN') : ''}
                </span>
              </div>
            </div>
          ))
        )}
      </div>

      {/* 详情弹窗 */}
      {selectedBehavior && (
        <BehaviorDetailModal
          behavior={selectedBehavior}
          onClose={() => setSelectedBehavior(null)}
        />
      )}
    </div>
  );
};

const PageProfile = ({ trendData, interestProfile, abilityProfile, onImportReport, onExportReport, childProfile, calculateAge, onUpdateAvatar }: { trendData: any[], interestProfile: UserInterestProfile, abilityProfile: UserAbilityProfile, onImportReport: (file: File) => void, onExportReport: () => void, childProfile: ChildProfile | null, calculateAge: (birthDate: string) => number, onUpdateAvatar: (avatarUrl: string) => void }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const avatarInputRef = useRef<HTMLInputElement>(null);
  const [showReportList, setShowReportList] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [reports, setReports] = useState<Report[]>([]);

  // 加载报告列表
  useEffect(() => {
    setReports(reportStorageService.getAllReports());
  }, [showReportList]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImportReport(file);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  // 处理头像上传
  const handleAvatarSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // 检查文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }

    // 检查文件大小（限制为2MB）
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过2MB');
      return;
    }

    try {
      // 读取文件并转换为base64
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result as string;
        onUpdateAvatar(base64);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      console.error('头像上传失败:', error);
      alert('头像上传失败，请重试');
    }

    // 清空input，允许重复选择同一文件
    if (avatarInputRef.current) {
      avatarInputRef.current.value = '';
    }
  };

  // 重置为默认头像
  const handleResetAvatar = () => {
    onUpdateAvatar(defaultAvatar);
  };

  const age = childProfile ? calculateAge(childProfile.birthDate) : 0;
  const latestReport = reportStorageService.getLatestReport();

  // 报告详情弹窗
  const ReportDetailModal = ({ report, onClose }: { report: Report, onClose: () => void }) => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h3 className="font-bold text-gray-800">报告详情</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-6 space-y-4">
          {/* 报告摘要 - 必填字段，始终显示 */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
            <h5 className="text-sm font-bold text-purple-700 mb-2 flex items-center">
              <Sparkles className="w-4 h-4 mr-2" />
              报告摘要
            </h5>
            <p className="text-sm text-gray-700">{report.summary}</p>
          </div>

          {/* 报告原图 - 仅当有图片时显示 */}
          {report.imageUrl && (
            <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <h5 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
                <FileText className="w-4 h-4 mr-2 text-blue-600" />
                报告原图
              </h5>
              <img
                src={report.imageUrl.startsWith('data:') ? report.imageUrl : `data:image/jpeg;base64,${report.imageUrl}`}
                alt="报告原图"
                className="w-full rounded-lg border border-gray-300 cursor-pointer hover:opacity-90 transition"
                onClick={() => window.open(report.imageUrl.startsWith('data:') ? report.imageUrl : `data:image/jpeg;base64,${report.imageUrl}`, '_blank')}
              />
              <p className="text-xs text-gray-400 mt-2 text-center">点击查看大图</p>
            </div>
          )}

          {/* OCR 提取结果 - 仅当有OCR结果时显示 */}
          {report.ocrResult && (
            <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
              <h5 className="text-sm font-bold text-blue-700 mb-3 flex items-center">
                <Eye className="w-4 h-4 mr-2" />
                文字提取
              </h5>
              <div className="bg-white rounded-lg p-3 max-h-60 overflow-y-auto text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
                {report.ocrResult}
              </div>
            </div>
          )}

          {/* 孩子画像 - 必填字段，始终显示 */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-200">
            <h5 className="text-sm font-bold text-green-700 mb-3 flex items-center">
              <User className="w-4 h-4 mr-2" />
              孩子画像
            </h5>
            <div className="bg-white rounded-lg p-3 text-sm text-gray-700 leading-relaxed whitespace-pre-wrap">
              {report.diagnosis}
            </div>
          </div>

          {/* 下一步干预建议 - 仅当有建议时显示（评估报告才有） */}
          {report.nextStepSuggestion && (
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-xl p-4">
              <h5 className="text-sm font-bold mb-3 flex items-center">
                <Lightbulb className="w-4 h-4 mr-2 text-yellow-300" />
                下一步干预建议
              </h5>
              <div className="text-sm leading-relaxed whitespace-pre-wrap">
                {report.nextStepSuggestion}
              </div>
            </div>
          )}

          {/* 报告信息 */}
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <div className="grid grid-cols-2 gap-3 text-xs">
              <div>
                <span className="text-gray-500">报告日期：</span>
                <span className="font-medium text-gray-700">{report.date}</span>
              </div>
              <div>
                <span className="text-gray-500">报告类型：</span>
                <span className="font-medium text-gray-700">
                  {report.type === 'hospital' ? '医院报告' :
                    report.type === 'ai_generated' ? 'AI评估' :
                      report.type === 'assessment' ? '评估报告' : '其他'}
                </span>
              </div>
              <div className="col-span-2">
                <span className="text-gray-500">创建时间：</span>
                <span className="font-medium text-gray-700">
                  {new Date(report.createdAt).toLocaleString('zh-CN')}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // 报告列表页面
  if (showReportList) {
    return (
      <div className="p-4 space-y-4 h-full overflow-y-auto bg-background">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setShowReportList(false)}
            className="flex items-center text-gray-600 hover:text-gray-800"
          >
            <ChevronLeft className="w-5 h-5 mr-1" />
            返回档案
          </button>
          <h2 className="font-bold text-gray-800">报告历史</h2>
          <div className="w-20"></div>
        </div>

        {reports.length === 0 ? (
          <div className="text-center py-20 text-gray-400">
            <FileText className="w-16 h-16 mx-auto mb-4 text-gray-300" />
            <p>暂无报告记录</p>
          </div>
        ) : (
          <div className="space-y-3">
            {reports.map((report) => (
              <div
                key={report.id}
                onClick={() => setSelectedReport(report)}
                className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 cursor-pointer hover:border-primary/30 transition"
              >
                <div className="flex items-start space-x-3">
                  {/* 缩略图或默认图标 */}
                  {report.imageUrl ? (
                    <img
                      src={report.imageUrl.startsWith('data:') ? report.imageUrl : `data:image/jpeg;base64,${report.imageUrl}`}
                      alt="报告缩略图"
                      className="w-16 h-16 rounded-lg object-cover border border-gray-200 flex-shrink-0"
                    />
                  ) : (
                    <div className="w-16 h-16 rounded-lg border border-gray-200 flex items-center justify-center flex-shrink-0 bg-gradient-to-br from-purple-50 to-blue-50">
                      {report.type === 'ai_generated' || report.type === 'assessment' ? (
                        <Award className="w-8 h-8 text-purple-500" />
                      ) : (
                        <FileText className="w-8 h-8 text-blue-500" />
                      )}
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-gray-800 truncate">{report.summary}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {report.date} · {report.type === 'hospital' ? '医院报告' : report.type === 'ai_generated' ? 'AI评估' : report.type === 'assessment' ? '评估报告' : '其他'}
                    </p>
                    <p className="text-xs text-gray-400 mt-1 line-clamp-2">{report.diagnosis}</p>
                  </div>
                  <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                </div>
              </div>
            ))}
          </div>
        )}

        {selectedReport && (
          <ReportDetailModal
            report={selectedReport}
            onClose={() => setSelectedReport(null)}
          />
        )}
      </div>
    );
  }

  // 档案主页
  return (
    <div className="p-4 space-y-6 h-full overflow-y-auto bg-background">
      {/* 头像和基本信息 */}
      <div className="flex flex-col items-center space-y-4 bg-white p-6 rounded-2xl shadow-sm">
        {/* 头像容器 - 添加编辑功能 */}
        <div className="relative group">
          <img
            src={childProfile?.avatar || defaultAvatar}
            className="w-24 h-24 rounded-full border-4 border-white shadow-lg"
            alt={childProfile?.name || '孩子'}
          />
          {/* 编辑按钮 */}
          <div className="absolute inset-0 rounded-full bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
            <button
              onClick={() => avatarInputRef.current?.click()}
              className="bg-white text-gray-700 p-2 rounded-full hover:bg-gray-100 transition"
              title="更换头像"
            >
              <Camera className="w-5 h-5" />
            </button>
          </div>
          {/* 重置按钮 - 仅当头像不是默认头像时显示 */}
          {childProfile?.avatar && childProfile.avatar !== defaultAvatar && (
            <button
              onClick={handleResetAvatar}
              className="absolute -bottom-2 -right-2 bg-gray-500 text-white p-1.5 rounded-full hover:bg-gray-600 transition shadow-md"
              title="恢复默认头像"
            >
              <RefreshCw className="w-3 h-3" />
            </button>
          )}
        </div>

        {/* 隐藏的头像上传input */}
        <input
          type="file"
          ref={avatarInputRef}
          onChange={handleAvatarSelect}
          className="hidden"
          accept="image/*"
        />

        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-800">{childProfile?.name || '未设置'}, {age}岁</h2>
          <p className="text-sm text-gray-500 mt-1">
            {childProfile?.gender === 'male' ? '男孩' : childProfile?.gender === 'female' ? '女孩' : ''}
          </p>
        </div>
      </div>

      {/* 最新画像 */}
      <div className="bg-gradient-to-br from-green-50 to-blue-50 p-5 rounded-2xl shadow-sm border border-green-100">
        <h3 className="font-bold text-gray-700 mb-3 flex items-center">
          <Sparkles className="w-5 h-5 mr-2 text-green-600" />
          最新画像
        </h3>
        <p className="text-sm text-gray-700 leading-relaxed">
          {latestReport?.diagnosis || childProfile?.diagnosis || '暂无评估信息，请导入报告或完成评估'}
        </p>
        {latestReport && (
          <p className="text-xs text-gray-400 mt-3">
            更新于 {new Date(latestReport.createdAt).toLocaleDateString('zh-CN')}
          </p>
        )}
      </div>

      {/* 底部按钮 */}
      <div className="space-y-3 pb-4">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileSelect}
          className="hidden"
          accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png,.gif,.webp"
        />

        <button
          onClick={() => setShowReportList(true)}
          className="w-full bg-white text-gray-700 py-3 rounded-xl font-bold flex items-center justify-center hover:bg-gray-50 transition shadow-sm border border-gray-200"
        >
          <FileText className="w-5 h-5 mr-2" />
          查看报告列表 ({reports.length})
        </button>

        <button
          onClick={() => fileInputRef.current?.click()}
          className="w-full bg-primary text-white py-3 rounded-xl font-bold flex items-center justify-center hover:bg-green-600 transition shadow-md"
        >
          <Upload className="w-5 h-5 mr-2" />
          导入报告
        </button>

        <button
          onClick={onExportReport}
          className="w-full bg-blue-500 text-white py-3 rounded-xl font-bold flex items-center justify-center hover:bg-blue-600 transition shadow-md"
        >
          <FileText className="w-5 h-5 mr-2" />
          导出报告
        </button>
      </div>
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
  activeGame,
  childProfile
}: {
  initialGameId?: string,
  gameState: GameState,
  setGameState: (s: GameState) => void,
  onBack: () => void,
  trendData: any[],
  onUpdateTrend: (score: number) => void,
  onProfileUpdate: (u: ProfileUpdate) => void,
  activeGame?: Game,
  childProfile: ChildProfile | null
}) => {
  // 从 floorGameStorage 读取游戏并转换为 Game 类型
  const floorGames = floorGameStorageService.getAllGames();
  const GAMES_FROM_STORAGE: Game[] = floorGames.map(fg => ({
    id: fg.id,
    title: fg.gameTitle,
    target: fg.goal,
    duration: '15-20分钟',
    reason: fg.summary,
    isVR: fg.isVR,
    steps: fg.steps.map(s => ({
      instruction: s.instruction,
      guidance: s.instruction  // 地板游戏中，指令本身就是指导
    })),
    summary: fg.summary,
    materials: [],
    status: fg.status,
    date: fg.dtstart // 使用 dtstart 作为 date（向后兼容）
  }));

  const [internalActiveGame, setInternalActiveGame] = useState<Game | undefined>(
    activeGame || (initialGameId ? GAMES_FROM_STORAGE.find(g => g.id === initialGameId) : undefined)
  );

  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [timer, setTimer] = useState(0);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const [clickedLog, setClickedLog] = useState<string | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [evaluation, setEvaluation] = useState<EvaluationResult | null>(null);
  const [gameReview, setGameReview] = useState<GameReviewResult | null>(null);
  const [hasUpdatedTrend, setHasUpdatedTrend] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [activeFilter, setActiveFilter] = useState('全部');
  const [showVideoCall, setShowVideoCall] = useState(false); // AI 视频通话状态
  const [coverImages, setCoverImages] = useState<Map<string, string>>(new Map()); // gameId → 第一步图片（列表封面）
  const [stepImages, setStepImages] = useState<Map<number, string>>(new Map()); // stepIndex → dataUrl（当前游戏步骤图片）
  const FILTERS = ['全部', '共同注意', '自我调节', '亲密感', '双向沟通', '情绪思考', '创造力'];

  useEffect(() => {
    if (initialGameId && !internalActiveGame) {
      console.log('[Game Page] 初始化游戏，ID:', initialGameId);

      // 先尝试从 floorGameStorage 获取待开始的游戏（来自聊天推荐）
      const floorGame = floorGameStorageService.getGameById(initialGameId);
      console.log('[Game Page] floorGame:', floorGame ? '存在' : '不存在');

      if (floorGame) {
        console.log('[Game Page] ✅ 加载推荐的游戏:', floorGame.gameTitle);
        // 转换为 Game 对象供游戏页面使用
        const gameFromFloor: Game = {
          id: floorGame.id,
          title: floorGame.gameTitle,
          target: floorGame.goal,
          duration: '15-20分钟',
          reason: floorGame.summary,
          isVR: floorGame.isVR,
          steps: floorGame.steps.map(s => ({
            instruction: s.instruction,
            guidance: s.instruction  // 地板游戏中，指令本身就是指导
          })),
          summary: floorGame.summary,
          materials: []
        };
        setInternalActiveGame(gameFromFloor);
        setCurrentStepIndex(0); setTimer(0); setLogs([]); setEvaluation(null); setHasUpdatedTrend(false);
        return;
      }

      // 如果没有待开始的游戏，从转换后的游戏列表中查找
      const game = GAMES_FROM_STORAGE.find(g => g.id === initialGameId);
      if (game) {
        console.log('[Game Page] 从游戏库加载游戏:', game.title);
        setInternalActiveGame(game);
        setCurrentStepIndex(0); setTimer(0); setLogs([]); setEvaluation(null); setHasUpdatedTrend(false);
      } else {
        console.warn('[Game Page] ❌ 未找到游戏:', initialGameId);
      }
    }
  }, [initialGameId, internalActiveGame]);

  useEffect(() => {
    if (gameState === GameState.PLAYING) { timerRef.current = setInterval(() => setTimer(t => t + 1), 1000); }
    else { if (timerRef.current) clearInterval(timerRef.current); }
    return () => { if (timerRef.current) clearInterval(timerRef.current); };
  }, [gameState]);

  useEffect(() => { if (gameState === GameState.SUMMARY && !evaluation && !isAnalyzing) performAnalysis(); }, [gameState]);

  // 加载游戏封面图（每个游戏的第一步图片）和监听实时更新
  useEffect(() => {
    let cancelled = false;
    const loadCovers = async () => {
      try {
        const { imageStorageService } = await import('./services/imageStorage');
        const newCovers = new Map<string, string>();
        for (const fg of floorGames) {
          const img = await imageStorageService.getStepImage(fg.id, 0);
          if (img && !cancelled) newCovers.set(fg.id, img);
        }
        if (!cancelled) setCoverImages(newCovers);
      } catch (e) { console.warn('[PageGames] 加载封面图失败:', e); }
    };
    loadCovers();

    const handleImageUpdate = async (e: Event) => {
      const { gameId, stepIndex } = (e as CustomEvent).detail;
      if (stepIndex === 0) {
        try {
          const { imageStorageService } = await import('./services/imageStorage');
          const img = await imageStorageService.getStepImage(gameId, 0);
          if (img && !cancelled) setCoverImages(prev => new Map(prev).set(gameId, img));
        } catch (_) { /* ignore */ }
      }
      // 如果正在查看的游戏有新图片，更新步骤图片
      if (internalActiveGame?.id === gameId) {
        try {
          const { imageStorageService } = await import('./services/imageStorage');
          const img = await imageStorageService.getStepImage(gameId, stepIndex);
          if (img && !cancelled) setStepImages(prev => new Map(prev).set(stepIndex, img));
        } catch (_) { /* ignore */ }
      }
    };
    window.addEventListener('floorGameStepImagesUpdated', handleImageUpdate);
    return () => { cancelled = true; window.removeEventListener('floorGameStepImagesUpdated', handleImageUpdate); };
  }, [floorGames.length]);

  // 当选中游戏变化时，加载该游戏的全部步骤图片
  useEffect(() => {
    if (!internalActiveGame?.id) { setStepImages(new Map()); return; }
    let cancelled = false;
    const loadStepImages = async () => {
      try {
        const { imageStorageService } = await import('./services/imageStorage');
        const imgs = await imageStorageService.getGameImages(internalActiveGame.id);
        if (!cancelled) setStepImages(imgs);
      } catch (e) { console.warn('[PageGames] 加载步骤图片失败:', e); }
    };
    loadStepImages();
    return () => { cancelled = true; };
  }, [internalActiveGame?.id]);

  const performAnalysis = async () => {
    setIsAnalyzing(true);
    try {
      const logsToAnalyze = logs.length > 0 ? logs : [{ type: 'emoji', content: '完成了游戏', timestamp: new Date() } as LogEntry];

      // 格式化聊天记录用于复盘
      const chatHistoryText = logsToAnalyze.map(log => {
        const time = log.timestamp instanceof Date ? log.timestamp.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '';
        return `[${time}] ${log.type === 'emoji' ? '快速记录' : '语音记录'}: ${log.content}`;
      }).join('\n');

      // 从 storage 获取完整的 FloorGame 数据
      const floorGame = internalActiveGame?.id ? floorGameStorageService.getGameById(internalActiveGame.id) : null;

      // 并行调用：评估 + 复盘
      const evaluationPromise = api.analyzeSession(logsToAnalyze);
      const reviewPromise = floorGame ? reviewFloorGame({
        game: { ...floorGame, status: 'completed', dtend: new Date().toISOString() },
        chatHistory: chatHistoryText,
        parentFeedback: chatHistoryText
      }).catch(e => { console.error('[GameReview] 复盘失败:', e); return null; }) : Promise.resolve(null);

      const [result, reviewResult] = await Promise.all([evaluationPromise, reviewPromise]);

      setEvaluation(result);
      if (reviewResult) {
        setGameReview(reviewResult);
        console.log('[GameReview] 复盘完成，综合得分:', reviewResult.overallScore);
      }

      // 将评估结果写入 FloorGame 记录
      if (internalActiveGame?.id) {
        try {
          floorGameStorageService.updateGame(internalActiveGame.id, {
            evaluation: result,
            status: 'completed',
            dtend: new Date().toISOString()
          });
        } catch (e) { console.warn('Failed to save evaluation to FloorGame:', e); }
      }

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

  const handleStartGame = (game: Game) => {
    floorGameStorageService.updateGame(game.id, {
      dtstart: new Date().toISOString()
    });
    setInternalActiveGame(game);
    setGameState(GameState.PLAYING);
    setCurrentStepIndex(0);
    setTimer(0);
    setLogs([]);
    setEvaluation(null);
    setGameReview(null);
    setHasUpdatedTrend(false);
  };
  const handleLog = (type: 'emoji' | 'voice', content: string) => { setLogs(prev => [...prev, { type, content, timestamp: new Date() }]); setClickedLog(content); setTimeout(() => setClickedLog(null), 300); };
  const formatTime = (seconds: number) => { const m = Math.floor(seconds / 60); const s = seconds % 60; return `${m}:${s < 10 ? '0' : ''}${s}`; };

  if (gameState === GameState.LIST) {
    const filteredGames = GAMES_FROM_STORAGE.filter(game => {
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
          {filteredGames.length > 0 ? (filteredGames.map(game => {
            const statusConfig = game.status === 'completed' ? { label: '已完成', cls: 'bg-green-50 text-green-700' } : game.status === 'aborted' ? { label: '已中止', cls: 'bg-red-50 text-red-700' } : { label: '未开始', cls: 'bg-gray-100 text-gray-500' };
            // LIST 状态：只显示年月日
            const dateStr = game.date ? new Date(game.date).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : '';
            return (<div key={game.id} onClick={() => handleStartGame(game)} className="bg-white rounded-2xl shadow-sm border border-gray-100 active:scale-98 transition transform cursor-pointer group hover:border-primary/30 overflow-hidden">{coverImages.get(game.id) && (<div className="w-full h-32 overflow-hidden"><img src={coverImages.get(game.id)} alt="" className="w-full h-full object-cover" /></div>)}<div className="p-5"><div className="flex justify-between items-start"><h4 className="font-bold text-gray-800 text-lg group-hover:text-primary transition flex items-center">{game.title}{game.isVR && (<span className="ml-2 bg-indigo-600 text-white text-[10px] px-2 py-0.5 rounded-md shadow-sm font-bold flex items-center animate-pulse"><Sparkles className="w-3 h-3 mr-1 fill-current" /> VR体验</span>)}</h4><div className="flex items-center space-x-2 shrink-0 ml-2"><span className={`text-xs px-2 py-1 rounded-full font-medium ${statusConfig.cls}`}>{statusConfig.label}</span>{dateStr && <span className="text-xs text-gray-400">{dateStr}</span>}</div></div><p className="text-gray-500 text-sm mt-1 line-clamp-2">{game.reason}</p><div className="mt-4 flex items-center text-xs font-bold text-blue-600 bg-blue-50 w-fit px-3 py-1.5 rounded-lg">目标: {game.target}</div></div></div>);
          })) : (<div className="text-center py-10 text-gray-400 flex flex-col items-center"><div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4"><Search className="w-8 h-8 text-gray-300" /></div><p>没有找到匹配的游戏</p><button onClick={() => { setSearchText(''); setActiveFilter('全部') }} className="mt-2 text-primary font-bold text-sm">清除筛选</button></div>)}
        </div>
      </div>
    );
  }

  if (gameState === GameState.PLAYING && internalActiveGame) {
    const currentStep = internalActiveGame.steps[currentStepIndex];
    const isLastStep = currentStepIndex === internalActiveGame.steps.length - 1;

    return (
      <div className="h-full flex flex-col bg-background">
        <div className="w-full flex flex-col items-center py-4 bg-background z-0 relative">
          <button
            onClick={() => setShowVideoCall(!showVideoCall)}
            className={`absolute left-4 top-4 text-xs px-3 py-1.5 rounded-lg font-bold transition flex items-center ${showVideoCall ? 'text-red-500 bg-red-50 hover:bg-red-100' : 'text-blue-500 bg-blue-50 hover:bg-blue-100'}`}
          >
            <Camera className="w-3 h-3 mr-1" />
            {showVideoCall ? '关闭视频通话' : 'AI 视频通话'}
          </button>
          <h3 className="font-bold text-sm text-gray-500 mb-1">{internalActiveGame.title}</h3>
          <div className="text-green-600 font-mono text-3xl font-bold">{formatTime(timer)}</div>
        </div>
        <div className="flex-1 px-4 pb-2 flex flex-col min-h-0">
          {/* 视频通话组件 */}
          {showVideoCall && (
            <div className="mb-4 bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              <AIVideoCall
                childProfile={childProfile}
                gameContext={`当前游戏: ${internalActiveGame.title}\n当前步骤: ${currentStep.instruction}\n互动提示: ${currentStep.guidance}`}
                onClose={() => setShowVideoCall(false)}
              />
            </div>
          )}

          <div className="bg-white rounded-[2rem] shadow-sm border border-gray-100 flex-1 flex flex-col p-6 relative overflow-hidden"><div className="w-full flex justify-center mb-6 shrink-0"><div className="w-12 h-12 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-xl shadow-sm">{currentStepIndex + 1}</div></div><div className="flex-1 flex flex-col justify-center overflow-y-auto no-scrollbar">{stepImages.get(currentStepIndex) && (<div className="w-full mb-4 rounded-2xl overflow-hidden shrink-0"><img src={stepImages.get(currentStepIndex)} alt={`步骤 ${currentStepIndex + 1} 插图`} className="w-full h-48 object-cover rounded-2xl" /></div>)}<h2 className="text-2xl font-bold text-gray-800 leading-normal text-center mb-8">{currentStep.instruction}</h2><div className="bg-blue-50/80 p-5 rounded-2xl border border-blue-100 text-left w-full"><h4 className="text-blue-800 font-bold mb-2 flex items-center text-sm"><Lightbulb className="w-4 h-4 mr-2 text-yellow-500 fill-current" /> 互动小贴士</h4><p className="text-blue-900/80 text-sm leading-relaxed font-medium">{currentStep.guidance}</p></div></div></div></div>
        <div className="flex items-center justify-between px-6 py-4 mb-2"><button onClick={() => setCurrentStepIndex(Math.max(0, currentStepIndex - 1))} disabled={currentStepIndex === 0} className={`flex items-center text-gray-400 font-bold transition px-4 py-3 ${currentStepIndex === 0 ? 'opacity-30 cursor-not-allowed' : 'hover:text-gray-600'}`}><ChevronLeft className="w-5 h-5 mr-1" /> 上一步</button><div className="bg-white px-4 py-2 rounded-xl shadow-sm border border-gray-100 text-xs font-bold text-gray-500 tracking-wide">步骤 {currentStepIndex + 1} / {internalActiveGame.steps.length}</div>{isLastStep ? (<button onClick={() => setGameState(GameState.SUMMARY)} className="bg-primary text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-primary/30 flex items-center hover:bg-green-600 transition transform active:scale-95">完成 <CheckCircle2 className="w-5 h-5 ml-2" /></button>) : (<button onClick={() => setCurrentStepIndex(currentStepIndex + 1)} className="bg-secondary text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-secondary/30 flex items-center hover:bg-blue-600 transition transform active:scale-95">下一步 <ChevronRight className="w-5 h-5 ml-1" /></button>)}</div>
        <div className="p-4 bg-white border-t border-gray-100 pb-8 rounded-t-3xl shadow-[0_-4px_20px_-5px_rgba(0,0,0,0.1)] z-20 relative"><p className="text-center text-[10px] text-gray-400 mb-3 uppercase tracking-widest font-bold">快速记录当前反应</p><div className="flex justify-between max-w-sm mx-auto mb-3 space-x-2">{[{ icon: Smile, label: '微笑', color: 'text-yellow-600 bg-yellow-100 ring-yellow-300' }, { icon: Eye, label: '眼神', color: 'text-blue-600 bg-blue-100 ring-blue-300' }, { icon: Handshake, label: '互动', color: 'text-green-600 bg-green-100 ring-green-300' }, { icon: Frown, label: '抗拒', color: 'text-red-500 bg-red-100 ring-red-300' }].map((btn, i) => (<button key={i} onClick={() => handleLog('emoji', btn.label)} className={`flex-1 py-3 rounded-xl shadow-sm active:scale-95 transition flex flex-col items-center justify-center ${btn.color} ${clickedLog === btn.label ? 'ring-4 ring-offset-2 scale-110 bg-opacity-100' : ''}`}><btn.icon className="w-5 h-5 mb-1" /><span className="text-[10px] font-bold">{btn.label}</span></button>))}</div><button onMouseDown={() => { setClickedLog('voice'); handleLog('voice', '录音开始...'); }} onMouseUp={() => handleLog('voice', '录音结束')} className={`w-full bg-gray-50 border border-gray-200 py-3 rounded-xl text-gray-600 font-bold flex items-center justify-center shadow-sm active:bg-gray-200 active:scale-98 transition text-sm ${clickedLog === 'voice' ? 'ring-2 ring-gray-300 bg-gray-100' : ''}`}><Mic className="w-4 h-4 mr-2" /> 按住说话 记录观察笔记</button></div>
      </div>
    );
  }

  if (gameState === GameState.SUMMARY) {
    // SUMMARY 状态：显示游戏开始时间（年月日 时:分）
    const gameStartTime = internalActiveGame?.date
      ? new Date(internalActiveGame.date).toLocaleString('zh-CN', {
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

    return (
      <div className="h-full bg-background p-6 overflow-y-auto">
        {isAnalyzing ? (
          <div className="flex flex-col items-center justify-center h-[60vh] text-center space-y-6 animate-in fade-in duration-700"><div className="relative"><div className="w-20 h-20 border-4 border-gray-200 rounded-full"></div><div className="w-20 h-20 border-4 border-primary border-t-transparent rounded-full animate-spin absolute top-0 left-0"></div><Activity className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-primary w-8 h-8" /></div><div><h2 className="text-xl font-bold text-gray-800">AI 正在复盘互动数据...</h2><p className="text-gray-500 text-sm mt-2">分析眼神接触频率、情绪稳定度及八大兴趣维度</p></div></div>
        ) : evaluation ? (
          <div className="animate-in slide-in-from-bottom-10 duration-700 fade-in pb-10">
            <div className="text-center mb-8"><h2 className="text-2xl font-bold text-gray-800">本次互动评估</h2><p className="text-gray-400 text-xs mt-1">{gameStartTime}</p></div>
            <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 relative overflow-hidden text-center">
              <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-green-400 to-blue-500"></div>
              <div className="mb-2 text-gray-500 font-bold text-sm uppercase tracking-wider">综合互动分</div>
              <div className="text-6xl font-black text-gray-800 mb-2 tracking-tighter">{evaluation.score}</div>
              <div className="flex justify-center mb-4"><div className="flex space-x-1">{[1, 2, 3, 4, 5].map(star => (<div key={star} className={`w-2 h-2 rounded-full ${evaluation.score >= star * 18 ? 'bg-yellow-400' : 'bg-gray-200'}`}></div>))}</div></div>

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
            {evaluation.interestAnalysis && evaluation.interestAnalysis.length > 0 && (<div className="bg-white p-5 rounded-2xl shadow-sm mb-6 border border-gray-100"><h3 className="font-bold text-gray-700 mb-4 flex items-center"><Dna className="w-5 h-5 mr-2 text-indigo-500" /> 兴趣探索度分析</h3><div className="space-y-4">{evaluation.interestAnalysis.map((item, idx) => (<div key={idx} className="bg-gray-50 rounded-xl p-3 border border-gray-100"><p className="text-sm font-semibold text-gray-800 mb-2">"{item.behavior}"</p><div className="flex flex-wrap gap-2">{item.matches.map((match, mIdx) => { const config = getDimensionConfig(match.dimension); return (<div key={mIdx} className="flex flex-col"><div className={`flex items-center px-2 py-1 rounded-md text-xs font-bold ${config.color}`}><config.icon className="w-3 h-3 mr-1" />{config.label} {(match.weight * 100).toFixed(0)}%</div></div>) })}</div>{item.matches[0] && (<p className="text-[10px] text-gray-500 mt-2 italic border-t border-gray-200 pt-1">💡 {item.matches[0].reasoning}</p>)}</div>))}</div></div>)}
            <div className="bg-gradient-to-br from-indigo-500 to-purple-600 text-white p-5 rounded-2xl shadow-lg mb-6 relative overflow-hidden"><div className="relative z-10"><h3 className="font-bold flex items-center mb-3"><Lightbulb className="w-4 h-4 mr-2 text-yellow-300" /> 下一步建议</h3><p className="text-indigo-100 text-sm leading-relaxed font-medium">{evaluation.suggestion}</p></div><Sparkles className="absolute -right-2 -bottom-2 text-white/10 w-24 h-24 rotate-12" /></div>

            {/* AI 专业复盘 */}
            {gameReview && (
              <div className="space-y-4 mb-6">
                {/* 复盘总结 + 推荐标签 */}
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
                  {/* 多维度打分 */}
                  <div className="space-y-2.5">
                    {([
                      { key: 'childEngagement', label: '孩子配合度', color: 'bg-green-500' },
                      { key: 'gameCompletion', label: '游戏完成度', color: 'bg-blue-500' },
                      { key: 'emotionalConnection', label: '情感连接', color: 'bg-pink-500' },
                      { key: 'communicationLevel', label: '沟通互动', color: 'bg-purple-500' },
                      { key: 'skillProgress', label: '能力进步', color: 'bg-yellow-500' },
                      { key: 'parentExecution', label: '家长执行', color: 'bg-indigo-500' }
                    ] as const).map(dim => {
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

                {/* 下一步建议 */}
                <div className="bg-gradient-to-br from-teal-500 to-emerald-600 text-white p-5 rounded-2xl shadow-lg relative overflow-hidden">
                  <div className="relative z-10">
                    <h3 className="font-bold flex items-center mb-3">
                      <Lightbulb className="w-4 h-4 mr-2 text-yellow-300" /> 下一步建议
                    </h3>
                    <p className="text-teal-100 text-sm leading-relaxed">{gameReview.nextStepSuggestion}</p>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-white p-4 rounded-2xl shadow-sm mb-20 border border-gray-100"><h3 className="font-bold text-gray-700 mb-4 flex items-center justify-between"><span className="flex items-center"><TrendingUp className="w-4 h-4 mr-2 text-green-500" /> 成长曲线已更新</span><span className="text-[10px] bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold">+1 记录</span></h3><div className="h-40 w-full"><ResponsiveContainer width="100%" height="100%"><LineChart data={trendData}><CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f3f4f6" /><XAxis dataKey="name" tick={{ fontSize: 9, fill: '#9ca3af' }} axisLine={false} tickLine={false} interval={0} /><YAxis hide domain={[0, 100]} /><Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)' }} /><Line type="monotone" dataKey="engagement" stroke="#10B981" strokeWidth={3} dot={(props: any) => { const isLast = props.index === trendData.length - 1; return (<circle cx={props.cx} cy={props.cy} r={isLast ? 6 : 4} fill={isLast ? "#10B981" : "#fff"} stroke="#10B981" strokeWidth={2} />); }} isAnimationActive={true} /></LineChart></ResponsiveContainer></div></div>
            <div className="fixed bottom-0 left-0 right-0 p-4 bg-white border-t border-gray-100"><button onClick={() => { setGameState(GameState.LIST); onBack(); }} className="w-full bg-gray-900 text-white py-3.5 rounded-xl font-bold shadow-lg hover:bg-gray-800 transition active:scale-95 flex items-center justify-center"><RefreshCw className="w-4 h-4 mr-2" /> 返回游戏库</button></div>
          </div>
        ) : (<div className="text-center mt-20 text-gray-400"><p>无法生成评估结果</p><button onClick={() => setGameState(GameState.LIST)} className="mt-4 text-primary">返回</button></div>)}
      </div>
    );
  }

  return <div>加载中...</div>;
};

// --- App Root ---

export default function App() {
  // 检查是否首次进入（通过 localStorage 判断）
  const [isFirstTime, setIsFirstTime] = useState<boolean>(() => {
    try {
      const hasProfile = localStorage.getItem('asd_floortime_child_profile');
      return !hasProfile;
    } catch (e) {
      return true;
    }
  });

  const [currentPage, setCurrentPage] = useState<Page>(() => {
    return isFirstTime ? Page.WELCOME : Page.CHAT;
  });

  const [isSidebarOpen, setSidebarOpen] = useState(false);
  const [activeGameId, setActiveGameId] = useState<string | undefined>(undefined);
  const [gameMode, setGameMode] = useState<GameState>(GameState.LIST);
  const [trendData, setTrendData] = useState(INITIAL_TREND_DATA);
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [showExitConfirm, setShowExitConfirm] = useState(false); // 退出互动确认

  // 加载真实的儿童档案
  const [childProfile, setChildProfile] = useState<ChildProfile | null>(() => {
    try {
      const saved = localStorage.getItem('asd_floortime_child_profile');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to load child profile:', e);
    }
    return null;
  });

  const [interestProfile, setInterestProfile] = useState<UserInterestProfile>(() => {
    try { const saved = localStorage.getItem('asd_floortime_interests_v1'); if (saved) return JSON.parse(saved); } catch (e) { }
    return INITIAL_INTEREST_SCORES;
  });

  const [abilityProfile, setAbilityProfile] = useState<UserAbilityProfile>(() => {
    try { const saved = localStorage.getItem('asd_floortime_abilities_v1'); if (saved) return JSON.parse(saved); } catch (e) { }
    return INITIAL_ABILITY_SCORES;
  });

  // *** Serialize Profile Context for Agents ***
  const profileContextString = `
  [当前兴趣画像]
  ${Object.entries(interestProfile).map(([k, v]) => `${k}: ${v}`).join(', ')}
  
  [当前能力画像]
  ${Object.entries(abilityProfile).map(([k, v]) => `${k}: ${v}`).join(', ')}
  `;

  useEffect(() => { localStorage.setItem('asd_floortime_interests_v1', JSON.stringify(interestProfile)); }, [interestProfile]);
  useEffect(() => { localStorage.setItem('asd_floortime_abilities_v1', JSON.stringify(abilityProfile)); }, [abilityProfile]);

  const handleProfileUpdate = (update: ProfileUpdate) => {
    // 保存行为数据到存储
    if (update.interestUpdates?.length > 0) {
      update.interestUpdates.forEach(behaviorAnalysis => {
        const behaviorWithMeta: BehaviorAnalysis = {
          ...behaviorAnalysis,
          source: update.source,
          timestamp: new Date().toISOString(),
          id: behaviorStorageService.generateBehaviorId()
        };
        behaviorStorageService.saveBehavior(behaviorWithMeta);
      });

      // 更新兴趣档案
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
  const handleStartGame = (gameId: string) => {
    console.log('[App] handleStartGame 被调用，gameId:', gameId);
    setActiveGameId(gameId);
    setGameMode(GameState.PLAYING);
    setCurrentPage(Page.GAMES);
    console.log('[App] 已设置 activeGameId:', gameId, 'gameMode: PLAYING, currentPage: GAMES');
  };
  const handleUpdateTrend = (newScore: number) => { setTrendData(prev => [...prev, { name: '本次', engagement: newScore }]); };

  // 计算年龄的辅助函数
  const calculateAge = (birthDate: string): number => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    return age;
  };

  // 导入报告处理（在档案页面）
  const handleImportReportFromProfile = async (file: File) => {
    const category = fileUploadService.categorizeFile(file);

    try {
      if (category === 'image') {
        // 分析图片 - 使用统一的分析 prompt
        const result = await multimodalService.parseImage(file, ASD_REPORT_ANALYSIS_PROMPT);
        if (result.success) {
          // 尝试解析 JSON 格式
          try {
            let jsonContent = result.content;
            const jsonMatch = result.content.match(/```json\s*([\s\S]*?)\s*```/);
            if (jsonMatch) {
              jsonContent = jsonMatch[1];
            }
            const parsed = JSON.parse(jsonContent);
            alert('报告分析完成！\n\nOCR提取：\n' + (parsed.ocr || '').substring(0, 100) + '...\n\n孩子画像：\n' + (parsed.profile || '').substring(0, 100) + '...\n\n（数据将保存到 SQLite，功能待实现）');
          } catch {
            alert('报告分析完成！\n\n' + result.content.substring(0, 200) + '...\n\n（数据将保存到 SQLite，功能待实现）');
          }
          // TODO: 调用后端 SQLite API 保存数据
          // await api.saveReportToSQLite(result.content);
        } else {
          alert('报告分析失败：' + result.error);
        }
      } else if (category === 'document') {
        // 分析文档
        const textContent = file.type === "text/plain" ? await file.text() : `文件名: ${file.name}`;
        const analysis = await api.analyzeReport(textContent);
        handleProfileUpdate(analysis);
        alert('报告分析完成并已更新档案！\n\n（数据将保存到 SQLite，功能待实现）');
        // TODO: 调用后端 SQLite API 保存数据
      } else {
        alert('不支持的文件类型，请上传图片或文档');
      }
    } catch (error) {
      alert('报告分析失败：' + (error instanceof Error ? error.message : '未知错误'));
    }
  };

  // 导出报告处理
  const handleExportReport = () => {
    alert('导出报告功能待实现\n\n将生成包含以下内容的PDF报告：\n- 孩子基本信息\n- 兴趣热力图\n- 能力雷达图\n- 互动参与度趋势\n- 行为记录\n- 游戏推荐');
    // TODO: 实现报告导出功能
  };

  // 更新头像
  const handleUpdateAvatar = (avatarUrl: string) => {
    if (!childProfile) return;

    const updatedProfile = {
      ...childProfile,
      avatar: avatarUrl
    };

    setChildProfile(updatedProfile);
    localStorage.setItem('asd_floortime_child_profile', JSON.stringify(updatedProfile));
    console.log('[App] 头像已更新');
  };

  // 欢迎页面完成处理
  const handleWelcomeComplete = async (childInfo: any) => {
    // 保存孩子信息到 localStorage
    const profile: ChildProfile = {
      name: childInfo.name,
      gender: childInfo.gender,
      birthDate: childInfo.birthDate,
      diagnosis: childInfo.diagnosis || '暂无评估信息',
      avatar: defaultAvatar,
      createdAt: childInfo.createdAt
    };

    localStorage.setItem('asd_floortime_child_profile', JSON.stringify(profile));
    setChildProfile(profile);

    // 标记不再是首次使用
    setIsFirstTime(false);
    setCurrentPage(Page.CHAT);
  };

  // 退出登录处理（从侧边栏调用）
  const handleLogout = () => {
    setShowLogoutConfirm(true);
  };

  const confirmLogout = () => {
    // 清空所有 localStorage 数据
    localStorage.clear();

    // 清空所有 sessionStorage 数据
    sessionStorage.clear();

    // 重置状态
    setInterestProfile(INITIAL_INTEREST_SCORES);
    setAbilityProfile(INITIAL_ABILITY_SCORES);
    setTrendData(INITIAL_TREND_DATA);
    setIsFirstTime(true);

    console.log('[Logout] 已清空所有本地数据');

    // 跳转到欢迎页面
    setCurrentPage(Page.WELCOME);
    setSidebarOpen(false);
    setShowLogoutConfirm(false);
  };

  const cancelLogout = () => {
    setShowLogoutConfirm(false);
  };

  const getHeaderTitle = () => {
    switch (currentPage) {
      case Page.WELCOME: return "欢迎使用";
      case Page.CHAT: return "AI 地板时光助手";
      case Page.CALENDAR: return "游戏计划";
      case Page.PROFILE: return `${childProfile?.name || '孩子'}的档案`;
      case Page.GAMES: return "游戏库";
      case Page.BEHAVIORS: return "行为数据";
      case Page.RADAR: return "兴趣雷达图";
      default: return "App";
    }
  };

  const handleExitInteraction = (type: 'report' | 'list') => {
    if (type === 'report') {
      setGameMode(GameState.SUMMARY);
    } else {
      if (activeGameId) {
        floorGameStorageService.updateGame(activeGameId, { status: 'aborted' });
      }
      setGameMode(GameState.LIST);
    }
    setShowExitConfirm(false);
  };

  return (
    <div className="max-w-md mx-auto h-screen bg-gray-50 flex flex-col shadow-2xl overflow-hidden relative">
      <Sidebar isOpen={isSidebarOpen} onClose={() => setSidebarOpen(false)} setPage={handleNavigate} onLogout={handleLogout} childProfile={childProfile} />

      {/* 退出登录确认对话框 */}
      {showLogoutConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={cancelLogout}></div>
          <div className="relative bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-100 mx-auto mb-4">
              <X className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800 text-center mb-2">确定要退出登录吗？</h3>
            <p className="text-gray-600 text-center mb-6">这将清空所有孩子的数据，包括兴趣档案、能力评估和互动记录。</p>
            <div className="flex gap-3">
              <button
                onClick={cancelLogout}
                className="flex-1 bg-gray-100 text-gray-700 py-3 rounded-xl font-bold hover:bg-gray-200 transition"
              >
                取消
              </button>
              <button
                onClick={confirmLogout}
                className="flex-1 bg-red-500 text-white py-3 rounded-xl font-bold hover:bg-red-600 transition"
              >
                确定退出
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 退出互动确认对话框 */}
      {showExitConfirm && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/50" onClick={() => setShowExitConfirm(false)}></div>
          <div className="relative bg-white rounded-2xl shadow-2xl p-6 max-w-sm w-full animate-in fade-in zoom-in-95">
            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-blue-100 mx-auto mb-4">
              <LogOut className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-800 text-center mb-2">退出本次互动？</h3>
            <p className="text-gray-600 text-center mb-6 text-sm">您可以选择生成评估报告以保存记录，或者直接退出本次游戏。</p>
            <div className="flex flex-col gap-3">
              <button
                onClick={() => handleExitInteraction('report')}
                className="w-full bg-primary text-white py-3 rounded-xl font-bold hover:bg-green-600 transition flex items-center justify-center"
              >
                <CheckCircle2 className="w-4 h-4 mr-2" />
                生成评估报告并保存
              </button>
              <button
                onClick={() => handleExitInteraction('list')}
                className="w-full bg-gray-100 text-gray-700 py-3 rounded-xl font-bold hover:bg-gray-200 transition text-sm"
              >
                直接返回列表 (不保存)
              </button>
              <button
                onClick={() => setShowExitConfirm(false)}
                className="w-full text-gray-400 py-2 font-medium hover:text-gray-600 transition text-xs"
              >
                继续游戏
              </button>
            </div>
          </div>
        </div>
      )}

      <header className="bg-white px-4 py-3 flex items-center justify-between border-b border-gray-100 z-10 sticky top-0"><div className="flex items-center">{currentPage !== Page.CHAT && currentPage !== Page.WELCOME && (<button onClick={() => setCurrentPage(Page.CHAT)} className="mr-3 text-gray-500 hover:text-primary transition"><ChevronLeft className="w-6 h-6" /></button>)}{currentPage === Page.CHAT && (<button onClick={() => setSidebarOpen(true)} className="mr-3 text-gray-700 hover:text-primary transition"><Menu className="w-6 h-6" /></button>)}<h1 className="text-lg font-bold text-gray-800">{getHeaderTitle()}</h1></div>{currentPage === Page.GAMES && gameMode === GameState.PLAYING ? (<button onClick={() => setShowExitConfirm(true)} className="text-red-500 font-bold text-sm h-8 flex items-center px-2 rounded hover:bg-red-50 transition">退出互动</button>) : currentPage !== Page.WELCOME && (<div className="w-8 h-8 rounded-full bg-gray-100 overflow-hidden border border-gray-200"><img src={childProfile?.avatar || defaultAvatar} alt="User" /></div>)}</header>
      <main className="flex-1 overflow-hidden relative">
        {currentPage === Page.WELCOME && <PageWelcome onComplete={handleWelcomeComplete} />}
        {currentPage === Page.CHAT && <PageAIChat navigateTo={handleNavigate} onStartGame={handleStartGame} onProfileUpdate={handleProfileUpdate} profileContext={profileContextString} childProfile={childProfile} />}
        {currentPage === Page.CALENDAR && <PageCalendar navigateTo={handleNavigate} onStartGame={handleStartGame} />}
        {currentPage === Page.PROFILE && <PageProfile trendData={trendData} interestProfile={interestProfile} abilityProfile={abilityProfile} onImportReport={handleImportReportFromProfile} onExportReport={handleExportReport} childProfile={childProfile} calculateAge={calculateAge} onUpdateAvatar={handleUpdateAvatar} />}
        {currentPage === Page.BEHAVIORS && <PageBehaviors childProfile={childProfile} />}
        {currentPage === Page.RADAR && <PageRadar />}
        {currentPage === Page.GAMES && (<PageGames initialGameId={activeGameId} gameState={gameMode} setGameState={setGameMode} onBack={() => setCurrentPage(Page.CALENDAR)} trendData={trendData} onUpdateTrend={handleUpdateTrend} onProfileUpdate={handleProfileUpdate} childProfile={childProfile} />)}
      </main>
    </div>
  );
}