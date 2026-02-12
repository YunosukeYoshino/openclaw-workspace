#!/usr/bin/env python3
"""
ワークアウトエージェント #47
- 種目・セット・回数・重量
- 日付・時間・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "workout.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ワークアウトテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exercise TEXT NOT NULL,
        sets INTEGER NOT NULL,
        reps INTEGER,
        weight REAL,
        unit TEXT DEFAULT 'kg',
        date DATE NOT NULL,
        time TIME,
        notes TEXT,
        category TEXT,
        rpe INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_exercise ON workouts(exercise)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_category ON workouts(category)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_workout(exercise, sets, reps=None, weight=None, unit='kg',
                date=None, time=None, notes=None, category=None, rpe=None):
    """ワークアウトを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if time is None:
        time = datetime.now().strftime("%H:%M")

    cursor.execute('''
    INSERT INTO workouts (exercise, sets, reps, weight, unit, date, time, notes, category, rpe)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (exercise, sets, reps, weight, unit, date, time, notes, category, rpe))

    workout_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return workout_id

def update_workout(workout_id, exercise=None, sets=None, reps=None, weight=None,
                   unit=None, date=None, time=None, notes=None, category=None, rpe=None):
    """ワークアウトを更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if exercise:
        updates.append("exercise = ?")
        params.append(exercise)
    if sets is not None:
        updates.append("sets = ?")
        params.append(sets)
    if reps is not None:
        updates.append("reps = ?")
        params.append(reps)
    if weight is not None:
        updates.append("weight = ?")
        params.append(weight)
    if unit:
        updates.append("unit = ?")
        params.append(unit)
    if date:
        updates.append("date = ?")
        params.append(date)
    if time:
        updates.append("time = ?")
        params.append(time)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if category:
        updates.append("category = ?")
        params.append(category)
    if rpe is not None:
        updates.append("rpe = ?")
        params.append(rpe)

    if updates:
        query = f"UPDATE workouts SET {', '.join(updates)} WHERE id = ?"
        params.append(workout_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_workout(workout_id):
    """ワークアウトを削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))

    conn.commit()
    conn.close()

def list_workouts(date=None, exercise=None, category=None, limit=20):
    """ワークアウト一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, exercise, sets, reps, weight, unit, date, time, notes, category, rpe, created_at
    FROM workouts
    '''

    params = []
    conditions = []

    if date:
        conditions.append("date = ?")
        params.append(date)
    if exercise:
        conditions.append("exercise = ?")
        params.append(exercise)
    if category:
        conditions.append("category = ?")
        params.append(category)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, time DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_by_date(date):
    """日付でワークアウト取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, exercise, sets, reps, weight, unit, date, time, notes, category, rpe, created_at
    FROM workouts
    WHERE date = ?
    ORDER BY time ASC
    ''', (date,))

    workouts = cursor.fetchall()
    conn.close()
    return workouts

def search_workouts(keyword):
    """ワークアウトを検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, exercise, sets, reps, weight, unit, date, time, notes, category, rpe, created_at
    FROM workouts
    WHERE exercise LIKE ? OR notes LIKE ? OR category LIKE ?
    ORDER BY date DESC, time DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_exercises():
    """種目一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT exercise, category, COUNT(*) as count, AVG(weight) as avg_weight
    FROM workouts
    GROUP BY exercise, category
    ORDER BY count DESC
    ''')

    exercises = cursor.fetchall()
    conn.close()
    return exercises

def get_categories():
    """カテゴリ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT category, COUNT(*) as count
    FROM workouts
    WHERE category IS NOT NULL
    GROUP BY category
    ORDER BY count DESC
    ''')

    categories = cursor.fetchall()
    conn.close()
    return categories

def get_stats(exercise=None, date_from=None, date_to=None):
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    query = 'SELECT COUNT(*), SUM(sets), SUM(reps * sets) FROM workouts'
    params = []
    conditions = []

    if exercise:
        conditions.append("exercise = ?")
        params.append(exercise)
    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    cursor.execute(query, params)
    count, total_sets, total_reps = cursor.fetchone()

    stats['total_workouts'] = count or 0
    stats['total_sets'] = total_sets or 0
    stats['total_reps'] = total_reps or 0

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM workouts WHERE date = ?', (today,))
    stats['today'] = cursor.fetchone()[0]

    # 今月
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM workouts WHERE date LIKE ?', (f'{current_month}%',))
    stats['this_month'] = cursor.fetchone()[0]

    # トレーニング日数
    cursor.execute('SELECT COUNT(DISTINCT date) FROM workouts')
    stats['training_days'] = cursor.fetchone()[0]

    # 最大重量
    cursor.execute('SELECT MAX(weight) FROM workouts WHERE weight IS NOT NULL')
    stats['max_weight'] = cursor.fetchone()[0]

    conn.close()
    return stats

def get_exercise_history(exercise, limit=10):
    """種目の履歴"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, exercise, sets, reps, weight, unit, date, time, notes, category, rpe, created_at
    FROM workouts
    WHERE exercise = ?
    ORDER BY date DESC, time DESC
    LIMIT ?
    ''', (exercise, limit))

    history = cursor.fetchall()
    conn.close()
    return history

if __name__ == '__main__':
    init_db()
