"""
文件上传服务配置
"""
import os
from pathlib import Path

# 上传文件根目录
UPLOAD_BASE_DIR = os.getenv('UPLOAD_DIR', os.getenv('UPLOAD_BASE_DIR', './uploads'))

# 最大文件大小（MB）
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '100'))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'image': ['jpg', 'jpeg', 'png', 'bmp', 'webp'],
    'document': ['pdf', 'docx', 'doc'],
    'audio': ['mp3', 'wav', 'pcm', 'm4a', 'aac', 'flac', 'ogg'],
    'video': ['mp4', 'avi', 'mov', 'mkv']
}

# 文件分类目录
FILE_CATEGORIES = {
    'image': 'images',
    'document': 'documents',
    'audio': 'audio',
    'video': 'videos'
}

# 扩展名到分类的映射
EXTENSION_TO_CATEGORY = {}
for category, extensions in ALLOWED_EXTENSIONS.items():
    for ext in extensions:
        EXTENSION_TO_CATEGORY[ext.lower()] = category


def get_category_dir(category: str) -> Path:
    """获取分类目录路径"""
    base_dir = Path(UPLOAD_BASE_DIR)
    category_name = FILE_CATEGORIES.get(category, 'others')
    return base_dir / category_name


def ensure_upload_dirs():
    """确保上传目录存在"""
    base_dir = Path(UPLOAD_BASE_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    for category_dir in list(FILE_CATEGORIES.values()) + ['others']:
        (base_dir / category_dir).mkdir(parents=True, exist_ok=True)
