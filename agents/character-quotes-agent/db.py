#!/usr/bin/env python3
"""
character-quotes-agent Database Module
SQLite database for character-quotes-agent
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class CharacterQuotesAgentDatabase:
    """Database for character-quotes-agent"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "character-quotes-agent.db")
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        """データベースに接続する"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

    def create_tables(self):
        """テーブルを作成する"""
        cursor = self.conn.cursor()

        # characters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS characters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # entries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                character_id INTEGER,
                type TEXT NOT NULL,
                content TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (character_id) REFERENCES characters (id)
            )
        """)

        self.conn.commit()

    def add_character(self, name: str, source: str, description: str = None, tags: str = None) -> int:
        """キャラクターを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO characters (name, source, description, tags)
            VALUES (?, ?, ?, ?)
        """, (name, source, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_character(self, character_id: int) -> Optional[Dict[str, Any]]:
        """キャラクターを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM characters WHERE id = ?', (character_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_characters(self, source: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """キャラクターリストを取得する"""
        cursor = self.conn.cursor()
        if source:
            cursor.execute('SELECT * FROM characters WHERE source = ? ORDER BY created_at DESC LIMIT ?', (source, limit))
        else:
            cursor.execute('SELECT * FROM characters ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_characters(self, query: str) -> List[Dict[str, Any]]:
        """キャラクターを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM characters
            WHERE name LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, character_id: int, entry_type: str, content: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (character_id, type, content, metadata)
            VALUES (?, ?, ?, ?)
        """, (character_id, entry_type, content, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, character_id: int, entry_type: str = None) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE character_id = ? AND type = ?
                ORDER BY created_at DESC
            """, (character_id, entry_type))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE character_id = ?
                ORDER BY created_at DESC
            """, (character_id,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    db = CharacterQuotesAgentDatabase()
    print(f"Database initialized: {{db.db_path}}")
