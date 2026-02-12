#!/usr/bin/env python3
"""
Debug Agent - Database Management
Debug sessions and issues management
"""

import sqlite3
from pathlib import Path
from datetime import datetime
import json

DB_PATH = Path(__file__).parent / "debug.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Debug sessions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active' CHECK(status IN ('active','paused','completed','abandoned')),
        priority TEXT DEFAULT 'normal' CHECK(priority IN ('low','normal','high','critical')),
        component TEXT,
        assignee TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        started_at TIMESTAMP,
        completed_at TIMESTAMP
    )
    ''')

    # Issues table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        title TEXT NOT NULL,
        description TEXT,
        severity TEXT CHECK(severity IN ('info','minor','major','critical')),
        category TEXT,
        status TEXT DEFAULT 'open' CHECK(status IN ('open','investigating','resolved','closed','reopened')),
        stack_trace TEXT,
        error_code TEXT,
        environment TEXT,
        reproduction_steps TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id)
    )
    ''')

    # Debug notes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        issue_id INTEGER,
        author TEXT,
        content TEXT NOT NULL,
        note_type TEXT DEFAULT 'general' CHECK(note_type IN ('general','hypothesis','solution','observation','question')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (issue_id) REFERENCES issues(id)
    )
    ''')

    # Solutions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS solutions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        issue_id INTEGER,
        description TEXT NOT NULL,
        code_diff TEXT,
        files_modified TEXT,
        verified BOOLEAN DEFAULT 0,
        verified_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (issue_id) REFERENCES issues(id)
    )
    ''')

    # Resources table (logs, screenshots, etc.)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER,
        issue_id INTEGER,
        resource_type TEXT NOT NULL CHECK(resource_type IN ('log','screenshot','video','code','config','other')),
        file_path TEXT,
        url TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (issue_id) REFERENCES issues(id)
    )
    ''')

    # Time tracking table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS time_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        issue_id INTEGER,
        started_at TIMESTAMP NOT NULL,
        ended_at TIMESTAMP,
        duration_minutes INTEGER,
        notes TEXT,
        FOREIGN KEY (session_id) REFERENCES sessions(id),
        FOREIGN KEY (issue_id) REFERENCES issues(id)
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_sessions_priority ON sessions(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_session ON issues(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_issues_status ON issues(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notes_session ON notes(session_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_solutions_issue ON solutions(issue_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_resources_session ON resources(session_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_session(title, description=None, component=None, priority='normal', assignee=None):
    """Create a new debug session"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO sessions (title, description, component, priority, assignee, started_at)
    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    ''', (title, description, component, priority, assignee))

    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    return session_id

def get_session(session_id):
    """Get session by ID"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    session = cursor.fetchone()
    conn.close()
    return dict(session) if session else None

def list_sessions(status=None, priority=None, limit=20):
    """List sessions with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM sessions WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)
    if priority:
        query += ' AND priority = ?'
        params.append(priority)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return sessions

def update_session_status(session_id, status):
    """Update session status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    update_time = 'completed_at = CURRENT_TIMESTAMP' if status == 'completed' else 'updated_at = CURRENT_TIMESTAMP'
    cursor.execute(f'UPDATE sessions SET status = ?, {update_time} WHERE id = ?', (status, session_id))

    conn.commit()
    conn.close()

def create_issue(session_id, title, description=None, severity='major', category=None, stack_trace=None, error_code=None):
    """Create a new issue"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO issues (session_id, title, description, severity, category, stack_trace, error_code)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (session_id, title, description, severity, category, stack_trace, error_code))

    conn.commit()
    issue_id = cursor.lastrowid
    conn.close()
    return issue_id

def get_issues(session_id=None, status=None, severity=None, limit=20):
    """Get issues with optional filters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM issues WHERE 1=1'
    params = []

    if session_id:
        query += ' AND session_id = ?'
        params.append(session_id)
    if status:
        query += ' AND status = ?'
        params.append(status)
    if severity:
        query += ' AND severity = ?'
        params.append(severity)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    issues = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return issues

def update_issue_status(issue_id, status):
    """Update issue status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    update_time = 'resolved_at = CURRENT_TIMESTAMP' if status in ('resolved', 'closed') else 'updated_at = CURRENT_TIMESTAMP'
    cursor.execute(f'UPDATE issues SET status = ?, {update_time} WHERE id = ?', (status, issue_id))

    conn.commit()
    conn.close()

def add_note(session_id, content, issue_id=None, author=None, note_type='general'):
    """Add a debug note"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO notes (session_id, issue_id, author, content, note_type)
    VALUES (?, ?, ?, ?, ?)
    ''', (session_id, issue_id, author, content, note_type))

    conn.commit()
    conn.close()

def get_notes(session_id=None, issue_id=None, limit=50):
    """Get notes for session or issue"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if issue_id:
        cursor.execute('SELECT * FROM notes WHERE issue_id = ? ORDER BY created_at DESC LIMIT ?', (issue_id, limit))
    elif session_id:
        cursor.execute('SELECT * FROM notes WHERE session_id = ? ORDER BY created_at DESC LIMIT ?', (session_id, limit))
    else:
        cursor.execute('SELECT * FROM notes ORDER BY created_at DESC LIMIT ?', (limit,))

    notes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return notes

def create_solution(session_id, issue_id, description, code_diff=None, files_modified=None):
    """Create a solution"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    files_json = json.dumps(files_modified) if files_modified else None
    cursor.execute('''
    INSERT INTO solutions (session_id, issue_id, description, code_diff, files_modified)
    VALUES (?, ?, ?, ?, ?)
    ''', (session_id, issue_id, description, code_diff, files_json))

    conn.commit()
    conn.close()

def get_solutions(issue_id=None, verified=None, limit=20):
    """Get solutions"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM solutions WHERE 1=1'
    params = []

    if issue_id:
        query += ' AND issue_id = ?'
        params.append(issue_id)
    if verified is not None:
        query += ' AND verified = ?'
        params.append(verified)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    solutions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return solutions

def verify_solution(solution_id):
    """Mark solution as verified"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE solutions
    SET verified = 1, verified_at = CURRENT_TIMESTAMP
    WHERE id = ?
    ''', (solution_id,))

    conn.commit()
    conn.close()

def add_resource(session_id, resource_type, description=None, file_path=None, url=None, issue_id=None):
    """Add a debug resource"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO resources (session_id, issue_id, resource_type, file_path, url, description)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (session_id, issue_id, resource_type, file_path, url, description))

    conn.commit()
    conn.close()

def get_resources(session_id=None, issue_id=None, resource_type=None, limit=20):
    """Get resources"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM resources WHERE 1=1'
    params = []

    if session_id:
        query += ' AND session_id = ?'
        params.append(session_id)
    if issue_id:
        query += ' AND issue_id = ?'
        params.append(issue_id)
    if resource_type:
        query += ' AND resource_type = ?'
        params.append(resource_type)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    resources = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return resources

def start_time_entry(session_id, issue_id=None):
    """Start a time entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO time_entries (session_id, issue_id, started_at)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ''', (session_id, issue_id))

    conn.commit()
    entry_id = cursor.lastrowid
    conn.close()
    return entry_id

def end_time_entry(entry_id, notes=None):
    """End a time entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE time_entries
    SET ended_at = CURRENT_TIMESTAMP,
        duration_minutes = CAST((julianday(CURRENT_TIMESTAMP) - julianday(started_at)) * 24 * 60 AS INTEGER),
        notes = ?
    WHERE id = ?
    ''', (notes, entry_id))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
