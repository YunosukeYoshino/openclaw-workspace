#!/usr/bin/env python3
"""
Skills Agent #26
- Skill acquisition tracking
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "skills.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT,
        description TEXT,
        level INTEGER DEFAULT 1 CHECK(level IN (1,2,3,4,5)),
        status TEXT DEFAULT 'learning' CHECK(status IN ('learning', 'practicing', 'mastered', 'abandoned')),
        priority INTEGER DEFAULT 0,
        goal TEXT,
        resources TEXT,
        notes TEXT,
        started_at TIMESTAMP,
        mastered_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skill_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        skill_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        duration INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_status ON skills(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_category ON skills(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_skills_level ON skills(level)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_skill_logs_skill ON skill_logs(skill_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_skill(name, category=None, description=None, level=1, priority=0, goal=None, resources=None, notes=None):
    """Add new skill"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO skills (name, category, description, level, priority, goal, resources, notes, started_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (name, category, description, level, priority, goal, resources, notes))

    skill_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return skill_id

def update_level(skill_id, level):
    """Update skill level"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if level == 5:
        cursor.execute('''
        UPDATE skills SET level = ?, status = 'mastered', mastered_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (level, skill_id))
    else:
        cursor.execute('''
        UPDATE skills SET level = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (level, skill_id))

    conn.commit()
    conn.close()

def update_status(skill_id, status):
    """Update skill status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if status == 'mastered':
        cursor.execute('''
        UPDATE skills SET status = 'mastered', mastered_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (skill_id,))
    else:
        cursor.execute('''
        UPDATE skills SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (status, skill_id))

    conn.commit()
    conn.close()

def log_practice(skill_id, action, duration=None, notes=None):
    """Log practice session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO skill_logs (skill_id, action, duration, notes)
    VALUES (?, ?, ?, ?)
    ''', (skill_id, action, duration, notes))

    conn.commit()
    conn.close()

def list_skills(status=None, category=None, level=None, limit=50):
    """List skills"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, category, description, level, status, priority, goal, resources, notes, started_at, created_at
    FROM skills
    '''

    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)

    if category:
        conditions.append('category = ?')
        params.append(category)

    if level:
        conditions.append('level = ?')
        params.append(level)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY priority DESC, level DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    skills = cursor.fetchall()
    conn.close()
    return skills

def search_skills(keyword):
    """Search skills"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, category, description, level, status, priority, goal, resources, notes, started_at, created_at
    FROM skills
    WHERE name LIKE ? OR description LIKE ? OR goal LIKE ?
    ORDER BY priority DESC, level DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    skills = cursor.fetchall()
    conn.close()
    return skills

def get_skill_logs(skill_id, limit=20):
    """Get practice logs for skill"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, action, duration, notes, created_at
    FROM skill_logs
    WHERE skill_id = ?
    ORDER BY created_at DESC LIMIT ?
    ''', (skill_id, limit))

    logs = cursor.fetchall()
    conn.close()
    return logs

def get_total_practice_time(skill_id):
    """Get total practice time for skill"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT SUM(duration) FROM skill_logs WHERE skill_id = ? AND duration IS NOT NULL
    ''', (skill_id,))

    result = cursor.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0

def get_stats():
    """Get skills statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM skills')
    stats['total_skills'] = cursor.fetchone()[0]

    for status in ['learning', 'practicing', 'mastered', 'abandoned']:
        cursor.execute('SELECT COUNT(*) FROM skills WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    cursor.execute('SELECT SUM(duration) FROM skill_logs WHERE duration IS NOT NULL')
    total_time = cursor.fetchone()[0]
    stats['total_practice_minutes'] = total_time if total_time else 0

    cursor.execute('SELECT COUNT(*) FROM skills WHERE level = 5')
    stats['mastered_count'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
