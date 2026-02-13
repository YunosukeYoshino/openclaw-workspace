#!/usr/bin/env python3
"""
SQLiteデータベース操作モジュール
"""

import sqlite3
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from contextlib import contextmanager


@contextmanager
def get_connection(db_path: str):
    """データベース接続コンテキストマネージャ"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class Database:
    """SQLiteデータベース操作クラス"""

    def __init__(self, db_path: str = "predictions.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)

    def initialize(self):
        """データベーステーブルを作成"""
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()

            # 予測テーブル
            cursor.execute('CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, input_data TEXT NOT NULL, prediction TEXT NOT NULL, features TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

            # 訓練結果テーブル
            cursor.execute('CREATE TABLE IF NOT EXISTS training_results (id INTEGER PRIMARY KEY AUTOINCREMENT, model_type TEXT NOT NULL, result_data TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

            # 評価結果テーブル
            cursor.execute('CREATE TABLE IF NOT EXISTS evaluation_results (id INTEGER PRIMARY KEY AUTOINCREMENT, metrics TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

            # インデックス
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at DESC)')

            conn.commit()
            self.logger.info(f"Database initialized: {self.db_path}")

    def save_prediction(
        self,
        input_data: Dict[str, Any],
        prediction: Dict[str, Any],
        features: Dict[str, Any] = None
    ) -> int:
        """
        予測を保存

        Args:
            input_data: 入力データ
            prediction: 予測結果
            features: 特徴量

        Returns:
            予測ID
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO predictions (input_data, prediction, features) VALUES (?, ?, ?)', (
                json.dumps(input_data, ensure_ascii=False),
                json.dumps(prediction, ensure_ascii=False),
                json.dumps(features or {}, ensure_ascii=False)
            ))
            conn.commit()
            return cursor.lastrowid

    def get_predictions(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        予測履歴を取得

        Args:
            limit: 取得件数
            offset: オフセット

        Returns:
            予測リスト
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM predictions ORDER BY created_at DESC LIMIT ? OFFSET ?', (limit, offset))

            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row["id"],
                    "input_data": json.loads(row["input_data"]),
                    "prediction": json.loads(row["prediction"]),
                    "features": json.loads(row["features"]) if row["features"] else None,
                    "created_at": row["created_at"]
                })

            return results

    def get_prediction_by_id(self, prediction_id: int) -> Optional[Dict[str, Any]]:
        """
        予測IDで取得

        Args:
            prediction_id: 予測ID

        Returns:
            予測データ
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))

            row = cursor.fetchone()
            if row:
                return {
                    "id": row["id"],
                    "input_data": json.loads(row["input_data"]),
                    "prediction": json.loads(row["prediction"]),
                    "features": json.loads(row["features"]) if row["features"] else None,
                    "created_at": row["created_at"]
                }
            return None

    def save_training_result(self, result_data: Dict[str, Any]) -> int:
        """
        訓練結果を保存

        Args:
            result_data: 訓練結果

        Returns:
            訓練結果ID
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO training_results (model_type, result_data) VALUES (?, ?)', (
                result_data.get("model_type", "unknown"),
                json.dumps(result_data, ensure_ascii=False)
            ))
            conn.commit()
            return cursor.lastrowid

    def save_evaluation_result(self, metrics: Dict[str, Any]) -> int:
        """
        評価結果を保存

        Args:
            metrics: 評価指標

        Returns:
            評価結果ID
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO evaluation_results (metrics) VALUES (?)', (json.dumps(metrics, ensure_ascii=False),))
            conn.commit()
            return cursor.lastrowid

    def get_statistics(self) -> Dict[str, Any]:
        """
        統計情報を取得

        Returns:
            統計情報
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()

            # 予測件数
            cursor.execute('SELECT COUNT(*) as count FROM predictions')
            prediction_count = cursor.fetchone()["count"]

            # 訓練件数
            cursor.execute('SELECT COUNT(*) as count FROM training_results')
            training_count = cursor.fetchone()["count"]

            # 評価件数
            cursor.execute('SELECT COUNT(*) as count FROM evaluation_results')
            evaluation_count = cursor.fetchone()["count"]

            return {
                "prediction_count": prediction_count,
                "training_count": training_count,
                "evaluation_count": evaluation_count
            }

    def clear_old_predictions(self, days: int = 30) -> int:
        """
        古い予測を削除

        Args:
            days: 保存日数

        Returns:
            削除件数
        """
        with get_connection(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM predictions WHERE created_at < datetime('now', '-' || ? || ' days')", (days,))
            conn.commit()
            return cursor.rowcount
