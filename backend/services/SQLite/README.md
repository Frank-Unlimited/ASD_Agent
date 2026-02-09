# SQLite 数据管理模块

管理所有结构化数据的存储和查询

## 功能特性

- ✅ 孩子档案管理（CRUD）
- ✅ 干预会话管理（创建、查询、更新）
- ✅ 周计划管理（保存、查询）
- ✅ 观察记录管理（保存）
- ✅ 会话历史查询
- ✅ 自动 JSON 序列化/反序列化
- ✅ 事务支持
- ✅ 外键约束
- ✅ WAL 模式（Write-Ahead Logging）

## 快速开始

### 1. 安装依赖

```bash
# 无需额外依赖，Python 内置 sqlite3
```

### 2. 配置环境变量

在 `.env` 文件中设置：

```bash
# SQLite 数据库路径
SQLITE_DB_PATH=./data/asd_intervention.db

# 可选配置
SQLITE_ENABLE_WAL=true
SQLITE_ENABLE_FK=true
SQLITE_AUTO_CREATE=true
```

### 3. 使用示例

```python
from api_interface import (
    get_child, save_child,
    create_session, get_session, update_session,
    save_weekly_plan, get_weekly_plan,
    save_observation,
    get_session_history
)

# 保存孩子档案
save_child({
    'child_id': 'child-001',
    'name': '小明',
    'age': 36,  # 月
    'gender': '男',
    'eye_contact': 5.0,
    'strengths': ['喜欢积木', '专注力好']
})

# 查询孩子档案
profile = get_child('child-001')
print(profile['name'], profile['age'])

# 创建会话
session_id = create_session('child-001', 'game-001')

# 更新会话
update_session(session_id, {
    'status': 'in_progress',
    'quick_observations': [
        {'type': 'smile', 'timestamp': '...'}
    ]
})

# 查询会话历史
history = get_session_history('child-001', limit=10)
```

## 数据模型

### 孩子档案（ChildProfile）

```python
{
    'child_id': str,           # 孩子ID
    'name': str,               # 姓名
    'age': int,                # 年龄（月）
    'gender': str,             # 性别
    'diagnosis': str,          # 诊断信息
    
    # 6大维度评分（1-10分）
    'eye_contact': float,
    'two_way_communication': float,
    'emotional_expression': float,
    'problem_solving': float,
    'creative_thinking': float,
    'logical_thinking': float,
    
    # 画像信息
    'strengths': List[str],    # 优势
    'weaknesses': List[str],   # 短板
    'interests': List[str],    # 兴趣
    'focus_points': List[str], # 关注点
    
    # 元数据
    'created_at': datetime,
    'updated_at': datetime
}
```

### 干预会话（Session）

```python
{
    'session_id': str,         # 会话ID
    'child_id': str,           # 孩子ID
    'game_id': str,            # 游戏ID
    'game_name': str,          # 游戏名称
    'status': str,             # 状态
    
    # 时间信息
    'start_time': datetime,
    'end_time': datetime,
    'duration': int,           # 秒
    
    # 观察记录
    'quick_observations': List[Dict],
    'voice_observations': List[Dict],
    
    # 视频相关
    'has_video': bool,
    'video_path': str,
    'video_analysis': Dict,
    
    # 总结相关
    'preliminary_summary': Dict,
    'feedback_form': Dict,
    'parent_feedback': Dict,
    'final_summary': Dict,
    
    # 元数据
    'created_at': datetime,
    'updated_at': datetime
}
```

### 周计划（WeeklyPlan）

```python
{
    'plan_id': str,            # 计划ID
    'child_id': str,           # 孩子ID
    'week_start': datetime,    # 周开始日期
    'week_end': datetime,      # 周结束日期
    
    # 计划目标
    'weekly_goal': str,
    'focus_dimensions': List[str],
    
    # 每日计划
    'daily_plans': List[Dict],
    
    # 状态
    'status': str,             # active/completed/cancelled
    'completion_rate': float,
    
    # 元数据
    'created_at': datetime,
    'updated_at': datetime
}
```

### 观察记录（Observation）

```python
{
    'observation_id': str,     # 观察ID
    'session_id': str,         # 会话ID
    'child_id': str,           # 孩子ID
    'observation_type': str,   # quick/voice/video
    
    # 观察内容
    'timestamp': datetime,
    'content': str,
    'structured_data': Dict,
    
    # 验证状态
    'is_verified': bool,
    'verification_source': str,
    
    # 元数据
    'created_at': datetime
}
```

## API 接口

### 孩子档案管理

#### `get_child(child_id: str) -> Optional[Dict]`
获取孩子档案

#### `save_child(profile: Dict) -> None`
保存孩子档案（创建或更新）

### 会话管理

#### `create_session(child_id: str, game_id: str) -> str`
创建干预会话，返回会话ID

#### `get_session(session_id: str) -> Optional[Dict]`
获取会话信息

#### `update_session(session_id: str, data: Dict) -> None`
更新会话信息

### 周计划管理

#### `save_weekly_plan(plan: Dict) -> str`
保存周计划，返回计划ID

#### `get_weekly_plan(plan_id: str) -> Optional[Dict]`
获取周计划

### 观察记录管理

#### `save_observation(observation: Dict) -> str`
保存观察记录，返回观察ID

### 会话历史查询

#### `get_session_history(child_id: str, limit: int = 10) -> List[Dict]`
获取会话历史（按时间倒序）

## 数据库设计

### 表结构

- `children` - 孩子档案表
- `sessions` - 干预会话表
- `weekly_plans` - 周计划表
- `observations` - 观察记录表

### 索引

- `idx_sessions_child_id` - 会话按孩子ID索引
- `idx_sessions_status` - 会话按状态索引
- `idx_weekly_plans_child_id` - 周计划按孩子ID索引
- `idx_weekly_plans_week_start` - 周计划按开始日期索引
- `idx_observations_session_id` - 观察按会话ID索引
- `idx_observations_child_id` - 观察按孩子ID索引

### 外键约束

- `sessions.child_id` → `children.child_id`
- `weekly_plans.child_id` → `children.child_id`
- `observations.session_id` → `sessions.session_id`
- `observations.child_id` → `children.child_id`

## 配置选项

### SQLiteConfig

```python
@dataclass
class SQLiteConfig:
    db_path: str = "./data/asd_intervention.db"  # 数据库路径
    pool_size: int = 5                           # 连接池大小
    max_overflow: int = 10                       # 最大溢出连接数
    pool_timeout: int = 30                       # 连接超时（秒）
    enable_wal: bool = True                      # 启用WAL模式
    enable_foreign_keys: bool = True             # 启用外键约束
    auto_create_tables: bool = True              # 自动创建表
```

## 测试

运行测试：

```bash
cd services/SQLite
python test_simple.py
```

测试内容：
- ✅ 孩子档案的创建、查询、更新
- ✅ 会话的创建、查询、更新
- ✅ 周计划的创建、查询
- ✅ 观察记录的保存
- ✅ 会话历史查询

## 技术特性

### 1. 自动 JSON 序列化

复杂字段（如列表、字典）自动序列化为 JSON 存储：

```python
save_child({
    'child_id': 'child-001',
    'strengths': ['喜欢积木', '专注力好'],  # 自动序列化
    'interests': ['积木', '拼图']           # 自动序列化
})

profile = get_child('child-001')
print(profile['strengths'])  # 自动反序列化为列表
```

### 2. 事务支持

使用上下文管理器自动管理事务：

```python
with db.get_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    # 自动提交或回滚
```

### 3. WAL 模式

启用 Write-Ahead Logging 提升并发性能：
- 读写不阻塞
- 更好的并发性能
- 更快的写入速度

### 4. 外键约束

确保数据完整性：
- 删除孩子时自动删除相关会话
- 删除会话时自动删除相关观察
- 防止无效的外键引用

## 注意事项

1. **数据库路径**：确保数据库目录存在，模块会自动创建
2. **JSON 字段**：复杂数据类型会自动序列化，无需手动处理
3. **时间格式**：使用 ISO 8601 格式字符串存储时间
4. **事务管理**：使用 `get_connection()` 上下文管理器确保事务正确提交
5. **并发访问**：WAL 模式支持多个读取者和一个写入者

## 性能优化

1. **索引优化**：为常用查询字段创建索引
2. **批量操作**：使用事务批量插入数据
3. **连接池**：复用数据库连接
4. **WAL 模式**：提升并发性能

## 故障排查

### 问题1: 数据库文件不存在

```
FileNotFoundError: [Errno 2] No such file or directory
```

**解决**：模块会自动创建目录和数据库文件，确保有写入权限

### 问题2: JSON 序列化错误

```
TypeError: Object of type datetime is not JSON serializable
```

**解决**：使用 ISO 格式字符串存储时间：`datetime.now().isoformat()`

### 问题3: 外键约束错误

```
FOREIGN KEY constraint failed
```

**解决**：确保引用的父记录存在（如先创建孩子档案，再创建会话）

## 文件结构

```
services/SQLite/
├── __init__.py           # 模块入口
├── config.py             # 配置管理
├── models.py             # 数据模型
├── database.py           # 数据库管理
├── service.py            # 服务实现
├── api_interface.py      # API接口
├── test_simple.py        # 功能测试
└── README.md             # 本文档
```

## 版本

v1.0.0

## 许可

MIT License
