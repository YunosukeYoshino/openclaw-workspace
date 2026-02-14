"""
ゲームキャラクターデザイナーエージェント - データベース管理
キャラクターデザインの管理・作成支援
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import json

logger = logging.getLogger('game-character-designer-agent')

class Game_character_designer_agentDB:
    """データベース管理クラス"""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or str(Path(__file__).parent / "game-character-designer-agent.db")
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """DB接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """データベースを初期化"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # エントリーテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    category TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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

            # エントリー-タグ紐付けテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entry_tags (
                    entry_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (entry_id, tag_id),
                    FOREIGN KEY (entry_id) REFERENCES entries(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)

            # 設定テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            logger.info(f"Database initialized: {self.db_path}")

    def add_entry(self, title: str, content: str, category: str = None,
                   tags: List[str] = None) -> int:
        """エントリーを追加"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO entries (title, content, category) VALUES (?, ?, ?)",
                (title, content, category)
            )
            entry_id = cursor.lastrowid

            if tags:
                for tag_name in tags:
                    # タグが存在しない場合は作成
                    cursor.execute(
                        "INSERT OR IGNORE INTO tags (name) VALUES (?)",
                        (tag_name,)
                    )
                    cursor.execute("SELECT id FROM tags WHERE name = ?", (tag_name,))
                    tag_id = cursor.fetchone()["id"]

                    # 紐付け
                    cursor.execute(
                        "INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
                        (entry_id, tag_id)
                    )

            conn.commit()
            logger.info("Entry added: " + str(entry_id))
            return entry_id

    def get_entries(self, category: str = None, limit: int = 100
                   ) -> List[Dict[str, Any]]:
        """エントリー一覧を取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if category:
                cursor.execute("""
                    SELECT * FROM entries WHERE category = ?
                    ORDER BY created_at DESC LIMIT ?
                """, (category, limit))
            else:
                cursor.execute("""
                    SELECT * FROM entries ORDER BY created_at DESC LIMIT ?
                """, (limit,))

            return [dict(row) for row in cursor.fetchall()]

    def get_entry_by_id(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーをIDで取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_entry(self, entry_id: int, title: str = None,
                    content: str = None, category: str = None) -> bool:
        """エントリーを更新"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            updates = []
            params = []

            if title:
                updates.append("title = ?")
                params.append(title)
            if content:
                updates.append("content = ?")
                params.append(content)
            if category:
                updates.append("category = ?")
                params.append(category)

            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                params.append(entry_id)

                query = f"UPDATE entries SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(query, params)
                conn.commit()
                logger.info(f"Entry updated: {entry_id}")
                return True

            return False

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            conn.commit()
            logger.info(f"Entry deleted: {entry_id}")
            return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 50
                      ) -> List[Dict[str, Any]]:
        """エントリーを検索"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            search_term = f"%{query}%"
            cursor.execute("""
                SELECT * FROM entries
                WHERE title LIKE ? OR content LIKE ?
                ORDER BY created_at DESC LIMIT ?
            """, (search_term, search_term, limit))
            return [dict(row) for row in cursor.fetchall()]

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) as total FROM entries")
            total = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM entries GROUP BY category
            """)
            by_category = {row["category"]: row["count"] for row in cursor.fetchall()}

            cursor.execute("SELECT COUNT(*) as total FROM tags")
            total_tags = cursor.fetchone()["total"]

            return {
                "total_entries": total,
                "entries_by_category": by_category,
                "total_tags": total_tags
            }

    def set_setting(self, key: str, value: str) -> None:
        """設定を保存"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            conn.commit()

    def get_setting(self, key: str) -> Optional[str]:
        """設定を取得"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row["value"] if row else None

    def close(self) -> None:
        """DB接続を閉じる（使用しない、context manager方式）"""
        pass
