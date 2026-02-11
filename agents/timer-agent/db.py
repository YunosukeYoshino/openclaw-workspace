#!/usr/bin/env python3
"""
タイマーエージェント #9
- タイマー管理
- Pomodoro機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "timers.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # タイマーテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS timers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        duration INTEGER NOT NULL,
        start_time TEXT,
        end_time TEXT,
        status TEXT DEFAULT 'stopped' CHECK(status IN ('stopped', 'running', 'paused', 'completed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timers_status ON timers(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_timers_created ON timers(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_timer(name, duration_minutes):
    """タイマー追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    duration_seconds = duration_minutes * 60

    cursor.execute('''
    INSERT INTO timers (name, duration)
    VALUES (?, ?)
    ''', (name, duration_seconds))

    timer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return timer_id

def start_timer(timer_id):
    """タイマー開始"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 継続時間取得
    cursor.execute('SELECT duration FROM timers WHERE id = ?', (timer_id,))
    result = cursor.fetchone()

    if result:
        duration_seconds = result[0]
        end_time = (datetime.now() + timedelta(seconds=duration_seconds)).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute('''
        UPDATE timers SET status = 'running', start_time = ?, end_time = ?
        WHERE id = ?
        ''', (start_time, end_time, timer_id))

    conn.commit()
    conn.close()

def stop_timer(timer_id):
    """タイマー停止"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE timers SET status = 'stopped', end_time = NULL
    WHERE id = ?
    ''', (timer_id,))

    conn.commit()
    conn.close()

def complete_timer(timer_id):
    """タイマー完了"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
    UPDATE timers SET status = 'completed', end_time = ?
    WHERE id = ?
    ''', (end_time, timer_id))

    conn.commit()
    conn.close()

def get_timer_status(timer_id):
    """タイマー状況取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, duration, start_time, end_time, status
    FROM timers
    WHERE id = ?
    ''', (timer_id,))

    timer = cursor.fetchone()
    conn.close()

    if not timer:
        return None

    id, name, duration, start_time, end_time, status = timer

    # 残り時間計算
    remaining = duration
    if status == 'running' and end_time:
        end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        remaining = max(0, int((end_dt - datetime.now()).total_seconds()))
    elif status == 'completed':
        remaining = 0

    return {
        'id': id,
        'name': name,
        'duration': duration,
        'start_time': start_time,
        'end_time': end_time,
        'status': status,
        'remaining': remaining
    }

def list_active_timers():
    """アクティブタイマー一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, duration, start_time, end_time, status
    FROM timers
    WHERE status IN ('running', 'paused')
    ORDER BY created_at DESC
    ''')

    timers = cursor.fetchall()
    conn.close()

    result = []
    for timer in timers:
        id, name, duration, start_time, end_time, status = timer

        # 残り時間計算
        remaining = duration
        if status == 'running' and end_time:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            remaining = max(0, int((end_dt - datetime.now()).total_seconds()))

        result.append({
            'id': id,
            'name': name,
            'duration': duration,
            'start_time': start_time,
            'end_time': end_time,
            'status': status,
            'remaining': remaining
        })

    return result

if __name__ == '__main__':
    init_db()
