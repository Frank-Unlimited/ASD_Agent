"""
观察记录服务
负责记录和管理孩子的日常观察

依赖的基础服务：
- Speech_Processing: 语音转文字
- Graphiti: 保存观察到知识图谱
- SQLite: 存储观察记录
- LLM: 结构化提取观察信息
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.models.observation import (
    Observation,
    ObservationType,
    StructuredObservationData,
    ObservationResponse,
    ObservationListResponse,
    VoiceObservationRequest,
    TextObservationRequest,
    ObservationDimension,
    ObservationSignificance,
    EmotionalState,
)

# 导入基础服务API
from services.Speech_Processing.api_interface import speech_to_text
from services.Graphiti.api_interface import save_memories


class ObservationService:
    """观察记录服务"""

    def __init__(
        self,
        sqlite_service: Any,  # SQLite服务
        llm_service: Any,  # LLM服务
    ):
        """
        初始化观察记录服务

        Args:
            sqlite_service: SQLite数据库服务
            llm_service: LLM服务（用于结构化提取）
        """
        self.sqlite = sqlite_service
        self.llm = llm_service

    async def record_voice_observation(
        self,
        request: VoiceObservationRequest
    ) -> ObservationResponse:
        """
        记录语音观察

        流程：
        1. 使用Speech_Processing将语音转文字
        2. 使用LLM提取结构化观察数据
        3. 创建观察记录
        4. 保存到SQLite
        5. 保存到Graphiti知识图谱
        6. 返回观察记录

        Args:
            request: 语音观察请求（包含audio_file_path, child_id等）

        Returns:
            ObservationResponse: 观察记录响应
        """
        print(f"\n[ObservationService] 开始处理语音观察: {request.audio_file_path}")

        # 1. 语音转文字
        try:
            raw_content = speech_to_text(request.audio_file_path)
            print(f"[ObservationService] 语音识别完成: {raw_content[:50]}...")
        except Exception as e:
            print(f"[ObservationService] 语音识别失败: {e}")
            raise ValueError(f"语音识别失败: {str(e)}")

        # 2. 使用LLM提取结构化数据
        structured_data = await self._extract_structured_observation(
            raw_content,
            request.child_id
        )

        # 3. 创建观察记录
        observation_id = f"obs-{uuid.uuid4().hex[:12]}"
        observation = Observation(
            observation_id=observation_id,
            child_id=request.child_id,
            type=ObservationType.VOICE,
            timestamp=datetime.now(),
            raw_content=raw_content,
            audio_file_path=request.audio_file_path,
            structured_data=structured_data,
            session_id=request.session_id,
            game_id=request.game_id,
            parent_notes=request.parent_notes,
            processed=True,
            graphiti_saved=False,
        )

        # 4. 保存到SQLite
        await self.sqlite.save_observation({
            "observationId": observation_id,
            "childId": request.child_id,
            "data": observation.dict()
        })

        # 5. 保存到Graphiti
        await self._save_to_graphiti(observation)
        observation.graphiti_saved = True

        # 更新SQLite中的graphiti_saved标志
        await self.sqlite.save_observation({
            "observationId": observation_id,
            "childId": request.child_id,
            "data": observation.dict()
        })

        print(f"[ObservationService] 语音观察记录成功: {observation_id}")

        return ObservationResponse(
            observation_id=observation_id,
            child_id=request.child_id,
            type=ObservationType.VOICE,
            timestamp=observation.timestamp,
            raw_content=raw_content,
            structured_data=structured_data,
            message="语音观察记录成功"
        )

    async def record_text_observation(
        self,
        request: TextObservationRequest
    ) -> ObservationResponse:
        """
        记录文字观察

        流程：
        1. 使用LLM提取结构化观察数据
        2. 创建观察记录
        3. 保存到SQLite
        4. 保存到Graphiti知识图谱
        5. 返回观察记录

        Args:
            request: 文字观察请求（包含content, child_id等）

        Returns:
            ObservationResponse: 观察记录响应
        """
        print(f"\n[ObservationService] 开始处理文字观察")

        # 1. 使用LLM提取结构化数据
        structured_data = await self._extract_structured_observation(
            request.content,
            request.child_id
        )

        # 2. 创建观察记录
        observation_id = f"obs-{uuid.uuid4().hex[:12]}"
        observation = Observation(
            observation_id=observation_id,
            child_id=request.child_id,
            type=ObservationType.TEXT,
            timestamp=datetime.now(),
            raw_content=request.content,
            structured_data=structured_data,
            session_id=request.session_id,
            game_id=request.game_id,
            parent_notes=request.parent_notes,
            processed=True,
            graphiti_saved=False,
        )

        # 3. 保存到SQLite
        await self.sqlite.save_observation({
            "observationId": observation_id,
            "childId": request.child_id,
            "data": observation.dict()
        })

        # 4. 保存到Graphiti
        await self._save_to_graphiti(observation)
        observation.graphiti_saved = True

        # 更新SQLite
        await self.sqlite.save_observation({
            "observationId": observation_id,
            "childId": request.child_id,
            "data": observation.dict()
        })

        print(f"[ObservationService] 文字观察记录成功: {observation_id}")

        return ObservationResponse(
            observation_id=observation_id,
            child_id=request.child_id,
            type=ObservationType.TEXT,
            timestamp=observation.timestamp,
            raw_content=request.content,
            structured_data=structured_data,
            message="文字观察记录成功"
        )

    async def get_observation_history(
        self,
        child_id: str,
        limit: int = 50,
        offset: int = 0
    ) -> ObservationListResponse:
        """
        获取观察历史记录

        Args:
            child_id: 孩子ID
            limit: 返回数量限制
            offset: 偏移量

        Returns:
            ObservationListResponse: 观察记录列表
        """
        # 从SQLite查询（这里假设SQLite有类似的查询接口）
        # 实际实现时需要根据SQLite服务的接口调整
        history_data = await self.sqlite.get_session_history(child_id)

        # 转换为Observation对象
        observations = []
        # TODO: 根据实际SQLite返回的数据结构进行转换

        return ObservationListResponse(
            child_id=child_id,
            total=len(observations),
            observations=observations
        )

    # ============ 私有方法 ============

    async def _extract_structured_observation(
        self,
        raw_content: str,
        child_id: str
    ) -> StructuredObservationData:
        """
        使用LLM从原始观察内容中提取结构化数据

        Args:
            raw_content: 原始观察内容
            child_id: 孩子ID

        Returns:
            StructuredObservationData: 结构化观察数据
        """
        prompt = f"""
请从以下家长的观察记录中提取结构化信息，以JSON格式返回：

观察内容：
{raw_content}

请提取：
1. dimensions: 涉及的发展维度（数组，可选值：eye_contact, joint_attention, social_interaction, language, imitation, emotional_regulation, play_skills, sensory, motor_skills, cognitive, other）
2. behaviors: 观察到的具体行为（字符串数组）
3. emotional_state: 孩子的情绪状态（可选值：happy, calm, excited, frustrated, anxious, angry, neutral）
4. significance: 观察的重要性（可选值：breakthrough, improvement, normal, concern, regression）
5. key_points: 关键要点（字符串数组）
6. interests_mentioned: 提到的兴趣点（字符串数组）
7. context: 情境描述（字符串，描述当时在做什么活动、环境如何等）
8. duration: 持续时间（字符串，如"3分钟"、"整个上午"）

返回JSON格式：
{{
    "dimensions": ["eye_contact", "social_interaction"],
    "behaviors": ["主动与妈妈对视", "微笑回应"],
    "emotional_state": "happy",
    "significance": "improvement",
    "key_points": ["眼神接触时间比以前长", "出现社交性微笑"],
    "interests_mentioned": ["水流"],
    "context": "在玩水的时候",
    "duration": "约5分钟"
}}

注意：
- 如果某个字段在观察中找不到，返回null或空数组
- 只返回JSON，不要其他文字
"""

        try:
            # 调用LLM
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.1,
                response_format="json"
            )

            # 解析JSON
            data = json.loads(response)

            # 转换为StructuredObservationData
            return StructuredObservationData(
                dimensions=[
                    ObservationDimension(dim) for dim in data.get("dimensions", [])
                ],
                behaviors=data.get("behaviors", []),
                emotional_state=EmotionalState(data.get("emotional_state")) if data.get("emotional_state") else None,
                significance=ObservationSignificance(data.get("significance", "normal")),
                key_points=data.get("key_points", []),
                interests_mentioned=data.get("interests_mentioned", []),
                context=data.get("context"),
                duration=data.get("duration")
            )

        except Exception as e:
            print(f"[ObservationService] LLM结构化提取失败: {e}，使用降级方案")
            # 降级方案：返回基础数据
            return StructuredObservationData(
                dimensions=[],
                behaviors=[],
                emotional_state=None,
                significance=ObservationSignificance.NORMAL,
                key_points=[],
                interests_mentioned=[],
                context=None,
                duration=None
            )

    async def _save_to_graphiti(
        self,
        observation: Observation
    ) -> None:
        """
        将观察记录保存到Graphiti知识图谱

        Args:
            observation: 观察记录
        """
        if not observation.structured_data:
            print("[ObservationService] 没有结构化数据，跳过Graphiti保存")
            return

        # 构建记忆内容
        memories = []

        # 主要观察内容
        content = observation.raw_content
        if observation.structured_data.context:
            content = f"{observation.structured_data.context}: {content}"

        memory = {
            "content": content,
            "type": "observation",
            "timestamp": observation.timestamp.isoformat(),
            "metadata": {
                "source": observation.type.value,
                "observation_id": observation.observation_id,
                "significance": observation.structured_data.significance.value,
                "dimensions": [dim.value for dim in observation.structured_data.dimensions],
                "emotional_state": observation.structured_data.emotional_state.value if observation.structured_data.emotional_state else None,
            }
        }
        memories.append(memory)

        # 如果有突破性进展或重要改善，单独记录
        if observation.structured_data.significance in [ObservationSignificance.BREAKTHROUGH, ObservationSignificance.IMPROVEMENT]:
            for key_point in observation.structured_data.key_points:
                memories.append({
                    "content": key_point,
                    "type": "milestone" if observation.structured_data.significance == ObservationSignificance.BREAKTHROUGH else "improvement",
                    "timestamp": observation.timestamp.isoformat(),
                    "metadata": {
                        "source": "observation_analysis",
                        "observation_id": observation.observation_id,
                    }
                })

        # 保存到Graphiti
        if memories:
            await save_memories(
                child_id=observation.child_id,
                memories=memories
            )
            print(f"[ObservationService] 已保存{len(memories)}条记忆到Graphiti")
