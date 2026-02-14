#!/usr/bin/env python3
"""
game-enemy-ai-agent - Database Module
SQLite-based data persistence
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

class GameEnemyAiAgentDB:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = Path(__file__).parent / "game-enemy-ai-agent.db"
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row

    def _create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS data_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, title TEXT, content TEXT NOT NULL, status TEXT DEFAULT "active", priority INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')
        cursor.execute('CREATE TABLE IF NOT EXISTS tags (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)')
        cursor.execute('CREATE TABLE IF NOT EXISTS entry_tags (entry_id INTEGER, tag_id INTEGER, PRIMARY KEY (entry_id, tag_id), FOREIGN KEY (entry_id) REFERENCES data_entries(id) ON DELETE CASCADE, FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE)')
        self.conn.commit()

    def insert(self, entry_type: str, content: str, title: Optional[str] = None,
                status: str = 'active', priority: int = 0, tags: Optional[List[str]] = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO data_entries (type, title, content, status, priority) VALUES (?, ?, ?, ?, ?)', (entry_type, title, content, status, priority))
        entry_id = cursor.lastrowid

        if tags:
            for tag in tags:
                tag_id = self._get_or_create_tag(tag)
                cursor.execute('INSERT INTO entry_tags (entry_id, tag_id) VALUES (?, ?)', (entry_id, tag_id))

        self.conn.commit()
        return entry_id

    def _get_or_create_tag(self, tag_name: str) -> int:
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM tags WHERE name = ?', (tag_name,))
        row = cursor.fetchone()
        if row:
            return row['id']

        cursor.execute('INSERT INTO tags (name) VALUES (?)', (tag_name,))
        return cursor.lastrowid

    def get_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM data_entries WHERE id = ?', (entry_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_by_type(self, entry_type: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        cursor = self.conn.cursor()
        query = 'SELECT * FROM data_entries WHERE type = ? ORDER BY created_at DESC'
        if limit:
            query += ' LIMIT ?'
            cursor.execute(query, (entry_type, limit))
        else:
            cursor.execute(query, (entry_type,))
        return [dict(row) for row in cursor.fetchall()]

    def update_status(self, entry_id: int, status: str):
        cursor = self.conn.cursor()
        cursor.execute('UPDATE data_entries SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (status, entry_id))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()

def snake_to_camel(name):
    return ''.join(word.capitalize() for word in name.replace('-', '_').split('_'))

if __name__ == "__main__":
    db = GameEnemyAiAgentDB()
    print("Database initialized at:", db.db_path)
    db.close()
