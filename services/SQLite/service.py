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
    
    def get_child(self, child_id: str) -> Optional[Dict[str, Any]]:
        """获取孩子档案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM children WHERE child_id = ?", (child_id,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            data = self.db._row_to_dict(row)
            
            # 反序列化JSON字段
            data['custom_dimensions'] = self.db._deserialize_json(data.get('custom_dimensions'))
            data['strengths'] = self.db._deserialize_json(data.get('strengths'))
            data['weaknesses'] = self.db._deserialize_json(data.get('weaknesses'))
            data['interests'] = self.db._deserialize_json(data.get('interests'))
            data['observation_framework'] = self.db._deserialize_json(data.get('observation_framework'))
            data['focus_points'] = self.db._deserialize_json(data.get('focus_points'))
            data['metadata'] = self.db._deserialize_json(data.get('metadata'))
            
            return data
    
    def save_child(self, profile: Dict[str, Any]) -> None:
        """保存孩子档案"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否存在
            cursor.execute("SELECT child_id FROM children WHERE child_id = ?", (profile['child_id'],))
            exists = cursor.fetchone() is not None
            
            # 序列化JSON字段
            profile_data = profile.copy()
            profile_data['custom_dimensions'] = self.db._serialize_json(profile.get('custom_dimensions'))
            profile_data['strengths'] = self.db._serialize_json(profile.get('strengths'))
            profile_data['weaknesses'] = self.db._serialize_json(profile.get('weaknesses'))
            profile_data['interests'] = self.db._serialize_json(profile.get('interests'))
            profile_data['observation_framework'] = self.db._serialize_json(profile.get('observation_framework'))
            profile_data['focus_points'] = self.db._serialize_json(profile.get('focus_points'))
            profile_data['metadata'] = self.db._serialize_json(profile.get('metadata'))
            
            if exists:
                # 更新
                profile_data['updated_at'] = datetime.now().isoformat()
                cursor.execute("""
                    UPDATE children SET
                        name = ?,
                        age = ?,
                        gender = ?,
                        diagnosis = ?,
                        eye_contact = ?,
                        two_way_communication = ?,
                        emotional_expression = ?,
                        problem_solving = ?,
                        creative_thinking = ?,
                        logical_thinking = ?,
                        custom_dimensions = ?,
                        strengths = ?,
                        weaknesses = ?,
                        interests = ?,
                        observation_framework = ?,
                        focus_points = ?,
                        updated_at = ?,
                        metadata = ?
                    WHERE child_id = ?
                """, (
                    profile_data.get('name'),
                    profile_data.get('age'),
                    profile_data.get('gender'),
                    profile_data.get('diagnosis'),
                    profile_data.get('eye_contact'),
                    profile_data.get('two_way_communication'),
                    profile_data.get('emotional_expression'),
                    profile_data.get('problem_solving'),
                    profile_data.get('creative_thinking'),
                    profile_data.get('logical_thinking'),
                    profile_data.get('custom_dimensions'),
                    profile_data.get('strengths'),
                    profile_data.get('weaknesses'),
                    profile_data.get('interests'),
                    profile_data.get('observation_framework'),
                    profile_data.get('focus_points'),
                    profile_data.get('updated_at'),
                    profile_data.get('metadata'),
                    profile_data['child_id']
                ))
            else:
                # 插入
                profile_data['created_at'] = datetime.now().isoformat()
                profile_data['updated_at'] = profile_data['created_at']
                cursor.execute("""
                    INSERT INTO children (
                        child_id, name, age, gender, diagnosis,
                        eye_contact, two_way_communication, emotional_expression,
                        problem_solving, creative_thinking, logical_thinking,
                        custom_dimensions, strengths, weaknesses, interests,
                        observation_framework, focus_points,
                        created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_data['child_id'],
                    profile_data.get('name'),
                    profile_data.get('age'),
                    profile_data.get('gender'),
                    profile_data.get('diagnosis'),
                    profile_data.get('eye_contact'),
                    profile_data.get('two_way_communication'),
                    profile_data.get('emotional_expression'),
                    profile_data.get('problem_solving'),
                    profile_data.get('creative_thinking'),
                    profile_data.get('logical_thinking'),
                    profile_data.get('custom_dimensions'),
                    profile_data.get('strengths'),
                    profile_data.get('weaknesses'),
                    profile_data.get('interests'),
                    profile_data.get('observation_framework'),
                    profile_data.get('focus_points'),
                    profile_data.get('created_at'),
                    profile_data.get('updated_at'),
                    profile_data.get('metadata')
                ))
    
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
