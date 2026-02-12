#!/usr/bin/env python3
"""
映画記録エージェント #6
- 見た映画の記録
- 検索・統計機能
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "movies.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 映画テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS movies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        director TEXT,
        genre TEXT,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        memo TEXT,
        watched_at DATE,
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
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_created ON movies(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_genre ON movies(genre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_movies_rating ON movies(rating)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_movie(title, director=None, genre=None, rating=None, memo=None, watched_at=None):
    """映画追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ジャンル登録
    if genre:
        cursor.execute('INSERT OR IGNORE INTO genres (name) VALUES (?)', (genre,))

    # 視聴日
    if not watched_at:
        watched_at = datetime.now().strftime("%Y-%m-%d")

    cursor.execute('''
    INSERT INTO movies (title, director, genre, rating, memo, watched_at)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, director, genre, rating, memo, watched_at))

    movie_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return movie_id

def list_movies(limit=20):
    """映画一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, director, genre, rating, watched_at
    FROM movies
    ORDER BY watched_at DESC, created_at DESC
    LIMIT ?
    ''', (limit,))

    movies = cursor.fetchall()
    conn.close()
    return movies

def search_movies(keyword):
    """映画検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, director, genre, rating, watched_at
    FROM movies
    WHERE title LIKE ? OR director LIKE ? OR memo LIKE ?
    ORDER BY watched_at DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    movies = cursor.fetchall()
    conn.close()
    return movies

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全映画数
    cursor.execute('SELECT COUNT(*) FROM movies')
    stats['total_movies'] = cursor.fetchone()[0]

    # ジャンル別
    cursor.execute('''
    SELECT genre, COUNT(*) as count
    FROM movies
    WHERE genre IS NOT NULL
    GROUP BY genre
    ORDER BY count DESC
    ''')
    stats['by_genre'] = dict(cursor.fetchall())

    # 評価別
    cursor.execute('''
    SELECT rating, COUNT(*) as count
    FROM movies
    WHERE rating IS NOT NULL
    GROUP BY rating
    ORDER BY rating DESC
    ''')
    stats['by_rating'] = dict(cursor.fetchall())

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
