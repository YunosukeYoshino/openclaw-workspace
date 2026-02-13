#!/usr/bin/env python3
"""
Database module for erotic-similar-agent
erotic-similar-agentのデータベース管理モジュール
"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class Database:
    """データベース管理クラス"""

    def __init__(self, db_path: str = "erotic-similar-agent.db"):
        self.db_path = db_path
        self._initialize_db()

    @contextmanager
    def get_connection(self):
        """データベース接続を取得"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _initialize_db(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # 基本テーブル
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT,
                source_url TEXT,
                artist TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 追加テーブル

CREATE TABLE IF NOT EXISTS similar_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content_id INTEGER NOT NULL,
    similar_content_id INTEGER NOT NULL,
    similarity_score REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id),
    FOREIGN KEY (similar_content_id) REFERENCES entries(id)
);

            # タグテーブル
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL UNIQUE
            );
            """)

            # エントリータグ紐付けテーブル
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS entry_tags (
                entry_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (entry_id, tag_id),
                FOREIGN KEY (entry_id) REFERENCES entries(id),
                FOREIGN KEY (tag_id) REFERENCES tags(id)
            );
            """)

    def execute(self, query: str, params: Tuple = ()) -> sqlite3.Cursor:
        """SQLを実行"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor

    def fetch_all(self, query: str, params: Tuple = ()) -> List[Dict]:
        """全件取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def fetch_one(self, query: str, params: Tuple = ()) -> Optional[Dict]:
        """1件取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None

    def insert(self, table: str, data: Dict) -> int:
        """データを挿入"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {{table}} ({{columns}}) VALUES ({{placeholders}})"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(data.values()))
            return cursor.lastrowid

    def update(self, table: str, data: Dict, where: Dict) -> int:
        """データを更新"""
        set_clause = ", ".join([f"{{k}} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{{k}} = ?" for k in where.keys()])
        query = f"UPDATE {{table}} SET {{set_clause}} WHERE {{where_clause}}"
        params = tuple(data.values()) + tuple(where.values())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

    def delete(self, table: str, where: Dict) -> int:
        """データを削除"""
        where_clause = " AND ".join([f"{{k}} = ?" for k in where.keys()])
        query = f"DELETE FROM {{table}} WHERE {{where_clause}}"
        params = tuple(where.values())
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount


# シングルトンインスタンス
_db_instance = None


def get_db() -> Database:
    """データベースインスタンスを取得"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
