#!/usr/bin/env python3
"""
野球トレーニングエージェント データベースモジュール
Baseball Training Agent Database Module

An agent for managing player training records, physical data, and practice menus
"""

import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
from datetime import datetime


class BaseballTrainingAgentDB:
    """野球トレーニングエージェント データベースクラス"""

    def __init__(self, db_path: str = "baseball-training-agent.db"):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        """データベース接続のコンテキストマネージャー"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def init_database(self):
        """データベースを初期化"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # training_sessionsテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS training_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    data_json TEXT,
                    status TEXT DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # playersテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    team TEXT,
                    data_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # インデックス作成
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_training_sessions_status ON training_sessions(status)")
            cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_training_sessions_created ON training_sessions(created_at)")

            conn.commit()

    def insert_entry(self, title: str, description: str = "", data_json: str = "{}", status: str = "active") -> int:
        """エントリーを挿入"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO training_sessions (title, description, data_json, status)
                VALUES (?, ?, ?, ?)
                """,
                (title, description, data_json, status)
            )
            conn.commit()
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリーを取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM training_sessions WHERE id = ?",
                (entry_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def list_entries(self, limit: int = 100, offset: int = 0, status: str = None) -> List[Dict[str, Any]]:
        """エントリー一覧を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            query = f"SELECT * FROM training_sessions"
            params = []

            if status:
                query += " WHERE status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリーを更新"""
        if not kwargs:
            return False

        with self.get_connection() as conn:
            cursor = conn.cursor()

            update_fields = []
            params = []

            for key, value in kwargs.items():
                if key in ["title", "description", "data_json", "status"]:
                    update_fields.append(f"{key} = ?")
                    params.append(value)

            if not update_fields:
                return False

            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(entry_id)

            cursor.execute(
                f"UPDATE training_sessions SET {', '.join(update_fields)} WHERE id = ?",
                params
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"DELETE FROM training_sessions WHERE id = ?",
                (entry_id,)
            )
            conn.commit()
            return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """エントリーを検索"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                SELECT * FROM training_sessions
                WHERE title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC LIMIT ?
                """,
                (f"%{query}%", f"%{query}%", limit)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """統計情報を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(f"SELECT COUNT(*) FROM training_sessions")
            total_entries = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM training_sessions WHERE status = 'active'")
            active_entries = cursor.fetchone()[0]

            cursor.execute(f"SELECT COUNT(*) FROM players")
            total_items = cursor.fetchone()[0]

            return {
                "total_entries": total_entries,
                "active_entries": active_entries,
                "total_items": total_items
            }

    def insert_item(self, name: str, team: str = "", data_json: str = "{}") -> int:
        """アイテムを挿入"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"""
                INSERT INTO players (name, team, data_json)
                VALUES (?, ?, ?)
                """,
                (name, team, data_json)
            )
            conn.commit()
            return cursor.lastrowid

    def get_items(self, limit: int = 100) -> List[Dict[str, Any]]:
        """アイテム一覧を取得"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                f"SELECT * FROM players ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
