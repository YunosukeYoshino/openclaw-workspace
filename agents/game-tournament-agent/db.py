#!/usr/bin/env python3
"""
Database schema for game-tournament-agent
"""

import sqlite3
from pathlib import Path

def init_db(db_path: str = "agents/game-tournament-agent/data.db"):
    """Initialize database"""
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        # Entries table
        sql = "CREATE TABLE IF NOT EXISTS entries (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, metadata TEXT, status TEXT DEFAULT 'active' CHECK(status IN ('active','archived','completed')), created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        cursor.execute(sql)

        # Tags table
        sql = "CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)"
        cursor.execute(sql)

        # Entry tags junction
        sql = "CREATE TABLE IF NOT EXISTS entry_tags (entry_id INTEGER, tag_id INTEGER, PRIMARY KEY (entry_id, tag_id), FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE, FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)"
        cursor.execute(sql)

        conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
