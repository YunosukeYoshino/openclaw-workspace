#!/usr/bin/env python3
"""
野球選手予測エージェント - Database Module

SQLite-based database management for Baseball Player Forecast Agent.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any


class BaseballPlayerForecastAgentDB:
    """Database manager for 野球選手予測エージェント"""

    def __init__(self, db_path: str = "data/baseball-player-forecast-agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.init_db()

    def init_db(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Main table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    metadata TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # Entry-tags junction table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def add_entry(self, title: str, content: str, metadata: str = None, tags: List[str] = None) -> int:
        """Add a new entry."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO entries (title, content, metadata) VALUES (?, ?, ?)",
                (title, content, metadata)
            )
            entry_id = cursor.lastrowid

            if tags:
                for tag_name in tags:
                    cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_id = cursor.fetchone()["id"]
                    cursor.execute("INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                                 (entry_id, tag_id))

            conn.commit()
            return entry_id

    def get_entries(self, status: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve entries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute("SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                             (status, limit))
            else:
                cursor.execute("SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def update_entry_status(self, entry_id: int, status: str) -> bool:
        """Update entry status."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE entries SET status = ?, updated_at = ? WHERE id = ?",
                (status, datetime.utcnow().isoformat(), entry_id)
            )
            conn.commit()
            return cursor.rowcount > 0


def main():
    db = BaseballPlayerForecastAgentDB()
    print(f"Database initialized for baseball-player-forecast-agent")


if __name__ == "__main__":
    main()
