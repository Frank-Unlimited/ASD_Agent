"""
数据库管理模块
"""
import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

try:
    from .config import SQLiteConfig
    from .models import ChildProfile, Session, WeeklyPlan, Observation
except ImportError:
    from config import SQLiteConfig
    from models import ChildProfile, Session, WeeklyPlan, Observation


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, config: Optional[SQLiteConfig] = None):
        """初始化数据库管理器"""
        self.config = config or SQLiteConfig.from_env()
        self.db_path = self.config.db_path
        
        # 初始化数据库
        if self.config.auto_create_tables:
            self.create_tables()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接（上下文管理器）"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 返回字典格式
        
        # 启用 WAL 模式
        if self.config.enable_wal:
            conn.execute("PRAGMA journal_mode=WAL")
        
        # 启用外键约束
        if self.config.enable_foreign_keys:
            conn.execute("PRAGMA foreign_keys=ON")
        
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def create_tables(self):
        """创建所有表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 孩子档案表（对齐 src/models/profile.py）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS children (
                    child_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    birth_date TEXT NOT NULL,
                    
                    -- 诊断信息
                    diagnosis TEXT,
                    diagnosis_level TEXT,
                    diagnosis_date TEXT,
                    
                    -- 发展维度（JSON 数组）
                    development_dimensions TEXT,  -- JSON: List[DevelopmentDimension]
                    
                    -- 兴趣点（JSON 数组）
                    interests TEXT,  -- JSON: List[InterestPoint]
                    
                    -- 档案文件
                    archive_files TEXT,  -- JSON: List[str]
                    
                    -- 额外信息
                    notes TEXT,
                    custom_fields TEXT,  -- JSON
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 干预会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    game_id TEXT NOT NULL,
                    game_name TEXT,
                    status TEXT DEFAULT 'not_started',
                    
                    -- 时间信息
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    duration INTEGER,
                    
                    -- JSON字段
                    quick_observations TEXT,  -- JSON array
                    voice_observations TEXT,  -- JSON array
                    
                    -- 视频相关
                    has_video INTEGER DEFAULT 0,
                    video_path TEXT,
                    video_analysis TEXT,  -- JSON
                    verified_observations TEXT,  -- JSON array
                    
                    -- 总结相关
                    preliminary_summary TEXT,  -- JSON
                    feedback_form TEXT,  -- JSON
                    parent_feedback TEXT,  -- JSON
                    final_summary TEXT,  -- JSON
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,  -- JSON
                    
                    FOREIGN KEY (child_id) REFERENCES children(child_id)
                )
            """)
            
            # 周计划表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS weekly_plans (
                    plan_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    week_start TIMESTAMP NOT NULL,
                    week_end TIMESTAMP NOT NULL,
                    
                    -- 计划目标
                    weekly_goal TEXT,
                    focus_dimensions TEXT,  -- JSON array
                    
                    -- 每日计划
                    daily_plans TEXT NOT NULL,  -- JSON array
                    
                    -- 状态
                    status TEXT DEFAULT 'active',
                    completion_rate REAL,
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,  -- JSON
                    
                    FOREIGN KEY (child_id) REFERENCES children(child_id)
                )
            """)
            
            # 观察记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    
                    -- 观察类型
                    observation_type TEXT NOT NULL,
                    
                    -- 观察内容
                    timestamp TIMESTAMP NOT NULL,
                    content TEXT NOT NULL,
                    structured_data TEXT,  -- JSON
                    
                    -- 验证状态
                    is_verified INTEGER DEFAULT 0,
                    verification_source TEXT,
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,  -- JSON
                    
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
                    FOREIGN KEY (child_id) REFERENCES children(child_id)
                )
            """)
            
            # 游戏方案表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_plans (
                    game_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    
                    -- 基础信息
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    estimated_duration INTEGER NOT NULL,
                    
                    -- 目标和依据
                    target_dimension TEXT NOT NULL,
                    additional_dimensions TEXT,  -- JSON array
                    interest_points_used TEXT,  -- JSON array
                    design_rationale TEXT NOT NULL,
                    
                    -- 游戏内容（JSON）
                    steps TEXT NOT NULL,  -- JSON: List[GameStep]
                    precautions TEXT,  -- JSON: List[GamePrecaution]
                    goals TEXT NOT NULL,  -- JSON: GameGoal
                    
                    -- 材料和环境
                    materials_needed TEXT,  -- JSON array
                    environment_setup TEXT,
                    
                    -- 状态
                    status TEXT DEFAULT 'recommended',
                    scheduled_date TIMESTAMP,
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    recommended_by TEXT DEFAULT 'AI',
                    trend_analysis_summary TEXT,
                    
                    FOREIGN KEY (child_id) REFERENCES children(child_id)
                )
            """)
            
            # 游戏会话表（实施记录）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS game_sessions (
                    session_id TEXT PRIMARY KEY,
                    game_id TEXT NOT NULL,
                    child_id TEXT NOT NULL,
                    
                    -- 时间信息
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    actual_duration INTEGER,
                    
                    -- 观察记录（JSON）
                    parent_observations TEXT,  -- JSON: List[ParentObservation]
                    
                    -- 视频分析
                    has_video INTEGER DEFAULT 0,
                    video_path TEXT,
                    video_analysis TEXT,  -- JSON: VideoAnalysisSummary
                    
                    -- 状态
                    status TEXT DEFAULT 'in_progress',
                    
                    -- 总结和评估
                    session_summary TEXT,
                    child_engagement_score REAL,
                    goal_achievement_score REAL,
                    parent_satisfaction_score REAL,
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    notes TEXT,
                    
                    FOREIGN KEY (game_id) REFERENCES game_plans(game_id),
                    FOREIGN KEY (child_id) REFERENCES children(child_id)
                )
            """)
            
            # 评估报告表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS assessments (
                    assessment_id TEXT PRIMARY KEY,
                    child_id TEXT NOT NULL,
                    
                    -- 评估类型
                    assessment_type TEXT NOT NULL,  -- comprehensive/lightweight
                    
                    -- 时间信息
                    timestamp TIMESTAMP NOT NULL,
                    time_range_days INTEGER,
                    
                    -- 评估报告（JSON）
                    report TEXT NOT NULL,  -- JSON: AssessmentReport
                    interest_heatmap TEXT,  -- JSON: InterestHeatmap
                    dimension_trends TEXT,  -- JSON: DimensionTrends
                    
                    -- 关联游戏（如果是轻量级评估）
                    game_id TEXT,
                    
                    -- 元数据
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    FOREIGN KEY (child_id) REFERENCES children(child_id),
                    FOREIGN KEY (game_id) REFERENCES game_plans(game_id)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_child_id ON sessions(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_weekly_plans_child_id ON weekly_plans(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_weekly_plans_week_start ON weekly_plans(week_start)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_observations_session_id ON observations(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_observations_child_id ON observations(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_plans_child_id ON game_plans(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_plans_status ON game_plans(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_sessions_game_id ON game_sessions(game_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_sessions_child_id ON game_sessions(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_game_sessions_status ON game_sessions(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_child_id ON assessments(child_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_type ON assessments(assessment_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_assessments_timestamp ON assessments(timestamp)")
            
            print(f"[SQLite] 数据库表创建成功: {self.db_path}")
    
    def _serialize_json(self, data: Any) -> Optional[str]:
        """序列化为JSON字符串"""
        if data is None:
            return None
        return json.dumps(data, ensure_ascii=False, default=str)
    
    def _deserialize_json(self, data: Optional[str]) -> Any:
        """反序列化JSON字符串"""
        if data is None:
            return None
        try:
            return json.loads(data)
        except:
            return None
    
    def _row_to_dict(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将数据库行转换为字典"""
        return dict(row)
