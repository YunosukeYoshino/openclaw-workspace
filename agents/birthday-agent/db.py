#!/usr/bin/env python3
"""
誕生日管理エージェント #58
- 誕生日・ギフト・リマインダー
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "birthdays.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS birthdays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        birth_date DATE,
        year INTEGER,
        category TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS gifts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        birthday_id INTEGER NOT NULL,
        year INTEGER,
        gift TEXT,
        note TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (birthday_id) REFERENCES birthdays(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_birthdays_updated_at
    AFTER UPDATE ON birthdays
    BEGIN
        UPDATE birthdays SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_birthdays_name ON birthdays(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_birthdays_date ON birthdays(birth_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_gifts_birthday_id ON gifts(birthday_id)')

    conn.commit()
    conn.close()

def add_birthday(name, birth_date=None, year=None, category=None, notes=None):
    if not birth_date:
        birth_date = datetime.now().strftime("%m-%d")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO birthdays (name, birth_date, year, category, notes)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, birth_date, year, category, notes))

    birthday_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return birthday_id

def add_gift(birthday_id, year=None, gift=None, note=None):
    if not year:
        year = datetime.now().year

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO gifts (birthday_id, year, gift, note)
    VALUES (?, ?, ?, ?)
    ''', (birthday_id, year, gift, note))

    gift_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return gift_id

def update_birthday(birthday_id, name=None, birth_date=None, year=None, category=None, notes=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    updates = []
    params = []

    if name:
        updates.append("name = ?")
        params.append(name)
    if birth_date:
        updates.append("birth_date = ?")
        params.append(birth_date)
    if year:
        updates.append("year = ?")
        params.append(year)
    if category:
        updates.append("category = ?")
        params.append(category)
    if notes:
        updates.append("notes = ?")
        params.append(notes)

    if updates:
        query = f"UPDATE birthdays SET {', '.join(updates)} WHERE id = ?"
        params.append(birthday_id)
        cursor.execute(query, params)
        conn.commit()

    conn.close()

def list_birthdays(month=None, limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = 'SELECT id, name, birth_date, year, category, notes, created_at FROM birthdays'

    params = []
    if month:
        query += ' WHERE strftime("%m", birth_date) = ?'
        params.append(month)

    query += ' ORDER BY strftime("%m-%d", birth_date) ASC LIMIT ?'
    params.append(limit)

    cursor.execute(query, params)
    birthdays = cursor.fetchall()
    conn.close()
    return birthdays

def get_upcoming(days=30):
    today = datetime.now()
    target = (today.replace(day=1) + timedelta(days=90)).replace(day=1)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''
    SELECT id, name, birth_date, year, category, notes, created_at
    FROM birthdays
    WHERE DATE(substr('0000', 1, 4) || '-' || birth_date, '-01') >= DATE('now') AND DATE(substr('0000', 1, 4) || '-' || birth_date, '-01') <= DATE(?, '+90 days')
    ORDER BY DATE(substr('0000', 1, 4) || '-' || birth_date, '-01')
    LIMIT ?
    '''

    cursor.execute(query, (today.strftime("%Y-%m-%d"), days))
    birthdays = cursor.fetchall()
    conn.close()
    return birthdays

def get_gifts(birthday_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, birthday_id, year, gift, note, created_at
    FROM gifts
    WHERE birthday_id = ?
    ORDER BY year DESC
    ''', (birthday_id,))

    gifts = cursor.fetchall()
    conn.close()
    return gifts

if __name__ == '__main__':
    init_db()
