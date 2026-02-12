#!/usr/bin/env python3
"""
ブレインストーミングエージェント #18
- アイデア出し支援
- アイデア記録・評価
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "brainstorm.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # セッションテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # アイデアテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ideas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        idea TEXT NOT NULL,
        rating INTEGER DEFAULT 0 CHECK(rating >= 0 AND rating <= 5),
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_session ON ideas(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_rating ON ideas(rating)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ideas_created ON ideas(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def create_session(topic):
    """セッション作成"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO sessions (topic)
    VALUES (?)
    ''', (topic,))

    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return session_id

def add_idea(session_id, idea, tags=None):
    """アイデア追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # タグをカンマ区切りで保存
    tags_str = ','.join(tags) if tags else None

    cursor.execute('''
    INSERT INTO ideas (session_id, idea, tags)
    VALUES (?, ?, ?)
    ''', (session_id, idea, tags_str))

    idea_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return idea_id

def rate_idea(idea_id, rating):
    """アイデア評価"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE ideas SET rating = ? WHERE id = ?
    ''', (rating, idea_id))

    conn.commit()
    conn.close()

def get_session_ideas(session_id):
    """セッションのアイデア取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, idea, rating, tags, created_at
    FROM ideas
    WHERE session_id = ?
    ORDER BY rating DESC, created_at ASC
    ''', (session_id,))

    ideas = cursor.fetchall()
    conn.close()
    return ideas

def list_sessions(limit=10):
    """セッション一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, topic, created_at
    FROM sessions
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    sessions = cursor.fetchall()
    conn.close()
    return sessions

if __name__ == '__main__':
    init_db()
