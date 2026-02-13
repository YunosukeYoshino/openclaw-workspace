#!/usr/bin/env python3
"""
えっちプラットフォームエージェント
Erotic Platform Agent

えっちサイト、サービス情報、プラットフォームの比較を管理するエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class EroticPlatformAgent:
    """えっちプラットフォームエージェント"""

    def __init__(self, db_path: str = "erotic-platform-agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # platformsテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS platforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                data_json TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # featuresテーブル作成
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS features (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                data_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def add_entry(self, title: str, description: str, data_json: str = "{}") -> int:
        """新しいエントリーを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO platforms (title, description, data_json) VALUES (?, ?, ?)",
            (title, description, data_json)
        )
        conn.commit()
        entry_id = cursor.lastrowid
        conn.close()
        return entry_id

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリーを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM platforms WHERE id = ?",
            (entry_id,)
        )
        row = cursor.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "data_json": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
        return None

    def list_entries(self, limit: int = 100) -> List[Dict]:
        """エントリー一覧を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM platforms ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "data_json": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
            for row in rows
        ]

    def update_entry(self, entry_id: int, title: str = None, description: str = None, data_json: str = None) -> bool:
        """エントリーを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updates = []
        params = []
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if data_json is not None:
            updates.append("data_json = ?")
            params.append(data_json)

        if not updates:
            conn.close()
            return False

        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(entry_id)

        cursor.execute(
            f"UPDATE platforms SET {', '.join(updates)} WHERE id = ?",
            params
        )
        conn.commit()
        conn.close()
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリーを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM platforms WHERE id = ?", (entry_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    def search_entries(self, query: str, limit: int = 50) -> List[Dict]:
        """エントリーを検索"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT * FROM platforms WHERE title LIKE ? OR description LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", f"%{query}%", limit)
        )
        rows = cursor.fetchall()
        conn.close()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "data_json": row[3],
                "status": row[4],
                "created_at": row[5],
                "updated_at": row[6]
            }
            for row in rows
        ]

    def get_stats(self) -> Dict:
        """統計情報を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f"SELECT COUNT(*) FROM platforms")
        total_entries = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM platforms WHERE status = 'active'")
        active_entries = cursor.fetchone()[0]

        cursor.execute(f"SELECT COUNT(*) FROM features")
        total_items = cursor.fetchone()[0]

        conn.close()

        return {
            "total_entries": total_entries,
            "active_entries": active_entries,
            "total_items": total_items
        }


def main():
    """メイン関数"""
    agent = EroticPlatformAgent()
    print("えっちプラットフォームエージェント initialized!")
    print("Database:", agent.db_path)

    # サンプルデータ追加
    entry_id = agent.add_entry(
        title="サンプルエントリー",
        description="えっちプラットフォームエージェントのサンプルデータ"
    )
    print(f"Added sample entry with ID: {entry_id}")

    # 統計表示
    stats = agent.get_stats()
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
