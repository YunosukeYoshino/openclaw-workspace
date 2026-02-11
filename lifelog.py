#!/usr/bin/env python3
"""
Lifelog - SQLite-based entry management tool
"""

import sqlite3
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# Database location
DB_PATH = Path("/workspace") / "lifelog.db"

def get_db():
    db = sqlite3.connect(str(DB_PATH))
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL CHECK(type IN ('idea','goal','project','vision','note','task')),
            title TEXT,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'active' CHECK(status IN ('active','archived','completed')),
            priority INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entry_tags (
            entry_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (entry_id, tag_id),
            FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        )
    ''')
    db.commit()
    return db

def add_entry(entry_type, content, title=None, tags=None):
    db = init_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO entries (type, content, title)
        VALUES (?, ?, ?)
    ''', (entry_type, content, title))
    entry_id = cursor.lastrowid

    if tags:
        for tag in tags.split(','):
            tag = tag.strip()
            if tag:
                cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag,))
                cursor.execute('SELECT id FROM tags WHERE name = ?', (tag,))
                tag_id = cursor.fetchone()['id']
                cursor.execute('INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)',
                              (entry_id, tag_id))

    db.commit()
    return entry_id

def list_entries(entry_type=None):
    db = init_db()
    cursor = db.cursor()
    if entry_type:
        cursor.execute('''
            SELECT e.*, GROUP_CONCAT(t.name) as tags
            FROM entries e
            LEFT JOIN entry_tags et ON e.id = et.entry_id
            LEFT JOIN tags t ON et.tag_id = t.id
            WHERE e.type = ?
            GROUP BY e.id
            ORDER BY e.created_at DESC
        ''', (entry_type,))
    else:
        cursor.execute('''
            SELECT e.*, GROUP_CONCAT(t.name) as tags
            FROM entries e
            LEFT JOIN entry_tags et ON e.id = et.entry_id
            LEFT JOIN tags t ON et.tag_id = t.id
            GROUP BY e.id
            ORDER BY e.created_at DESC
        ''')

    rows = cursor.fetchall()
    return [dict(row) for row in rows]

def get_stats():
    db = init_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT type, status, COUNT(*) as count
        FROM entries
        GROUP BY type, status
        ORDER BY type, status
    ''')
    return [dict(row) for row in cursor.fetchall()]

def main():
    if len(sys.argv) < 2:
        print("Usage: lifelog.py <command> [args...]")
        print("Commands:")
        print("  add <type> <content> [title] [tags]")
        print("  list [type]")
        print("  stats")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'add':
        if len(sys.argv) < 4:
            print("Usage: lifelog.py add <type> <content> [title] [tags]")
            sys.exit(1)
        entry_type = sys.argv[2]
        content = sys.argv[3]
        title = sys.argv[4] if len(sys.argv) > 4 else None
        tags = sys.argv[5] if len(sys.argv) > 5 else None
        entry_id = add_entry(entry_type, content, title, tags)
        print(f"Added entry #{entry_id}")

    elif command == 'list':
        entry_type = sys.argv[2] if len(sys.argv) > 2 else None
        entries = list_entries(entry_type)
        if entries:
            print(json.dumps(entries, indent=2, default=str))
        else:
            print("No entries found.")

    elif command == 'stats':
        stats = get_stats()
        print(json.dumps(stats, indent=2))

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()
