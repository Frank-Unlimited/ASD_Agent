"""
文件上传服务
"""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException

from .config import (
    UPLOAD_BASE_DIR,
    MAX_FILE_SIZE_BYTES,
    ALLOWED_EXTENSIONS,
    EXTENSION_TO_CATEGORY,
    get_category_dir,
    ensure_upload_dirs
)


class FileUploadService:
    """文件上传服务"""
    
    def __init__(self):
        """初始化服务，确保上传目录存在"""
        ensure_upload_dirs()
    
    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    
    def _detect_category(self, extension: str) -> str:
        """根据扩展名检测文件分类"""
        return EXTENSION_TO_CATEGORY.get(extension, 'other')
    
    def _validate_file(self, file: UploadFile, extension: str) -> None:
        """验证文件"""
        # 检查文件扩展名是否允许
        all_extensions = []
        for exts in ALLOWED_EXTENSIONS.values():
            all_extensions.extend(exts)
        
        if extension not in all_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件类型: .{extension}。支持的类型: {', '.join(all_extensions)}"
            )
    
    def _generate_filename(self, original_filename: str) -> str:
        """生成唯一文件名"""
        extension = self._get_file_extension(original_filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        random_id = uuid.uuid4().hex[:8]
        return f"{timestamp}_{random_id}.{extension}"
    
    async def upload_file(
        self,
        file: UploadFile,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传文件到本地
        
        Args:
            file: FastAPI UploadFile 对象
            category: 文件分类（可选，不传则自动检测）
        
        Returns:
            {
                "file_path": "完整文件路径",
                "filename": "生成的文件名",
                "original_filename": "原始文件名",
                "file_size": 文件大小（字节）,
                "category": "文件分类"
            }
        """
        try:
            # 获取文件扩展名
            extension = self._get_file_extension(file.filename)
            
            # 验证文件
            self._validate_file(file, extension)
            
            # 检测或使用指定的分类
            if category is None:
                category = self._detect_category(extension)
            
            # 生成唯一文件名
            new_filename = self._generate_filename(file.filename)
            
            # 获取目标目录
            category_dir = get_category_dir(category)
            file_path = category_dir / new_filename
            
            # 读取文件内容
            content = await file.read()
            
            # 检查文件大小
            file_size = len(content)
            if file_size > MAX_FILE_SIZE_BYTES:
                raise HTTPException(
                    status_code=400,
                    detail=f"文件大小超过限制: {file_size / 1024 / 1024:.2f}MB > {MAX_FILE_SIZE_BYTES / 1024 / 1024}MB"
                )
            
            # 确保父目录存在
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # 获取绝对路径字符串
            abs_path = str(file_path.absolute())
            
            return {
                "file_path": abs_path,
                "filename": new_filename,
                "original_filename": file.filename,
                "file_size": file_size,
                "category": category
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"文件上传失败: {str(e)}"
            )
