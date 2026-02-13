#!/usr/bin/env python3
"""
Database for ゲームプロ選手エージェント / Game Pro Player Agent
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class Database:
    """Database for game-pro-player-agent"""

    def __init__(self, db_path: str = "data/game-pro-player-agent.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    async def initialize(self):
        """Initialize database and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()
        logger.info(f"Database initialized: {self.db_path}")

    def _create_tables(self):
        """Create database tables"""
        cursor = self.conn.cursor()

        # Main entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT,
                tags TEXT,
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

        # Entry tags relation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            )
        """)

        self.conn.commit()

    async def create_entry(self, title: str, content: str, category: str = None, tags: List[str] = None) -> int:
        """Create a new entry"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (title, content, category, tags)
            VALUES (?, ?, ?, ?)
        """, (title, content, category, ','.join(tags or [])))
        self.conn.commit()
        entry_id = cursor.lastrowid

        if tags:
            for tag in tags:
                await self._add_tag_to_entry(entry_id, tag)

        return entry_id

    async def _add_tag_to_entry(self, entry_id: int, tag_name: str):
        """Add a tag to an entry"""
        cursor = self.conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO tags (name) VALUES (?)', (tag_name,))
        self.conn.commit()
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        tag_id = cursor.fetchone()[0]
        cursor.execute('INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)',
                      (entry_id, tag_id))
        self.conn.commit()

    async def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get an entry by ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        if row:
            return {
                "id": row[0], "title": row[1], "content": row[2],
                "category": row[3], "tags": row[4].split(',') if row[4] else [],
                "created_at": row[5], "updated_at": row[6]
            }
        return None

    async def list_entries(self, category: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List entries"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute('SELECT * FROM entries WHERE category = ? ORDER BY created_at DESC LIMIT ?',
                          (category, limit))
        else:
            cursor.execute('SELECT * FROM entries ORDER BY created_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        return [{
            "id": row[0], "title": row[1], "content": row[2],
            "category": row[3], "tags": row[4].split(',') if row[4] else [],
            "created_at": row[5], "updated_at": row[6]
        } for row in rows]

    async def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """Search entries"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%'))
        rows = cursor.fetchall()
        return [{
            "id": row[0], "title": row[1], "content": row[2],
            "category": row[3], "tags": row[4].split(',') if row[4] else [],
            "created_at": row[5], "updated_at": row[6]
        } for row in rows]

    async def update_entry(self, entry_id: int, title: str = None, content: str = None,
                          category: str = None, tags: List[str] = None) -> bool:
        """Update an entry"""
        cursor = self.conn.cursor()
        updates = []
        values = []

        if title:
            updates.append("title = ?")
            values.append(title)
        if content:
            updates.append("content = ?")
            values.append(content)
        if category:
            updates.append("category = ?")
            values.append(category)
        if tags is not None:
            updates.append("tags = ?")
            values.append(','.join(tags))

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(entry_id)
            cursor.execute(f"UPDATE entries SET {', '.join(updates)} WHERE id = ?", values)
            self.conn.commit()
            return cursor.rowcount > 0
        return False

    async def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry"""
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM entry_tags WHERE entry_id = ?', (entry_id,))
        cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
        self.conn.commit()
        return cursor.rowcount > 0

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
