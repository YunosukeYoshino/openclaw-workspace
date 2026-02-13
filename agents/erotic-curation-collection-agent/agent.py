#!/usr/bin/env python3
"""
{agent_name} - {japanese_name}

{description}
"""

import sqlite3
from typing import Optional, List, Dict, Any
from datetime import datetime


class {class_name}:
    """{japanese_name}"""

    def __init__(self, db_path: str = "{agent_name}.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize database / データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                {content_field} TEXT NOT NULL,
                creator TEXT,
                category TEXT,
                rating REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: str, content: str, creator: str = "",
                   category: str = "", rating: float = 0.0, tags: str = "") -> int:
        """Add a curation entry / キュレーションエントリーを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO {table_name} (title, {content_field}, creator, category, rating, tags)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (title, content, creator, category, rating, tags))

        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """Get an entry by ID / IDでエントリーを取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name} WHERE id = ?
        ''', (entry_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def list_entries(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List all entries / 全エントリーを一覧"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name}
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Search entries by category / カテゴリでエントリーを検索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name}
            WHERE category LIKE ?
            ORDER BY rating DESC
        ''', (f"%{category}%",))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def {custom_method}(self) -> Any:
        """{custom_method_description}"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # TODO: Implement custom logic

        conn.close()
        return None


if __name__ == "__main__":
    agent = {class_name}()
    print("{japanese_name} initialized!")
    print(f"Database: {{agent.db_path}}")
