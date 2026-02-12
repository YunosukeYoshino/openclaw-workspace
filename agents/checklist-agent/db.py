#!/usr/bin/env python3
"""
Checklist Agent #3
- Checklist and task checklist management
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "checklists.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checklists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checklist_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        checklist_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        completed INTEGER DEFAULT 0,
        position INTEGER NOT NULL,
        FOREIGN KEY (checklist_id) REFERENCES checklists(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS checklist_templates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS template_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id INTEGER NOT NULL,
        text TEXT NOT NULL,
        position INTEGER NOT NULL,
        FOREIGN KEY (template_id) REFERENCES checklist_templates(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_checklists_category ON checklists(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_checklist ON checklist_items(checklist_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_items_completed ON checklist_items(completed)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_template_items ON template_items(template_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_checklist(title, description=None, category=None):
    """Create checklist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO checklists (title, description, category)
    VALUES (?, ?, ?)
    ''', (title, description, category))

    checklist_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return checklist_id

def add_item(checklist_id, text, position=None):
    """Add item to checklist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if position is None:
        cursor.execute('SELECT COALESCE(MAX(position), 0) + 1 FROM checklist_items WHERE checklist_id = ?', (checklist_id,))
        position = cursor.fetchone()[0]

    cursor.execute('''
    INSERT INTO checklist_items (checklist_id, text, position)
    VALUES (?, ?, ?)
    ''', (checklist_id, text, position))

    item_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return item_id

def toggle_item(item_id):
    """Toggle item completion"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT completed FROM checklist_items WHERE id = ?', (item_id,))
    current = cursor.fetchone()[0]

    new_status = 1 if current == 0 else 0
    cursor.execute('UPDATE checklist_items SET completed = ? WHERE id = ?', (new_status, item_id))

    conn.commit()
    conn.close()
    return new_status

def delete_item(item_id):
    """Delete item"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM checklist_items WHERE id = ?', (item_id,))

    conn.commit()
    conn.close()

def delete_checklist(checklist_id):
    """Delete checklist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM checklists WHERE id = ?', (checklist_id,))

    conn.commit()
    conn.close()

def list_checklists(category=None, limit=50):
    """List checklists"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, description, category, created_at
    FROM checklists
    '''

    params = []

    if category:
        query += ' WHERE category = ?'
        params.append(category)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    checklists = cursor.fetchall()
    conn.close()
    return checklists

def get_checklist_items(checklist_id):
    """Get checklist items"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, text, completed, position FROM checklist_items
    WHERE checklist_id = ?
    ORDER BY position
    ''', (checklist_id,))

    items = cursor.fetchall()
    conn.close()
    return items

def create_template(name, description=None):
    """Create template"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO checklist_templates (name, description)
    VALUES (?, ?)
    ''', (name, description))

    template_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return template_id

def add_template_item(template_id, text, position=None):
    """Add item to template"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if position is None:
        cursor.execute('SELECT COALESCE(MAX(position), 0) + 1 FROM template_items WHERE template_id = ?', (template_id,))
        position = cursor.fetchone()[0]

    cursor.execute('''
    INSERT INTO template_items (template_id, text, position)
    VALUES (?, ?, ?)
    ''', (template_id, text, position))

    conn.commit()
    conn.close()

def create_from_template(template_id, title):
    """Create checklist from template"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO checklists (title)
    VALUES (?)
    ''', (title,))

    checklist_id = cursor.lastrowid

    cursor.execute('''
    INSERT INTO checklist_items (checklist_id, text, position)
    SELECT ?, text, position FROM template_items WHERE template_id = ?
    ''', (checklist_id, template_id))

    conn.commit()
    conn.close()
    return checklist_id

def get_progress(checklist_id):
    """Get checklist progress"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM checklist_items WHERE checklist_id = ?', (checklist_id,))
    total = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM checklist_items WHERE checklist_id = ? AND completed = 1', (checklist_id,))
    completed = cursor.fetchone()[0]

    conn.close()

    if total == 0:
        return {'total': 0, 'completed': 0, 'percentage': 0}

    return {'total': total, 'completed': completed, 'percentage': round((completed / total) * 100, 1)}

def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM checklists')
    stats['total_checklists'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM checklist_items')
    stats['total_items'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM checklist_items WHERE completed = 1')
    stats['completed_items'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
