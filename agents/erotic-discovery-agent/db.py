#!/usr/bin/env python3
"""
データベースモジュール - えっちコンテンツディスカバリーエージェント
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict

class Database:
    """データベースクラス"""

    def __init__(self, db_path: str = "erotic_discovery_agent.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """データベースを初期化"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        # トレンドテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # 新着コンテンツテーブル
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS new_content (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()
