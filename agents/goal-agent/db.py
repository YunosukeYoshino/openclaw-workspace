#!/usr/bin/env python3
"""
目標追跡エージェント #17
- 目標の追跡と管理
- 達成状況確認
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "goals.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 目標テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        deadline DATE,
        priority INTEGER DEFAULT 2 CHECK(priority IN (1,2,3)),
        progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'completed', 'paused', 'cancelled')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    ''')

    # 進捗テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goal_progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        goal_id INTEGER NOT NULL,
        progress INTEGER NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (goal_id) REFERENCES goals(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goals_created ON goals(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_progress_goal ON goal_progress(goal_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goal_progress_created ON goal_progress(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_goal(title, description=None, deadline=None, priority=2):
    """目標追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO goals (title, description, deadline, priority)
    VALUES (?, ?, ?, ?)
    ''', (title, description, deadline, priority))

    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id

def update_goal_progress(goal_id, progress, note=None):
    """目標進捗更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 目標の進捗を更新
    cursor.execute('''
    UPDATE goals SET progress = ? WHERE id = ?
    ''', (progress, goal_id))

    # 進捗履歴に追加
    cursor.execute('''
    INSERT INTO goal_progress (goal_id, progress, note)
    VALUES (?, ?, ?)
    ''', (goal_id, progress, note))

    # 100%になったら完了
    if progress >= 100:
        cursor.execute('''
        UPDATE goals SET status = 'completed', completed_at = ?
        WHERE id = ?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), goal_id))

    conn.commit()
    conn.close()

def complete_goal(goal_id):
    """目標完了"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE goals SET status = 'completed', progress = 100, completed_at = ?
    WHERE id = ?
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), goal_id))

    conn.commit()
    conn.close()

def list_goals():
    """目標一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, description, deadline, priority, progress, status, created_at
    FROM goals
    WHERE status IN ('active', 'paused')
    ORDER BY priority DESC, created_at ASC
    ''')

    goals = cursor.fetchall()
    conn.close()
    return goals

if __name__ == '__main__':
    init_db()
