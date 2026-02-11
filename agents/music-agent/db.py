#!/usr/bin/env python3
"""
音楽エージェント #31
- 音楽プレイリスト管理
- 曲・アーティスト・アルバム・ジャンル
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "music.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 曲テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT,
        album TEXT,
        genre TEXT,
        year INTEGER,
        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # プレイリストテーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # プレイリスト曲関連テーブル
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER NOT NULL,
        song_id INTEGER NOT NULL,
        position INTEGER,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
        FOREIGN KEY (song_id) REFERENCES songs(id) ON DELETE CASCADE
    )
    ''')

    # インデックス
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_playlist_songs_playlist ON playlist_songs(playlist_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_playlist_songs_song ON playlist_songs(song_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_song(title, artist=None, album=None, genre=None, year=None, rating=None, notes=None):
    """曲追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO songs (title, artist, album, genre, year, rating, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, artist, album, genre, year, rating, notes))

    song_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return song_id

def update_song(song_id, title=None, artist=None, album=None, genre=None, year=None, rating=None, notes=None):
    """曲更新"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if artist:
        updates.append("artist = ?")
        params.append(artist)
    if album:
        updates.append("album = ?")
        params.append(album)
    if genre:
        updates.append("genre = ?")
        params.append(genre)
    if year is not None:
        updates.append("year = ?")
        params.append(year)
    if rating is not None:
        updates.append("rating = ?")
        params.append(rating)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE songs SET {', '.join(updates)} WHERE id = ?"
        params.append(song_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def delete_song(song_id):
    """曲削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM songs WHERE id = ?', (song_id,))

    conn.commit()
    conn.close()

def list_songs(genre=None, artist=None, limit=20):
    """曲一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, artist, album, genre, year, rating, notes, created_at
    FROM songs
    '''

    params = []
    conditions = []

    if genre:
        conditions.append("genre = ?")
        params.append(genre)
    if artist:
        conditions.append("artist = ?")
        params.append(artist)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    songs = cursor.fetchall()
    conn.close()
    return songs

def search_songs(keyword):
    """曲検索"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, artist, album, genre, year, rating, notes, created_at
    FROM songs
    WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR genre LIKE ?
    ORDER BY created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    songs = cursor.fetchall()
    conn.close()
    return songs

def add_playlist(name, description=None):
    """プレイリスト追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO playlists (name, description)
    VALUES (?, ?)
    ''', (name, description))

    playlist_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return playlist_id

def add_song_to_playlist(playlist_id, song_id, position=None):
    """プレイリストに曲追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # positionが指定されていない場合、最後に追加
    if position is None:
        cursor.execute('SELECT COALESCE(MAX(position), 0) + 1 FROM playlist_songs WHERE playlist_id = ?', (playlist_id,))
        position = cursor.fetchone()[0]

    cursor.execute('''
    INSERT INTO playlist_songs (playlist_id, song_id, position)
    VALUES (?, ?, ?)
    ''', (playlist_id, song_id, position))

    conn.commit()
    conn.close()

def get_playlist(playlist_id):
    """プレイリスト取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # プレイリスト情報
    cursor.execute('''
    SELECT id, name, description, created_at
    FROM playlists
    WHERE id = ?
    ''', (playlist_id,))

    playlist = cursor.fetchone()

    # 曲一覧
    cursor.execute('''
    SELECT s.id, s.title, s.artist, s.album, s.genre, s.year, s.rating, ps.position
    FROM playlist_songs ps
    JOIN songs s ON ps.song_id = s.id
    WHERE ps.playlist_id = ?
    ORDER BY ps.position
    ''', (playlist_id,))

    songs = cursor.fetchall()
    conn.close()

    return {'playlist': playlist, 'songs': songs}

def list_playlists():
    """プレイリスト一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT p.id, p.name, p.description, COUNT(ps.song_id) as song_count
    FROM playlists p
    LEFT JOIN playlist_songs ps ON p.id = ps.playlist_id
    GROUP BY p.id
    ORDER BY p.name
    ''')

    playlists = cursor.fetchall()
    conn.close()
    return playlists

def remove_song_from_playlist(playlist_id, song_id):
    """プレイリストから曲削除"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM playlist_songs WHERE playlist_id = ? AND song_id = ?', (playlist_id, song_id))

    conn.commit()
    conn.close()

def get_stats():
    """統計情報"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # 全曲数
    cursor.execute('SELECT COUNT(*) FROM songs')
    stats['total_songs'] = cursor.fetchone()[0]

    # アーティスト数
    cursor.execute('SELECT COUNT(DISTINCT artist) FROM songs WHERE artist IS NOT NULL')
    stats['artists'] = cursor.fetchone()[0]

    # ジャンル数
    cursor.execute('SELECT COUNT(DISTINCT genre) FROM songs WHERE genre IS NOT NULL')
    stats['genres'] = cursor.fetchone()[0]

    # プレイリスト数
    cursor.execute('SELECT COUNT(*) FROM playlists')
    stats['playlists'] = cursor.fetchone()[0]

    # 平均評価
    cursor.execute('SELECT AVG(rating) FROM songs WHERE rating IS NOT NULL')
    avg_rating = cursor.fetchone()[0]
    stats['avg_rating'] = round(avg_rating, 2) if avg_rating else None

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
