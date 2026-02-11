#!/usr/bin/env python3
"""
記念日管理エージェント #59
- 記念日・祝い・記録
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "anniversaries.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS anniversaries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date DATE,
        type TEXT CHECK(type IN ('wedding', 'dating', 'work', 'other')),
        description TEXT,
        partner TEXT,
        location TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS celebrations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        anniversary_id INTEGER NOT NULL,
        year INTEGER,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (anniversary_id) REFERENCES anniversaries(id) ON DELETE CASCADE
    )
    ''')

    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS update_anniversaries_updated_at
    AFTER UPDATE ON anniversaries
    BEGIN
        UPDATE anniversaries SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
    END
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_anniversaries_date ON anniversaries(date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_celebrations_anniversary_id ON celebrations(anniversary_id)')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

def add_anniversary(title, date, type=None, description=None, partner=None, location=None, notes=None):
    """記念日追加"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO anniversaries (title, date, type, description, partner, location, notes)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (title, date, type, description, partner, location, notes))

    anniversary_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return anniversary_id

def add_celebration(anniversary_id, year=None, notes=None):
    if not year:
        year = datetime.now().year

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO celebrations (anniversary_id, year, notes)
    VALUES (?, ?, ?)
    ''', (anniversary_id, year, notes))

    celebration_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return celebration_id

def list_anniversaries(limit=20):
    """記念日一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, date, type, description, partner, location, notes, created_at
    FROM anniversaries
    ORDER BY date ASC
    LIMIT ?
    ''', (limit,))

    anniversaries = cursor.fetchall()
    conn.close()
    return anniversaries

def list_celebrations(anniversary_id):
    """お祝い記録一覧"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, anniversary_id, year, notes, created_at
    FROM celebrations
    WHERE anniversary_id = ?
    ORDER BY year DESC
    ''', (anniversary_id,))

    celebrations = cursor.fetchall()
    conn.close()
    return celebrations

def get_upcoming(days=30):
    """近日の記念日を取得"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    today = datetime.now().date()

    cursor.execute('''
    SELECT id, title, date, type, description, partner, location, notes, created_at
    FROM anniversaries
    WHERE DATE(date) >= DATE('now') AND DATE(date) <= DATE('now', '+' || ? || ' days')
    ORDER BY date ASC
    ''', (days,))

    anniversaries = cursor.fetchall()
    conn.close()
    return anniversaries

if __name__ == '__main__':
    init_db()
