#!/usr/bin/env python3
"""
Search Agent
- Web search tracking
- Local file search
- Search history management
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "search.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Search history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        query TEXT NOT NULL,
        search_type TEXT NOT NULL CHECK(search_type IN ('web', 'local', 'file')),
        result_count INTEGER DEFAULT 0,
        search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        saved BOOLEAN DEFAULT 0
    )
    ''')

    # Saved searches table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS saved_searches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (search_id) REFERENCES search_history(id) ON DELETE CASCADE
    )
    ''')

    # Search results cache
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        search_id INTEGER NOT NULL,
        title TEXT,
        url TEXT,
        snippet TEXT,
        rank INTEGER,
        FOREIGN KEY (search_id) REFERENCES search_history(id) ON DELETE CASCADE
    )
    ''')

    # Local files index
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS local_files_index (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        filename TEXT NOT NULL,
        content_preview TEXT,
        indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_modified TIMESTAMP,
        file_type TEXT,
        UNIQUE(filepath)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_history_timestamp ON search_history(search_timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_history_type ON search_history(search_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_search_results_search ON search_results(search_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_local_files_filename ON local_files_index(filename)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_local_files_content ON local_files_index(content_preview)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_search(query, search_type, result_count=0):
    """Add search to history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO search_history (query, search_type, result_count)
    VALUES (?, ?, ?)
    ''', (query, search_type, result_count))

    search_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return search_id

def add_search_result(search_id, title, url, snippet, rank):
    """Add search result"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO search_results (search_id, title, url, snippet, rank)
    VALUES (?, ?, ?, ?, ?)
    ''', (search_id, title, url, snippet, rank))

    conn.commit()
    conn.close()

def save_search(search_id, name, description=None):
    """Save search for later use"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO saved_searches (search_id, name, description)
        VALUES (?, ?, ?)
        ''', (search_id, name, description))

        # Mark as saved
        cursor.execute('UPDATE search_history SET saved = 1 WHERE id = ?', (search_id,))

        saved_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return saved_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def get_search_history(limit=20, search_type=None):
    """Get search history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if search_type:
        cursor.execute('''
        SELECT * FROM search_history
        WHERE search_type = ?
        ORDER BY search_timestamp DESC
        LIMIT ?
        ''', (search_type, limit))
    else:
        cursor.execute('''
        SELECT * FROM search_history
        ORDER BY search_timestamp DESC
        LIMIT ?
        ''', (limit,))

    history = cursor.fetchall()
    conn.close()
    return history

def get_saved_searches():
    """Get saved searches"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT ss.id, ss.name, ss.description, ss.created_at, sh.query, sh.search_type
    FROM saved_searches ss
    JOIN search_history sh ON ss.search_id = sh.id
    ORDER BY ss.created_at DESC
    ''')

    saved = cursor.fetchall()
    conn.close()
    return saved

def index_local_file(filepath, filename, content_preview=None, file_type=None, last_modified=None):
    """Index local file for search"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT OR REPLACE INTO local_files_index (filepath, filename, content_preview, file_type, last_modified, indexed_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (filepath, filename, content_preview, file_type, last_modified, datetime.now()))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        return False

def search_local_files(keyword):
    """Search local files"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM local_files_index
    WHERE filename LIKE ? OR content_preview LIKE ?
    ORDER BY filename
    ''', (f'%{keyword}%', f'%{keyword}%'))

    files = cursor.fetchall()
    conn.close()
    return files

def delete_search(search_id):
    """Delete search from history"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM search_history WHERE id = ?', (search_id,))
    conn.commit()
    conn.close()

def unsave_search(saved_id):
    """Unsave search"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get search_id first
    cursor.execute('SELECT search_id FROM saved_searches WHERE id = ?', (saved_id,))
    result = cursor.fetchone()

    if result:
        search_id = result[0]
        cursor.execute('DELETE FROM saved_searches WHERE id = ?', (saved_id,))
        # Check if still saved
        cursor.execute('SELECT COUNT(*) FROM saved_searches WHERE search_id = ?', (search_id,))
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute('UPDATE search_history SET saved = 0 WHERE id = ?', (search_id,))

    conn.commit()
    conn.close()

def get_stats():
    """Get search statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Total searches
    cursor.execute('SELECT COUNT(*) FROM search_history')
    stats['total_searches'] = cursor.fetchone()[0]

    # By type
    cursor.execute('''
    SELECT search_type, COUNT(*)
    FROM search_history
    GROUP BY search_type
    ''')
    stats['by_type'] = dict(cursor.fetchall())

    # Saved searches
    cursor.execute('SELECT COUNT(*) FROM saved_searches')
    stats['saved_searches'] = cursor.fetchone()[0]

    # Indexed files
    cursor.execute('SELECT COUNT(*) FROM local_files_index')
    stats['indexed_files'] = cursor.fetchone()[0]

    # Recent searches (last 7 days)
    cursor.execute('''
    SELECT COUNT(*) FROM search_history
    WHERE search_timestamp >= datetime('now', '-7 days')
    ''')
    stats['recent_searches'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
