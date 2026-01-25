-- ASD Intervention System Database Schema
-- Created for Floor Time therapy sessions and child progress tracking

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Users table - stores therapist and staff information
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'therapist',
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Child profiles table - stores individual child information and progress data
CREATE TABLE IF NOT EXISTS child_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    birth_date TEXT,
    gender TEXT,
    diagnosis TEXT,
    current_emotional_level INTEGER DEFAULT 0,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Emotional milestones table - stores predefined emotional milestone levels
CREATE TABLE IF NOT EXISTS emotional_milestones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level INTEGER NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Custom metrics table - stores user-defined custom metrics
CREATE TABLE IF NOT EXISTS custom_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    icon TEXT,
    color TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Micro observations table - stores detailed micro-observations during sessions
CREATE TABLE IF NOT EXISTS micro_observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    session_id INTEGER,
    timestamp DATETIME NOT NULL,
    behavior TEXT,
    intensity INTEGER,
    duration REAL,
    context TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (session_id) REFERENCES intervention_sessions(id) ON DELETE CASCADE
);

-- Games library table - stores available interactive games
CREATE TABLE IF NOT EXISTS games_library (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    target_level INTEGER,
    icon TEXT,
    difficulty TEXT,
    category TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Intervention sessions table - stores session records
CREATE TABLE IF NOT EXISTS intervention_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    duration REAL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Feedback forms table - stores session feedback
CREATE TABLE IF NOT EXISTS feedback_forms (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    engagement_score INTEGER,
    communication_score INTEGER,
    sensory_score INTEGER,
    overall_score INTEGER,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES intervention_sessions(id) ON DELETE CASCADE
);

-- Child profile snapshots table - stores historical profile data
CREATE TABLE IF NOT EXISTS child_profile_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    child_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    snapshot_date DATETIME NOT NULL,
    emotional_level INTEGER,
    custom_metrics TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (child_id) REFERENCES child_profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for frequently accessed data
CREATE INDEX IF NOT EXISTS idx_child_profiles_user_id ON child_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_micro_observations_child_id ON micro_observations(child_id);
CREATE INDEX IF NOT EXISTS idx_micro_observations_session_id ON micro_observations(session_id);
CREATE INDEX IF NOT EXISTS idx_intervention_sessions_child_id ON intervention_sessions(child_id);
CREATE INDEX IF NOT EXISTS idx_intervention_sessions_user_id ON intervention_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_feedback_forms_session_id ON feedback_forms(session_id);
CREATE INDEX IF NOT EXISTS idx_child_profile_snapshots_child_id ON child_profile_snapshots(child_id);
CREATE INDEX IF NOT EXISTS idx_child_profile_snapshots_user_id ON child_profile_snapshots(user_id);

-- Seed initial emotional milestones data
INSERT OR IGNORE INTO emotional_milestones (level, name, description, icon) VALUES
(1, 'Shared Attention', 'Developing basic joint attention and eye contact', '👀'),
(2, 'Two-Way Communication', 'Engaging in reciprocal interactions with gestures', '🤝'),
(3, 'Complex Communication', 'Using symbols and early language', '💬'),
(4, 'Emotional Ideas', 'Expressing and understanding emotional concepts', '❤️'),
(5, 'Emotional Thinking', 'Developing abstract emotional understanding', '🧠'),
(6, 'Emotional Logic', 'Applying emotional reasoning to situations', '🔍');
