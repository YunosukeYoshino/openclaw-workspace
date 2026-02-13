#!/usr/bin/env python3
"""
クロスカテゴリ推薦エージェント / Cross-Category Recommendation Agent
personalized-cross-recommendation-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class PersonalizedCrossRecommendationAgentAgent:
    """クロスカテゴリ推薦エージェント"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Path("data/preference.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # 嗜好テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                item_id TEXT NOT NULL,
                rating REAL,
                interaction_count INTEGER DEFAULT 0,
                last_interaction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 行動ログテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS behavior_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT NOT NULL,
                category TEXT NOT NULL,
                item_id TEXT,
                context TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 推薦履歴テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                category TEXT NOT NULL,
                item_ids TEXT NOT NULL,
                algorithm TEXT,
                score REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_preference(self, category, item_id, rating=None, tags=None):
        """嗜好を追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO preferences
            (category, item_id, rating, interaction_count, tags)
            VALUES (?, ?, ?,
                COALESCE((SELECT interaction_count FROM preferences WHERE category=? AND item_id=?), 0) + 1,
                ?)
        """, (category, item_id, rating, category, item_id, tags))
        self.conn.commit()
        return cursor.lastrowid

    def log_behavior(self, user_id, action, category, item_id=None, context=None):
        """行動を記録"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO behavior_logs (user_id, action, category, item_id, context)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, action, category, item_id, context))
        self.conn.commit()
        return cursor.lastrowid

    def get_preferences(self, category=None):
        """嗜好を取得"""
        cursor = self.conn.cursor()
        if category:
            cursor.execute("""
                SELECT * FROM preferences WHERE category = ?
                ORDER BY rating DESC, interaction_count DESC
            """, (category,))
        else:
            cursor.execute("""
                SELECT * FROM preferences
                ORDER BY rating DESC, interaction_count DESC
            """)
        return cursor.fetchall()

    def get_user_behavior(self, user_id, limit=100):
        """ユーザー行動を取得"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM behavior_logs
            WHERE user_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (user_id, limit))
        return cursor.fetchall()

    def analyze_preferences(self, category=None):
        """嗜好を分析"""
        preferences = self.get_preferences(category)

        analysis = {
            "top_items": [],
            "category_distribution": {},
            "average_rating": 0,
            "total_interactions": 0
        }

        category_counts = {}
        total_rating = 0
        rating_count = 0

        for pref in preferences:
            # カテゴリ集計
            cat = pref[1]
            category_counts[cat] = category_counts.get(cat, 0) + 1

            # 評価集計
            rating = pref[3]
            if rating:
                total_rating += rating
                rating_count += 1

            # トップアイテム
            analysis["top_items"].append({
                "category": pref[1],
                "item_id": pref[2],
                "rating": pref[3],
                "interaction_count": pref[4]
            })

        analysis["category_distribution"] = category_counts
        analysis["total_interactions"] = sum(pref[4] for pref in preferences)
        if rating_count > 0:
            analysis["average_rating"] = total_rating / rating_count

        return analysis

    def get_close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = PersonalizedCrossRecommendationAgentAgent()

    # サンプルデータ追加
    agent.add_preference("baseball", "npb-2024", 5.0, "プロ野球,日本")
    agent.add_preference("baseball", "mlb-yankees", 4.5, "メジャーリーグ,ヤンキース")
    agent.add_preference("game", "pokemon-scarlet", 4.0, "RPG,ポケモン")
    agent.add_preference("erotic", "character-001", 5.0, "アニメ,かわいい")

    # 分析実行
    analysis = agent.analyze_preferences()
    print("嗜好分析:")
    print(json.dumps(analysis, indent=2, ensure_ascii=False))

    agent.get_close()
