#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database for Game AI Dialogue System Agent
ゲームAI対話システムエージェント
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

DB_PATH = Path(__file__).parent / "game-ai-dialogue-system-agent.db"


class GameAiDialogueSystemAgentDB:
    """Database handler for Game AI Dialogue System Agent"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self._init_db()

    def _init_db(self):
        """Initialize database tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Main entries table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    type TEXT DEFAULT 'default',
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 0,
                    tags TEXT,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Tags table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Entry-tags mapping table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            # Activity log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

    def add_entry(self, title: str, content: str, **kwargs) -> int:
        """Add a new entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO entries (title, content, type, status, priority, tags, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                title, content,
                kwargs.get('type', 'default'),
                kwargs.get('status', 'active'),
                kwargs.get('priority', 0),
                kwargs.get('tags', ''),
                kwargs.get('metadata', '')
            ))
            conn.commit()
            self._log_activity('add_entry', f"Added entry: {title}")
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get entry by ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_entries(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entries with optional status filter."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if status:
                cursor.execute(
                    "SELECT * FROM entries WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                    (status, limit)
                )
            else:
                cursor.execute(
                    "SELECT * FROM entries ORDER BY updated_at DESC LIMIT ?",
                    (limit,)
                )
            return [dict(row) for row in cursor.fetchall()]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """Update entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            fields = []
            values = []
            for key, value in kwargs.items():
                if key in ['title', 'content', 'type', 'status', 'priority', 'tags', 'metadata']:
                    fields.append(f"{key} = ?")
                    values.append(value)
            if not fields:
                return False
            values.append(entry_id)
            cursor.execute(f"""
                UPDATE entries SET {', '.join(fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
            self._log_activity('update_entry', f"Updated entry: {entry_id}")
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """Delete entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            self._log_activity('delete_entry', f"Deleted entry: {entry_id}")
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            total_entries = cursor.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            active_entries = cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'active'").fetchone()[0]
            total_tags = cursor.execute("SELECT COUNT(*) FROM tags").fetchone()[0]

            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "total_tags": total_tags
            }

    def _log_activity(self, action: str, details: str = ""):
        """Log activity to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_log (action, details) VALUES (?, ?)",
                (action, details)
            )
            conn.commit()


if __name__ == "__main__":
    db = GameAiDialogueSystemAgentDB()
    print(f"Database initialized: "ゲームAI対話システムエージェント"")
    print(f"Stats: {db.get_stats()}")
