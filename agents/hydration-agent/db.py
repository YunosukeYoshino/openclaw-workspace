#!/usr/bin/env python3
"""
水分摂取エージェント #50
- 水分量・時間・目標
- 日付・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "hydration.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 水分摂取テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hydration (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        unit TEXT DEFAULT 'ml',
        time_taken TIME,
        date DATE NOT NULL,
        notes TEXT,
        drink_type TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 目標テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        goal_amount REAL NOT NULL,
        unit TEXT DEFAULT 'ml',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date)
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hydration_date ON hydration(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_hydration_type ON hydration(drink_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goals_date ON goals(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_hydration(amount, unit='ml', time_taken=None, date=None, notes=None, drink_type=None):
    """水分摂取を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if time_taken is None:
        time_taken = datetime.now().strftime("%H:%M")

    cursor.execute('''
    INSERT INTO hydration (amount, unit, time_taken, date, notes, drink_type)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (amount, unit, time_taken, date, notes, drink_type))

    hydration_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return hydration_id

def update_hydration(hydration_id, amount=None, unit=None, time_taken=None,
                    date=None, notes=None, drink_type=None):
    """水分摂取を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if unit:
        updates.append("unit = ?")
        params.append(unit)
    if time_taken:
        updates.append("time_taken = ?")
        params.append(time_taken)
    if date:
        updates.append("date = ?")
        params.append(date)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if drink_type:
        updates.append("drink_type = ?")
        params.append(drink_type)

    if updates:
        query = f"UPDATE hydration SET {', '.join(updates)} WHERE id = ?"
        params.append(hydration_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_hydration(hydration_id):
    """水分摂取を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM hydration WHERE id = ?', (hydration_id,))

    conn.commit()
    conn.close()

def list_hydration(date=None, drink_type=None, limit=30):
    """水分摂取一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, amount, unit, time_taken, date, notes, drink_type, created_at
    FROM hydration
    '''

    params = []
    conditions = []

    if date:
        conditions.append("date = ?")
        params.append(date)
    if drink_type:
        conditions.append("drink_type = ?")
        params.append(drink_type)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, time_taken ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    hydration = cursor.fetchall()
    conn.close()
    return hydration

def get_by_date(date):
    """日付で水分摂取取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, amount, unit, time_taken, date, notes, drink_type, created_at
    FROM hydration
    WHERE date = ?
    ORDER BY time_taken ASC
    ''', (date,))

    hydration = cursor.fetchall()
    conn.close()
    return hydration

def set_goal(date, goal_amount, unit='ml'):
    """目標を設定"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO goals (date, goal_amount, unit)
    VALUES (?, ?, ?)
    ''', (date, goal_amount, unit))

    conn.commit()
    conn.close()

def get_goal(date):
    """目標を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, goal_amount, unit, created_at
    FROM goals
    WHERE date = ?
    ''', (date,))

    result = cursor.fetchone()
    conn.close()
    return result

def get_daily_summary(date):
    """日次サマリー"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT
        COUNT(*) as drink_count,
        COALESCE(SUM(amount), 0) as total_amount
    FROM hydration
    WHERE date = ?
    ''', (date,))

    result = cursor.fetchone()
    conn.close()
    return result

def get_stats(date_from=None, date_to=None):
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 総摂取回数
    query = 'SELECT COUNT(*) FROM hydration'
    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    stats['total_drinks'] = cursor.fetchone()[0]

    # 総摂取量
    query = 'SELECT COALESCE(SUM(amount), 0) FROM hydration'
    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    stats['total_amount'] = cursor.fetchone()[0]

    # 平均摂取量
    query = 'SELECT AVG(amount) FROM hydration'
    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    stats['avg_amount'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    today_summary = get_daily_summary(today)
    stats['today_drinks'] = today_summary[0]
    stats['today_amount'] = today_summary[1]

    # 記録日数
    cursor.execute('SELECT COUNT(DISTINCT date) FROM hydration')
    stats['logged_days'] = cursor.fetchone()[0]

    # 飲み物タイプ
    cursor.execute('''
    SELECT drink_type, COUNT(*) as count, SUM(amount) as total
    FROM hydration
    WHERE drink_type IS NOT NULL
    GROUP BY drink_type
    ORDER BY total DESC
    ''')
    stats['drink_types'] = cursor.fetchall()

    conn.close()
    return stats

def get_drink_types():
    """飲み物タイプ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT drink_type, COUNT(*) as count
    FROM hydration
    WHERE drink_type IS NOT NULL
    GROUP BY drink_type
    ORDER BY count DESC
    ''')

    drink_types = cursor.fetchall()
    conn.close()
    return drink_types

if __name__ == '__main__':
    init_db()
