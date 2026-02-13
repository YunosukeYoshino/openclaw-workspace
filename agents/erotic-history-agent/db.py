#!/usr/bin/env python3
"""
えっちコンテンツ閲覧履歴エージェント - データベースモジュール
Erotic Content History Agent - Database Module

SQLiteを使用したデータ永続化機能
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager


class EroticHistoryAgentDB:
    """えっちコンテンツ閲覧履歴エージェント データベースクラス"""

    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        self.db_path = Path(db_path) if db_path else Path(__file__).parent / "erotic-history-agent.db"

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
            # 履歴テーブル
            conn.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_id TEXT NOT NULL,
                    content_title TEXT NOT NULL,
                    artist TEXT,
                    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tags TEXT,
                    source TEXT
                )
            """)

            # インデックス作成
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_content_id ON history(content_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_title ON history(content_title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_artist ON history(artist)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_viewed ON history(viewed_at)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_history_source ON history(source)")

    def add_history(self, content_id: str, content_title: str, artist: str = "",
                    tags: str = "", source: str = "") -> int:
        """履歴追加"""
        now = datetime.now().isoformat()
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO history
                (content_id, content_title, artist, viewed_at, tags, source)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (content_id, content_title, artist, now, tags, source))
            return cursor.lastrowid

    def get_history(self, history_id: int) -> Optional[Dict[str, Any]]:
        """履歴取得"""
        with self._get_connection() as conn:
            row = conn.execute("SELECT * FROM history WHERE id = ?", (history_id,)).fetchone()
            return dict(row) if row else None

    def list_history(self, limit: int = 50, offset: int = 0,
                     artist: str = None, source: str = None,
                     sort_by: str = "viewed_at", order: str = "DESC") -> List[Dict[str, Any]]:
        """履歴一覧"""
        valid_sort = ["id", "content_title", "artist", "viewed_at", "source"]
        valid_order = ["ASC", "DESC"]

        sort_by = sort_by if sort_by in valid_sort else "viewed_at"
        order = order.upper() if order.upper() in valid_order else "DESC"

        query = "SELECT * FROM history WHERE 1=1"
        params = []

        if artist:
            query += " AND artist LIKE ?"
            params.append(f"%{artist}%")
        if source:
            query += " AND source = ?"
            params.append(source)

        query += f" ORDER BY {sort_by} {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def search_history(self, query: str, limit: int = 50) -> List[Dict[str, Any]]:
        """履歴検索"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM history
                WHERE content_id LIKE ? OR content_title LIKE ? OR artist LIKE ?
                   OR tags LIKE ? OR source LIKE ?
                ORDER BY viewed_at DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_history_by_artist(self, artist: str, limit: int = 50) -> List[Dict[str, Any]]:
        """アーティストで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM history
                WHERE artist LIKE ?
                ORDER BY viewed_at DESC
                LIMIT ?
            """, (f"%{artist}%", limit)).fetchall()
            return [dict(row) for row in rows]

    def get_history_by_source(self, source: str, limit: int = 50) -> List[Dict[str, Any]]:
        """ソースで取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM history
                WHERE source = ?
                ORDER BY viewed_at DESC
                LIMIT ?
            """, (source, limit)).fetchall()
            return [dict(row) for row in rows]

    def get_recent_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """最近の履歴"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM history
                ORDER BY viewed_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_history_date_range(self, start_date: str, end_date: str, limit: int = 100) -> List[Dict[str, Any]]:
        """日付範囲で履歴取得"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM history
                WHERE viewed_at >= ? AND viewed_at <= ?
                ORDER BY viewed_at DESC
                LIMIT ?
            """, (start_date, end_date, limit)).fetchall()
            return [dict(row) for row in rows]

    def get_unique_content(self, limit: int = 100) -> List[Dict[str, Any]]:
        """一意なコンテンツ（重複排除）"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT MAX(id) as id, content_id, content_title, artist, MAX(viewed_at) as viewed_at, tags, source
                FROM history
                GROUP BY content_id
                ORDER BY MAX(viewed_at) DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def get_most_viewed(self, limit: int = 10) -> List[Dict[str, Any]]:
        """最多閲覧コンテンツ"""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT content_id, content_title, artist, COUNT(*) as view_count,
                       MAX(viewed_at) as last_viewed
                FROM history
                GROUP BY content_id
                ORDER BY view_count DESC
                LIMIT ?
            """, (limit,)).fetchall()
            return [dict(row) for row in rows]

    def delete_history(self, history_id: int) -> bool:
        """履歴削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM history WHERE id = ?", (history_id,))
            return cursor.rowcount > 0

    def clear_old_history(self, days: int = 30) -> int:
        """古い履歴を削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM history
                WHERE viewed_at < datetime('now', '-' || ? || ' days')
            """, (days,))
            return cursor.rowcount

    def clear_all_history(self) -> int:
        """全履歴削除"""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM history")
            return cursor.rowcount

    def get_stats(self) -> Dict[str, Any]:
        """統計情報取得"""
        with self._get_connection() as conn:
            total = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]

            # 一意なコンテンツ数
            unique = conn.execute("SELECT COUNT(DISTINCT content_id) FROM history").fetchone()[0]

            # アーティスト別
            top_artist = conn.execute("""
                SELECT artist, COUNT(*) as cnt
                FROM history WHERE artist != ''
                GROUP BY artist ORDER BY cnt DESC LIMIT 1
            """).fetchone()

            # ソース別
            source_dist = conn.execute("""
                SELECT source, COUNT(*) as cnt
                FROM history WHERE source != ''
                GROUP BY source ORDER BY cnt DESC
            """).fetchall()

            # 最近7日間の閲覧数
            recent_week = conn.execute("""
                SELECT COUNT(*) FROM history
                WHERE viewed_at >= datetime('now', '-7 days')
            """).fetchone()[0]

            # 今日の閲覧数
            today = conn.execute("""
                SELECT COUNT(*) FROM history
                WHERE viewed_at >= datetime('now', 'start of day')
            """).fetchone()[0]

            return dict((
                ("total_views", total),
                ("unique_content", unique),
                ("top_artist", top_artist[0] if top_artist else "なし"),
                ("sources", {s[0]: s[1] for s in source_dist}),
                ("views_last_7days", recent_week),
                ("views_today", today)
            ))


if __name__ == "__main__":
    db = EroticHistoryAgentDB()
    db.initialize()

    # テスト
    db.add_history(
        content_id="001",
        content_title="素晴らしい作品",
        artist="名前なし",
        tags="最高,おすすめ"
    )

    history = db.list_history()
    print("履歴数: " + str(len(history)))

    stats = db.get_stats()
    print("統計: " + str(stats))
