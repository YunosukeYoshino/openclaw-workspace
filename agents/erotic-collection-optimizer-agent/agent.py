#!/usr/bin/env python3
"""
えっちコレクション最適化エージェント / Erotic Collection Optimization Agent
erotic-collection-optimizer-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json as json_module

class EroticCollectionOptimizerAgentAgent:
    """えっちコレクション最適化エージェント"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Path("data/erotic_advanced.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # コンテンツテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT UNIQUE NOT NULL,
                title TEXT,
                artist TEXT,
                source TEXT,
                url TEXT,
                tags TEXT,
                embedding BLOB,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # タグテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT UNIQUE NOT NULL,
                category TEXT,
                count INTEGER DEFAULT 0,
                related_tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # コンテンツタグ関連付けテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS content_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_id TEXT NOT NULL,
                tag_name TEXT NOT NULL,
                relevance REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(content_id, tag_name)
            )
        """)

        # 検索ログテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                results_count INTEGER,
                clicked_contents TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # キュレーションテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_name TEXT NOT NULL,
                description TEXT,
                tags TEXT,
                auto_update BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # コレクションアイテムテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collection_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL,
                content_id TEXT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(collection_id, content_id)
            )
        """)

        self.conn.commit()

    def add_content(self, content_id, title, artist, source, url, tags, description=""):
        """コンテンツを追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO contents (content_id, title, artist, source, url, tags, description, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (content_id, title, artist, source, url, tags, description, datetime.now().isoformat()))
        self.conn.commit()

        # タグの更新
        self.update_tags(content_id, tags)

        return cursor.lastrowid

    def update_tags(self, content_id, tags_str):
        """タグを更新"""
        cursor = self.conn.cursor()

        # 既存のタグ関連付けを削除
        cursor.execute("DELETE FROM content_tags WHERE content_id = ?", (content_id,))

        # タグをパース
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]

        for tag in tags:
            # タグを追加（存在しない場合）
            cursor.execute("""
                INSERT OR IGNORE INTO tags (tag_name, count)
                VALUES (?, 0)
            """, (tag,))
            cursor.execute("""
                UPDATE tags SET count = count + 1 WHERE tag_name = ?
            """, (tag,))

            # コンテンツタグ関連付けを追加
            cursor.execute("""
                INSERT OR REPLACE INTO content_tags (content_id, tag_name)
                VALUES (?, ?)
            """, (content_id, tag))

        self.conn.commit()

    def semantic_search(self, query, limit=20):
        """意味検索"""
        cursor = self.conn.cursor()

        # タグベースの簡易検索
        query_tags = [t.strip() for t in query.split() if t.strip()]

        conditions = []
        params = []

        for tag in query_tags:
            conditions.append("tags LIKE ?")
            params.append(f"%{tag}%")

        if conditions:
            query_str = " AND ".join(conditions)
            cursor.execute(f"""
                SELECT * FROM contents WHERE {query_str}
                ORDER BY updated_at DESC
                LIMIT ?
            """, params + [limit])
        else:
            cursor.execute("""
                SELECT * FROM contents
                ORDER BY updated_at DESC
                LIMIT ?
            """, (limit,))

        return cursor.fetchall()

    def get_related_contents(self, content_id, limit=10):
        """関連コンテンツを取得"""
        cursor = self.conn.cursor()

        # 同じタグを持つコンテンツを検索
        cursor.execute("""
            SELECT DISTINCT c.*
            FROM contents c
            INNER JOIN content_tags ct ON c.content_id = ct.content_id
            WHERE ct.tag_name IN (
                SELECT tag_name FROM content_tags WHERE content_id = ?
            ) AND c.content_id != ?
            ORDER BY COUNT(ct.tag_name) DESC, c.updated_at DESC
            LIMIT ?
        """, (content_id, content_id, limit))

        return cursor.fetchall()

    def get_top_tags(self, limit=50):
        """トップタグを取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM tags
            ORDER BY count DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()

    def create_collection(self, collection_name, description, tags, auto_update=True):
        """コレクションを作成"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO collections (collection_name, description, tags, auto_update)
            VALUES (?, ?, ?, ?)
        """, (collection_name, description, tags, 1 if auto_update else 0))
        self.conn.commit()
        return cursor.lastrowid

    def add_to_collection(self, collection_id, content_id):
        """コレクションにコンテンツを追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO collection_items (collection_id, content_id)
            VALUES (?, ?)
        """, (collection_id, content_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_collection_contents(self, collection_id):
        """コレクションのコンテンツを取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT c.* FROM contents c
            INNER JOIN collection_items ci ON c.content_id = ci.content_id
            WHERE ci.collection_id = ?
            ORDER BY ci.added_at DESC
        """, (collection_id,))
        return cursor.fetchall()

    def log_search(self, query, results_count, clicked_contents=None):
        """検索をログ"""
        cursor = self.conn.cursor()
        clicked_json = json_module.dumps(clicked_contents) if clicked_contents else None
        cursor.execute("""
            INSERT INTO search_logs (query, results_count, clicked_contents)
            VALUES (?, ?, ?)
        """, (query, results_count, clicked_json))
        self.conn.commit()
        return cursor.lastrowid

    def get_search_suggestions(self, query_prefix, limit=10):
        """検索候補を取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT DISTINCT query, COUNT(*) as freq
            FROM search_logs
            WHERE query LIKE ?
            GROUP BY query
            ORDER BY freq DESC
            LIMIT ?
        """, (f"{query_prefix}%", limit))
        return cursor.fetchall()

    def get_close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = EroticCollectionOptimizerAgentAgent()

    # サンプルデータ追加
    agent.add_content("er001", "美少女の冒険", "ArtistA", "pixiv", "https://example.com/1", "アニメ,美少女,冒険", "かわいい")
    agent.add_content("er002", "暗黒の儀式", "ArtistB", "twitter", "https://example.com/2", "ダーク,魔法,エルフ", "暗い系")
    agent.add_content("er003", "日常の幸せ", "ArtistA", "pixiv", "https://example.com/3", "日常,癒やし,スライス", "ほのぼの")

    # 検索
    results = agent.semantic_search("アニメ")
    print(f"検索結果: {len(results)}件")

    # タグ取得
    top_tags = agent.get_top_tags(5)
    print("\nトップタグ:")
    for tag in top_tags:
        print(f"  {tag[1]}: {tag[3]}回")

    agent.get_close()
