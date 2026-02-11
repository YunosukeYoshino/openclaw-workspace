#!/usr/bin/env python3
"""
イベント管理エージェント #57
- イベント・招待・RSVP
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "events.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        location TEXT,
        start_date DATE,
        start_time TIME,
        end_date DATE,
        end_time TIME,
        category TEXT,
        status TEXT DEFAULT 'upcoming' CHECK(status IN ('upcoming', 'ongoing', 'completed', 'cancelled')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS invitations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_id INTEGER NOT NULL,
        guest_name TEXT,
        email TEXT,
        rsvp_status TEXT CHECK(rsvp_status IN ('pending', 'accepted', 'declined', 'tentative')),
        responded_at DATE,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_events_updated_at
    AFTER UPDATE ON events
    BEGIN
        UPDATE events SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_status ON events(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_start_date ON events(start_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_invitations_event_id ON invitations(event_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_invitations_rsvp ON invitations(rsvp_status)')

    conn.commit()
    conn.close()

def add_event(title, description=None, location=None, start_date=None, start_time=None, end_date=None, end_time=None, category=None, notes=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO events (title, description, location, start_date, start_time, end_date, end_time, category, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, description, location, start_date, start_time, end_date, end_time, category, notes))

    event_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return event_id

def update_event(event_id, status=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if status:
        cursor.execute('UPDATE events SET status = ? WHERE id = ?', (status, event_id))
        conn.commit()

    conn.close()

def add_invitation(event_id, guest_name=None, email=None, rsvp_status='pending', notes=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO invitations (event_id, guest_name, email, rsvp_status, notes)
    VALUES (?, ?, ?, ?, ?)
    ''', (event_id, guest_name, email, rsvp_status, notes))

    invite_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return invite_id

def update_rsvp(invite_id, rsvp_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE invitations
    SET rsvp_status = ?, responded_at = ?
    WHERE id = ?
    ''', (rsvp_status, datetime.now().strftime("%Y-%m-%d"), invite_id))
    conn.commit()
    conn.close()

def list_events(status=None, date_from=None, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, title, description, location, start_date, start_time, end_date, end_time, category, status, notes, created_at FROM events'

    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if date_from:
        conditions.append("start_date >= ?")
        params.append(date_from)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY start_date ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    events = cursor.fetchall()
    conn.close()
    return events

def list_invitations(event_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, event_id, guest_name, email, rsvp_status, responded_at, notes, created_at
    FROM invitations
    WHERE event_id = ?
    ORDER BY guest_name
    ''', (event_id,))

    invites = cursor.fetchall()
    conn.close()
    return invites

if __name__ == '__main__':
    init_db()
