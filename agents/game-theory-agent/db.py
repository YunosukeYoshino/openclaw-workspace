#!/usr/bin/env python3
"""
ゲーム理論エージェント データベースモジュール
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

class GameTheoryAgentDB:
    """ゲーム理論エージェント データベース管理"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path("data/game-theory-agent.db")
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """データベースを初期化"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS simulations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    parameters TEXT,
                    results TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    target TEXT,
                    data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_simulation(self, name, parameters, results):
        """シミュレーションを追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO simulations (name, parameters, results) VALUES (?, ?, ?)",
                (name, json.dumps(parameters), json.dumps(results))
            )
            conn.commit()
            return cursor.lastrowid

    def add_analysis(self, analysis_type, target, data):
        """分析結果を追加"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "INSERT INTO analyses (type, target, data) VALUES (?, ?, ?)",
                (analysis_type, target, json.dumps(data))
            )
            conn.commit()
            return cursor.lastrowid

    def get_simulation(self, simulation_id):
        """シミュレーションを取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM simulations WHERE id = ?", (simulation_id,)).fetchone()
            return dict(row) if row else None

    def list_simulations(self, limit=100):
        """シミュレーション一覧を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM simulations ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def list_analyses(self, analysis_type=None, limit=100):
        """分析結果一覧を取得"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            if analysis_type:
                rows = conn.execute(
                    "SELECT * FROM analyses WHERE type = ? ORDER BY created_at DESC LIMIT ?",
                    (analysis_type, limit)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM analyses ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]
