#!/usr/bin/env python3
"""
Wishlist Agent #22
- Track items you want
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "wishlist.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        category TEXT,
        price REAL,
        url TEXT,
        priority INTEGER DEFAULT 0,
        status TEXT DEFAULT 'wanted' CHECK(status IN ('wanted', 'acquired', 'abandoned')),
        acquired_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_wishlist_status ON wishlist(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_wishlist_category ON wishlist(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_wishlist_priority ON wishlist(priority)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_item(name, description=None, category=None, price=None, url=None, priority=None, notes=None):
    """Add item to wishlist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO wishlist (name, description, category, price, url, priority, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, description, category, price, url, priority, notes))

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def mark_acquired(item_id):
    """Mark item as acquired"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE wishlist SET status = 'acquired', acquired_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (item_id,))

    conn.commit()
    conn.close()

def update_status(item_id, status):
    """Update item status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE wishlist SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (status, item_id))

    conn.commit()
    conn.close()

def list_items(status=None, category=None, limit=20):
    """List wishlist items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, description, category, price, url, priority, status, notes, created_at, updated_at
    FROM wishlist
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
    """Search wishlist items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, description, category, price, url, priority, status, notes, created_at, updated_at
    FROM wishlist
    WHERE name LIKE ? OR description LIKE ? OR notes LIKE ?
    ORDER BY priority DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    items = cursor.fetchall()
    conn.close()
    return items

def delete_item(item_id):
    """Delete item from wishlist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM wishlist WHERE id = ?', (item_id,))

    conn.commit()
    conn.close()

def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM wishlist')
    stats['total'] = cursor.fetchone()[0]

    for status in ['wanted', 'acquired', 'abandoned']:
        cursor.execute('SELECT COUNT(*) FROM wishlist WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(price) FROM wishlist WHERE status = "wanted" AND price IS NOT NULL')
    total_price = cursor.fetchone()[0]
    stats['total_price'] = total_price if total_price else 0

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
