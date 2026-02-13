#!/usr/bin/env python3
"""
ゲームリプレイ分析エージェント - Database Module
ゲームモデリング・シミュレーションエージェントデータベースモジュール
"""

import sqlite3
import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class GameReplayAnalysisAgentDatabase:
    """ゲームモデリング・シミュレーションデータベースクラス"""

    def __init__(self, db_path: str = "game_modeling.db"):
        self.db_path = db_path
        self._init_db()

    @contextmanager
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_db(self):
        """データベースを初期化"""
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS probability_calculations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT NOT NULL,
                    success_rate REAL NOT NULL,
                    calculated_probability REAL NOT NULL,
                    trials INTEGER NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    simulation_type TEXT NOT NULL,
                    iterations INTEGER NOT NULL,
                    average_result REAL NOT NULL,
                    results_json TEXT,
                    parameters TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS mechanics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mechanic_name TEXT NOT NULL,
                    formula TEXT NOT NULL,
                    balance_score REAL,
                    description TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS game_theory_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    scenario_name TEXT NOT NULL,
                    players_count INTEGER NOT NULL,
                    nash_equilibrium TEXT,
                    optimal_strategy TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS replays (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    game_name TEXT NOT NULL,
                    player_name TEXT NOT NULL,
                    replay_path TEXT,
                    analysis_results TEXT,
                    patterns_found TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE INDEX IF NOT EXISTS idx_prob_event ON probability_calculations(event_name);
                CREATE INDEX IF NOT EXISTS idx_sim_type ON simulations(simulation_type);
                CREATE INDEX IF NOT EXISTS idx_mech_name ON mechanics(mechanic_name);
                CREATE INDEX IF NOT EXISTS idx_replay_game ON replays(game_name);
            """)

    def add_probability_calculation(self, calc_data: Dict) -> int:
        """確率計算結果を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO probability_calculations
                   (event_name, success_rate, calculated_probability, trials)
                   VALUES (?, ?, ?, ?)""",
                (
                    calc_data.get("event_name"),
                    calc_data.get("success_rate"),
                    calc_data.get("calculated_probability"),
                    calc_data.get("trials")
                )
            )
            return cursor.lastrowid

    def get_probability_calculations(self, event_name: Optional[str] = None) -> List[Dict]:
        """確率計算結果を取得"""
        query = "SELECT * FROM probability_calculations WHERE 1=1"
        params = []

        if event_name:
            query += " AND event_name = ?"
            params.append(event_name)

        query += " ORDER BY timestamp DESC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def add_simulation(self, sim_data: Dict) -> int:
        """シミュレーション結果を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO simulations
                   (simulation_type, iterations, average_result, results_json, parameters)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    sim_data.get("simulation_type"),
                    sim_data.get("iterations"),
                    sim_data.get("average_result"),
                    json.dumps(sim_data.get("results", [])),
                    json.dumps(sim_data.get("parameters", {}))
                )
            )
            return cursor.lastrowid

    def get_simulations(self, sim_type: Optional[str] = None) -> List[Dict]:
        """シミュレーション結果を取得"""
        query = "SELECT * FROM simulations WHERE 1=1"
        params = []

        if sim_type:
            query += " AND simulation_type = ?"
            params.append(sim_type)

        query += " ORDER BY timestamp DESC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def add_mechanic(self, mechanic_data: Dict) -> int:
        """メカニクスを追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO mechanics
                   (mechanic_name, formula, balance_score, description)
                   VALUES (?, ?, ?, ?)""",
                (
                    mechanic_data.get("mechanic_name"),
                    mechanic_data.get("formula"),
                    mechanic_data.get("balance_score"),
                    mechanic_data.get("description")
                )
            )
            return cursor.lastrowid

    def get_mechanics(self) -> List[Dict]:
        """メカニクス一覧を取得"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM mechanics ORDER BY mechanic_name")
            return [dict(row) for row in cursor.fetchall()]

    def add_game_theory_analysis(self, analysis_data: Dict) -> int:
        """ゲーム理論分析を追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO game_theory_analyses
                   (scenario_name, players_count, nash_equilibrium, optimal_strategy)
                   VALUES (?, ?, ?, ?)""",
                (
                    analysis_data.get("scenario_name"),
                    analysis_data.get("players_count"),
                    analysis_data.get("nash_equilibrium"),
                    analysis_data.get("optimal_strategy")
                )
            )
            return cursor.lastrowid

    def get_game_theory_analyses(self) -> List[Dict]:
        """ゲーム理論分析を取得"""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT * FROM game_theory_analyses ORDER BY timestamp DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_replay(self, replay_data: Dict) -> int:
        """リプレイを追加"""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO replays
                   (game_name, player_name, replay_path, analysis_results, patterns_found)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    replay_data.get("game_name"),
                    replay_data.get("player_name"),
                    replay_data.get("replay_path"),
                    json.dumps(replay_data.get("analysis_results", {})),
                    json.dumps(replay_data.get("patterns_found", []))
                )
            )
            return cursor.lastrowid

    def get_replays(self, game_name: Optional[str] = None) -> List[Dict]:
        """リプレイ一覧を取得"""
        query = "SELECT * FROM replays WHERE 1=1"
        params = []

        if game_name:
            query += " AND game_name = ?"
            params.append(game_name)

        query += " ORDER BY timestamp DESC"

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

def main():
    """テスト実行"""
    db = GameReplayAnalysisAgentDatabase()

    # テストデータを追加
    sim_id = db.add_simulation({
        "simulation_type": "combat",
        "iterations": 1000,
        "average_result": 52.3,
        "results": [50, 55, 48, 52, 54],
        "parameters": {"base_value": 50, "variance": 10}
    })

    print(f"Added simulation ID: {sim_id}")
    print(f"Simulations: {len(db.get_simulations())}")

if __name__ == "__main__":
    main()
