#!/usr/bin/env python3
"""
えっちコンテンツディスカバリーエージェント
Erotic Content Discovery Agent

えっちコンテンツの発見、トレンド、新着コンテンツを管理するエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class EroticDiscoveryAgent:
    """えっちコンテンツディスカバリーエージェント"""

    def __init__(self, db_path: str = "erotic_discovery_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # トレンドテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # 新着コンテンツテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS new_content (
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

    def add_trend(self, name: str, data: str):
        """Trendを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO trends (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_trend(self, trend_id: int):
        """Trendを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM trends WHERE id = ?", (trend_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_trendss(self, limit: int = 100):
        """全Trendsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM trends LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_trend(self, trend_id: int, name: str = None, data: str = None):
        """Trendを更新"""
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
            values.append(trend_id)
            cursor.execute(f"UPDATE trends SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_trend(self, trend_id: int):
        """Trendを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM trends WHERE id = ?", (trend_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

    def add_new_content(self, name: str, data: str):
        """New_contentを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO new_content (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_new_content(self, new_content_id: int):
        """New_contentを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM new_content WHERE id = ?", (new_content_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_new_contents(self, limit: int = 100):
        """全New_contentを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM new_content LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_new_content(self, new_content_id: int, name: str = None, data: str = None):
        """New_contentを更新"""
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
            values.append(new_content_id)
            cursor.execute(f"UPDATE new_content SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_new_content(self, new_content_id: int):
        """New_contentを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM new_content WHERE id = ?", (new_content_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

