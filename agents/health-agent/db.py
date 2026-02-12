#!/usr/bin/env python3
"""
健康管理エージェント #3
- 睡眠・運動・食事・体重記録
- 統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "health.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 睡眠記録
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sleep_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bedtime TEXT NOT NULL,
        wakeup TEXT NOT NULL,
        duration REAL,
        quality INTEGER CHECK(quality IN (1,2,3,4,5)),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 運動記録
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercise_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        duration REAL,
        distance REAL,
        calories REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 食事記録
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meal_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_type TEXT NOT NULL CHECK(meal_type IN ('朝食','昼食','夕食','間食')),
        content TEXT NOT NULL,
        calories REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 体重記録
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weight_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        weight REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sleep_created ON sleep_records(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_exercise_created ON exercise_records(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meal_created ON meal_records(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weight_created ON weight_records(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_sleep(bedtime, wakeup, quality):
    """睡眠記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 睡眠時間計算
    bedtime_dt = datetime.strptime(bedtime, "%Y-%m-%d %H:%M")
    wakeup_dt = datetime.strptime(wakeup, "%Y-%m-%d %H:%M")
    duration = (wakeup_dt - bedtime_dt).total_seconds() / 3600

    cursor.execute('''
    INSERT INTO sleep_records (bedtime, wakeup, duration, quality)
    VALUES (?, ?, ?, ?)
    ''', (bedtime, wakeup, duration, quality))

    memo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memo_id

def add_exercise(exercise_type, duration, distance=None, calories=None, notes=None):
    """運動記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO exercise_records (type, duration, distance, calories, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (exercise_type, duration, distance, calories, notes))

    memo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memo_id

def add_meal(meal_type, content, calories=None, notes=None):
    """食事記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO meal_records (meal_type, content, calories, notes)
    VALUES (?, ?, ?, ?)
    ''', (meal_type, content, calories, notes))

    memo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memo_id

def add_weight(weight):
    """体重記録追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO weight_records (weight)
    VALUES (?)
    ''', (weight,))

    memo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return memo_id

def get_sleep_stats(days=7):
    """睡眠統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    cursor.execute('''
    SELECT AVG(duration) as avg_duration, AVG(quality) as avg_quality, COUNT(*) as count
    FROM sleep_records
    WHERE created_at >= ?
    ''', (cutoff_date,))

    stats = cursor.fetchone()
    conn.close()
    return {
        'avg_duration': round(stats[0], 1) if stats[0] else 0,
        'avg_quality': round(stats[1], 1) if stats[1] else 0,
        'count': stats[2] or 0
    }

def get_exercise_stats(days=7):
    """運動統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    cursor.execute('''
    SELECT SUM(duration) as total_duration, SUM(calories) as total_calories, COUNT(*) as count
    FROM exercise_records
    WHERE created_at >= ?
    ''', (cutoff_date,))

    stats = cursor.fetchone()
    conn.close()
    return {
        'total_duration': round(stats[0], 1) if stats[0] else 0,
        'total_calories': round(stats[1], 1) if stats[1] else 0,
        'count': stats[2] or 0
    }

def get_meal_stats(days=7):
    """食事統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    cursor.execute('''
    SELECT SUM(calories) as total_calories, COUNT(*) as count
    FROM meal_records
    WHERE created_at >= ?
    ''', (cutoff_date,))

    stats = cursor.fetchone()
    conn.close()
    return {
        'total_calories': round(stats[0], 1) if stats[0] else 0,
        'count': stats[1] or 0
    }

def get_recent_records(days=7):
    """最近の記録をまとめて取得"""
    return {
        'sleep': get_sleep_stats(days),
        'exercise': get_exercise_stats(days),
        'meal': get_meal_stats(days)
    }

if __name__ == '__main__':
    init_db()
