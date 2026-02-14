#!/usr/bin/env python3
"""
Database module for game-level-design-agent
"""

import sqlite3
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

DB_PATH = Path(__file__).parent / "data" / "game-level-design-agent.db"

@contextmanager
def get_db():
    """Get database connection"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database tables"""
    with get_db() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS entries ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "type TEXT NOT NULL,"
            "content TEXT NOT NULL,"
            "metadata TEXT,"
            "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,"
            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS tags ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT,"
            "name TEXT UNIQUE NOT NULL"
            ")"
        )
        conn.execute(
            "CREATE TABLE IF NOT EXISTS entry_tags ("
            "entry_id INTEGER NOT NULL,"
            "tag_id INTEGER NOT NULL,"
            "PRIMARY KEY (entry_id, tag_id),"
            "FOREIGN KEY (entry_id) REFERENCES entries(id),"
            "FOREIGN KEY (tag_id) REFERENCES tags(id)"
            ")"
        )
        conn.commit()

class Database:
    """Database operations for game-level-design-agent"""

    def __init__(self):
        self.init_db()

    def init_db(self):
        """Initialize database"""
        init_db()

    def add_entry(self, entry_type: str, content: str, metadata: Optional[str] = None) -> int:
        """Add a new entry"""
        with get_db() as conn:
            cursor = conn.execute(
                'INSERT INTO entries (type, content, metadata) VALUES (?, ?, ?)',
                (entry_type, content, metadata)
            )
            conn.commit()
            return cursor.lastrowid

    def get_entries(self, entry_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get entries"""
        with get_db() as conn:
            if entry_type:
                cursor = conn.execute(
                    'SELECT * FROM entries WHERE type = ? ORDER BY created_at DESC LIMIT ?',
                    (entry_type, limit)
                )
            else:
                cursor = conn.execute(
                    'SELECT * FROM entries ORDER BY created_at DESC LIMIT ?',
                    (limit,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def add_tag(self, name: str) -> int:
        """Add a tag"""
        with get_db() as conn:
            cursor = conn.execute(
                'INSERT OR IGNORE INTO tags (name) VALUES (?)',
                (name,)
            )
            conn.commit()
            return cursor.lastrowid

    def get_tags(self) -> List[str]:
        """Get all tags"""
        with get_db() as conn:
            cursor = conn.execute('SELECT name FROM tags ORDER BY name')
            return [row[0] for row in cursor.fetchall()]

if __name__ == "__main__":
    db = Database()
    print(f"Database initialized: {DB_PATH}")
