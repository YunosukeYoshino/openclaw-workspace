#!/usr/bin/env python3
"""
えっちなイラスト・アート管理エージェント - データベースモジュール

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class EroticArtworkAgentDB:
    """えっちなイラスト・アート管理エージェント データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "erotic-artwork-agent.db"

    @contextmanager
    def _get_connection(self):
        """データベース接続コンテキストマネージャー"""
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
        """データベース初期化"""
        with self._get_connection() as conn:
            # entriesテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    source TEXT,
                    url TEXT,
                    tags TEXT,
                    rating INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, source)
                )
            """)

            # タグテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_title ON entries(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_created ON entries(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entries_tags ON entries(tags)")

    def add_entry(self, title: str, description: str = "", source: str = "",
                  url: str = "", tags: str = "", rating: int = 0) -> int:
        """エントリー追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO entries
                (title, description, source, url, tags, rating, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM entries WHERE title = ? AND source = ?), ?), ?)
            """, (title, description, source, url, tags, rating, title, source, now, now))
            return cursor.lastrowid

    def get_entry(self, entry_id: int) -> Optional[Dict[str, Any]]:
        """エントリー取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
            return dict(row) if row else None

    def list_entries(self, limit: int = 50, offset: int = 0,
                     sort_by: str = "created_at", order: str = "DESC") -> List[Dict[str, Any]]:
        """エントリー一覧"""
        valid_sort = ["id", "title", "rating", "created_at", "updated_at"]
        valid_order = ["ASC", "DESC"]

        sort_by = sort_by if sort_by in valid_sort else "created_at"
        order = order.upper() if order.upper() in valid_order else "DESC"

        with self._get_connection() as conn:
            query = f"""
                SELECT * FROM entries
                ORDER BY {sort_by} {order}
                LIMIT ? OFFSET ?
            """
            rows = conn.execute(query, (limit, offset)).fetchall()
            return [dict(row) for row in rows]

    def search_entries(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """エントリー検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM entries
                WHERE title LIKE ? OR description LIKE ? OR tags LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_entries_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """タグでエントリー取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM entries
                WHERE tags LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (f"%{tag}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def update_entry(self, entry_id: int, **kwargs) -> bool:
        """エントリー更新"""
        valid_fields = ["title", "description", "source", "url", "tags", "rating"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])

        with self._get_connection() as conn:
            query = f"""
                UPDATE entries SET {set_clause}, updated_at = ? WHERE id = ?
            """
            cursor = conn.execute(query, list(updates.values()) + [entry_id])
            return cursor.rowcount > 0

    def delete_entry(self, entry_id: int) -> bool:
        """エントリー削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            avg_rating = conn.execute(
                "SELECT AVG(rating) FROM entries WHERE rating > 0"
            ).fetchone()[0] or 0
            top_rated = conn.execute("""
                SELECT title, rating FROM entries
                WHERE rating > 0 ORDER BY rating DESC LIMIT 5
            """).fetchall()

            return dict((
                ("total_entries", total),
                ("average_rating", round(avg_rating, 2)),
                ("top_rated", [dict(row) for row in top_rated])
            ))

    def add_tag(self, name: str) -> int:
        """タグ追加"""
        with self._get_connection() as conn:
            now = datetime.now().isoformat()
            cursor = conn.execute("""
                INSERT OR IGNORE INTO tags (name, created_at) VALUES (?, ?)
            """, (name, now))
            if cursor.rowcount > 0:
                return cursor.lastrowid

            # 既存の場合、カウント増加
            conn.execute("UPDATE tags SET count = count + 1 WHERE name = ?", (name,))
            row = conn.execute("SELECT id FROM tags WHERE name = ?", (name,)).fetchone()
            return row["id"] if row else 0

    def list_tags(self, limit: int = 100) -> List[Dict[str, Any]]:
        """タグ一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM tags ORDER BY count DESC, name ASC LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]


if __name__ == "__main__":
    db = EroticArtworkAgentDB()
    db.initialize()

    # テスト
    db.add_entry(
        title="サンプルエントリー",
        description="これはサンプルです",
        source="test",
        tags="サンプル,テスト"
    )

    entries = db.list_entries()
    print("エントリー数: " + str(len(entries)))

    stats = db.get_stats()
    print("統計: " + str(stats))
