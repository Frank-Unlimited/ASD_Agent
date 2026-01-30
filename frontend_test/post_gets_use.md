# API 测试指南

本文档提供所有基础设施服务的 API 测试示例。

---

## 全局前置条件

### 基础环境
- 后端服务已启动（端口 7860）
- Python 环境：`conda activate asd_agent`

### 服务配置（.env 文件）

#### SQLite 数据管理
- `USE_REAL_SQLITE=true`
- 数据库文件路径正确配置

#### Graphiti 记忆网络
- `USE_REAL_GRAPHITI=true`
- Neo4j 容器已启动（端口 7688）
- Neo4j 连接配置：`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### 视频分析服务
- `USE_REAL_VIDEO_ANALYSIS=true`
- 配置多模态 LLM API 密钥（如 `DASHSCOPE_API_KEY`）
- 视频文件路径可访问

#### 语音处理服务
- `USE_REAL_SPEECH=true`
- 配置阿里云语音服务：`ALIYUN_APPKEY`, `ALIYUN_TOKEN`
- （可选）安装 ffmpeg 用于音频格式转换

#### 文档解析服务
- `USE_REAL_DOCUMENT_PARSER=true`
- 配置多模态 LLM API 密钥（如 `DASHSCOPE_API_KEY`）
- 文档文件路径可访问

#### 文件上传服务
- 上传目录已配置（`UPLOAD_BASE_DIR`）
- 文件大小限制（默认 100MB）

---

# SQLite API 测试

## API 端点列表

### 1. 保存孩子档案
**POST** `/api/infrastructure/sqlite/save_child`

```json
{
  "profile": {
    "child_id": "test-child-001",
    "name": "小明",
    "age": 36,
    "gender": "男",
    "diagnosis": "自闭症谱系障碍",
    "eye_contact": 5.0,
    "joint_attention": 4.5,
    "imitation": 3.8,
    "emotional_response": 4.2,
    "strengths": ["喜欢积木", "专注力好"],
    "challenges": ["眼神接触少", "语言表达困难"]
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "保存孩子档案成功"
}
```

---

### 2. 获取孩子档案
**POST** `/api/infrastructure/sqlite/get_child`

```json
{
  "child_id": "test-child-001"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "child_id": "test-child-001",
    "name": "小明",
    "age": 36,
    "eye_contact": 5.0,
    "...": "..."
  }
}
```

---

### 3. 创建干预会话
**POST** `/api/infrastructure/sqlite/create_session`

```json
{
  "child_id": "test-child-001",
  "game_id": "game-001"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "session_id": "session-abc123"
  },
  "message": "创建会话成功"
}
```

---

### 4. 更新会话信息
**POST** `/api/infrastructure/sqlite/update_session`

```json
{
  "session_id": "session-abc123",
  "data": {
    "status": "in_progress",
    "quick_observations": [
      {
        "type": "smile",
        "timestamp": "2026-01-28T14:35:00",
        "description": "孩子微笑了"
      }
    ]
  }
}
```

---

### 5. 保存观察记录
**POST** `/api/infrastructure/sqlite/save_observation`

```json
{
  "observation": {
    "session_id": "session-abc123",
    "child_id": "test-child-001",
    "observation_type": "quick",
    "timestamp": "2026-01-28T14:35:00",
    "content": "孩子在玩积木时主动看向家长，持续约3秒"
  }
}
```

---

### 6. 保存周计划
**POST** `/api/infrastructure/sqlite/save_weekly_plan`

```json
{
  "plan": {
    "child_id": "test-child-001",
    "week_start": "2026-01-27",
    "week_end": "2026-02-02",
    "weekly_goal": "提升眼神接触频率和持续时间",
    "daily_plans": [...]
  }
}
```

---

### 7. 获取会话历史
**GET** `/api/infrastructure/sqlite/session_history/{child_id}?limit=10`

**示例URL：**
```
http://localhost:7860/api/infrastructure/sqlite/session_history/test-child-001?limit=10
```

---

## curl 测试示例

```bash
# 保存孩子档案
curl -X POST http://localhost:7860/api/infrastructure/sqlite/save_child \
  -H "Content-Type: application/json" \
  -d '{"profile": {"child_id": "test-child-001", "name": "小明", "age": 36}}'

# 获取孩子档案
curl -X POST http://localhost:7860/api/infrastructure/sqlite/get_child \
  -H "Content-Type: application/json" \
  -d '{"child_id": "test-child-001"}'

# 创建会话
curl -X POST http://localhost:7860/api/infrastructure/sqlite/create_session \
  -H "Content-Type: application/json" \
  -d '{"child_id": "test-child-001", "game_id": "game-001"}'
```

---

# 视频分析 API 测试

## API 端点列表

### 1. 分析视频
**POST** `/api/infrastructure/video_analysis/analyze_video`

```json
{
  "video_path": "E:\\videos\\session_20260128.mp4",
  "context": {
    "child_profile": {
      "child_id": "test-child-001",
      "name": "小明",
      "age": 36
    },
    "session_info": {
      "session_id": "session-abc123",
      "game_name": "积木游戏",
      "focus_areas": ["eye_contact", "joint_attention"]
    }
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "behaviors": [...],
    "interactions": [...],
    "emotions": {...},
    "attention": {...},
    "summary": "孩子在本次会话中表现良好"
  },
  "message": "视频分析完成"
}
```

---

### 2. 提取关键片段
**POST** `/api/infrastructure/video_analysis/extract_highlights`

```json
{
  "video_path": "E:\\videos\\session_20260128.mp4",
  "analysis_result": {
    "behaviors": [
      {
        "description": "孩子主动看向家长",
        "timestamp": "00:15",
        "significance": 4
      }
    ]
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "00:15",
      "duration": 5,
      "type": "behavior",
      "description": "孩子主动看向家长",
      "importance": 4
    }
  ],
  "message": "提取到 1 个关键片段"
}
```

---

## curl 测试示例

```bash
# 分析视频
curl -X POST http://localhost:7860/api/infrastructure/video_analysis/analyze_video \
  -H "Content-Type: application/json" \
  -d '{"video_path": "E:\\videos\\test.mp4", "context": {"child_profile": {"child_id": "test-child-001"}}}'

# 提取关键片段
curl -X POST http://localhost:7860/api/infrastructure/video_analysis/extract_highlights \
  -H "Content-Type: application/json" \
  -d '{"video_path": "E:\\videos\\test.mp4", "analysis_result": {"behaviors": []}}'
```

---

# 语音服务 API 测试

## API 端点列表

### 1. 语音转文字 (ASR)
**POST** `/api/infrastructure/speech/speech_to_text`

```json
{
  "audio_path": "E:\\audio\\observation_20260128.mp3"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "text": "孩子今天主动看向我三次，每次持续大约两到三秒钟"
  },
  "message": "语音识别完成"
}
```

**支持格式**：MP3, WAV, PCM, M4A, AAC, FLAC, OGG

---

### 2. 文字转语音 (TTS)
**POST** `/api/infrastructure/speech/text_to_speech`

```json
{
  "text": "小明，我们一起来玩积木吧！"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "audio_path": "C:\\Users\\windows\\AppData\\Local\\Temp\\tts_a1b2c3d4.wav"
  },
  "message": "语音合成完成"
}
```

---

## curl 测试示例

```bash
# 语音转文字
curl -X POST http://localhost:7860/api/infrastructure/speech/speech_to_text \
  -H "Content-Type: application/json" \
  -d '{"audio_path": "E:\\audio\\test.mp3"}'

# 文字转语音
curl -X POST http://localhost:7860/api/infrastructure/speech/text_to_speech \
  -H "Content-Type: application/json" \
  -d '{"text": "小明，我们一起来玩积木吧！"}'
```

---

# 文档解析服务 API 测试

## API 端点列表

### 1. 解析医院报告
**POST** `/api/infrastructure/document_parser/parse_report`

```json
{
  "file_path": "E:\\documents\\diagnosis_report.jpg",
  "file_type": "image"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "raw_text": "完整的解析文本...",
    "diagnosis": "诊断结果摘要",
    "severity": "严重程度评估",
    "recommendations": ["建议1", "建议2"],
    "file_path": "E:\\documents\\diagnosis_report.jpg"
  },
  "message": "报告解析完成"
}
```

**支持格式**：JPG, PNG, BMP, WEBP, PDF, DOCX

---

### 2. 解析量表数据
**POST** `/api/infrastructure/document_parser/parse_scale`

**使用图片：**
```json
{
  "scale_type": "ABC",
  "scale_data": {
    "image_path": "E:\\documents\\abc_scale.jpg"
  }
}
```

**使用文本：**
```json
{
  "scale_type": "CARS",
  "scale_data": {
    "text": "CARS量表评估结果\n总分：32分"
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "scale_type": "ABC",
    "total_score": 8,
    "dimension_scores": {...},
    "severity_level": "轻度",
    "interpretation": "解读文本...",
    "recommendations": [...]
  },
  "message": "量表解析完成"
}
```

**支持量表**：ABC, CARS, PEP-3, ADOS, WISC

---

## curl 测试示例

```bash
# 解析医院报告
curl -X POST http://localhost:7860/api/infrastructure/document_parser/parse_report \
  -H "Content-Type: application/json" \
  -d '{"file_path": "E:\\documents\\report.jpg", "file_type": "image"}'

# 解析量表（图片）
curl -X POST http://localhost:7860/api/infrastructure/document_parser/parse_scale \
  -H "Content-Type: application/json" \
  -d '{"scale_type": "ABC", "scale_data": {"image_path": "E:\\documents\\abc.jpg"}}'

# 解析量表（文本）
curl -X POST http://localhost:7860/api/infrastructure/document_parser/parse_scale \
  -H "Content-Type: application/json" \
  -d '{"scale_type": "CARS", "scale_data": {"text": "总分：32分"}}'
```

---

# 文件上传 API 测试

## API 端点列表

### 上传文件
**POST** `/api/infrastructure/file_upload/upload`
**Content-Type:** `multipart/form-data`

**参数：**
- `file`: 文件对象（必需）
- `category`: 文件分类（可选: image/document/audio/video，不传则自动检测）

**响应：**
```json
{
  "success": true,
  "data": {
    "file_path": "E:\\pro\\hhc\\uploads\\images\\20260128_143025_abc123.jpg",
    "filename": "20260128_143025_abc123.jpg",
    "original_filename": "report.jpg",
    "file_size": 1024000,
    "category": "image"
  },
  "message": "文件上传成功"
}
```

**支持格式**：
- 图片: JPG, JPEG, PNG, BMP, WEBP
- 文档: PDF, DOCX, DOC
- 音频: MP3, WAV, PCM, M4A, AAC, FLAC, OGG
- 视频: MP4, AVI, MOV, MKV

---

## curl 测试示例

```bash
# 上传文件（自动检测分类）
curl -X POST http://localhost:7860/api/infrastructure/file_upload/upload \
  -F "file=@E:/documents/report.jpg"

# 上传文件（指定分类）
curl -X POST http://localhost:7860/api/infrastructure/file_upload/upload \
  -F "file=@E:/documents/report.jpg" \
  -F "category=image"
```

---

## 使用流程示例

```javascript
// 1. 上传文件
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const uploadResponse = await fetch('http://localhost:7860/api/infrastructure/file_upload/upload', {
  method: 'POST',
  body: formData
});

const uploadResult = await uploadResponse.json();
const filePath = uploadResult.data.file_path;

// 2. 使用文件路径调用其他服务（如文档解析）
const parseResponse = await fetch('http://localhost:7860/api/infrastructure/document_parser/parse_report', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    file_path: filePath,  // 格式: E:\\pro\\hhc\\uploads\\images\\20260128_143025_abc123.jpg
    file_type: 'image'
  })
});
```

---

# Graphiti API 测试（重构版本 v2.0）

## 概述

Graphiti 模块已完全重构，采用自定义图结构存储观察数据，提供多维度趋势分析、平台期检测、异常检测和跨维度关联分析功能。

## API 端点列表

### 1. 保存观察数据（新标准接口）
**POST** `/api/infrastructure/graphiti/save_observations`

```json
{
  "child_id": "child-001",
  "timestamp": "2026-01-29T14:30:00Z",
  "source": "observation_agent",
  "session_id": "session-20260129-001",
  "observations": [
    {
      "dimension": "eye_contact",
      "value": 8,
      "value_type": "score",
      "context": "积木游戏中主动看向家长",
      "confidence": 0.85
    },
    {
      "dimension": "spontaneous_smile",
      "value": 3,
      "value_type": "count",
      "context": "游戏过程中的微笑次数",
      "confidence": 0.90
    }
  ],
  "milestone": {
    "detected": true,
    "type": "first_time",
    "description": "首次主动发起眼神接触",
    "dimension": "eye_contact"
  }
}
```

**支持的维度**：
- **六大情绪里程碑**：self_regulation, intimacy, two_way_communication, complex_communication, emotional_ideas, logical_thinking
- **行为观察维度**：eye_contact, spontaneous_smile, verbal_attempt, repetitive_behavior, sensory_response, social_initiation

**响应：**
```json
{
  "success": true,
  "message": "成功保存 2 条观察记录"
}
```

---

### 2. 获取完整趋势分析
**POST** `/api/infrastructure/graphiti/get_full_trend`

```json
{
  "child_id": "child-001"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "child_id": "child-001",
    "child_name": "辰辰",
    "analysis_time": "2026-01-29T15:00:00Z",
    "dimensions": {
      "eye_contact": {
        "dimension": "eye_contact",
        "display_name": "眼神接触",
        "category": "behavior",
        "current_value": 7.5,
        "baseline_value": 2.0,
        "total_improvement": 2.75,
        "trend_7d": {
          "direction": "improving",
          "rate": 0.15,
          "confidence": 0.82,
          "p_value": 0.03
        },
        "trend_30d": {...},
        "trend_90d": {...},
        "plateau": {
          "is_plateau": false,
          "duration_days": 0,
          "suggestion": "继续当前计划"
        },
        "anomaly": {
          "has_anomaly": false,
          "anomaly_type": "none",
          "anomaly_value": 0,
          "anomaly_date": "",
          "interpretation": "无异常"
        },
        "data_point_count": 45
      }
    },
    "recent_milestones": [...],
    "total_milestones": 8,
    "correlations": [...],
    "summary": {
      "attention_dimensions": ["repetitive_behavior"],
      "improving_dimensions": ["eye_contact", "spontaneous_smile"],
      "stable_dimensions": ["self_regulation"],
      "overall_status": "good",
      "recommendation": "眼神接触和双向沟通进展良好..."
    }
  }
}
```

---

### 3. 获取单维度趋势
**POST** `/api/infrastructure/graphiti/get_dimension_trend`

```json
{
  "child_id": "child-001",
  "dimension": "eye_contact",
  "include_data_points": true
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "dimension": "eye_contact",
    "display_name": "眼神接触",
    "current_value": 7.5,
    "baseline_value": 2.0,
    "total_improvement": 2.75,
    "trend_7d": {...},
    "trend_30d": {...},
    "trend_90d": {...},
    "plateau": {...},
    "anomaly": {...},
    "data_points": [
      {
        "timestamp": "2026-01-22T10:00:00Z",
        "value": 6.0,
        "source": "observation_agent",
        "confidence": 0.85,
        "context": "积木游戏"
      }
    ],
    "data_point_count": 45
  }
}
```

---

### 4. 获取快速摘要
**POST** `/api/infrastructure/graphiti/get_quick_summary`

```json
{
  "child_id": "child-001"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "attention_dimensions": ["repetitive_behavior"],
    "improving_dimensions": ["eye_contact", "spontaneous_smile"],
    "stable_dimensions": ["self_regulation"],
    "overall_status": "good",
    "recommendation": "眼神接触和双向沟通进展良好，建议继续当前游戏类型"
  }
}
```

---

### 5. 获取里程碑
**POST** `/api/infrastructure/graphiti/get_milestones`

```json
{
  "child_id": "child-001",
  "days": 30,
  "dimension": "eye_contact"
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "milestone_id": "mile-20260129-001",
      "dimension": "eye_contact",
      "type": "first_time",
      "description": "首次主动发起眼神接触",
      "timestamp": "2026-01-29T14:30:00Z",
      "significance": "high"
    }
  ]
}
```

---

### 6. 获取维度关联
**POST** `/api/infrastructure/graphiti/get_correlations`

```json
{
  "child_id": "child-001",
  "min_correlation": 0.3
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "dimension_a": "eye_contact",
      "dimension_b": "two_way_communication",
      "correlation": 0.72,
      "lag_days": 5,
      "relationship": "eye_contact 可能促进 two_way_communication（正相关，领先 5 天）",
      "confidence": 0.95,
      "p_value": 0.001
    }
  ]
}
```

---

### 7. 刷新关联分析
**POST** `/api/infrastructure/graphiti/refresh_correlations`

```json
{
  "child_id": "child-001"
}
```

**响应：**
```json
{
  "success": true,
  "message": "关联分析已刷新"
}
```

---

### 8. 清空孩子数据
**POST** `/api/infrastructure/graphiti/clear_child_data`

```json
{
  "child_id": "child-001"
}
```

**响应：**
```json
{
  "success": true,
  "message": "已清空孩子 child-001 的所有数据"
}
```

---

## curl 测试示例

```bash
# 保存观察数据
curl -X POST http://localhost:7860/api/infrastructure/graphiti/save_observations \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "child-001",
    "timestamp": "2026-01-29T14:30:00Z",
    "source": "observation_agent",
    "observations": [
      {
        "dimension": "eye_contact",
        "value": 8,
        "value_type": "score",
        "context": "积木游戏中主动看向家长",
        "confidence": 0.85
      }
    ]
  }'

# 获取完整趋势
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get_full_trend \
  -H "Content-Type: application/json" \
  -d '{"child_id": "child-001"}'

# 获取单维度趋势
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get_dimension_trend \
  -H "Content-Type: application/json" \
  -d '{"child_id": "child-001", "dimension": "eye_contact", "include_data_points": false}'

# 获取快速摘要
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get_quick_summary \
  -H "Content-Type: application/json" \
  -d '{"child_id": "child-001"}'

# 获取里程碑
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get_milestones \
  -H "Content-Type: application/json" \
  -d '{"child_id": "child-001", "days": 30}'

# 获取关联
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get_correlations \
  -H "Content-Type: application/json" \
  -d '{"child_id": "child-001", "min_correlation": 0.3}'

# 刷新关联分析
curl -X POST http://localhost:7860/api/infrastructure/graphiti/refresh_correlations \
  -H "Content-Type: application/json" \
  -d '{"child_id": "child-001"}'
```

---

## 数据格式说明

### 观察值类型（value_type）
- `score`: 评分（0-10）
- `count`: 计数（次数）
- `duration`: 持续时间（秒）
- `boolean`: 布尔值（0或1）

### 趋势方向（direction）
- `improving`: 上升趋势
- `stable`: 稳定
- `declining`: 下降趋势

### 里程碑类型（type）
- `first_time`: 首次出现
- `breakthrough`: 突破性进步
- `significant_improvement`: 显著改善
- `consistency`: 稳定表现

### 整体状态（overall_status）
- `excellent`: 优秀
- `good`: 良好
- `attention_needed`: 需要关注

---

## 常见问题

### Neo4j 连接问题
- 检查容器状态：`docker ps`
- 检查端口：7688（bolt）、7475（web UI）
- 验证 `.env` 配置：`NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

### 数据不足问题
- 趋势分析需要最少数据点：7天≥3个，30天≥7个，90天≥15个
- 关联分析需要最少10个数据点
- 平台期检测需要最少14天数据

### 性能优化
- 首次使用时会自动创建索引
- 定期调用 `refresh_correlations` 更新关联关系
- 大量数据时建议分批保存
