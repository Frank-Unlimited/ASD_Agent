
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
  PREVIEW = 'PREVIEW',
  PLAYING = 'PLAYING',
  FEEDBACK = 'FEEDBACK',
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
  stepTitle: string;   // Required title for the step
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
  status?: FloorGameStatus;  // 游戏状态
  date?: string;             // 日期（ISO string）
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

// 兴趣维度分析（单个维度）
export interface DimensionAnalysis {
  dimension: InterestDimensionType;
  strength: number;           // 强度 0-100
  exploration: number;        // 探索度 0-100
  category: 'leverage' | 'explore' | 'avoid' | 'neutral';
  specificObjects: string[];  // 从行为中提取的具体对象
  reasoning: string;
}

// 兴趣分析结果
export interface InterestAnalysisResult {
  summary: string;                           // 总体分析（100-150字）
  dimensions: DimensionAnalysis[];           // 8个维度分析
  leverageDimensions: string[];              // 可利用的维度
  exploreDimensions: string[];               // 可探索的维度
  avoidDimensions: string[];                 // 应避免的维度
  interventionSuggestions: InterventionSuggestion[];  // 3-5条干预建议
}

// 干预建议
export interface InterventionSuggestion {
  targetDimension: InterestDimensionType;
  strategy: 'leverage' | 'explore';
  suggestion: string;
  rationale: string;
  exampleActivities: string[];
}

// 游戏实施方案
export interface GameImplementationPlan {
  gameId: string;                    // 游戏ID
  gameTitle: string;                 // 游戏名称
  summary: string;                   // 游戏概要（2-3句话描述游戏的核心玩法）
  goal: string;                      // 游戏目标（明确的训练目标）
  steps: GameStep[];
  materials?: string[];               // 所需材料清单
  _analysis?: string;                // LLM 分析总结（可选，用于显示）
}

export type FloorGameStatus = 'pending' | 'completed' | 'aborted';

export interface GameReviewScores {
  childEngagement: number;      // 孩子参与度/配合度 0-100
  gameCompletion: number;       // 游戏完成度 0-100
  emotionalConnection: number;  // 情感连接质量 0-100
  communicationLevel: number;   // 沟通互动水平 0-100
  skillProgress: number;        // 目标能力进步 0-100
  parentExecution: number;      // 家长执行质量 0-100
}

export interface GameReviewResult {
  reviewSummary: string;        // 游戏过程总结与复盘
  scores: GameReviewScores;     // 多维度打分
  recommendation: 'continue' | 'adjust' | 'avoid';
  nextStepSuggestion: string;   // 下一步建议（含改进方向和理由）
}

export interface FloorGame {
  id: string;                  // 如 floor_game_1739612345678
  gameTitle: string;
  summary: string;
  goal: string;
  steps: GameStep[];
  materials?: string[];           // 所需材料清单
  _analysis?: string;

  status: FloorGameStatus;     // 未完成 / 已完成 / 中止
  dtstart: string;             // ISO string，开始时间
  dtend: string;               // ISO string，结束时间
  isVR: boolean;               // 是否VR游戏
  result?: string;             // 实施结果（预留）
  evaluation?: EvaluationResult; // 游戏结束后的评估结果
  chat_history_in_game?: string; // AI 视频通话的聊天记录（JSON 字符串）
  review?: GameReviewResult;     // 游戏复盘结果
}

export interface FeedbackData {
  q1: string; // Shared Attention
  q2: string; // Communication Circles
  q3: string; // Self-Regulation
  q4: string; // Open Notes / Flashpoints
  q5: string; // AI Helpfulness
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
  interestTrends: Record<InterestDimensionType, number>; // 兴趣趋势（各维度加权平均分）
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

// 反馈调查数据
export interface FeedbackData {
  q1: string; // 共同注意
  q2: string; // 沟通循环
  q3: string; // 情绪调节
  q4: string; // 互动随手记
  q5: string; // 助手反馈
}

