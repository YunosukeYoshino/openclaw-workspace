#!/usr/bin/env python3
"""
クロスカテゴリ推薦エージェント データベース管理 / Cross-Category Recommendation Agent Database Management
personalized-cross-recommendation-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class PreferenceDB:
    """嗜好データベース管理クラス"""

    def __init__(self, db_path: str = "data/preference.db"):
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

    def create_preference(
        self,
        category: str,
        item_id: str,
        rating: Optional[float] = None,
        tags: Optional[str] = None
    ) -> int:
        """嗜好作成"""
        query = """
            INSERT INTO preferences (category, item_id, rating, tags)
            VALUES (?, ?, ?, ?)
        """
        return self.execute_update(query, (category, item_id, rating, tags))

    def get_preference(self, preference_id: int) -> Optional[Dict]:
        """嗜好取得"""
        rows = self.execute_query(
            "SELECT * FROM preferences WHERE id = ?",
            (preference_id,)
        )
        return dict(rows[0]) if rows else None

    def list_preferences(
        self,
        category: Optional[str] = None,
        min_rating: Optional[float] = None
    ) -> List[Dict]:
        """嗜好一覧"""
        query = "SELECT * FROM preferences WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if min_rating:
            query += " AND rating >= ?"
            params.append(min_rating)

        query += " ORDER BY rating DESC, interaction_count DESC"

        rows = self.execute_query(query, tuple(params) if params else None)
        return [dict(row) for row in rows]

    def create_behavior_log(
        self,
        user_id: str,
        action: str,
        category: str,
        item_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> int:
        """行動ログ作成"""
        query = """
            INSERT INTO behavior_logs (user_id, action, category, item_id, context)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (user_id, action, category, item_id, context))

    def get_user_behavior(
        self,
        user_id: str,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """ユーザー行動取得"""
        query = "SELECT * FROM behavior_logs WHERE user_id = ?"
        params = [user_id]

        if action:
            query += " AND action = ?"
            params.append(action)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def create_recommendation(
        self,
        user_id: str,
        category: str,
        item_ids: str,
        algorithm: str,
        score: float
    ) -> int:
        """推薦作成"""
        query = """
            INSERT INTO recommendations (user_id, category, item_ids, algorithm, score)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (user_id, category, item_ids, algorithm, score))

    def get_recommendations(
        self,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """推薦取得"""
        query = "SELECT * FROM recommendations WHERE user_id = ?"
        params = [user_id]

        if category:
            query += " AND category = ?"
            params.append(category)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_statistics(self) -> Dict:
        """統計情報取得"""
        total_prefs = self.execute_query("SELECT COUNT(*) FROM preferences")[0][0]
        total_logs = self.execute_query("SELECT COUNT(*) FROM behavior_logs")[0][0]
        total_recs = self.execute_query("SELECT COUNT(*) FROM recommendations")[0][0]

        # カテゴリ別分布
        categories = self.execute_query("""
            SELECT category, COUNT(*) as count
            FROM preferences
            GROUP BY category
            ORDER BY count DESC
        """)

        return {
            "total_preferences": total_prefs,
            "total_behavior_logs": total_logs,
            "total_recommendations": total_recs,
            "category_distribution": [dict(cat) for cat in categories]
        }

    def cleanup_old_records(self, days: int = 90) -> int:
        """古いレコードを削除"""
        query = """
            DELETE FROM behavior_logs
            WHERE timestamp < datetime('now', '-' || ? || ' days')
        """
        return self.execute_update(query, (days,))


if __name__ == "__main__":
    import json
    with PreferenceDB() as db:
        stats = db.get_statistics()
        print("統計情報:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
