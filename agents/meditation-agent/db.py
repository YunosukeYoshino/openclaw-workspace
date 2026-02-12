#!/usr/bin/env python3
"""
メディテーションエージェント #43
- 瞑想記録
- 日時・時間・タイプ・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "meditation.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 瞑想テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meditations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        time TIME,
        duration_minutes INTEGER,
        meditation_type TEXT,
        notes TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meditations_date ON meditations(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meditations_type ON meditations(meditation_type)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_meditation(date, time=None, duration_minutes=None, meditation_type=None, notes=None, rating=None):
    """瞑想を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if time is None:
        time = datetime.now().strftime("%H:%M")

    cursor.execute('''
    INSERT INTO meditations (date, time, duration_minutes, meditation_type, notes, rating)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, time, duration_minutes, meditation_type, notes, rating))

    meditation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meditation_id

def update_meditation(meditation_id, date=None, time=None, duration_minutes=None,
                      meditation_type=None, notes=None, rating=None):
    """瞑想を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if time:
        updates.append("time = ?")
        params.append(time)
    if duration_minutes:
        updates.append("duration_minutes = ?")
        params.append(duration_minutes)
    if meditation_type:
        updates.append("meditation_type = ?")
        params.append(meditation_type)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if rating:
        updates.append("rating = ?")
        params.append(rating)

    if updates:
        query = f"UPDATE meditations SET {', '.join(updates)} WHERE id = ?"
        params.append(meditation_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_meditation(meditation_id):
    """瞑想を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM meditations WHERE id = ?', (meditation_id,))

    conn.commit()
    conn.close()

def list_meditations(date_from=None, date_to=None, meditation_type=None, limit=20):
    """瞑想一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, time, duration_minutes, meditation_type, notes, rating, created_at
    FROM meditations
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if meditation_type:
        conditions.append("meditation_type = ?")
        params.append(meditation_type)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, time DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    meditations = cursor.fetchall()
    conn.close()
    return meditations

def get_by_date(date):
    """日付で瞑想取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, time, duration_minutes, meditation_type, notes, rating, created_at
    FROM meditations
    WHERE date = ?
    ORDER BY time ASC
    ''', (date,))

    meditations = cursor.fetchall()
    conn.close()
    return meditations

def search_meditations(keyword):
    """瞑想を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, time, duration_minutes, meditation_type, notes, rating, created_at
    FROM meditations
    WHERE meditation_type LIKE ? OR notes LIKE ?
    ORDER BY date DESC, time DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    meditations = cursor.fetchall()
    conn.close()
    return meditations

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全記録数
    cursor.execute('SELECT COUNT(*) FROM meditations')
    stats['total'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM meditations WHERE date = ?', (today,))
    stats['today'] = cursor.fetchone()[0]

    # 今月
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM meditations WHERE date LIKE ?', (f'{current_month}%',))
    stats['this_month'] = cursor.fetchone()[0]

    # 総瞑想時間
    cursor.execute('SELECT SUM(duration_minutes) FROM meditations WHERE duration_minutes IS NOT NULL')
    total_minutes = cursor.fetchone()[0]
    stats['total_minutes'] = total_minutes if total_minutes else 0
    stats['total_hours'] = round(total_minutes / 60, 1) if total_minutes else 0

    # 今週
    from datetime import timedelta
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    cursor.execute('''
    SELECT COUNT(*), SUM(duration_minutes)
    FROM meditations
    WHERE date >= ?
    ''', (week_ago,))
    result = cursor.fetchone()
    stats['week_count'] = result[0] if result[0] else 0
    stats['week_minutes'] = result[1] if result[1] else 0

    # 平均評価
    cursor.execute('SELECT AVG(rating) FROM meditations WHERE rating IS NOT NULL')
    avg_rating = cursor.fetchone()[0]
    stats['avg_rating'] = round(avg_rating, 1) if avg_rating else None

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
