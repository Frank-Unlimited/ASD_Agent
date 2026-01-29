"""
档案管理 API

API层负责：
1. 使用FileUploadService上传文件
2. 调用ProfileService处理业务逻辑
3. 返回响应
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

from src.models.profile import (
    ProfileCreateResponse,
    ProfileUpdateRequest,
    ChildProfile,
)
from src.container import container

router = APIRouter(prefix="/api/profile", tags=["档案管理"])


@router.post("/upload", response_model=ProfileCreateResponse)
async def upload_archive_image(
    file: UploadFile = File(..., description="档案图片文件")
):
    """
    上传档案图片并解析

    流程：
    1. 使用FileUploadService保存上传的图片文件
    2. 调用ProfileService解析图片并创建档案
    3. 返回解析结果和child_id

    注意：此时返回的档案中name和gender是待补充的，需要调用PATCH接口补充
    """
    try:
        # 1. 使用FileUploadService上传文件
        file_upload_service = container.get('file_upload')
        upload_result = await file_upload_service.upload_file(
            file=file,
            category="documents"  # 档案图片归类为documents
        )

        print(f"[API] 档案图片已上传: {upload_result['file_path']}")

        # 2. 调用ProfileService解析图片并创建档案
        profile_service = container.get('profile')
        result = await profile_service.create_profile_from_image(
            image_path=upload_result['file_path']
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"档案上传失败: {str(e)}")


@router.patch("/{child_id}", response_model=ChildProfile)
async def update_profile(
    child_id: str,
    update_data: ProfileUpdateRequest
):
    """
    补充/更新档案信息

    用途：
    1. 首次补充姓名、性别等基本信息
    2. 后续更新诊断信息、备注等

    当家长首次补充姓名和性别后，系统会自动将档案信息存入Graphiti
    """
    try:
        profile_service = container.get('profile')
        updated_profile = await profile_service.update_profile_info(
            child_id=child_id,
            update_data=update_data
        )

        return updated_profile

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"档案更新失败: {str(e)}")


@router.get("/{child_id}", response_model=ChildProfile)
async def get_profile(child_id: str):
    """
    获取孩子档案

    返回完整的档案信息，包括：
    - 基本信息（姓名、性别、出生日期等）
    - 诊断信息
    - 发展维度评估
    - 兴趣点列表
    - 档案文件路径
    """
    try:
        profile_service = container.get('profile')
        profile = await profile_service.get_profile(child_id)

        if not profile:
            raise HTTPException(status_code=404, detail=f"档案不存在: {child_id}")

        return profile

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取档案失败: {str(e)}")
