
export enum Page {
  WELCOME = 'WELCOME',
  CHAT = 'CHAT',
  CALENDAR = 'CALENDAR',
  PROFILE = 'PROFILE',
  GAMES = 'GAMES',
  BEHAVIORS = 'BEHAVIORS',
  RADAR = 'RADAR'
}

export enum GameState {
  LIST = 'LIST',
  PLAYING = 'PLAYING',
  SUMMARY = 'SUMMARY'
}

export interface ChildProfile {
  name: string;
  gender: string;
  birthDate: string; // YYYY-MM-DD 格式
  diagnosis: string; // 孩子画像/诊断描述（最新的）
  avatar: string;
  createdAt: string; // 创建时间
}

// 报告类型
export type ReportType = 'hospital' | 'ai_generated' | 'assessment' | 'other';

// 报告（包括医疗报告和AI生成的评估报告）
export interface Report {
  id: string; // 报告唯一ID
  imageUrl?: string; // 报告原图（base64 或 URL），AI生成的评估报告可能没有
  ocrResult?: string; // OCR 识别结果，AI生成的评估报告可能没有
  summary: string; // 报告摘要（一句话）
  diagnosis: string; // 根据报告生成的孩子画像
  nextStepSuggestion?: string; // 下一步干预建议（仅评估报告有）
  date: string; // 报告日期 YYYY-MM-DD
  type: ReportType; // 报告类型
  createdAt: string; // 导入时间
}

// 为了向后兼容，保留 MedicalReport 类型别名
export type MedicalReport = Report;

export interface GameStep {
  instruction: string; // The main action
  guidance: string;    // The coaching tip/interaction guide
}

export interface Game {
  id: string;
  title: string;
  target: string;
  duration: string;
  reason: string;
  isVR?: boolean;     // New property for VR feature
  steps: GameStep[]; // Changed from string[] to GameStep[]
  summary?: string;   // 游戏玩法概要（用于阶段2展示）
  materials?: string[]; // 所需材料列表（用于阶段2展示）
}

export interface CalendarEvent {
  day: number;
  weekday: string;
  status: 'completed' | 'today' | 'future';
  gameTitle?: string;
  progress?: string;
  time?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'model';
  text: string;
  timestamp: Date;
  options?: string[]; // New: Suggested replies/chips for this message
}

export interface LogEntry {
  type: 'emoji' | 'voice';
  content: string;
  timestamp: Date;
}

// Used for UI display grouping
export interface InterestItem {
  name: string;
  level: 1 | 2 | 3 | 4 | 5; // 1 (low) to 5 (high interest)
}

export interface InterestCategory {
  category: string;
  items: InterestItem[];
}

// --- New Types for Interest Analysis Agent ---

export type InterestDimensionType = 
  | 'Visual' | 'Auditory' | 'Tactile' | 'Motor' 
  | 'Construction' | 'Order' | 'Cognitive' | 'Social';

// Store accumulated raw scores for Interests
export type UserInterestProfile = Record<InterestDimensionType, number>;

export interface InterestMatch {
  dimension: InterestDimensionType;
  weight: number; // 0.0 - 1.0 关联度：行为与该兴趣维度的关联程度
  intensity: number; // -1.0 - 1.0 强度：孩子对该维度的喜欢/讨厌程度（正值=喜欢，负值=讨厌，0=中性）
  reasoning: string;
}

export interface BehaviorAnalysis {
  behavior: string; // Extracted behavior description
  matches: InterestMatch[]; // Associated interest dimensions
  timestamp?: string; // 记录时间
  source?: 'GAME' | 'REPORT' | 'CHAT'; // 来源
  id?: string; // 唯一标识
}

// --- New Types for Ability/Radar Analysis ---

export type AbilityDimensionType = 
  | '自我调节' | '亲密感' | '双向沟通' | '复杂沟通' | '情绪思考' | '逻辑思维';

// Store accumulated scores for Radar Chart (0-100 scale)
export type UserAbilityProfile = Record<AbilityDimensionType, number>;

export interface EvaluationResult {
  score: number; // Composite score
  feedbackScore: number; // Single feedback quality score
  explorationScore: number; // Exploration/Breadth score
  summary: string;
  suggestion: string;
  interestAnalysis?: BehaviorAnalysis[]; 
}

// --- Module Separation Types ---

export interface AbilityUpdate {
  dimension: AbilityDimensionType;
  scoreChange: number; // e.g., +5, -2
  reason: string;
}

// The unified payload for updating the profile module
export interface ProfileUpdate {
  source: 'GAME' | 'REPORT' | 'CHAT';
  interestUpdates: BehaviorAnalysis[];
  abilityUpdates: AbilityUpdate[];
}

// --- Comprehensive Assessment Types ---

// 综合评估结果（简化版，只保留3个核心字段）
export interface ComprehensiveAssessment {
  id: string; // 唯一ID
  timestamp: string; // 评估时间
  summary: string; // 评估摘要（一句话，50字以内）
  currentProfile: string; // 当前孩子画像（详细描述，200-300字）
  nextStepSuggestion: string; // 下一步干预建议（150-200字）
}

// 游戏推荐结果
export interface GameRecommendation {
  id: string; // 推荐ID
  timestamp: string; // 推荐时间
  assessmentId: string; // 关联的评估ID
  game: Game;
  reason: string; // 推荐理由（详细）
  expectedOutcome: string; // 预期效果
  parentGuidance: string; // 家长指导要点
  adaptationSuggestions: string[]; // 适应性调整建议
}

// 游戏推荐对话状态
export type GameRecommendationState = 
  | 'idle'              // 空闲状态
  | 'discussing'        // 需求探讨阶段
  | 'designing'         // 方案细化阶段
  | 'confirming'        // 实施确认阶段
  | 'generating';       // 生成游戏卡片

// 游戏方向建议
export interface GameDirection {
  name: string;         // 方向名称
  reason: string;       // 推荐理由（必须引用具体数据）
  goal: string;         // 预期目标
  scene: string;        // 适合场景（室内/户外、时长、难度）
  _analysis?: string;   // LLM 分析总结（可选，用于显示）
}

// 候选游戏信息
export interface CandidateGame {
  id: string;
  title: string;
  summary: string;      // 玩法概述
  reason: string;       // 为什么适合这个孩子
  materials: string[];  // 需要准备的材料
  duration: string;     // 预计时长
  difficulty: number;   // 难度（1-5星）
  challenges: string[]; // 可能遇到的挑战和应对
  fullGame?: Game;      // 完整的游戏对象（可选）
  source?: 'library' | 'generated';  // 游戏来源：游戏库检索 or LLM生成
  _analysis?: string;   // LLM 分析总结（可选，用于显示）
}

// 游戏实施方案
export interface GameImplementationPlan {
  gameId: string;                    // 游戏ID
  gameTitle: string;                 // 游戏名称
  summary: string;                   // 游戏概要（2-3句话描述游戏的核心玩法）
  goal: string;                      // 游戏目标（明确的训练目标）
  steps: Array<{                     // 游戏步骤
    stepTitle: string;               // 步骤标题，如 "第一步：准备材料"
    instruction: string;             // 详细指令（家长应该做什么）
    expectedOutcome: string;         // 预期效果（这一步期望达到什么效果）
  }>;
  _analysis?: string;                // LLM 分析总结（可选，用于显示）
}

// 家长偏好
export interface ParentPreference {
  duration: 'short' | 'medium' | 'long'; // 游戏时长偏好
  difficulty: 'easy' | 'moderate' | 'challenging'; // 难度偏好
  environment: 'indoor' | 'outdoor' | 'both'; // 环境偏好
  focus: AbilityDimensionType[]; // 希望重点训练的能力
  avoidTopics?: string[]; // 需要避免的主题
  notes?: string; // 其他备注
}

// 用户偏好（从对话中提取）
export interface UserPreferences {
  environment?: 'indoor' | 'outdoor' | 'both' | 'any';
  duration?: 'short' | 'medium' | 'long' | 'any';
  avoidMaterials?: string[];  // 需要避免的材料
  preferMaterials?: string[]; // 偏好的材料
  otherRequirements?: string; // 其他要求
}

// 历史数据摘要（用于Agent输入）
export interface HistoricalDataSummary {
  recentAssessments: ComprehensiveAssessment[]; // 最近3次评估
  recentReports: Report[]; // 最近3份报告
  recentBehaviors: BehaviorAnalysis[]; // 最近10条行为记录
  recentGames: EvaluationResult[]; // 最近5次游戏评估
  interestTrends: Record<InterestDimensionType, number>; // 兴趣趋势
  abilityTrends: Record<AbilityDimensionType, number>; // 能力趋势
}

// --- Interest Radar Chart Types ---

// 雷达图查询类型
export type RadarChartType = 'weight' | 'intensity' | 'both';

// 雷达图数据点
export interface RadarDataPoint {
  dimension: InterestDimensionType; // 维度名称
  weight: number; // 关联度累计值
  intensity: number; // 强度累计值（可能为负）
  count: number; // 该维度的行为记录数量
}

// 雷达图查询参数
export interface RadarChartQuery {
  type: RadarChartType; // 查询类型
  startDate: string; // 开始日期 YYYY-MM-DD
  endDate: string; // 结束日期 YYYY-MM-DD
}

// 雷达图数据结构
export interface RadarChartData {
  type: RadarChartType;
  startDate: string;
  endDate: string;
  data: RadarDataPoint[]; // 8个维度的数据
  totalBehaviors: number; // 时间段内的总行为数
  summary: string; // 数据摘要
}
