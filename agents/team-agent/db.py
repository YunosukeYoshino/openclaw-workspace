#!/usr/bin/env python3
"""
Team Agent #25
- Team member management
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "team.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT,
        email TEXT,
        phone TEXT,
        department TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive', 'on_leave')),
        skills TEXT,
        joined_at TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS member_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'in_progress', 'completed')),
        due_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_status ON members(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_members_department ON members(department)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_tasks_member ON member_tasks(member_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_member_tasks_status ON member_tasks(status)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_member(name, role=None, email=None, phone=None, department=None, skills=None, joined_at=None, notes=None):
    """Add team member"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO members (name, role, email, phone, department, skills, joined_at, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, role, email, phone, department, skills, joined_at, notes))

    member_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return member_id

def update_status(member_id, status):
    """Update member status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE members SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (status, member_id))

    conn.commit()
    conn.close()

def assign_task(member_id, task, due_date=None):
    """Assign task to member"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO member_tasks (member_id, task, due_date)
    VALUES (?, ?, ?)
    ''', (member_id, task, due_date))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return task_id

def complete_task(task_id):
    """Mark task as completed"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE member_tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (task_id,))

    conn.commit()
    conn.close()

def list_members(status=None, department=None, limit=50):
    """List team members"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, role, email, phone, department, status, skills, joined_at, created_at
    FROM members
    '''

    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)

    if department:
        conditions.append('department = ?')
        params.append(department)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY name ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    members = cursor.fetchall()
    conn.close()
    return members

def search_members(keyword):
    """Search team members"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, name, role, email, phone, department, status, skills, joined_at, created_at
    FROM members
    WHERE name LIKE ? OR role LIKE ? OR skills LIKE ?
    ORDER BY name ASC
    ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    members = cursor.fetchall()
    conn.close()
    return members

def get_member_tasks(member_id, status=None):
    """Get tasks for a member"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, task, status, due_date, created_at, completed_at
    FROM member_tasks
    WHERE member_id = ?
    '''

    params = [member_id]

    if status:
        query += ' AND status = ?'
        params.append(status)

    query += ' ORDER BY due_date ASC, created_at DESC'

    cursor.execute(query, params)
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_stats():
    """Get team statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM members')
    stats['total_members'] = cursor.fetchone()[0]

    for status in ['active', 'inactive', 'on_leave']:
        cursor.execute('SELECT COUNT(*) FROM members WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM member_tasks WHERE status = "pending"')
    stats['pending_tasks'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM member_tasks WHERE status = "completed"')
    stats['completed_tasks'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
