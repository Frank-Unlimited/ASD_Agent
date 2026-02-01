"""
业务逻辑层 Mock 服务（模块7-16）
"""
from typing import Any, Dict, List, Optional
from src.interfaces import (
    IAssessmentService,
    IWeeklyPlanService,
    IGuidanceService,
    IObservationService,
    IVideoValidationService,
    ISummaryService,
    IMemoryUpdateService,
    IReassessmentService,
    IChatAssistantService,
    IVisualizationService,
)


# ============ 模块7: 初始评估 Mock ============

class MockAssessmentService(IAssessmentService):
    """初始评估 Mock 服务"""
    
    def get_service_name(self) -> str:
        return "MockAssessmentService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def build_portrait(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """构建孩子画像"""
        print(f"[Mock Assessment] 构建画像")
        
        return {
            "strengths": ["视觉记忆好", "对规律敏感"],
            "weaknesses": ["眼神接触少", "语言发育迟缓"],
            "interests": ["旋转物体", "水流", "积木"],
            "emotionalMilestones": {
                "selfRegulation": 3,
                "intimacy": 2,
                "twoWayCommunication": 2,
                "complexCommunication": 1,
                "emotionalIdeas": 1,
                "logicalThinking": 1
            },
            "customDimensions": {
                "sensorySensitivity": {"level": "high", "triggers": ["loud_noise"]},
                "repetitiveBehaviors": {"frequency": "moderate"}
            }
        }
    
    async def create_observation_framework(self, portrait: Dict[str, Any]) -> Dict[str, Any]:
        """创建观察框架"""
        print(f"[Mock Assessment] 创建观察框架")
        
        return {
            "focusAreas": ["eyeContact", "twoWayCommunication", "emotionalRegulation"],
            "observationPoints": [
                "眼神接触的频率和时长",
                "主动发起互动的次数",
                "情绪调节能力"
            ]
        }


# ============ 模块8: 周计划推荐 Mock ============

class MockWeeklyPlanService(IWeeklyPlanService):
    """周计划推荐 Mock 服务"""
    
    def get_service_name(self) -> str:
        return "MockWeeklyPlanService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def generate_weekly_plan(
        self,
        child_id: str,
        child_profile: Dict[str, Any],
        current_context: Dict[str, Any],
        last_week_performance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成周计划"""
        print(f"[Mock WeeklyPlan] 生成周计划: {child_id}")
        
        return {
            "weeklyGoal": {
                "title": "建立稳定的眼神接触习惯",
                "description": "通过游戏互动，提升眼神接触频率",
                "targetDimensions": ["eyeContact", "twoWayCommunication"]
            },
            "dailyPlans": [
                {
                    "day": "周一",
                    "date": "2026-01-27",
                    "game": {"id": "game-001", "name": "积木传递游戏"},
                    "dailyGoal": {"title": "尝试3次眼神接触", "metrics": {"eyeContact": 3}},
                    "scheduledTime": "10:00",
                    "estimatedDuration": 15,
                    "reasoning": "从简单游戏开始，建立信心"
                },
                {
                    "day": "周二",
                    "date": "2026-01-28",
                    "game": {"id": "game-001", "name": "积木传递游戏"},
                    "dailyGoal": {"title": "达到5次眼神接触", "metrics": {"eyeContact": 5}},
                    "scheduledTime": "10:00",
                    "estimatedDuration": 15,
                    "reasoning": "重复练习，巩固效果"
                }
            ],
            "status": "draft"
        }
    
    async def calculate_priority_dimensions(
        self,
        metrics: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """计算优先维度"""
        print(f"[Mock WeeklyPlan] 计算优先维度")
        
        return ["eyeContact", "twoWayCommunication"]


# ============ 模块9-16: 其他业务服务 Mock（简化实现）============

class MockGuidanceService(IGuidanceService):
    """实时指引 Mock"""
    
    def get_service_name(self) -> str:
        return "MockGuidanceService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def get_step_guidance(self, game_id: str, step: int, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Guidance] 获取步骤指引: game={game_id}, step={step}")
        return {"instruction": "坐在孩子对面，拿起一块积木", "audioPath": "/mock/audio/step1.mp3"}
    
    async def recommend_phrases(self, situation: str, child_profile: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Guidance] 推荐话术: {situation}")
        return {"recommended": ["看看孩子会怎么做"], "avoid": ["看着妈妈"]}


class MockObservationService(IObservationService):
    """观察捕获 Mock"""
    
    def get_service_name(self) -> str:
        return "MockObservationService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def capture_quick_observation(self, session_id: str, observation_type: str, timestamp: str) -> Dict[str, Any]:
        print(f"[Mock Observation] 快捷观察: type={observation_type}")
        return {"observationId": "obs-001", "type": observation_type, "timestamp": timestamp}
    
    async def capture_voice_observation(self, session_id: str, audio_path: str) -> Dict[str, Any]:
        print(f"[Mock Observation] 语音观察: {audio_path}")
        return {"observationId": "obs-002", "text": "孩子今天很开心"}
    
    async def structure_observation(self, raw_text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Observation] 结构化观察")
        return {"structured": True, "content": raw_text}


class MockVideoValidationService(IVideoValidationService):
    """视频验证 Mock"""
    
    def get_service_name(self) -> str:
        return "MockVideoValidationService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def analyze_and_validate(self, session_id: str, video_path: str, quick_observations: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"[Mock VideoValidation] 分析并验证")
        return {"validated": True, "conflicts": [], "missed": []}
    
    async def cross_validate(self, quick_observations: List[Dict[str, Any]], video_analysis: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock VideoValidation] 交叉验证")
        return {"validatedObservations": quick_observations}


class MockSummaryService(ISummaryService):
    """总结生成 Mock"""
    
    def get_service_name(self) -> str:
        return "MockSummaryService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def generate_preliminary_summary(self, session_id: str, session_data: Dict[str, Any], historical_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Summary] 生成初步总结")
        return {"highlights": ["眼神接触5次"], "concerns": []}
    
    async def generate_feedback_form(self, preliminary_summary: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Summary] 生成反馈表")
        return {"questions": [{"id": "q1", "question": "孩子今天状态如何？", "type": "rating"}]}
    
    async def generate_final_summary(self, session_id: str, all_data: Dict[str, Any], parent_feedback: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Summary] 生成最终总结")
        return {"summary": "孩子今天表现很好", "milestones": []}


class MockMemoryUpdateService(IMemoryUpdateService):
    """记忆更新 Mock"""
    
    def get_service_name(self) -> str:
        return "MockMemoryUpdateService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def update_memory(self, child_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock MemoryUpdate] 更新记忆")
        return {"updated": True}
    
    async def refresh_context(self, child_id: str) -> Dict[str, Any]:
        print(f"[Mock MemoryUpdate] 刷新上下文")
        return {"recentTrends": {}, "attentionPoints": []}


class MockReassessmentService(IReassessmentService):
    """再评估 Mock"""
    
    def get_service_name(self) -> str:
        return "MockReassessmentService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def reassess_child(self, child_id: str, session_data: Dict[str, Any], current_context: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Reassessment] 再评估")
        return {"progressReport": {}, "needsAdjustment": False}
    
    async def update_portrait(self, child_id: str, reassessment_result: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Reassessment] 更新画像")
        return {"updated": True}
    
    async def check_adjustment_needed(self, reassessment_result: Dict[str, Any]) -> bool:
        print(f"[Mock Reassessment] 检查是否需要调整")
        return False


class MockChatAssistantService(IChatAssistantService):
    """对话助手 Mock"""
    
    def get_service_name(self) -> str:
        return "MockChatAssistantService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def chat(self, child_id: str, user_message: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"[Mock Chat] 对话: {user_message}")
        return {"response": "这是一个Mock回答", "sources": []}
    
    async def route_query(self, query: str) -> str:
        print(f"[Mock Chat] 路由查询: {query}")
        return "general"


class MockVisualizationService(IVisualizationService):
    """可视化 Mock"""
    
    def get_service_name(self) -> str:
        return "MockVisualizationService"
    
    def get_service_version(self) -> str:
        return "1.0.0-mock"
    
    async def generate_radar_chart(self, child_id: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        print(f"[Mock Visualization] 生成雷达图")
        return {"chartData": []}
    
    async def generate_timeline(self, child_id: str, milestones: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"[Mock Visualization] 生成时间线")
        return {"timelineData": []}
    
    async def generate_trend_chart(self, child_id: str, dimension: str, time_range: str) -> Dict[str, Any]:
        print(f"[Mock Visualization] 生成趋势图")
        return {"trendData": []}
    
    async def generate_parent_report(self, child_id: str, time_range: str) -> str:
        print(f"[Mock Visualization] 生成家长报告")
        return "/mock/reports/parent_report.pdf"
    
    async def generate_medical_report(self, child_id: str, time_range: str) -> str:
        print(f"[Mock Visualization] 生成医生报告")
        return "/mock/reports/medical_report.pdf"
