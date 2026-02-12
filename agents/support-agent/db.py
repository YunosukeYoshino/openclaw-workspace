#!/usr/bin/env python3
"""
Support Agent - Database Management
Customer Support Inquiry, FAQ, and Ticket Tracking
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "support.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Support tickets table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        subject TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'open' CHECK(status IN ('open','in_progress','resolved','closed')),
        priority TEXT DEFAULT 'normal' CHECK(priority IN ('low','normal','high','urgent')),
        category TEXT,
        assigned_to TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP
    )
    ''')

    # FAQ table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS faqs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        category TEXT,
        keywords TEXT,
        views INTEGER DEFAULT 0,
        helpful_count INTEGER DEFAULT 0,
        not_helpful_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Ticket responses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ticket_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL,
        responder TEXT NOT NULL,
        message TEXT NOT NULL,
        is_internal BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_status ON tickets(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_user ON tickets(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_tickets_priority ON tickets(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_faqs_category ON faqs(category)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_responses_ticket ON ticket_responses(ticket_id)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def create_ticket(user_id, subject, description, category=None, priority='normal'):
    """Create a new support ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO tickets (user_id, subject, description, category, priority)
    VALUES (?, ?, ?, ?, ?)
    ''', (user_id, subject, description, category, priority))

    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return ticket_id

def update_ticket(ticket_id, status=None, priority=None, assigned_to=None):
    """Update ticket status or details"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if status:
        updates.append("status = ?")
        params.append(status)
        if status == 'resolved':
            updates.append("resolved_at = ?")
            params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    if priority:
        updates.append("priority = ?")
        params.append(priority)

    if assigned_to:
        updates.append("assigned_to = ?")
        params.append(assigned_to)

    if updates:
        updates.append("updated_at = ?")
        params.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        params.append(ticket_id)

        query = f"UPDATE tickets SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def add_response(ticket_id, responder, message, is_internal=False):
    """Add a response to a ticket"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO ticket_responses (ticket_id, responder, message, is_internal)
    VALUES (?, ?, ?, ?)
    ''', (ticket_id, responder, message, is_internal))

    response_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return response_id

def get_ticket(ticket_id):
    """Get ticket details with responses"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tickets WHERE id = ?', (ticket_id,))
    ticket = cursor.fetchone()

    responses = []
    if ticket:
        cursor.execute('''
        SELECT responder, message, is_internal, created_at
        FROM ticket_responses WHERE ticket_id = ? ORDER BY created_at
        ''', (ticket_id,))
        responses = cursor.fetchall()

    conn.close()
    return ticket, responses

def list_tickets(status=None, priority=None, user_id=None, limit=10):
    """List tickets with filters"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, user_id, subject, status, priority, created_at FROM tickets WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)

    if priority:
        query += ' AND priority = ?'
        params.append(priority)

    if user_id:
        query += ' AND user_id = ?'
        params.append(user_id)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    tickets = cursor.fetchall()
    conn.close()
    return tickets

def add_faq(question, answer, category=None, keywords=None):
    """Add a new FAQ entry"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO faqs (question, answer, category, keywords)
    VALUES (?, ?, ?, ?)
    ''', (question, answer, category, keywords))

    faq_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return faq_id

def search_faqs(keyword, category=None):
    """Search FAQs by keyword or category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if category:
        cursor.execute('''
        SELECT id, question, answer, category FROM faqs
        WHERE category = ? AND (question LIKE ? OR answer LIKE ? OR keywords LIKE ?)
        ORDER BY helpful_count DESC
        ''', (category, f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))
    else:
        cursor.execute('''
        SELECT id, question, answer, category FROM faqs
        WHERE question LIKE ? OR answer LIKE ? OR keywords LIKE ?
        ORDER BY helpful_count DESC LIMIT 10
        ''', (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%'))

    faqs = cursor.fetchall()
    conn.close()
    return faqs

def rate_faq(faq_id, helpful):
    """Rate an FAQ as helpful or not"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if helpful:
        cursor.execute('UPDATE faqs SET helpful_count = helpful_count + 1 WHERE id = ?', (faq_id,))
    else:
        cursor.execute('UPDATE faqs SET not_helpful_count = not_helpful_count + 1 WHERE id = ?', (faq_id,))

    conn.commit()
    conn.close()

def get_stats():
    """Get support statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ticket counts by status
    cursor.execute('SELECT status, COUNT(*) FROM tickets GROUP BY status')
    status_counts = dict(cursor.fetchall())

    # Ticket counts by priority
    cursor.execute('SELECT priority, COUNT(*) FROM tickets GROUP BY priority')
    priority_counts = dict(cursor.fetchall())

    # FAQ stats
    cursor.execute('SELECT COUNT(*) FROM faqs')
    total_faqs = cursor.fetchone()[0]

    # Average resolution time (simplified)
    cursor.execute('''
    SELECT AVG(CASE WHEN resolved_at IS NOT NULL THEN
        julianday(resolved_at) - julianday(created_at) END) FROM tickets WHERE resolved_at IS NOT NULL
    ''')
    avg_resolution = cursor.fetchone()[0]

    conn.close()
    return {
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'total_faqs': total_faqs,
        'avg_resolution_days': avg_resolution
    }

if __name__ == '__main__':
    init_db()
