#!/usr/bin/env python3
"""
気分トラッカーエージェント #64
- 気分のパターン追跡
- トリガーの記録
- 気分変動の分析
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "mood_tracker.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 気分記録テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mood_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mood TEXT NOT NULL CHECK(mood IN ('very_happy', 'happy', 'neutral', 'sad', 'very_sad', 'anxious', 'calm', 'energetic', 'tired', 'other')),
        intensity INTEGER CHECK(intensity >= 1 AND intensity <= 10),
        trigger TEXT,
        location TEXT,
        activity TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # トリガーテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS triggers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        type TEXT CHECK(type IN ('positive', 'negative', 'neutral')),
        frequency INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_mood ON mood_entries(mood)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_created ON mood_entries(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_mood_trigger ON mood_entries(trigger)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_mood_entry(mood, intensity=None, trigger=None, location=None, activity=None, notes=None):
    """気分エントリーを追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO mood_entries (mood, intensity, trigger, location, activity, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (mood, intensity, trigger, location, activity, notes))

    mood_id = cursor.lastrowid
    conn.commit()
    conn.close()

    # トリガーがあれば回数を更新
    if trigger:
        update_trigger_frequency(trigger)

    return mood_id

def update_trigger_frequency(trigger_name):
    """トリガーの頻度を更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 既存のトリガーをチェック
    cursor.execute('SELECT id, frequency FROM triggers WHERE name = ?', (trigger_name,))
    result = cursor.fetchone()

    if result:
        # 既存のトリガーを更新
        cursor.execute('UPDATE triggers SET frequency = frequency + 1 WHERE id = ?', (result[0],))
    else:
        # 新しいトリガーを作成
        cursor.execute('INSERT INTO triggers (name, frequency) VALUES (?, 1)', (trigger_name,))

    conn.commit()
    conn.close()

def list_mood_entries(limit=20):
    """気分エントリー一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, mood, intensity, trigger, location, activity, notes, created_at
    FROM mood_entries
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    entries = cursor.fetchall()
    conn.close()
    return entries

def get_mood_stats(days=7):
    """気分統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    from datetime import timedelta
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    # 合計数
    cursor.execute('''
    SELECT COUNT(*) FROM mood_entries
    WHERE created_at >= ?
    ''', (cutoff_date,))
    total = cursor.fetchone()[0]

    # 気分別カウント
    cursor.execute('''
    SELECT mood, COUNT(*) as count, AVG(intensity) as avg_intensity
    FROM mood_entries
    WHERE created_at >= ?
    GROUP BY mood
    ORDER BY count DESC
    ''', (cutoff_date,))
    by_mood = [{'mood': r[0], 'count': r[1], 'avg_intensity': round(r[2], 1) if r[2] else 0} for r in cursor.fetchall()]

    # 一般的なトリガー
    cursor.execute('''
    SELECT name, frequency FROM triggers
    ORDER BY frequency DESC
    LIMIT 5
    ''')
    top_triggers = cursor.fetchall()

    conn.close()
    return {
        'total': total,
        'by_mood': by_mood,
        'top_triggers': top_triggers
    }

def search_by_trigger(trigger_name, limit=10):
    """トリガーで検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, mood, intensity, trigger, location, activity, notes, created_at
    FROM mood_entries
    WHERE trigger LIKE ?
    ORDER BY created_at DESC
    LIMIT ?
    ''', (f'%{trigger_name}%', limit))

    entries = cursor.fetchall()
    conn.close()
    return entries

if __name__ == '__main__':
    init_db()
