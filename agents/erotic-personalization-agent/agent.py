#!/usr/bin/env python3
"""
えっちコンテンツパーソナライゼーションエージェント
Erotic Content Personalization Agent

えっちコンテンツのパーソナライズされたおすすめ、ユーザー設定を管理するエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class EroticPersonalizationAgent:
    """えっちコンテンツパーソナライゼーションエージェント"""

    def __init__(self, db_path: str = "erotic_personalization_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # 設定テーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # おすすめテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS recommendations (
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

    def add_preference(self, name: str, data: str):
        """Preferenceを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO preferences (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_preference(self, preference_id: int):
        """Preferenceを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM preferences WHERE id = ?", (preference_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_preferencess(self, limit: int = 100):
        """全Preferencesを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM preferences LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_preference(self, preference_id: int, name: str = None, data: str = None):
        """Preferenceを更新"""
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
            values.append(preference_id)
            cursor.execute(f"UPDATE preferences SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_preference(self, preference_id: int):
        """Preferenceを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM preferences WHERE id = ?", (preference_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

    def add_recommendation(self, name: str, data: str):
        """Recommendationを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO recommendations (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_recommendation(self, recommendation_id: int):
        """Recommendationを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM recommendations WHERE id = ?", (recommendation_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_recommendationss(self, limit: int = 100):
        """全Recommendationsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM recommendations LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_recommendation(self, recommendation_id: int, name: str = None, data: str = None):
        """Recommendationを更新"""
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
            values.append(recommendation_id)
            cursor.execute(f"UPDATE recommendations SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_recommendation(self, recommendation_id: int):
        """Recommendationを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM recommendations WHERE id = ?", (recommendation_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

