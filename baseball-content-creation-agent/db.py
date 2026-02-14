#!/usr/bin/env python3
"""
baseball-content-creation-agent - データベースモジュール
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Any


class BaseballContentCreationAgentDatabase:
    """野球コンテンツ作成エージェント。野球コンテンツの作成・管理。 データベース"""

    def __init__(self, config_path=None):
        self.config_path = config_path or Path(__file__).parent / "config.json"
        self.db_path = Path(__file__).parent / "data" / f"{self.__class__.__name__}.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()

    def init_db(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # メインテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS baseball_content_creation_agent (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    status TEXT DEFAULT 'active',
                    priority INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # メタデータテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # タグテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)

            # エントリータグリレーションテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES baseball_content_creation_agent(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            conn.commit()

    def create_entry(self, entry_data: Dict[str, Any]) -> int:
        """エントリーを作成"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO baseball_content_creation_agent (type, title, content, status, priority)
                VALUES (?, ?, ?, ?, ?)
            """, (
                entry_data.get("type", "default"),
                entry_data.get("title"),
                entry_data.get("content"),
                entry_data.get("status", "active"),
                entry_data.get("priority", 0)
            ))
            entry_id = cursor.lastrowid

            # タグを追加
            for tag_name in entry_data.get("tags", []):
                self._add_tag_to_entry(cursor, entry_id, tag_name)

            conn.commit()
            return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM baseball_content_creation_agent WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            if row:
                entry = dict(row)
                entry["tags"] = self._get_entry_tags(cursor, entry_id)
                return entry
            return None

    def list_entries(self, entry_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """エントリー一覧を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            if entry_type:
                cursor.execute("""
                    SELECT * FROM baseball_content_creation_agent
                    WHERE type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (entry_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM baseball_content_creation_agent
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (limit,))

            entries = []
            for row in cursor.fetchall():
                entry = dict(row)
                entry["tags"] = self._get_entry_tags(cursor, entry["id"])
                entries.append(entry)

            return entries

    def update_entry(self, entry_id: int, entry_data: Dict[str, Any]) -> bool:
        """エントリーを更新"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE baseball_content_creation_agent
                SET type = ?, title = ?, content = ?, status = ?, priority = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                entry_data.get("type"),
                entry_data.get("title"),
                entry_data.get("content"),
                entry_data.get("status"),
                entry_data.get("priority"),
                entry_id
            ))
            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM baseball_content_creation_agent WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0

    def _add_tag_to_entry(self, cursor, entry_id: int, tag_name: str):
        """エントリーにタグを追加"""
        cursor.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
        tag_id = cursor.fetchone()[0]
        cursor.execute("INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                      (entry_id, tag_id))

    def _get_entry_tags(self, cursor, entry_id: int) -> List[str]:
        """エントリーのタグを取得"""
        cursor.execute("""
            SELECT t.name
            FROM tags t
            JOIN entry_tags et ON t.id = et.tag_id
            WHERE et.entry_id = ?
        """, (entry_id,))
        return [row[0] for row in cursor.fetchall()]

    def set_metadata(self, key: str, value: Any):
        """メタデータを設定"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO metadata (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, json.dumps(value)))
            conn.commit()

    def get_metadata(self, key: str) -> Optional[Any]:
        """メタデータを取得"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row[0])
            return None


if __name__ == "__main__":
    # テスト実行
    db = BaseballContentCreationAgentDatabase()
    test_entry = {
        "type": "test",
        "title": "テスト",
        "content": "テストエントリー",
        "tags": ["test", "demo"]
    }
    entry_id = db.create_entry(test_entry)
    print(f"Created entry: {entry_id}")
    print(f"Retrieved: {db.get_entry(entry_id)}")
