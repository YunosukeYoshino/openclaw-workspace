#!/usr/bin/env python3
"""
夢日記エージェント #16
- 夢の記録と分析
- 統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

DB_PATH = Path(__file__).parent / "dreams.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 夢テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS dreams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        type TEXT CHECK(type IN ('clear', 'vague', 'nightmare', 'lucid', 'recurrent')),
        mood TEXT,
        tags TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dreams_type ON dreams(type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dreams_created ON dreams(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dreams_mood ON dreams(mood)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_dream(content, dream_type='vague', mood=None, tags=None, note=None):
    """夢追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # タグをカンマ区切りで保存
    tags_str = ','.join(tags) if tags else None

    cursor.execute('''
    INSERT INTO dreams (content, type, mood, tags, note)
    VALUES (?, ?, ?, ?, ?)
    ''', (content, dream_type, mood, tags_str, note))

    dream_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return dream_id

def list_dreams(limit=20):
    """夢一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, content, type, mood, tags, note, created_at
    FROM dreams
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    dreams = cursor.fetchall()
    conn.close()
    return dreams

def get_dream_stats(days=7):
    """夢統計"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d %H:%M")

    # 合計数
    cursor.execute('''
    SELECT COUNT(*) FROM dreams
    WHERE created_at >= ?
    ''', (cutoff_date,))
    total = cursor.fetchone()[0]

    # 種類別
    cursor.execute('''
    SELECT type, COUNT(*) as count
    FROM dreams
    WHERE created_at >= ?
    GROUP BY type
    ORDER BY count DESC
    ''', (cutoff_date,))
    by_type = dict(cursor.fetchall())

    # 感情別
    cursor.execute('''
    SELECT mood, COUNT(*) as count
    FROM dreams
    WHERE created_at >= ? AND mood IS NOT NULL
    GROUP BY mood
    ORDER BY count DESC
    ''', (cutoff_date,))
    by_mood = dict(cursor.fetchall())

    conn.close()
    return {
        'total': total,
        'by_type': by_type,
        'by_mood': by_mood
    }

if __name__ == '__main__':
    init_db()
