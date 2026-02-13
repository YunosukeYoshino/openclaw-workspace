#!/usr/bin/env python3
"""Database module for threat-hunter-agent"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Database:
    """SQLite database handler"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_entry(self, content: str) -> int:
        """Add a new entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO entries (content) VALUES (?)", (content,))
        entry_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """Get an entry by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return {"id": row[0], "content": row[1], "created_at": row[2], "updated_at": row[3]}
        return None

    def list_entries(self, limit: int = 100) -> List[Dict]:
        """List all entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [{"id": r[0], "content": r[1], "created_at": r[2], "updated_at": r[3]} for r in rows]

    def update_entry(self, entry_id: int, content: str) -> bool:
        """Update an entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE entries SET content = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (content, entry_id))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success

    def delete_entry(self, entry_id: int) -> bool:
        """Delete an entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return success
