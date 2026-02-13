#!/usr/bin/env python3
"""
erotic-recommendation-agent - えっちコンテンツ推薦エージェント
Recommend erotic content based on user preferences and history
ユーザーの好みと履歴に基づいてえっちコンテンツを推薦
"""

import sqlite3
from typing import List, Dict, Optional
from datetime import datetime


class EroticRecommendationAgentAgent:
    """えっちコンテンツ推薦エージェント"""

    def __init__(self, db_path: str = "erotic-recommendation-agent.db"):
        self.db_path = db_path
        self.conn = None
        self._initialize_db()

    def _initialize_db(self):
        """データベースを初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()

        # 基本テーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            source_url TEXT,
            artist TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

        # 追加テーブル

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    content_id INTEGER NOT NULL,
    score REAL DEFAULT 0,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (content_id) REFERENCES entries(id)
);

CREATE TABLE IF NOT EXISTS user_preferences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    preference_key TEXT NOT NULL,
    preference_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

        # タグテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT NOT NULL UNIQUE
        );
        """)

        # エントリータグ紐付けテーブル
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS entry_tags (
            entry_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (entry_id, tag_id),
            FOREIGN KEY (entry_id) REFERENCES entries(id),
            FOREIGN KEY (tag_id) REFERENCES tags(id)
        );
        """)

        self.conn.commit()

    def add_entry(self, title: str, content: str = "", source_url: str = "", artist: str = "", tags: List[str] = None) -> int:
        """エントリーを追加"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO entries (title, content, source_url, artist, tags) VALUES (?, ?, ?, ?, ?)",
            (title, content, source_url, artist, ",".join(tags or []))
        )
        entry_id = cursor.lastrowid

        # タグを追加
        if tags:
            for tag in tags:
                self._add_tag_to_entry(entry_id, tag)

        self.conn.commit()
        return entry_id

    def _add_tag_to_entry(self, entry_id: int, tag_name: str):
        """エントリーにタグを追加"""
        cursor = self.conn.cursor()

        # タグが存在しない場合は作成
        cursor.execute("INSERT OR IGNORE INTO tags (tag_name) VALUES (?)", (tag_name,))
        cursor.execute("SELECT id FROM tags WHERE tag_name = ?", (tag_name,))
        tag_id = cursor.fetchone()["id"]

        # エントリーとタグを紐付け
        cursor.execute(
            "INSERT OR IGNORE INTO entry_tags (entry_id, tag_id) VALUES (?, ?)",
            (entry_id, tag_id)
        )

        self.conn.commit()

    def get_entry(self, entry_id: int) -> Optional[Dict]:
        """エントリーを取得"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM entries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def list_entries(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """エントリー一覧を取得"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM entries ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [dict(row) for row in cursor.fetchall()]

    def search_entries(self, query: str) -> List[Dict]:
        """エントリーを検索"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM entries WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?",
            (f"%{query}%", f"%{query}%", f"%{query}%")
        )
        return [dict(row) for row in cursor.fetchall()]


    def generate_recommendations(self, user_id, limit=10):
        """推薦を生成"""
        # ユーザーの好みと履歴に基づいて推薦
        pass

    def update_user_preferences(self, user_id, preferences):
        """ユーザー好みを更新"""
        pass

    def save_preference(self, user_id, key, value):
        """好みを保存"""
        pass

    def get_preferences(self, user_id):
        """好みを取得"""
        pass

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = EroticRecommendationAgentAgent()
    print("えっちコンテンツ推薦エージェントが起動しました")
