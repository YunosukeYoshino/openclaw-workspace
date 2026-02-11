#!/usr/bin/env python3
"""
Weather Agent - 天気情報管理
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "weather.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ユーザーの場所テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        name TEXT,
        city TEXT NOT NULL,
        country TEXT DEFAULT 'JP',
        latitude REAL,
        longitude REAL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 天気履歴テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS weather_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_id INTEGER NOT NULL,
        temperature REAL,
        humidity REAL,
        condition TEXT,
        description TEXT,
        wind_speed REAL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    )
    ''')

    # 通知設定テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notification_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        daily_summary BOOLEAN DEFAULT 0,
        weekly_summary BOOLEAN DEFAULT 0,
        alert_threshold REAL,
        time_hour INTEGER DEFAULT 8,
        FOREIGN KEY (location_id) REFERENCES locations(id)
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_user ON locations(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_location ON weather_history(location_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_weather_recorded ON weather_history(recorded_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notification_user ON notification_settings(user_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_location(user_id, city, name=None, country='JP', lat=None, lon=None):
    """場所を追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO locations (user_id, name, city, country, latitude, longitude)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, city, country, lat, lon))

    location_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return location_id

def get_user_locations(user_id):
    """ユーザーの場所一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, city, country, latitude, longitude
    FROM locations
    WHERE user_id = ?
    ORDER BY created_at DESC
    ''', (user_id,))

    locations = cursor.fetchall()
    conn.close()
    return locations

def delete_location(location_id):
    """場所を削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM locations WHERE id = ?', (location_id,))
    conn.commit()
    conn.close()

def save_weather_data(location_id, temp, humidity, condition, description, wind_speed=None):
    """天気データを保存"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO weather_history (location_id, temperature, humidity, condition, description, wind_speed)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (location_id, temp, humidity, condition, description, wind_speed))

    conn.commit()
    conn.close()

def get_recent_weather(location_id, hours=24):
    """最近の天気データを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT temperature, humidity, condition, description, wind_speed, recorded_at
    FROM weather_history
    WHERE location_id = ?
    AND datetime(recorded_at) >= datetime('now', ? || ' hours')
    ORDER BY recorded_at DESC
    ''', (location_id, str(-hours)))

    weather_data = cursor.fetchall()
    conn.close()
    return weather_data

def set_notification(user_id, location_id, daily=False, weekly=False, alert_threshold=None, time_hour=8):
    """通知設定"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT OR REPLACE INTO notification_settings
    (user_id, location_id, daily_summary, weekly_summary, alert_threshold, time_hour)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, location_id, int(daily), int(weekly), alert_threshold, time_hour))

    conn.commit()
    conn.close()

def get_notification_settings(user_id):
    """通知設定を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT ns.id, l.name, l.city, ns.daily_summary, ns.weekly_summary,
           ns.alert_threshold, ns.time_hour
    FROM notification_settings ns
    JOIN locations l ON ns.location_id = l.id
    WHERE ns.user_id = ?
    ''', (user_id,))

    settings = cursor.fetchall()
    conn.close()
    return settings

def get_daily_summary(location_id):
    """日次サマリーを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp,
        AVG(humidity) as avg_humidity,
        COUNT(*) as readings
    FROM weather_history
    WHERE location_id = ?
    AND date(recorded_at) = date('now')
    ''', (location_id,))

    summary = cursor.fetchone()
    conn.close()
    return summary

def get_weekly_summary(location_id):
    """週次サマリーを取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT
        AVG(temperature) as avg_temp,
        MIN(temperature) as min_temp,
        MAX(temperature) as max_temp,
        AVG(humidity) as avg_humidity,
        COUNT(*) as readings
    FROM weather_history
    WHERE location_id = ?
    AND date(recorded_at) >= date('now', '-7 days')
    ''', (location_id,))

    summary = cursor.fetchone()
    conn.close()
    return summary

if __name__ == '__main__':
    init_db()
