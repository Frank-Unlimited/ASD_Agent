"""聊天 Agent 的 Tool 集合"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import json


class RecordBehaviorParams(BaseModel):
    child_id: str
    description: str
    input_type: str = "text"


class RecommendGameParams(BaseModel):
    child_id: str
    context: Optional[str] = None


class GetChildProfileParams(BaseModel):
    child_id: str


class GetLatestAssessmentParams(BaseModel):
    child_id: str
    assessment_type: Optional[str] = None


class GetRecentGamesParams(BaseModel):
    child_id: str
    limit: int = 10


class GenerateAssessmentParams(BaseModel):
    child_id: str
    assessment_type: str = "comprehensive"  # comprehensive, interest_mining, trend_analysis


class QueryBehaviorsParams(BaseModel):
    child_id: str
    limit: int = 20
    keyword: Optional[str] = None


class QueryInterestsParams(BaseModel):
    child_id: str


class QueryDimensionProgressParams(BaseModel):
    child_id: str
    dimension_name: Optional[str] = None


class ChatTools:
    def __init__(self, memory_service, sqlite_service, observation_service,
                 game_recommender, game_summarizer, assessment_service, report_service):
        self.memory_service = memory_service
        self.sqlite_service = sqlite_service
        self.observation_service = observation_service
        self.game_recommender = game_recommender
        self.game_summarizer = game_summarizer
        self.assessment_service = assessment_service
        self.report_service = report_service
    
    async def record_behavior(self, params: RecordBehaviorParams) -> Dict[str, Any]:
        try:
            result = await self.memory_service.record_behavior(
                child_id=params.child_id, raw_input=params.description, input_type=params.input_type)
            
            response = {"success": True, "message": "行为记录成功", "behavior_id": result.get("behavior_id")}
            print(f"\n[ChatTools] 📋 record_behavior 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ record_behavior 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def recommend_game(self, params: RecommendGameParams) -> Dict[str, Any]:
        try:
            # 构建请求
            from src.models.game import GameRecommendRequest
            request = GameRecommendRequest(
                child_id=params.child_id,
                context=params.context or ""
            )
            
            result = await self.game_recommender.recommend_game(request)
            
            # 提取游戏信息
            game_plan = result.game_plan
            game_info = {
                "game_id": game_plan.game_id,
                "name": game_plan.title,
                "description": game_plan.description,
                "design_rationale": game_plan.design_rationale,
                "steps": [step.description for step in game_plan.steps] if game_plan.steps else []
            }
            
            response = {
                "success": True, 
                "game": game_info,
                "message": f"已为您推荐游戏：{game_info['name']}"
            }
            print(f"\n[ChatTools] 📋 recommend_game 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ recommend_game 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def get_child_profile(self, params: GetChildProfileParams) -> Dict[str, Any]:
        try:
            profile = self.sqlite_service.get_child(params.child_id)
            if not profile:
                return {"success": False, "error": f"档案不存在: {params.child_id}"}
            
            response = {"success": True, "profile": {"child_id": profile.child_id, "name": profile.name, "diagnosis": profile.diagnosis}}
            print(f"\n[ChatTools] 📋 get_child_profile 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ get_child_profile 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def get_latest_assessment(self, params: GetLatestAssessmentParams) -> Dict[str, Any]:
        try:
            assessment = await self.memory_service.get_latest_assessment(
                child_id=params.child_id, assessment_type=params.assessment_type)
            if not assessment:
                return {"success": False, "error": "暂无评估记录"}
            
            analysis = assessment.get("analysis", {})
            overall = analysis.get("overall_assessment", "")[:200]
            
            response = {"success": True, "assessment": {"assessment_id": assessment.get("assessment_id"),
                    "overall_assessment": overall}}
            print(f"\n[ChatTools] 📋 get_latest_assessment 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ get_latest_assessment 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def get_recent_games(self, params: GetRecentGamesParams) -> Dict[str, Any]:
        try:
            games = await self.memory_service.get_recent_games(child_id=params.child_id, limit=params.limit)
            game_list = []
            for game in games:
                created_at = game.get("created_at", "")
                date_str = created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)[:10]
                game_list.append({"game_id": game.get("game_id"), "name": game.get("name"), "date": date_str})
            
            response = {"success": True, "games": game_list}
            print(f"\n[ChatTools] 📋 get_recent_games 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ get_recent_games 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def generate_assessment(self, params: GenerateAssessmentParams) -> Dict[str, Any]:
        try:
            # 调用评估服务生成完整评估
            from src.models.assessment import AssessmentRequest
            request = AssessmentRequest(
                child_id=params.child_id,
                assessment_type=params.assessment_type
            )
            
            result = await self.assessment_service.generate_comprehensive_assessment(request)
            
            # 提取关键信息
            assessment_info = {
                "assessment_id": result.assessment_id,
                "assessment_type": result.report.assessment_type if result.report else "comprehensive",
                "overall_assessment": result.report.overall_assessment[:200] if result.report else "",
                "overall_score": result.report.overall_score if result.report else 0,
                "recommendations": result.report.recommendations[:3] if result.report and result.report.recommendations else []
            }
            
            response = {
                "success": True,
                "assessment": assessment_info,
                "message": f"✅ 评估已完成：{result.assessment_id}"
            }
            print(f"\n[ChatTools] 📋 generate_assessment 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ generate_assessment 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def query_behaviors(self, params: QueryBehaviorsParams) -> Dict[str, Any]:
        """查询行为记录"""
        try:
            filters = {"limit": params.limit}
            if params.keyword:
                filters["keyword"] = params.keyword
            
            behaviors = await self.memory_service.get_behaviors(
                child_id=params.child_id,
                filters=filters
            )
            
            behavior_list = []
            for behavior in behaviors:
                created_at = behavior.get("created_at", "")
                date_str = created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)[:10]
                behavior_list.append({
                    "date": date_str,
                    "description": behavior.get("description", "")[:100],  # 限制长度
                    "behavior_id": behavior.get("behavior_id", "")
                })
            
            response = {
                "success": True,
                "behaviors": behavior_list,
                "total": len(behavior_list)
            }
            print(f"\n[ChatTools] 📋 query_behaviors 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ query_behaviors 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def query_interests(self, params: QueryInterestsParams) -> Dict[str, Any]:
        """查询孩子的兴趣点"""
        try:
            # 从 Memory 服务获取最新的兴趣数据
            latest_interest = await self.memory_service.get_latest_interest(params.child_id)
            
            if not latest_interest:
                return {"success": False, "error": "暂无兴趣数据"}
            
            # 提取兴趣维度信息
            dimensions = latest_interest.get("dimensions", {})
            interest_summary = []
            
            for dim_name, dim_data in dimensions.items():
                if isinstance(dim_data, dict):
                    interest_summary.append({
                        "dimension": dim_name,
                        "strength": dim_data.get("strength", 0),
                        "key_objects": [obj.get("name") for obj in dim_data.get("key_objects", [])[:3]]  # 只取前3个
                    })
            
            response = {
                "success": True,
                "interests": interest_summary,
                "overall_breadth": latest_interest.get("overall_breadth", "unknown")
            }
            print(f"\n[ChatTools] 📋 query_interests 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ query_interests 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}
    
    async def query_dimension_progress(self, params: QueryDimensionProgressParams) -> Dict[str, Any]:
        """查询功能维度进展"""
        try:
            # 从 Memory 服务获取最新的功能数据
            latest_function = await self.memory_service.get_latest_function(params.child_id)
            
            if not latest_function:
                return {"success": False, "error": "暂无功能维度数据"}
            
            active_dimensions = latest_function.get("active_dimensions", {})
            
            if params.dimension_name:
                # 查询特定维度
                dim_data = active_dimensions.get(params.dimension_name)
                if not dim_data:
                    return {"success": False, "error": f"维度不存在: {params.dimension_name}"}
                
                response = {
                    "success": True,
                    "dimension": params.dimension_name,
                    "current_level": dim_data.get("current_level", 0),
                    "baseline": dim_data.get("baseline", 0),
                    "change": dim_data.get("change", "0"),
                    "trend": dim_data.get("trend", "stable")
                }
            else:
                # 查询所有维度概览
                dimension_summary = []
                for dim_name, dim_data in active_dimensions.items():
                    if isinstance(dim_data, dict):
                        dimension_summary.append({
                            "dimension": dim_name,
                            "current_level": dim_data.get("current_level", 0),
                            "trend": dim_data.get("trend", "stable")
                        })
                
                response = {
                    "success": True,
                    "dimensions": dimension_summary
                }
            
            print(f"\n[ChatTools] 📋 query_dimension_progress 完整响应:")
            print(f"{json.dumps(response, ensure_ascii=False, indent=2)}")
            return response
        except Exception as e:
            print(f"[ChatTools] ❌ query_dimension_progress 失败: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e)}


TOOL_DEFINITIONS = [
    {"name": "record_behavior", 
     "description": "【必须调用】记录孩子的行为观察。当用户消息中包含孩子的行为、兴趣、表现描述时，必须立即调用此工具。触发词包括但不限于：喜欢、讨厌、做了、表现、感兴趣、玩了、说了、看了、听了。无需询问用户确认，直接记录。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "description": {"type": "string", "description": "行为描述（自然语言）"},
         "input_type": {"type": "string", "enum": ["text", "voice"], "default": "text"}},
         "required": ["child_id", "description"]}},
    
    {"name": "recommend_game", 
     "description": "根据孩子当前状态推荐地板时光游戏。当家长询问'玩什么游戏'、'推荐游戏'时使用。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "context": {"type": "string", "description": "可选的上下文信息"}},
         "required": ["child_id"]}},
    
    {"name": "get_child_profile", 
     "description": "查询孩子的档案信息（姓名、诊断等基本信息）。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"}},
         "required": ["child_id"]}},
    
    {"name": "query_behaviors", 
     "description": "查询孩子的历史行为记录。当家长询问'孩子之前做了什么'、'最近的行为记录'、'查看行为'时使用。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "limit": {"type": "integer", "default": 20, "description": "返回记录数量"},
         "keyword": {"type": "string", "description": "可选的关键词过滤"}},
         "required": ["child_id"]}},
    
    {"name": "query_interests", 
     "description": "查询孩子当前的兴趣点分布。当家长询问'孩子喜欢什么'、'孩子的兴趣'、'兴趣点'时使用。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"}},
         "required": ["child_id"]}},
    
    {"name": "query_dimension_progress", 
     "description": "查询孩子在各个功能维度的进展情况。当家长询问'孩子进步如何'、'各方面发展'、'维度进展'时使用。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "dimension_name": {"type": "string", "description": "可选的特定维度名称"}},
         "required": ["child_id"]}},
    
    {"name": "get_recent_games", 
     "description": "查询最近玩过的游戏。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "limit": {"type": "integer", "default": 10}},
         "required": ["child_id"]}},
    
    {"name": "get_latest_assessment", 
     "description": "【仅查询历史】查看之前已经生成的评估报告。仅用于回顾历史评估。当家长询问'上次评估结果'、'之前的评估'时使用。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "assessment_type": {"type": "string", "enum": ["comprehensive", "interest_mining", "trend_analysis"]}},
         "required": ["child_id"]}},
    
    {"name": "generate_assessment", 
     "description": "【生成新评估】基于最近的行为和游戏数据，生成一份全新的发展评估报告。当家长要求'评估一下孩子'、'帮我做个评估'、'分析孩子发展情况'时使用。注意：需要30-60秒。",
     "parameters": {"type": "object", "properties": {
         "child_id": {"type": "string", "description": "孩子ID"},
         "assessment_type": {"type": "string", "enum": ["comprehensive", "interest_mining", "trend_analysis"], "default": "comprehensive", "description": "评估类型：comprehensive(综合评估), interest_mining(兴趣挖掘), trend_analysis(趋势分析)"}},
         "required": ["child_id"]}}
]
