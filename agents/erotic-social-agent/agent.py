#!/usr/bin/env python3
"""
えっちコンテンツソーシャルエージェント
Erotic Content Social Agent

えっちコンテンツのソーシャルシェア、いいね、コメントを管理するエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class EroticSocialAgent:
    """えっちコンテンツソーシャルエージェント"""

    def __init__(self, db_path: str = "erotic_social_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 投稿テーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # インタラクションテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    def add_post(self, name: str, data: str):
        """Postを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO posts (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_post(self, post_id: int):
        """Postを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM posts WHERE id = ?", (post_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_postss(self, limit: int = 100):
        """全Postsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM posts LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_post(self, post_id: int, name: str = None, data: str = None):
        """Postを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates = []
        values = []
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if data is not None:
            updates.append("data = ?")
            values.append(data)
        if updates:
            values.append(post_id)
            cursor.execute(f"UPDATE posts SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_post(self, post_id: int):
        """Postを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

    def add_interaction(self, name: str, data: str):
        """Interactionを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO interactions (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_interaction(self, interaction_id: int):
        """Interactionを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM interactions WHERE id = ?", (interaction_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_interactionss(self, limit: int = 100):
        """全Interactionsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM interactions LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_interaction(self, interaction_id: int, name: str = None, data: str = None):
        """Interactionを更新"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        updates = []
        values = []
        if name is not None:
            updates.append("name = ?")
            values.append(name)
        if data is not None:
            updates.append("data = ?")
            values.append(data)
        if updates:
            values.append(interaction_id)
            cursor.execute(f"UPDATE interactions SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_interaction(self, interaction_id: int):
        """Interactionを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM interactions WHERE id = ?", (interaction_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

