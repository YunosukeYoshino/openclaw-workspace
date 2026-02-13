#!/usr/bin/env python3
"""
お気に入りのえっちな作品コレクションエージェント - データベースモジュール

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class EroticFavoritesAgentDB:
    """お気に入りのえっちな作品コレクションエージェント データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "erotic-favorites-agent.db"

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
            # お気に入り作品テーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT,
                    description TEXT,
                    source TEXT,
                    url TEXT,
                    category TEXT,
                    tags TEXT,
                    favorite_rank INTEGER DEFAULT 0,
                    is_public INTEGER DEFAULT 0,
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, artist)
                )
            """)

            # コレクショングループテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    icon TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 作品-コレクション紐付けテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS collection_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection_id INTEGER NOT NULL,
                    favorite_id INTEGER NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE,
                    FOREIGN KEY (favorite_id) REFERENCES favorites(id) ON DELETE CASCADE,
                    UNIQUE(collection_id, favorite_id)
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_favorites_title ON favorites(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_favorites_artist ON favorites(artist)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_favorites_category ON favorites(category)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_favorites_rank ON favorites(favorite_rank)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_favorites_created ON favorites(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_collections_name ON collections(name)")

    def add_favorite(self, title: str, artist: str = "", description: str = "",
                     source: str = "", url: str = "", category: str = "",
                     tags: str = "", favorite_rank: int = 0,
                     is_public: bool = False, notes: str = "") -> int:
        """お気に入り追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO favorites
                (title, artist, description, source, url, category, tags,
                 favorite_rank, is_public, notes, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM favorites WHERE title = ? AND artist = ?), ?), ?)
            """, (title, artist, description, source, url, category, tags,
                  favorite_rank, 1 if is_public else 0, notes,
                  title, artist, now, now))
            return cursor.lastrowid

    def get_favorite(self, favorite_id: int) -> Optional[Dict[str, Any]]:
        """お気に入り取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM favorites WHERE id = ?", (favorite_id,)).fetchone()
            return dict(row) if row else None

    def list_favorites(self, limit: int = 50, offset: int = 0,
                      category: str = None, is_public: bool = None,
                      sort_by: str = "favorite_rank", order: str = "DESC") -> List[Dict[str, Any]]:
        """お気に入り一覧"""
        valid_sort = ["id", "title", "artist", "category", "favorite_rank", "created_at", "updated_at"]
        valid_order = ["ASC", "DESC"]

        sort_by = sort_by if sort_by in valid_sort else "favorite_rank"
        order = order.upper() if order.upper() in valid_order else "DESC"

        query = "SELECT * FROM favorites WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if is_public is not None:
            query += " AND is_public = ?"
            params.append(1 if is_public else 0)

        query += f" ORDER BY {sort_by} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def search_favorites(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """お気に入り検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM favorites
                WHERE title LIKE ? OR artist LIKE ? OR description LIKE ?
                   OR tags LIKE ? OR notes LIKE ?
                ORDER BY favorite_rank DESC, created_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_favorites_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """カテゴリで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM favorites
                WHERE category = ?
                ORDER BY favorite_rank DESC, created_at DESC
                LIMIT ?
            """, (category, limit)).fetchall()
            return [dict(row) for row in rows]

    def get_favorites_by_artist(self, artist: str, limit: int = 50) -> List[Dict[str, Any]]:
        """アーティストで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM favorites
                WHERE artist LIKE ?
                ORDER BY favorite_rank DESC, created_at DESC
                LIMIT ?
            """, (f"%{artist}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def update_favorite(self, favorite_id: int, **kwargs) -> bool:
        """お気に入り更新"""
        valid_fields = ["title", "artist", "description", "source", "url",
                       "category", "tags", "favorite_rank", "is_public", "notes"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        # is_publicを0/1に変換
        if "is_public" in updates:
            updates["is_public"] = 1 if updates["is_public"] else 0

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])

        with self._get_connection() as conn:
            query = f"""
                UPDATE favorites SET {set_clause}, updated_at = ? WHERE id = ?
            """
            cursor = conn.execute(query, list(updates.values()) + [favorite_id])
            return cursor.rowcount > 0

    def delete_favorite(self, favorite_id: int) -> bool:
        """お気に入り削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM favorites WHERE id = ?", (favorite_id,))
            return cursor.rowcount > 0

    def create_collection(self, name: str, description: str = "", icon: str = "") -> int:
        """コレクション作成"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO collections (name, description, icon, created_at)
                VALUES (?, ?, ?, ?)
            """, (name, description, icon, now))
            return cursor.lastrowid

    def add_to_collection(self, collection_id: int, favorite_id: int) -> bool:
        """コレクションに追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            try:
                cursor = conn.execute("""
                    INSERT OR IGNORE INTO collection_items (collection_id, favorite_id, added_at)
                    VALUES (?, ?, ?)
                """, (collection_id, favorite_id, now))
                return cursor.rowcount > 0
            except Exception:
                return False

    def get_collection(self, collection_id: int) -> Optional[Dict[str, Any]]:
        """コレクション取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM collections WHERE id = ?", (collection_id,)).fetchone()
            return dict(row) if row else None

    def list_collections(self) -> List[Dict[str, Any]]:
        """コレクション一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT c.*,
                       (SELECT COUNT(*) FROM collection_items WHERE collection_id = c.id) as item_count
                FROM collections c
                ORDER BY c.created_at DESC
            """).fetchall()
            return [dict(row) for row in rows]

    def get_collection_favorites(self, collection_id: int) -> List[Dict[str, Any]]:
        """コレクション内のお気に入り一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT f.* FROM favorites f
                INNER JOIN collection_items ci ON f.id = ci.favorite_id
                WHERE ci.collection_id = ?
                ORDER BY ci.added_at DESC
            """, (collection_id,)).fetchall()
            return [dict(row) for row in rows]

    def remove_from_collection(self, collection_id: int, favorite_id: int) -> bool:
        """コレクションから削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM collection_items
                WHERE collection_id = ? AND favorite_id = ?
            """, (collection_id, favorite_id))
            return cursor.rowcount > 0

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
            public_count = conn.execute("SELECT COUNT(*) FROM favorites WHERE is_public = 1").fetchone()[0]
            collections = conn.execute("SELECT COUNT(*) FROM collections").fetchone()[0]
            top_category = conn.execute("""
                SELECT category, COUNT(*) as cnt
                FROM favorites WHERE category != ''
                GROUP BY category ORDER BY cnt DESC LIMIT 1
            """).fetchone()
            top_artist = conn.execute("""
                SELECT artist, COUNT(*) as cnt
                FROM favorites WHERE artist != ''
                GROUP BY artist ORDER BY cnt DESC LIMIT 1
            """).fetchone()

            return dict((
                ("total_favorites", total),
                ("public_favorites", public_count),
                ("private_favorites", total - public_count),
                ("total_collections", collections),
                ("top_category", top_category[0] if top_category else "なし"),
                ("top_artist", top_artist[0] if top_artist else "なし")
            ))


if __name__ == "__main__":
    db = EroticFavoritesAgentDB()
    db.initialize()

    # テスト
    db.add_favorite(
        title="素晴らしい作品",
        artist="名前なし",
        description="最高の作品",
        tags="最高,おすすめ"
    )

    favorites = db.list_favorites()
    print("お気に入り数: " + str(len(favorites)))

    stats = db.get_stats()
    print("統計: " + str(stats))
