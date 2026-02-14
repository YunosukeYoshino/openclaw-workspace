#!/usr/bin/env python3
# security-reporter-agent データベース操作

import sqlite3
import logging
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@contextmanager
def get_db_connection(db_path: str):
    # データベース接続コンテキストマネージャー
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class Security_reporter_agentDatabase:
    # security-reporter-agent データベース操作クラス

    def __init__(self, db_path: str = "security-reporter-agent.db"):
        # 初期化
        self.db_path = db_path

    def initialize(self) -> None:
        # データベースを初期化
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    content TEXT NOT NULL,
    status TEXT DEFAULT 'active',
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS entry_tags (
    entry_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (entry_id, tag_id),
    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_entries_status ON entries(status)''')
            cursor.execute('''CREATE INDEX IF NOT EXISTS idx_entries_created_at ON entries(created_at)''')
            conn.commit()
        logger.info("Database initialized: %s", self.db_path)

    def add_entry(self, title: Optional[str], content: str, status: str = "active", priority: int = 0) -> int:
        # エントリーを追加
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO entries (title, content, status, priority, created_at, updated_at)
VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
RETURNING id''', (title, content, status, priority))
            entry_id = cursor.fetchone()["id"]
            conn.commit()
        logger.info("Entry added: %d", entry_id)
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        # エントリーを取得
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM entries WHERE id = ?', (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_entries(self, status: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        # エントリー一覧を取得
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            if status:
                cursor.execute('SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?', (status, limit))
            else:
                cursor.execute('SELECT * FROM entries ORDER BY created_at DESC LIMIT ?', (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, title: Optional[str] = None,
                     content: Optional[str] = None, status: Optional[str] = None,
                     priority: Optional[int] = None) -> bool:
        # エントリーを更新
        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        if status is not None:
            updates.append("status = ?")
            params.append(status)
        if priority is not None:
            updates.append("priority = ?")
            params.append(priority)
        if not updates:
            return False
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(entry_id)
        query = "UPDATE entries SET " + ', '.join(updates) + " WHERE id = ?"
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
        logger.info("Entry updated: %d", entry_id)
        return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        # エントリーを削除
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM entries WHERE id = ?', (entry_id,))
            conn.commit()
        logger.info("Entry deleted: %d", entry_id)
        return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        # エントリーを検索
        with get_db_connection(self.db_path) as conn:
            cursor = conn.cursor()
            search_pattern = "%" + query + "%"
            cursor.execute('SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? ORDER BY created_at DESC LIMIT ?',
                         (search_pattern, search_pattern, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
