#!/usr/bin/env python3
"""
えっちコンテンツキュレーションエージェント
Erotic Content Curation Agent

えっちコンテンツのキュレーション、コレクション、おすすめリストを管理するエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class EroticCurationAgent:
    """えっちコンテンツキュレーションエージェント"""

    def __init__(self, db_path: str = "erotic_curation_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # コレクションテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # アイテムテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS items (
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

    def add_collection(self, name: str, data: str):
        """Collectionを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO collections (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_collection(self, collection_id: int):
        """Collectionを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM collections WHERE id = ?", (collection_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_collectionss(self, limit: int = 100):
        """全Collectionsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM collections LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_collection(self, collection_id: int, name: str = None, data: str = None):
        """Collectionを更新"""
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
            values.append(collection_id)
            cursor.execute(f"UPDATE collections SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_collection(self, collection_id: int):
        """Collectionを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM collections WHERE id = ?", (collection_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

    def add_item(self, name: str, data: str):
        """Itemを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO items (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_item(self, item_id: int):
        """Itemを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM items WHERE id = ?", (item_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_itemss(self, limit: int = 100):
        """全Itemsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM items LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_item(self, item_id: int, name: str = None, data: str = None):
        """Itemを更新"""
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
            values.append(item_id)
            cursor.execute(f"UPDATE items SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_item(self, item_id: int):
        """Itemを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM items WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

