#!/usr/bin/env python3
"""
感情記録エージェント #14
- 感情の記録と追跡
- 統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "moods.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 感情テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS moods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL CHECK(type IN ('happy', 'sad', 'angry', 'anxious', 'excited', 'calm', 'tired', 'other')),
        intensity INTEGER CHECK(intensity >= 1 AND intensity <= 5),
        cause TEXT,
        memo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_type ON moods(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_created ON moods(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_moods_intensity ON moods(intensity)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_mood(mood_type, intensity, cause=None, memo=None):
    """感情追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO moods (type, intensity, cause, memo)
    VALUES (?, ?, ?, ?)
    ''', (mood_type, intensity, cause, memo))

    mood_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return mood_id

def list_moods(limit=20):
    """感情一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, type, intensity, cause, memo, created_at
    FROM moods
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    moods = cursor.fetchall()
    conn.close()
    return moods

def get_mood_stats(days=7):
    """感情統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    # 合計数
    cursor.execute('''
    SELECT COUNT(*) FROM moods
    WHERE created_at >= ?
    ''', (cutoff_date,))
    total = cursor.fetchone()[0]

    # 種類別
    cursor.execute('''
    SELECT type, COUNT(*) as count
    FROM moods
    WHERE created_at >= ?
    GROUP BY type
    ORDER BY count DESC
    ''', (cutoff_date,))
    by_type = dict(cursor.fetchall())

    # 平均強度
    cursor.execute('''
    SELECT AVG(intensity) FROM moods
    WHERE created_at >= ?
    ''', (cutoff_date,))
    avg_intensity = cursor.fetchone()[0] or 0

    conn.close()
    return {
        'total': total,
        'by_type': by_type,
        'avg_intensity': round(avg_intensity, 1)
    }

if __name__ == '__main__':
    init_db()
