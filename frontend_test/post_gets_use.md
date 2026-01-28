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

# Graphiti API 测试

## API 端点列表

### 1. 保存记忆
**POST** `/api/infrastructure/graphiti/save_memories`

```json
{
  "child_id": "test-child-001",
  "memories": [
    {
      "timestamp": "2026-01-28T14:30:00",
      "type": "observation",
      "content": "孩子主动眼神接触3次，持续时间约2-3秒"
    }
  ]
}
```

**响应：**
```json
{
  "success": true,
  "message": "成功保存 1 条记忆"
}
```

---

### 2. 获取最近记忆
**POST** `/api/infrastructure/graphiti/get_recent_memories`

```json
{
  "child_id": "test-child-001",
  "days": 7
}
```

---

### 3. 构建上下文
**POST** `/api/infrastructure/graphiti/build_context`

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
    "recentTrends": {...},
    "attentionPoints": [...],
    "activeGoals": [...],
    "recentMilestones": [...]
  },
  "message": "上下文构建完成"
}
```

---

### 4. 分析趋势
**POST** `/api/infrastructure/graphiti/analyze_trends`

```json
{
  "child_id": "test-child-001",
  "dimension": "眼神接触"
}
```

---

### 5. 检测里程碑
**POST** `/api/infrastructure/graphiti/detect_milestones`

```json
{
  "child_id": "test-child-001"
}
```

---

### 6. 检测平台期
**POST** `/api/infrastructure/graphiti/detect_plateau`

```json
{
  "child_id": "test-child-001",
  "dimension": "眼神接触"
}
```

---

### 7. 清空记忆
**POST** `/api/infrastructure/graphiti/clear_memories`

```json
{
  "child_id": "test-child-001"
}
```

---

## curl 测试示例

```bash
# 保存记忆
curl -X POST http://localhost:7860/api/infrastructure/graphiti/save_memories \
  -H "Content-Type: application/json" \
  -d '{"child_id": "test-child-001", "memories": [{"timestamp": "2026-01-28T14:30:00", "type": "observation", "content": "孩子主动眼神接触3次"}]}'

# 获取记忆
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get_recent_memories \
  -H "Content-Type: application/json" \
  -d '{"child_id": "test-child-001", "days": 7}'

# 构建上下文
curl -X POST http://localhost:7860/api/infrastructure/graphiti/build_context \
  -H "Content-Type: application/json" \
  -d '{"child_id": "test-child-001"}'
```

---

## 常见问题

### Neo4j 连接问题
- 检查容器状态：`docker ps`
- 检查端口：7688（bolt）、7475（web UI）
- 验证 `.env` 配置

### 多模态服务配置
视频分析和文档解析需要配置 LLM API 密钥（如 `DASHSCOPE_API_KEY`）
