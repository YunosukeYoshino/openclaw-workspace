#!/usr/bin/env python3
"""
Communication Agent #28
- Message history
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "communication.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        recipient TEXT,
        channel TEXT,
        content TEXT NOT NULL,
        message_type TEXT DEFAULT 'text' CHECK(message_type IN ('text', 'image', 'file', 'voice')),
        direction TEXT CHECK(direction IN ('inbound', 'outbound')),
        status TEXT DEFAULT 'sent' CHECK(status IN ('sent', 'delivered', 'read', 'failed')),
        tags TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        participant TEXT NOT NULL,
        topic TEXT,
        last_message_date TIMESTAMP,
        message_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'archived', 'closed')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_recipient ON messages(recipient)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_participant ON conversations(participant)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(status)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_message(sender, content, recipient=None, channel=None, message_type='text', direction=None, tags=None, notes=None):
    """Add message"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO messages (sender, content, recipient, channel, message_type, direction, tags, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (sender, content, recipient, channel, message_type, direction, tags, notes))

    message_id = cursor.lastrowid

    # Update or create conversation
    participant = recipient if direction == 'outbound' else sender
    cursor.execute('''
    INSERT OR IGNORE INTO conversations (participant, last_message_date, message_count)
    VALUES (?, CURRENT_TIMESTAMP, 0)
    ''', (participant,))

    cursor.execute('''
    UPDATE conversations SET
        last_message_date = CURRENT_TIMESTAMP,
        message_count = message_count + 1,
        updated_at = CURRENT_TIMESTAMP
    WHERE participant = ?
    ''', (participant,))

    conn.commit()
    conn.close()
    return message_id

def list_messages(sender=None, recipient=None, channel=None, limit=50):
    """List messages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, sender, recipient, channel, content, message_type, direction, status, tags, created_at
    FROM messages
    '''

    params = []
    conditions = []

    if sender:
        conditions.append('sender = ?')
        params.append(sender)

    if recipient:
        conditions.append('recipient = ?')
        params.append(recipient)

    if channel:
        conditions.append('channel = ?')
        params.append(channel)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    messages = cursor.fetchall()
    conn.close()
    return messages

def search_messages(keyword, limit=50):
    """Search messages"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, sender, recipient, channel, content, message_type, direction, status, tags, created_at
    FROM messages
    WHERE content LIKE ? OR tags LIKE ?
    ORDER BY created_at DESC LIMIT ?
    ''', (f'%{keyword}%', f'%{keyword}%', limit))

    messages = cursor.fetchall()
    conn.close()
    return messages

def list_conversations(status=None, limit=20):
    """List conversations"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, participant, topic, last_message_date, message_count, status, notes, created_at
    FROM conversations
    '''

    params = []

    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY last_message_date DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    conversations = cursor.fetchall()
    conn.close()
    return conversations

def get_conversation_messages(participant, limit=50):
    """Get messages for conversation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, sender, recipient, channel, content, message_type, direction, status, tags, created_at
    FROM messages
    WHERE sender = ? OR recipient = ?
    ORDER BY created_at DESC LIMIT ?
    ''', (participant, participant, limit))

    messages = cursor.fetchall()
    conn.close()
    return messages

def archive_conversation(participant):
    """Archive conversation"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE conversations SET status = 'archived', updated_at = CURRENT_TIMESTAMP WHERE participant = ?
    ''', (participant,))

    conn.commit()
    conn.close()

def get_stats():
    """Get communication statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM messages')
    stats['total_messages'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM conversations')
    stats['total_conversations'] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM conversations WHERE status = "active"')
    stats['active_conversations'] = cursor.fetchone()[0]

    for direction in ['inbound', 'outbound']:
        cursor.execute('SELECT COUNT(*) FROM messages WHERE direction = ?', (direction,))
        stats[direction] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
