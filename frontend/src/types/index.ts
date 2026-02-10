
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

// 医疗/评估报告
export interface MedicalReport {
  id: string; // 报告唯一ID
  imageUrl: string; // 报告原图（base64 或 URL）
  ocrResult: string; // OCR 识别结果
  summary: string; // 报告摘要（一句话）
  diagnosis: string; // 根据报告生成的孩子画像
  date: string; // 报告日期 YYYY-MM-DD
  type: ReportType; // 报告类型
  createdAt: string; // 导入时间
}

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
  source: 'GAME' | 'REPORT';
  interestUpdates: BehaviorAnalysis[];
  abilityUpdates: AbilityUpdate[];
}
