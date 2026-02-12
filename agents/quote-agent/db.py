#!/usr/bin/env python3
"""
名言エージェント #20
- 名言の記録と検索
- インスピレーション提供
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "quotes.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 名言テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        author TEXT,
        category TEXT,
        tags TEXT,
        rating INTEGER DEFAULT 0 CHECK(rating >= 0 AND rating <= 5),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_category ON quotes(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_rating ON quotes(rating)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quotes_created ON quotes(created_at)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_quote(content, author=None, category=None, tags=None):
    """名言追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # タグをカンマ区切りで保存
    tags_str = ','.join(tags) if tags else None

    cursor.execute('''
    INSERT INTO quotes (content, author, category, tags)
    VALUES (?, ?, ?, ?)
    ''', (content, author, category, tags_str))

    quote_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return quote_id

def list_quotes(limit=20):
    """名言一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, content, author, category, rating
    FROM quotes
    ORDER BY rating DESC, created_at DESC
    LIMIT ?
    ''', (limit,))

    quotes = cursor.fetchall()
    conn.close()
    return quotes

def search_quotes(keyword):
    """名言検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, content, author, category, rating
    FROM quotes
    WHERE content LIKE ? OR author LIKE ? OR category LIKE ?
    ORDER BY rating DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    quotes = cursor.fetchall()
    conn.close()
    return quotes

if __name__ == '__main__':
    init_db()
