/**
 * Prompts 统一导出
 */

export { CHAT_SYSTEM_PROMPT } from './chatSystemPrompt';
export {
  REACT_INTEREST_ANALYSIS_SYSTEM_PROMPT,
  REACT_GAME_PLAN_SYSTEM_PROMPT
} from './conversationalSystemPrompt';
export { ASSESSMENT_SYSTEM_PROMPT } from './assessmentPrompt';
export { BEHAVIOR_ANALYSIS_SYSTEM_PROMPT, BEHAVIOR_EXTRACTOR_SYSTEM_PROMPT } from './behaviorAnalysisPrompt';
export { ONLINE_SEARCH_PARSER_SYSTEM_PROMPT } from './onlineSearchPrompt';
export { GAME_REVIEW_SYSTEM_PROMPT, buildGameReviewPrompt } from './gameReviewPrompt';
export { GAME_ASSISTANT_PROMPT } from './gameAssistantPrompt';
export { buildInterestAnalysisPrompt } from './interestAnalysisPrompt';
export { buildFloorGamePlanPrompt } from './floorGamePlanPrompt';
export { ASD_REPORT_ANALYSIS_PROMPT } from './asd-report-analysis';
export { MEDICAL_REPORT_ANALYSIS_PROMPT, VERBAL_DESCRIPTION_ANALYSIS_PROMPT } from './diagnosis-analysis';
export { DEFAULT_IMAGE_ANALYSIS_PROMPT, DEFAULT_VIDEO_ANALYSIS_PROMPT } from './multimodal-analysis';

export type { InterestAnalysisPromptParams } from './interestAnalysisPrompt';
export type { FloorGamePlanPromptParams } from './floorGamePlanPrompt';
