#!/usr/bin/env python3
"""
Watchlist Agent #21
- Track items you're watching
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "watchlist.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        url TEXT,
        status TEXT DEFAULT 'watching' CHECK(status IN ('watching', 'completed', 'dropped', 'on_hold')),
        priority INTEGER DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlist(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_category ON watchlist(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_watchlist_priority ON watchlist(priority)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_item(title, description=None, category=None, url=None, priority=None, notes=None):
    """Add item to watchlist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO watchlist (title, description, category, url, priority, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (title, description, category, url, priority, notes))

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def update_status(item_id, status):
    """Update item status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE watchlist SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (status, item_id))

    conn.commit()
    conn.close()

def list_items(status=None, category=None, limit=20):
    """List watchlist items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, description, category, url, status, priority, notes, created_at, updated_at
    FROM watchlist
    '''

    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)

    if category:
        conditions.append('category = ?')
        params.append(category)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY priority DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    items = cursor.fetchall()
    conn.close()
    return items

def search_items(keyword):
    """Search watchlist items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, description, category, url, status, priority, notes, created_at, updated_at
    FROM watchlist
    WHERE title LIKE ? OR description LIKE ? OR notes LIKE ?
    ORDER BY priority DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    items = cursor.fetchall()
    conn.close()
    return items

def delete_item(item_id):
    """Delete item from watchlist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM watchlist WHERE id = ?', (item_id,))

    conn.commit()
    conn.close()

def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM watchlist')
    stats['total'] = cursor.fetchone()[0]

    for status in ['watching', 'completed', 'dropped', 'on_hold']:
        cursor.execute('SELECT COUNT(*) FROM watchlist WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
