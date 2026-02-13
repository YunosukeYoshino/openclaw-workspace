#!/usr/bin/env python3
"""
えっちコンテンツフィードバックエージェント
Erotic Content Feedback Agent

えっちコンテンツのフィードバック、評価、改善提案を管理するエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class EroticFeedbackAgent:
    """えっちコンテンツフィードバックエージェント"""

    def __init__(self, db_path: str = "erotic_feedback_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # フィードバックテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # レビューテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS reviews (
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

    def add_feedback(self, name: str, data: str):
        """Feedbackを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO feedback (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_feedback(self, feedback_id: int):
        """Feedbackを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM feedback WHERE id = ?", (feedback_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_feedbacks(self, limit: int = 100):
        """全Feedbackを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM feedback LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_feedback(self, feedback_id: int, name: str = None, data: str = None):
        """Feedbackを更新"""
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
            values.append(feedback_id)
            cursor.execute(f"UPDATE feedback SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_feedback(self, feedback_id: int):
        """Feedbackを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM feedback WHERE id = ?", (feedback_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

    def add_review(self, name: str, data: str):
        """Reviewを追加"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO reviews (name, data) VALUES (?, ?)", (name, data))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def get_review(self, review_id: int):
        """Reviewを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM reviews WHERE id = ?", (review_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def list_reviewss(self, limit: int = 100):
        """全Reviewsを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM reviews LIMIT ?", (limit,))
        results = cursor.fetchall()
        conn.close()
        return results

    def update_review(self, review_id: int, name: str = None, data: str = None):
        """Reviewを更新"""
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
            values.append(review_id)
            cursor.execute(f"UPDATE reviews SET {', '.join(updates)} WHERE id = ?", values)
            conn.commit()
        conn.close()
        return cursor.rowcount if updates else 0

    def delete_review(self, review_id: int):
        """Reviewを削除"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM reviews WHERE id = ?", (review_id,))
        conn.commit()
        conn.close()
        return cursor.rowcount

