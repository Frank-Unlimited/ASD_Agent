
export enum Page {
  WELCOME = 'WELCOME',
  CHAT = 'CHAT',
  CALENDAR = 'CALENDAR',
  PROFILE = 'PROFILE',
  GAMES = 'GAMES',
  BEHAVIORS = 'BEHAVIORS'
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

// 家长偏好
export interface ParentPreference {
  duration: 'short' | 'medium' | 'long'; // 游戏时长偏好
  difficulty: 'easy' | 'moderate' | 'challenging'; // 难度偏好
  environment: 'indoor' | 'outdoor' | 'both'; // 环境偏好
  focus: AbilityDimensionType[]; // 希望重点训练的能力
  avoidTopics?: string[]; // 需要避免的主题
  notes?: string; // 其他备注
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
