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
  Tag,
  Keyboard
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
import { Page, GameState, ChildProfile, Game, CalendarEvent, ChatMessage, LogEntry, InterestCategory, BehaviorAnalysis, InterestDimensionType, EvaluationResult, UserInterestProfile, UserAbilityProfile, AbilityDimensionType, ProfileUpdate, MedicalReport } from './types';
import { api } from './services/api';
import { multimodalService } from './services/multimodalService';
import { fileUploadService } from './services/fileUpload';
import { speechService } from './services/speechService';
import { reportStorageService } from './services/reportStorage';
import { ASD_REPORT_ANALYSIS_PROMPT } from './prompts';
import { MOCK_GAMES, WEEK_DATA, INITIAL_TREND_DATA, INITIAL_INTEREST_SCORES, INITIAL_ABILITY_SCORES } from './constants/mockData';
import { getDimensionConfig, calculateAge, formatTime, getInterestLevel } from './utils/helpers';

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
        </nav>
        <div className="mt-auto pt-6 border-t border-gray-100 relative">
          <div 
            className="flex items-center space-x-3 cursor-pointer hover:bg-gray-50 p-2 rounded-lg transition" 
            onClick={() => setShowProfileMenu(!showProfileMenu)}
          >
            <img src={childProfile?.avatar || 'https://ui-avatars.com/api/?name=User&background=random&size=200'} alt="Profile" className="w-10 h-10 rounded-full" />
            <div className="flex-1">
              <p className="font-semibold text-sm">{childProfile?.name || '未设置'}</p>
              <p className="text-xs text-gray-500">{childProfile?.diagnosis || '暂无信息'}</p>
            </div>
            <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform ${showProfileMenu ? 'rotate-90' : ''}`} />
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
              const report: MedicalReport = {
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
                  className={`flex-1 py-3 rounded-xl border-2 transition ${
                    gender === '男' ? 'border-primary bg-primary/10 text-primary font-medium' : 'border-gray-300 text-gray-600'
                  }`}
                >
                  男孩
                </button>
                <button
                  onClick={() => setGender('女')}
                  className={`flex-1 py-3 rounded-xl border-2 transition ${
                    gender === '女' ? 'border-primary bg-primary/10 text-primary font-medium' : 'border-gray-300 text-gray-600'
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
                      className={`border-2 border-dashed rounded-xl p-8 text-center transition ${
                        isAnalyzing ? 'border-gray-300 bg-gray-50 cursor-not-allowed' : 'border-gray-300 hover:border-primary hover:bg-primary/5 cursor-pointer'
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
                className={`flex-1 py-3 rounded-xl font-medium transition ${
                  canSubmit
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
  const [voiceMode, setVoiceMode] = useState(false); // 语音模式开关
  const [recognizing, setRecognizing] = useState(false); // 识别中状态
  const [showNoSpeechToast, setShowNoSpeechToast] = useState(false); // 显示"未识别到文字"提示
  
  const [checkInStep, setCheckInStep] = useState(0); 
  const [targetGameId, setTargetGameId] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
    if (!file) return;

    // 检测文件类型
    const category = fileUploadService.categorizeFile(file);
    
    // 开始加载（不显示上传消息）
    setLoading(true);

    try {
      // 处理图片文件
      if (category === 'image') {
        const result = await multimodalService.parseImage(file);
        
        if (result.success) {
          // 显示图片预览和分析结果
          const replyText = `**📸 图片分析完成**\n\n${result.content}`;
          setMessages(prev => [...prev, { 
            id: (Date.now() + 1).toString(), 
            role: 'model', 
            text: replyText, 
            timestamp: new Date() 
          }]);
        } else {
          throw new Error(result.error || '图片分析失败');
        }
      }
      // 处理视频文件
      else if (category === 'video') {
        const result = await multimodalService.parseVideo(file);
        
        if (result.success) {
          const replyText = `**🎬 视频分析完成**\n\n${result.content}`;
          setMessages(prev => [...prev, { 
            id: (Date.now() + 1).toString(), 
            role: 'model', 
            text: replyText, 
            timestamp: new Date() 
          }]);
        } else {
          throw new Error(result.error || '视频分析失败');
        }
      }
      // 处理文档文件（原有逻辑）
      else if (category === 'document') {
        let textContent = file.type === "text/plain" ? await file.text() : `文件名: ${file.name}。假设这是一份医疗评估报告。`;
        
        // *** Evaluation Agent Call (Report) ***
        const analysis = await api.analyzeReport(textContent);
        onProfileUpdate(analysis);

        const abilityChanges = analysis.abilityUpdates.map(u => `${u.dimension} ${u.scoreChange > 0 ? '+' : ''}${u.scoreChange}`).join('、');
        const replyText = `收到您的报告。我已经分析完毕并更新了孩子档案。\n\n**分析结果：**\n- 发现 ${analysis.interestUpdates.length} 个兴趣点\n- 能力维度调整：${abilityChanges || "无明显变化"}`;
        
        setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), role: 'model', text: replyText, timestamp: new Date() }]);
      }
      // 不支持的文件类型
      else {
        throw new Error('不支持的文件类型');
      }

    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : "文件处理失败，请稍后再试。";
      setMessages(prev => [...prev, { 
        id: Date.now().toString(), 
        role: 'model', 
        text: `❌ ${errorMsg}`, 
        timestamp: new Date() 
      }]);
    } finally {
      setLoading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
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
       {/* 未识别到文字的提示 Toast */}
       {showNoSpeechToast && (
         <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 animate-in fade-in">
           <div className="bg-gray-800/40 text-white px-6 py-3 rounded-2xl shadow-lg backdrop-blur-sm">
             <p className="text-base font-medium">未识别到文字</p>
           </div>
         </div>
       )}
       
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
                className={`flex-1 py-1.5 rounded-full font-bold transition transform active:scale-95 flex items-center justify-center ${
                  recognizing 
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

const PageProfile = ({ trendData, interestProfile, abilityProfile, onImportReport, onExportReport, childProfile, calculateAge }: { trendData: any[], interestProfile: UserInterestProfile, abilityProfile: UserAbilityProfile, onImportReport: (file: File) => void, onExportReport: () => void, childProfile: ChildProfile | null, calculateAge: (birthDate: string) => number }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [showReportList, setShowReportList] = useState(false);
  const [selectedReport, setSelectedReport] = useState<MedicalReport | null>(null);
  const [reports, setReports] = useState<MedicalReport[]>([]);
  
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

  const age = childProfile ? calculateAge(childProfile.birthDate) : 0;
  const latestReport = reportStorageService.getLatestReport();

  // 报告详情弹窗
  const ReportDetailModal = ({ report, onClose }: { report: MedicalReport, onClose: () => void }) => (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
        <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <h3 className="font-bold text-gray-800">报告详情</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <div className="p-6 space-y-4">
          {/* 报告摘要 */}
          <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
            <h5 className="text-sm font-bold text-purple-700 mb-2 flex items-center">
              <Sparkles className="w-4 h-4 mr-2" />
              报告摘要
            </h5>
            <p className="text-sm text-gray-700">{report.summary}</p>
          </div>

          {/* 报告原图 */}
          <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
            <h5 className="text-sm font-bold text-gray-700 mb-3 flex items-center">
              <FileText className="w-4 h-4 mr-2 text-blue-600" />
              报告原图
            </h5>
            <img 
              src={`data:image/jpeg;base64,${report.imageUrl}`} 
              alt="报告原图" 
              className="w-full rounded-lg border border-gray-300"
            />
          </div>

          {/* OCR 提取结果 */}
          <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
            <h5 className="text-sm font-bold text-blue-700 mb-3 flex items-center">
              <Eye className="w-4 h-4 mr-2" />
              文字提取
            </h5>
            <div className="bg-white rounded-lg p-3 max-h-60 overflow-y-auto text-xs text-gray-700 leading-relaxed whitespace-pre-wrap">
              {report.ocrResult}
            </div>
          </div>

          {/* 孩子画像 */}
          <div className="bg-green-50 rounded-xl p-4 border border-green-200">
            <h5 className="text-sm font-bold text-green-700 mb-3 flex items-center">
              <User className="w-4 h-4 mr-2" />
              孩子画像
            </h5>
            <div className="bg-white rounded-lg p-3 text-sm text-gray-700 leading-relaxed">
              {report.diagnosis}
            </div>
          </div>

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
                   report.type === 'ai_generated' ? 'AI生成' : 
                   report.type === 'assessment' ? '评估报告' : '其他'}
                </span>
              </div>
              <div className="col-span-2">
                <span className="text-gray-500">导入时间：</span>
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
                  <img 
                    src={`data:image/jpeg;base64,${report.imageUrl}`} 
                    alt="报告缩略图" 
                    className="w-16 h-16 rounded-lg object-cover border border-gray-200"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-bold text-gray-800 truncate">{report.summary}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      {report.date} · {report.type === 'hospital' ? '医院报告' : 'AI生成'}
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
        <img 
          src={childProfile?.avatar || 'https://ui-avatars.com/api/?name=User&background=random&size=200'} 
          className="w-24 h-24 rounded-full border-4 border-white shadow-lg" 
          alt={childProfile?.name || '孩子'} 
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
  
  // 欢迎页面完成处理
  const handleWelcomeComplete = async (childInfo: any) => {
    // 保存孩子信息到 localStorage
    const profile: ChildProfile = {
      name: childInfo.name,
      gender: childInfo.gender,
      birthDate: childInfo.birthDate,
      diagnosis: childInfo.diagnosis || '暂无评估信息',
      avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(childInfo.name)}&background=random&size=200`,
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
    
    // 重置状态
    setInterestProfile(INITIAL_INTEREST_SCORES);
    setAbilityProfile(INITIAL_ABILITY_SCORES);
    setTrendData(INITIAL_TREND_DATA);
    setIsFirstTime(true);
    
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
      default: return "App"; 
    } 
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
      
      <header className="bg-white px-4 py-3 flex items-center justify-between border-b border-gray-100 z-10 sticky top-0"><div className="flex items-center">{currentPage !== Page.CHAT && currentPage !== Page.WELCOME && (<button onClick={() => setCurrentPage(Page.CHAT)} className="mr-3 text-gray-500 hover:text-primary transition"><ChevronLeft className="w-6 h-6" /></button>)}{currentPage === Page.CHAT && (<button onClick={() => setSidebarOpen(true)} className="mr-3 text-gray-700 hover:text-primary transition"><Menu className="w-6 h-6" /></button>)}<h1 className="text-lg font-bold text-gray-800">{getHeaderTitle()}</h1></div>{currentPage === Page.GAMES && gameMode === GameState.PLAYING ? (<button onClick={() => setGameMode(GameState.SUMMARY)} className="text-red-500 font-bold text-sm h-8 flex items-center px-2 rounded hover:bg-red-50 transition">结束</button>) : currentPage !== Page.WELCOME && (<div className="w-8 h-8 rounded-full bg-gray-100 overflow-hidden border border-gray-200"><img src={childProfile?.avatar || 'https://ui-avatars.com/api/?name=User&background=random&size=200'} alt="User" /></div>)}</header>
      <main className="flex-1 overflow-hidden relative">
        {currentPage === Page.WELCOME && <PageWelcome onComplete={handleWelcomeComplete} />}
        {currentPage === Page.CHAT && <PageAIChat navigateTo={handleNavigate} onStartGame={handleStartGame} onProfileUpdate={handleProfileUpdate} profileContext={profileContextString} />}
        {currentPage === Page.CALENDAR && <PageCalendar navigateTo={handleNavigate} onStartGame={handleStartGame} />}
        {currentPage === Page.PROFILE && <PageProfile trendData={trendData} interestProfile={interestProfile} abilityProfile={abilityProfile} onImportReport={handleImportReportFromProfile} onExportReport={handleExportReport} childProfile={childProfile} calculateAge={calculateAge} />}
        {currentPage === Page.GAMES && (<PageGames initialGameId={activeGameId} gameState={gameMode} setGameState={setGameMode} onBack={() => setCurrentPage(Page.CALENDAR)} trendData={trendData} onUpdateTrend={handleUpdateTrend} onProfileUpdate={handleProfileUpdate} />)}
      </main>
    </div>
  );
}