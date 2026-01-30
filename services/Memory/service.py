"""
Memory 服务 - 记忆驱动架构的核心
提供语义化的记忆读写接口 + LLM 智能解析
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import json

from .config import MemoryConfig
from .prompts import (
    BEHAVIOR_PARSE_PROMPT,
    NEGATIVE_EVENT_DETECT_PROMPT,
    INTEREST_MINING_PROMPT,
    FUNCTION_TREND_PROMPT,
    COMPREHENSIVE_ASSESSMENT_PROMPT,
    GAME_SUMMARY_PROMPT
)
from .schemas import (
    BehaviorParseOutput,
    GameSummaryOutput,
    InterestMiningOutput,
    FunctionTrendOutput,
    ComprehensiveAssessmentOutput,
    ProfileImportOutput
)

# 导入 Graphiti 存储层
from services.Graphiti.storage.graph_storage import GraphStorage
from services.Graphiti.models.nodes import Person, Behavior, Object, FloorTimeGame, ChildAssessment
from services.Graphiti.models.edges import EdgeType
from services.Graphiti.utils.validators import validate_person, validate_behavior, validate_object

# 导入 LLM 服务（统一服务）
from services.LLM_Service.service import get_llm_service

# 导入 Schema 构建器
from services.game.schema_builder import pydantic_to_json_schema


class MemoryService:
    """
    记忆服务 - 集成 LLM 的智能读写
    
    职责：
    1. 提供语义化的业务接口
    2. LLM 智能解析（行为记录、评估生成、游戏总结）
    3. 数据验证和错误处理
    4. 封装图存储操作
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        self.storage = GraphStorage(
            uri=self.config.neo4j_uri,
            user=self.config.neo4j_user,
            password=self.config.neo4j_password
        )
        
        # LLM 服务（按需初始化）
        self._llm_service = None
    
    @property
    def llm_service(self):
        """延迟初始化 LLM 服务"""
        if self._llm_service is None and self.config.enable_llm:
            self._llm_service = get_llm_service()
        return self._llm_service
    
    async def initialize(self):
        """初始化服务（创建固定节点、约束、索引）"""
        await self.storage.initialize_fixed_nodes()
    
    async def close(self):
        """关闭服务"""
        await self.storage.close()
    
    # ========== 智能写入（LLM 解析）==========
    # 输入都是文字信息，Memory 负责解析成结构化节点存入 Graphiti
    
    async def record_behavior(
        self,
        child_id: str,
        raw_input: str,
        input_type: str = "text",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        日常行为记录 - LLM 解析自然语言 → 结构化行为节点
        
        调用方：行为观察模块（已完成语音转文字）
        
        Args:
            child_id: 孩子ID
            raw_input: 原始输入（文字描述）
            input_type: 输入类型（text/quick_button）
            context: 可选上下文
        
        Returns:
            BehaviorNode（字典格式）
        """
        if not self.config.enable_llm:
            raise ValueError("LLM 功能未启用，无法解析行为记录")
        
        # 1. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=BehaviorParseOutput,
            schema_name="BehaviorParseOutput",
            description="行为解析结果"
        )
        
        # 2. 调用 LLM 解析
        prompt = BEHAVIOR_PARSE_PROMPT.format(raw_input=raw_input)
        
        result = await self.llm_service.call(
            system_prompt="你是一个专业的 ASD 儿童行为分析师。",
            user_message=prompt,
            output_schema=output_schema,
            temperature=0.3,  # 较低温度，保证结构化输出的稳定性
            max_tokens=1500
        )
        
        # 3. 获取结构化输出
        if not result.get("structured_output"):
            raise ValueError("LLM 未返回结构化输出")
        
        parsed_data = result["structured_output"]
        
        # 4. 创建 Behavior 节点
        behavior_id = f"behavior_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        timestamp = datetime.now(timezone.utc).isoformat()
        
        behavior = Behavior(
            behavior_id=behavior_id,
            child_id=child_id,
            timestamp=timestamp,
            event_type=parsed_data.get("event_type", "other"),
            description=parsed_data.get("description", raw_input[:50]),
            raw_input=raw_input,
            input_type=input_type,
            significance=parsed_data.get("significance", "normal"),
            ai_analysis=parsed_data.get("ai_analysis", {}),
            context=parsed_data.get("context", context or {}),
            evidence={"source": "parent_observation", "timestamp": timestamp}
        )
        
        # 验证并创建节点
        validate_behavior(behavior)
        await self.storage.create_behavior(behavior)
        
        # 5. 创建关系：孩子 -> 行为
        await self.storage.create_relationship(
            from_id=child_id,
            from_label="Person",
            to_id=behavior_id,
            to_label="Behavior",
            rel_type="展现"
        )
        
        # 6. 创建关系：行为 -> 对象
        objects_involved = parsed_data.get("objects_involved", [])
        for obj_name in objects_involved:
            # 创建或获取对象节点
            obj_id = f"obj_{obj_name.replace(' ', '_').lower()}"
            obj = Object(
                object_id=obj_id,
                name=obj_name,
                description=f"在行为记录中提到的对象：{obj_name}",
                tags=[],
                usage={"mentioned_in": [behavior_id]}
            )
            await self.storage.create_object(obj)
            
            # 创建关系
            await self.storage.create_relationship(
                from_id=behavior_id,
                from_label="Behavior",
                to_id=obj_id,
                to_label="Object",
                rel_type="涉及对象"
            )
        
        # 7. 创建关系：行为 -> 兴趣维度
        related_interests = parsed_data.get("related_interests", [])
        for interest_name in related_interests:
            interest_id = f"interest_{interest_name}"
            await self.storage.create_relationship(
                from_id=behavior_id,
                from_label="Behavior",
                to_id=interest_id,
                to_label="InterestDimension",
                rel_type="体现兴趣"
            )
        
        # 8. 创建关系：行为 -> 功能维度
        related_functions = parsed_data.get("related_functions", [])
        for function_name in related_functions:
            function_id = f"function_{function_name}"
            await self.storage.create_relationship(
                from_id=behavior_id,
                from_label="Behavior",
                to_id=function_id,
                to_label="FunctionDimension",
                rel_type="体现功能"
            )
        
        # 9. 返回完整的行为数据
        return {
            "behavior_id": behavior_id,
            "child_id": child_id,
            "timestamp": timestamp,
            "event_type": behavior.event_type,
            "description": behavior.description,
            "raw_input": raw_input,
            "input_type": input_type,
            "significance": behavior.significance,
            "ai_analysis": behavior.ai_analysis,
            "context": behavior.context,
            "objects_involved": objects_involved,
            "related_interests": related_interests,
            "related_functions": related_functions
        }
    
    async def summarize_game(
        self,
        game_id: str,
        video_analysis: Optional[Dict[str, Any]] = None,
        parent_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        地板游戏总结 - LLM 生成游戏总结 → 更新游戏节点
        
        调用方：游戏总结模块
        
        Args:
            game_id: 游戏ID
            video_analysis: 视频分析结果（文字，可选）
            parent_feedback: 家长反馈（文字，可选）
        
        Returns:
            GameNode（字典格式）
        """
        if not self.config.enable_llm:
            raise ValueError("LLM 功能未启用，无法生成游戏总结")
        
        # 1. 获取游戏信息
        game = await self.storage.get_game(game_id)
        if not game:
            raise ValueError(f"游戏不存在: {game_id}")
        
        # 2. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=GameSummaryOutput,
            schema_name="GameSummaryOutput",
            description="游戏总结结果"
        )
        
        # 3. 构建 Prompt
        prompt = GAME_SUMMARY_PROMPT.format(
            game_info=json.dumps(game, ensure_ascii=False, indent=2),
            video_analysis=json.dumps(video_analysis or {}, ensure_ascii=False, indent=2),
            parent_feedback=json.dumps(parent_feedback or {}, ensure_ascii=False, indent=2)
        )
        
        # 4. 调用 LLM
        result = await self.llm_service.call(
            system_prompt="你是一个专业的地板时光游戏分析师。",
            user_message=prompt,
            output_schema=output_schema,
            temperature=0.5,  # 中等温度，平衡创造性和准确性
            max_tokens=2500
        )
        
        # 5. 获取结构化输出
        if not result.get("structured_output"):
            raise ValueError("LLM 未返回结构化输出")
        
        summary_data = result["structured_output"]
        
        # 6. 更新游戏节点
        updates = {
            "status": "completed",
            "implementation": {
                **game.get("implementation", {}),
                "summary": summary_data.get("session_summary", ""),
                "engagement_score": summary_data.get("engagement_score", 0),
                "goal_achievement_score": summary_data.get("goal_achievement_score", 0),
                "highlights": summary_data.get("highlights", []),
                "concerns": summary_data.get("concerns", []),
                "improvement_suggestions": summary_data.get("improvement_suggestions", []),
                "parent_notes": summary_data.get("parent_notes", "")
            }
        }
        
        await self.storage.update_game(game_id, updates)
        
        # 7. 记录关键行为（如果有）
        key_behaviors = summary_data.get("key_behaviors", [])
        for kb in key_behaviors:
            # 为每个关键行为创建一个 Behavior 节点
            behavior_id = f"behavior_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            behavior = Behavior(
                behavior_id=behavior_id,
                child_id=game.get("child_id"),
                timestamp=kb.get("timestamp", datetime.now(timezone.utc).isoformat()),
                event_type=kb.get("event_type", "other"),
                description=kb.get("description", ""),
                raw_input=f"游戏中的关键时刻：{kb.get('description', '')}",
                input_type="game_observation",
                significance=kb.get("significance", "normal"),
                ai_analysis={"source": "game_summary", "game_id": game_id},
                context={"game_id": game_id, "timestamp": kb.get("timestamp", "")},
                evidence={"source": "game_video_analysis"}
            )
            
            await self.storage.create_behavior(behavior)
            
            # 创建关系：孩子 -> 行为
            await self.storage.create_relationship(
                from_id=game.get("child_id"),
                from_label="Person",
                to_id=behavior_id,
                to_label="Behavior",
                rel_type="展现"
            )
            
            # 创建关系：游戏 -> 行为
            await self.storage.create_relationship(
                from_id=game_id,
                from_label="FloorTimeGame",
                to_id=behavior_id,
                to_label="Behavior",
                rel_type="包含行为"
            )
        
        # 8. 返回更新后的游戏数据
        updated_game = await self.storage.get_game(game_id)
        return updated_game
    
    async def generate_assessment(
        self,
        child_id: str,
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        孩子评估总结 - LLM 综合评估 → 评估节点
        
        调用方：评估模块
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（comprehensive/interest_mining/trend_analysis）
        
        Returns:
            AssessmentNode（字典格式）
        """
        if not self.config.enable_llm:
            raise ValueError("LLM 功能未启用，无法生成评估")
        
        # 1. 获取最近的行为记录（用于分析）
        recent_behaviors = await self.storage.get_behaviors(
            child_id=child_id,
            limit=50  # 最近50条行为记录
        )
        
        # 构建行为摘要
        behaviors_summary = "\n".join([
            f"- [{b.get('timestamp', '')}] {b.get('description', '')} (类型: {b.get('event_type', '')}, 重要性: {b.get('significance', '')})"
            for b in recent_behaviors[:20]  # 只取前20条用于 Prompt
        ])
        
        # 2. 根据评估类型选择 Prompt 和 Schema
        if assessment_type == "interest_mining":
            # 兴趣挖掘
            prompt = INTEREST_MINING_PROMPT.format(behaviors_summary=behaviors_summary)
            system_prompt = "你是一个专业的 ASD 儿童兴趣分析师。"
            output_schema = pydantic_to_json_schema(
                model=InterestMiningOutput,
                schema_name="InterestMiningOutput",
                description="兴趣挖掘结果"
            )
            
        elif assessment_type == "trend_analysis":
            # 功能趋势分析
            previous_assessment = await self.get_latest_assessment(child_id, "trend_analysis")
            previous_assessment_str = json.dumps(previous_assessment or {}, ensure_ascii=False, indent=2)
            
            prompt = FUNCTION_TREND_PROMPT.format(
                behaviors_summary=behaviors_summary,
                previous_assessment=previous_assessment_str
            )
            system_prompt = "你是一个专业的 ASD 儿童发展评估师。"
            output_schema = pydantic_to_json_schema(
                model=FunctionTrendOutput,
                schema_name="FunctionTrendOutput",
                description="功能趋势分析结果"
            )
            
        elif assessment_type == "comprehensive":
            # 综合评估
            interest_mining = await self.get_latest_assessment(child_id, "interest_mining")
            function_trend = await self.get_latest_assessment(child_id, "trend_analysis")
            recent_games = await self.get_recent_games(child_id, limit=5)
            previous_assessment = await self.get_latest_assessment(child_id, "comprehensive")
            
            prompt = COMPREHENSIVE_ASSESSMENT_PROMPT.format(
                interest_mining=json.dumps(interest_mining or {}, ensure_ascii=False, indent=2),
                function_trend=json.dumps(function_trend or {}, ensure_ascii=False, indent=2),
                recent_games=json.dumps(recent_games or [], ensure_ascii=False, indent=2),
                previous_assessment=json.dumps(previous_assessment or {}, ensure_ascii=False, indent=2)
            )
            system_prompt = "你是一个专业的 ASD 儿童综合评估师。"
            output_schema = pydantic_to_json_schema(
                model=ComprehensiveAssessmentOutput,
                schema_name="ComprehensiveAssessmentOutput",
                description="综合评估结果"
            )
            
        else:
            raise ValueError(f"不支持的评估类型: {assessment_type}")
        
        # 3. 调用 LLM
        result = await self.llm_service.call(
            system_prompt=system_prompt,
            user_message=prompt,
            output_schema=output_schema,
            temperature=0.3,  # 较低温度，保证评估的客观性
            max_tokens=3000
        )
        
        # 4. 获取结构化输出
        if not result.get("structured_output"):
            raise ValueError("LLM 未返回结构化输出")
        
        analysis_data = result["structured_output"]
        
        # 5. 创建评估节点
        assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        assessment = ChildAssessment(
            assessment_id=assessment_id,
            child_id=child_id,
            assessor_id="system_llm",
            timestamp=datetime.now(timezone.utc).isoformat(),
            assessment_type=assessment_type,
            analysis=analysis_data,
            recommendations=analysis_data.get("recommendations", analysis_data.get("summary", {}).get("recommendations", []))
        )
        
        await self.storage.create_assessment(assessment)
        
        # 6. 创建关系：孩子 -> 评估
        await self.storage.create_relationship(
            from_id=child_id,
            from_label="Person",
            to_id=assessment_id,
            to_label="ChildAssessment",
            rel_type="接受评估"
        )
        
        # 7. 返回评估数据
        return {
            "assessment_id": assessment_id,
            "child_id": child_id,
            "assessor_id": "system_llm",
            "timestamp": assessment.timestamp,
            "assessment_type": assessment_type,
            "analysis": analysis_data,
            "recommendations": assessment.recommendations
        }
    
    async def import_profile(
        self,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        导入档案 - LLM 解析档案数据 → 创建档案节点 + 初始评估
        
        调用方：导入模块
        
        Args:
            profile_data: 档案数据（文字，包含基本信息、医学报告、量表等）
        
        Returns:
            {
                "child_id": "...",
                "assessment_id": "...",
                "message": "..."
            }
        """
        if not self.config.enable_llm:
            raise ValueError("LLM 功能未启用，无法导入档案")
        
        # 1. 提取基本信息
        name = profile_data.get("name", "未命名")
        age = profile_data.get("age")
        diagnosis = profile_data.get("diagnosis", "")
        medical_reports = profile_data.get("medical_reports", "")
        assessment_scales = profile_data.get("assessment_scales", "")
        
        # 2. 创建孩子档案节点
        child_id = f"child_{uuid.uuid4().hex[:12]}"
        
        child = Person(
            person_id=child_id,
            person_type="child",
            name=name,
            role="patient",
            basic_info={
                "age": age,
                "diagnosis": diagnosis,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                "source": "profile_import"
            },
            created_at=datetime.now(timezone.utc).isoformat()
        )
        
        await self.storage.create_person(child)
        
        # 3. 构建 Output Schema
        output_schema = pydantic_to_json_schema(
            model=ProfileImportOutput,
            schema_name="ProfileImportOutput",
            description="档案导入分析结果"
        )
        
        # 4. 构建 LLM Prompt（解析档案，生成初始评估）
        prompt = f"""请分析以下儿童档案，生成初始评估报告。

【基本信息】
姓名：{name}
年龄：{age}
诊断：{diagnosis}

【医学报告】
{medical_reports}

【评估量表】
{assessment_scales}

【任务】
1. 分析孩子的当前状况
2. 识别优势领域和挑战领域
3. 提取关键的兴趣偏好（如果有）
4. 提取关键的功能维度表现（如果有）
5. 生成初步的干预建议
"""
        
        # 5. 调用 LLM
        result = await self.llm_service.call(
            system_prompt="你是一个专业的 ASD 儿童档案分析师。",
            user_message=prompt,
            output_schema=output_schema,
            temperature=0.3,
            max_tokens=2500
        )
        
        # 6. 获取结构化输出
        if not result.get("structured_output"):
            raise ValueError("LLM 未返回结构化输出")
        
        initial_assessment = result["structured_output"]
        
        # 7. 创建初始评估节点
        assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        assessment = ChildAssessment(
            assessment_id=assessment_id,
            child_id=child_id,
            assessor_id="system_llm",
            timestamp=datetime.now(timezone.utc).isoformat(),
            assessment_type="comprehensive",
            analysis=initial_assessment,
            recommendations=initial_assessment.get("recommendations", [])
        )
        
        await self.storage.create_assessment(assessment)
        
        # 8. 创建关系：孩子 -> 评估
        await self.storage.create_relationship(
            from_id=child_id,
            from_label="Person",
            to_id=assessment_id,
            to_label="ChildAssessment",
            rel_type="接受评估"
        )
        
        # 9. 返回结果
        return {
            "child_id": child_id,
            "assessment_id": assessment_id,
            "message": f"档案导入成功，已为 {name} 创建初始评估"
        }
    
    # ========== 基础读写 ==========
    
    # 人物
    
    async def get_child(self, child_id: str) -> Optional[Dict[str, Any]]:
        """获取孩子档案"""
        return await self.storage.get_person(child_id)
    
    async def save_child(self, child: Person) -> str:
        """
        保存孩子档案
        
        Args:
            child: 人物节点（person_type 必须是 "child"）
            
        Returns:
            person_id
        """
        validate_person(child)
        
        if child.person_type != "child":
            raise ValueError(f"person_type 必须是 'child'，当前是 '{child.person_type}'")
        
        if not child.person_id:
            child.person_id = f"child_{uuid.uuid4().hex[:12]}"
        
        if not child.created_at:
            child.created_at = datetime.now(timezone.utc).isoformat()
        
        return await self.storage.create_person(child)
    
    # 行为
    
    async def get_behaviors(
        self,
        child_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询行为记录
        
        Args:
            child_id: 孩子ID
            filters: 过滤条件（可选）
                - start_time: 开始时间
                - end_time: 结束时间
                - limit: 返回数量限制
        
        Returns:
            行为记录列表
        """
        filters = filters or {}
        return await self.storage.get_behaviors(
            child_id=child_id,
            start_time=filters.get("start_time"),
            end_time=filters.get("end_time"),
            limit=filters.get("limit", 100)
        )
    
    # 对象
    
    async def save_object(self, obj: Object) -> str:
        """
        保存对象（玩具/物品）
        
        Args:
            obj: 对象节点
            
        Returns:
            object_id
        """
        validate_object(obj)
        
        if not obj.object_id:
            obj.object_id = f"obj_{uuid.uuid4().hex[:12]}"
        
        return await self.storage.create_object(obj)
    
    async def get_objects(self, child_id: str) -> List[Dict[str, Any]]:
        """
        获取孩子相关的对象列表
        
        Args:
            child_id: 孩子ID
        
        Returns:
            对象列表
        """
        return await self.storage.get_objects_by_child(child_id)
    
    # 兴趣维度
    
    async def save_interest(self, interest: Dict[str, Any]) -> str:
        """
        保存兴趣评估快照
        
        实际保存到 ChildAssessment 节点（assessment_type="interest_mining"）
        
        Args:
            interest: 兴趣评估数据（InterestNode 字典格式）
        
        Returns:
            assessment_id
        """
        child_id = interest.get("child_id")
        if not child_id:
            raise ValueError("缺少 child_id")
        
        return await self.save_assessment(
            child_id=child_id,
            assessment_type="interest_mining",
            analysis=interest,
            recommendations=interest.get("recommendations", {})
        )
    
    async def get_latest_interest(self, child_id: str) -> Optional[Dict[str, Any]]:
        """
        获取最新兴趣评估
        
        Args:
            child_id: 孩子ID
        
        Returns:
            最新兴趣评估数据（InterestNode 字典格式）
        """
        return await self.get_latest_assessment(child_id, "interest_mining")
    
    async def get_interest_history(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取兴趣评估历史
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
        
        Returns:
            兴趣评估历史列表
        """
        return await self.get_assessment_history(child_id, "interest_mining", limit)
    
    # 功能维度
    
    async def save_function(self, func: Dict[str, Any]) -> str:
        """
        保存功能评估快照
        
        实际保存到 ChildAssessment 节点（assessment_type="trend_analysis"）
        
        Args:
            func: 功能评估数据（FunctionNode 字典格式）
        
        Returns:
            assessment_id
        """
        child_id = func.get("child_id")
        if not child_id:
            raise ValueError("缺少 child_id")
        
        return await self.save_assessment(
            child_id=child_id,
            assessment_type="trend_analysis",
            analysis=func,
            recommendations=func.get("recommendations", {})
        )
    
    async def get_latest_function(self, child_id: str) -> Optional[Dict[str, Any]]:
        """
        获取最新功能评估
        
        Args:
            child_id: 孩子ID
        
        Returns:
            最新功能评估数据（FunctionNode 字典格式）
        """
        return await self.get_latest_assessment(child_id, "trend_analysis")
    
    async def get_function_history(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取功能评估历史
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
        
        Returns:
            功能评估历史列表
        """
        return await self.get_assessment_history(child_id, "trend_analysis", limit)
    
    # 地板游戏
    
    async def save_game(self, game: Dict[str, Any]) -> str:
        """
        保存游戏节点
        
        Args:
            game: 游戏数据（GameNode 字典格式）
        
        Returns:
            game_id
        """
        game_node = FloorTimeGame(
            game_id=game.get("game_id", f"game_{uuid.uuid4().hex[:12]}"),
            child_id=game.get("child_id", ""),
            name=game.get("name", ""),
            description=game.get("description", ""),
            created_at=game.get("created_at", datetime.now(timezone.utc).isoformat()),
            status=game.get("status", "recommended"),
            design=game.get("design", {}),
            implementation=game.get("implementation", {})
        )
        
        game_id = await self.storage.create_game(game_node)
        
        # 创建关系：孩子 -> 游戏
        await self.storage.create_relationship(
            from_id=game_node.child_id,
            from_label="Person",
            to_id=game_id,
            to_label="FloorTimeGame",
            rel_type="参与"
        )
        
        return game_id
    
    async def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个游戏
        
        Args:
            game_id: 游戏ID
        
        Returns:
            游戏数据（GameNode 字典格式）
        """
        return await self.storage.get_game(game_id)
    
    async def get_recent_games(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最近游戏列表
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
        
        Returns:
            游戏列表（GameNode 字典格式）
        """
        return await self.storage.get_games_by_child(child_id, limit)
    
    # 儿童评估
    
    async def save_assessment(
        self,
        child_id: str,
        assessment_type: str,
        analysis: Dict[str, Any],
        recommendations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        保存评估结果
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（interest_mining/trend_analysis/comprehensive）
            analysis: 分析结果
            recommendations: 建议（可选）
            
        Returns:
            assessment_id
        """
        assessment = ChildAssessment(
            assessment_id=f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
            child_id=child_id,
            assessor_id="system_llm",
            timestamp=datetime.now(timezone.utc).isoformat(),
            assessment_type=assessment_type,
            analysis=analysis,
            recommendations=recommendations or {}
        )
        
        return await self.storage.create_assessment(assessment)
    
    async def get_latest_assessment(
        self,
        child_id: str,
        assessment_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取最新评估
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            
        Returns:
            最新评估数据（AssessmentNode 字典格式）
        """
        return await self.storage.get_latest_assessment(child_id, assessment_type)
    
    async def get_assessment_history(
        self,
        child_id: str,
        assessment_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取评估历史
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            limit: 返回数量限制
            
        Returns:
            评估历史列表
        """
        return await self.storage.get_assessments_by_child(child_id, assessment_type, limit)


# ============ 全局服务实例 ============

_memory_service_instance: Optional[MemoryService] = None


async def get_memory_service(config: Optional[MemoryConfig] = None) -> MemoryService:
    """获取记忆服务实例（单例）"""
    global _memory_service_instance
    
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService(config)
        await _memory_service_instance.initialize()
    
    return _memory_service_instance
