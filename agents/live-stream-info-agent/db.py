#!/usr/bin/env python3
"""
live-stream-info-agent Database Module
SQLite database for live-stream-info-agent
"""

import sqlite3
import os
from datetime import datetime
from typing import Optional, List, Dict, Any

class LiveStreamInfoAgentDatabase:
    """Database for live-stream-info-agent"""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), "live-stream-info-agent.db")
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

        # events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                venue TEXT,
                event_date TIMESTAMP,
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
                event_id INTEGER,
                type TEXT NOT NULL,
                content TEXT,
                url TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (event_id) REFERENCES events (id)
            )
        """)

        self.conn.commit()

    def add_event(self, title: str, artist: str, venue: str = None, event_date: str = None, description: str = None, tags: str = None) -> int:
        """イベントを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO events (title, artist, venue, event_date, description, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, artist, venue, event_date, description, tags))
        self.conn.commit()
        return cursor.lastrowid

    def get_event(self, event_id: int) -> Optional[Dict[str, Any]]:
        """イベントを取得する"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM events WHERE id = ?', (event_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def list_events(self, artist: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """イベントリストを取得する"""
        cursor = self.conn.cursor()
        if artist:
            cursor.execute('SELECT * FROM events WHERE artist = ? ORDER BY event_date DESC LIMIT ?', (artist, limit))
        else:
            cursor.execute('SELECT * FROM events ORDER BY event_date DESC LIMIT ?', (limit,))
        return [dict(row) for row in cursor.fetchall()]

    def search_events(self, query: str) -> List[Dict[str, Any]]:
        """イベントを検索する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM events
            WHERE title LIKE ? OR artist LIKE ? OR venue LIKE ? OR tags LIKE ?
            ORDER BY event_date DESC
        """, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
        return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, event_id: int, entry_type: str, content: str = None, url: str = None, metadata: str = None) -> int:
        """エントリーを追加する"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO entries (event_id, type, content, url, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (event_id, entry_type, content, url, metadata))
        self.conn.commit()
        return cursor.lastrowid

    def get_entries(self, event_id: int, entry_type: str = None) -> List[Dict[str, Any]]:
        """エントリーリストを取得する"""
        cursor = self.conn.cursor()
        if entry_type:
            cursor.execute("""
                SELECT * FROM entries
                WHERE event_id = ? AND type = ?
                ORDER BY created_at DESC
            """, (event_id, entry_type))
        else:
            cursor.execute("""
                SELECT * FROM entries
                WHERE event_id = ?
                ORDER BY created_at DESC
            """, (event_id,))
        return [dict(row) for row in cursor.fetchall()]

if __name__ == "__main__":
    db = LiveStreamInfoAgentDatabase()
    print(f"Database initialized: {{db.db_path}}")
