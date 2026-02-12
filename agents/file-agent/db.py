#!/usr/bin/env python3
"""
File Management Agent
- File upload/download tracking
- File organization and categorization
- Search and tagging
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "files.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Files table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        filepath TEXT NOT NULL,
        category TEXT,
        tags TEXT,
        description TEXT,
        file_size INTEGER,
        file_type TEXT,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        download_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'deleted'))
    )
    ''')

    # Categories table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Tags table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_tags ON files(tags)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_status ON files(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_upload_date ON files(upload_date)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_file(filename, filepath, category=None, tags=None, description=None, file_size=None, file_type=None):
    """Add file record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO files (filename, filepath, category, tags, description, file_size, file_type)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (filename, filepath, category, tags, description, file_size, file_type))

    file_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return file_id

def get_file(file_id):
    """Get file by ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM files WHERE id = ?', (file_id,))
    file_data = cursor.fetchone()
    conn.close()
    return file_data

def list_files(limit=50, category=None, status='active'):
    """List files"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if category:
        cursor.execute('''
        SELECT * FROM files
        WHERE category = ? AND status = ?
        ORDER BY upload_date DESC
        LIMIT ?
        ''', (category, status, limit))
    else:
        cursor.execute('''
        SELECT * FROM files
        WHERE status = ?
        ORDER BY upload_date DESC
        LIMIT ?
        ''', (status, limit))

    files = cursor.fetchall()
    conn.close()
    return files

def search_files(keyword):
    """Search files by keyword"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM files
    WHERE status = 'active' AND
        (filename LIKE ? OR description LIKE ? OR tags LIKE ? OR category LIKE ?)
    ORDER BY upload_date DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    files = cursor.fetchall()
    conn.close()
    return files

def search_by_tag(tag):
    """Search files by tag"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT * FROM files
    WHERE status = 'active' AND tags LIKE ?
    ORDER BY upload_date DESC
    ''', (f'%{tag}%',))

    files = cursor.fetchall()
    conn.close()
    return files

def update_file(file_id, **kwargs):
    """Update file record"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            updates.append(f"{key} = ?")
            values.append(value)
    values.append(file_id)

    if updates:
        cursor.execute(f'''
        UPDATE files
        SET {', '.join(updates)}
        WHERE id = ?
        ''', values)
        conn.commit()

    conn.close()

def archive_file(file_id):
    """Archive file"""
    update_file(file_id, status='archived')

def delete_file(file_id):
    """Delete file (soft delete)"""
    update_file(file_id, status='deleted')

def increment_download_count(file_id):
    """Increment download count"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE files
    SET download_count = download_count + 1
    WHERE id = ?
    ''', (file_id,))

    conn.commit()
    conn.close()

def add_category(name, description=None):
    """Add category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO categories (name, description)
        VALUES (?, ?)
        ''', (name, description))
        conn.commit()
        category_id = cursor.lastrowid
        conn.close()
        return category_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def list_categories():
    """List all categories"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = cursor.fetchall()
    conn.close()
    return categories

def get_stats():
    """Get file statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Total files
    cursor.execute('SELECT COUNT(*) FROM files WHERE status = ?', ('active',))
    stats['total'] = cursor.fetchone()[0]

    # By category
    cursor.execute('''
    SELECT category, COUNT(*)
    FROM files
    WHERE status = 'active' AND category IS NOT NULL
    GROUP BY category
    ORDER BY COUNT(*) DESC
    ''')
    stats['by_category'] = dict(cursor.fetchall())

    # Total size
    cursor.execute('SELECT SUM(file_size) FROM files WHERE status = ? AND file_size IS NOT NULL', ('active',))
    total_size = cursor.fetchone()[0]
    stats['total_size'] = total_size if total_size else 0

    # Total downloads
    cursor.execute('SELECT SUM(download_count) FROM files WHERE status = ?', ('active',))
    total_downloads = cursor.fetchone()[0]
    stats['total_downloads'] = total_downloads if total_downloads else 0

    # Most downloaded
    cursor.execute('''
    SELECT filename, download_count
    FROM files
    WHERE status = 'active'
    ORDER BY download_count DESC
    LIMIT 5
    ''')
    stats['most_downloaded'] = cursor.fetchall()

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
