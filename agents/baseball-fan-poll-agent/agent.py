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
                username TEXT,
                team TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_entry(self, title: str, content: str, username: str = "",
                   team: str = "", tags: str = "") -> int:
        """Add a community entry / コミュニティエントリーを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO {table_name} (title, {content_field}, username, team, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, content, username, team, tags))

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
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def search_by_team(self, team: str) -> List[Dict[str, Any]]:
        """Search entries by team / チームでエントリーを検索"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM {table_name}
            WHERE team LIKE ?
            ORDER BY timestamp DESC
        ''', (f"%{team}%",))

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
