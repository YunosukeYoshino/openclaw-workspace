#!/usr/bin/env python3
"""
fanart-agent Database Module
SQLite database for fanart-agent
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class FanartAgentDatabase:
    """Database for fanart-agent"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "fanart-agent.db")
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

        # content table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                creator TEXT NOT NULL,
                source TEXT,
                url TEXT,
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
                content_id INTEGER,
                type TEXT NOT NULL,
                content TEXT,
                url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (content_id) REFERENCES content (id)
            )
        """)

        self.conn.commit()

    def add_content(self, title: str, creator: str, source: str = None, url: str = None, description: str = None, tags: str = None) -> int:
        """コンテンツを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO content (title, creator, source, url, description, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, creator, source, url, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """コンテンツを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM content WHERE id = ?', (content_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_content(self, creator: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """コンテンツリストを取得する"""
        cursor = self.conn.cursor()
        if creator:
            cursor.execute('SELECT * FROM content WHERE creator = ? ORDER BY created_at DESC LIMIT ?', (creator, limit))
        else:
            cursor.execute('SELECT * FROM content ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_content(self, query: str) -> List[Dict[str, Any]]:
        """コンテンツを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM content
            WHERE title LIKE ? OR creator LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, content_id: int, entry_type: str, content: str = None, url: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (content_id, type, content, url, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (content_id, entry_type, content, url, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, content_id: int, entry_type: str = None) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE content_id = ? AND type = ?
                ORDER BY created_at DESC
            """, (content_id, entry_type))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE content_id = ?
                ORDER BY created_at DESC
            """, (content_id,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    db = FanartAgentDatabase()
    print(f"Database initialized: {{db.db_path}}")
