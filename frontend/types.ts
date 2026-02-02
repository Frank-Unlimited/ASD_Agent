export enum Page {
  WELCOME = 'WELCOME',
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
}

export interface LogEntry {
  type: 'emoji' | 'voice';
  content: string;
  timestamp: Date;
}

export interface InterestItem {
  name: string;
  level: 1 | 2 | 3 | 4 | 5; // 1 (low) to 5 (high interest)
}

export interface InterestCategory {
  category: string;
  items: InterestItem[];
}