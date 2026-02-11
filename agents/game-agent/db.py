#!/usr/bin/env python3
"""
ゲームエージェント #32
- ゲーム記録管理
- タイトル・ジャンル・プレイ時間・クリア状況・評価
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "games.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ゲームテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        platform TEXT,
        genre TEXT,
        start_date DATE,
        end_date DATE,
        play_time INTEGER,
        status TEXT DEFAULT 'playing' CHECK(status IN ('playing', 'completed', 'dropped', 'wishlist')),
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_title ON games(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_status ON games(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_genre ON games(genre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_games_platform ON games(platform)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_game(title, platform=None, genre=None, start_date=None, end_date=None, play_time=None, status='playing', rating=None, notes=None):
    """ゲーム追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO games (title, platform, genre, start_date, end_date, play_time, status, rating, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, platform, genre, start_date, end_date, play_time, status, rating, notes))

    game_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return game_id

def update_game(game_id, title=None, platform=None, genre=None, start_date=None, end_date=None, play_time=None, status=None, rating=None, notes=None):
    """ゲーム更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if platform:
        updates.append("platform = ?")
        params.append(platform)
    if genre:
        updates.append("genre = ?")
        params.append(genre)
    if start_date:
        updates.append("start_date = ?")
        params.append(start_date)
    if end_date:
        updates.append("end_date = ?")
        params.append(end_date)
    if play_time is not None:
        updates.append("play_time = ?")
        params.append(play_time)
    if status:
        updates.append("status = ?")
        params.append(status)
    if rating is not None:
        updates.append("rating = ?")
        params.append(rating)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE games SET {', '.join(updates)} WHERE id = ?"
        params.append(game_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_game(game_id):
    """ゲーム削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM games WHERE id = ?', (game_id,))

    conn.commit()
    conn.close()

def list_games(status=None, genre=None, platform=None, limit=20):
    """ゲーム一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, platform, genre, start_date, end_date, play_time, status, rating, notes, created_at
    FROM games
    '''

    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if genre:
        conditions.append("genre = ?")
        params.append(genre)
    if platform:
        conditions.append("platform = ?")
        params.append(platform)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    games = cursor.fetchall()
    conn.close()
    return games

def search_games(keyword):
    """ゲーム検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, platform, genre, start_date, end_date, play_time, status, rating, notes, created_at
    FROM games
    WHERE title LIKE ? OR genre LIKE ? OR platform LIKE ? OR notes LIKE ?
    ORDER BY created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    games = cursor.fetchall()
    conn.close()
    return games

def get_game(game_id):
    """ゲーム詳細取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, platform, genre, start_date, end_date, play_time, status, rating, notes, created_at
    FROM games
    WHERE id = ?
    ''', (game_id,))

    game = cursor.fetchone()
    conn.close()
    return game

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全ゲーム数
    cursor.execute('SELECT COUNT(*) FROM games')
    stats['total'] = cursor.fetchone()[0]

    # プレイ中
    cursor.execute('SELECT COUNT(*) FROM games WHERE status = "playing"')
    stats['playing'] = cursor.fetchone()[0]

    # クリア済み
    cursor.execute('SELECT COUNT(*) FROM games WHERE status = "completed"')
    stats['completed'] = cursor.fetchone()[0]

    # 中断
    cursor.execute('SELECT COUNT(*) FROM games WHERE status = "dropped"')
    stats['dropped'] = cursor.fetchone()[0]

    # ウィッシュリスト
    cursor.execute('SELECT COUNT(*) FROM games WHERE status = "wishlist"')
    stats['wishlist'] = cursor.fetchone()[0]

    # 総プレイ時間
    cursor.execute('SELECT SUM(play_time) FROM games WHERE play_time IS NOT NULL')
    total_time = cursor.fetchone()[0]
    stats['total_play_time'] = total_time if total_time else 0

    # 平均評価
    cursor.execute('SELECT AVG(rating) FROM games WHERE rating IS NOT NULL')
    avg_rating = cursor.fetchone()[0]
    stats['avg_rating'] = round(avg_rating, 2) if avg_rating else None

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
