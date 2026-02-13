#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Game Meta Analysis Agent Database Module
ゲームメタ分析エージェント データベースモジュール
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

class GameMetaAnalysisAgentDB:
    """Game Meta Analysis Agent Database"""

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent / "data.db"
        self.db_path = db_path
        self._init_database()

    def _init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS game_meta_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS meta_analysis_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()


    def insert(self, table, data):
        """データを挿入"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"INSERT INTO {table} (data) VALUES (?)", (json.dumps(data),))
        conn.commit()
        conn.close()
        return cursor.lastrowid

    def select(self, table, limit=10):
        """データを選択"""
        conn = self.connect()
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table} ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        conn.close()
        return rows


    def connect(self):
        """接続を取得"""
        return sqlite3.connect(self.db_path)

def main():
    """メイン関数"""
    db = GameMetaAnalysisAgentDB()
    print("Game Meta Analysis Agent Database initialized")

if __name__ == "__main__":
    main()
