#!/usr/bin/env python3
"""
MOD・カスタムコンテンツ管理エージェント - データベースモジュール
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager


class Database:
    """データベース管理クラス"""

    def __init__(self, db_path: str = "game-mod-agent.db"):
        """初期化"""
        self.db_path = Path(db_path)
        self.conn = None

    @contextmanager
    def get_connection(self):
        """接続を取得（コンテキストマネージャー）"""
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

    def initialize(self) -> None:
        """データベースを初期化"""
        with self.get_connection() as conn:
            conn.executescript("""

        CREATE TABLE IF NOT EXISTS mods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            mod_id TEXT NOT NULL,
            mod_name TEXT NOT NULL,
            mod_type TEXT,
            author TEXT,
            version TEXT,
            description TEXT,
            download_url TEXT,
            install_instructions TEXT,
            file_size INTEGER,
            category TEXT,
            rating REAL DEFAULT 0.0,
            download_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(mod_id)
        );

        CREATE TABLE IF NOT EXISTS mod_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mod_id TEXT NOT NULL,
            required_mod_id TEXT NOT NULL,
            required_version TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS custom_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_id TEXT NOT NULL,
            game_title TEXT NOT NULL,
            content_type TEXT NOT NULL,
            content_name TEXT NOT NULL,
            creator TEXT,
            description TEXT,
            download_url TEXT,
            file_size INTEGER,
            rating REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
            """)

    def execute(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """クエリを実行"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def execute_many(self, query: str, params_list: List[tuple]) -> None:
        """複数のクエリを実行"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)

    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """データを挿入"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            return cursor.lastrowid

    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """データを更新"""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()) + list(where.values()))
            return cursor.rowcount

    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """データを削除"""
        where_clause = " AND ".join([f"{k} = ?" for k in where.keys()])
        query = f"DELETE FROM {table} WHERE {where_clause}"
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(where.values()))
            return cursor.rowcount

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        """全てのデータを取得"""
        return self.execute(f"SELECT * FROM {table} ORDER BY id DESC")

    def get_by_id(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """IDでデータを取得"""
        result = self.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
        return result[0] if result else None

    def count(self, table: str) -> int:
        """レコード数を取得"""
        result = self.execute(f"SELECT COUNT(*) as count FROM {table}")
        return result[0]["count"] if result else 0

    def search(self, table: str, search_field: str, query: str) -> List[Dict[str, Any]]:
        """検索"""
        return self.execute(
            f"SELECT * FROM {table} WHERE {search_field} LIKE ? ORDER BY id DESC",
            (f"%{query}%",)
        )


def main():
    """メイン関数"""
    db = Database()
    db.initialize()
    print("Database initialized successfully")


if __name__ == "__main__":
    main()
