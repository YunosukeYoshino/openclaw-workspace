#!/usr/bin/env python3
"""
alert-rule-manager-agent - データベースモジュール
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class AlertRuleManagerAgentDB:
    """alert-rule-manager-agent データベース"""

    def __init__(self, db_path: str = "alert-rule-manager-agent.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self._init_tables()

    def _init_tables(self):
        """テーブル初期化"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_entry(self, title: str, content: str) -> int:
        """エントリー追加"""
        self.cursor.execute(
            "INSERT INTO entries (title, content) VALUES (?, ?)",
            (title, content)
        )
        self.conn.commit()
        return self.cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリー取得"""
        self.cursor.execute(
            "SELECT * FROM entries WHERE id = ?",
            (entry_id,)
        )
        row = self.cursor.fetchone()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
        return None

    def list_entries(self, limit: int = 100) -> List[Dict]:
        """エントリー一覧"""
        self.cursor.execute(
            "SELECT * FROM entries ORDER BY created_at DESC LIMIT ?",
            (limit,)
        )
        rows = self.cursor.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "content": row[2],
                "created_at": row[3],
                "updated_at": row[4]
            }
            for row in rows
        ]

    def close(self):
        """接続クローズ"""
        self.conn.close()

def main():
    """メイン関数"""
    db = AlertRuleManagerAgentDB()

    # サンプルエントリー追加
    entry_id = db.add_entry(
        "Sample Entry",
        "This is a sample entry for alert-rule-manager-agent"
    )
    print(f"Added entry with ID: {entry_id}")

    # エントリー一覧
    entries = db.list_entries()
    print(f"Total entries: {len(entries)}")

    db.close()

if __name__ == "__main__":
    main()
