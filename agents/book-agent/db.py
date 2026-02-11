#!/usr/bin/env python3
"""
読書記録エージェント #4
- 読んだ本の記録
- 検索・統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "books.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 本テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        genre TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        memo TEXT,
        started_at DATE,
        finished_at DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ジャンルテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS genres (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_created ON books(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_genre ON books(genre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_books_rating ON books(rating)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_book(title, author=None, genre=None, rating=None, memo=None, started_at=None, finished_at=None):
    """本追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ジャンル登録
    if genre:
        cursor.execute('INSERT OR IGNORE INTO genres (name) VALUES (?)', (genre,))

    cursor.execute('''
    INSERT INTO books (title, author, genre, rating, memo, started_at, finished_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, author, genre, rating, memo, started_at, finished_at))

    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return book_id

def list_books(limit=20):
    """本一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, author, genre, rating, finished_at
    FROM books
    ORDER BY finished_at DESC, created_at DESC
    LIMIT ?
    ''', (limit,))

    books = cursor.fetchall()
    conn.close()
    return books

def search_books(keyword):
    """本検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, author, genre, rating, finished_at
    FROM books
    WHERE title LIKE ? OR author LIKE ? OR memo LIKE ?
    ORDER BY finished_at DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    books = cursor.fetchall()
    conn.close()
    return books

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全冊数
    cursor.execute('SELECT COUNT(*) FROM books')
    stats['total_books'] = cursor.fetchone()[0]

    # ジャンル別
    cursor.execute('''
    SELECT genre, COUNT(*) as count
    FROM books
    WHERE genre IS NOT NULL
    GROUP BY genre
    ORDER BY count DESC
    ''')
    stats['by_genre'] = dict(cursor.fetchall())

    # 評価別
    cursor.execute('''
    SELECT rating, COUNT(*) as count
    FROM books
    WHERE rating IS NOT NULL
    GROUP BY rating
    ORDER BY rating DESC
    ''')
    stats['by_rating'] = dict(cursor.fetchall())

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
