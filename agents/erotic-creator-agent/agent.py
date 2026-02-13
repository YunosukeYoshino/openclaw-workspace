#!/usr/bin/env python3
"""
えっちなイラスト・アート管理エージェント

えっちなイラストやアートワークを管理・整理するエージェント
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class EroticCreatorAgent:
    """えっちなイラスト・アート管理エージェント"""

    def __init__(self, db_path: str = None):
        """初期化"""
        self.db_path = db_path or Path(__file__).parent / "erotic_content.db"
        self.conn = None
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # テーブル作成
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                source TEXT,
                url TEXT,
                tags TEXT,
                rating INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # タグテーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                count INTEGER DEFAULT 0
            )
        """)

        self.conn.commit()

    def add_entry(self, title: str, description: str = "", source: str = "", url: str = "", tags: str = "") -> int:
        """エントリー追加"""
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            INSERT INTO entries (title, description, source, url, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, source, url, tags, now, now))
        self.conn.commit()
        return cursor.lastrowid

    def get_entry(self, entry_id: int) -> dict:
        """エントリー取得"""
        row = self.conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None

    def list_entries(self, limit: int = 50, offset: int = 0) -> list:
        """エントリー一覧"""
        rows = self.conn.execute("""
            SELECT * FROM entries ORDER BY created_at DESC LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        return [dict(row) for row in rows]

    def search_entries(self, query: str) -> list:
        """エントリー検索"""
        rows = self.conn.execute("""
            SELECT * FROM entries
            WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
            ORDER BY created_at DESC
        """, (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
        return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        valid_fields = ["title", "description", "source", "url", "tags", "rating"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])

        self.conn.execute(f"""
            UPDATE entries SET {set_clause}, updated_at = ? WHERE id = ?
        """, list(updates.values()) + [entry_id])
        self.conn.commit()
        return True

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        self.conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        self.conn.commit()
        return True

    def get_stats(self) -> dict:
        """統計情報取得"""
        total = self.conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
        avg_rating = self.conn.execute("SELECT AVG(rating) FROM entries WHERE rating > 0").fetchone()[0] or 0
        return dict((
            ("total_entries", total),
            ("average_rating", round(avg_rating, 2))
        ))

    def close(self):
        """接続終了"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """デストラクタ"""
        self.close()


if __name__ == "__main__":
    agent = EroticCreatorAgent()

    # テストエントリー追加
    agent.add_entry(
        title="サンプルエントリー",
        description="これはサンプルのエントリーです",
        source="test",
        tags="サンプル,テスト"
    )

    # エントリー一覧表示
    entries = agent.list_entries()
    for entry in entries:
        print(str(entry['id']) + ": " + str(entry['title']))

    # 統計情報表示
    stats = agent.get_stats()
    print("\n統計: " + str(stats))
