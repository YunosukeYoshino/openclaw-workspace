#!/usr/bin/env python3
"""
カレンダーエージェント #8
- 予定の管理
- 検索・統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "calendar.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # イベントテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        event_datetime TEXT NOT NULL,
        location TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_datetime ON events(event_datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_created ON events(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_event(title, event_datetime, location=None, description=None):
    """イベント追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO events (title, event_datetime, location, description)
    VALUES (?, ?, ?, ?)
    ''', (title, event_datetime, location, description))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id

def list_events(limit=20):
    """イベント一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, event_datetime, location, description, created_at
    FROM events
    ORDER BY event_datetime ASC, created_at DESC
    LIMIT ?
    ''', (limit,))

    events = cursor.fetchall()
    conn.close()
    return events

def list_upcoming_events(days=7):
    """今後のイベント一覧"""
    import datetime as dt_module
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    future_date = (datetime.now() + dt_module.timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    cursor.execute('''
    SELECT id, title, event_datetime, location, description, created_at
    FROM events
    WHERE event_datetime >= ? AND event_datetime <= ?
    ORDER BY event_datetime ASC
    ''', (cutoff_date, future_date))

    events = cursor.fetchall()
    conn.close()
    return events

def search_events(keyword):
    """イベント検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, event_datetime, location, description, created_at
    FROM events
    WHERE title LIKE ? OR description LIKE ?
    ORDER BY event_datetime ASC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    events = cursor.fetchall()
    conn.close()
    return events

def get_stats():
    """統計情報"""
    import datetime as dt_module
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全イベント数
    cursor.execute('SELECT COUNT(*) FROM events WHERE event_datetime >= ?',
                  (datetime.now().strftime("%Y-%m-%d %H:%M"),))
    stats['upcoming'] = cursor.fetchone()[0]

    # 今週のイベント
    cutoff_date = datetime.now() + dt_module.timedelta(days=7)
    cursor.execute('''SELECT COUNT(*) FROM events
                     WHERE event_datetime >= ? AND event_datetime <= ?''',
                  (datetime.now().strftime("%Y-%m-%d %H:%M"), cutoff_date.strftime("%Y-%m-%d %H:%M")))
    stats['this_week'] = cursor.fetchone()[0]

    # 全体
    cursor.execute('SELECT COUNT(*) FROM events')
    stats['total'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
