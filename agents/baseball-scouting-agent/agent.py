#!/usr/bin/env python3
"""
選手スカウティング情報エージェント
選手のスカウティング情報を管理するエージェント
"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional


class BaseballScoutingAgent:
    """選手スカウティング情報エージェント"""

    def __init__(self, db_path: str = "baseball-scouting-agent.db"):
        """初期化"""
        self.db_path = db_path
        self.conn = None

    def connect(self) -> sqlite3.Connection:
        """データベースに接続"""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def close(self) -> None:
        """接続を閉じる"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        """コンテキストマネージャー"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー"""
        self.close()

    def get_all(self) -> List[Dict[str, Any]]:
        """全てのデータを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM baseball_stats ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]

    def add_stat(self, player_id: str, player_name: str, **kwargs) -> int:
        """統計データを追加"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO baseball_stats (player_id, player_name, team, games, at_bats, hits, home_runs, rbi, batting_average, era, wins, saves, season)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                player_id, player_name,
                kwargs.get("team"), kwargs.get("games", 0),
                kwargs.get("at_bats", 0), kwargs.get("hits", 0),
                kwargs.get("home_runs", 0), kwargs.get("rbi", 0),
                kwargs.get("batting_average", 0.0), kwargs.get("era", 0.0),
                kwargs.get("wins", 0), kwargs.get("saves", 0),
                kwargs.get("season", datetime.now().strftime("%Y"))
            ))
            conn.commit()
            return cursor.lastrowid

    def get_by_player(self, player_id: str) -> Optional[Dict[str, Any]]:
        """選手の統計を取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM baseball_stats WHERE player_id = ?", (player_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_stat(self, player_id: str, season: str, **kwargs) -> bool:
        """統計データを更新"""
        updates = ", ".join([f"{k} = ?" for k in kwargs.keys()])
        values = list(kwargs.values()) + [player_id, season]

        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE baseball_stats SET {updates}, updated_at = CURRENT_TIMESTAMP
                WHERE player_id = ? AND season = ?
            """, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_stat(self, player_id: str, season: str) -> bool:
        """統計データを削除"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM baseball_stats WHERE player_id = ? AND season = ?", (player_id, season))
            conn.commit()
            return cursor.rowcount > 0

    def search(self, query: str) -> List[Dict[str, Any]]:
        """統計データを検索"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM baseball_stats
                WHERE player_name LIKE ? OR team LIKE ?
                ORDER BY created_at DESC
            """, (f"%{query}%", f"%{query}%"))
            return [dict(row) for row in cursor.fetchall()]

    def get_stats_summary(self) -> Dict[str, Any]:
        """統計のサマリーを取得"""
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as total_players,
                       AVG(batting_average) as avg_ba,
                       AVG(era) as avg_era,
                       SUM(home_runs) as total_hr
                FROM baseball_stats
            """)
            row = cursor.fetchone()
            return dict(row) if row else {}


def main():
    """メイン関数"""
    agent = BaseballScoutingAgent()
    print(f"{agent.__class__.__name__} initialized")


if __name__ == "__main__":
    main()
