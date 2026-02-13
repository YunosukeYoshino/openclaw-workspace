#!/usr/bin/env python3
"""
えっちコンテンツブックマークエージェント - データベースモジュール
Erotic Content Bookmark Agent - Database Module

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class EroticBookmarkAgentDB:
    """えっちコンテンツブックマークエージェント データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "erotic-bookmark-agent.db"

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
            # ブックマークテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS bookmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    description TEXT,
                    tags TEXT,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_url ON bookmarks(url)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_title ON bookmarks(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_category ON bookmarks(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_created ON bookmarks(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_bookmarks_last_accessed ON bookmarks(last_accessed)")

    def add_bookmark(self, url: str, title: str = "", description: str = "",
                     tags: str = "", category: str = "") -> int:
        """ブックマーク追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO bookmarks
                (url, title, description, tags, category, created_at, last_accessed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (url, title, description, tags, category, now, now))
            return cursor.lastrowid

    def get_bookmark(self, bookmark_id: int) -> Optional[Dict[str, Any]]:
        """ブックマーク取得（閲覧時刻更新）"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM bookmarks WHERE id = ?", (bookmark_id,)).fetchone()
            if row:
                # 閲覧時刻更新
                conn.execute("""
                    UPDATE bookmarks SET last_accessed = ? WHERE id = ?
                """, (datetime.now().isoformat(), bookmark_id))
                return dict(row)
            return None

    def list_bookmarks(self, limit: int = 50, offset: int = 0,
                      category: str = None, sort_by: str = "created_at",
                      order: str = "DESC") -> List[Dict[str, Any]]:
        """ブックマーク一覧"""
        valid_sort = ["id", "title", "category", "created_at", "last_accessed"]
        valid_order = ["ASC", "DESC"]

        sort_by = sort_by if sort_by in valid_sort else "created_at"
        order = order.upper() if order.upper() in valid_order else "DESC"

        query = "SELECT * FROM bookmarks WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        query += f" ORDER BY {sort_by} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def search_bookmarks(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """ブックマーク検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM bookmarks
                WHERE url LIKE ? OR title LIKE ? OR description LIKE ? OR tags LIKE ?
                ORDER BY last_accessed DESC, created_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_bookmarks_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """カテゴリで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM bookmarks
                WHERE category = ?
                ORDER BY last_accessed DESC, created_at DESC
                LIMIT ?
            """, (category, limit)).fetchall()
            return [dict(row) for row in rows]

    def get_recently_accessed(self, limit: int = 20) -> List[Dict[str, Any]]:
        """最近アクセスしたブックマーク"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM bookmarks
                WHERE last_accessed IS NOT NULL
                ORDER BY last_accessed DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def update_bookmark(self, bookmark_id: int, **kwargs) -> bool:
        """ブックマーク更新"""
        valid_fields = ["url", "title", "description", "tags", "category"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        with self._get_connection() as conn:
            set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])
            cursor = conn.execute(f"""
                UPDATE bookmarks SET {set_clause} WHERE id = ?
            """, list(updates.values()) + [bookmark_id])
            return cursor.rowcount > 0

    def delete_bookmark(self, bookmark_id: int) -> bool:
        """ブックマーク削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM bookmarks WHERE id = ?", (bookmark_id,))
            return cursor.rowcount > 0

    def get_categories(self) -> List[str]:
        """カテゴリ一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT DISTINCT category FROM bookmarks
                WHERE category != ''
                ORDER BY category
            """).fetchall()
            return [row[0] for row in rows]

    def get_tags(self) -> List[str]:
        """タグ一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT DISTINCT tags FROM bookmarks
                WHERE tags != ''
            """).fetchall()

            tags = []
            for row in rows:
                tags.extend([t.strip() for t in row[0].split(',') if t.strip()])

            return sorted(set(tags))

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM bookmarks").fetchone()[0]

            # カテゴリ別
            category_dist = conn.execute("""
                SELECT category, COUNT(*) as cnt
                FROM bookmarks WHERE category != ''
                GROUP BY category ORDER BY cnt DESC LIMIT 10
            """).fetchall()

            # 最近追加
            recent_added = conn.execute("""
                SELECT COUNT(*) FROM bookmarks
                WHERE created_at >= datetime('now', '-7 days')
            """).fetchone()[0]

            # 最近アクセス
            recent_accessed = conn.execute("""
                SELECT COUNT(*) FROM bookmarks
                WHERE last_accessed >= datetime('now', '-7 days')
            """).fetchone()[0]

            return dict((
                ("total_bookmarks", total),
                ("recent_added", recent_added),
                ("recent_accessed", recent_accessed),
                ("top_categories", {c[0]: c[1] for c in category_dist})
            ))


if __name__ == "__main__":
    db = EroticBookmarkAgentDB()
    db.initialize()

    # テスト
    db.add_bookmark(
        url="https://example.com",
        title="素晴らしい作品",
        description="最高の作品",
        tags="最高,おすすめ"
    )

    bookmarks = db.list_bookmarks()
    print("ブックマーク数: " + str(len(bookmarks)))

    stats = db.get_stats()
    print("統計: " + str(stats))
