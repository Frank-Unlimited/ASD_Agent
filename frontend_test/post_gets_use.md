# API 测试指南

## 前置条件

1. 启动 Neo4j 容器（端口 7688）- Graphiti 需要
2. 启动后端服务：`python src/main.py`（端口 7860）
3. 确保 `.env` 中 `USE_REAL_GRAPHITI=true` 和 `USE_REAL_SQLITE=true`

---

# SQLite API 测试

## API 端点列表

### 1. 保存孩子档案
**POST** `/api/infrastructure/sqlite/save-child`

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
**POST** `/api/infrastructure/sqlite/get-child`

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
    "gender": "男",
    "diagnosis": "自闭症谱系障碍",
    "eye_contact": 5.0,
    "joint_attention": 4.5,
    "imitation": 3.8,
    "emotional_response": 4.2,
    "strengths": ["喜欢积木", "专注力好"],
    "challenges": ["眼神接触少", "语言表达困难"],
    "created_at": "2026-01-28T14:30:00",
    "updated_at": "2026-01-28T14:30:00"
  }
}
```

---

### 3. 创建干预会话（后面的session_id都要改成这个模块生成的id）
**POST** `/api/infrastructure/sqlite/create-session`

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
  "message": "会话已创建"
}
```

---

### 4. 更新会话信息
**POST** `/api/infrastructure/sqlite/update-session`

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
      },
      {
        "type": "eye_contact",
        "timestamp": "2026-01-28T14:36:00",
        "description": "主动眼神接触3秒"
      }
    ]
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "更新会话成功"
}
```

---

### 5. 保存观察记录
**POST** `/api/infrastructure/sqlite/save-observation`

```json
{
  "observation": {
    "session_id": "session-abc123",
    "child_id": "test-child-001",
    "observation_type": "quick",
    "timestamp": "2026-01-28T14:35:00",
    "content": "孩子在玩积木时主动看向家长，持续约3秒",
    "tags": ["eye_contact", "joint_attention"]
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "observation_id": "obs-xyz789"
  },
  "message": "保存观察记录成功"
}
```

---

### 6. 保存周计划
**POST** `/api/infrastructure/sqlite/save-weekly-plan`

```json
{
  "plan": {
    "child_id": "test-child-001",
    "week_start": "2026-01-27",
    "week_end": "2026-02-02",
    "weekly_goal": "提升眼神接触频率和持续时间",
    "daily_plans": [
      {
        "day": "Monday",
        "activities": [
          {
            "time": "09:00",
            "activity": "积木游戏",
            "goal": "眼神接触3次以上"
          }
        ]
      }
    ]
  }
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "plan_id": "plan-123"
  },
  "message": "保存周计划成功"
}
```

---

### 7. 获取会话历史
**GET** `/api/infrastructure/sqlite/session-history/{child_id}?limit=10`

**URL 参数：**
- `child_id`: 孩子ID (路径参数)
- `limit`: 返回数量限制 (查询参数，默认10)

**示例URL：**
```
http://localhost:7860/api/infrastructure/sqlite/session-history/test-child-001?limit=10
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "session_id": "session-abc123",
      "game_id": "game-001",
      "game_name": "积木游戏",
      "status": "completed",
      "created_at": "2026-01-28T14:30:00",
      "duration": 1800
    }
  ],
  "message": "获取到 1 条会话历史"
}
```

---

## 使用 curl 测试 SQLite

### 保存孩子档案
```bash
curl -X POST http://localhost:7860/api/infrastructure/sqlite/save-child \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "child_id": "test-child-001",
      "name": "小明",
      "age": 36,
      "gender": "男",
      "diagnosis": "自闭症谱系障碍",
      "eye_contact": 5.0,
      "strengths": ["喜欢积木", "专注力好"]
    }
  }'
```

### 获取孩子档案
```bash
curl -X POST http://localhost:7860/api/infrastructure/sqlite/get-child \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child-001"
  }'
```

### 创建会话
```bash
curl -X POST http://localhost:7860/api/infrastructure/sqlite/create-session \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child-001",
    "game_id": "game-001"
  }'
```

---

# Graphiti API 测试

## API 端点列表

### 1. 保存记忆
**POST** `/api/infrastructure/graphiti/save-memories`

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
**POST** `/api/infrastructure/graphiti/get-recent-memories`

```json
{
  "child_id": "test-child-001",
  "days": 7
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2026-01-28T14:30:00",
      "type": "observation",
      "content": "孩子主动眼神接触3次",
      "source": "uuid-xxx",
      "target": "uuid-yyy",
      "confidence": 0.8
    }
  ],
  "message": "获取到 1 条记忆"
}
```

---

### 3. 构建上下文
**POST** `/api/infrastructure/graphiti/build-context`

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
    "recentTrends": {
      "eye_contact": {
        "dimension": "eye_contact",
        "trend": "improving",
        "rate": 0.5,
        "dataPoints": 15
      }
    },
    "attentionPoints": ["eye_contact 进展良好"],
    "activeGoals": [
      {
        "goal": "提升眼神接触频率",
        "status": "in_progress",
        "progress": 0.6
      }
    ],
    "recentMilestones": [],
    "lastUpdated": "2026-01-28T14:30:00"
  },
  "message": "上下文构建完成"
}
```

---

### 4. 分析趋势
**POST** `/api/infrastructure/graphiti/analyze-trends`

```json
{
  "child_id": "test-child-001",
  "dimension": "眼神接触"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "dimension": "眼神接触",
    "trend": "improving",
    "rate": 0.5,
    "dataPoints": 15,
    "lastUpdated": "2026-01-28T14:30:00"
  },
  "message": "趋势分析完成"
}
```

---

### 5. 检测里程碑
**POST** `/api/infrastructure/graphiti/detect-milestones`

```json
{
  "child_id": "test-child-001"
}
```

**响应：**
```json
{
  "success": true,
  "data": [
    {
      "timestamp": "2026-01-28T14:30:00",
      "type": "breakthrough",
      "description": "首次主动眼神接触超过5秒",
      "dimension": "eye_contact",
      "significance": "high"
    }
  ],
  "message": "检测到 1 个里程碑"
}
```

---

### 6. 检测平台期
**POST** `/api/infrastructure/graphiti/detect-plateau`

```json
{
  "child_id": "test-child-001",
  "dimension": "眼神接触"
}
```

**响应：**
```json
{
  "success": true,
  "data": {
    "dimension": "眼神接触",
    "isPlateau": false,
    "duration": 0,
    "suggestion": "继续当前计划"
  },
  "message": "平台期检测完成"
}
```

---

### 7. 清空记忆
**POST** `/api/infrastructure/graphiti/clear-memories`

```json
{
  "child_id": "test-child-001"
}
```

**响应：**
```json
{
  "success": true,
  "message": "已清空孩子 test-child-001 的所有记忆"
}
```

---

## 使用 curl 测试

### 保存记忆
```bash
curl -X POST http://localhost:7860/api/infrastructure/graphiti/save-memories \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child-001",
    "memories": [
      {
        "timestamp": "2026-01-28T14:30:00",
        "type": "observation",
        "content": "孩子主动眼神接触3次"
      }
    ]
  }'
```

### 获取记忆
```bash
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get-recent-memories \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child-001",
    "days": 7
  }'
```

### 构建上下文
```bash
curl -X POST http://localhost:7860/api/infrastructure/graphiti/build-context \
  -H "Content-Type: application/json" \
  -d '{
    "child_id": "test-child-001"
  }'
```

---

## 使用 Python requests 测试

```python
import requests
import json

BASE_URL = "http://localhost:7860"

# 1. 保存记忆
response = requests.post(
    f"{BASE_URL}/api/infrastructure/graphiti/save-memories",
    json={
        "child_id": "test-child-001",
        "memories": [
            {
                "timestamp": "2026-01-28T14:30:00",
                "type": "observation",
                "content": "孩子主动眼神接触3次"
            }
        ]
    }
)
print("保存记忆:", response.json())

# 2. 获取记忆
response = requests.post(
    f"{BASE_URL}/api/infrastructure/graphiti/get-recent-memories",
    json={
        "child_id": "test-child-001",
        "days": 7
    }
)
print("获取记忆:", response.json())

# 3. 构建上下文
response = requests.post(
    f"{BASE_URL}/api/infrastructure/graphiti/build-context",
    json={
        "child_id": "test-child-001"
    }
)
print("构建上下文:", response.json())
```

---

## 使用 post_get.html 测试

1. 打开 `frontend_test/post_get.html`
2. 选择 **POST** 方法
3. 输入 URL：`/api/infrastructure/graphiti/save-memories`
4. 输入请求体：
```json
{
  "child_id": "test-child-001",
  "memories": [
    {
      "timestamp": "2026-01-28T14:30:00",
      "type": "observation",
      "content": "孩子主动眼神接触3次"
    }
  ]
}
```
5. 点击"发送请求"

---

## 验证数据是否保存

### 方法 1：通过 API 查询
```bash
curl -X POST http://localhost:7860/api/infrastructure/graphiti/get-recent-memories \
  -H "Content-Type: application/json" \
  -d '{"child_id": "test-child-001", "days": 7}'
```

### 方法 2：直接查询 Neo4j
打开 Neo4j Browser（http://localhost:7475）

```cypher
// 查询所有节点数量
MATCH (n) RETURN count(n) as node_count

// 查询所有边数量
MATCH ()-[r]->() RETURN count(r) as edge_count

// 查询最近的边
MATCH ()-[r]->()
RETURN r.fact, r.created_at
ORDER BY r.created_at DESC
LIMIT 10

// 查询特定孩子的数据
MATCH (n)
WHERE n.group_id = 'test-child-001' OR n.source_description CONTAINS 'test-child-001'
RETURN n
LIMIT 20
```

---

## 常见问题

### 1. 保存成功但 Neo4j 中看不到数据
- 检查 `child_id` 是否正确
- 使用正确的 Cypher 查询（见上方）
- 数据可能以边（Edge）的形式存储，不是节点

### 2. 后端日志不显示
- 确保使用最新版本的 `src/main.py`（包含日志中间件）
- 重启后端服务

### 3. 连接 Neo4j 失败
- 检查 Neo4j 容器是否运行：`docker ps`
- 检查端口是否正确：7688（bolt）、7475（web UI）
- 检查 `.env` 中的 Neo4j 配置
