#!/usr/bin/env python3
"""
MOD・カスタムコンテンツ管理エージェント
ゲームのMOD・カスタムコンテンツを管理するエージェント
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class GameModAgent:
    """MOD・カスタムコンテンツ管理エージェント"""

    def __init__(self, db_path: str = "game-mod-agent.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = None

    def connect(self) -> sqlite3.Connection:
        """データベースに接続"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self) -> None:
        """接続を閉じる"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """コンテキストマネージャー"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー"""
        self.close()

    def get_all(self, table: str = "walkthroughs") -> List[Dict[str, Any]]:
        """全てのデータを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_entry(self, table: str, data: Dict[str, Any]) -> int:
        """エントリーを追加"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(query, list(data.values()))
            conn.commit()
            return cursor.lastrowid

    def get_by_game(self, game_id: str, table: str = "walkthroughs") -> List[Dict[str, Any]]:
        """ゲームでデータを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE game_id = ? ORDER BY step_number, created_at", (game_id,))
            return [dict(row) for row in cursor.fetchall()]

    def search(self, query: str, table: str = "walkthroughs") -> List[Dict[str, Any]]:
        """データを検索"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                SELECT * FROM {table}
                WHERE game_title LIKE ? OR step_title LIKE ? OR description LIKE ?
                ORDER BY created_at DESC
            """, (f"%{query}%", f"%{query}%", f"%{query}%"))
            return [dict(row) for row in cursor.fetchall()]

    def update_entry(self, table: str, entry_id: int, data: Dict[str, Any]) -> bool:
        """エントリーを更新"""
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        values = list(data.values()) + [entry_id]

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE {table} SET {set_clause}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_entry(self, table: str, entry_id: int) -> bool:
        """エントリーを削除"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table} WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0


def main():
    """メイン関数"""
    agent = GameModAgent()
    print(f"{agent.__class__.__name__} initialized")


if __name__ == "__main__":
    main()
