#!/usr/bin/env python3
"""
コードスニペットエージェント #7
- コードスニペットの保存
- 検索・統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "snippets.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # スニペットテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS snippets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        language TEXT,
        code TEXT NOT NULL,
        memo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 言語テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_created ON snippets(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_language ON snippets(language)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_snippet(title, code, language=None, memo=None):
    """スニペット追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 言語登録
    if language:
        cursor.execute('INSERT OR IGNORE INTO languages (name) VALUES (?)', (language,))

    cursor.execute('''
    INSERT INTO snippets (title, code, language, memo)
    VALUES (?, ?, ?, ?)
    ''', (title, code, language, memo))

    snippet_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return snippet_id

def list_snippets(limit=20):
    """スニペット一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, language, created_at
    FROM snippets
    ORDER BY created_at DESC
    LIMIT ?
    ''', (limit,))

    snippets = cursor.fetchall()
    conn.close()
    return snippets

def get_snippet(snippet_id):
    """スニペット取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, language, code, memo, created_at
    FROM snippets
    WHERE id = ?
    ''', (snippet_id,))

    snippet = cursor.fetchone()
    conn.close()
    return snippet

def search_snippets(keyword):
    """スニペット検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, language, created_at
    FROM snippets
    WHERE title LIKE ? OR code LIKE ? OR memo LIKE ?
    ORDER BY created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    snippets = cursor.fetchall()
    conn.close()
    return snippets

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全スニペット数
    cursor.execute('SELECT COUNT(*) FROM snippets')
    stats['total_snippets'] = cursor.fetchone()[0]

    # 言語別
    cursor.execute('''
    SELECT language, COUNT(*) as count
    FROM snippets
    WHERE language IS NOT NULL
    GROUP BY language
    ORDER BY count DESC
    ''')
    stats['by_language'] = dict(cursor.fetchall())

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
