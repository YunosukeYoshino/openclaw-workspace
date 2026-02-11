#!/usr/bin/env python3
"""
休暇管理エージェント #60
- 休暇・予定・ブッキング
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "holidays.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS holidays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        destination TEXT,
        start_date DATE,
        end_date DATE,
        days INTEGER,
        budget INTEGER,
        status TEXT DEFAULT 'planning' CHECK(status IN ('planning', 'booked', 'completed', 'cancelled')),
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        holiday_id INTEGER NOT NULL,
        type TEXT CHECK(type IN ('flight', 'hotel', 'car_rental', 'activity', 'other')),
        provider TEXT,
        cost INTEGER,
        currency TEXT DEFAULT 'JPY',
        booking_date DATE,
        confirmation_number TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (holiday_id) REFERENCES holidays(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_holidays_updated_at
    AFTER UPDATE ON holidays
    BEGIN
        UPDATE holidays SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_holidays_status ON holidays(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_holidays_start_date ON holidays(start_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookings_holiday_id ON bookings(holiday_id)')

    conn.commit()
    conn.close()

def add_holiday(title, destination=None, start_date=None, end_date=None, budget=None, status='planning', notes=None):
    if not start_date:
        start_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    days = None
    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1

    cursor.execute('''
    INSERT INTO holidays (title, destination, start_date, end_date, days, budget, status, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, destination, start_date, end_date, days, budget, status, notes))

    holiday_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return holiday_id

def add_booking(holiday_id, type, provider=None, cost=None, currency='JPY', booking_date=None, confirmation_number=None, notes=None):
    if not booking_date:
        booking_date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO bookings (holiday_id, type, provider, cost, currency, booking_date, confirmation_number, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (holiday_id, type, provider, cost, currency, booking_date, confirmation_number, notes))

    booking_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def update_holiday(holiday_id, title=None, destination=None, start_date=None, end_date=None, budget=None, status=None, notes=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if title:
        updates.append("title = ?")
        params.append(title)
    if destination:
        updates.append("destination = ?")
        params.append(destination)
    if start_date:
        updates.append("start_date = ?")
        params.append(start_date)
    if end_date:
        updates.append("end_date = ?")
        params.append(end_date)
        if budget is not None:
        updates.append("budget = ?")
        params.append(budget)
    if status:
        updates.append("status = ?")
        params.append(status)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        days = (end - start).days + 1
        updates.append("days = ?")
        params.append(days)

    if updates:
        query = f"UPDATE holidays SET {', '.join(updates)} WHERE id = ?"
        params.append(holiday_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def list_holidays(status=None, destination=None, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, title, destination, start_date, end_date, days, budget, status, notes, created_at
    FROM holidays
    '''

    params = []
    conditions = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if destination:
        conditions.append("destination LIKE ?")
        params.append(f"%{destination}%")

    if conditions:
        query += ' WHERE ' + ' AND '.join(conditions)

    query += ' ORDER BY start_date ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    holidays = cursor.fetchall()
    conn.close()
    return holidays

def list_bookings(holiday_id, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, holiday_id, type, provider, cost, currency, booking_date, confirmation_number, notes, created_at
    FROM bookings
    WHERE holiday_id = ?
    ORDER BY booking_date ASC
    LIMIT ?
    ''', (holiday_id, limit))

    bookings = cursor.fetchall()
    conn.close()
    return bookings

if __name__ == '__main__':
    init_db()
