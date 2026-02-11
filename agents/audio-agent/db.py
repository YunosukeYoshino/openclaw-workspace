#!/usr/bin/env python3
"""
Audio Agent #1
- Audio management and organization
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "audio.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audio_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        file_path TEXT,
        duration REAL,
        format TEXT,
        bitrate INTEGER,
        category TEXT,
        tags TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS playlist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        playlist_id INTEGER NOT NULL,
        audio_id INTEGER NOT NULL,
        position INTEGER NOT NULL,
        FOREIGN KEY (playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
        FOREIGN KEY (audio_id) REFERENCES audio_files(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recordings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        file_path TEXT,
        duration REAL,
        format TEXT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audio_title ON audio_files(title)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audio_category ON audio_files(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_playlist_items ON playlist_items(playlist_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_recordings_date ON recordings(recorded_at)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_audio(title, file_path=None, duration=None, format=None, bitrate=None, category=None, tags=None, description=None):
    """Add audio file"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO audio_files (title, file_path, duration, format, bitrate, category, tags, description)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, file_path, duration, format, bitrate, category, tags, description))

    audio_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return audio_id

def update_audio(audio_id, **kwargs):
    """Update audio file"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    allowed_fields = ['title', 'file_path', 'duration', 'format', 'bitrate', 'category', 'tags', 'description']
    set_clause = ', '.join([f"{field} = ?" for field in kwargs if field in allowed_fields])
    values = [kwargs[field] for field in kwargs if field in allowed_fields]

    if set_clause:
        values.append(audio_id)
        cursor.execute(f'''
        UPDATE audio_files SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', values)

    conn.commit()
    conn.close()

def delete_audio(audio_id):
    """Delete audio file"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM audio_files WHERE id = ?', (audio_id,))

    conn.commit()
    conn.close()

def list_audio(category=None, tags=None, limit=50):
    """List audio files"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, file_path, duration, format, bitrate, category, tags, description, created_at
    FROM audio_files
    '''

    params = []
    conditions = []

    if category:
        conditions.append('category = ?')
        params.append(category)

    if tags:
        conditions.append('tags LIKE ?')
        params.append(f'%{tags}%')

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    audio_list = cursor.fetchall()
    conn.close()
    return audio_list

def create_playlist(name, description=None):
    """Create playlist"""
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

def add_to_playlist(playlist_id, audio_id, position=None):
    """Add audio to playlist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if position is None:
        cursor.execute('SELECT COALESCE(MAX(position), 0) + 1 FROM playlist_items WHERE playlist_id = ?', (playlist_id,))
        position = cursor.fetchone()[0]

    cursor.execute('''
    INSERT INTO playlist_items (playlist_id, audio_id, position)
    VALUES (?, ?, ?)
    ''', (playlist_id, audio_id, position))

    conn.commit()
    conn.close()

def list_playlists():
    """List playlists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, created_at
    FROM playlists
    ORDER BY name
    ''')

    playlists = cursor.fetchall()
    conn.close()
    return playlists

def get_playlist_items(playlist_id):
    """Get playlist items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT pi.id, a.id, a.title, a.duration, pi.position
    FROM playlist_items pi
    JOIN audio_files a ON pi.audio_id = a.id
    WHERE pi.playlist_id = ?
    ORDER BY pi.position
    ''', (playlist_id,))

    items = cursor.fetchall()
    conn.close()
    return items

def add_recording(title, file_path, duration, format, notes=None):
    """Add recording"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO recordings (title, file_path, duration, format, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (title, file_path, duration, format, notes))

    recording_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return recording_id

def list_recordings(limit=50):
    """List recordings"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, file_path, duration, format, recorded_at, notes
    FROM recordings
    ORDER BY recorded_at DESC
    LIMIT ?
    ''', (limit,))

    recordings = cursor.fetchall()
    conn.close()
    return recordings

def search_audio(query, limit=20):
    """Search audio"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, file_path, duration, format, category, tags, description, created_at
    FROM audio_files
    WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
    ORDER BY created_at DESC
    LIMIT ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))

    results = cursor.fetchall()
    conn.close()
    return results

def get_stats():
    """Get audio statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM audio_files')
    stats['total_audio'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM playlists')
    stats['total_playlists'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM recordings')
    stats['total_recordings'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM audio_files WHERE format = "mp3"')
    stats['mp3_count'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM audio_files WHERE format = "wav"')
    stats['wav_count'] = cursor.fetchone()[0]

    cursor.execute('SELECT COALESCE(SUM(duration), 0) FROM audio_files')
    stats['total_duration'] = round(cursor.fetchone()[0], 2)

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
