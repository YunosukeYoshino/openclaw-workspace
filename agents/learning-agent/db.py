#!/usr/bin/env python3
"""
学習エージェント #37
- 学習記録管理
- 科目・時間・進捗・目標・タグ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "learning.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 学習セッションテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        subject TEXT NOT NULL,
        topic TEXT,
        duration INTEGER,
        notes TEXT,
        progress INTEGER CHECK(progress >= 0 AND progress <= 100),
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 目標テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        subject TEXT,
        target_hours INTEGER,
        current_hours INTEGER DEFAULT 0,
        deadline DATE,
        status TEXT DEFAULT 'ongoing' CHECK(status IN ('ongoing', 'completed', 'cancelled')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 更新トリガー
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_goals_updated_at
    AFTER UPDATE ON goals
    BEGIN
        UPDATE goals SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_subject ON sessions(subject)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_session(date, subject, topic=None, duration=None, notes=None, progress=None, tags=None):
    """学習セッション追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO sessions (date, subject, topic, duration, notes, progress, tags)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (date, subject, topic, duration, notes, progress, tags))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def update_session(session_id, date=None, subject=None, topic=None, duration=None, notes=None, progress=None, tags=None):
    """学習セッション更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if subject:
        updates.append("subject = ?")
        params.append(subject)
    if topic:
        updates.append("topic = ?")
        params.append(topic)
    if duration is not None:
        updates.append("duration = ?")
        params.append(duration)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if progress is not None:
        updates.append("progress = ?")
        params.append(progress)
    if tags:
        updates.append("tags = ?")
        params.append(tags)

    if updates:
        query = f"UPDATE sessions SET {', '.join(updates)} WHERE id = ?"
        params.append(session_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_session(session_id):
    """学習セッション削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))

    conn.commit()
    conn.close()

def list_sessions(date_from=None, date_to=None, subject=None, limit=20):
    """学習セッション一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, subject, topic, duration, notes, progress, tags, created_at
    FROM sessions
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if subject:
        conditions.append("subject = ?")
        params.append(subject)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    sessions = cursor.fetchall()
    conn.close()
    return sessions

def search_sessions(keyword):
    """学習セッション検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, subject, topic, duration, notes, progress, tags, created_at
    FROM sessions
    WHERE subject LIKE ? OR topic LIKE ? OR notes LIKE ? OR tags LIKE ?
    ORDER BY date DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    sessions = cursor.fetchall()
    conn.close()
    return sessions

def get_by_date(date):
    """日付で学習セッション取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, subject, topic, duration, notes, progress, tags, created_at
    FROM sessions
    WHERE date = ?
    ORDER BY created_at ASC
    ''', (date,))

    sessions = cursor.fetchall()
    conn.close()
    return sessions

# 目標関連
def add_goal(title, subject=None, target_hours=None, deadline=None, notes=None):
    """目標追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO goals (title, subject, target_hours, deadline, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, subject, target_hours, deadline, notes))

    goal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return goal_id

def update_goal(goal_id, title=None, subject=None, target_hours=None, current_hours=None, deadline=None, status=None, notes=None):
    """目標更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if subject:
        updates.append("subject = ?")
        params.append(subject)
    if target_hours is not None:
        updates.append("target_hours = ?")
        params.append(target_hours)
    if current_hours is not None:
        updates.append("current_hours = ?")
        params.append(current_hours)
    if deadline:
        updates.append("deadline = ?")
        params.append(deadline)
    if status:
        updates.append("status = ?")
        params.append(status)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE goals SET {', '.join(updates)} WHERE id = ?"
        params.append(goal_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_goal(goal_id):
    """目標削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM goals WHERE id = ?', (goal_id,))

    conn.commit()
    conn.close()

def list_goals(status=None, limit=20):
    """目標一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, subject, target_hours, current_hours, deadline, status, notes, created_at
    FROM goals
    '''

    params = []

    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    goals = cursor.fetchall()
    conn.close()
    return goals

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全セッション数
    cursor.execute('SELECT COUNT(*) FROM sessions')
    stats['total_sessions'] = cursor.fetchone()[0]

    # 全学習時間
    cursor.execute('SELECT SUM(duration) FROM sessions WHERE duration IS NOT NULL')
    total_hours = cursor.fetchone()[0]
    stats['total_hours'] = total_hours if total_hours else 0

    # 今日の学習時間
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT SUM(duration) FROM sessions WHERE date = ? AND duration IS NOT NULL', (today,))
    today_hours = cursor.fetchone()[0]
    stats['today_hours'] = today_hours if today_hours else 0

    # 今月の学習時間
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT SUM(duration) FROM sessions WHERE date LIKE ? AND duration IS NOT NULL', (f'{current_month}%',))
    month_hours = cursor.fetchone()[0]
    stats['month_hours'] = month_hours if month_hours else 0

    # 科目数
    cursor.execute('SELECT COUNT(DISTINCT subject) FROM sessions')
    stats['subjects'] = cursor.fetchone()[0]

    # 目標数
    cursor.execute('SELECT COUNT(*) FROM goals')
    stats['goals'] = cursor.fetchone()[0]

    # 進行中の目標
    cursor.execute('SELECT COUNT(*) FROM goals WHERE status = "ongoing"')
    stats['ongoing_goals'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
