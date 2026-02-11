#!/usr/bin/env python3
"""
スリープエージェント #42
- 睡眠記録
- 就寝時刻・起床時刻・睡眠時間・睡眠品質・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "sleep.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 睡眠テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sleeps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        bed_time TIME,
        wake_time TIME,
        duration_hours REAL,
        quality INTEGER CHECK(quality >= 1 AND quality <= 5),
        mood TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sleeps_date ON sleeps(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sleeps_quality ON sleeps(quality)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_sleep(date, bed_time=None, wake_time=None, duration_hours=None, quality=None, mood=None, notes=None):
    """睡眠を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO sleeps (date, bed_time, wake_time, duration_hours, quality, mood, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, bed_time, wake_time, duration_hours, quality, mood, notes))

    sleep_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return sleep_id

def update_sleep(sleep_id, date=None, bed_time=None, wake_time=None, duration_hours=None,
                 quality=None, mood=None, notes=None):
    """睡眠を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if bed_time:
        updates.append("bed_time = ?")
        params.append(bed_time)
    if wake_time:
        updates.append("wake_time = ?")
        params.append(wake_time)
    if duration_hours is not None:
        updates.append("duration_hours = ?")
        params.append(duration_hours)
    if quality:
        updates.append("quality = ?")
        params.append(quality)
    if mood:
        updates.append("mood = ?")
        params.append(mood)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE sleeps SET {', '.join(updates)} WHERE id = ?"
        params.append(sleep_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_sleep(sleep_id):
    """睡眠を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM sleeps WHERE id = ?', (sleep_id,))

    conn.commit()
    conn.close()

def list_sleeps(date_from=None, date_to=None, quality=None, limit=20):
    """睡眠一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, bed_time, wake_time, duration_hours, quality, mood, notes, created_at
    FROM sleeps
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if quality:
        conditions.append("quality >= ?")
        params.append(quality)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    sleeps = cursor.fetchall()
    conn.close()
    return sleeps

def get_by_date(date):
    """日付で睡眠取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, bed_time, wake_time, duration_hours, quality, mood, notes, created_at
    FROM sleeps
    WHERE date = ?
    ''', (date,))

    sleep = cursor.fetchone()
    conn.close()
    return sleep

def search_sleeps(keyword):
    """睡眠を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, bed_time, wake_time, duration_hours, quality, mood, notes, created_at
    FROM sleeps
    WHERE notes LIKE ? OR mood LIKE ?
    ORDER BY date DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    sleeps = cursor.fetchall()
    conn.close()
    return sleeps

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全記録数
    cursor.execute('SELECT COUNT(*) FROM sleeps')
    stats['total'] = cursor.fetchone()[0]

    # 昨日
    from datetime import timedelta
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    cursor.execute('SELECT duration_hours FROM sleeps WHERE date = ?', (yesterday,))
    result = cursor.fetchone()
    stats['yesterday'] = result[0] if result else None

    # 平均睡眠時間
    cursor.execute('SELECT AVG(duration_hours) FROM sleeps WHERE duration_hours IS NOT NULL')
    avg_duration = cursor.fetchone()[0]
    stats['avg_duration'] = round(avg_duration, 1) if avg_duration else None

    # 平均睡眠品質
    cursor.execute('SELECT AVG(quality) FROM sleeps WHERE quality IS NOT NULL')
    avg_quality = cursor.fetchone()[0]
    stats['avg_quality'] = round(avg_quality, 1) if avg_quality else None

    # 今週
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT COUNT(*), AVG(duration_hours), AVG(quality)
    FROM sleeps
    WHERE date >= ?
    ''', (week_ago,))
    result = cursor.fetchone()
    stats['week_count'] = result[0] if result[0] else 0
    stats['week_avg_duration'] = round(result[1], 1) if result[1] else None
    stats['week_avg_quality'] = round(result[2], 1) if result[2] else None

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
