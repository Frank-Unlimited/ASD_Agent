"""
Memory 服务 - 记忆驱动架构的核心
提供语义化的记忆读写接口 + LLM 智能解析
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import uuid
import json
import sys
from pathlib import Path

# 添加 graphiti_core 到路径
graphiti_path = Path(__file__).parent.parent.parent / "external" / "graphiti"
if str(graphiti_path) not in sys.path:
    sys.path.insert(0, str(graphiti_path))

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

# 导入存储层（已合并到 Memory 模块）
from .storage.graph_storage import GraphStorage
from .models.nodes import Person, Behavior, Object, FloorTimeGame, ChildAssessment
from .models.edges import EdgeType
from .utils.validators import validate_person, validate_behavior, validate_object

# 导入 LLM 服务（统一服务）
from services.LLM_Service.service import get_llm_service

# 导入 Schema 构建器
from services.game.schema_builder import pydantic_to_json_schema

# 导入 Graphiti-core
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from graphiti_core.llm_client.openai_generic_client import OpenAIGenericClient
from graphiti_core.llm_client.config import LLMConfig
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient

# 导入自定义实体模型和提取指令
from .entity_models import (
    BehaviorEntityModel,
    ObjectEntityModel,
    InterestEntityModel,
    FunctionEntityModel,
    PersonEntityModel,
    GameSummaryEntityModel,
    KeyBehaviorEntityModel,
    AssessmentEntityModel,
    ExhibitEdgeModel,
    InvolveObjectEdgeModel,
    ShowInterestEdgeModel,
    ShowFunctionEdgeModel,
    InvolvePersonEdgeModel,
)
from .extraction_instructions import (
    BEHAVIOR_EXTRACTION_INSTRUCTIONS,
    GAME_SUMMARY_EXTRACTION_INSTRUCTIONS,
    ASSESSMENT_EXTRACTION_INSTRUCTIONS,
)
from .converters import (
    extract_event_type,
    extract_description,
    extract_significance,
    extract_objects,
    extract_interests,
    extract_functions,
    build_ai_analysis,
    build_game_summary_content,
    extract_summary_data,
    build_assessment_content,
    extract_assessment_data,
)


class MemoryService:
    """
    记忆服务 - 集成 LLM 的智能读写
    
    职责：
    1. 提供语义化的业务接口
    2. 使用 Graphiti-core 自动提取实体和关系
    3. 数据验证和错误处理
    4. 封装图存储操作
    """
    
    def __init__(self, config: Optional[MemoryConfig] = None):
        self.config = config or MemoryConfig()
        
        # GraphStorage（用于直接查询和兼容性）
        self.storage = GraphStorage(
            uri=self.config.neo4j_uri,
            user=self.config.neo4j_user,
            password=self.config.neo4j_password
        )
        
        # LLM 服务（按需初始化）
        self._llm_service = None
        
        # Graphiti-core 实例（按需初始化）
        self._graphiti = None
    
    @property
    def llm_service(self):
        """延迟初始化 LLM 服务"""
        if self._llm_service is None and self.config.enable_llm:
            self._llm_service = get_llm_service()
        return self._llm_service
    
    @property
    def graphiti(self):
        """延迟初始化 Graphiti-core 实例"""
        if self._graphiti is None and self.config.enable_llm:
            # 配置 LLM（用于主要的提取任务）
            llm_config = LLMConfig(
                api_key=self.config.llm_api_key,
                model=self.config.llm_model,
                small_model=self.config.llm_small_model,
                base_url=self.config.llm_base_url
            )
            llm_client = OpenAIGenericClient(config=llm_config)
            
            # 配置 Embedder
            embedder_config = OpenAIEmbedderConfig(
                api_key=self.config.llm_api_key,
                embedding_model=self.config.llm_embedding_model,
                embedding_dim=self.config.llm_embedding_dim,
                base_url=self.config.llm_base_url
            )
            embedder = OpenAIEmbedder(config=embedder_config)
            
            # 配置 Cross Encoder (Reranker) - 使用 Qwen 的小模型
            reranker_config = LLMConfig(
                api_key=self.config.llm_api_key,
                model=self.config.llm_small_model,  # 使用小模型做 reranking
                base_url=self.config.llm_base_url
            )
            cross_encoder = OpenAIRerankerClient(config=reranker_config)
            
            # 创建 Graphiti 实例
            self._graphiti = Graphiti(
                uri=self.config.neo4j_uri,
                user=self.config.neo4j_user,
                password=self.config.neo4j_password,
                llm_client=llm_client,
                embedder=embedder,
                cross_encoder=cross_encoder,
                store_raw_episode_content=True
            )
        
        return self._graphiti
    
    async def initialize(self):
        """初始化服务（创建固定节点、约束、索引）"""
        await self.storage.initialize_fixed_nodes()
        
        # 如果启用了 LLM，初始化 Graphiti 索引
        if self.config.enable_llm and self._graphiti is not None:
            await self._graphiti.build_indices_and_constraints()
    
    async def close(self):
        """关闭服务"""
        await self.storage.close()
        
        # 关闭 Graphiti 连接
        if self._graphiti is not None:
            await self._graphiti.close()
    
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
        日常行为记录 - 使用 Graphiti-core 自动提取实体和关系
        
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
        
        # 1. 定义实体类型
        entity_types = {
            'Behavior': BehaviorEntityModel,
            'Object': ObjectEntityModel,
            'Interest': InterestEntityModel,
            'Function': FunctionEntityModel,
            'Person': PersonEntityModel,
        }
        
        # 2. 定义边类型
        edge_types = {
            '展现': ExhibitEdgeModel,
            '涉及对象': InvolveObjectEdgeModel,
            '体现兴趣': ShowInterestEdgeModel,
            '体现功能': ShowFunctionEdgeModel,
            '涉及人物': InvolvePersonEdgeModel,
        }
        
        # 3. 定义边类型映射
        edge_type_map = {
            ('Person', 'Behavior'): ['展现'],
            ('Behavior', 'Object'): ['涉及对象'],
            ('Behavior', 'Interest'): ['体现兴趣'],
            ('Behavior', 'Function'): ['体现功能'],
            ('Behavior', 'Person'): ['涉及人物'],
        }
        
        # 4. 使用 Graphiti-core 自动提取
        result = await self.graphiti.add_episode(
            name=f"行为观察_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            episode_body=raw_input,
            source_description=f"家长观察记录 ({input_type})",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text,  # 使用 text 类型
            group_id=child_id,
            entity_types=entity_types,
            edge_types=edge_types,
            edge_type_map=edge_type_map,
            custom_extraction_instructions=BEHAVIOR_EXTRACTION_INSTRUCTIONS,
        )
        
        # 5. 转换为原有返回格式（保持向后兼容）
        behavior_id = result.episode.uuid
        timestamp = result.episode.valid_at.isoformat()
        
        return {
            "behavior_id": behavior_id,
            "child_id": child_id,
            "timestamp": timestamp,
            "event_type": extract_event_type(result),
            "description": extract_description(result),
            "raw_input": raw_input,
            "input_type": input_type,
            "significance": extract_significance(result),
            "ai_analysis": build_ai_analysis(result),
            "context": context or {},
            "objects_involved": extract_objects(result),
            "related_interests": extract_interests(result),
            "related_functions": extract_functions(result)
        }
    
    async def summarize_game(
        self,
        game_id: str,
        video_analysis: Optional[Dict[str, Any]] = None,
        parent_feedback: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        地板游戏总结 - 使用 Graphiti-core 自动提取游戏总结
        
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
        
        child_id = game.get("child_id")
        
        # 2. 构建 episode 内容
        episode_content = build_game_summary_content(game, video_analysis, parent_feedback)
        
        # 3. 定义实体类型
        entity_types = {
            'GameSummary': GameSummaryEntityModel,
            'KeyBehavior': KeyBehaviorEntityModel,
        }
        
        # 4. 使用 Graphiti-core 自动提取总结
        result = await self.graphiti.add_episode(
            name=f"游戏总结_{game_id}",
            episode_body=episode_content,
            source_description="游戏实施总结",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text,  # 使用 text 类型
            group_id=child_id,
            entity_types=entity_types,
            custom_extraction_instructions=GAME_SUMMARY_EXTRACTION_INSTRUCTIONS,
        )
        
        # 5. 提取总结数据
        summary_data = extract_summary_data(result)
        
        # 6. 更新游戏节点
        updates = {
            "status": "completed",
            "implementation": {
                **game.get("implementation", {}),
                **summary_data
            }
        }
        
        await self.storage.update_game(game_id, updates)
        
        # 7. 返回更新后的游戏数据
        updated_game = await self.storage.get_game(game_id)
        return updated_game
    
    async def generate_assessment(
        self,
        child_id: str,
        assessment_type: str
    ) -> Dict[str, Any]:
        """
        孩子评估总结 - 使用 Graphiti-core 搜索和提取
        
        调用方：评估模块
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（comprehensive/interest_mining/trend_analysis）
        
        Returns:
            AssessmentNode（字典格式）
        """
        if not self.config.enable_llm:
            raise ValueError("LLM 功能未启用，无法生成评估")
        
        # 1. 使用 Graphiti 搜索获取相关历史数据
        # 根据评估类型构建搜索查询
        if assessment_type == "interest_mining":
            search_queries = [
                "孩子的兴趣爱好和偏好",
                "孩子喜欢的物品和活动",
                "孩子的情绪反应和表现"
            ]
        elif assessment_type == "trend_analysis":
            search_queries = [
                "孩子的社交互动能力",
                "孩子的沟通表达能力",
                "孩子的认知和学习能力",
                "孩子的情绪调节能力"
            ]
        elif assessment_type == "comprehensive":
            search_queries = [
                "孩子的整体发展情况",
                "孩子的进步和突破",
                "孩子的挑战和困难"
            ]
        else:
            raise ValueError(f"不支持的评估类型: {assessment_type}")
        
        # 执行多个搜索查询，收集相关事实
        all_edges = []
        for query in search_queries:
            edges = await self.graphiti.search(
                query=query,
                group_ids=[child_id],
                num_results=20  # 每个查询返回20条相关事实
            )
            all_edges.extend(edges)
        
        # 去重并构建历史数据摘要
        unique_edges = {edge.uuid: edge for edge in all_edges}.values()
        historical_facts = "\n".join([
            f"- {edge.fact}"
            for edge in list(unique_edges)[:30]  # 最多使用30条事实
        ])
        
        # 2. 构建评估内容
        assessment_content = build_assessment_content(
            child_id=child_id,
            assessment_type=assessment_type,
            historical_data={"facts": historical_facts}
        )
        
        # 3. 定义实体类型
        entity_types = {
            'Assessment': AssessmentEntityModel,
        }
        
        # 4. 获取评估提取指令
        from .extraction_instructions import ASSESSMENT_EXTRACTION_INSTRUCTIONS
        extraction_instructions = ASSESSMENT_EXTRACTION_INSTRUCTIONS
        
        # 5. 使用 Graphiti-core 自动提取评估
        result = await self.graphiti.add_episode(
            name=f"评估_{assessment_type}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            episode_body=assessment_content,
            source_description=f"{assessment_type} 评估",
            reference_time=datetime.now(timezone.utc),
            source=EpisodeType.text,
            group_id=child_id,
            entity_types=entity_types,
            custom_extraction_instructions=extraction_instructions,
        )
        
        # 6. 提取评估数据
        assessment_data = extract_assessment_data(result)
        
        # 7. 创建评估节点（保持向后兼容）
        assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        assessment = ChildAssessment(
            assessment_id=assessment_id,
            child_id=child_id,
            assessor_id="system_llm",
            timestamp=datetime.now(timezone.utc).isoformat(),
            assessment_type=assessment_type,
            analysis=assessment_data.get("analysis", {}),
            recommendations=assessment_data.get("recommendations", [])
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
        
        # 9. 返回评估数据
        return {
            "assessment_id": assessment_id,
            "child_id": child_id,
            "assessor_id": "system_llm",
            "timestamp": assessment.timestamp,
            "assessment_type": assessment_type,
            "analysis": assessment_data.get("analysis", {}),
            "recommendations": assessment_data.get("recommendations", [])
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
    
    # ========== 查询方法（完全使用 Graphiti-core）==========
    
    async def get_child(self, child_id: str) -> Optional[Dict[str, Any]]:
        """
        获取孩子档案 - 使用 Graphiti 原生查询
        """
        try:
            # 直接使用 Graphiti driver 查询
            records, _, _ = await self.graphiti.driver.execute_query(
                """
                MATCH (p:Entity {uuid: $child_id})
                WHERE 'Person' IN labels(p)
                RETURN p.uuid AS person_id,
                       p.name AS name,
                       properties(p) AS props,
                       p.created_at AS created_at
                """,
                child_id=child_id
            )
            
            if records:
                record = records[0]
                props = record['props']
                
                # 反序列化 basic_info
                import json
                basic_info_str = props.get('basic_info', '{}')
                try:
                    basic_info = json.loads(basic_info_str) if isinstance(basic_info_str, str) else basic_info_str
                except:
                    basic_info = {}
                
                return {
                    "person_id": record['person_id'],
                    "name": record['name'],
                    "person_type": props.get('person_type', 'child'),
                    "role": props.get('role', 'patient'),
                    "basic_info": basic_info,
                    "created_at": str(record['created_at'])
                }
            
            return None
            
        except Exception as e:
            print(f"[get_child] 查询失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def save_child(self, child: Person) -> str:
        """
        保存孩子档案 - 使用 Graphiti 原生存储
        
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
        
        try:
            # 使用 Graphiti 的 EntityNode 保存
            from graphiti_core.nodes import EntityNode
            import json
            
            # 创建实体节点
            entity_node = EntityNode(
                uuid=child.person_id,
                name=child.name,
                group_id=child.person_id,  # 使用 person_id 作为 group_id
                labels=['Person', 'Child'],
                attributes={
                    'person_type': child.person_type,
                    'role': child.role,
                    'basic_info': json.dumps(child.basic_info),  # 序列化为 JSON 字符串
                    'created_at': child.created_at
                },
                created_at=datetime.fromisoformat(child.created_at.replace('Z', '+00:00'))
            )
            
            # 生成 embedding
            await entity_node.generate_name_embedding(self.graphiti.embedder)
            
            # 保存到图数据库
            await entity_node.save(self.graphiti.driver)
            
            return child.person_id
            
        except Exception as e:
            print(f"[save_child] 保存失败: {e}")
            raise
    
    # 行为
    
    async def get_behaviors(
        self,
        child_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        查询行为记录 - 使用 Graphiti 原生查询
        
        Args:
            child_id: 孩子ID
            filters: 过滤条件（可选）
                - start_time: 开始时间
                - end_time: 结束时间
                - limit: 返回数量限制
        
        Returns:
            行为记录列表
        """
        try:
            from graphiti_core.nodes import EpisodicNode
            
            filters = filters or {}
            limit = filters.get("limit", 100)
            
            # 使用 Graphiti 的 EpisodicNode 查询
            episodes = await EpisodicNode.get_by_group_ids(
                self.graphiti.driver,
                group_ids=[child_id],
                limit=limit
            )
            
            # 转换为行为记录格式
            behaviors = []
            for episode in episodes:
                # 从 episode 获取关联的实体节点
                records, _, _ = await self.graphiti.driver.execute_query(
                    """
                    MATCH (e:Episodic {uuid: $episode_uuid})-[:MENTIONS]->(n:Entity)
                    WHERE 'Behavior' IN labels(n)
                    RETURN n.uuid AS behavior_id,
                           properties(n) AS props,
                           n.created_at AS created_at
                    LIMIT 1
                    """,
                    episode_uuid=episode.uuid
                )
                
                if records:
                    record = records[0]
                    props = record['props']
                    
                    behaviors.append({
                        "behavior_id": episode.uuid,
                        "child_id": child_id,
                        "timestamp": episode.valid_at.isoformat(),
                        "event_type": props.get('event_type', 'other'),
                        "description": props.get('description', episode.content[:100]),
                        "raw_input": episode.content,
                        "input_type": "text",
                        "significance": props.get('significance', 'normal'),
                        "ai_analysis": {},
                        "context": {},
                        "objects_involved": [],
                        "related_interests": [],
                        "related_functions": []
                    })
            
            return behaviors
            
        except Exception as e:
            print(f"[get_behaviors] 查询失败: {e}")
            return []
    
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
        保存游戏节点 - 使用 Graphiti 原生存储
        
        Args:
            game: 游戏数据（GameNode 字典格式）
        
        Returns:
            game_id
        """
        try:
            from graphiti_core.nodes import EntityNode
            import json
            
            game_id = game.get("game_id", f"game_{uuid.uuid4().hex[:12]}")
            child_id = game.get("child_id", "")
            
            # 创建游戏实体节点
            game_node = EntityNode(
                uuid=game_id,
                name=game.get("name", ""),
                group_id=child_id,  # 使用 child_id 作为 group_id
                labels=['FloorTimeGame', 'Game'],
                attributes={
                    'game_id': game_id,
                    'child_id': child_id,
                    'description': game.get("description", ""),
                    'created_at': game.get("created_at", datetime.now(timezone.utc).isoformat()),
                    'status': game.get("status", "recommended"),
                    'design': json.dumps(game.get("design", {})),  # 序列化
                    'implementation': json.dumps(game.get("implementation", {}))  # 序列化
                },
                created_at=datetime.now(timezone.utc)
            )
            
            # 生成 embedding
            await game_node.generate_name_embedding(self.graphiti.embedder)
            
            # 保存到图数据库
            await game_node.save(self.graphiti.driver)
            
            return game_id
            
        except Exception as e:
            print(f"[save_game] 保存失败: {e}")
            raise
    
    async def get_game(self, game_id: str) -> Optional[Dict[str, Any]]:
        """
        获取单个游戏 - 使用 Graphiti 原生查询
        
        Args:
            game_id: 游戏ID
        
        Returns:
            游戏数据（GameNode 字典格式）
        """
        try:
            records, _, _ = await self.graphiti.driver.execute_query(
                """
                MATCH (g:Entity {uuid: $game_id})
                WHERE 'FloorTimeGame' IN labels(g)
                RETURN g.uuid AS game_id,
                       g.name AS name,
                       properties(g) AS props,
                       g.created_at AS created_at
                """,
                game_id=game_id
            )
            
            if records:
                record = records[0]
                props = record['props']
                
                import json
                # 反序列化嵌套对象
                design = props.get('design', '{}')
                implementation = props.get('implementation', '{}')
                
                try:
                    design = json.loads(design) if isinstance(design, str) else design
                except:
                    design = {}
                
                try:
                    implementation = json.loads(implementation) if isinstance(implementation, str) else implementation
                except:
                    implementation = {}
                
                return {
                    "game_id": record['game_id'],
                    "child_id": props.get('child_id', ''),
                    "name": record['name'],
                    "description": props.get('description', ''),
                    "created_at": props.get('created_at', ''),
                    "status": props.get('status', 'recommended'),
                    "design": design,
                    "implementation": implementation
                }
            
            return None
            
        except Exception as e:
            print(f"[get_game] 查询失败: {e}")
            return None
    
    async def get_recent_games(
        self,
        child_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最近游戏列表 - 使用 Graphiti 原生查询
        
        Args:
            child_id: 孩子ID
            limit: 返回数量限制
        
        Returns:
            游戏列表（GameNode 字典格式）
        """
        try:
            records, _, _ = await self.graphiti.driver.execute_query(
                """
                MATCH (g:Entity {group_id: $child_id})
                WHERE 'FloorTimeGame' IN labels(g)
                RETURN g.uuid AS game_id,
                       g.name AS name,
                       properties(g) AS props,
                       g.created_at AS created_at
                ORDER BY g.created_at DESC
                LIMIT $limit
                """,
                child_id=child_id,
                limit=limit
            )
            
            games = []
            for record in records:
                props = record['props']
                
                import json
                # 反序列化嵌套对象
                design = props.get('design', '{}')
                implementation = props.get('implementation', '{}')
                
                try:
                    design = json.loads(design) if isinstance(design, str) else design
                except:
                    design = {}
                
                try:
                    implementation = json.loads(implementation) if isinstance(implementation, str) else implementation
                except:
                    implementation = {}
                
                games.append({
                    "game_id": record['game_id'],
                    "child_id": props.get('child_id', ''),
                    "name": record['name'],
                    "description": props.get('description', ''),
                    "created_at": props.get('created_at', ''),
                    "status": props.get('status', 'recommended'),
                    "design": design,
                    "implementation": implementation
                })
            
            return games
            
        except Exception as e:
            print(f"[get_recent_games] 查询失败: {e}")
            return []
    
    # 儿童评估
    
    async def save_assessment(
        self,
        child_id: str,
        assessment_type: str,
        analysis: Dict[str, Any],
        recommendations: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        保存评估结果 - 使用 Graphiti 原生存储
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（interest_mining/trend_analysis/comprehensive）
            analysis: 分析结果
            recommendations: 建议（可选）
            
        Returns:
            assessment_id
        """
        try:
            from graphiti_core.nodes import EntityNode
            import json
            
            assessment_id = f"assess_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
            
            # 创建评估实体节点
            assessment_node = EntityNode(
                uuid=assessment_id,
                name=f"{assessment_type} 评估",
                group_id=child_id,
                labels=['ChildAssessment', 'Assessment'],
                attributes={
                    'assessment_id': assessment_id,
                    'child_id': child_id,
                    'assessor_id': 'system_llm',
                    'timestamp': datetime.now(timezone.utc).isoformat(),
                    'assessment_type': assessment_type,
                    'analysis': json.dumps(analysis),  # 序列化
                    'recommendations': json.dumps(recommendations or {})  # 序列化
                },
                created_at=datetime.now(timezone.utc)
            )
            
            # 生成 embedding
            await assessment_node.generate_name_embedding(self.graphiti.embedder)
            
            # 保存到图数据库
            await assessment_node.save(self.graphiti.driver)
            
            return assessment_id
            
        except Exception as e:
            print(f"[save_assessment] 保存失败: {e}")
            raise
    
    async def get_latest_assessment(
        self,
        child_id: str,
        assessment_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取最新评估 - 使用 Graphiti 原生查询
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            
        Returns:
            最新评估数据（AssessmentNode 字典格式）
        """
        try:
            # 构建查询条件
            type_filter = ""
            params = {"child_id": child_id}
            
            if assessment_type:
                type_filter = "AND props.assessment_type = $assessment_type"
                params["assessment_type"] = assessment_type
            
            records, _, _ = await self.graphiti.driver.execute_query(
                f"""
                MATCH (a:Entity {{group_id: $child_id}})
                WHERE 'ChildAssessment' IN labels(a)
                WITH a, properties(a) AS props
                WHERE true {type_filter}
                RETURN a.uuid AS assessment_id,
                       a.name AS name,
                       props,
                       a.created_at AS created_at
                ORDER BY a.created_at DESC
                LIMIT 1
                """,
                **params
            )
            
            if records:
                record = records[0]
                props = record['props']
                
                import json
                # 反序列化嵌套对象
                analysis = props.get('analysis', '{}')
                recommendations = props.get('recommendations', '{}')
                
                try:
                    analysis = json.loads(analysis) if isinstance(analysis, str) else analysis
                except:
                    analysis = {}
                
                try:
                    recommendations = json.loads(recommendations) if isinstance(recommendations, str) else recommendations
                except:
                    recommendations = {}
                
                return {
                    "assessment_id": record['assessment_id'],
                    "child_id": props.get('child_id', ''),
                    "assessor_id": props.get('assessor_id', ''),
                    "timestamp": props.get('timestamp', ''),
                    "assessment_type": props.get('assessment_type', ''),
                    "analysis": analysis,
                    "recommendations": recommendations
                }
            
            return None
            
        except Exception as e:
            print(f"[get_latest_assessment] 查询失败: {e}")
            return None
    
    async def get_assessment_history(
        self,
        child_id: str,
        assessment_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取评估历史 - 使用 Graphiti 原生查询
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            limit: 返回数量限制
            
        Returns:
            评估历史列表
        """
        try:
            # 构建查询条件
            type_filter = ""
            params = {"child_id": child_id, "limit": limit}
            
            if assessment_type:
                type_filter = "AND props.assessment_type = $assessment_type"
                params["assessment_type"] = assessment_type
            
            records, _, _ = await self.graphiti.driver.execute_query(
                f"""
                MATCH (a:Entity {{group_id: $child_id}})
                WHERE 'ChildAssessment' IN labels(a)
                WITH a, properties(a) AS props
                WHERE true {type_filter}
                RETURN a.uuid AS assessment_id,
                       a.name AS name,
                       props,
                       a.created_at AS created_at
                ORDER BY a.created_at DESC
                LIMIT $limit
                """,
                **params
            )
            
            assessments = []
            for record in records:
                props = record['props']
                
                import json
                # 反序列化嵌套对象
                analysis = props.get('analysis', '{}')
                recommendations = props.get('recommendations', '{}')
                
                try:
                    analysis = json.loads(analysis) if isinstance(analysis, str) else analysis
                except:
                    analysis = {}
                
                try:
                    recommendations = json.loads(recommendations) if isinstance(recommendations, str) else recommendations
                except:
                    recommendations = {}
                
                assessments.append({
                    "assessment_id": record['assessment_id'],
                    "child_id": props.get('child_id', ''),
                    "assessor_id": props.get('assessor_id', ''),
                    "timestamp": props.get('timestamp', ''),
                    "assessment_type": props.get('assessment_type', ''),
                    "analysis": analysis,
                    "recommendations": recommendations
                })
            
            return assessments
            
        except Exception as e:
            print(f"[get_assessment_history] 查询失败: {e}")
            return []
    
    # ========== Graphiti 高级功能 ==========
    
    async def discover_interest_communities(
        self,
        child_id: str
    ) -> Dict[str, Any]:
        """
        使用 Graphiti 社区检测发现兴趣聚类
        
        通过分析孩子的行为图谱，自动识别兴趣社区（相关联的兴趣、对象、行为的聚类）
        
        Args:
            child_id: 孩子ID
            
        Returns:
            {
                "communities": [
                    {
                        "community_id": "...",
                        "name": "...",
                        "summary": "...",
                        "members": ["node_uuid1", "node_uuid2", ...],
                        "size": 5
                    },
                    ...
                ],
                "insights": "基于社区的洞察"
            }
        """
        try:
            # 1. 使用 Graphiti 构建社区
            community_nodes, community_edges = await self.graphiti.build_communities(
                group_ids=[child_id]
            )
            
            # 2. 转换为返回格式
            communities = []
            for node in community_nodes:
                # 获取社区成员
                members_query = """
                MATCH (c:Community {uuid: $community_uuid})-[:HAS_MEMBER]->(m)
                RETURN m.uuid AS member_uuid, m.name AS member_name
                """
                records, _, _ = await self.graphiti.driver.execute_query(
                    members_query,
                    community_uuid=node.uuid
                )
                
                members = [
                    {"uuid": record["member_uuid"], "name": record.get("member_name", "")}
                    for record in records
                ]
                
                communities.append({
                    "community_id": node.uuid,
                    "name": node.name,
                    "summary": node.summary,
                    "members": members,
                    "size": len(members)
                })
            
            # 3. 生成洞察
            insights = self._generate_community_insights(communities)
            
            return {
                "communities": communities,
                "insights": insights,
                "total_communities": len(communities)
            }
            
        except Exception as e:
            return {
                "communities": [],
                "insights": f"社区检测失败: {str(e)}",
                "total_communities": 0
            }
    
    def _generate_community_insights(self, communities: List[Dict]) -> str:
        """根据社区生成洞察"""
        if not communities:
            return "暂无足够数据进行社区分析"
        
        insights = []
        insights.append(f"发现 {len(communities)} 个兴趣社区：")
        
        for i, comm in enumerate(communities[:5], 1):  # 只展示前5个
            insights.append(f"{i}. {comm['name']} - {comm['size']} 个相关元素")
            if comm.get('summary'):
                insights.append(f"   {comm['summary'][:100]}...")
        
        return "\n".join(insights)
    
    async def analyze_temporal_trends(
        self,
        child_id: str,
        dimension: str = "interest",
        days: int = 30
    ) -> Dict[str, Any]:
        """
        使用 Graphiti 时序分析功能分析发展趋势
        
        Args:
            child_id: 孩子ID
            dimension: 分析维度（interest/function/behavior）
            days: 分析天数
            
        Returns:
            {
                "dimension": "interest",
                "period_days": 30,
                "trends": [
                    {
                        "name": "visual",
                        "data_points": [
                            {"date": "2024-01-01", "value": 7.5},
                            ...
                        ],
                        "trend": "increasing",  # increasing/decreasing/stable
                        "change_rate": 0.15  # 变化率
                    },
                    ...
                ],
                "summary": "趋势总结"
            }
        """
        try:
            from datetime import timedelta
            
            # 1. 计算时间范围
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # 2. 使用 Graphiti 搜索获取时序数据
            search_queries = {
                "interest": ["兴趣表现", "喜欢的活动", "偏好"],
                "function": ["社交能力", "沟通能力", "情绪调节"],
                "behavior": ["行为表现", "互动情况", "进步"]
            }
            
            queries = search_queries.get(dimension, search_queries["interest"])
            
            all_edges = []
            for query in queries:
                edges = await self.graphiti.search(
                    query=query,
                    group_ids=[child_id],
                    num_results=50
                )
                all_edges.extend(edges)
            
            # 3. 按时间分组分析
            trends = self._analyze_edges_temporal(all_edges, start_date, end_date)
            
            # 4. 生成总结
            summary = self._generate_trend_summary(trends, dimension)
            
            return {
                "dimension": dimension,
                "period_days": days,
                "trends": trends,
                "summary": summary,
                "total_data_points": len(all_edges)
            }
            
        except Exception as e:
            return {
                "dimension": dimension,
                "period_days": days,
                "trends": [],
                "summary": f"趋势分析失败: {str(e)}",
                "total_data_points": 0
            }
    
    def _analyze_edges_temporal(
        self,
        edges: List,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """分析边的时序数据"""
        # 简化实现：按创建时间分组
        from collections import defaultdict
        
        time_series = defaultdict(list)
        
        for edge in edges:
            if hasattr(edge, 'created_at'):
                date_key = edge.created_at.date().isoformat()
                time_series[date_key].append(edge)
        
        # 构建趋势数据
        trends = []
        sorted_dates = sorted(time_series.keys())
        
        if len(sorted_dates) >= 2:
            first_count = len(time_series[sorted_dates[0]])
            last_count = len(time_series[sorted_dates[-1]])
            
            if last_count > first_count * 1.2:
                trend = "increasing"
                change_rate = (last_count - first_count) / first_count
            elif last_count < first_count * 0.8:
                trend = "decreasing"
                change_rate = (first_count - last_count) / first_count
            else:
                trend = "stable"
                change_rate = 0.0
            
            trends.append({
                "name": "overall",
                "data_points": [
                    {"date": date, "value": len(time_series[date])}
                    for date in sorted_dates
                ],
                "trend": trend,
                "change_rate": change_rate
            })
        
        return trends
    
    def _generate_trend_summary(self, trends: List[Dict], dimension: str) -> str:
        """生成趋势总结"""
        if not trends:
            return f"{dimension} 维度暂无足够数据进行趋势分析"
        
        summary_parts = []
        for trend in trends:
            if trend["trend"] == "increasing":
                summary_parts.append(f"{trend['name']} 呈上升趋势（+{trend['change_rate']:.1%}）")
            elif trend["trend"] == "decreasing":
                summary_parts.append(f"{trend['name']} 呈下降趋势（-{trend['change_rate']:.1%}）")
            else:
                summary_parts.append(f"{trend['name']} 保持稳定")
        
        return "；".join(summary_parts)
    
    async def intelligent_search(
        self,
        child_id: str,
        query: str,
        search_type: str = "hybrid",
        num_results: int = 10
    ) -> Dict[str, Any]:
        """
        使用 Graphiti 高级搜索功能进行智能检索
        
        Args:
            child_id: 孩子ID
            query: 搜索查询
            search_type: 搜索类型（hybrid/semantic/keyword）
            num_results: 返回结果数量
            
        Returns:
            {
                "query": "...",
                "results": [
                    {
                        "fact": "...",
                        "source": "...",
                        "relevance_score": 0.95,
                        "timestamp": "..."
                    },
                    ...
                ],
                "total_results": 10
            }
        """
        try:
            # 使用 Graphiti 的高级搜索
            from graphiti_core.search.search_config_recipes import (
                COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
                EDGE_HYBRID_SEARCH_RRF
            )
            
            # 选择搜索配置
            if search_type == "hybrid":
                config = COMBINED_HYBRID_SEARCH_CROSS_ENCODER
            else:
                config = EDGE_HYBRID_SEARCH_RRF
            
            config.limit = num_results
            
            # 执行搜索
            search_results = await self.graphiti.search_(
                query=query,
                config=config,
                group_ids=[child_id]
            )
            
            # 转换结果
            results = []
            for edge in search_results.edges:
                results.append({
                    "fact": edge.fact,
                    "source_node": edge.source_node_uuid,
                    "target_node": edge.target_node_uuid,
                    "relevance_score": 0.9,  # 简化：实际应该从搜索结果中获取
                    "timestamp": edge.created_at.isoformat() if hasattr(edge, 'created_at') else None
                })
            
            return {
                "query": query,
                "results": results,
                "total_results": len(results),
                "search_type": search_type
            }
            
        except Exception as e:
            return {
                "query": query,
                "results": [],
                "total_results": 0,
                "error": str(e)
            }
    
    async def close(self):
        """关闭服务 - 关闭 Graphiti driver"""
        if self.graphiti and self.graphiti.driver:
            await self.graphiti.driver.close()
        
        # 保留 storage 的关闭（向后兼容）
        if hasattr(self, 'storage') and self.storage:
            await self.storage.close()


# ============ 全局服务实例 ============

_memory_service_instance: Optional[MemoryService] = None


async def get_memory_service(config: Optional[MemoryConfig] = None) -> MemoryService:
    """获取记忆服务实例（单例）"""
    global _memory_service_instance
    
    if _memory_service_instance is None:
        _memory_service_instance = MemoryService(config)
        await _memory_service_instance.initialize()
    
    return _memory_service_instance
