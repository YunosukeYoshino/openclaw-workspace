#!/usr/bin/env python3
"""
ゲーム価値計算エージェント / Game Value Calculator Agent
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "game_value_calculator.db"

def init_db():
    """データベース初期化"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()
    print("✅ データベース初期化完了")

if __name__ == '__main__':
    init_db()
