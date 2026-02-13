#!/usr/bin/env python3
"""
ゲームDLCエージェント Database Module
Game DLC Agent データベースモジュール
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class GameDlcAgentDB:
    "Game DLC Agent Database"

    def __init__(self, db_path: str = "data/game-dlc-agent.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.create_tables()

    def create_tables(self):
        """テーブルを作成する"""
        cursor = self.conn.cursor()

        # reviews/dlc/tournaments/guides/news テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
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

    def get_all_reviews(self) -> List[Dict]:
        """すべてのレビューを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = 'review' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_dlc(self) -> List[Dict]:
        """すべてのDLCを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = 'dlc' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_tournaments(self) -> List[Dict]:
        """すべてのトーナメントを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = 'tournament' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_guides(self) -> List[Dict]:
        """すべてのガイドを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = 'guide' ORDER BY name")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def get_all_news(self) -> List[Dict]:
        """すべてのニュースを取得する"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM items WHERE category = 'news' ORDER BY name DESC")
        return [dict(zip([col[0] for col in cursor.description], row)) for row in cursor.fetchall()]

    def add_item(self, name: str, description: str, category: str = "general") -> int:
        """アイテムを追加する"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO items (name, description, category) VALUES (?, ?, ?)",
            (name, description, category)
        )
        self.conn.commit()
        return cursor.lastrowid

    def close(self):
        """接続を閉じる"""
        self.conn.close()

def main():
    db = GameDlcAgentDB()
    print("Database initialized")

if __name__ == "__main__":
    main()
