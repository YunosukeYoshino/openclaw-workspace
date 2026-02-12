#!/usr/bin/env python3
"""
Email Agent - Database Management
Supports Japanese and English
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "email.db"

def init_db():
    """データベース初期化 / Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Emails table (メール管理)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS emails (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT,
        is_read INTEGER DEFAULT 0,
        is_important INTEGER DEFAULT 0,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Auto-reply rules table (自動返信ルール)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS auto_replies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_name TEXT NOT NULL,
        trigger_keyword TEXT NOT NULL,
        reply_message TEXT NOT NULL,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Contacts table (連絡先)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        name TEXT,
        is_important INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_read ON emails(is_read)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_important ON emails(is_important)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_emails_sender ON emails(sender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_contacts_email ON contacts(email)')

    conn.commit()
    conn.close()
    print("✅ Database initialized / データベース初期化完了")

def add_email(sender, subject, body=None, is_important=False):
    """メールを追加 / Add email"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO emails (sender, subject, body, is_important)
    VALUES (?, ?, ?, ?)
    ''', (sender, subject, body, 1 if is_important else 0))

    email_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return email_id

def list_emails(is_read=None, is_important=None, limit=20):
    """メール一覧 / List emails"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, sender, subject, body, is_read, is_important, received_at FROM emails'
    params = []
    conditions = []

    if is_read is not None:
        conditions.append('is_read = ?')
        params.append(1 if is_read else 0)

    if is_important is not None:
        conditions.append('is_important = ?')
        params.append(1 if is_important else 0)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY received_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    emails = cursor.fetchall()
    conn.close()
    return emails

def mark_read(email_id):
    """メールを既読にする / Mark email as read"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE emails SET is_read = 1 WHERE id = ?', (email_id,))
    conn.commit()
    conn.close()

def mark_important(email_id):
    """メールを重要にマーク / Mark email as important"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE emails SET is_important = 1 WHERE id = ?', (email_id,))
    conn.commit()
    conn.close()

def add_contact(email, name=None, is_important=False):
    """連絡先を追加 / Add contact"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO contacts (email, name, is_important)
        VALUES (?, ?, ?)
        ''', (email, name, 1 if is_important else 0))

        contact_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return contact_id
    except sqlite3.IntegrityError:
        conn.close()
        return None

def list_contacts():
    """連絡先一覧 / List contacts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, email, name, is_important, created_at
    FROM contacts
    ORDER BY name, email
    ''')

    contacts = cursor.fetchall()
    conn.close()
    return contacts

def add_auto_reply(rule_name, trigger_keyword, reply_message):
    """自動返信ルールを追加 / Add auto-reply rule"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO auto_replies (rule_name, trigger_keyword, reply_message)
    VALUES (?, ?, ?)
    ''', (rule_name, trigger_keyword, reply_message))

    rule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rule_id

def list_auto_replies(is_active=True):
    """自動返信ルール一覧 / List auto-reply rules"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, rule_name, trigger_keyword, reply_message, is_active, created_at
    FROM auto_replies
    WHERE is_active = ?
    ORDER BY rule_name
    ''', (1 if is_active else 0,))

    rules = cursor.fetchall()
    conn.close()
    return rules

def get_unread_count():
    """未読メール数を取得 / Get unread count"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM emails WHERE is_read = 0')
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_important_unread():
    """重要な未読メールを取得 / Get important unread emails"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, sender, subject, body, is_read, is_important, received_at
    FROM emails
    WHERE is_read = 0 AND is_important = 1
    ORDER BY received_at DESC
    ''')

    emails = cursor.fetchall()
    conn.close()
    return emails

if __name__ == '__main__':
    init_db()
