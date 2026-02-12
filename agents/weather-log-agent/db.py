#!/usr/bin/env python3
"""
天気ログエージェント #61
- 日次の天気状況を記録
- 日付・天気・気温・湿度・風速・メモ
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "weather.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 天気ログテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        weather TEXT,
        temperature REAL,
        humidity INTEGER,
        wind_speed REAL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_logs_date ON weather_logs(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_logs_weather ON weather_logs(weather)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_log(date, weather=None, temperature=None, humidity=None, wind_speed=None, notes=None):
    """天気ログ追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO weather_logs (date, weather, temperature, humidity, wind_speed, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (date, weather, temperature, humidity, wind_speed, notes))

    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id

def update_log(log_id, date=None, weather=None, temperature=None, humidity=None, wind_speed=None, notes=None):
    """天気ログ更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if date:
        updates.append("date = ?")
        params.append(date)
    if weather:
        updates.append("weather = ?")
        params.append(weather)
    if temperature:
        updates.append("temperature = ?")
        params.append(temperature)
    if humidity is not None:
        updates.append("humidity = ?")
        params.append(humidity)
    if wind_speed:
        updates.append("wind_speed = ?")
        params.append(wind_speed)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE weather_logs SET {', '.join(updates)} WHERE id = ?"
        params.append(log_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def list_logs(date_from=None, date_to=None, weather=None, limit=20):
    """天気ログ一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, date, weather, temperature, humidity, wind_speed, notes, created_at
    FROM weather_logs
    '''

    params = []
    conditions = []

    if date_from:
        conditions.append("date >= ?")
        params.append(date_from)
    if date_to:
        conditions.append("date <= ?")
        params.append(date_to)
    if weather:
        conditions.append("weather = ?")
        params.append(weather)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY date DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    logs = cursor.fetchall()
    conn.close()
    return logs

def get_by_date(date):
    """日付で天気ログ取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, date, weather, temperature, humidity, wind_speed, notes, created_at
    FROM weather_logs
    WHERE date = ?
    ORDER BY created_at ASC
    ''', (date,))

    logs = cursor.fetchall()
    conn.close()
    return logs

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全ログ数
    cursor.execute('SELECT COUNT(*) FROM weather_logs')
    stats['total'] = cursor.fetchone()[0]

    # 天気別集計
    cursor.execute('''
    SELECT weather, COUNT(*) as count
    FROM weather_logs
    GROUP BY weather
    ORDER BY count DESC
    ''')
    stats['by_weather'] = cursor.fetchall()

    # 平均気温
    cursor.execute('''
    SELECT AVG(temperature) as avg_temp
    FROM weather_logs
    WHERE temperature IS NOT NULL
    ''')
    result = cursor.fetchone()
    stats['avg_temperature'] = result[0] if result else None

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
