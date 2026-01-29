"""
档案管理服务
负责创建、更新和查询孩子档案
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional

from src.models.profile import (
    ChildProfile,
    ParsedProfileData,
    ProfileCreateResponse,
    ProfileUpdateRequest,
    DevelopmentDimension,
    InterestPoint,
    DiagnosisLevel,
    Gender,
)
from src.interfaces.infrastructure import (
    IDocumentParserService,
    ISQLiteService,
    IGraphitiService,
)


class ProfileService:
    """档案管理服务"""

    def __init__(
        self,
        document_parser: IDocumentParserService,
        sqlite_service: ISQLiteService,
        graphiti_service: IGraphitiService,
        llm_service: Any,  # LLM服务用于结构化提取
    ):
        self.document_parser = document_parser
        self.sqlite = sqlite_service
        self.graphiti = graphiti_service
        self.llm = llm_service

    async def create_profile_from_image(
        self,
        image_path: str,
        file_type: str = "image"
    ) -> ProfileCreateResponse:
        """
        从档案图片创建孩子档案

        流程：
        1. 使用文档解析服务解析图片
        2. 使用LLM提取结构化信息
        3. 创建初步档案（等待家长补充姓名、性别等）
        4. 保存到SQLite
        5. 返回解析结果和child_id

        Args:
            image_path: 图片文件路径
            file_type: 文件类型（默认image）

        Returns:
            ProfileCreateResponse: 包含child_id和解析数据
        """
        print(f"\n[ProfileService] 开始解析档案图片: {image_path}")

        # 1. 解析图片
        raw_parsed_data = await self.document_parser.parse_report(
            file_path=image_path,
            file_type=file_type
        )

        # 2. 使用LLM提取结构化信息
        parsed_data = await self._extract_structured_profile_data(
            raw_parsed_data.get("raw_text", "")
        )
        parsed_data.raw_text = raw_parsed_data.get("raw_text", "")

        # 3. 生成child_id
        child_id = f"child-{uuid.uuid4().hex[:12]}"

        # 4. 创建初步档案（姓名和性别待补充）
        profile = ChildProfile(
            child_id=child_id,
            name="待补充",  # 家长后续补充
            gender=Gender.OTHER,  # 家长后续补充
            birth_date=parsed_data.birth_date or "2020-01-01",
            diagnosis=parsed_data.diagnosis,
            diagnosis_level=parsed_data.diagnosis_level,
            diagnosis_date=parsed_data.assessment_date,
            development_dimensions=parsed_data.development_dimensions,
            interests=[
                InterestPoint(
                    interest_id=f"int-{i}",
                    name=interest,
                    intensity=5.0,  # 默认中等强度
                )
                for i, interest in enumerate(parsed_data.interests)
            ],
            archive_files=[image_path],
            notes=f"系统自动解析。关键发现: {', '.join(parsed_data.key_findings[:3])}"
        )

        # 5. 保存到SQLite
        await self.sqlite.save_child({
            "childId": child_id,
            "name": profile.name,
            "portrait": profile.dict()
        })

        print(f"[ProfileService] 档案创建成功: {child_id}")

        return ProfileCreateResponse(
            child_id=child_id,
            name=profile.name,
            parsed_data=parsed_data,
            message="档案图片解析成功，请补充孩子的姓名和性别信息"
        )

    async def update_profile_info(
        self,
        child_id: str,
        update_data: ProfileUpdateRequest
    ) -> ChildProfile:
        """
        更新档案信息（家长补充）

        流程：
        1. 从SQLite获取现有档案
        2. 更新字段
        3. 保存到SQLite
        4. 如果是首次完善（补充了姓名和性别），则存入Graphiti

        Args:
            child_id: 孩子ID
            update_data: 更新数据

        Returns:
            ChildProfile: 更新后的档案
        """
        print(f"\n[ProfileService] 更新档案: {child_id}")

        # 1. 获取现有档案
        existing_data = await self.sqlite.get_child(child_id)
        if not existing_data:
            raise ValueError(f"档案不存在: {child_id}")

        existing_profile = ChildProfile(**existing_data["portrait"])

        # 2. 更新字段
        update_dict = update_data.dict(exclude_unset=True)
        for key, value in update_dict.items():
            if value is not None:
                setattr(existing_profile, key, value)

        existing_profile.updated_at = datetime.now()

        # 3. 检查是否首次完善（姓名从"待补充"改为实际姓名）
        is_first_completion = (
            existing_data["portrait"]["name"] == "待补充"
            and update_data.name
            and update_data.name != "待补充"
        )

        # 4. 保存到SQLite
        await self.sqlite.save_child({
            "childId": child_id,
            "name": existing_profile.name,
            "portrait": existing_profile.dict()
        })

        # 5. 如果是首次完善，存入Graphiti
        if is_first_completion:
            await self._save_initial_profile_to_graphiti(existing_profile)
            print(f"[ProfileService] 首次完善档案，已存入Graphiti")

        print(f"[ProfileService] 档案更新成功: {child_id}")

        return existing_profile

    async def get_profile(self, child_id: str) -> Optional[ChildProfile]:
        """
        获取孩子档案

        Args:
            child_id: 孩子ID

        Returns:
            ChildProfile: 档案信息，如果不存在则返回None
        """
        data = await self.sqlite.get_child(child_id)
        if not data:
            return None

        return ChildProfile(**data["portrait"])

    # ============ 私有方法 ============

    async def _extract_structured_profile_data(
        self,
        raw_text: str
    ) -> ParsedProfileData:
        """
        使用LLM从原始文本中提取结构化档案数据

        Args:
            raw_text: 原始解析文本

        Returns:
            ParsedProfileData: 结构化档案数据
        """
        prompt = f"""
请从以下医院报告文本中提取关键信息，以JSON格式返回：

报告文本：
{raw_text}

请提取：
1. diagnosis: 诊断结果（如"自闭症谱系障碍"）
2. diagnosis_level: 诊断级别（mild/moderate/severe/suspected/not_diagnosed）
3. birth_date: 出生日期（YYYY-MM-DD格式）
4. assessment_date: 评估日期（YYYY-MM-DD格式）
5. key_findings: 关键发现列表（字符串数组，最多5条）
6. development_dimensions: 发展维度评估（数组，包含dimension_id, dimension_name, current_level）
   - 可能的维度：eye_contact, joint_attention, social_interaction, language, imitation, emotional_regulation, play_skills, sensory, motor_skills, cognitive
7. interests: 兴趣点列表（字符串数组）
8. recommendations: 医生建议列表（字符串数组）

返回JSON格式：
{{
    "diagnosis": "...",
    "diagnosis_level": "mild",
    "birth_date": "2020-01-01",
    "assessment_date": "2024-01-15",
    "key_findings": ["...", "..."],
    "development_dimensions": [
        {{
            "dimension_id": "eye_contact",
            "dimension_name": "眼神接触",
            "current_level": 3.5
        }}
    ],
    "interests": ["水流", "旋转物体"],
    "recommendations": ["建议...", "建议..."]
}}

注意：
- 如果某个字段在文本中找不到，返回null或空数组
- current_level是0-10的评分
- 只返回JSON，不要其他文字
"""

        try:
            # 调用LLM
            response = await self.llm.generate(
                prompt=prompt,
                temperature=0.1,  # 低温度，保证结构化输出
                response_format="json"
            )

            # 解析JSON
            data = json.loads(response)

            # 转换为ParsedProfileData
            return ParsedProfileData(
                diagnosis=data.get("diagnosis"),
                diagnosis_level=data.get("diagnosis_level"),
                birth_date=data.get("birth_date"),
                assessment_date=data.get("assessment_date"),
                key_findings=data.get("key_findings", []),
                development_dimensions=[
                    DevelopmentDimension(**dim)
                    for dim in data.get("development_dimensions", [])
                ],
                interests=data.get("interests", []),
                recommendations=data.get("recommendations", [])
            )

        except Exception as e:
            print(f"[ProfileService] LLM结构化提取失败: {e}，使用降级方案")
            # 降级方案：返回空数据
            return ParsedProfileData(
                diagnosis=None,
                diagnosis_level=None,
                birth_date=None,
                assessment_date=None,
                key_findings=[],
                development_dimensions=[],
                interests=[],
                recommendations=[]
            )

    async def _save_initial_profile_to_graphiti(
        self,
        profile: ChildProfile
    ) -> None:
        """
        将初始档案信息保存到Graphiti

        Args:
            profile: 孩子档案
        """
        # 构建初始记忆
        memories = []

        # 1. 基础信息
        memories.append({
            "content": f"{profile.name}的基本信息：性别{profile.gender.value}，出生日期{profile.birth_date}",
            "type": "profile",
            "timestamp": profile.created_at.isoformat(),
            "metadata": {
                "source": "initial_profile",
                "child_id": profile.child_id
            }
        })

        # 2. 诊断信息
        if profile.diagnosis:
            memories.append({
                "content": f"{profile.name}的诊断：{profile.diagnosis}（{profile.diagnosis_level.value if profile.diagnosis_level else '未知程度'}）",
                "type": "diagnosis",
                "timestamp": profile.created_at.isoformat(),
                "metadata": {
                    "source": "initial_profile",
                    "diagnosis_date": profile.diagnosis_date
                }
            })

        # 3. 发展维度
        for dim in profile.development_dimensions:
            if dim.current_level is not None:
                memories.append({
                    "content": f"{profile.name}在{dim.dimension_name}维度的初始评估为{dim.current_level}/10",
                    "type": "assessment",
                    "timestamp": profile.created_at.isoformat(),
                    "metadata": {
                        "source": "initial_profile",
                        "dimension": dim.dimension_id,
                        "level": dim.current_level
                    }
                })

        # 4. 兴趣点
        for interest in profile.interests:
            memories.append({
                "content": f"{profile.name}对{interest.name}表现出兴趣",
                "type": "interest",
                "timestamp": profile.created_at.isoformat(),
                "metadata": {
                    "source": "initial_profile",
                    "interest_id": interest.interest_id,
                    "intensity": interest.intensity
                }
            })

        # 保存到Graphiti
        if memories:
            await self.graphiti.save_memories(
                child_id=profile.child_id,
                memories=memories
            )
            print(f"[ProfileService] 已保存{len(memories)}条初始记忆到Graphiti")
