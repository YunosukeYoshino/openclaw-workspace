#!/usr/bin/env python3
"""
Shift Agent #27
- Shift scheduling
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "shifts.db"

def init_db():
    """Initialize database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT NOT NULL,
        shift_date DATE NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        role TEXT,
        status TEXT DEFAULT 'scheduled' CHECK(status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS shift_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_name TEXT NOT NULL,
        request_date DATE NOT NULL,
        request_type TEXT CHECK(request_type IN ('time_off', 'swap', 'extra')),
        reason TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'denied')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shifts_date ON shifts(shift_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shifts_member ON shifts(member_name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shifts_status ON shifts(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shift_requests_date ON shift_requests(request_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shift_requests_status ON shift_requests(status)')

    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_shift(member_name, shift_date, start_time, end_time, role=None, notes=None):
    """Add shift"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO shifts (member_name, shift_date, start_time, end_time, role, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (member_name, shift_date, start_time, end_time, role, notes))

    shift_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return shift_id

def update_shift_status(shift_id, status):
    """Update shift status"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE shifts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    ''', (status, shift_id))

    conn.commit()
    conn.close()

def request_time_off(member_name, request_date, reason=None):
    """Request time off"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO shift_requests (member_name, request_date, request_type, reason)
    VALUES (?, ?, 'time_off', ?)
    ''', (member_name, request_date, reason))

    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return request_id

def approve_request(request_id):
    """Approve request"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE shift_requests SET status = 'approved' WHERE id = ?
    ''', (request_id,))

    conn.commit()
    conn.close()

def deny_request(request_id):
    """Deny request"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    UPDATE shift_requests SET status = 'denied' WHERE id = ?
    ''', (request_id,))

    conn.commit()
    conn.close()

def list_shifts(date=None, member_name=None, status=None, limit=50):
    """List shifts"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, member_name, shift_date, start_time, end_time, role, status, notes, created_at
    FROM shifts
    '''

    params = []
    conditions = []

    if date:
        conditions.append('shift_date = ?')
        params.append(date)

    if member_name:
        conditions.append('member_name = ?')
        params.append(member_name)

    if status:
        conditions.append('status = ?')
        params.append(status)

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY shift_date ASC, start_time ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    shifts = cursor.fetchall()
    conn.close()
    return shifts

def list_requests(status=None, limit=20):
    """List shift requests"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, member_name, request_date, request_type, reason, status, created_at
    FROM shift_requests
    '''

    params = []

    if status:
        query += ' WHERE status = ?'
        params.append(status)

    query += ' ORDER BY created_at DESC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    requests = cursor.fetchall()
    conn.close()
    return requests

def get_shifts_by_date_range(start_date, end_date):
    """Get shifts within date range"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, member_name, shift_date, start_time, end_time, role, status, notes, created_at
    FROM shifts
    WHERE shift_date BETWEEN ? AND ?
    ORDER BY shift_date ASC, start_time ASC
    ''', (start_date, end_date))

    shifts = cursor.fetchall()
    conn.close()
    return shifts

def get_stats():
    """Get shift statistics"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    cursor.execute('SELECT COUNT(*) FROM shifts')
    stats['total_shifts'] = cursor.fetchone()[0]

    for status in ['scheduled', 'completed', 'cancelled', 'no_show']:
        cursor.execute('SELECT COUNT(*) FROM shifts WHERE status = ?', (status,))
        stats[status] = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM shift_requests WHERE status = "pending"')
    stats['pending_requests'] = cursor.fetchone()[0]

    conn.close()
    return stats

if __name__ == '__main__':
    init_db()
