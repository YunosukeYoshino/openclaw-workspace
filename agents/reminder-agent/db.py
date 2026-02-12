#!/usr/bin/env python3
"""
リマインダーエージェント #10
- リマインダー管理
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "reminders.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # リマインダーテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        reminder_time TEXT NOT NULL,
        memo TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'completed', 'dismissed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_time ON reminders(reminder_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reminders_status ON reminders(status)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_reminder(title, reminder_time, memo=None):
    """リマインダー追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO reminders (title, reminder_time, memo)
    VALUES (?, ?, ?)
    ''', (title, reminder_time, memo))

    reminder_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return reminder_id

def list_reminders(limit=20):
    """リマインダー一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, reminder_time, memo, status
    FROM reminders
    WHERE status != 'dismissed'
    ORDER BY reminder_time ASC, created_at DESC
    LIMIT ?
    ''', (limit,))

    reminders = cursor.fetchall()
    conn.close()
    return reminders

def complete_reminder(reminder_id):
    """リマインダー完了"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
    UPDATE reminders SET status = 'completed', completed_at = ?
    WHERE id = ?
    ''', (completed_at, reminder_id))

    conn.commit()
    conn.close()

def dismiss_reminder(reminder_id):
    """リマインダー無視"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE reminders SET status = 'dismissed'
    WHERE id = ?
    ''', (reminder_id,))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
