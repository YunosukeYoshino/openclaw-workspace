#!/usr/bin/env python3
"""
Ticket Agent #23
- Support ticket management
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "tickets.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        priority INTEGER DEFAULT 1 CHECK(priority IN (1,2,3,4,5)),
        status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved', 'closed')),
        assignee TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        closed_at TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ticket_comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        comment TEXT NOT NULL,
        author TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_category ON tickets(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ticket_comments_ticket ON ticket_comments(ticket_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_ticket(title, description=None, category=None, priority=1):
    """Add new ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tickets (title, description, category, priority)
    VALUES (?, ?, ?, ?)
    ''', (title, description, category, priority))

    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def add_comment(ticket_id, comment, author=None):
    """Add comment to ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO ticket_comments (ticket_id, comment, author)
    VALUES (?, ?, ?)
    ''', (ticket_id, comment, author))

    conn.commit()
    conn.close()

def update_status(ticket_id, status):
    """Update ticket status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if status == 'resolved':
        cursor.execute('''
        UPDATE tickets SET status = ?, resolved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (status, ticket_id))
    elif status == 'closed':
        cursor.execute('''
        UPDATE tickets SET status = ?, closed_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (status, ticket_id))
    else:
        cursor.execute('''
        UPDATE tickets SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
        ''', (status, ticket_id))

    conn.commit()
    conn.close()

def assign_ticket(ticket_id, assignee):
    """Assign ticket to someone"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE tickets SET assignee = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (assignee, ticket_id))

    conn.commit()
    conn.close()

def list_tickets(status=None, category=None, assignee=None, limit=20):
    """List tickets"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, description, category, priority, status, assignee, created_at, updated_at
    FROM tickets
    '''

    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)

    if category:
        conditions.append('category = ?')
        params.append(category)

    if assignee:
        conditions.append('assignee = ?')
        params.append(assignee)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY priority DESC, created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    tickets = cursor.fetchall()
    conn.close()
    return tickets

def search_tickets(keyword):
    """Search tickets"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, description, category, priority, status, assignee, created_at, updated_at
    FROM tickets
    WHERE title LIKE ? OR description LIKE ?
    ORDER BY priority DESC, created_at DESC
    ''', (f'%{keyword}%', f'%{keyword}%'))

    tickets = cursor.fetchall()
    conn.close()
    return tickets

def get_ticket_comments(ticket_id):
    """Get comments for a ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, comment, author, created_at
    FROM ticket_comments
    WHERE ticket_id = ?
    ORDER BY created_at ASC
    ''', (ticket_id,))

    comments = cursor.fetchall()
    conn.close()
    return comments

def get_stats():
    """Get statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM tickets')
    stats['total'] = cursor.fetchone()[0]

    for status in ['open', 'in_progress', 'resolved', 'closed']:
        cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
