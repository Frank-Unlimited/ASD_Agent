"""
迁移脚本：创建游戏实时行为记录相关表

创建以下表：
- behavior_records: 行为事件记录
- snapshot_records: 定时快照记录
- game_sessions_extended: 游戏会话扩展信息
- ai_inference_records: AI推断记录
- ai_probe_questions: AI探测问题

幂等执行：所有建表语句均使用 CREATE TABLE IF NOT EXISTS。
"""
import sqlite3
import os
from pathlib import Path


def get_db_path() -> str:
    """从环境变量获取数据库路径，默认 ./data/asd_intervention.db"""
    return os.environ.get("SQLITE_DB_PATH", "./data/asd_intervention.db")


def run_migration(db_path: str = None):
    """
    执行迁移：创建行为记录相关表和索引。

    Args:
        db_path: 数据库文件路径，为 None 时从环境变量读取
    """
    if db_path is None:
        db_path = get_db_path()

    # 确保数据库目录存在
    db_dir = Path(db_path).parent
    db_dir.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # ========== 1. 行为事件记录表 ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_records (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                event_type TEXT NOT NULL,
                detail TEXT,
                valence INTEGER NOT NULL DEFAULT 0,
                source TEXT NOT NULL,
                confidence REAL NOT NULL DEFAULT 1.0,
                game_phase TEXT,
                related_interest TEXT,
                is_confirmed INTEGER
            )
        """)

        # 索引：按会话查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_behavior_records_session_id
            ON behavior_records(session_id)
        """)

        # 索引：按时间排序
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_behavior_records_timestamp
            ON behavior_records(timestamp)
        """)

        # 复合索引：按会话+时间
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_behavior_records_session_time
            ON behavior_records(session_id, timestamp)
        """)

        # ========== 2. 定时快照记录表 ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS snapshot_records (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                engagement_level TEXT,
                skipped INTEGER NOT NULL DEFAULT 0,
                scheduler_mode TEXT NOT NULL DEFAULT 'normal'
            )
        """)

        # 索引：按会话查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshot_records_session_id
            ON snapshot_records(session_id)
        """)

        # 索引：按时间排序
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_snapshot_records_timestamp
            ON snapshot_records(timestamp)
        """)

        # ========== 3. 游戏会话扩展信息表 ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_sessions_extended (
                session_id TEXT PRIMARY KEY,
                child_id TEXT NOT NULL,
                game_type TEXT NOT NULL,
                game_name TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                planned_duration_minutes INTEGER NOT NULL DEFAULT 20,
                fixed_buttons TEXT NOT NULL DEFAULT '[]',
                dynamic_buttons TEXT NOT NULL DEFAULT '[]',
                total_events INTEGER NOT NULL DEFAULT 0,
                ai_inferences_count INTEGER NOT NULL DEFAULT 0,
                engagement_score REAL,
                ai_summary TEXT
            )
        """)

        # 索引：按孩子ID查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_sessions_extended_child_id
            ON game_sessions_extended(child_id)
        """)

        # 索引：按开始时间排序
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_game_sessions_extended_start_time
            ON game_sessions_extended(start_time)
        """)

        # ========== 4. AI推断记录表 ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_inference_records (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                inference_text TEXT NOT NULL,
                inference_type TEXT NOT NULL,
                valence INTEGER NOT NULL DEFAULT 0,
                confidence REAL NOT NULL DEFAULT 0.5,
                is_confirmed INTEGER
            )
        """)

        # 索引：按会话查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_inference_records_session_id
            ON ai_inference_records(session_id)
        """)

        # 索引：按时间排序
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_inference_records_timestamp
            ON ai_inference_records(timestamp)
        """)

        # ========== 5. AI探测问题表 ==========
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_probe_questions (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                session_id TEXT NOT NULL,
                question_text TEXT NOT NULL,
                options TEXT NOT NULL DEFAULT '[]',
                selected_option TEXT,
                game_phase TEXT
            )
        """)

        # 索引：按会话查询
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_probe_questions_session_id
            ON ai_probe_questions(session_id)
        """)

        # 索引：按时间排序
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ai_probe_questions_timestamp
            ON ai_probe_questions(timestamp)
        """)

        conn.commit()
        print(f"[迁移成功] 行为记录相关表已创建/确认存在于: {db_path}")
        print("  - behavior_records")
        print("  - snapshot_records")
        print("  - game_sessions_extended")
        print("  - ai_inference_records")
        print("  - ai_probe_questions")

    except Exception as e:
        conn.rollback()
        print(f"[迁移失败] {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
