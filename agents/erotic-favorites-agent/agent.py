#!/usr/bin/env python3
"""
お気に入りのえっちな作品コレクションエージェント

お気に入りのえっちな作品を管理・コレクションするエージェント
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class EroticFavoritesAgent:
    """お気に入りのえっちな作品コレクションエージェント"""

    def __init__(self, db_path: str = None):
        """初期化"""
        self.db_path = db_path or Path(__file__).parent / "erotic_favorites.db"
        self.conn = None
        self._init_db()

    def _init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        # お気に入り作品テーブル
        self.conn.execute("""
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
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # コレクショングループテーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                icon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 作品-コレクション紐付けテーブル
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS collection_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                favorite_id INTEGER NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (collection_id) REFERENCES collections(id),
                FOREIGN KEY (favorite_id) REFERENCES favorites(id),
                UNIQUE(collection_id, favorite_id)
            )
        """)

        self.conn.commit()

    def add_favorite(self, title: str, artist: str = "", description: str = "",
                     source: str = "", url: str = "", category: str = "",
                     tags: str = "", favorite_rank: int = 0,
                     is_public: bool = False, notes: str = "") -> int:
        """お気に入り追加"""
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            INSERT INTO favorites
            (title, artist, description, source, url, category, tags,
             favorite_rank, is_public, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, artist, description, source, url, category, tags,
              favorite_rank, 1 if is_public else 0, notes, now, now))
        self.conn.commit()
        return cursor.lastrowid

    def get_favorite(self, favorite_id: int) -> dict:
        """お気に入り取得"""
        row = self.conn.execute("SELECT * FROM favorites WHERE id = ?", (favorite_id,)).fetchone()
        return dict(row) if row else None

    def list_favorites(self, limit: int = 50, offset: int = 0,
                      category: str = None, is_public: bool = None) -> list:
        """お気に入り一覧"""
        query = "SELECT * FROM favorites WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)
        if is_public is not None:
            query += " AND is_public = ?"
            params.append(1 if is_public else 0)

        query += " ORDER BY favorite_rank DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        rows = self.conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def search_favorites(self, query: str) -> list:
        """お気に入り検索"""
        rows = self.conn.execute("""
            SELECT * FROM favorites
            WHERE title LIKE ? OR artist LIKE ? OR description LIKE ?
               OR tags LIKE ? OR notes LIKE ?
            ORDER BY favorite_rank DESC, created_at DESC
        """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
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

        self.conn.execute(f"""
            UPDATE favorites SET {set_clause}, updated_at = ? WHERE id = ?
        """, list(updates.values()) + [favorite_id])
        self.conn.commit()
        return True

    def delete_favorite(self, favorite_id: int) -> bool:
        """お気に入り削除"""
        # コレクションからの紐付けも削除
        self.conn.execute("DELETE FROM collection_items WHERE favorite_id = ?", (favorite_id,))
        self.conn.execute("DELETE FROM favorites WHERE id = ?", (favorite_id,))
        self.conn.commit()
        return True

    def create_collection(self, name: str, description: str = "", icon: str = "") -> int:
        """コレクション作成"""
        now = datetime.now().isoformat()
        cursor = self.conn.execute("""
            INSERT INTO collections (name, description, icon, created_at)
            VALUES (?, ?, ?, ?)
        """, (name, description, icon, now))
        self.conn.commit()
        return cursor.lastrowid

    def add_to_collection(self, collection_id: int, favorite_id: int) -> bool:
        """コレクションに追加"""
        now = datetime.now().isoformat()
        try:
            self.conn.execute("""
                INSERT OR IGNORE INTO collection_items (collection_id, favorite_id, added_at)
                VALUES (?, ?, ?)
            """, (collection_id, favorite_id, now))
            self.conn.commit()
            return True
        except Exception:
            return False

    def get_collection(self, collection_id: int) -> dict:
        """コレクション取得"""
        row = self.conn.execute("SELECT * FROM collections WHERE id = ?", (collection_id,)).fetchone()
        return dict(row) if row else None

    def list_collections(self) -> list:
        """コレクション一覧"""
        rows = self.conn.execute("""
            SELECT c.*,
                   (SELECT COUNT(*) FROM collection_items WHERE collection_id = c.id) as item_count
            FROM collections c
            ORDER BY c.created_at DESC
        """).fetchall()
        return [dict(row) for row in rows]

    def get_collection_favorites(self, collection_id: int) -> list:
        """コレクション内のお気に入り一覧"""
        rows = self.conn.execute("""
            SELECT f.* FROM favorites f
            INNER JOIN collection_items ci ON f.id = ci.favorite_id
            WHERE ci.collection_id = ?
            ORDER BY ci.added_at DESC
        """, (collection_id,)).fetchall()
        return [dict(row) for row in rows]

    def get_stats(self) -> dict:
        """統計情報取得"""
        total = self.conn.execute("SELECT COUNT(*) FROM favorites").fetchone()[0]
        public_count = self.conn.execute("SELECT COUNT(*) FROM favorites WHERE is_public = 1").fetchone()[0]
        collections = self.conn.execute("SELECT COUNT(*) FROM collections").fetchone()[0]
        top_category = self.conn.execute("""
            SELECT category, COUNT(*) as cnt
            FROM favorites WHERE category != ''
            GROUP BY category ORDER BY cnt DESC LIMIT 1
        """).fetchone()

        return dict((
            ("total_favorites", total),
            ("public_favorites", public_count),
            ("private_favorites", total - public_count),
            ("total_collections", collections),
            ("top_category", top_category[0] if top_category else "なし")
        ))

    def close(self):
        """接続終了"""
        if self.conn:
            self.conn.close()

    def __del__(self):
        """デストラクタ"""
        self.close()


if __name__ == "__main__":
    agent = EroticFavoritesAgent()

    # テストお気に入り追加
    agent.add_favorite(
        title="素晴らしい作品",
        artist="名前なし",
        description="最高のえっちな作品",
        source="test",
        tags="最高,おすすめ"
    )

    # お気に入り一覧表示
    favorites = agent.list_favorites()
    for fav in favorites:
        print(str(fav['id']) + ": " + str(fav['title']) + " by " + str(fav['artist']))

    # 統計情報表示
    stats = agent.get_stats()
    print("\n統計: " + str(stats))
