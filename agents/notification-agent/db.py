#!/usr/bin/env python3
"""
Notification Agent - Database Management
Aggregate, manage, and filter notifications
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "notification.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Notifications table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT,
        type TEXT NOT NULL CHECK(type IN ('info','warning','error','success','reminder')),
        priority TEXT DEFAULT 'normal' CHECK(priority IN ('low','normal','high','urgent')),
        status TEXT DEFAULT 'unread' CHECK(status IN ('unread','read','archived','dismissed')),
        target_user TEXT,
        scheduled_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        read_at TIMESTAMP,
        expires_at TIMESTAMP
    )
    ''')

    # Notification schedules table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        schedule_type TEXT NOT NULL CHECK(schedule_type IN ('daily','weekly','monthly','cron')),
        schedule_value TEXT,
        notification_template TEXT,
        priority TEXT DEFAULT 'normal',
        active BOOLEAN DEFAULT 1,
        last_run TIMESTAMP,
        next_run TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Notification rules table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS rules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        condition_type TEXT NOT NULL CHECK(condition_type IN ('source','type','priority','keyword')),
        condition_value TEXT,
        action TEXT NOT NULL CHECK(action IN ('block','promote','demote','forward','auto_read')),
        action_value TEXT,
        active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Indexes
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_priority ON notifications(priority)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(target_user)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON notifications(scheduled_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_schedules_active ON schedules(active)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_notification(source, title, message, type='info', priority='normal', target_user=None, scheduled_at=None, expires_at=None):
    """Add a new notification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO notifications (source, title, message, type, priority, target_user, scheduled_at, expires_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (source, title, message, type, priority, target_user, scheduled_at, expires_at))

    notification_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return notification_id

def mark_read(notification_id):
    """Mark notification as read"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE notifications SET status = 'read', read_at = ?
    WHERE id = ?
    ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), notification_id))

    conn.commit()
    conn.close()

def mark_all_read(user_id=None):
    """Mark all notifications as read (optionally for specific user)"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if user_id:
        cursor.execute('''
        UPDATE notifications SET status = 'read', read_at = ?
        WHERE status = 'unread' AND target_user = ?
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), user_id))
    else:
        cursor.execute('''
        UPDATE notifications SET status = 'read', read_at = ?
        WHERE status = 'unread'
        ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),))

    conn.commit()
    conn.close()

def archive_notification(notification_id):
    """Archive notification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE notifications SET status = 'archived' WHERE id = ?", (notification_id,))

    conn.commit()
    conn.close()

def dismiss_notification(notification_id):
    """Dismiss notification"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("UPDATE notifications SET status = 'dismissed' WHERE id = ?", (notification_id,))

    conn.commit()
    conn.close()

def get_notifications(status=None, priority=None, type=None, user_id=None, limit=20):
    """Get notifications with filters"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, source, title, message, type, priority, status, created_at FROM notifications WHERE 1=1'
    params = []

    if status:
        query += ' AND status = ?'
        params.append(status)

    if priority:
        query += ' AND priority = ?'
        params.append(priority)

    if type:
        query += ' AND type = ?'
        params.append(type)

    if user_id:
        query += ' AND (target_user = ? OR target_user IS NULL)'
        params.append(user_id)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    notifications = cursor.fetchall()
    conn.close()
    return notifications

def create_schedule(name, schedule_type, schedule_value, notification_template, priority='normal', active=True):
    """Create a notification schedule"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO schedules (name, schedule_type, schedule_value, notification_template, priority, active)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, schedule_type, schedule_value, notification_template, priority, 1 if active else 0))

    schedule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return schedule_id

def get_schedules(active_only=True):
    """Get schedules"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if active_only:
        cursor.execute('''
        SELECT id, name, schedule_type, schedule_value, priority, next_run
        FROM schedules WHERE active = 1 ORDER BY next_run
        ''')
    else:
        cursor.execute('SELECT id, name, schedule_type, schedule_value, priority, active FROM schedules')

    schedules = cursor.fetchall()
    conn.close()
    return schedules

def create_rule(name, condition_type, condition_value, action, action_value=None, active=True):
    """Create a notification rule"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO rules (name, condition_type, condition_value, action, action_value, active)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, condition_type, condition_value, action, action_value, 1 if active else 0))

    rule_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rule_id

def apply_rules(notification):
    """Apply rules to a notification and return modified priority or action"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('SELECT condition_type, condition_value, action, action_value FROM rules WHERE active = 1')
    rules = cursor.fetchall()

    actions = []

    for rule in rules:
        cond_type, cond_value, action, action_value = rule

        match = False
        if cond_type == 'source' and notification.get('source') == cond_value:
            match = True
        elif cond_type == 'type' and notification.get('type') == cond_value:
            match = True
        elif cond_type == 'priority' and notification.get('priority') == cond_value:
            match = True
        elif cond_type == 'keyword' and cond_value.lower() in str(notification.get('message', '')).lower():
            match = True

        if match:
            if action == 'promote':
                # Increase priority
                current = notification.get('priority', 'normal')
                priority_order = ['low', 'normal', 'high', 'urgent']
                try:
                    idx = priority_order.index(current)
                    if idx < len(priority_order) - 1:
                        actions.append(('priority', priority_order[idx + 1]))
                except:
                    pass
            elif action == 'demote':
                current = notification.get('priority', 'normal')
                priority_order = ['low', 'normal', 'high', 'urgent']
                try:
                    idx = priority_order.index(current)
                    if idx > 0:
                        actions.append(('priority', priority_order[idx - 1]))
                except:
                    pass
            elif action == 'block':
                actions.append(('block', True))
            elif action == 'forward' and action_value:
                actions.append(('forward', action_value))

    conn.close()
    return actions

def get_stats():
    """Get notification statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Count by status
    cursor.execute('SELECT status, COUNT(*) FROM notifications GROUP BY status')
    status_counts = dict(cursor.fetchall())

    # Count by priority
    cursor.execute('SELECT priority, COUNT(*) FROM notifications WHERE status = "unread" GROUP BY priority')
    priority_counts = dict(cursor.fetchall())

    # Count by type
    cursor.execute('SELECT type, COUNT(*) FROM notifications GROUP BY type')
    type_counts = dict(cursor.fetchall())

    conn.close()

    return {
        'status_counts': status_counts,
        'priority_counts': priority_counts,
        'type_counts': type_counts
    }

if __name__ == '__main__':
    init_db()
