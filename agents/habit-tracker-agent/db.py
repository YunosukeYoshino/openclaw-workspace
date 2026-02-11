#!/usr/bin/env python3
"""
習慣トラッカーエージェント #51
- 日次習慣の追跡
- 習慣・継続日数(streak)・達成率
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "habits.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 習慣テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        target_days INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 習慣ログテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        date DATE NOT NULL,
        status TEXT DEFAULT 'completed' CHECK(status IN ('completed', 'skipped', 'missed')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_habit_logs_habit_id ON habit_logs(habit_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_habit(name, category=None, target_days=None):
    """習慣追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO habits (name, category, target_days)
    VALUES (?, ?, ?)
    ''', (name, category, target_days))

    habit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return habit_id

def log_habit(habit_id, date, status='completed', notes=None):
    """習慣を記録"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO habit_logs (habit_id, date, status, notes)
    VALUES (?, ?, ?, ?)
    ''', (habit_id, date, status, notes))

    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def get_streak(habit_id):
    """継続日数を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 過去7日間の記録を取得
    cursor.execute('''
    SELECT date, status
    FROM habit_logs
    WHERE habit_id = ?
    ORDER BY date DESC
    LIMIT 7
    ''', (habit_id,))

    logs = cursor.fetchall()
    conn.close()

    streak = 0
    for date, status in logs:
        if status == 'completed':
            streak += 1
        else:
            break

    return streak

def get_completion_rate(habit_id, days=7):
    """達成率を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT COUNT(*) as total,
           SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed
    FROM habit_logs
    WHERE habit_id = ?
    ORDER BY date DESC
    LIMIT ?
    ''', (habit_id, days))

    result = cursor.fetchone()
    conn.close()

    if result and result[0] > 0:
        return (result[1] / result[0]) * 100
    return 0.0

def list_habits():
    """習慣一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, category, target_days, created_at
    FROM habits
    ORDER BY created_at DESC
    ''')

    habits = cursor.fetchall()
    conn.close()
    return habits

def list_logs(habit_id, limit=20):
    """記録一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, habit_id, date, status, notes, created_at
    FROM habit_logs
    WHERE habit_id = ?
    ORDER BY date DESC
    LIMIT ?
    ''', (habit_id, limit))

    logs = cursor.fetchall()
    conn.close()
    return logs

if __name__ == '__main__':
    init_db()
