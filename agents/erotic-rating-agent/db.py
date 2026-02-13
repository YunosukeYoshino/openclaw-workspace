#!/usr/bin/env python3
"""
えっちコンテンツ評価レビューエージェント - データベースモジュール

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class EroticRatingAgentDB:
    """えっちコンテンツ評価レビューエージェント データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "erotic-rating-agent.db"

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
            # 評価テーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS ratings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    artist TEXT,
                    description TEXT,
                    source TEXT,
                    url TEXT,
                    overall_rating INTEGER DEFAULT 0,
                    art_quality INTEGER,
                    story_quality INTEGER,
                    erotic_quality INTEGER,
                    technical_quality INTEGER,
                    tags TEXT,
                    review_text TEXT,
                    is_recommended INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(title, artist)
                )
            """)

            # 評価カテゴリーテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rating_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # レビューコメントテーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS review_comments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rating_id INTEGER NOT NULL,
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (rating_id) REFERENCES ratings(id) ON DELETE CASCADE
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_title ON ratings(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_artist ON ratings(artist)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_overall ON ratings(overall_rating)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_recommended ON ratings(is_recommended)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ratings_created ON ratings(created_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_comments_rating ON review_comments(rating_id)")

    def add_rating(self, title: str, artist: str = "", description: str = "",
                   source: str = "", url: str = "", overall_rating: int = 0,
                   art_quality: int = None, story_quality: int = None,
                   erotic_quality: int = None, technical_quality: int = None,
                   tags: str = "", review_text: str = "",
                   is_recommended: bool = False) -> int:
        """評価追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO ratings
                (title, artist, description, source, url, overall_rating,
                 art_quality, story_quality, erotic_quality, technical_quality,
                 tags, review_text, is_recommended, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT created_at FROM ratings WHERE title = ? AND artist = ?), ?), ?)
            """, (title, artist, description, source, url, overall_rating,
                  art_quality, story_quality, erotic_quality, technical_quality,
                  tags, review_text, 1 if is_recommended else 0,
                  title, artist, now, now))
            return cursor.lastrowid

    def get_rating(self, rating_id: int) -> Optional[Dict[str, Any]]:
        """評価取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM ratings WHERE id = ?", (rating_id,)).fetchone()
            return dict(row) if row else None

    def list_ratings(self, limit: int = 50, offset: int = 0,
                    min_rating: int = None, is_recommended: bool = None,
                    sort_by: str = "overall_rating", order: str = "DESC") -> List[Dict[str, Any]]:
        """評価一覧"""
        valid_sort = ["id", "title", "artist", "overall_rating", "art_quality",
                     "story_quality", "created_at", "updated_at"]
        valid_order = ["ASC", "DESC"]

        sort_by = sort_by if sort_by in valid_sort else "overall_rating"
        order = order.upper() if order.upper() in valid_order else "DESC"

        query = "SELECT * FROM ratings WHERE 1=1"
        params = []

        if min_rating is not None:
            query += " AND overall_rating >= ?"
            params.append(min_rating)
        if is_recommended is not None:
            query += " AND is_recommended = ?"
            params.append(1 if is_recommended else 0)

        query += f" ORDER BY {sort_by} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def search_ratings(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """評価検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM ratings
                WHERE title LIKE ? OR artist LIKE ? OR description LIKE ?
                   OR tags LIKE ? OR review_text LIKE ?
                ORDER BY overall_rating DESC, created_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_ratings_by_tag(self, tag: str, limit: int = 50) -> List[Dict[str, Any]]:
        """タグで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM ratings
                WHERE tags LIKE ?
                ORDER BY overall_rating DESC, created_at DESC
                LIMIT ?
            """, (f"%{tag}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_ratings_by_artist(self, artist: str, limit: int = 50) -> List[Dict[str, Any]]:
        """アーティストで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM ratings
                WHERE artist LIKE ?
                ORDER BY overall_rating DESC, created_at DESC
                LIMIT ?
            """, (f"%{artist}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def update_rating(self, rating_id: int, **kwargs) -> bool:
        """評価更新"""
        valid_fields = ["title", "artist", "description", "source", "url",
                       "overall_rating", "art_quality", "story_quality",
                       "erotic_quality", "technical_quality", "tags",
                       "review_text", "is_recommended"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        if "is_recommended" in updates:
            updates["is_recommended"] = 1 if updates["is_recommended"] else 0

        updates["updated_at"] = datetime.now().isoformat()
        set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])

        with self._get_connection() as conn:
            query = f"""
                UPDATE ratings SET {set_clause}, updated_at = ? WHERE id = ?
            """
            cursor = conn.execute(query, list(updates.values()) + [rating_id])
            return cursor.rowcount > 0

    def delete_rating(self, rating_id: int) -> bool:
        """評価削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM ratings WHERE id = ?", (rating_id,))
            return cursor.rowcount > 0

    def add_comment(self, rating_id: int, comment: str) -> int:
        """コメント追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO review_comments (rating_id, comment, created_at)
                VALUES (?, ?, ?)
            """, (rating_id, comment, now))
            return cursor.lastrowid

    def get_comments(self, rating_id: int) -> List[Dict[str, Any]]:
        """コメント取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM review_comments
                WHERE rating_id = ?
                ORDER BY created_at ASC
            """, (rating_id,)).fetchall()
            return [dict(row) for row in rows]

    def delete_comment(self, comment_id: int) -> bool:
        """コメント削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM review_comments WHERE id = ?", (comment_id,))
            return cursor.rowcount > 0

    def get_top_rated(self, limit: int = 10) -> List[Dict[str, Any]]:
        """高評価順に取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM ratings
                WHERE overall_rating > 0
                ORDER BY overall_rating DESC, created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_recommended(self, limit: int = 10) -> List[Dict[str, Any]]:
        """おすすめ取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM ratings
                WHERE is_recommended = 1
                ORDER BY overall_rating DESC, created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM ratings").fetchone()[0]
            avg_overall = conn.execute("SELECT AVG(overall_rating) FROM ratings WHERE overall_rating > 0").fetchone()[0] or 0
            avg_art = conn.execute("SELECT AVG(art_quality) FROM ratings WHERE art_quality > 0").fetchone()[0] or 0
            avg_story = conn.execute("SELECT AVG(story_quality) FROM ratings WHERE story_quality > 0").fetchone()[0] or 0
            avg_erotic = conn.execute("SELECT AVG(erotic_quality) FROM ratings WHERE erotic_quality > 0").fetchone()[0] or 0
            recommended_count = conn.execute("SELECT COUNT(*) FROM ratings WHERE is_recommended = 1").fetchone()[0]

            return dict((
                ("total_ratings", total),
                ("average_overall", round(avg_overall, 2)),
                ("average_art_quality", round(avg_art, 2)),
                ("average_story_quality", round(avg_story, 2)),
                ("average_erotic_quality", round(avg_erotic, 2)),
                ("recommended_count", recommended_count)
            ))


if __name__ == "__main__":
    db = EroticRatingAgentDB()
    db.initialize()

    # テスト
    db.add_rating(
        title="素晴らしい作品",
        overall_rating=5,
        art_quality=5,
        story_quality=4,
        review_text="傑作です！"
    )

    ratings = db.list_ratings()
    print("評価数: " + str(len(ratings)))

    stats = db.get_stats()
    print("統計: " + str(stats))
