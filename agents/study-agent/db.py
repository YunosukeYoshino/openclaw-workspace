#!/usr/bin/env python3
"""
学習記録エージェント #15
- 学習の記録と追跡
- 統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "study.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 学習テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT NOT NULL,
        duration INTEGER NOT NULL,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_study_subject ON study_sessions(subject)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_study_created ON study_sessions(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_study_session(subject, duration, note=None):
    """学習記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO study_sessions (subject, duration, note)
    VALUES (?, ?, ?)
    ''', (subject, duration, note))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def list_study_sessions(limit=20):
    """学習記録一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, subject, duration, note, created_at
    FROM study_sessions
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_study_stats(days=7):
    """学習統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    # 合計時間
    cursor.execute('''
    SELECT SUM(duration) as total, COUNT(*) as count
    FROM study_sessions
    WHERE created_at >= ?
    ''', (cutoff_date,))
    result = cursor.fetchone()
    total_minutes = result[0] or 0
    count = result[1] or 0

    # 科目別
    cursor.execute('''
    SELECT subject, SUM(duration) as total, COUNT(*) as count
    FROM study_sessions
    WHERE created_at >= ?
    GROUP BY subject
    ORDER BY total DESC
    ''', (cutoff_date,))
    by_subject = cursor.fetchall()

    conn.close()

    # 分を時間と分に変換
    hours = total_minutes // 60
    minutes = total_minutes % 60

    return {
        'total_minutes': total_minutes,
        'total_hours': hours,
        'total_minutes_only': minutes,
        'count': count,
        'by_subject': [
            {'subject': s[0], 'total': s[1], 'count': s[2]}
            for s in by_subject
        ]
    }

if __name__ == '__main__':
    init_db()
