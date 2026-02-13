#!/usr/bin/env python3
"""
えっちコンテンツ高度検索エージェント - データベースモジュール
Erotic Content Advanced Search Agent - Database Module

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class EroticSearchAgentDB:
    """えっちコンテンツ高度検索エージェント データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "erotic-search-agent.db"

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
            # 検索インデックステーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    artist TEXT,
                    tags TEXT,
                    description TEXT,
                    source TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # 検索クエリ履歴テーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS search_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    results_count INTEGER DEFAULT 0,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_index_content_id ON search_index(content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_index_title ON search_index(title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_index_artist ON search_index(artist)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_index_tags ON search_index(tags)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_index_source ON search_index(source)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_index_indexed ON search_index(indexed_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_queries_query ON search_queries(query)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_search_queries_executed ON search_queries(executed_at)")

    def add_to_index(self, content_id: str, title: str, artist: str = "",
                     tags: str = "", description: str = "", source: str = "") -> int:
        """インデックスに追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT OR REPLACE INTO search_index
                (content_id, title, artist, tags, description, source, indexed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (content_id, title, artist, tags, description, source, now))
            return cursor.lastrowid

    def get_indexed_content(self, index_id: int) -> Optional[Dict[str, Any]]:
        """インデックスされたコンテンツ取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM search_index WHERE id = ?", (index_id,)).fetchone()
            return dict(row) if row else None

    def search(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM search_index
                WHERE content_id LIKE ? OR title LIKE ? OR artist LIKE ?
                   OR tags LIKE ? OR description LIKE ? OR source LIKE ?
                ORDER BY
                    CASE
                        WHEN title LIKE ? THEN 1
                        WHEN artist LIKE ? THEN 2
                        WHEN tags LIKE ? THEN 3
                        ELSE 4
                    END,
                    indexed_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%",
                  f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()

            # 検索クエリ履歴に記録
            self._log_search_query(query, len(rows))

            return [dict(row) for row in rows]

    def search_by_title(self, title: str, limit: int = 50) -> List[Dict[str, Any]]:
        """タイトルで検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM search_index
                WHERE title LIKE ?
                ORDER BY indexed_at DESC
                LIMIT ?
            """, (f"%{title}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def search_by_artist(self, artist: str, limit: int = 50) -> List[Dict[str, Any]]:
        """アーティストで検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM search_index
                WHERE artist LIKE ?
                ORDER BY indexed_at DESC
                LIMIT ?
            """, (f"%{artist}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def search_by_tags(self, tags: List[str], limit: int = 50) -> List[Dict[str, Any]]:
        """タグで検索"""
        with self._get_connection() as conn:
            query = "SELECT * FROM search_index WHERE 1=1"
            params = []

            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")

            query += " ORDER BY indexed_at DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def search_by_source(self, source: str, limit: int = 50) -> List[Dict[str, Any]]:
        """ソースで検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM search_index
                WHERE source LIKE ?
                ORDER BY indexed_at DESC
                LIMIT ?
            """, (f"%{source}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def advanced_search(self, title: str = "", artist: str = "", tags: List[str] = None,
                       source: str = "", limit: int = 50) -> List[Dict[str, Any]]:
        """高度検索"""
        query = "SELECT * FROM search_index WHERE 1=1"
        params = []

        if title:
            query += " AND title LIKE ?"
            params.append(f"%{title}%")
        if artist:
            query += " AND artist LIKE ?"
            params.append(f"%{artist}%")
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        if source:
            query += " AND source LIKE ?"
            params.append(f"%{source}%")

        query += " ORDER BY indexed_at DESC LIMIT ?"
        params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def list_index(self, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """インデックス一覧"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM search_index
                ORDER BY indexed_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset)).fetchall()
            return [dict(row) for row in rows]

    def update_index(self, index_id: int, **kwargs) -> bool:
        """インデックス更新"""
        valid_fields = ["content_id", "title", "artist", "tags", "description", "source"]
        updates = dict((k, v) for k, v in kwargs.items() if k in valid_fields)

        if not updates:
            return False

        with self._get_connection() as conn:
            set_clause = ", ".join([str(k) + " = ?" for k in updates.keys()])
            cursor = conn.execute(f"""
                UPDATE search_index SET {set_clause}, indexed_at = ? WHERE id = ?
            """, list(updates.values()) + [datetime.now().isoformat(), index_id])
            return cursor.rowcount > 0

    def remove_from_index(self, index_id: int) -> bool:
        """インデックスから削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM search_index WHERE id = ?", (index_id,))
            return cursor.rowcount > 0

    def clear_index(self) -> int:
        """インデックスをクリア"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM search_index")
            return cursor.rowcount

    def _log_search_query(self, query: str, results_count: int) -> None:
        """検索クエリ履歴を記録"""
        with self._get_connection() as conn:
            conn.execute("""
                INSERT INTO search_queries (query, results_count, executed_at)
                VALUES (?, ?, ?)
            """, (query, results_count, datetime.now().isoformat()))

    def get_search_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """検索履歴取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM search_queries
                ORDER BY executed_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """人気の検索キーワード"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT query, COUNT(*) as search_count,
                       SUM(results_count) as total_results,
                       MAX(executed_at) as last_searched
                FROM search_queries
                GROUP BY query
                ORDER BY search_count DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total_indexed = conn.execute("SELECT COUNT(*) FROM search_index").fetchone()[0]
            total_searches = conn.execute("SELECT COUNT(*) FROM search_queries").fetchone()[0]

            # アーティスト別
            top_artist = conn.execute("""
                SELECT artist, COUNT(*) as cnt
                FROM search_index WHERE artist != ''
                GROUP BY artist ORDER BY cnt DESC LIMIT 1
            """).fetchone()

            # ソース別
            source_dist = conn.execute("""
                SELECT source, COUNT(*) as cnt
                FROM search_index WHERE source != ''
                GROUP BY source ORDER BY cnt DESC
            """).fetchall()

            # 最近のインデックス追加
            recent_indexed = conn.execute("""
                SELECT COUNT(*) FROM search_index
                WHERE indexed_at >= datetime('now', '-7 days')
            """).fetchone()[0]

            return dict((
                ("total_indexed", total_indexed),
                ("total_searches", total_searches),
                ("top_artist", top_artist[0] if top_artist else "なし"),
                ("sources", {s[0]: s[1] for s in source_dist}),
                ("recently_indexed", recent_indexed)
            ))


if __name__ == "__main__":
    db = EroticSearchAgentDB()
    db.initialize()

    # テスト
    db.add_to_index(
        content_id="001",
        title="素晴らしい作品",
        artist="名前なし",
        tags="最高,おすすめ"
    )

    indexed = db.list_index()
    print("インデックス数: " + str(len(indexed)))

    results = db.search("最高")
    print("検索結果: " + str(len(results)))

    stats = db.get_stats()
    print("統計: " + str(stats))
