#!/usr/bin/env python3
"""
vtuber-archive-agent Database Module
SQLite database for vtuber-archive-agent
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class VtuberArchiveAgentDatabase:
    """Database for vtuber-archive-agent"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "vtuber-archive-agent.db")
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

        # vtubers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vtubers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                channel_url TEXT,
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
                vtuber_id INTEGER,
                type TEXT NOT NULL,
                title TEXT,
                content TEXT,
                url TEXT,
                scheduled_time TIMESTAMP,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vtuber_id) REFERENCES vtubers (id)
            )
        """)

        self.conn.commit()

    def add_vtuber(self, name: str, channel_url: str = None, description: str = None, tags: str = None) -> int:
        """VTuberを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO vtubers (name, channel_url, description, tags)
            VALUES (?, ?, ?, ?)
        """, (name, channel_url, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_vtuber(self, vtuber_id: int) -> Optional[Dict[str, Any]]:
        """VTuberを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM vtubers WHERE id = ?', (vtuber_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_vtubers(self, limit: int = 100) -> List[Dict[str, Any]]:
        """VTuberリストを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM vtubers ORDER BY created_at DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_vtubers(self, query: str) -> List[Dict[str, Any]]:
        """VTuberを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM vtubers
            WHERE name LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, vtuber_id: int, entry_type: str, title: str = None, content: str = None, url: str = None, scheduled_time: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (vtuber_id, type, title, content, url, scheduled_time, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (vtuber_id, entry_type, title, content, url, scheduled_time, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, vtuber_id: int, entry_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE vtuber_id = ? AND type = ?
                ORDER BY created_at DESC LIMIT ?
            """, (vtuber_id, entry_type, limit))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE vtuber_id = ?
                ORDER BY created_at DESC LIMIT ?
            """, (vtuber_id, limit))
        return [dict(row) for row in cursor.fetchall()]

    def get_upcoming_streams(self, days: int = 7) -> List[Dict[str, Any]]:
        """近日の配信を取得する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT e.*, v.name as vtuber_name
            FROM entries e
            JOIN vtubers v ON e.vtuber_id = v.id
            WHERE e.type = 'stream'
            AND e.scheduled_time >= datetime('now')
            AND e.scheduled_time <= datetime('now', '+' || ? || ' days')
            ORDER BY e.scheduled_time ASC
        """, (days,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    db = VtuberArchiveAgentDatabase()
    print(f"Database initialized: {{db.db_path}}")
