#!/usr/bin/env python3
"""
機械学習試合予測エージェント データベース管理 / Machine Learning Prediction Agent Database Management
baseball-prediction-ml-agent
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class BaseballAdvancedDB:
    """野球高度分析データベース管理クラス"""

    def __init__(self, db_path: str = "data/baseball_advanced.db"):
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

    def create_player_sabermetric(
        self,
        player_id: str,
        player_name: str,
        team: str,
        season: int,
        stat_type: str,
        stat_name: str,
        stat_value: float
    ) -> int:
        """選手セイバーメトリクス作成"""
        query = """
            INSERT INTO sabermetrics (player_id, player_name, team, season, stat_type, stat_name, stat_value)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (player_id, player_name, team, season, stat_type, stat_name, stat_value))

    def get_player_sabermetrics(
        self,
        player_id: str,
        season: Optional[int] = None
    ) -> List[Dict]:
        """選手セイバーメトリクス取得"""
        query = "SELECT * FROM sabermetrics WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC, calculated_at DESC"
        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]

    def get_top_players(
        self,
        stat_name: str,
        season: int,
        stat_type: str = "batting",
        limit: int = 10
    ) -> List[Dict]:
        """トップ選手を取得"""
        query = """
            SELECT DISTINCT player_id, player_name, team, stat_value
            FROM sabermetrics
            WHERE season = ? AND stat_type = ? AND stat_name = ?
            ORDER BY stat_value DESC
            LIMIT ?
        """
        rows = self.execute_query(query, (season, stat_type, stat_name, limit))
        return [dict(row) for row in rows]

    def create_pitcher_stats(
        self,
        player_id: str,
        player_name: str,
        team: str,
        season: int,
        era: Optional[float] = None,
        whip: Optional[float] = None,
        fip: Optional[float] = None,
        k_per_9: Optional[float] = None,
        bb_per_9: Optional[float] = None
    ) -> int:
        """投手統計作成"""
        query = """
            INSERT INTO pitcher_stats (player_id, player_name, team, season, era, whip, fip, k_per_9, bb_per_9)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (player_id, player_name, team, season, era, whip, fip, k_per_9, bb_per_9))

    def get_pitcher_stats(self, player_id: str, season: Optional[int] = None) -> Optional[Dict]:
        """投手統計取得"""
        query = "SELECT * FROM pitcher_stats WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC LIMIT 1"
        rows = self.execute_query(query, tuple(params))
        return dict(rows[0]) if rows else None

    def create_batter_stats(
        self,
        player_id: str,
        player_name: str,
        team: str,
        season: int,
        avg: Optional[float] = None,
        obp: Optional[float] = None,
        slg: Optional[float] = None,
        ops: Optional[float] = None
    ) -> int:
        """打者統計作成"""
        query = """
            INSERT INTO batter_stats (player_id, player_name, team, season, avg, obp, slg, ops)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (player_id, player_name, team, season, avg, obp, slg, ops))

    def get_batter_stats(self, player_id: str, season: Optional[int] = None) -> Optional[Dict]:
        """打者統計取得"""
        query = "SELECT * FROM batter_stats WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC LIMIT 1"
        rows = self.execute_query(query, tuple(params))
        return dict(rows[0]) if rows else None

    def create_prediction(
        self,
        model_name: str,
        match_id: str,
        prediction_type: str,
        predicted_value: float,
        confidence: float
    ) -> int:
        """予測作成"""
        query = """
            INSERT INTO predictions (model_name, match_id, prediction_type, predicted_value, confidence)
            VALUES (?, ?, ?, ?, ?)
        """
        return self.execute_update(query, (model_name, match_id, prediction_type, predicted_value, confidence))

    def update_prediction_result(self, prediction_id: int, actual_value: float) -> bool:
        """予測結果を更新"""
        query = "UPDATE predictions SET actual_value = ? WHERE id = ?"
        result = self.execute_update(query, (actual_value, prediction_id))
        return result > 0

    def get_model_statistics(self, model_name: str) -> Dict:
        """モデル統計取得"""
        # 予測数
        total = self.execute_query(
            "SELECT COUNT(*) FROM predictions WHERE model_name = ?",
            (model_name,)
        )[0][0]

        # 実績がある予測
        with_actual = self.execute_query(
            "SELECT COUNT(*) FROM predictions WHERE model_name = ? AND actual_value IS NOT NULL",
            (model_name,)
        )[0][0]

        # 平均誤差
        error_rows = self.execute_query(
            "SELECT ABS(predicted_value - actual_value) as error FROM predictions WHERE model_name = ? AND actual_value IS NOT NULL",
            (model_name,)
        )
        if error_rows:
            mae = sum(row['error'] for row in error_rows) / len(error_rows)
        else:
            mae = 0

        return {
            "model_name": model_name,
            "total_predictions": total,
            "predictions_with_results": with_actual,
            "mean_absolute_error": mae
        }

    def get_fielding_stats(self, player_id: str, season: Optional[int] = None) -> List[Dict]:
        """守備統計取得"""
        query = "SELECT * FROM fielding_stats WHERE player_id = ?"
        params = [player_id]

        if season:
            query += " AND season = ?"
            params.append(season)

        query += " ORDER BY season DESC"
        rows = self.execute_query(query, tuple(params))
        return [dict(row) for row in rows]


if __name__ == "__main__":
    import json
    with BaseballAdvancedDB() as db:
        # テスト: 投手統計作成
        db.create_pitcher_stats("p001", "佐藤投手", "巨人", 2024, 2.45, 0.98, 2.89, 9.5, 2.1)

        # テスト: 投手統計取得
        stats = db.get_pitcher_stats("p001", 2024)
        print("投手統計:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
