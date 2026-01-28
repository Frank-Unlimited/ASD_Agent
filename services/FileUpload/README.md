# 文件上传服务

## 功能说明

提供客户端文件上传到服务器本地的功能，方便后续的文档解析、视频分析、语音处理等操作。

## 特性

- ✅ 支持多种文件类型（图片、文档、音频、视频）
- ✅ 自动文件分类存储
- ✅ 文件大小限制（默认 100MB）
- ✅ 唯一文件名生成（避免冲突）
- ✅ 文件类型验证

## 支持的文件类型

### 图片
- jpg, jpeg, png, bmp, webp

### 文档
- pdf, docx, doc

### 音频
- mp3, wav, pcm, m4a, aac, flac, ogg

### 视频
- mp4, avi, mov, mkv

## 配置

在 `.env` 文件中配置：

```bash
# 文件上传配置
UPLOAD_BASE_DIR=E:/pro/hhc/uploads
MAX_FILE_SIZE_MB=100
```

## 目录结构

```
E:/pro/hhc/uploads/
├── images/      # 图片文件
├── documents/   # 文档文件
├── audio/       # 音频文件
└── videos/      # 视频文件
```

## API 使用

### 上传文件

**请求：**
```
POST /api/infrastructure/file_upload/upload
Content-Type: multipart/form-data

参数:
- file: 文件对象（必需）
- category: 文件分类（可选: image/document/audio/video）
```

**响应：**
```json
{
  "success": true,
  "data": {
    "file_path": "E:/pro/hhc/uploads/images/20260128_143025_abc123.jpg",
    "filename": "20260128_143025_abc123.jpg",
    "original_filename": "report.jpg",
    "file_size": 1024000,
    "category": "image"
  },
  "message": "文件上传成功"
}
```

## 使用示例

### JavaScript/前端

```javascript
// 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await fetch('http://localhost:7860/api/infrastructure/file_upload/upload', {
  method: 'POST',
  body: formData
});

const result = await response.json();
const filePath = result.data.file_path;

// 使用文件路径调用其他服务
await fetch('http://localhost:7860/api/infrastructure/document_parser/parse_report', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_path: filePath,
    file_type: 'image'
  })
});
```

### curl

```bash
# 上传文件
curl -X POST http://localhost:7860/api/infrastructure/file_upload/upload \
  -F "file=@/path/to/your/file.jpg"

# 指定分类
curl -X POST http://localhost:7860/api/infrastructure/file_upload/upload \
  -F "file=@/path/to/your/file.jpg" \
  -F "category=image"
```

## 文件命名规则

上传的文件会自动重命名为：`{日期}_{时间}_{随机ID}.{扩展名}`

示例：`20260128_143025_a1b2c3d4.jpg`

这样可以：
- 避免文件名冲突
- 保留时间信息便于管理
- 增加安全性

## 安全措施

1. **文件类型验证**：只允许指定类型的文件上传
2. **文件大小限制**：防止上传过大文件
3. **路径安全**：防止路径遍历攻击
4. **文件名清理**：自动生成安全的文件名
