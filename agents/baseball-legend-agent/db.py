#!/usr/bin/env python3
"""
野球伝説エージェント Database Module
Baseball Legends Agent データベースモジュール
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class BaseballLegendAgentDB:
    "Baseball Legends Agent Database"

    def __init__(self, db_path: str = "data/baseball-legend-agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()

    def create_tables(self):
        """テーブルを作成する"""
        cursor = self.conn.cursor()

        # rules/stadiums/legends テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
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

    def get_all_rules(self) -> List[Dict]:
        """すべてのルールを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_inductees(self) -> List[Dict]:
        """すべての殿堂入り選手を取得する（rulesテーブルを使用）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'hof' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_awards(self) -> List[Dict]:
        """すべての賞を取得する（rulesテーブルを使用）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'award' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_stadiums(self) -> List[Dict]:
        """すべての野球場を取得する（rulesテーブルを使用）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'stadium' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_legends(self) -> List[Dict]:
        """すべての伝説を取得する（rulesテーブルを使用）"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM rules WHERE category = 'legend' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def add_rule(self, name: str, description: str, category: str = "general") -> int:
        """ルールを追加する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO rules (name, description, category) VALUES (?, ?, ?)",
            (name, description, category)
        )
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        """接続を閉じる"""
        self.conn.close()

def main():
    db = BaseballLegendAgentDB()
    print("Database initialized")

if __name__ == "__main__":
    main()
