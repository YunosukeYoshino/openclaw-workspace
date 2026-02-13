#!/usr/bin/env python3
"""
ゲームプレイヤー統計エージェント Database Module
Game Player Statistics Agent データベースモジュール
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class GamePlayerStatsAgentDB:
    "Game Player Statistics Agent Database"

    def __init__(self, db_path: str = "data/game-player-stats-agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()

    def create_tables(self):
        """テーブルを作成する"""
        cursor = self.conn.cursor()

        # players/predictions/rankings/groups/patterns テーブル
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

    def get_all_players(self) -> List[Dict]:
        """すべてのプレイヤーを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'player' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_player_stats(self, player_name: str) -> Optional[str]:
        """プレイヤー統計を取得する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? AND data_type = 'player'",
            (player_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_predictions(self) -> List[Dict]:
        """すべての予測を取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'prediction' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_rankings(self) -> List[Dict]:
        """すべてのランキングを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'ranking' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_groups(self) -> List[Dict]:
        """すべてのグループを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'group' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_group_stats(self, group_name: str) -> Optional[str]:
        """グループ統計を取得する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT description FROM main_table WHERE name = ? AND data_type = 'group'",
            (group_name,)
        )
        row = cursor.fetchone()
        return row[0] if row else None

    def get_all_patterns(self) -> List[Dict]:
        """すべてのパターンを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM main_table WHERE data_type = 'pattern' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

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
    db = GamePlayerStatsAgentDB()
    print("Database initialized")

if __name__ == "__main__":
    main()
