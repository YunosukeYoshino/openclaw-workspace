#!/usr/bin/env python3
"""
野球歴史的名試合エージェント Database Module
Baseball Historic Match Agent データベースモジュール
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class BaseballHistoryMatchAgentDB:
    "Baseball Historic Match Agent Database"

    def __init__(self, db_path: str = "data/baseball-history-match-agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()

    def create_tables(self):
        """テーブルを作成する"""
        cursor = self.conn.cursor()

        # players/matches/teams/charts/scout_reports テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS main_table (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                data_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # entries テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                content TEXT NOT NULL,
                type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        self.conn.commit()

    def get_player_comparison(self, player1: str, player2: str) -> Optional[str]:
        """選手の比較を取得する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? OR name = ? AND data_type = 'player'",
            (player1, player2)
        )
        rows = cursor.fetchall()
        if len(rows) < 2:
            return None
        return f"{rows[0][0]}\n\n{rows[1][0]}"

    def get_all_matches(self) -> List[Dict]:
        """すべての試合を取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'match' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_match(self, match_id: str) -> Optional[str]:
        """試合を取得する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? AND data_type = 'match'",
            (match_id,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_teams(self) -> List[Dict]:
        """すべてのチームを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'team' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_team_analysis(self, team_name: str) -> Optional[str]:
        """チーム分析を取得する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? AND data_type = 'team'",
            (team_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_charts(self) -> List[Dict]:
        """すべてのチャートを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'chart' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_reports(self) -> List[Dict]:
        """すべてのレポートを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'report' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_player_report(self, player_name: str) -> Optional[str]:
        """選手レポートを取得する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? AND data_type = 'report'",
            (player_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def add_item(self, name: str, description: str, data_type: str = "general") -> int:
        """アイテムを追加する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO main_table (name, description, data_type) VALUES (?, ?, ?)",
            (name, description, data_type)
        )
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        """接続を閉じる"""
        self.conn.close()

def main():
    db = BaseballHistoryMatchAgentDB()
    print("Database initialized")

if __name__ == "__main__":
    main()
