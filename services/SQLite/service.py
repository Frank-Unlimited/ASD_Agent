"""
SQLite 服务实现
"""
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

try:
    from .database import DatabaseManager
    from .models import ChildProfile, Session, WeeklyPlan, Observation
    from .config import SQLiteConfig
except ImportError:
    from database import DatabaseManager
    from models import ChildProfile, Session, WeeklyPlan, Observation
    from config import SQLiteConfig


class SQLiteService:
    """SQLite 数据管理服务"""
    
    def __init__(self, config: Optional[SQLiteConfig] = None):
        """初始化服务"""
        self.db = DatabaseManager(config)
    
    # ============ 孩子档案管理 ============
    
    def get_child(self, child_id: str) -> Optional[ChildProfile]:
        """获取孩子档案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM children WHERE child_id = ?", (child_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化 JSON 字段
            if data.get('development_dimensions'):
                data['development_dimensions'] = self.db._deserialize_json(data['development_dimensions'])
            else:
                data['development_dimensions'] = []
            
            if data.get('interests'):
                data['interests'] = self.db._deserialize_json(data['interests'])
            else:
                data['interests'] = []
            
            if data.get('archive_files'):
                data['archive_files'] = self.db._deserialize_json(data['archive_files'])
            else:
                data['archive_files'] = []
            
            if data.get('custom_fields'):
                data['custom_fields'] = self.db._deserialize_json(data['custom_fields'])
            else:
                data['custom_fields'] = {}
            
            # 转换为 ChildProfile 对象
            try:
                return ChildProfile(**data)
            except Exception as e:
                print(f"[SQLite] 解析 ChildProfile 失败: {e}")
                print(f"[SQLite] 数据: {data}")
                return None
    
    def save_child(self, profile: ChildProfile) -> None:
        """保存孩子档案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否存在
            cursor.execute("SELECT child_id FROM children WHERE child_id = ?", (profile.child_id,))
            exists = cursor.fetchone() is not None
            
            # 序列化 JSON 字段
            development_dimensions_json = self.db._serialize_json(
                [dim.dict() for dim in profile.development_dimensions]
            )
            interests_json = self.db._serialize_json(
                [interest.dict() for interest in profile.interests]
            )
            archive_files_json = self.db._serialize_json(profile.archive_files)
            custom_fields_json = self.db._serialize_json(profile.custom_fields)
            
            if exists:
                # 更新
                cursor.execute("""
                    UPDATE children SET
                        name = ?,
                        gender = ?,
                        birth_date = ?,
                        diagnosis = ?,
                        diagnosis_level = ?,
                        diagnosis_date = ?,
                        development_dimensions = ?,
                        interests = ?,
                        archive_files = ?,
                        notes = ?,
                        custom_fields = ?,
                        updated_at = ?
                    WHERE child_id = ?
                """, (
                    profile.name,
                    profile.gender.value,
                    profile.birth_date,
                    profile.diagnosis,
                    profile.diagnosis_level.value if profile.diagnosis_level else None,
                    profile.diagnosis_date,
                    development_dimensions_json,
                    interests_json,
                    archive_files_json,
                    profile.notes,
                    custom_fields_json,
                    datetime.now().isoformat(),
                    profile.child_id
                ))
            else:
                # 插入
                cursor.execute("""
                    INSERT INTO children (
                        child_id, name, gender, birth_date,
                        diagnosis, diagnosis_level, diagnosis_date,
                        development_dimensions, interests, archive_files,
                        notes, custom_fields,
                        created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.child_id,
                    profile.name,
                    profile.gender.value,
                    profile.birth_date,
                    profile.diagnosis,
                    profile.diagnosis_level.value if profile.diagnosis_level else None,
                    profile.diagnosis_date,
                    development_dimensions_json,
                    interests_json,
                    archive_files_json,
                    profile.notes,
                    custom_fields_json,
                    profile.created_at.isoformat() if profile.created_at else datetime.now().isoformat(),
                    profile.updated_at.isoformat() if profile.updated_at else datetime.now().isoformat()
                ))
    
    def delete_child(self, child_id: str) -> None:
        """删除孩子档案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            # 删除孩子档案
            cursor.execute("DELETE FROM children WHERE child_id = ?", (child_id,))
            # 删除相关会话
            cursor.execute("DELETE FROM sessions WHERE child_id = ?", (child_id,))
            # 删除相关周计划
            cursor.execute("DELETE FROM weekly_plans WHERE child_id = ?", (child_id,))
            # 删除相关观察记录
            cursor.execute("DELETE FROM observations WHERE child_id = ?", (child_id,))
            conn.commit()
    
    def get_all_children(self) -> List[Dict[str, Any]]:
        """获取所有孩子档案（简化版，只返回基本信息）"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT child_id, name, gender, birth_date, diagnosis, diagnosis_level
                FROM children
                ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                data = self.db._row_to_dict(row)
                results.append(data)
            
            return results
    
    # ============ 会话管理 ============
    
    def create_session(self, child_id: str, game_id: str) -> str:
        """创建干预会话"""
        session_id = f"session-{uuid.uuid4().hex[:12]}"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sessions (
                    session_id, child_id, game_id, status, created_at, updated_at
                ) VALUES (?, ?, ?, 'not_started', ?, ?)
            """, (
                session_id,
                child_id,
                game_id,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取会话信息"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化JSON字段
            data['quick_observations'] = self.db._deserialize_json(data.get('quick_observations'))
            data['voice_observations'] = self.db._deserialize_json(data.get('voice_observations'))
            data['video_analysis'] = self.db._deserialize_json(data.get('video_analysis'))
            data['verified_observations'] = self.db._deserialize_json(data.get('verified_observations'))
            data['preliminary_summary'] = self.db._deserialize_json(data.get('preliminary_summary'))
            data['feedback_form'] = self.db._deserialize_json(data.get('feedback_form'))
            data['parent_feedback'] = self.db._deserialize_json(data.get('parent_feedback'))
            data['final_summary'] = self.db._deserialize_json(data.get('final_summary'))
            data['metadata'] = self.db._deserialize_json(data.get('metadata'))
            
            # 转换布尔值
            data['has_video'] = bool(data.get('has_video'))
            
            return data
    
    def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """更新会话信息"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建更新语句
            update_fields = []
            update_values = []
            
            # 处理每个字段
            for key, value in data.items():
                if key in ['session_id', 'created_at']:
                    continue  # 跳过不可更新的字段
                
                # JSON字段需要序列化
                if key in ['quick_observations', 'voice_observations', 'video_analysis',
                          'verified_observations', 'preliminary_summary', 'feedback_form',
                          'parent_feedback', 'final_summary', 'metadata']:
                    value = self.db._serialize_json(value)
                
                # 布尔值转整数
                if key == 'has_video':
                    value = 1 if value else 0
                
                update_fields.append(f"{key} = ?")
                update_values.append(value)
            
            # 添加更新时间
            update_fields.append("updated_at = ?")
            update_values.append(datetime.now().isoformat())
            
            # 添加 session_id
            update_values.append(session_id)
            
            # 执行更新
            sql = f"UPDATE sessions SET {', '.join(update_fields)} WHERE session_id = ?"
            cursor.execute(sql, update_values)
    
    # ============ 周计划管理 ============
    
    def save_weekly_plan(self, plan: Dict[str, Any]) -> str:
        """保存周计划"""
        plan_id = plan.get('plan_id') or f"plan-{uuid.uuid4().hex[:12]}"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否存在
            cursor.execute("SELECT plan_id FROM weekly_plans WHERE plan_id = ?", (plan_id,))
            exists = cursor.fetchone() is not None
            
            # 序列化JSON字段
            plan_data = plan.copy()
            plan_data['plan_id'] = plan_id
            plan_data['focus_dimensions'] = self.db._serialize_json(plan.get('focus_dimensions'))
            plan_data['daily_plans'] = self.db._serialize_json(plan.get('daily_plans'))
            plan_data['metadata'] = self.db._serialize_json(plan.get('metadata'))
            
            if exists:
                # 更新
                plan_data['updated_at'] = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE weekly_plans SET
                        child_id = ?,
                        week_start = ?,
                        week_end = ?,
                        weekly_goal = ?,
                        focus_dimensions = ?,
                        daily_plans = ?,
                        status = ?,
                        completion_rate = ?,
                        updated_at = ?,
                        metadata = ?
                    WHERE plan_id = ?
                """, (
                    plan_data.get('child_id'),
                    plan_data.get('week_start'),
                    plan_data.get('week_end'),
                    plan_data.get('weekly_goal'),
                    plan_data.get('focus_dimensions'),
                    plan_data.get('daily_plans'),
                    plan_data.get('status', 'active'),
                    plan_data.get('completion_rate'),
                    plan_data.get('updated_at'),
                    plan_data.get('metadata'),
                    plan_id
                ))
            else:
                # 插入
                plan_data['created_at'] = datetime.now().isoformat()
                plan_data['updated_at'] = plan_data['created_at']
                cursor.execute("""
                    INSERT INTO weekly_plans (
                        plan_id, child_id, week_start, week_end,
                        weekly_goal, focus_dimensions, daily_plans,
                        status, completion_rate,
                        created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    plan_id,
                    plan_data.get('child_id'),
                    plan_data.get('week_start'),
                    plan_data.get('week_end'),
                    plan_data.get('weekly_goal'),
                    plan_data.get('focus_dimensions'),
                    plan_data.get('daily_plans'),
                    plan_data.get('status', 'active'),
                    plan_data.get('completion_rate'),
                    plan_data.get('created_at'),
                    plan_data.get('updated_at'),
                    plan_data.get('metadata')
                ))
        
        return plan_id
    
    def get_weekly_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """获取周计划"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM weekly_plans WHERE plan_id = ?", (plan_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化JSON字段
            data['focus_dimensions'] = self.db._deserialize_json(data.get('focus_dimensions'))
            data['daily_plans'] = self.db._deserialize_json(data.get('daily_plans'))
            data['metadata'] = self.db._deserialize_json(data.get('metadata'))
            
            return data
    
    # ============ 观察记录管理 ============
    
    def save_observation(self, observation: Dict[str, Any]) -> str:
        """保存观察记录"""
        observation_id = observation.get('observation_id') or f"obs-{uuid.uuid4().hex[:12]}"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 序列化JSON字段
            obs_data = observation.copy()
            obs_data['observation_id'] = observation_id
            obs_data['structured_data'] = self.db._serialize_json(observation.get('structured_data'))
            obs_data['metadata'] = self.db._serialize_json(observation.get('metadata'))
            obs_data['is_verified'] = 1 if observation.get('is_verified') else 0
            obs_data['created_at'] = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO observations (
                    observation_id, session_id, child_id,
                    observation_type, timestamp, content,
                    structured_data, is_verified, verification_source,
                    created_at, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                observation_id,
                obs_data.get('session_id'),
                obs_data.get('child_id'),
                obs_data.get('observation_type'),
                obs_data.get('timestamp'),
                obs_data.get('content'),
                obs_data.get('structured_data'),
                obs_data.get('is_verified'),
                obs_data.get('verification_source'),
                obs_data.get('created_at'),
                obs_data.get('metadata')
            ))
        
        return observation_id
    
    # ============ 会话历史查询 ============
    
    def get_session_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会话历史"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM sessions
                WHERE child_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (child_id, limit))
            
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                data = self.db._row_to_dict(row)
                
                # 反序列化JSON字段
                data['quick_observations'] = self.db._deserialize_json(data.get('quick_observations'))
                data['voice_observations'] = self.db._deserialize_json(data.get('voice_observations'))
                data['video_analysis'] = self.db._deserialize_json(data.get('video_analysis'))
                data['verified_observations'] = self.db._deserialize_json(data.get('verified_observations'))
                data['preliminary_summary'] = self.db._deserialize_json(data.get('preliminary_summary'))
                data['feedback_form'] = self.db._deserialize_json(data.get('feedback_form'))
                data['parent_feedback'] = self.db._deserialize_json(data.get('parent_feedback'))
                data['final_summary'] = self.db._deserialize_json(data.get('final_summary'))
                data['metadata'] = self.db._deserialize_json(data.get('metadata'))
                data['has_video'] = bool(data.get('has_video'))
                
                result.append(data)
            
            return result

    # ============ 游戏方案管理 ============
    
    def save_game_plan(self, plan_data: Dict[str, Any]) -> str:
        """保存游戏方案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            game_id = plan_data.get('game_id') or f"game-{uuid.uuid4().hex[:12]}"
            
            cursor.execute("""
                INSERT OR REPLACE INTO game_plans (
                    game_id, child_id, title, description, estimated_duration,
                    target_dimension, additional_dimensions, interest_points_used,
                    design_rationale, steps, precautions, goals,
                    materials_needed, environment_setup, status, scheduled_date,
                    created_at, recommended_by, trend_analysis_summary
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                game_id,
                plan_data['child_id'],
                plan_data['title'],
                plan_data['description'],
                plan_data['estimated_duration'],
                plan_data['target_dimension'],
                self.db._serialize_json(plan_data.get('additional_dimensions', [])),
                self.db._serialize_json(plan_data.get('interest_points_used', [])),
                plan_data['design_rationale'],
                self.db._serialize_json(plan_data['steps']),
                self.db._serialize_json(plan_data.get('precautions', [])),
                self.db._serialize_json(plan_data['goals']),
                self.db._serialize_json(plan_data.get('materials_needed', [])),
                plan_data.get('environment_setup'),
                plan_data.get('status', 'recommended'),
                plan_data.get('scheduled_date'),
                plan_data.get('created_at', datetime.now().isoformat()),
                plan_data.get('recommended_by', 'AI'),
                plan_data.get('trend_analysis_summary')
            ))
            
            print(f"[SQLite] 游戏方案已保存: {game_id}")
            return game_id
    
    def get_game_plan(self, game_id: str) -> Optional[Dict[str, Any]]:
        """获取游戏方案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM game_plans WHERE game_id = ?", (game_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化 JSON 字段
            data['additional_dimensions'] = self.db._deserialize_json(data.get('additional_dimensions')) or []
            data['interest_points_used'] = self.db._deserialize_json(data.get('interest_points_used')) or []
            data['steps'] = self.db._deserialize_json(data.get('steps')) or []
            data['precautions'] = self.db._deserialize_json(data.get('precautions')) or []
            data['goals'] = self.db._deserialize_json(data.get('goals')) or {}
            data['materials_needed'] = self.db._deserialize_json(data.get('materials_needed')) or []
            
            return data
    
    def get_game_calendar(self, child_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """获取游戏日历（最近的游戏方案）"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    gp.*,
                    COUNT(gs.session_id) as session_count
                FROM game_plans gp
                LEFT JOIN game_sessions gs ON gp.game_id = gs.game_id
                WHERE gp.child_id = ?
                GROUP BY gp.game_id
                ORDER BY gp.created_at DESC
                LIMIT ?
            """, (child_id, limit))
            
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                data = self.db._row_to_dict(row)
                
                # 反序列化必要字段
                data['additional_dimensions'] = self.db._deserialize_json(data.get('additional_dimensions')) or []
                data['interest_points_used'] = self.db._deserialize_json(data.get('interest_points_used')) or []
                data['steps'] = self.db._deserialize_json(data.get('steps')) or []
                data['goals'] = self.db._deserialize_json(data.get('goals')) or {}
                data['materials_needed'] = self.db._deserialize_json(data.get('materials_needed')) or []
                
                result.append(data)
            
            return result
    
    def update_game_plan_status(self, game_id: str, status: str, scheduled_date: Optional[str] = None) -> None:
        """更新游戏方案状态"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if scheduled_date:
                cursor.execute("""
                    UPDATE game_plans 
                    SET status = ?, scheduled_date = ?
                    WHERE game_id = ?
                """, (status, scheduled_date, game_id))
            else:
                cursor.execute("""
                    UPDATE game_plans 
                    SET status = ?
                    WHERE game_id = ?
                """, (status, game_id))
            
            print(f"[SQLite] 游戏方案状态已更新: {game_id} -> {status}")
    
    # ============ 游戏会话管理 ============
    
    def create_game_session(self, child_id: str, game_id: str) -> str:
        """创建游戏会话"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            session_id = f"session-{uuid.uuid4().hex[:12]}"
            
            cursor.execute("""
                INSERT INTO game_sessions (
                    session_id, game_id, child_id, start_time, status
                ) VALUES (?, ?, ?, ?, ?)
            """, (
                session_id,
                game_id,
                child_id,
                datetime.now().isoformat(),
                'in_progress'
            ))
            
            print(f"[SQLite] 游戏会话已创建: {session_id}")
            return session_id
    
    def get_game_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取游戏会话"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM game_sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化 JSON 字段
            data['parent_observations'] = self.db._deserialize_json(data.get('parent_observations')) or []
            data['video_analysis'] = self.db._deserialize_json(data.get('video_analysis'))
            data['has_video'] = bool(data.get('has_video'))
            
            return data
    
    def update_game_session(self, session_id: str, updates: Dict[str, Any]) -> None:
        """更新游戏会话"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 构建更新语句
            set_clauses = []
            values = []
            
            # 处理各个字段
            if 'end_time' in updates:
                set_clauses.append("end_time = ?")
                values.append(updates['end_time'])
            
            if 'actual_duration' in updates:
                set_clauses.append("actual_duration = ?")
                values.append(updates['actual_duration'])
            
            if 'parent_observations' in updates:
                set_clauses.append("parent_observations = ?")
                values.append(self.db._serialize_json(updates['parent_observations']))
            
            if 'has_video' in updates:
                set_clauses.append("has_video = ?")
                values.append(1 if updates['has_video'] else 0)
            
            if 'video_path' in updates:
                set_clauses.append("video_path = ?")
                values.append(updates['video_path'])
            
            if 'video_analysis' in updates:
                set_clauses.append("video_analysis = ?")
                values.append(self.db._serialize_json(updates['video_analysis']))
            
            if 'status' in updates:
                set_clauses.append("status = ?")
                values.append(updates['status'])
            
            if 'session_summary' in updates:
                set_clauses.append("session_summary = ?")
                values.append(updates['session_summary'])
            
            if 'child_engagement_score' in updates:
                set_clauses.append("child_engagement_score = ?")
                values.append(updates['child_engagement_score'])
            
            if 'goal_achievement_score' in updates:
                set_clauses.append("goal_achievement_score = ?")
                values.append(updates['goal_achievement_score'])
            
            if 'parent_satisfaction_score' in updates:
                set_clauses.append("parent_satisfaction_score = ?")
                values.append(updates['parent_satisfaction_score'])
            
            if 'notes' in updates:
                set_clauses.append("notes = ?")
                values.append(updates['notes'])
            
            # 总是更新 updated_at
            set_clauses.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            
            # 添加 session_id 到 values
            values.append(session_id)
            
            # 执行更新
            sql = f"UPDATE game_sessions SET {', '.join(set_clauses)} WHERE session_id = ?"
            cursor.execute(sql, values)
            
            print(f"[SQLite] 游戏会话已更新: {session_id}")
    
    def get_game_session_history(self, child_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """获取游戏会话历史"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT gs.*, gp.title as game_title
                FROM game_sessions gs
                LEFT JOIN game_plans gp ON gs.game_id = gp.game_id
                WHERE gs.child_id = ?
                ORDER BY gs.start_time DESC
                LIMIT ?
            """, (child_id, limit))
            
            rows = cursor.fetchall()
            result = []
            
            for row in rows:
                data = self.db._row_to_dict(row)
                
                # 反序列化 JSON 字段
                data['parent_observations'] = self.db._deserialize_json(data.get('parent_observations')) or []
                data['video_analysis'] = self.db._deserialize_json(data.get('video_analysis'))
                data['has_video'] = bool(data.get('has_video'))
                
                result.append(data)
            
            return result

    
    # ============ 评估管理 ============
    
    def save_assessment(self, assessment_data: Dict[str, Any]) -> str:
        """
        保存评估报告
        
        Args:
            assessment_data: 评估数据
                - assessment_id: 评估ID
                - child_id: 孩子ID
                - assessment_type: 评估类型（comprehensive/lightweight）
                - timestamp: 时间戳
                - time_range_days: 时间范围（天）
                - report: 评估报告（dict）
                - interest_heatmap: 兴趣热力图（dict，可选）
                - dimension_trends: 功能维度趋势（dict，可选）
                - game_id: 关联游戏ID（可选）
                
        Returns:
            assessment_id
        """
        assessment_id = assessment_data.get('assessment_id')
        if not assessment_id:
            assessment_id = f"assess_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO assessments (
                    assessment_id, child_id, assessment_type, timestamp,
                    time_range_days, report, interest_heatmap, dimension_trends, game_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                assessment_id,
                assessment_data['child_id'],
                assessment_data['assessment_type'],
                assessment_data['timestamp'],
                assessment_data.get('time_range_days'),
                self.db._serialize_json(assessment_data['report']),
                self.db._serialize_json(assessment_data.get('interest_heatmap')),
                self.db._serialize_json(assessment_data.get('dimension_trends')),
                assessment_data.get('game_id')
            ))
            
            print(f"[SQLite] 评估已保存: {assessment_id}")
            return assessment_id
    
    def get_assessment(self, assessment_id: str) -> Optional[Dict[str, Any]]:
        """获取评估报告"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM assessments WHERE assessment_id = ?", (assessment_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化 JSON 字段
            data['report'] = self.db._deserialize_json(data['report'])
            data['interest_heatmap'] = self.db._deserialize_json(data['interest_heatmap'])
            data['dimension_trends'] = self.db._deserialize_json(data['dimension_trends'])
            
            return data
    
    def get_assessment_history(
        self,
        child_id: str,
        assessment_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取评估历史
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            limit: 返回数量限制
            
        Returns:
            评估历史列表
        """
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            if assessment_type:
                cursor.execute("""
                    SELECT * FROM assessments
                    WHERE child_id = ? AND assessment_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (child_id, assessment_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM assessments
                    WHERE child_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (child_id, limit))
            
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                data = self.db._row_to_dict(row)
                
                # 反序列化 JSON 字段
                data['report'] = self.db._deserialize_json(data['report'])
                data['interest_heatmap'] = self.db._deserialize_json(data['interest_heatmap'])
                data['dimension_trends'] = self.db._deserialize_json(data['dimension_trends'])
                
                results.append(data)
            
            return results
    
    def get_latest_assessment(
        self,
        child_id: str,
        assessment_type: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        获取最新评估
        
        Args:
            child_id: 孩子ID
            assessment_type: 评估类型（可选）
            
        Returns:
            最新评估数据
        """
        history = self.get_assessment_history(child_id, assessment_type, limit=1)
        return history[0] if history else None
