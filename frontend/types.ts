
export enum Page {
  CHAT = 'CHAT',
  CALENDAR = 'CALENDAR',
  PROFILE = 'PROFILE',
  GAMES = 'GAMES'
}

export enum GameState {
  LIST = 'LIST',
  PLAYING = 'PLAYING',
  SUMMARY = 'SUMMARY'
}

export interface ChildProfile {
  name: string;
  age: number;
  diagnosis: string;
  avatar: string;
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
  weight: number; // 0.0 - 1.0
  reasoning: string;
}

export interface BehaviorAnalysis {
  behavior: string; // Extracted behavior description
  matches: InterestMatch[]; // Associated interest dimensions
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
