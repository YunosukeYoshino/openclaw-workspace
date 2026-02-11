#!/usr/bin/env python3
"""
習慣トラッカーエージェント #11
- 習慣の記録と追跡
- ストリーク機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

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
        frequency TEXT CHECK(frequency IN ('daily', 'weekly', 'monthly')),
        goal_days INTEGER,
        memo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 習慣記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS habit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        completed_at DATE NOT NULL,
        note TEXT,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_habit_logs_habit ON habit_logs(habit_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(completed_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_habit(name, frequency='daily', goal_days=30, memo=None):
    """習慣追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO habits (name, frequency, goal_days, memo)
    VALUES (?, ?, ?, ?)
    ''', (name, frequency, goal_days, memo))

    habit_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return habit_id

def log_habit(habit_id, date=None, note=None):
    """習慣記録"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    # 既存チェック
    cursor.execute('''
    SELECT id FROM habit_logs
    WHERE habit_id = ? AND completed_at = ?
    ''', (habit_id, date))

    if cursor.fetchone():
        conn.close()
        return None

    cursor.execute('''
    INSERT INTO habit_logs (habit_id, completed_at, note)
    VALUES (?, ?, ?)
    ''', (habit_id, date, note))

    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def get_habit_streak(habit_id):
    """習慣のストリークを計算"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 最近の記録を取得
    cursor.execute('''
    SELECT completed_at FROM habit_logs
    WHERE habit_id = ?
    ORDER BY completed_at DESC
    ''', (habit_id,))

    logs = [row[0] for row in cursor.fetchall()]
    conn.close()

    if not logs:
        return 0

    # 今日含めて連続日数を計算
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    streak = 0
    check_date = datetime.now()

    for _ in range(365):  # 最大1年
        check_str = check_date.strftime("%Y-%m-%d")
        if check_str in logs:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    # 昨日も今日も記録がない場合、ストリークは0
    if streak == 0:
        return 0

    return streak

def list_habits():
    """習慣一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, frequency, goal_days, memo, created_at
    FROM habits
    ORDER BY created_at DESC
    ''')

    habits = cursor.fetchall()
    conn.close()

    result = []
    for habit in habits:
        id, name, frequency, goal_days, memo, created_at = habit
        streak = get_habit_streak(id)
        result.append({
            'id': id,
            'name': name,
            'frequency': frequency,
            'goal_days': goal_days,
            'memo': memo,
            'streak': streak
        })

    return result

if __name__ == '__main__':
    init_db()
