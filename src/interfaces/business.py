"""
业务逻辑层接口定义（模块7-16）
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from src.interfaces.base import BaseService


# ============ 模块7: 初始评估模块 ============

class IAssessmentService(BaseService):
    """初始评估接口"""
    
    @abstractmethod
    async def build_portrait(
        self, 
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """构建孩子画像"""
        pass
    
    @abstractmethod
    async def create_observation_framework(
        self, 
        portrait: Dict[str, Any]
    ) -> Dict[str, Any]:
        """创建观察框架"""
        pass


# ============ 模块8: 周计划推荐模块 ============

class IWeeklyPlanService(BaseService):
    """周计划推荐接口"""
    
    @abstractmethod
    async def generate_weekly_plan(
        self,
        child_id: str,
        child_profile: Dict[str, Any],
        current_context: Dict[str, Any],
        last_week_performance: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """生成周计划"""
        pass
    
    @abstractmethod
    async def calculate_priority_dimensions(
        self,
        metrics: Dict[str, Any],
        trends: Dict[str, Any]
    ) -> List[str]:
        """计算优先维度"""
        pass


# ============ 模块9: 实时指引模块 ============

class IGuidanceService(BaseService):
    """实时指引接口"""
    
    @abstractmethod
    async def get_step_guidance(
        self,
        game_id: str,
        step: int,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """获取步骤指引"""
        pass
    
    @abstractmethod
    async def recommend_phrases(
        self,
        situation: str,
        child_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """推荐话术"""
        pass


# ============ 模块10: 观察捕获模块 ============

class IObservationService(BaseService):
    """观察捕获接口"""
    
    @abstractmethod
    async def capture_quick_observation(
        self,
        session_id: str,
        observation_type: str,
        timestamp: str
    ) -> Dict[str, Any]:
        """捕获快捷观察"""
        pass
    
    @abstractmethod
    async def capture_voice_observation(
        self,
        session_id: str,
        audio_path: str
    ) -> Dict[str, Any]:
        """捕获语音观察"""
        pass
    
    @abstractmethod
    async def structure_observation(
        self,
        raw_text: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """结构化观察内容"""
        pass


# ============ 模块11: 视频分析与验证模块 ============

class IVideoValidationService(BaseService):
    """视频分析与验证接口"""
    
    @abstractmethod
    async def analyze_and_validate(
        self,
        session_id: str,
        video_path: str,
        quick_observations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """分析视频并验证观察"""
        pass
    
    @abstractmethod
    async def cross_validate(
        self,
        quick_observations: List[Dict[str, Any]],
        video_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """交叉验证"""
        pass


# ============ 模块12: 总结生成模块 ============

class ISummaryService(BaseService):
    """总结生成接口"""
    
    @abstractmethod
    async def generate_preliminary_summary(
        self,
        session_id: str,
        session_data: Dict[str, Any],
        historical_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成初步总结"""
        pass
    
    @abstractmethod
    async def generate_feedback_form(
        self,
        preliminary_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成反馈表"""
        pass
    
    @abstractmethod
    async def generate_final_summary(
        self,
        session_id: str,
        all_data: Dict[str, Any],
        parent_feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成最终总结"""
        pass


# ============ 模块13: 记忆更新模块 ============

class IMemoryUpdateService(BaseService):
    """记忆更新接口"""
    
    @abstractmethod
    async def update_memory(
        self,
        child_id: str,
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新记忆网络"""
        pass
    
    @abstractmethod
    async def refresh_context(
        self,
        child_id: str
    ) -> Dict[str, Any]:
        """刷新上下文"""
        pass


# ============ 模块14: 再评估模块 ============

class IReassessmentService(BaseService):
    """再评估接口"""
    
    @abstractmethod
    async def reassess_child(
        self,
        child_id: str,
        session_data: Dict[str, Any],
        current_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """重新评估孩子"""
        pass
    
    @abstractmethod
    async def update_portrait(
        self,
        child_id: str,
        reassessment_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新画像"""
        pass
    
    @abstractmethod
    async def check_adjustment_needed(
        self,
        reassessment_result: Dict[str, Any]
    ) -> bool:
        """检查是否需要调整计划"""
        pass


# ============ 模块15: 对话助手模块 ============

class IChatAssistantService(BaseService):
    """对话助手接口"""
    
    @abstractmethod
    async def chat(
        self,
        child_id: str,
        user_message: str,
        conversation_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """对话"""
        pass
    
    @abstractmethod
    async def route_query(
        self,
        query: str
    ) -> str:
        """路由查询（判断查询类型）"""
        pass


# ============ 模块16: 可视化与报告模块 ============

class IVisualizationService(BaseService):
    """可视化与报告接口"""
    
    @abstractmethod
    async def generate_radar_chart(
        self,
        child_id: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """生成雷达图数据"""
        pass
    
    @abstractmethod
    async def generate_timeline(
        self,
        child_id: str,
        milestones: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成时间线数据"""
        pass
    
    @abstractmethod
    async def generate_trend_chart(
        self,
        child_id: str,
        dimension: str,
        time_range: str
    ) -> Dict[str, Any]:
        """生成趋势图数据"""
        pass
    
    @abstractmethod
    async def generate_parent_report(
        self,
        child_id: str,
        time_range: str
    ) -> str:
        """生成家长版报告（返回PDF路径）"""
        pass
    
    @abstractmethod
    async def generate_medical_report(
        self,
        child_id: str,
        time_range: str
    ) -> str:
        """生成医生版报告（返回PDF路径）"""
        pass
