#!/usr/bin/env python3
"""
えっちAIキュレーションエージェント データベースモジュール
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

class EroticAiCurationAgentDB:
    """えっちAIキュレーションエージェント データベース管理"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path("data/erotic-ai-curation-agent.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_record(self, title, description, data=None):
        """レコードを追加"""
        data_json = json.dumps(data) if data else None
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO records (title, description, data) VALUES (?, ?, ?)",
                (title, description, data_json)
            )
            conn.commit()
            return cursor.lastrowid

    def get_record(self, record_id):
        """レコードを取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM records WHERE id = ?", (record_id,)).fetchone()
            return dict(row) if row else None

    def list_records(self, limit=100):
        """レコード一覧を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM records ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def update_record(self, record_id, title=None, description=None, data=None):
        """レコードを更新"""
        updates = []
        params = []
        if title:
            updates.append("title = ?")
            params.append(title)
        if description:
            updates.append("description = ?")
            params.append(description)
        if data is not None:
            updates.append("data = ?")
            params.append(json.dumps(data))
        params.append(record_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"UPDATE records SET {', '.join(updates)} WHERE id = ?", params)
            conn.commit()

def to_camel_case(snake_str):
    return ''.join(word.capitalize() for word in snake_str.split('-'))
