#!/usr/bin/env python3
"""
野球メディア統合エージェント

野球関連メディアの統合管理エージェント
"""

import sqlite3
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseballMediaAggregatorAgent:
    """野球メディア統合エージェント"""

    def __init__(self, db_path: str = "baseball-media-aggregator-agent.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()

        # エントリーテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                tags TEXT,
                priority INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS media_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                url TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                url TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                url TEXT,
                entry_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (entry_id) REFERENCES entries(id)
            )
        """)

        self.conn.commit()
        logger.info("Database initialized")

    def add_entry(self, title: str, content: str, tags: Optional[str] = None, priority: int = 0) -> int:
        """エントリー追加"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO entries (title, content, tags, priority) VALUES (?, ?, ?, ?)",
            (title, content, tags, priority)
        )
        self.conn.commit()
        entry_id = cursor.lastrowid
        logger.info(f"Entry added: {title} (ID: {entry_id})")
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリー取得"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None

    def list_entries(self, limit: int = 100, status: str = None) -> List[Dict[str, Any]]:
        """エントリーリスト取得"""
        cursor = self.conn.cursor()
        if status:
            cursor.execute(
                "SELECT * FROM entries WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit)
            )
        else:
            cursor.execute("SELECT * FROM entries ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        valid_fields = ['title', 'content', 'tags', 'priority', 'status']
        update_fields = {k: v for k, v in kwargs.items() if k in valid_fields}
        if not update_fields:
            return False

        update_fields['updated_at'] = str(datetime.now())
        set_clause = ', '.join([f"{k} = ?" for k in update_fields.keys()])
        values = list(update_fields.values()) + [entry_id]

        cursor = self.conn.cursor()
        cursor.execute(f"UPDATE entries SET {set_clause} WHERE id = ?", values)
        self.conn.commit()
        logger.info(f"Entry updated: ID {entry_id}")
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.conn.commit()
        if cursor.rowcount > 0:
            logger.info(f"Entry deleted: ID {entry_id}")
            return True
        return False

    def search_entries(self, query: str) -> List[Dict[str, Any]]:
        """エントリー検索"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def get_stats(self) -> Dict[str, int]:
        """統計情報取得"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM entries WHERE status = 'active'")
        active = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM entries")
        total = cursor.fetchone()[0]
        return {"active": active, "total": total}

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


def main():
    """メイン関数"""
    agent = BaseballMediaAggregatorAgent()
    print(f"{agent.__class__.__name__} initialized")
    print(f"Stats: {agent.get_stats()}")
    agent.close()


if __name__ == "__main__":
    main()
