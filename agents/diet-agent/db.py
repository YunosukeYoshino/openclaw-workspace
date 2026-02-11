#!/usr/bin/env python3
"""
ダイエットエージェント #48
- 食事・カロリー・栄養素
- 日付・時間・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "diet.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 食事テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meal_type TEXT NOT NULL,
        food TEXT NOT NULL,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        fiber REAL,
        date DATE NOT NULL,
        time TIME,
        notes TEXT,
        amount REAL,
        unit TEXT DEFAULT 'g',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 目標テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS goals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        calories REAL,
        protein REAL,
        carbs REAL,
        fat REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(date)
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meals_date ON meals(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_meals_type ON meals(meal_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_goals_date ON goals(date)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_meal(meal_type, food, calories=None, protein=None, carbs=None, fat=None,
             fiber=None, date=None, time=None, notes=None, amount=None, unit='g'):
    """食事を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    if time is None:
        time = datetime.now().strftime("%H:%M")

    cursor.execute('''
    INSERT INTO meals (meal_type, food, calories, protein, carbs, fat, fiber, date, time, notes, amount, unit)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (meal_type, food, calories, protein, carbs, fat, fiber, date, time, notes, amount, unit))

    meal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meal_id

def update_meal(meal_id, meal_type=None, food=None, calories=None, protein=None, carbs=None,
               fat=None, fiber=None, date=None, time=None, notes=None, amount=None, unit=None):
    """食事を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if meal_type:
        updates.append("meal_type = ?")
        params.append(meal_type)
    if food:
        updates.append("food = ?")
        params.append(food)
    if calories is not None:
        updates.append("calories = ?")
        params.append(calories)
    if protein is not None:
        updates.append("protein = ?")
        params.append(protein)
    if carbs is not None:
        updates.append("carbs = ?")
        params.append(carbs)
    if fat is not None:
        updates.append("fat = ?")
        params.append(fat)
    if fiber is not None:
        updates.append("fiber = ?")
        params.append(fiber)
    if date:
        updates.append("date = ?")
        params.append(date)
    if time:
        updates.append("time = ?")
        params.append(time)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if amount is not None:
        updates.append("amount = ?")
        params.append(amount)
    if unit:
        updates.append("unit = ?")
        params.append(unit)

    if updates:
        query = f"UPDATE meals SET {', '.join(updates)} WHERE id = ?"
        params.append(meal_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_meal(meal_id):
    """食事を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))

    conn.commit()
    conn.close()

def list_meals(date=None, meal_type=None, limit=30):
    """食事一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, meal_type, food, calories, protein, carbs, fat, fiber, date, time, notes, amount, unit, created_at
    FROM meals
    '''

    params = []
    conditions = []

    if date:
        conditions.append("date = ?")
        params.append(date)
    if meal_type:
        conditions.append("meal_type = ?")
        params.append(meal_type)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, time ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    meals = cursor.fetchall()
    conn.close()
    return meals

def get_by_date(date):
    """日付で食事取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, meal_type, food, calories, protein, carbs, fat, fiber, date, time, notes, amount, unit, created_at
    FROM meals
    WHERE date = ?
    ORDER BY time ASC
    ''', (date,))

    meals = cursor.fetchall()
    conn.close()
    return meals

def search_meals(keyword):
    """食事を検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, meal_type, food, calories, protein, carbs, fat, fiber, date, time, notes, amount, unit, created_at
    FROM meals
    WHERE food LIKE ? OR notes LIKE ? OR meal_type LIKE ?
    ORDER BY date DESC, time ASC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    meals = cursor.fetchall()
    conn.close()
    return meals

def set_goal(date, calories=None, protein=None, carbs=None, fat=None):
    """目標を設定"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO goals (date, calories, protein, carbs, fat)
    VALUES (?, ?, ?, ?, ?)
    ''', (date, calories, protein, carbs, fat))

    conn.commit()
    conn.close()

def get_goal(date):
    """目標を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, calories, protein, carbs, fat, created_at
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
        COUNT(*) as meal_count,
        COALESCE(SUM(calories), 0) as total_calories,
        COALESCE(SUM(protein), 0) as total_protein,
        COALESCE(SUM(carbs), 0) as total_carbs,
        COALESCE(SUM(fat), 0) as total_fat,
        COALESCE(SUM(fiber), 0) as total_fiber
    FROM meals
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

    # 総食事数
    query = 'SELECT COUNT(*) FROM meals'
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
    stats['total_meals'] = cursor.fetchone()[0]

    # 平均カロリー
    cursor.execute('SELECT AVG(calories) FROM meals WHERE calories IS NOT NULL')
    stats['avg_calories'] = cursor.fetchone()[0]

    # 今日
    today = datetime.now().strftime("%Y-%m-%d")
    today_summary = get_daily_summary(today)
    stats['today_meals'] = today_summary[0]
    stats['today_calories'] = today_summary[1]

    # トレーニング日数
    cursor.execute('SELECT COUNT(DISTINCT date) FROM meals')
    stats['logged_days'] = cursor.fetchone()[0]

    # よく食べる食品
    cursor.execute('''
    SELECT food, COUNT(*) as count
    FROM meals
    GROUP BY food
    ORDER BY count DESC
    LIMIT 10
    ''')
    stats['frequent_foods'] = cursor.fetchall()

    conn.close()
    return stats

def get_meal_types():
    """食事タイプ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT meal_type, COUNT(*) as count
    FROM meals
    GROUP BY meal_type
    ORDER BY count DESC
    ''')

    meal_types = cursor.fetchall()
    conn.close()
    return meal_types

if __name__ == '__main__':
    init_db()
