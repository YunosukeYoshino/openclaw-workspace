#!/usr/bin/env python3
"""
守備分析エージェント / Fielding Analysis Agent
baseball-fielding-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path

class BaseballFieldingAgentAgent:
    """守備分析エージェント"""

    def __init__(self, db_path=None):
        self.db_path = db_path or Path("data/baseball_advanced.db")
        self.conn = None
        self.init_db()

    def init_db(self):
        """データベース初期化"""
        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()

    def create_tables(self):
        """テーブル作成"""
        cursor = self.conn.cursor()

        # セイバーメトリクステーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sabermetrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER NOT NULL,
                stat_type TEXT NOT NULL,
                stat_name TEXT NOT NULL,
                stat_value REAL,
                calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 予測モデルテーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                match_id TEXT NOT NULL,
                prediction_type TEXT NOT NULL,
                predicted_value REAL,
                confidence REAL,
                actual_value REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 投手分析テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pitcher_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER,
                era REAL,
                whip REAL,
                fip REAL,
                k_per_9 REAL,
                bb_per_9 REAL,
                hr_per_9 REAL,
                strikeout_rate REAL,
                groundball_rate REAL,
                avg_velocity REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 打者分析テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS batter_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER,
                avg REAL,
                obp REAL,
                slg REAL,
                ops REAL,
                wrc_plus REAL,
                iso REAL,
                babip REAL,
                hard_hit_rate REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 守備分析テーブル
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fielding_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT NOT NULL,
                player_name TEXT,
                team TEXT,
                season INTEGER,
                position TEXT,
                games_played INTEGER,
                innings_played REAL,
                putouts INTEGER,
                assists INTEGER,
                errors INTEGER,
                fielding_percentage REAL,
                drs INTEGER,
                uzr REAL,
                oaa REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        self.conn.commit()

    def add_sabermetric(self, player_id, player_name, team, season, stat_type, stat_name, stat_value):
        """セイバーメトリクスを追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sabermetrics (player_id, player_name, team, season, stat_type, stat_name, stat_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (player_id, player_name, team, season, stat_type, stat_name, stat_value))
        self.conn.commit()
        return cursor.lastrowid

    def get_sabermetrics(self, player_id=None, season=None):
        """セイバーメトリクスを取得"""
        cursor = self.conn.cursor()
        query = "SELECT * FROM sabermetrics WHERE 1=1"
        params = []

        if player_id:
            query += " AND player_id = ?"
            params.append(player_id)

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC, calculated_at DESC"
        cursor.execute(query, params)
        return cursor.fetchall()

    def calculate_ops(self, obp, slg):
        """OPSを計算"""
        return obp + slg if obp and slg else None

    def calculate_fip(self, hr, bb, hbp, k, ip):
        """FIP (Fielding Independent Pitching) を計算"""
        if ip == 0:
            return None
        return ((13 * hr) + (3 * (bb + hbp)) - (2 * k)) / ip + 3.2

    def calculate_rc(self, h, tb, bb, hbp, ab, sf):
        """RC (Runs Created) を計算"""
        denominator = ab + bb + hbp + sf
        if denominator == 0:
            return None
        numerator = (h + bb + hbp) * tb
        return numerator / denominator

    def add_prediction(self, model_name, match_id, prediction_type, predicted_value, confidence):
        """予測を追加"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO predictions (model_name, match_id, prediction_type, predicted_value, confidence)
            VALUES (?, ?, ?, ?, ?)
        """, (model_name, match_id, prediction_type, predicted_value, confidence))
        self.conn.commit()
        return cursor.lastrowid

    def get_prediction_accuracy(self, model_name=None, limit=100):
        """予測精度を取得"""
        cursor = self.conn.cursor()
        query = """
            SELECT * FROM predictions
            WHERE actual_value IS NOT NULL
        """
        params = []

        if model_name:
            query += " AND model_name = ?"
            params.append(model_name)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        predictions = cursor.fetchall()

        if not predictions:
            return None

        errors = []
        for pred in predictions:
            predicted = pred[6]
            actual = pred[7]
            if predicted is not None and actual is not None:
                errors.append(abs(predicted - actual))

        if errors:
            mae = sum(errors) / len(errors)  # Mean Absolute Error
            return {
                "count": len(predictions),
                "mae": mae,
                "predictions": predictions
            }

        return None

    def get_close(self):
        """接続を閉じる"""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":
    agent = BaseballFieldingAgentAgent()

    # サンプルデータ追加
    agent.add_sabermetric("player001", "山田太郎", "ヤンキース", 2024, "batting", "OPS", 0.923)
    agent.add_sabermetric("player001", "山田太郎", "ヤンキース", 2024, "batting", "wRC+", 145)

    # セイバーメトリクス取得
    metrics = agent.get_sabermetrics(player_id="player001")
    print("セイバーメトリクス:")
    for metric in metrics:
        print(f"  {metric[2]}: {metric[5]} = {metric[6]}")

    # 計算
    print(f"\nOPS計算: {agent.calculate_ops(0.380, 0.543)}")
    print(f"FIP計算: {agent.calculate_fip(20, 50, 5, 200, 180)}")

    agent.get_close()
