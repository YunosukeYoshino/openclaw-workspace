#!/usr/bin/env python3
"""
フィットネスエージェント #35
- トレーニング記録
- 種目・回数・重量・セット・日付
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "fitness.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # トレーニングテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        exercise TEXT NOT NULL,
        sets INTEGER,
        reps INTEGER,
        weight INTEGER,
        weight_unit TEXT DEFAULT 'kg',
        duration INTEGER,
        duration_unit TEXT DEFAULT 'minutes',
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_workouts_exercise ON workouts(exercise)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_workout(date, exercise, sets=None, reps=None, weight=None, weight_unit='kg', duration=None, duration_unit='minutes', notes=None):
    """トレーニング追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO workouts (date, exercise, sets, reps, weight, weight_unit, duration, duration_unit, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (date, exercise, sets, reps, weight, weight_unit, duration, duration_unit, notes))

    workout_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return workout_id

def update_workout(workout_id, date=None, exercise=None, sets=None, reps=None, weight=None, weight_unit=None, duration=None, duration_unit=None, notes=None):
    """トレーニング更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
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
    if weight_unit:
        updates.append("weight_unit = ?")
        params.append(weight_unit)
    if duration is not None:
        updates.append("duration = ?")
        params.append(duration)
    if duration_unit:
        updates.append("duration_unit = ?")
        params.append(duration_unit)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE workouts SET {', '.join(updates)} WHERE id = ?"
        params.append(workout_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_workout(workout_id):
    """トレーニング削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))

    conn.commit()
    conn.close()

def list_workouts(date_from=None, date_to=None, exercise=None, limit=20):
    """トレーニング一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, exercise, sets, reps, weight, weight_unit, duration, duration_unit, notes, created_at
    FROM workouts
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if exercise:
        conditions.append("exercise = ?")
        params.append(exercise)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    workouts = cursor.fetchall()
    conn.close()
    return workouts

def search_workouts(keyword):
    """トレーニング検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, exercise, sets, reps, weight, weight_unit, duration, duration_unit, notes, created_at
    FROM workouts
    WHERE exercise LIKE ? OR notes LIKE ?
    ORDER BY date DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_by_date(date):
    """日付でトレーニング取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, exercise, sets, reps, weight, weight_unit, duration, duration_unit, notes, created_at
    FROM workouts
    WHERE date = ?
    ORDER BY created_at ASC
    ''', (date,))

    workouts = cursor.fetchall()
    conn.close()
    return workouts

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全トレーニング数
    cursor.execute('SELECT COUNT(*) FROM workouts')
    stats['total'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('SELECT COUNT(*) FROM workouts WHERE date = ?', (today,))
    stats['today'] = cursor.fetchone()[0]

    # 今月
    current_month = datetime.now().strftime("%Y-%m")
    cursor.execute('SELECT COUNT(*) FROM workouts WHERE date LIKE ?', (f'{current_month}%',))
    stats['this_month'] = cursor.fetchone()[0]

    # 総セット数
    cursor.execute('SELECT SUM(sets) FROM workouts WHERE sets IS NOT NULL')
    total_sets = cursor.fetchone()[0]
    stats['total_sets'] = total_sets if total_sets else 0

    # 総重量
    cursor.execute('SELECT SUM(weight * sets * reps) FROM workouts WHERE weight IS NOT NULL AND sets IS NOT NULL AND reps IS NOT NULL')
    total_volume = cursor.fetchone()[0]
    stats['total_volume'] = total_volume if total_volume else 0

    # 種目数
    cursor.execute('SELECT COUNT(DISTINCT exercise) FROM workouts')
    stats['exercises'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
