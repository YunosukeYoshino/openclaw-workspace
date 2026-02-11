#!/usr/bin/env python3
"""
Social Media Agent - Database Management
Supports Japanese and English
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "social.db"

def init_db():
    """データベース初期化 / Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Posts table (投稿管理)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        content TEXT NOT NULL,
        status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'scheduled', 'posted', 'cancelled')),
        scheduled_time TIMESTAMP,
        posted_time TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Notifications table (通知管理)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        content TEXT NOT NULL,
        notification_type TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Connected accounts table (連携アカウント)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        platform TEXT NOT NULL,
        account_name TEXT NOT NULL,
        account_id TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indices
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_status ON posts(status, scheduled_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_posts_platform ON posts(platform)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_platform ON notifications(platform)')

    conn.commit()
    conn.close()
    print("✅ Database initialized / データベース初期化完了")

def add_post(platform, content, scheduled_time=None):
    """投稿を追加 / Add post"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO posts (platform, content, scheduled_time)
    VALUES (?, ?, ?)
    ''', (platform.lower(), content, scheduled_time))

    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def list_posts(status=None, platform=None):
    """投稿一覧 / List posts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, platform, content, status, scheduled_time, posted_time, created_at FROM posts'
    params = []
    conditions = []

    if status:
        conditions.append('status = ?')
        params.append(status)

    if platform:
        conditions.append('platform = ?')
        params.append(platform.lower())

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY created_at DESC'

    cursor.execute(query, params)
    posts = cursor.fetchall()
    conn.close()
    return posts

def update_post_status(post_id, status):
    """投稿ステータスを更新 / Update post status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    update_data = {'status': status}
    if status == 'posted':
        update_data['posted_time'] = datetime.now().strftime("%Y-%m-%d %H:%M")

    set_clause = ', '.join([f'{k} = ?' for k in update_data.keys()])
    params = list(update_data.values()) + [post_id]

    cursor.execute(f'UPDATE posts SET {set_clause} WHERE id = ?', params)
    conn.commit()
    conn.close()

def add_notification(platform, content, notification_type):
    """通知を追加 / Add notification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO notifications (platform, content, notification_type)
    VALUES (?, ?, ?)
    ''', (platform.lower(), content, notification_type))

    notification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return notification_id

def list_notifications(is_read=None, platform=None):
    """通知一覧 / List notifications"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, platform, content, notification_type, is_read, timestamp FROM notifications'
    params = []
    conditions = []

    if is_read is not None:
        conditions.append('is_read = ?')
        params.append(1 if is_read else 0)

    if platform:
        conditions.append('platform = ?')
        params.append(platform.lower())

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY timestamp DESC'

    cursor.execute(query, params)
    notifications = cursor.fetchall()
    conn.close()
    return notifications

def mark_notification_read(notification_id):
    """通知を既読にする / Mark notification as read"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notification_id,))
    conn.commit()
    conn.close()

def add_account(platform, account_name, account_id=None):
    """アカウントを追加 / Add account"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO accounts (platform, account_name, account_id)
    VALUES (?, ?, ?)
    ''', (platform.lower(), account_name, account_id))

    account_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return account_id

def list_accounts():
    """アカウント一覧 / List accounts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, platform, account_name, account_id, is_active, created_at
    FROM accounts
    ORDER BY platform, created_at
    ''')

    accounts = cursor.fetchall()
    conn.close()
    return accounts

def get_unread_count():
    """未読通知数を取得 / Get unread count"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM notifications WHERE is_read = 0')
    count = cursor.fetchone()[0]
    conn.close()
    return count

if __name__ == '__main__':
    init_db()
