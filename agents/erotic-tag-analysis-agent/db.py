#!/usr/bin/env python3
"""
えっちタグ高度分析エージェント データベース管理 / Erotic Tag Advanced Analysis Agent Database Management
erotic-tag-analysis-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class EroticAdvancedDB:
    """えっちコンテンツ高度検索・キュレーションデータベース管理クラス"""

    def __init__(self, db_path: str = "data/erotic_advanced.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self.connect()

    def connect(self):
        """データベース接続"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def execute_query(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """クエリ実行"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = None) -> int:
        """更新クエリ実行"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        self.conn.commit()
        return cursor.lastrowid

    def create_content(
        self,
        content_id: str,
        title: str,
        artist: str,
        source: str,
        url: str,
        tags: str,
        description: str = ""
    ) -> int:
        """コンテンツ作成"""
        query = """
            INSERT OR REPLACE INTO contents
            (content_id, title, artist, source, url, tags, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(
            query,
            (content_id, title, artist, source, url, tags, description, datetime.now().isoformat())
        )

    def get_content(self, content_id: str) -> Optional[Dict]:
        """コンテンツ取得"""
        rows = self.execute_query(
            "SELECT * FROM contents WHERE content_id = ?",
            (content_id,)
        )
        return dict(rows[0]) if rows else None

    def list_contents(
        self,
        tag: Optional[str] = None,
        artist: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """コンテンツ一覧"""
        query = "SELECT * FROM contents WHERE 1=1"
        params = []

        if tag:
            query += " AND tags LIKE ?"
            params.append(f"%{tag}%")

        if artist:
            query += " AND artist = ?"
            params.append(artist)

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def create_tag(
        self,
        tag_name: str,
        category: str = "",
        related_tags: str = ""
    ) -> int:
        """タグ作成"""
        query = """
            INSERT OR IGNORE INTO tags (tag_name, category, related_tags)
            VALUES (?, ?, ?)
        """
        return self.execute_update(query, (tag_name, category, related_tags))

    def get_tag(self, tag_name: str) -> Optional[Dict]:
        """タグ取得"""
        rows = self.execute_query(
            "SELECT * FROM tags WHERE tag_name = ?",
            (tag_name,)
        )
        return dict(rows[0]) if rows else None

    def list_tags(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """タグ一覧"""
        query = "SELECT * FROM tags WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY count DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def create_collection(
        self,
        collection_name: str,
        description: str,
        tags: str,
        auto_update: bool = True
    ) -> int:
        """コレクション作成"""
        query = """
            INSERT INTO collections (collection_name, description, tags, auto_update)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (collection_name, description, tags, 1 if auto_update else 0))

    def get_collection(self, collection_id: int) -> Optional[Dict]:
        """コレクション取得"""
        rows = self.execute_query(
            "SELECT * FROM collections WHERE id = ?",
            (collection_id,)
        )
        return dict(rows[0]) if rows else None

    def list_collections(self, limit: int = 50) -> List[Dict]:
        """コレクション一覧"""
        rows = self.execute_query(
            "SELECT * FROM collections ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in rows]

    def add_to_collection(self, collection_id: int, content_id: str) -> int:
        """コレクションにコンテンツ追加"""
        query = """
            INSERT OR IGNORE INTO collection_items (collection_id, content_id)
            VALUES (?, ?)
        """
        return self.execute_update(query, (collection_id, content_id))

    def remove_from_collection(self, collection_id: int, content_id: str) -> bool:
        """コレクションからコンテンツ削除"""
        query = "DELETE FROM collection_items WHERE collection_id = ? AND content_id = ?"
        self.execute_update(query, (collection_id, content_id))
        return self.conn.total_changes > 0

    def get_collection_contents(self, collection_id: int) -> List[Dict]:
        """コレクションのコンテンツ取得"""
        query = """
            SELECT c.* FROM contents c
            INNER JOIN collection_items ci ON c.content_id = ci.content_id
            WHERE ci.collection_id = ?
            ORDER BY ci.added_at DESC
        """
        rows = self.execute_query(query, (collection_id,))
        return [dict(row) for row in rows]

    def create_search_log(
        self,
        query: str,
        results_count: int,
        clicked_contents: Optional[List[str]] = None
    ) -> int:
        """検索ログ作成"""
        import json as json_module
        clicked_json = json_module.dumps(clicked_contents) if clicked_contents else None
        query_str = """
            INSERT INTO search_logs (query, results_count, clicked_contents)
            VALUES (?, ?, ?)
        """
        return self.execute_update(query_str, (query, results_count, clicked_json))

    def get_search_logs(
        self,
        limit: int = 100
    ) -> List[Dict]:
        """検索ログ取得"""
        rows = self.execute_query(
            "SELECT * FROM search_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """統計情報取得"""
        total_contents = self.execute_query("SELECT COUNT(*) FROM contents")[0][0]
        total_tags = self.execute_query("SELECT COUNT(*) FROM tags")[0][0]
        total_collections = self.execute_query("SELECT COUNT(*) FROM collections")[0][0]
        total_searches = self.execute_query("SELECT COUNT(*) FROM search_logs")[0][0]

        # アーティスト別分布
        artists = self.execute_query("""
            SELECT artist, COUNT(*) as count
            FROM contents
            GROUP BY artist
            ORDER BY count DESC
            LIMIT 10
        """)

        return {
            "total_contents": total_contents,
            "total_tags": total_tags,
            "total_collections": total_collections,
            "total_searches": total_searches,
            "top_artists": [dict(artist) for artist in artists]
        }


if __name__ == "__main__":
    import json
    with EroticAdvancedDB() as db:
        stats = db.get_statistics()
        print("統計情報:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
