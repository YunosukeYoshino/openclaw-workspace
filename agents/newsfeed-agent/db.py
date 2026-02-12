#!/usr/bin/env python3
"""
Newsfeed Agent #30
- News tracking
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "newsfeed.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        url TEXT,
        source TEXT,
        category TEXT,
        summary TEXT,
        author TEXT,
        publish_date DATE,
        status TEXT DEFAULT 'unread' CHECK(status IN ('unread', 'read', 'archived', 'saved')),
        importance INTEGER DEFAULT 0,
        tags TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        url TEXT,
        category TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
        last_fetched TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_status ON news(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_category ON news(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_source ON news(source)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_importance ON news(importance)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_created ON news(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_sources_status ON news_sources(status)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_news(title, url=None, source=None, category=None, summary=None, author=None, publish_date=None, importance=0, tags=None, notes=None):
    """Add news item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO news (title, url, source, category, summary, author, publish_date, importance, tags, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, url, source, category, summary, author, publish_date, importance, tags, notes))

    news_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return news_id

def mark_read(news_id):
    """Mark news as read"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE news SET status = 'read', updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (news_id,))

    conn.commit()
    conn.close()

def mark_saved(news_id):
    """Mark news as saved"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE news SET status = 'saved', updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (news_id,))

    conn.commit()
    conn.close()

def add_source(name, url=None, category=None):
    """Add news source"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO news_sources (name, url, category)
    VALUES (?, ?, ?)
    ''', (name, url, category))

    source_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return source_id

def list_news(status=None, category=None, source=None, limit=50):
    """List news items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, url, source, category, summary, author, publish_date, status, importance, tags, created_at
    FROM news
    '''

    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)

    if category:
        conditions.append('category = ?')
        params.append(category)

    if source:
        conditions.append('source = ?')
        params.append(source)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY importance DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    news = cursor.fetchall()
    conn.close()
    return news

def search_news(keyword):
    """Search news"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, url, source, category, summary, author, publish_date, status, importance, tags, created_at
    FROM news
    WHERE title LIKE ? OR summary LIKE ? OR tags LIKE ?
    ORDER BY importance DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    news_items = cursor.fetchall()
    conn.close()
    return news_items

def list_sources(status=None, limit=20):
    """List news sources"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, url, category, status, last_fetched, created_at
    FROM news_sources
    '''

    params = []

    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY name ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    sources = cursor.fetchall()
    conn.close()
    return sources

def archive_old_news(days=30):
    """Archive news older than specified days"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE news SET status = 'archived', updated_at = CURRENT_TIMESTAMP
    WHERE status = 'read' AND created_at < datetime('now', '-' || ? || ' days')
    ''', (days,))

    conn.commit()
    conn.close()

def get_stats():
    """Get news statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM news')
    stats['total_news'] = cursor.fetchone()[0]

    for status in ['unread', 'read', 'saved', 'archived']:
        cursor.execute('SELECT COUNT(*) FROM news WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM news_sources WHERE status = "active"')
    stats['active_sources'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
