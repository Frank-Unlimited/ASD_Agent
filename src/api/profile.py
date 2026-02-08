"""
档案管理 API
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from typing import Dict, Any
import os

from src.models.profile import (
    ChildProfile,
    ProfileImportResponse,
    ProfileExportData
)
from src.container import get_memory_service, get_sqlite_service
from services.FileUpload.service import FileUploadService
from services.Multimodal_Understanding.api_interface import parse_image
from services.Multimodal_Understanding.utils import encode_local_image

router = APIRouter(prefix="/api/profile", tags=["档案管理"])


@router.post("/import/image")
async def import_profile_from_image(
    file: UploadFile = File(..., description="医学报告图片"),
    memory_service = Depends(get_memory_service),
    sqlite_service = Depends(get_sqlite_service)
):
    """
    从医学报告图片导入档案
    
    流程：
    1. 上传图片文件
    2. 使用多模态理解服务提取文字（OCR）
    3. 交给 Memory 服务自动解析并创建档案
    """
    try:
        # 1. 上传文件
        file_service = FileUploadService()
        upload_result = await file_service.upload_file(file, category="document")
        image_path = upload_result['file_path']
        
        print(f"[档案导入] 图片已上传: {image_path}")
        
        # 2. 提取文字并生成画像总结
        print(f"[档案导入] 开始提取文字...")
        
        # 编码图片为 base64
        image_base64 = encode_local_image(image_path)
        
        # 使用多模态理解服务提取文字并生成画像
        prompt = """
请完成两个任务：

1. 提取这张医学报告中的所有文字内容，保持原有格式和结构。

2. 基于提取的内容，生成一个简短的孩子画像总结（100-150字），包括：
   - 孩子的基本情况（年龄、诊断）
   - 主要特点和表现
   - 当前的发展状况
   - 需要关注的重点

请按以下格式输出：

【提取的文字】
（这里是完整的文字内容）

【孩子画像】
（这里是100-150字的画像总结）
"""
        
        result_text = parse_image(image_base64, prompt)
        
        print(f"[档案导入] ✅ 文字提取完成")
        print(f"[档案导入] 📄 Gemini 解析结果（完整）:")
        print("=" * 80)
        print(result_text)
        print("=" * 80)
        
        # 3. 分离提取的文字和画像总结
        extracted_text = ""
        profile_summary = ""
        
        if "【提取的文字】" in result_text and "【孩子画像】" in result_text:
            parts = result_text.split("【孩子画像】")
            extracted_text = parts[0].replace("【提取的文字】", "").strip()
            profile_summary = parts[1].strip()
        else:
            # 如果格式不对，全部作为提取文字
            extracted_text = result_text
            profile_summary = "档案已导入，正在生成详细评估..."
        
        print(f"[档案导入] 📝 提取的文字（前200字）: {extracted_text[:200]}...")
        print(f"[档案导入] 🎯 画像总结（前100字）: {profile_summary[:100]}...")
        
        # 4. 构建医学报告数据，交给 Memory 服务解析
        report_data = {
            "name": "待解析",  # Memory 服务会自动解析
            "age": 0,
            "diagnosis": "",
            "medical_reports": extracted_text,  # 提取的文字
            "assessment_scales": "",
            "image_path": image_path
        }
        
        # 5. 调用 Memory 服务解析医学报告（自动提取实体关系）
        print(f"[档案导入] 调用 Memory 服务解析医学报告...")
        memory_result = await memory_service.import_profile(report_data)
        
        # 6. 创建系统档案（保存到 SQLite）
        print(f"[档案导入] 创建系统档案...")
        from datetime import datetime
        from src.models.profile import ChildProfile, Gender, DiagnosisLevel
        
        # 从 Graphiti 获取解析后的信息
        child_data = await memory_service.get_child(memory_result["child_id"]) or {}
        
        # 处理 child_data 为 None 的情况
        if child_data is None:
            print(f"[档案导入] 警告: 未能从 Memory 服务获取孩子数据，使用默认值")
            child_data = {
                "name": "待完善",
                "basic_info": {}
            }
        
        profile = ChildProfile(
            child_id=memory_result["child_id"],
            name=child_data.get("name", "待完善"),
            gender=Gender.OTHER,  # 默认值，后续可以更新
            birth_date=datetime.now().strftime("%Y-%m-%d"),  # 默认值
            diagnosis=child_data.get("basic_info", {}).get("diagnosis", ""),
            diagnosis_level=DiagnosisLevel.NOT_DIAGNOSED,  # 默认值
            archive_files=[image_path],  # 保存医学报告图片路径
            notes=f"从医学报告导入\n\n画像总结：\n{profile_summary}\n\n提取的文字：\n{extracted_text[:500]}..."
        )
        
        # 保存到 SQLite
        sqlite_service.save_child(profile)
        print(f"[档案导入] 系统档案已创建: {profile.child_id}")
        
        # 7. 返回结构化响应
        return ProfileImportResponse(
            child_id=memory_result["child_id"],
            assessment_id=memory_result["assessment_id"],
            profile_summary=profile_summary,
            extracted_text=extracted_text,
            image_path=image_path,
            message=f"档案创建成功，已为 {profile.name} 生成初始评估"
        )
        
    except Exception as e:
        print(f"[档案导入] 失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"档案导入失败: {str(e)}")


@router.post("/import/text")
async def import_profile_from_text(
    profile_data: Dict[str, Any],
    memory_service = Depends(get_memory_service),
    sqlite_service = Depends(get_sqlite_service)
):
    """
    从文字描述导入档案
    
    请求数据：
    {
        "name": "孩子姓名",
        "age": 年龄,
        "diagnosis": "诊断信息",
        "medical_reports": "医学报告（文字）",
        "assessment_scales": "评估量表（文字）"
    }
    """
    try:
        # 1. 调用 Memory 服务解析医学报告
        memory_result = await memory_service.import_profile(profile_data)
        
        # 2. 创建系统档案（保存到 SQLite）
        from datetime import datetime
        from src.models.profile import ChildProfile, Gender, DiagnosisLevel
        
        profile = ChildProfile(
            child_id=memory_result["child_id"],
            name=profile_data.get("name", "待完善"),
            gender=Gender.OTHER,
            birth_date=datetime.now().strftime("%Y-%m-%d"),
            diagnosis=profile_data.get("diagnosis", ""),
            diagnosis_level=DiagnosisLevel.NOT_DIAGNOSED,
            notes=f"从文字导入\n\n医学报告：\n{profile_data.get('medical_reports', '')[:500]}..."
        )
        
        sqlite_service.save_child(profile)
        
        return {
            "child_id": memory_result["child_id"],
            "assessment_id": memory_result["assessment_id"],
            "message": f"档案创建成功，已为 {profile.name} 生成初始评估"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"档案导入失败: {str(e)}")


@router.get("/{child_id}")
async def get_profile(
    child_id: str,
    sqlite_service = Depends(get_sqlite_service)
):
    """获取孩子档案"""
    try:
        profile = sqlite_service.get_child(child_id)

        if not profile:
            raise HTTPException(status_code=404, detail=f"档案不存在: {child_id}")

        return profile.dict()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取档案失败: {str(e)}")


@router.get("/{child_id}/stats")
async def get_profile_stats(
    child_id: str,
    sqlite_service = Depends(get_sqlite_service),
    memory_service = Depends(get_memory_service)
):
    """获取孩子统计数据（雷达图、趋势图、兴趣热力图）"""
    try:
        # 获取档案
        profile = sqlite_service.get_child(child_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"档案不存在: {child_id}")

        # DIR 六大能力维度雷达图数据
        radar_data = []
        dimension_names = [
            "自我调节", "亲密感", "双向沟通",
            "共同注意", "情绪思考", "创造力"
        ]

        # 从档案中获取维度数据
        if profile.development_dimensions:
            dim_map = {d.dimension_name: d.current_level for d in profile.development_dimensions}
            for name in dimension_names:
                level = dim_map.get(name)
                if level is not None:
                    radar_data.append({
                        "subject": name,
                        "A": level
                    })

        # 趋势数据（从游戏会话历史获取）
        trend_data = []
        try:
            sessions = sqlite_service.get_game_session_history(child_id, limit=7)
            if sessions:
                for i, session in enumerate(reversed(sessions)):
                    trend_data.append({
                        "name": f"Day{i+1}",
                        "engagement": session.get("child_engagement_score", 70) or 70
                    })
        except Exception as e:
            print(f"[Profile API] 获取趋势数据失败: {e}")

        # 兴趣热力图数据
        interests_data = []
        if profile.interests:
            # 按类别分组
            category_map = {}
            for interest in profile.interests:
                category = interest.tags[0] if interest.tags else "其他"
                if category not in category_map:
                    category_map[category] = []
                category_map[category].append({
                    "name": interest.name,
                    "level": interest.intensity or 3
                })

            for category, items in category_map.items():
                interests_data.append({
                    "category": category,
                    "items": items
                })

        return {
            "radar": radar_data,
            "trend": trend_data,
            "interests": interests_data
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[Profile API] 获取统计数据失败: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")


@router.get("/{child_id}/export")
async def export_profile(
    child_id: str,
    format: str = "json",
    sqlite_service = Depends(get_sqlite_service),
    memory_service = Depends(get_memory_service)
):
    """
    导出档案
    
    支持格式：
    - json: JSON 格式
    - markdown: Markdown 格式
    """
    try:
        # 获取档案
        profile = sqlite_service.get_child(child_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"档案不存在: {child_id}")
        
        # 获取最新评估
        latest_assessment = await memory_service.get_latest_assessment(
            child_id=child_id,
            assessment_type="comprehensive"
        )
        
        if format == "json":
            from fastapi.responses import JSONResponse
            export_data = {
                "profile": profile.dict(),
                "latest_assessment": latest_assessment
            }
            return JSONResponse(content=export_data)
        
        elif format == "markdown":
            from fastapi.responses import PlainTextResponse
            markdown_content = _generate_profile_markdown(profile, latest_assessment)
            return PlainTextResponse(
                content=markdown_content,
                media_type="text/markdown",
                headers={
                    "Content-Disposition": f"attachment; filename=profile_{child_id}.md"
                }
            )
        
        else:
            raise HTTPException(status_code=400, detail="不支持的导出格式")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出档案失败: {str(e)}")


@router.get("/")
async def list_profiles(
    sqlite_service = Depends(get_sqlite_service)
):
    """获取所有档案列表"""
    try:
        profiles = sqlite_service.get_all_children()
        return {
            "profiles": profiles or [],
            "total": len(profiles) if profiles else 0
        }
    except Exception as e:
        # 数据库未初始化或其他错误时返回空列表
        print(f"[Profile API] 获取档案列表失败: {e}")
        return {
            "profiles": [],
            "total": 0
        }


@router.get("/{child_id}/stats")
async def get_profile_stats(
    child_id: str,
    memory_service = Depends(get_memory_service)
):
    """
    获取孩子的统计数据
    
    返回：
    - 观察记录数量
    - 游戏会话数量
    - 评估次数
    - 最近活动时间
    """
    try:
        # 从Memory服务获取统计数据
        stats = await memory_service.get_child_stats(child_id)
        
        return {
            "child_id": child_id,
            "stats": stats,
            "message": "统计数据获取成功"
        }
    except Exception as e:
        # 如果获取失败，返回默认值
        print(f"[Profile API] 获取统计数据失败: {e}")
        return {
            "child_id": child_id,
            "stats": {
                "observation_count": 0,
                "game_session_count": 0,
                "assessment_count": 0,
                "last_activity": None
            },
            "message": "统计数据获取成功（使用默认值）"
        }


def _generate_profile_markdown(profile: ChildProfile, latest_assessment: dict = None) -> str:
    """生成 Markdown 格式的档案"""
    from datetime import datetime
    
    md = f"""# 孩子档案

**档案ID**: {profile.child_id}  
**姓名**: {profile.name}  
**性别**: {profile.gender.value}  
**出生日期**: {profile.birth_date}  

---

## 诊断信息

**诊断**: {profile.diagnosis or '未填写'}  
**诊断程度**: {profile.diagnosis_level.value if profile.diagnosis_level else '未填写'}  
**诊断日期**: {profile.diagnosis_date or '未填写'}  

---

## 发展维度评估

"""
    
    if profile.development_dimensions:
        for dim in profile.development_dimensions:
            md += f"### {dim.dimension_name}\n"
            md += f"- **当前水平**: {dim.current_level or '未评估'}/10\n"
            if dim.baseline:
                md += f"- **基线**: {dim.baseline}/10\n"
            if dim.notes:
                md += f"- **备注**: {dim.notes}\n"
            md += "\n"
    else:
        md += "暂无发展维度评估数据\n\n"
    
    md += "---\n\n## 兴趣点\n\n"
    
    if profile.interests:
        for interest in profile.interests:
            md += f"### {interest.name}\n"
            md += f"- **强度**: {interest.intensity or '未评估'}/10\n"
            if interest.description:
                md += f"- **描述**: {interest.description}\n"
            if interest.tags:
                md += f"- **标签**: {', '.join(interest.tags)}\n"
            md += "\n"
    else:
        md += "暂无兴趣点数据\n\n"
    
    if latest_assessment:
        md += "---\n\n## 最新评估\n\n"
        md += f"**评估ID**: {latest_assessment.get('assessment_id', '')}\n"
        md += f"**评估时间**: {latest_assessment.get('timestamp', '')}\n"
        md += f"**评估类型**: {latest_assessment.get('assessment_type', '')}\n\n"
    
    if profile.notes:
        md += f"---\n\n## 备注\n\n{profile.notes}\n\n"
    
    md += f"---\n\n*档案创建时间: {profile.created_at}*  \n"
    md += f"*最后更新时间: {profile.updated_at}*\n"
    
    return md
